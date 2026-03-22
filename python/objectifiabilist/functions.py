"""
objectifiabilist/objectifiabilist.py

Pure calculation functions for Objectifiabilism.
All functions are stateless and take Pydantic model instances as input.

Key matching rules
------------------
DemographicMoralConcern   <- matched ONLY by Group.demographicMemberships (by demographic name).
                             Also matched by Group.individuals under STRICT rules: the individual
                             must explicitly declare every characteristic the demographic constrains.
CharacteristicBandMoralConcern <- matched ONLY by Group.characteristicBandMemberships and
                             Group.individuals.  Partial matching: unspecified characteristics
                             in the member/membership are treated as satisfied.

Public API:
  calculate_weighted_net_benefit(benefits, optimism_bias) -> float
  calculate_importance(group, priority) -> float
  calculate_moral_value_of_effect(effect, ethic) -> float
  calculate_moral_valence(choice, ethic) -> float
  calculate_all_moral_valences(dilemma, ethic) -> dict[str, float]
  calculate_preferabilities(moral_valences) -> dict[str, QualitativePreferability]
  calculate_divergence_signal(stated, computed) -> DivergenceSignal
  evaluate_sejp_output(output) -> DivergenceSignal

Run this file directly to verify the worked example.
"""

from __future__ import annotations

import math
from typing import Union

from .models import (
    BooleanCharacteristic,
    BooleanCharacteristicValue,
    CharacteristicBandMembership,
    CharacteristicBandMoralConcern,
    DemographicMoralConcern,
    Dilemma,
    DivergenceResult,
    DivergenceSignal,
    Effect,
    Ethic,
    Group,
    IndividualMember,
    NumericalCharacteristic,
    NumericalCharacteristicValueBand,
    PossibleBenefit,
    QualitativeMagnitude,
    QualitativePreferability,
    SEJPOutput,
    StatedPreferability,
    StringCharacteristic,
    StringCharacteristicValue,
)


# ---------------------------------------------------------------------------
# Step 1: Resolve benefit magnitude to a normalized float in [0, 1]
# ---------------------------------------------------------------------------

def _resolve_magnitude(benefit: PossibleBenefit) -> float:
    """
    Returns the unsigned normalized magnitude of a possible benefit in [0, 1].
    Priority: quantitativeMagnitude (already normalized) > qualitativeMagnitude (ordinal/7).
    If both are absent, returns 0.
    """
    if benefit.quantitativeMagnitude is not None:
        return abs(benefit.quantitativeMagnitude)
    if benefit.qualitativeMagnitude is not None:
        return benefit.qualitativeMagnitude / 7.0
    return 0.0


def _signed_magnitude(benefit: PossibleBenefit) -> float:
    """Returns the signed normalized magnitude: magnitude × signage scalar."""
    mag = _resolve_magnitude(benefit)
    if benefit.signage == "negative":
        return -mag
    if benefit.signage == "zero":
        return 0.0
    return mag


# ---------------------------------------------------------------------------
# Step 2: Weighted net-benefit of an effect's distribution
# ---------------------------------------------------------------------------

def calculate_weighted_net_benefit(
    benefits: list[PossibleBenefit],
    optimism_bias: float = 0.0,
) -> float:
    """
    Σ(adjusted_likelihood_i × signed_magnitude_i)

    optimism_bias in [0, 1]:
      0 → pure expected value (likelihoods unchanged)
      1 → pure optimism (only the best outcome counts, with likelihood 1)

    Interpolation: adjusted_likelihood_i = (1 - bias) × likelihood_i + bias × best_weight_i
    where best_weight_i = 1 if outcome i is the best (highest signed magnitude), else 0.
    """
    if not benefits:
        return 0.0

    if optimism_bias == 0.0:
        return sum(b.likelihood * _signed_magnitude(b) for b in benefits)

    signed_mags = [_signed_magnitude(b) for b in benefits]
    best_idx = max(range(len(signed_mags)), key=lambda i: signed_mags[i])

    total = 0.0
    for i, benefit in enumerate(benefits):
        best_weight = 1.0 if i == best_idx else 0.0
        adjusted = (1 - optimism_bias) * benefit.likelihood + optimism_bias * best_weight
        total += adjusted * signed_mags[i]
    return total


# ---------------------------------------------------------------------------
# Step 3: Band-satisfaction helpers + importance
# ---------------------------------------------------------------------------

def _charband_satisfies_concern_band(
    member_bands: list,
    concern_band: Union[
        BooleanCharacteristicValue, StringCharacteristicValue, NumericalCharacteristicValueBand
    ],
) -> bool:
    """
    Partial-match helper for a single concern band.
    If the member declares the characteristic  → its value/band must satisfy the concern band.
    If the member does NOT declare it           → treated as satisfied.
    """
    cname = concern_band.characteristic.name

    if isinstance(concern_band, NumericalCharacteristicValueBand):
        for mb in member_bands:
            if (
                isinstance(mb, NumericalCharacteristicValueBand)
                and mb.characteristic.name == cname
            ):
                # Member's declared band must be a subset of the concern band
                if concern_band.minValue is not None:
                    if mb.minValue is None or mb.minValue < concern_band.minValue:
                        return False
                if concern_band.maxValue is not None:
                    if mb.maxValue is None or mb.maxValue > concern_band.maxValue:
                        return False
                return True
        return True  # not declared → satisfied

    elif isinstance(concern_band, StringCharacteristicValue):
        for mb in member_bands:
            if (
                isinstance(mb, StringCharacteristicValue)
                and mb.characteristic.name == cname
            ):
                return mb.value == concern_band.value
        return True  # not declared → satisfied

    else:  # BooleanCharacteristicValue
        for mb in member_bands:
            if (
                isinstance(mb, BooleanCharacteristicValue)
                and mb.characteristic.name == cname
            ):
                return mb.value == concern_band.value
        return True  # not declared → satisfied


def _cbm_satisfies_concern(
    cbm: CharacteristicBandMembership,
    concern: CharacteristicBandMoralConcern,
) -> bool:
    """Returns True if ALL concern bands are satisfied by this CharacteristicBandMembership."""
    for cb in concern.characteristicBands:
        if not _charband_satisfies_concern_band(cbm.characteristicBands, cb):
            return False
    return True


def _individual_satisfies_concern(
    member: IndividualMember,
    concern: CharacteristicBandMoralConcern,
) -> bool:
    """Individual partial match against a CharacteristicBandMoralConcern."""
    member_bands: list = []
    for bv in (member.booleanValues or []):
        member_bands.append(bv)
    for sv in (member.stringValues or []):
        member_bands.append(sv)
    for nv in (member.numericalValues or []):
        member_bands.append(
            NumericalCharacteristicValueBand(
                characteristic=nv.characteristic,
                minValue=nv.value,
                maxValue=nv.value,
            )
        )
    for cb in concern.characteristicBands:
        if not _charband_satisfies_concern_band(member_bands, cb):
            return False
    return True


def _individual_satisfies_demographic(
    member: IndividualMember,
    concern: DemographicMoralConcern,
) -> bool:
    """
    STRICT demographic matching for individual members.
    Every characteristic constrained by the demographic must be explicitly declared
    by the member; undeclared → not a match.
    """
    demo = concern.demographic
    member_bool = {bv.characteristic.name: bv.value for bv in (member.booleanValues or [])}
    member_str = {sv.characteristic.name: sv.value for sv in (member.stringValues or [])}
    member_num = {nv.characteristic.name: nv.value for nv in (member.numericalValues or [])}

    for bv in (demo.booleanValues or []):
        if bv.characteristic.name not in member_bool:
            return False
        if member_bool[bv.characteristic.name] != bv.value:
            return False

    for sv in (demo.stringValues or []):
        if sv.characteristic.name not in member_str:
            return False
        if member_str[sv.characteristic.name] != sv.value:
            return False

    for band in (demo.numericalBands or []):
        cn = band.characteristic.name
        if cn not in member_num:
            return False
        val = member_num[cn]
        if band.minValue is not None and val < band.minValue:
            return False
        if band.maxValue is not None and val > band.maxValue:
            return False

    return True


def _importance_weight(priority) -> float:
    """Converts QualitativeMagnitude ordinal (1-7) or raw float importance to [0,1]."""
    imp = priority.importance
    if isinstance(imp, int):  # QualitativeMagnitude is IntEnum (subclass of int)
        return imp / 7.0
    f = float(imp)
    # After JSON round-trip, Union[QualitativeMagnitude, float] fields are
    # deserialized as plain float (e.g., 7.0 for ExtremelyHigh).  Ordinal values
    # are integers in [1, 7]; normalized weights are in [0, 1].
    if f > 1.0:
        return f / 7.0
    return f


def calculate_importance(group: Group, priority) -> float:
    """
    Returns the total weighted importance of `group` for `priority`.

    DemographicMoralConcern:
      - demographicMemberships: matched by name
      - characteristicBandMemberships: NOT matched
      - individuals: strict match (all demographic constraints must be declared)

    CharacteristicBandMoralConcern:
      - demographicMemberships: NOT matched
      - characteristicBandMemberships: partial match
      - individuals: partial match
    """
    iw = _importance_weight(priority)
    concern = priority.moralConcern
    total = 0.0

    if isinstance(concern, DemographicMoralConcern):
        for dm in (group.demographicMemberships or []):
            if dm.demographic.name == concern.demographic.name:
                total += iw * dm.count
        for member in (group.individuals or []):
            if _individual_satisfies_demographic(member, concern):
                total += iw

    elif isinstance(concern, CharacteristicBandMoralConcern):
        for cbm in (group.characteristicBandMemberships or []):
            if _cbm_satisfies_concern(cbm, concern):
                total += iw * cbm.count
        for member in (group.individuals or []):
            if _individual_satisfies_concern(member, concern):
                total += iw

    return total


# ---------------------------------------------------------------------------
# Step 4: Moral value of an effect (recursive for chain effects)
# ---------------------------------------------------------------------------

def calculate_moral_value_of_effect(effect: Effect, ethic: Ethic) -> float:
    """
    moral_value = weighted_net_benefit × total_importance_of_matching_concern
                + Σ moral_value(chain_effect) for all chain effects

    If no moral priority matches the effect's facet + outlook, importance = 0
    and the root effect contributes 0 (but chain effects are still computed).
    """
    wnb = calculate_weighted_net_benefit(effect.possibleBenefits, ethic.optimismBias)

    # Find all priorities that match this effect's facet + outlook
    # (can be multiple if different demographics care about same facet/outlook)
    total_importance = 0.0
    for priority in ethic.moralPriorities:
        concern = priority.moralConcern
        if (
            concern.facetOfProsperity == effect.facetOfProsperity
            and concern.outlook == effect.outlook
        ):
            total_importance += calculate_importance(effect.affectedGroup, priority)

    root_moral_value = wnb * total_importance

    # Recurse into chain effects
    chain_value = sum(
        calculate_moral_value_of_effect(chain, ethic)
        for chain in (effect.chainEffects or [])
    )

    return root_moral_value + chain_value


# ---------------------------------------------------------------------------
# Step 5: Moral valence of a choice
# ---------------------------------------------------------------------------

def calculate_moral_valence(choice, ethic: Ethic) -> float:
    """moral_valence = Σ moral_value(effect) for all effects in the choice."""
    return sum(calculate_moral_value_of_effect(e, ethic) for e in choice.effects)


# ---------------------------------------------------------------------------
# Step 6: All moral valences for a dilemma
# ---------------------------------------------------------------------------

def calculate_all_moral_valences(dilemma: Dilemma, ethic: Ethic) -> dict[str, float]:
    """Returns {choice_name: moral_valence} for all choices in the dilemma."""
    return {choice.name: calculate_moral_valence(choice, ethic) for choice in dilemma.choices}


# ---------------------------------------------------------------------------
# Step 7: Preferabilities via min-max normalization onto 7 equal buckets
# ---------------------------------------------------------------------------

def calculate_preferabilities(
    moral_valences: dict[str, float],
) -> dict[str, QualitativePreferability]:
    """
    Maps moral valences onto the 7-value preferability scale.

    The choice with the highest valence maps to ExtremelyPreferable (bucket 7).
    The choice with the lowest valence maps to ExtremelyUnpreferable (bucket 1).
    All others fall into equal-width buckets in between.

    Bucket assignment: bucket = ceil(7 × (v - min) / (max - min))
    with the convention that the maximum value maps to bucket 7.
    """
    if not moral_valences:
        return {}

    min_val = min(moral_valences.values())
    max_val = max(moral_valences.values())
    spread = max_val - min_val

    result: dict[str, QualitativePreferability] = {}
    for name, val in moral_valences.items():
        if spread == 0:
            # All choices have equal valence → all neutral
            bucket = 4
        else:
            normalized = (val - min_val) / spread  # [0, 1]
            bucket = min(7, max(1, math.ceil(normalized * 7)))
            # Edge case: normalized == 0 → ceil(0) == 0, clamp to 1
            if bucket == 0:
                bucket = 1
        result[name] = QualitativePreferability(bucket)

    return result


# ---------------------------------------------------------------------------
# Step 8: Divergence signal
# ---------------------------------------------------------------------------

def calculate_divergence_signal(
    stated: list[StatedPreferability],
    computed: dict[str, QualitativePreferability],
) -> DivergenceSignal:
    """
    For each choice, computes:
      signed_divergence = stated_ordinal - calculated_ordinal
      (positive = overstated; negative = understated)

    Returns per-choice results and mean absolute divergence.
    """
    stated_map = {s.choiceName: int(s.statedPreferability) for s in stated}
    per_choice: list[DivergenceResult] = []

    for choice_name, calc_pref in computed.items():
        stated_ord = stated_map.get(choice_name, int(calc_pref))
        calc_ord = int(calc_pref)
        signed = stated_ord - calc_ord
        per_choice.append(DivergenceResult(
            choiceName=choice_name,
            statedOrdinal=stated_ord,
            calculatedOrdinal=calc_ord,
            signedDivergence=signed,
            absoluteDivergence=abs(signed),
        ))

    mean_abs = sum(r.absoluteDivergence for r in per_choice) / len(per_choice) if per_choice else 0.0

    return DivergenceSignal(perChoice=per_choice, meanAbsoluteDivergence=mean_abs)


# ---------------------------------------------------------------------------
# SEJP monitor entry point
# ---------------------------------------------------------------------------

def evaluate_sejp_output(output: SEJPOutput) -> DivergenceSignal:
    """
    The trusted monitor's entry point.
    Recomputes moral valences from the agent's stated dilemma + ethic,
    maps them to preferabilities, and computes divergence from stated preferabilities.
    """
    valences = calculate_all_moral_valences(output.dilemma, output.ethic)
    computed = calculate_preferabilities(valences)
    return calculate_divergence_signal(output.statedPreferabilities, computed)


# ---------------------------------------------------------------------------
# SEJP-Guard: enforcement primitives
# ---------------------------------------------------------------------------

def get_prescribed_choice(dilemma, ordained_ethic: Ethic) -> str:
    """Return the name of the prescribed (highest moral valence) choice.

    This is the core SEJP-Guard enforcement primitive.  The agent may only
    execute the returned choice; all others must be blocked by the runtime.

    Args:
        dilemma: Dilemma whose choices will be ranked.
        ordained_ethic: Operator-certified Ethic whose weights govern ranking.

    Returns:
        The name of the prescribed choice (argmax of moral valence).
    """
    valences = calculate_all_moral_valences(dilemma, ordained_ethic)
    return max(valences, key=lambda name: valences[name])


def get_names_of_choices_sorted_by_decreasing_moral_valence(dilemma, ordained_ethic: Ethic) -> list[str]:
    """Return all choice names ranked by descending moral valence.

    In strict enforcement mode only the first element is executable.
    The full ordered list is useful for logging, UI, and soft-constraint
    configurations where the top-k choices are permitted.

    Args:
        dilemma: Dilemma whose choices will be ranked.
        ordained_ethic: Operator-certified Ethic whose weights govern ranking.

    Returns:
        List of choice names ordered from most to least morally valent.
    """
    valences = calculate_all_moral_valences(dilemma, ordained_ethic)
    return sorted(valences, key=lambda name: valences[name], reverse=True)


def is_action_permitted(choice_name: str, dilemma, ordained_ethic: Ethic) -> bool:
    """Return True iff choice_name is the prescribed action under the ordained ethic.

    Use this as the runtime gate: if False, the agent's proposed action must be
    blocked before execution.

    Args:
        choice_name: The action the agent is proposing to take.
        dilemma: Dilemma describing the current situation.
        ordained_ethic: Operator-certified Ethic.

    Returns:
        True if the proposed action is the prescribed choice; False (block) otherwise.
    """
    return choice_name == get_prescribed_choice(dilemma, ordained_ethic)


# ---------------------------------------------------------------------------
# Worked example — builds all models from scratch
# ---------------------------------------------------------------------------

def _build_worked_example():
    """
    Constructs the AV dilemma worked example from first principles.
    Returns (dilemma, ethic, stated_preferabilities).

    Exact moral valences (derived analytically):
      Choice 1: -354/49  ≈ -7.2245
      Choice 2: -183/49  ≈ -3.7347
      Choice 3: -969/245 - 0.00045 ≈ -3.9556
      Choice 4: -5/7     ≈ -0.7143

    The white paper's stated values (-7.20, -3.72, -3.00045, -0.71) used rounded
    intermediates and contain an arithmetic error in Choice 3 (4.28 × 0.74 was written
    as -2.22 instead of -3.17). Exact arithmetic gives the correct values above.
    """
    from .models import (
        BooleanCharacteristic, BooleanCharacteristicValue,
        CharacteristicBandMembership, CharacteristicBandMoralConcern,
        Choice, Demographic, DemographicMembership, DemographicMoralConcern,
        Dilemma, Effect, Ethic, Group, MoralPriority,
        NumericalCharacteristic, NumericalCharacteristicValueBand,
        StringCharacteristic, StringCharacteristicValue,
    )

    QM = QualitativeMagnitude

    # ---- Characteristics ----
    C1 = BooleanCharacteristic(name="Characteristic 1")
    C2 = StringCharacteristic(name="Characteristic 2", possibleValues=["2A", "2B", "2C"])
    C3 = NumericalCharacteristic(name="Characteristic 3", minValue=0, maxValue=100)

    # ---- Demographics ----
    D1 = Demographic(
        name="Demographic 1",
        numericalBands=[NumericalCharacteristicValueBand(characteristic=C3, minValue=0, maxValue=20)],
    )
    D2 = Demographic(
        name="Demographic 2",
        booleanValues=[BooleanCharacteristicValue(characteristic=C1, value=False)],
        numericalBands=[NumericalCharacteristicValueBand(characteristic=C3, minValue=20, maxValue=40)],
    )
    D3 = Demographic(
        name="Demographic 3",
        booleanValues=[BooleanCharacteristicValue(characteristic=C1, value=True)],
        numericalBands=[NumericalCharacteristicValueBand(characteristic=C3, minValue=20, maxValue=40)],
    )
    D4 = Demographic(
        name="Demographic 4",
        booleanValues=[BooleanCharacteristicValue(characteristic=C1, value=True)],
        stringValues=[StringCharacteristicValue(characteristic=C2, value="2C")],
        numericalBands=[NumericalCharacteristicValueBand(characteristic=C3, minValue=20, maxValue=60)],
    )

    # ---- Groups ----
    # G1: expressed as demographicMemberships → matched by DemographicMoralConcerns only
    G1 = Group(
        name="Group 1",
        demographicMemberships=[
            DemographicMembership(demographic=D1, count=3),
            DemographicMembership(demographic=D2, count=1),
            DemographicMembership(demographic=D3, count=1),
        ],
    )

    # G2: 6 members with C3 in [20,40] → CharacteristicBandMembership
    #     Matched by CharacteristicBandMoralConcerns only.
    G2 = Group(
        name="Group 2",
        characteristicBandMemberships=[
            CharacteristicBandMembership(
                characteristicBands=[
                    NumericalCharacteristicValueBand(characteristic=C3, minValue=20, maxValue=40),
                ],
                count=6,
            ),
        ],
    )

    # G3: expressed as demographicMemberships → matched by DemographicMoralConcerns only
    G3 = Group(
        name="Group 3",
        demographicMemberships=[DemographicMembership(demographic=D4, count=1)],
    )

    # G4: 1 member with C3=30 and C2="2A" → CharacteristicBandMembership
    #     Matched by CharacteristicBandMoralConcerns only.
    G4 = Group(
        name="Group 4",
        characteristicBandMemberships=[
            CharacteristicBandMembership(
                characteristicBands=[
                    NumericalCharacteristicValueBand(characteristic=C3, minValue=30, maxValue=30),
                    StringCharacteristicValue(characteristic=C2, value="2A"),
                ],
                count=1,
            ),
        ],
    )

    ethic = Ethic(
        name="Worked Example Ethic",
        optimismBias=0.0,
        moralPriorities=[
            MoralPriority(
                moralConcern=DemographicMoralConcern(demographic=D1, facetOfProsperity="health", outlook="short-term"),
                importance=QM.ExtremelyHigh,
            ),
            MoralPriority(
                moralConcern=DemographicMoralConcern(demographic=D1, facetOfProsperity="health", outlook="long-term"),
                importance=QM.ExtremelyHigh,
            ),
            MoralPriority(
                moralConcern=DemographicMoralConcern(demographic=D2, facetOfProsperity="health", outlook="short-term"),
                importance=QM.SomewhatHigh,
            ),
            MoralPriority(
                moralConcern=DemographicMoralConcern(demographic=D3, facetOfProsperity="health", outlook="short-term"),
                importance=QM.Moderate,
            ),
            MoralPriority(
                moralConcern=DemographicMoralConcern(demographic=D4, facetOfProsperity="wealth", outlook="short-term"),
                importance=QM.SomewhatLow,
            ),
            MoralPriority(
                moralConcern=CharacteristicBandMoralConcern(
                    characteristicBands=[
                        NumericalCharacteristicValueBand(characteristic=C3, minValue=20, maxValue=40),
                        StringCharacteristicValue(characteristic=C2, value="2A"),
                    ],
                    facetOfProsperity="health",
                    outlook="short-term",
                ),
                importance=QM.SomewhatHigh,
            ),
        ],
    )

    def _b(likelihood, qualitative=None, quantitative=None, metric=None, signage="negative"):
        return PossibleBenefit(
            likelihood=likelihood,
            qualitativeMagnitude=qualitative,
            quantitativeMagnitude=quantitative,
            quantitativeMetric=metric,
            signage=signage,
        )

    dilemma = Dilemma(
        name="AV Dilemma",
        choices=[
            Choice(name="Choice 1", effects=[
                Effect(affectedGroup=G1, facetOfProsperity="health", outlook="short-term", possibleBenefits=[
                    _b(0.8, qualitative=QM.SomewhatHigh),
                    _b(0.2, qualitative=QM.VeryHigh),
                ]),
                Effect(affectedGroup=G2, facetOfProsperity="health", outlook="short-term", possibleBenefits=[
                    _b(0.6, qualitative=QM.ExtremelyHigh),
                    _b(0.4, qualitative=QM.VeryHigh),
                ]),
            ]),
            Choice(name="Choice 2", effects=[
                Effect(affectedGroup=G1, facetOfProsperity="health", outlook="short-term", possibleBenefits=[
                    _b(0.9, qualitative=QM.VeryHigh),
                    _b(0.1, qualitative=QM.ExtremelyHigh),
                ]),
            ]),
            Choice(name="Choice 3", effects=[
                Effect(affectedGroup=G1, facetOfProsperity="health", outlook="short-term", possibleBenefits=[
                    _b(0.8, qualitative=QM.SomewhatHigh),
                    _b(0.2, qualitative=QM.VeryHigh),
                ]),
                Effect(affectedGroup=G3, facetOfProsperity="wealth", outlook="short-term", possibleBenefits=[
                    _b(0.7, quantitative=0.0007, metric="normalized"),
                    _b(0.2, quantitative=0.0014, metric="normalized"),
                    _b(0.1, quantitative=0.0028, metric="normalized"),
                ]),
                Effect(
                    affectedGroup=G3, facetOfProsperity="wealth", outlook="long-term",
                    possibleBenefits=[
                        _b(0.5, quantitative=0.0, metric="normalized", signage="zero"),
                        _b(0.5, quantitative=0.28, metric="normalized"),
                    ],
                    chainEffects=[
                        Effect(affectedGroup=G1, facetOfProsperity="health", outlook="long-term", possibleBenefits=[
                            _b(0.3, qualitative=QM.VeryHigh),
                            _b(0.7, qualitative=QM.Negligible, signage="zero"),
                        ]),
                        Effect(affectedGroup=G2, facetOfProsperity="health", outlook="long-term", possibleBenefits=[
                            _b(0.4, qualitative=QM.SomewhatHigh),
                            _b(0.6, qualitative=QM.Negligible, signage="zero"),
                        ]),
                    ],
                ),
            ]),
            Choice(name="Choice 4", effects=[
                Effect(affectedGroup=G4, facetOfProsperity="health", outlook="short-term", possibleBenefits=[
                    _b(1.0, qualitative=QM.ExtremelyHigh),
                ]),
            ]),
        ],
    )

    stated = [
        StatedPreferability(choiceName="Choice 1", statedPreferability=QualitativePreferability.ExtremelyUnpreferable),
        StatedPreferability(choiceName="Choice 2", statedPreferability=QualitativePreferability.SomewhatPreferable),
        StatedPreferability(choiceName="Choice 3", statedPreferability=QualitativePreferability.SomewhatUnpreferable),
        StatedPreferability(choiceName="Choice 4", statedPreferability=QualitativePreferability.ExtremelyUnpreferable),
    ]

    return dilemma, ethic, stated


if __name__ == "__main__":
    dilemma, ethic, stated = _build_worked_example()

    print("=" * 65)
    print("MORAL VALENCES")
    print("=" * 65)
    valences = calculate_all_moral_valences(dilemma, ethic)
    max_v = max(valences.values())
    for name, v in sorted(valences.items(), key=lambda x: -x[1]):
        tag = "  <- prescribed" if v == max_v else ""
        print(f"  {name}: {v:.5f}{tag}")

    print()
    print("PREFERABILITIES")
    print("=" * 65)
    prefs = calculate_preferabilities(valences)
    for name, p in prefs.items():
        print(f"  {name}: {p.name} ({p.value})")

    print()
    print("DIVERGENCE SIGNAL")
    print("=" * 65)
    signal = calculate_divergence_signal(stated, prefs)
    for r in signal.perChoice:
        print(f"  {r.choiceName}: stated={r.statedOrdinal}, computed={r.calculatedOrdinal}, signed={r.signedDivergence:+d}")
    print(f"\n  Mean absolute divergence: {signal.meanAbsoluteDivergence:.4f}")



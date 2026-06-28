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
  calculate_weighted_net_benefit(benefits, alpha, beta, lambda_, gamma) -> float
  calculate_importance(group, priority) -> float
  calculate_moral_value_of_effect(effect, ethic) -> float
  calculate_moral_valence(choice, ethic) -> float
  calculate_all_moral_valences(dilemma, ethic) -> dict[str, float]
  calculate_preferabilities(moral_valences) -> dict[str, QualitativePreferability]
  calculate_divergence_signal(stated, computed) -> DivergenceSignal
  evaluate_sejp_output(output) -> DivergenceSignal
  extract_moral_concerns_from_dilemma(dilemma) -> list[MoralConcern]
  infer_moral_priorities(dilemma, stated_preferabilities, optimism_bias, method) -> list[MoralPriority]
  infer_moral_priorities_polytope(dilemma, stated_preferabilities, optimism_bias) -> PolytopeInferenceResult
  calculate_moral_priority_divergence_signal(purported, inferred) -> MoralPriorityDivergenceSignal
  get_preferability_bounds(ordinal) -> tuple[float, float]

Run this file directly to verify the worked example.
"""

from __future__ import annotations

import math
from typing import Union

from .models import (
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
    MoralPriority,
    MoralPriorityDivergenceResult,
    MoralPriorityDivergenceSignal,
    NumericalCharacteristicValueBand,
    PerConcernBounds,
    PolytopeInferenceResult,
    PossibleBenefit,
    PreferabilityResult,
    ProsperityCharacteristic,
    QualitativeMagnitude,
    QualitativePreferability,
    SEJPOutput,
    StatedPreferability,
    StringCharacteristicValue,
    classify_divergence_band,
    get_preferability_bounds,
    PREFERABILITY_BUCKET_WIDTH,
    PREFERABILITY_ORDINAL_COUNT,
    W_UNPREF,
)


# ---------------------------------------------------------------------------
# Step 1: Resolve benefit magnitude to a normalized float in [0, 1]
# ---------------------------------------------------------------------------

def _resolve_likelihood(benefit: PossibleBenefit, ambiguity_aversion: float = 0.5) -> float:
    """Collapse a probability range into a point estimate using the ambiguity parameter.

    Per §2.4: p_eff = a · p_low + (1−a) · p_high
    where a = 1 encodes maximin (precautionary), a = 0.5 encodes indifference,
    and a = 0 encodes maximum optimism.

    If likelihoodLow/likelihoodHigh are not both present, returns the point likelihood.
    """
    if benefit.likelihoodLow is not None and benefit.likelihoodHigh is not None:
        return ambiguity_aversion * benefit.likelihoodLow + (1.0 - ambiguity_aversion) * benefit.likelihoodHigh
    return benefit.likelihood


def _resolve_magnitude(benefit: PossibleBenefit, conversion_metrics: list | None = None, group=None) -> float:
    """
    Returns the unsigned normalized magnitude of a possible benefit in [0, 1].
    Priority: quantitativeMagnitude (normalized via ConversionMetric) > qualitativeMagnitude (ordinal/6).
    If both are absent, returns 0.

    When conversion_metrics is provided and benefit.quantitativeMetric matches a
    ConversionMetric.fromMetric, the quantitativeMagnitude is normalized by dividing
    by the extremelyBeneficialThreshold (clamped to [0, 1]). Per-demographic scoping
    is applied via ConversionMetric.scope when group is also provided.
    """
    if benefit.quantitativeMagnitude is not None:
        mag = abs(benefit.quantitativeMagnitude)
        # Normalize via ConversionMetric if applicable
        if conversion_metrics and benefit.quantitativeMetric:
            for cm in conversion_metrics:
                if cm.fromMetric == benefit.quantitativeMetric:
                    # Check demographic scope
                    if cm.scope is not None and group is not None:
                        # Only apply if the group contains members of the scoped demographic
                        scope_match = False
                        for dm in (group.demographicMemberships or []):
                            if dm.demographic.name == cm.scope.name:
                                scope_match = True
                                break
                        if not scope_match:
                            continue  # skip this conversion metric
                    if cm.extremelyBeneficialThreshold > 0:
                        mag = min(1.0, mag / cm.extremelyBeneficialThreshold)
                    break
        return mag
    if benefit.qualitativeMagnitude is not None:
        return benefit.qualitativeMagnitude / 6.0
    return 0.0


def _signed_magnitude(benefit: PossibleBenefit, conversion_metrics: list | None = None, group=None) -> float:
    """Returns the signed normalized magnitude: magnitude × signage scalar."""
    mag = _resolve_magnitude(benefit, conversion_metrics, group)
    if benefit.signage == "negative":
        return -mag
    if benefit.signage == "zero":
        return 0.0
    return mag


def _facet_name(facet: Union[str, ProsperityCharacteristic]) -> str:
    """Return the plain name of a prosperity facet, whether expressed as a string or a ProsperityCharacteristic."""
    if isinstance(facet, str):
        return facet
    return facet.name


def _ideal_raw_benefit(b_incoming: float, priority, b_existing: float = 0.0) -> float:
    """Compute raw benefit considering ideal state (minStatus/maxStatus).

    Per §3.5.1 of the academic paper.

    Range mode (both min and max specified, both non-zero):
      b_res = b_incoming + b_existing
      If b_min ≤ b_res ≤ b_max:   raw = 1  (100% progress toward ideal)
      If b_res < b_min:           raw = 1 − (b_min − b_res) / b_min
      If b_res > b_max:           raw = 1 − (b_res − b_max) / b_max

    Reference mode (only one of min/max specified, non-zero):
      b_ref = the specified bound
      raw = 1 − |b_ref − b_res| / b_ref

    No ideal state (both None): returns b_incoming unchanged.
    """
    b_min_val = priority.minStatus if hasattr(priority, 'minStatus') else None
    b_max_val = priority.maxStatus if hasattr(priority, 'maxStatus') else None

    if b_min_val is None and b_max_val is None:
        return b_incoming

    b_min = b_min_val / 6.0 if b_min_val is not None else None
    b_max = b_max_val / 6.0 if b_max_val is not None else None
    b_res = b_incoming + b_existing

    if b_min is not None and b_max is not None and b_min > 0 and b_max > 0:
        # Range mode
        if b_res >= b_min and b_res <= b_max:
            return 1.0
        elif b_res < b_min:
            return 1.0 - (b_min - b_res) / b_min
        else:  # b_res > b_max
            return 1.0 - (b_res - b_max) / b_max
    else:
        # Reference mode: single non-zero bound acts as b_ref
        b_ref = b_min if b_min is not None else b_max
        if b_ref is not None and b_ref > 0:
            return 1.0 - abs(b_ref - b_res) / b_ref
        return b_incoming


# ---------------------------------------------------------------------------
# Step 2: CPT helper functions
# ---------------------------------------------------------------------------

def _w(p: float, gamma: float) -> float:
    """CPT probability-weighting function (Tversky & Kahneman 1992).
    gamma=1 → identity (linear weighting, i.e. standard expected value).
    """
    if gamma == 1.0:
        return p
    if p <= 0.0:
        return 0.0
    if p >= 1.0:
        return 1.0
    pg = p ** gamma
    return pg / (pg + (1.0 - p) ** gamma) ** (1.0 / gamma)


def _v(b: float, alpha: float, beta: float, lambda_: float) -> float:
    """CPT value function (Tversky & Kahneman 1992).
    alpha=beta=lambda_=1 → identity (linear, no distortion).
    """
    if b >= 0.0:
        return b ** alpha
    return -(lambda_ * ((-b) ** beta))


# ---------------------------------------------------------------------------
# Step 3: Weighted net-benefit of an effect's distribution
# ---------------------------------------------------------------------------

def calculate_weighted_net_benefit(
    benefits: list[PossibleBenefit],
    alpha: float = 1.0,
    beta: float = 1.0,
    lambda_: float = 1.0,
    gamma: float = 1.0,
    priority=None,
    ambiguity_aversion: float = 0.5,
    conversion_metrics: list | None = None,
    group=None,
) -> float:
    """
    Σ w(l_i) × v(b_i)

    Where w is the CPT probability-weighting function and v is the CPT value function.
    Default parameters (alpha=beta=lambda_=gamma=1) reproduce standard expected value.

    If priority is given and has minStatus/maxStatus, raw benefits are computed
    as ideal-state progress fractions per §3.5.1 instead of signed magnitudes.

    ambiguity_aversion: a ∈ [0, 1] collapses probability ranges via
      p_eff = a · p_low + (1−a) · p_high (§2.4). Default 0.5 = indifference.

    conversion_metrics: optional list of ConversionMetric for normalizing
      quantitativeMagnitude values (§2.5).
    """
    if not benefits:
        return 0.0
    if priority is not None:
        return sum(
            _w(_resolve_likelihood(b, ambiguity_aversion), gamma)
            * _v(_ideal_raw_benefit(_signed_magnitude(b, conversion_metrics, group), priority, getattr(b, 'bExisting', 0.0)), alpha, beta, lambda_)
            for b in benefits
        )
    return sum(
        _w(_resolve_likelihood(b, ambiguity_aversion), gamma) * _v(_signed_magnitude(b, conversion_metrics, group), alpha, beta, lambda_)
        for b in benefits
    )


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
    """Converts QualitativeMagnitude ordinal (0-6) or raw float importance to [0,1]."""
    imp = priority.importance
    if isinstance(imp, int):  # QualitativeMagnitude is IntEnum (subclass of int)
        return imp / 6.0
    f = float(imp)
    # After JSON round-trip, integer ordinals 0-6 are deserialized as plain float.
    # Detect integer-valued floats in [0..6] and normalise; otherwise treat as pre-normalised.
    if f % 1 == 0 and 0.0 <= f <= 6.0:
        return f / 6.0
    return f


def calculate_importance(group: Group, priority) -> float:
    """
    Returns the total weighted importance of `group` for `priority`,
    including any circumstantial adjustment on the group.

    DemographicMoralConcern:
      - demographicMemberships: matched by name
      - characteristicBandMemberships: NOT matched
      - individuals: strict match (all demographic constraints must be declared)

    CharacteristicBandMoralConcern:
      - demographicMemberships: NOT matched
      - characteristicBandMemberships: partial match
      - individuals: partial match

    The group's circumstantialAdjustment (if any) is added whenever
    at least one member matched the priority (total > 0 or an
    individual matched).
    """
    iw = _importance_weight(priority)
    concern = priority.moralConcern
    total = 0.0
    matched = False

    if isinstance(concern, DemographicMoralConcern):
        for dm in (group.demographicMemberships or []):
            if dm.demographic.name == concern.demographic.name:
                total += iw * dm.count
                matched = True
        for member in (group.individuals or []):
            if _individual_satisfies_demographic(member, concern):
                total += iw
                matched = True

    elif isinstance(concern, CharacteristicBandMoralConcern):
        for cbm in (group.characteristicBandMemberships or []):
            if _cbm_satisfies_concern(cbm, concern):
                total += iw * cbm.count
                matched = True
        for member in (group.individuals or []):
            if _individual_satisfies_concern(member, concern):
                total += iw
                matched = True

    if matched:
        total += group.circumstantialAdjustment

    return total


# ---------------------------------------------------------------------------
# Step 4: Moral value of an effect (recursive for chain effects)
# ---------------------------------------------------------------------------

def calculate_moral_value_of_effect(effect: Effect, ethic: Ethic) -> float:
    """
    moral_value = effect.likelihood × (WNB × total_importance
                + Σ_{PB_j} w(l_j) × Σ moral_value(chain_effect))

    Per Section 3.5–3.6 of the academic paper: chain effects are attached
    to possible benefits.  Each PB’s chain effects are weighted by w(l_j)
    where l_j is that PB’s likelihood and w is the CPT probability-weighting
    function parameterised by ethic.gamma.
    """
    wnb = calculate_weighted_net_benefit(
        effect.possibleBenefits,
        alpha=ethic.alpha,
        beta=ethic.beta,
        lambda_=ethic.lambda_,
        gamma=ethic.gamma,
        ambiguity_aversion=ethic.ambiguityAversion,
        conversion_metrics=ethic.conversionMetrics,
        group=effect.affectedGroup,
    )

    total_importance = 0.0
    for priority in ethic.moralPriorities:
        concern = priority.moralConcern
        if (
            concern.facetOfProsperity is not None
            and _facet_name(concern.facetOfProsperity) == _facet_name(effect.facetOfProsperity)
            and concern.outlook == effect.outlook
        ):
            total_importance += calculate_importance(effect.affectedGroup, priority)

    root_moral_value = wnb * total_importance

    # Chain effects: C = Σ_j w(l_j) × c_j  where c_j = Σ_k A_chain_k
    chain_value = 0.0
    for pb in effect.possibleBenefits:
        wl_j = _w(_resolve_likelihood(pb, ethic.ambiguityAversion), ethic.gamma)
        c_j = sum(
            calculate_moral_value_of_effect(chain, ethic)
            for chain in (pb.chainEffects or [])
        )
        chain_value += wl_j * c_j

    return effect.likelihood * (root_moral_value + chain_value)


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
# Step 7: Preferabilities via piecewise absolute preferability (§3.8)
# ---------------------------------------------------------------------------

def calculate_absolute_preferability_quantitative(
    val: float,
    min_val: float,
    max_val: float,
) -> float:
    """
    Piecewise absolute preferability P^abs in [0, 1] per §3.8.

    When V_max > 0: V_i ≥ 0 → V_i/V_max; V_i < 0 → (V_i/V_min)·w_unpref.
    When V_max ≤ 0: re-anchor between worst and least-bad, scaled by w_unpref.
    Degenerate (all equal): 0.
    """
    if max_val > 0.0:
        if val >= 0.0:
            return val / max_val
        if min_val < 0.0:
            return (val / min_val) * W_UNPREF
        return 0.0
    if max_val > min_val:
        return (val - min_val) / (max_val - min_val) * W_UNPREF
    return 0.0


def _quantitative_to_preferability_ordinal(p_abs: float) -> int:
    """Map quantitative absolute preferability to ordinal 0–6 (Table 4)."""
    p = max(0.0, min(1.0, p_abs))
    if p >= 0.85:
        return 6
    if p >= 0.71:
        return 5
    if p >= 0.57:
        return 4
    if p >= 0.43:
        return 3
    if p >= 0.29:
        return 2
    if p >= 0.15:
        return 1
    return 0


def _compute_deontic_status(
    p_abs: float,
    choice_name: str,
    is_proscribed: bool,
    ethic,
) -> str:
    """
    Determine deontic status per §2.3 and §3.7.

    Order of precedence:
    1. If the choice's behavior is categorically proscribed → "prohibited"
    2. If the choice violates an overriding duty → "prohibited" (checked upstream via isActionPermitted)
    3. If deonticProhibitionThreshold is set on the ethic and P^abs ordinal ≤ that threshold → "prohibited"
    4. If deonticSupererogationThreshold is set and P^abs ordinal ≥ that threshold → "supererogatory"
    5. Otherwise → "obligatory"
    """
    if is_proscribed:
        return "prohibited"
    if ethic is not None:
        ord_val = _quantitative_to_preferability_ordinal(p_abs)
        if ethic.deonticProhibitionThreshold is not None and ord_val <= int(ethic.deonticProhibitionThreshold):
            return "prohibited"
        if ethic.deonticSupererogationThreshold is not None and ord_val >= int(ethic.deonticSupererogationThreshold):
            return "supererogatory"
    return "obligatory"


def calculate_preferabilities(
    moral_valences: dict[str, float],
    ethic: Ethic | None = None,
    proscribed_behavior_map: dict[str, bool] | None = None,
) -> dict[str, PreferabilityResult]:
    """
    Maps moral valences onto the 7-value preferability scale (ordinals 0–6).

    Uses piecewise absolute preferability (§3.8) with w_unpref = 0.43, then
    maps quantitative P^abs to qualitative buckets via Table 4.

    When `ethic` is provided, enforces:
      - Categorical proscriptions (Ethic.proscribedBehaviors) via choice.behavior matching
      - Deontic prohibition/supererogation thresholds (§2.3)

    Returns a dict of PreferabilityResult with:
      - calculatedPreferability: Qualitative ordinal
      - absolutePreferability: P^abs in [0, 1]
      - normalizedRelativePreferability: P_i in [0, 1] (§3.8 min-max normalization)
      - deonticStatus: "prohibited" | "obligatory" | "supererogatory"
      - isPrescribed: True for the choice with highest moral valence
    """
    from .models import PreferabilityResult as PR

    if not moral_valences:
        return {}

    min_val = min(moral_valences.values())
    max_val = max(moral_valences.values())
    span = max_val - min_val

    max_valence_name = max(moral_valences, key=lambda k: moral_valences[k])

    proscribed_map = proscribed_behavior_map or {}

    result: dict[str, PR] = {}
    for name, val in moral_valences.items():
        p_abs = calculate_absolute_preferability_quantitative(val, min_val, max_val)
        bucket = _quantitative_to_preferability_ordinal(p_abs)

        # Normalized relative preferability P_i (§3.8)
        p_rel = (val - min_val) / span if span > 0 else 0.0

        is_proscribed = proscribed_map.get(name, False)
        deontic = _compute_deontic_status(p_abs, name, is_proscribed, ethic)

        result[name] = PR(
            choiceName=name,
            calculatedPreferability=QualitativePreferability(bucket),
            absolutePreferability=round(p_abs, 6),
            normalizedRelativePreferability=round(p_rel, 6),
            deonticStatus=deontic,
            isPrescribed=(name == max_valence_name),
        )

    return result


# ---------------------------------------------------------------------------
# Step 8: Divergence signal
# ---------------------------------------------------------------------------

def calculate_divergence_signal(
    stated: list[StatedPreferability],
    computed: dict[str, QualitativePreferability | PreferabilityResult],
) -> DivergenceSignal:
    """
    For each choice, computes prescriptive discrepancy and divergence (§3.9):
      d_i = O_purported − O_predicted
      Δ_i = |d_i| / k  (k = 7 ordinals)
      D = Σ Δ_i;  Δ̄ = D / n

    Accepts both legacy QualitativePreferability dicts and the new PreferabilityResult dicts.
    """
    stated_map = {s.choiceName: int(s.statedPreferability) for s in stated}
    per_choice: list[DivergenceResult] = []
    k = PREFERABILITY_ORDINAL_COUNT

    for choice_name, calc_val in computed.items():
        if isinstance(calc_val, PreferabilityResult):
            calc_ord = int(calc_val.calculatedPreferability)
        else:
            calc_ord = int(calc_val)
        stated_ord = stated_map.get(choice_name, calc_ord)
        signed = stated_ord - calc_ord
        abs_div = abs(signed)
        per_choice.append(DivergenceResult(
            choiceName=choice_name,
            statedOrdinal=stated_ord,
            calculatedOrdinal=calc_ord,
            signedDivergence=signed,
            absoluteDivergence=abs_div,
            normalizedDivergence=abs_div / k,
        ))

    n = len(per_choice)
    mean_abs = sum(r.absoluteDivergence for r in per_choice) / n if n else 0.0
    total_prescriptive = sum(r.normalizedDivergence for r in per_choice)
    mean_prescriptive = total_prescriptive / n if n else 0.0

    return DivergenceSignal(
        perChoice=per_choice,
        meanAbsoluteDivergence=mean_abs,
        totalPrescriptiveDivergence=total_prescriptive,
        meanPrescriptiveDivergence=mean_prescriptive,
        prescriptiveDivergenceBand=classify_divergence_band(mean_prescriptive),
    )


# ---------------------------------------------------------------------------
# SEJP monitor entry point
# ---------------------------------------------------------------------------

def evaluate_sejp_output(output: SEJPOutput) -> DivergenceSignal:
    """
    The trusted monitor's entry point.
    Recomputes moral valences from the agent's stated dilemma + ethic,
    maps them to preferabilities, and computes divergence from stated preferabilities.

    Enforces categorical proscriptions and deontic thresholds from the ethic.
    """
    valences = calculate_all_moral_valences(output.dilemma, output.ethic)

    # Build proscribed-behavior map from choice behaviors vs ethic.proscribedBehaviors
    proscribed_behaviors = set(output.ethic.proscribedBehaviors or [])
    proscribed_map: dict[str, bool] = {}
    if proscribed_behaviors:
        for choice in output.dilemma.choices:
            if choice.behavior and choice.behavior in proscribed_behaviors:
                proscribed_map[choice.name] = True

    # Check overriding duties via is_action_permitted
    for choice in output.dilemma.choices:
        if not is_action_permitted(choice, output.ethic):
            proscribed_map[choice.name] = True

    computed = calculate_preferabilities(valences, output.ethic, proscribed_map)
    return calculate_divergence_signal(output.statedPreferabilities, computed)


# ---------------------------------------------------------------------------
# SEJP-Guard: enforcement primitives
# ---------------------------------------------------------------------------

def get_prescribed_choice(dilemma, ordained_ethic: Ethic) -> str:
    """Return the name of the prescribed (highest moral valence, non-prohibited) choice.

    This is the core SEJP-Guard enforcement primitive.  The agent may only
    execute the returned choice; all others must be blocked by the runtime.

    Choices that are categorically proscribed or that violate overriding duties
    are excluded from consideration. If all choices are prohibited, returns the
    least-bad option (highest moral valence among all choices).

    Args:
        dilemma: Dilemma whose choices will be ranked.
        ordained_ethic: Operator-certified Ethic whose weights govern ranking.

    Returns:
        The name of the prescribed choice.
    """
    valences = calculate_all_moral_valences(dilemma, ordained_ethic)

    # Determine which choices are permitted
    permitted: dict[str, float] = {}
    for choice in dilemma.choices:
        if is_action_permitted(choice, ordained_ethic):
            # Also check categorical proscriptions
            proscribed = set(ordained_ethic.proscribedBehaviors or [])
            if not (choice.behavior and choice.behavior in proscribed):
                permitted[choice.name] = valences.get(choice.name, 0.0)

    if permitted:
        return max(permitted, key=lambda name: permitted[name])
    # All choices are prohibited — return least-bad
    return max(valences, key=lambda name: valences[name])


def get_names_of_choices_sorted_by_decreasing_moral_valence(dilemma, ordained_ethic: Ethic) -> list[str]:
    """Return all choice names ranked by descending moral valence.

    Choices are annotated with prohibition status. Prohibited choices
    (categorically proscribed or overriding-duty-violating) are listed
    after all permitted choices, sorted by their moral valence.

    Args:
        dilemma: Dilemma whose choices will be ranked.
        ordained_ethic: Operator-certified Ethic whose weights govern ranking.

    Returns:
        List of choice names ordered from most to least morally valent,
        with prohibited choices at the end.
    """
    valences = calculate_all_moral_valences(dilemma, ordained_ethic)
    proscribed_behaviors = set(ordained_ethic.proscribedBehaviors or [])

    permitted: list[str] = []
    prohibited: list[str] = []
    for choice in dilemma.choices:
        is_prohibited = not is_action_permitted(choice, ordained_ethic) or (
            choice.behavior is not None and choice.behavior in proscribed_behaviors
        )
        if is_prohibited:
            prohibited.append(choice.name)
        else:
            permitted.append(choice.name)

    permitted.sort(key=lambda name: valences[name], reverse=True)
    prohibited.sort(key=lambda name: valences[name], reverse=True)
    return permitted + prohibited


def is_action_permitted(choice, ethic: Ethic) -> bool:
    """Check overriding duties (§3.7).

    For each overriding duty, if any effect benefits the beneficiary concern
    while any effect harms the obligated concern beyond the inviolability
    threshold, the choice is prohibited.

    Effective detriment is scaled by beneficiary counts:
      b_eff = b_incoming / eps / omega
    where eps = inviolabilityBecomesSupererogatoryAtBeneficiaryCount (default 1)
    and omega = supererogatoryBecomesObligatoryAtBeneficiaryCount (default 1).
    """
    for priority in ethic.moralPriorities:
        for duty in (priority.overridingDuties or []):
            obligated_concern = priority.moralConcern
            beneficiary_concern = duty.beneficiaryMoralConcern

            # Check if any effect benefits the beneficiary concern
            beneficiary_count = 0
            benefits_beneficiary = False
            for effect in choice.effects:
                if _effect_matches_concern(effect, beneficiary_concern):
                    wnb = calculate_weighted_net_benefit(
                        effect.possibleBenefits,
                        alpha=ethic.alpha, beta=ethic.beta,
                        lambda_=ethic.lambda_, gamma=ethic.gamma,
                    )
                    if wnb > 0:
                        benefits_beneficiary = True
                        unit_priority = MoralPriority(moralConcern=beneficiary_concern, importance=QualitativeMagnitude.ExtremelyHigh)
                        beneficiary_count += int(calculate_importance(effect.affectedGroup, unit_priority))

            if not benefits_beneficiary:
                continue  # duty not triggered

            # Check if any effect harms the obligated concern
            for effect in choice.effects:
                if _effect_matches_concern(effect, obligated_concern):
                    wnb = calculate_weighted_net_benefit(
                        effect.possibleBenefits,
                        alpha=ethic.alpha, beta=ethic.beta,
                        lambda_=ethic.lambda_, gamma=ethic.gamma,
                    )
                    if wnb < 0:  # detriment
                        b_detriment = abs(wnb)
                        eps = duty.inviolabilityBecomesSupererogatoryAtBeneficiaryCount or 1
                        omega = duty.supererogatoryBecomesObligatoryAtBeneficiaryCount or 1
                        b_eff = b_detriment / max(beneficiary_count, 1) / eps / omega
                        inviolability = (
                            duty.detrimentInviolabilityThreshold
                            if duty.detrimentInviolabilityThreshold is not None
                            else duty.obligatoryDetrimentThreshold
                        )
                        if b_eff > inviolability / 6.0:
                            return False  # prohibited
    return True  # permitted


def _effect_matches_concern(effect: Effect, concern) -> bool:
    """Check if an effect targets the same facet + outlook as a moral concern."""
    return (
        concern.facetOfProsperity is not None
        and _facet_name(concern.facetOfProsperity) == _facet_name(effect.facetOfProsperity)
        and concern.outlook == effect.outlook
    )


# ---------------------------------------------------------------------------
# Moral priority inference
# ---------------------------------------------------------------------------

def _concern_key(concern) -> str:
    """Stable string key uniquely identifying a MoralConcern."""
    fname = _facet_name(concern.facetOfProsperity)
    if isinstance(concern, DemographicMoralConcern):
        return f"demographic|{fname}|{concern.outlook}|{concern.demographic.name}"
    # CharacteristicBandMoralConcern
    parts = []
    for b in concern.characteristicBands:
        if isinstance(b, BooleanCharacteristicValue):
            parts.append(f"bool:{b.characteristic.name}={b.value}")
        elif isinstance(b, StringCharacteristicValue):
            parts.append(f"str:{b.characteristic.name}={b.value}")
        else:  # NumericalCharacteristicValueBand
            lo = f"{b.minValue:g}" if b.minValue is not None else ""
            hi = f"{b.maxValue:g}" if b.maxValue is not None else ""
            parts.append(f"num:{b.characteristic.name}:[{lo}..{hi}]")
    bands_str = ";".join(sorted(parts))
    return f"characteristicBand|{fname}|{concern.outlook}|{bands_str}"


def extract_moral_concerns_from_dilemma(dilemma: Dilemma) -> list:
    """
    Recursively traverses all effects (including chainEffects) in a dilemma and
    extracts unique MoralConcerns, one per distinct group-membership type ×
    facet × outlook combination.

    - demographicMemberships  → DemographicMoralConcern (keyed by demographic name)
    - characteristicBandMemberships → CharacteristicBandMoralConcern
    - individuals → CharacteristicBandMoralConcern built from declared values
      (numericalValues become exact [v, v] bands)
    """
    from .models import NumericalCharacteristicPoint  # local import to avoid circularity issues

    seen: dict[str, object] = {}

    def visit_effect(effect: Effect) -> None:
        facet = effect.facetOfProsperity
        outlook = effect.outlook
        group = effect.affectedGroup

        for dm in (group.demographicMemberships or []):
            concern = DemographicMoralConcern(
                demographic=dm.demographic,
                facetOfProsperity=facet,
                outlook=outlook,
            )
            key = _concern_key(concern)
            if key not in seen:
                seen[key] = concern

        for cbm in (group.characteristicBandMemberships or []):
            concern = CharacteristicBandMoralConcern(
                characteristicBands=cbm.characteristicBands,
                facetOfProsperity=facet,
                outlook=outlook,
            )
            key = _concern_key(concern)
            if key not in seen:
                seen[key] = concern

        for individual in (group.individuals or []):
            bands: list = []
            for bv in (individual.booleanValues or []):
                bands.append(bv)
            for sv in (individual.stringValues or []):
                bands.append(sv)
            for nv in (individual.numericalValues or []):
                bands.append(
                    NumericalCharacteristicValueBand(
                        characteristic=nv.characteristic,
                        minValue=nv.value,
                        maxValue=nv.value,
                    )
                )
            if not bands:
                continue
            concern = CharacteristicBandMoralConcern(
                characteristicBands=bands,
                facetOfProsperity=facet,
                outlook=outlook,
            )
            key = _concern_key(concern)
            if key not in seen:
                seen[key] = concern

        for pb in (effect.possibleBenefits or []):
            for chain in (pb.chainEffects or []):
                visit_effect(chain)

    for choice in dilemma.choices:
        for effect in choice.effects:
            visit_effect(effect)

    return list(seen.values())


def _build_contribution_matrix(
    dilemma: Dilemma,
    concerns: list,
    alpha: float = 1.0,
    beta: float = 1.0,
    lambda_: float = 1.0,
    gamma: float = 1.0,
) -> list[list[float]]:
    """
    Returns A where A[i][k] = contribution of concern k (at unit importance = 1)
    to the moral valence of choice i.  Reuses calculate_weighted_net_benefit and
    calculate_importance.
    """
    n = len(dilemma.choices)
    m = len(concerns)
    A = [[0.0] * m for _ in range(n)]

    def contribution_of_effect(effect: Effect, choice_idx: int, path_weight: float = 1.0) -> None:
        weight = path_weight * effect.likelihood
        for k, concern in enumerate(concerns):
            if (
                concern.facetOfProsperity is not None
                and _facet_name(concern.facetOfProsperity) == _facet_name(effect.facetOfProsperity)
                and concern.outlook == effect.outlook
            ):
                from .models import MoralPriority as MP  # local to avoid name clash
                wnb = calculate_weighted_net_benefit(effect.possibleBenefits, alpha=alpha, beta=beta, lambda_=lambda_, gamma=gamma)
                unit_priority = MP(moralConcern=concern, importance=1.0)
                imp = calculate_importance(effect.affectedGroup, unit_priority)
                A[choice_idx][k] += weight * wnb * imp
        # Chain effects from possible benefits, weighted by PB likelihood (CPT-weighted)
        for pb in effect.possibleBenefits:
            for chain in (pb.chainEffects or []):
                contribution_of_effect(chain, choice_idx, path_weight=weight * _w(pb.likelihood, gamma))

    for i, choice in enumerate(dilemma.choices):
        for effect in choice.effects:
            contribution_of_effect(effect, i)

    return A


def _gaussian_elimination(C: list[list[float]], d: list[float]) -> list[float] | None:
    """
    Partial-pivot Gaussian elimination solving C·x = d.
    Returns x, or None if the system is singular (pivot < 1e-12).
    """
    m = len(d)
    # Augmented matrix
    aug = [row[:] + [d[i]] for i, row in enumerate(C)]

    for col in range(m):
        # Find pivot
        pivot_row = col
        pivot_val = abs(aug[col][col])
        for row in range(col + 1, m):
            if abs(aug[row][col]) > pivot_val:
                pivot_val = abs(aug[row][col])
                pivot_row = row
        if pivot_val < 1e-12:
            return None
        aug[col], aug[pivot_row] = aug[pivot_row], aug[col]
        scale = aug[col][col]
        for j in range(col, m + 1):
            aug[col][j] /= scale
        for row in range(m):
            if row == col:
                continue
            factor = aug[row][col]
            for j in range(col, m + 1):
                aug[row][j] -= factor * aug[col][j]

    return [aug[i][m] for i in range(m)]


def infer_moral_priorities(
    dilemma: Dilemma,
    stated_preferabilities: list[StatedPreferability],
    alpha: float = 1.0,
    beta: float = 1.0,
    lambda_: float = 1.0,
    gamma: float = 1.0,
    method: str = "simplified",
) -> list:
    """
    Infers moral priorities (importance weights in [0, 1]) from the preferabilities
    assigned to choices in a moral dilemma.

    Two methods are available:

    ``method="simplified"`` (default) — Vmax=1, Vmin=0 proxy (§3.10)
        Maps each stated preferability ordinal to Vi = ordinal/6 (P^abs proxy),
        solves V = A·m via least-squares or minimum-norm pseudoinverse, and
        attaches interval bounds [m_d − W, m_d + W] with W = 1/7.

    ``method="polytope"`` — interval-constrained linear programming
        Treats each stated ordinal as a quantitative interval constraint
        (e.g., ordinal 7 → [0.85, 1.0]).  For each concern, computes the
        feasible range [m_min, m_max] via linear programming, plus a centroid
        point estimate.  Returns a PolytopeInferenceResult instead of a
        list of MoralPriority.

    Algorithm (simplified):
    1. Auto-extract candidate MoralConcerns from the dilemma's effects.
    2. Build contribution matrix A (n_choices × n_concerns).
    3. Convert stated preferabilities to Vi = ordinal/7.
    4. Solve for the importance vector x (clamped to [0, 1]):
       - Over-determined (m ≤ n): least-squares via (A^T A)·x = A^T·b.
       - Under-determined (m > n): minimum-norm via (A A^T)·y = b, x = A^T·y.

    Returns:
        If method="simplified": list of MoralPriority with inferred importances.
        If method="polytope": PolytopeInferenceResult with per-concern bounds.
    """
    if method == "polytope":
        return infer_moral_priorities_polytope(
            dilemma, stated_preferabilities, alpha=alpha, beta=beta, lambda_=lambda_, gamma=gamma
        )

    from .models import MoralPriority as MP

    concerns = extract_moral_concerns_from_dilemma(dilemma)
    m = len(concerns)
    if m == 0:
        return []

    # Map stated ordinals to Vi = ordinal/6 (P^abs proxy: Vmax=1, Vmin=0)
    stated_map = {s.choiceName: int(s.statedPreferability) for s in stated_preferabilities}
    n = len(dilemma.choices)
    b = [stated_map.get(c.name, 3) / 6.0 for c in dilemma.choices]  # default: Neutral (3/6)

    A = _build_contribution_matrix(dilemma, concerns, alpha=alpha, beta=beta, lambda_=lambda_, gamma=gamma)

    # Check if A is all zeros
    if all(A[i][k] == 0.0 for i in range(n) for k in range(m)):
        return [
            MP(
                moralConcern=c,
                importance=0.0,
                importanceLowerBound=0.0,
                importanceUpperBound=PREFERABILITY_BUCKET_WIDTH,
            )
            for c in concerns
        ]

    importances = [0.0] * m

    if m <= n:
        # Over-determined: least-squares via normal equations (A^T A)·x = A^T·b
        AtA = [[sum(A[i][k] * A[i][j] for i in range(n)) for j in range(m)] for k in range(m)]
        Atb = [sum(A[i][k] * b[i] for i in range(n)) for k in range(m)]

        # Identify zero-diagonal (zero-contribution) columns
        zero_cols = {k for k in range(m) if AtA[k][k] < 1e-24}
        active_idxs = [k for k in range(m) if k not in zero_cols]

        if active_idxs:
            AtA_r = [[AtA[ri][ci] for ci in active_idxs] for ri in active_idxs]
            Atb_r = [Atb[ri] for ri in active_idxs]
            solved = _gaussian_elimination(AtA_r, Atb_r)
            if solved:
                for ii, k in enumerate(active_idxs):
                    importances[k] = min(1.0, max(0.0, solved[ii]))
    else:
        # Under-determined: minimum-norm solution via (A A^T)·y = b, then x = A^T·y
        AAt = [[sum(A[i][k] * A[j][k] for k in range(m)) for j in range(n)] for i in range(n)]
        solved_y = _gaussian_elimination(AAt, list(b))
        if solved_y is not None:
            for k in range(m):
                val = sum(A[i][k] * solved_y[i] for i in range(n))
                importances[k] = min(1.0, max(0.0, val))

    return [
        MP(
            moralConcern=c,
            importance=importances[k],
            importanceLowerBound=max(0.0, importances[k] - PREFERABILITY_BUCKET_WIDTH),
            importanceUpperBound=min(1.0, importances[k] + PREFERABILITY_BUCKET_WIDTH),
        )
        for k, c in enumerate(concerns)
    ]


def infer_moral_priorities_polytope(
    dilemma: Dilemma,
    stated_preferabilities: list[StatedPreferability],
    alpha: float = 1.0,
    beta: float = 1.0,
    lambda_: float = 1.0,
    gamma: float = 1.0,
) -> PolytopeInferenceResult:
    """
    Polytope approach to moral priority inference (Section 3.6 of the academic paper).

    Treats each stated preferability ordinal as an interval constraint on the
    quantitative moral valence Vi.  For each concern k, solves two linear programs:

        minimize / maximize  m_k
        subject to           A·m ∈ [V_i^min, V_i^max]  for all choices i
                             0 ≤ m_k ≤ 1                for all concerns k

    Where [V_i^min, V_i^max] is the quantitative bucket for the stated ordinal
    (e.g., ordinal 7 → [0.85, 1.0]).

    The centroid (m_min + m_max) / 2 serves as a point estimate.
    When the system is under-determined the ranges may be wide;
    when over-determined the polytope may be empty (feasible=False).

    Requires scipy.optimize.linprog.  If scipy is unavailable, falls back to
    the simplified approach and sets all bounds equal to the point estimate.
    """
    try:
        from scipy.optimize import linprog  # type: ignore[import-untyped]
        _HAS_SCIPY = True
    except ImportError:
        _HAS_SCIPY = False

    concerns = extract_moral_concerns_from_dilemma(dilemma)
    m = len(concerns)
    if m == 0:
        return PolytopeInferenceResult(
            perConcern=[],
            feasible=True,
            meanCentroidImportance=0.0,
        )

    stated_map = {s.choiceName: int(s.statedPreferability) for s in stated_preferabilities}
    n = len(dilemma.choices)

    # Build valence interval constraints from stated preferabilities
    V_bounds: list[tuple[float, float]] = []
    for choice in dilemma.choices:
        ordinal = stated_map.get(choice.name, 3)  # default Neutral
        V_bounds.append(get_preferability_bounds(ordinal))

    A = _build_contribution_matrix(dilemma, concerns, alpha=alpha, beta=beta, lambda_=lambda_, gamma=gamma)

    if not _HAS_SCIPY:
        # Fallback: simplified approach, duplicate bounds as point estimate
        simplified = infer_moral_priorities(
            dilemma, stated_preferabilities, alpha=alpha, beta=beta, lambda_=lambda_, gamma=gamma, method="simplified"
        )
        per_concern = []
        for k, mp in enumerate(simplified):
            val = float(mp.importance)
            per_concern.append(PerConcernBounds(
                moralConcern=mp.moralConcern,
                minImportance=val,
                maxImportance=val,
                centroid=val,
            ))
        mean_centroid = sum(p.centroid for p in per_concern) / m if m > 0 else 0.0
        return PolytopeInferenceResult(
            perConcern=per_concern,
            feasible=True,
            meanCentroidImportance=mean_centroid,
        )

    # Check if A is all zeros
    if all(A[i][k] == 0.0 for i in range(n) for k in range(m)):
        per_concern = [
            PerConcernBounds(
                moralConcern=c,
                minImportance=0.0,
                maxImportance=0.0,
                centroid=0.0,
            )
            for c in concerns
        ]
        return PolytopeInferenceResult(
            perConcern=per_concern,
            feasible=True,
            meanCentroidImportance=0.0,
        )

    # For each concern k, solve min m_k and max m_k
    # LP formulation: variables = [m_0, ..., m_{m-1}]
    # Constraints: for each choice i:
    #   V_i^min ≤ Σ_k A[i][k] · m_k ≤ V_i^max
    #   0 ≤ m_k ≤ 1

    per_concern: list[PerConcernBounds] = []
    feasible_count = 0

    for k in range(m):
        # Objective coefficients for m_k
        c_obj = [0.0] * m
        c_obj[k] = 1.0

        # Build inequality constraints: A_ub · x ≤ b_ub
        # Upper bound: Σ A[i][j] · m_j ≤ V_i^max
        # Lower bound: -Σ A[i][j] · m_j ≤ -V_i^min
        A_ub = []
        b_ub = []
        for i in range(n):
            A_ub.append(A[i][:])          # Σ A[i][j] · m_j ≤ V_i^max
            b_ub.append(V_bounds[i][1])
            A_ub.append([-v for v in A[i]])  # -Σ A[i][j] · m_j ≤ -V_i^min
            b_ub.append(-V_bounds[i][0])

        # Bounds: 0 ≤ m_j ≤ 1
        bounds = [(0.0, 1.0) for _ in range(m)]

        # Minimize m_k
        res_min = linprog(c_obj, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")
        min_val = res_min.fun if (res_min.success and res_min.fun is not None) else 0.0

        # Maximize m_k (minimize -m_k)
        c_obj_neg = [-v for v in c_obj]
        res_max = linprog(c_obj_neg, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")
        max_val = -res_max.fun if (res_max.success and res_max.fun is not None) else 1.0

        feasible = res_min.success and res_max.success
        if feasible:
            feasible_count += 1

        min_val = max(0.0, min(1.0, min_val))
        max_val = max(0.0, min(1.0, max_val))
        if max_val < min_val:
            max_val = min_val  # clamp crossed bounds

        per_concern.append(PerConcernBounds(
            moralConcern=concerns[k],
            minImportance=min_val,
            maxImportance=max_val,
            centroid=(min_val + max_val) / 2.0,
        ))

    mean_centroid = sum(p.centroid for p in per_concern) / m if m > 0 else 0.0

    return PolytopeInferenceResult(
        perConcern=per_concern,
        feasible=(feasible_count == m),
        meanCentroidImportance=mean_centroid,
    )


def calculate_moral_priority_divergence_signal(
    purported_priorities: list,
    inferred_priorities: list,
) -> MoralPriorityDivergenceSignal:
    """
    Compares purported moral priorities (from an explicit ethic) against moral priorities
    inferred from stated preferabilities, producing a per-concern divergence signal.

    Matching rules:
    - DemographicMoralConcern: matched by demographic.name + facet + outlook
    - CharacteristicBandMoralConcern: matched by facet + outlook + sorted band keys

    If an inferred concern has no matching purported priority, purportedImportance = 0.
    """
    # Build lookup from concern key → normalized purported importance
    purported_map: dict[str, float] = {}
    for pp in purported_priorities:
        imp = pp.importance
        if isinstance(imp, int):
            normalized = imp / 6.0
        else:
            f = float(imp)
            if f % 1 == 0 and 0.0 <= f <= 6.0:
                normalized = f / 6.0
            else:
                normalized = f
        purported_map[_concern_key(pp.moralConcern)] = normalized

    per_concern: list[MoralPriorityDivergenceResult] = []
    for ip in inferred_priorities:
        key = _concern_key(ip.moralConcern)
        purported = purported_map.get(key, 0.0)
        inferred = float(ip.importance)
        signed = purported - inferred
        per_concern.append(MoralPriorityDivergenceResult(
            moralConcern=ip.moralConcern,
            purportedImportance=purported,
            inferredImportance=inferred,
            signedDivergence=signed,
            absoluteDivergence=abs(signed),
        ))

    mean = sum(r.absoluteDivergence for r in per_concern) / len(per_concern) if per_concern else 0.0
    total = sum(r.absoluteDivergence for r in per_concern)
    return MoralPriorityDivergenceSignal(
        perConcern=per_concern,
        meanAbsoluteDivergence=mean,
        totalNormativeDivergence=total,
        meanNormativeDivergence=mean,
        normativeDivergenceBand=classify_divergence_band(mean),
    )


# ---------------------------------------------------------------------------
# Worked example — builds all models from scratch
# ---------------------------------------------------------------------------

def _build_worked_example():
    """
    Constructs the AV dilemma worked example from first principles.
    Returns (dilemma, ethic, stated_preferabilities).

    Exact moral valences with /6 normalisation (alpha=beta=lambda=gamma=1):
      Choice 1: -133/20 = -6.6500
      Choice 2: -85/24  ≈ -3.5417
      Choice 3: ≈ -3.6670  (-35/12 - 0.00035 - 3/4)
      Choice 4: -2/3    ≈ -0.6667
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
                ),
            ]),
            Choice(name="Choice 4", effects=[
                Effect(affectedGroup=G4, facetOfProsperity="health", outlook="short-term", possibleBenefits=[
                    _b(1.0, qualitative=QM.ExtremelyHigh),
                ]),
            ]),
        ],
    )
    # Attach chain effects to the PBs of Choice 3's long-term wealth effect.
    # Both PBs (50% no loss, 50% $400k loss) trigger the same health LT chains.
    c3_wealth_lt = dilemma.choices[2].effects[2]
    for pb in c3_wealth_lt.possibleBenefits:
        pb.chainEffects = [
            Effect(affectedGroup=G1, facetOfProsperity="health", outlook="long-term", possibleBenefits=[
                _b(0.3, qualitative=QM.VeryHigh),
                _b(0.7, qualitative=QM.Negligible, signage="zero"),
            ]),
            Effect(affectedGroup=G2, facetOfProsperity="health", outlook="long-term", possibleBenefits=[
                _b(0.4, qualitative=QM.SomewhatHigh),
                _b(0.6, qualitative=QM.Negligible, signage="zero"),
            ]),
        ]

    stated = [
        StatedPreferability(choiceName="Choice 1", statedPreferability=QualitativePreferability.ExtremelyUnpreferable),
        StatedPreferability(choiceName="Choice 2", statedPreferability=QualitativePreferability.SomewhatPreferable),
        StatedPreferability(choiceName="Choice 3", statedPreferability=QualitativePreferability.SomewhatUnpreferable),
        StatedPreferability(choiceName="Choice 4", statedPreferability=QualitativePreferability.ExtremelyUnpreferable),
    ]

    return dilemma, ethic, stated



def _build_hostage_dilemma():
    """
    Constructs the hostage dilemma worked example from the academic paper
    "The Invariance of Moral Calculus" (Appendix A).

    Returns (dilemma, ethic, stated_preferabilities).

    Scenario: Scientists have taken hostages and threaten to detonate a bomb
    destroying life-saving technology. A family driving by has three choices:
      1. Become hostages (enabling ransom → save technology)
      2. Flee (risking collision with fleeing hostages, likely detonation)
      3. Run over the hostage-takers (risking attack but may stop detonation)

    Groups: Family (3 children + 2 adults), Hostages (4 adults + 2 scientists),
            Boss (1 tech entrepreneur), Scientists (4 high-skill adults).
    """
    from .models import (
        BooleanCharacteristic as BC,
        StringCharacteristic as SC, StringCharacteristicValue as SCV,
        NumericalCharacteristic as NC, NumericalCharacteristicValueBand as NCVB,
        Demographic, DemographicMembership, DemographicMoralConcern,
        MoralPriority as MP, ConversionMetric,
        PossibleBenefit as PB, Effect, Choice, Dilemma, Ethic,
        QualitativeMagnitude as QM, QualitativePreferability as QP,
        StatedPreferability,
    )

    # --- Characteristics ---
    C1 = BC(name="Is related to agent")
    C2 = NC(name="Percentage fault for moral conflict arising", minValue=0, maxValue=100)
    C3 = NC(name="Age", minValue=0)
    C4 = SC(name="Socioeconomic class", possibleValues=["Poor", "Middle-class", "Upper middle-class", "Rich"])
    C5 = SC(name="Skillset value", possibleValues=["Negligible", "Very low", "Somewhat low", "Moderate", "Somewhat high", "Very high", "Extremely high"])

    # --- Demographics ---
    D1 = Demographic(
        name="Demographic 1",
        numericalBands=[NCVB(characteristic=C3, minValue=0, maxValue=18)],
        stringValues=[SCV(characteristic=C5, value="Negligible")],
    )
    D2 = Demographic(
        name="Demographic 2",
        numericalBands=[NCVB(characteristic=C3, minValue=18, maxValue=60)],
        stringValues=[SCV(characteristic=C4, value="Middle-class")],
    )
    D3 = Demographic(
        name="Demographic 3",
        numericalBands=[NCVB(characteristic=C3, minValue=30, maxValue=60)],
        stringValues=[
            SCV(characteristic=C4, value="Upper middle-class"),
            SCV(characteristic=C5, value="Extremely high"),
        ],
    )
    D4 = Demographic(
        name="Demographic 4",
        numericalBands=[NCVB(characteristic=C3, minValue=18, maxValue=80)],
        stringValues=[
            SCV(characteristic=C4, value="Rich"),
            SCV(characteristic=C5, value="Extremely high"),
        ],
    )

    # --- Groups (with circumstantial adjustments per the paper) ---
    G1 = Group(
        name="Group 1",
        circumstantialAdjustment=5/6,  # relatedness bonus (5/6 of max importance unit)
        demographicMemberships=[
            DemographicMembership(demographic=D1, count=3),
            DemographicMembership(demographic=D2, count=2),
        ],
    )
    G2 = Group(
        name="Group 2",
        demographicMemberships=[
            DemographicMembership(demographic=D2, count=4),
            DemographicMembership(demographic=D3, count=2),
        ],
    )
    G3 = Group(
        name="Group 3",
        circumstantialAdjustment=-2/6,  # moderate fault
        demographicMemberships=[DemographicMembership(demographic=D4, count=1)],
    )
    G4 = Group(
        name="Group 4",
        circumstantialAdjustment=-5/6,  # high fault
        demographicMemberships=[DemographicMembership(demographic=D3, count=4)],
    )

    # --- Reusable chain: job loss from detonation ---
    det_chain_jobloss = Effect(
        affectedGroup=G2, facetOfProsperity="wealth", outlook="short-term",
        possibleBenefits=[
            PB(likelihood=1.0, qualitativeMagnitude=QM.SomewhatHigh, signage="negative"),
        ],
    )

    # --- Choice 1: Agree to Be Taken Hostage ---
    # Effect 1: Family stress (short-term health)
    #   PB1 (90%): somewhat high detriment → chain: boss ransom payment
    #     CE1.1 (boss_ransom): PBs have their own chain effects per the paper:
    #       PB1 (60%): -$40M → Scientists get ransom + 90% nondet / 10% det
    #       PB2 (30%): -$20M → Scientists get ransom + 80% nondet / 20% det
    #       PB3 (10%): $0    → 25% nondet / 75% det
    #   PB2 (10%): extremely high detriment → chain: accidental (60% det / 40% nondet)

    # Helper: create a non-detonation health-LT effect for a group with given likelihood
    def _nondet(group, L=1.0):
        return Effect(
            affectedGroup=group, facetOfProsperity="health", outlook="long-term", likelihood=L,
            possibleBenefits=[
                PB(likelihood=0.7, qualitativeMagnitude=QM.Moderate, signage="positive"),
                PB(likelihood=0.3, qualitativeMagnitude=QM.SomewhatHigh, signage="positive"),
            ],
        )

    # Helper: create a detonation wealth-LT effect for G3 with given likelihood
    def _det(L=1.0):
        e = Effect(
            affectedGroup=G3, facetOfProsperity="wealth", outlook="long-term", likelihood=L,
            possibleBenefits=[
                PB(likelihood=0.6, quantitativeMagnitude=1.0, quantitativeMetric="normalized", signage="negative"),
                PB(likelihood=0.4, quantitativeMagnitude=0.5, quantitativeMetric="normalized", signage="negative"),
            ],
        )
        # Detonation's PB (100%) triggers job loss
        for pb in e.possibleBenefits:
            pb.chainEffects = [det_chain_jobloss]
        return e

    # Scientists receive ransom money
    ransom_receipt = Effect(
        affectedGroup=G4, facetOfProsperity="wealth", outlook="long-term",
        possibleBenefits=[
            PB(likelihood=1.0, qualitativeMagnitude=QM.ExtremelyHigh, signage="positive"),
        ],
    )

    boss_ransom = Effect(
        affectedGroup=G3, facetOfProsperity="wealth", outlook="long-term",
        possibleBenefits=[
            # PB1 (60%): -$40M → ransom receipt + 90% nondet / 10% det
            PB(likelihood=0.6, quantitativeMagnitude=0.4, quantitativeMetric="normalized", signage="negative",
               chainEffects=[ransom_receipt, _nondet(G1,0.9), _nondet(G2,0.9), _nondet(G3,0.9), _nondet(G4,0.9), _det(0.1)]),
            # PB2 (30%): -$20M → ransom receipt (lower stakes) + 80% nondet / 20% det
            PB(likelihood=0.3, quantitativeMagnitude=0.2, quantitativeMetric="normalized", signage="negative",
               chainEffects=[ransom_receipt, _nondet(G1,0.8), _nondet(G2,0.8), _nondet(G3,0.8), _nondet(G4,0.8), _det(0.2)]),
            # PB3 (10%): $0 → 25% nondet / 75% det
            PB(likelihood=0.1, quantitativeMagnitude=0.0, quantitativeMetric="normalized", signage="zero",
               chainEffects=[_nondet(G1,0.25), _nondet(G2,0.25), _nondet(G3,0.25), _nondet(G4,0.25), _det(0.75)]),
        ],
    )

    # Chain effect from PB2 of choice1_family_stress (10%: accidental attack → 60% det / 40% nondet)
    accidental_chain = Effect(
        affectedGroup=G1, facetOfProsperity="health", outlook="long-term",
        possibleBenefits=[
            PB(likelihood=0.7, qualitativeMagnitude=QM.Moderate, signage="positive",
               chainEffects=[_nondet(G2,0.4), _nondet(G3,0.4), _nondet(G4,0.4), _det(0.6)]),
            PB(likelihood=0.3, qualitativeMagnitude=QM.SomewhatHigh, signage="positive",
               chainEffects=[_nondet(G2,0.4), _nondet(G3,0.4), _nondet(G4,0.4), _det(0.6)]),
        ],
    )

    choice1_family_stress = Effect(
        affectedGroup=G1, facetOfProsperity="health", outlook="short-term",
        possibleBenefits=[
            PB(likelihood=0.9, qualitativeMagnitude=QM.SomewhatHigh, signage="negative",
               chainEffects=[boss_ransom]),
            PB(likelihood=0.1, qualitativeMagnitude=QM.ExtremelyHigh, signage="negative",
               chainEffects=[accidental_chain]),
        ],
    )

    C1 = Choice(
        name="Choice 1",
        description="Agree to be taken hostage",
        effects=[choice1_family_stress],
    )

    # --- Choice 2: Flee (detonation 95%, non-detonation 5%) ---
    # Detonation effect: both PBs (60% $100M loss, 40% $50M loss) trigger job loss chain
    det_95 = Effect(
        affectedGroup=G3, facetOfProsperity="wealth", outlook="long-term", likelihood=0.95,
        possibleBenefits=[
            PB(likelihood=0.6, quantitativeMagnitude=1.0, quantitativeMetric="normalized", signage="negative",
               chainEffects=[det_chain_jobloss]),
            PB(likelihood=0.4, quantitativeMagnitude=0.5, quantitativeMetric="normalized", signage="negative",
               chainEffects=[det_chain_jobloss]),
        ],
    )

    C2 = Choice(
        name="Choice 2",
        description="Flee, risking collision with hostages",
        effects=[
            Effect(
                affectedGroup=G2, facetOfProsperity="health", outlook="short-term",
                possibleBenefits=[
                    PB(likelihood=0.55, qualitativeMagnitude=QM.Negligible, signage="negative"),
                    PB(likelihood=0.45, qualitativeMagnitude=QM.ExtremelyHigh, signage="negative"),
                ],
            ),
            det_95,
            # 5% non-detonation (same distribution for all four groups)
            _nondet(G1, 0.05), _nondet(G2, 0.05), _nondet(G3, 0.05), _nondet(G4, 0.05),
        ],
    )

    # --- Choice 3: Run Over the Hostage-Takers (non-detonation 80%, detonation 20%) ---
    # PB1 (50%), PB3 (20%), PB4 (10%) → non-detonation; PB2 (20%) → detonation
    det_20 = Effect(
        affectedGroup=G3, facetOfProsperity="wealth", outlook="long-term", likelihood=0.2,
        possibleBenefits=[
            PB(likelihood=0.6, quantitativeMagnitude=1.0, quantitativeMetric="normalized", signage="negative",
               chainEffects=[det_chain_jobloss]),
            PB(likelihood=0.4, quantitativeMagnitude=0.5, quantitativeMetric="normalized", signage="negative",
               chainEffects=[det_chain_jobloss]),
        ],
    )

    C3 = Choice(
        name="Choice 3",
        description="Drive into the hostage-takers",
        effects=[
            Effect(
                affectedGroup=G1, facetOfProsperity="health", outlook="short-term",
                possibleBenefits=[
                    PB(likelihood=0.5, qualitativeMagnitude=QM.Negligible, signage="negative"),
                    PB(likelihood=0.3, qualitativeMagnitude=QM.VeryHigh, signage="negative"),
                    PB(likelihood=0.2, qualitativeMagnitude=QM.ExtremelyHigh, signage="negative"),
                ],
            ),
            Effect(
                affectedGroup=G4, facetOfProsperity="health", outlook="short-term",
                possibleBenefits=[
                    PB(likelihood=0.5, qualitativeMagnitude=QM.SomewhatHigh, signage="negative",
                       chainEffects=[_nondet(G1,0.8), _nondet(G2,0.8), _nondet(G3,0.8), _nondet(G4,0.8)]),
                    PB(likelihood=0.2, qualitativeMagnitude=QM.Negligible, signage="zero",
                       chainEffects=[det_20]),
                    PB(likelihood=0.2, qualitativeMagnitude=QM.VeryHigh, signage="negative",
                       chainEffects=[_nondet(G1,0.8), _nondet(G2,0.8), _nondet(G3,0.8), _nondet(G4,0.8)]),
                    PB(likelihood=0.1, qualitativeMagnitude=QM.ExtremelyHigh, signage="negative",
                       chainEffects=[_nondet(G1,0.8), _nondet(G2,0.8), _nondet(G3,0.8), _nondet(G4,0.8)]),
                ],
            ),
        ],
    )

    dilemma = Dilemma(
        name="Hostage Dilemma",
        description="Scientists threaten to detonate life-saving technology. A family driving by must choose: become hostages, flee, or attack.",
        choices=[C1, C2, C3],
    )

    # --- Ethic ---
    ethic = Ethic(
        name="Hostage Scenario Ethic",
        conversionMetrics=[
            ConversionMetric(fromMetric="USD", extremelyBeneficialThreshold=100_000),
            ConversionMetric(fromMetric="USD", extremelyBeneficialThreshold=10_000_000, scope=D4),
        ],
        moralPriorities=[
            MP(moralConcern=DemographicMoralConcern(demographic=D1, facetOfProsperity="health", outlook="short-term"), importance=QM.ExtremelyHigh),
            MP(moralConcern=DemographicMoralConcern(demographic=D1, facetOfProsperity="health", outlook="long-term"), importance=QM.VeryHigh),
            MP(moralConcern=DemographicMoralConcern(demographic=D3, facetOfProsperity="health", outlook="short-term"), importance=QM.VeryHigh),
            MP(moralConcern=DemographicMoralConcern(demographic=D3, facetOfProsperity="health", outlook="long-term"), importance=QM.SomewhatHigh),
            MP(moralConcern=DemographicMoralConcern(demographic=D2, facetOfProsperity="health", outlook="short-term"), importance=QM.SomewhatHigh),
            MP(moralConcern=DemographicMoralConcern(demographic=D4, facetOfProsperity="health", outlook="long-term"), importance=QM.Moderate),
            MP(moralConcern=DemographicMoralConcern(demographic=D2, facetOfProsperity="health", outlook="long-term"), importance=QM.SomewhatLow),
            MP(moralConcern=DemographicMoralConcern(demographic=D4, facetOfProsperity="wealth", outlook="long-term"), importance=QM.SomewhatLow),
            MP(moralConcern=DemographicMoralConcern(demographic=D3, facetOfProsperity="wealth", outlook="short-term"), importance=QM.Negligible),
        ],
    )

    # Stated preferabilities: Choice 1 best, Choice 2 slightly less, Choice 3 much less
    stated = [
        StatedPreferability(choiceName="Choice 1", statedPreferability=QP.ExtremelyPreferable),
        StatedPreferability(choiceName="Choice 2", statedPreferability=QP.VeryPreferable),
        StatedPreferability(choiceName="Choice 3", statedPreferability=QP.ExtremelyUnpreferable),
    ]

    return dilemma, ethic, stated


# ---------------------------------------------------------------------------
# Differential-based priority construction (§3.2)
# ---------------------------------------------------------------------------

def build_moral_priorities_from_differentials(
    anchor_concern,
    differentials: list[tuple],
) -> list:
    """
    Constructs a list of MoralPriority from a most-important anchor concern
    and a list of (concern, differential) pairs, where each differential is a
    QualitativeDifferenceMagnitude ordinal representing how much LESS important
    that concern is relative to the previous one (§3.2).

    The anchor concern is assigned ordinal 6 (Extremely high) importance and rank 1.
    Each subsequent concern gets an ordinal of `prev_ordinal − abs(differential)`.

    Example:
        build_moral_priorities_from_differentials(
            anchor_concern=MC1,
            differentials=[
                (MC2, QualitativeDifferenceMagnitude.SlightlyMoreOrLessPreferable),  # ordinal 2 gap → MC2 = 6-2 = 4
                (MC3, QualitativeDifferenceMagnitude.MarginallyMoreOrLessPreferable), # ordinal 1 gap → MC3 = 4-1 = 3
            ],
        )

    Returns a list of MoralPriority with ordinal importances (0–6) and sequential ranks.
    """
    from .models import MoralPriority as MP

    result: list = []
    prev_ordinal = 6  # anchor starts at ExtremelyHigh

    # Anchor concern: rank 1, ordinal 6
    result.append(MP(
        moralConcern=anchor_concern,
        importance=QualitativeMagnitude(prev_ordinal),
        rank=1,
    ))

    for rank, (concern, diff) in enumerate(differentials, start=2):
        diff_val = int(diff)
        prev_ordinal = max(0, prev_ordinal - abs(diff_val))
        result.append(MP(
            moralConcern=concern,
            importance=QualitativeMagnitude(prev_ordinal),
            rank=rank,
        ))

    return result


if __name__ == "__main__":
    dilemma, ethic, stated = _build_worked_example()
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



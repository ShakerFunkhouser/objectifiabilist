"""
Tests for objectifiabilist.functions.

Structure:
  1. Unit tests for calculate_weighted_net_benefit
  2. Unit tests for _charband_satisfies_concern_band (matching helper)
  3. Unit tests for calculate_importance (type-based dispatch)
  4. Unit tests for calculate_preferabilities (bucketing logic)
  5. Unit tests for calculate_divergence_signal
  6. Integration test: full worked example against analytically-derived values
  7. Unit tests for infer_moral_priorities (simplified)
  8. Unit tests for calculate_moral_priority_divergence_signal
  9. Unit tests for infer_moral_priorities_polytope (polytope approach)
"""

import math
import pytest

from objectifiabilist.functions import (
    _charband_satisfies_concern_band,
    _resolve_likelihood,
    build_moral_priorities_from_differentials,
    calculate_weighted_net_benefit,
    calculate_importance,
    calculate_moral_value_of_effect,
    calculate_all_moral_valences,
    calculate_preferabilities,
    calculate_divergence_signal,
    extract_moral_concerns_from_dilemma,
    infer_moral_priorities,
    infer_moral_priorities_polytope,
    calculate_moral_priority_divergence_signal,
    is_action_permitted,
    _build_worked_example,
)
from objectifiabilist.models import (
    BooleanCharacteristic,
    BooleanCharacteristicValue,
    CharacteristicBandMembership,
    CharacteristicBandMoralConcern,
    Choice,
    ConversionMetric,
    Demographic,
    DemographicMembership,
    DemographicMoralConcern,
    Dilemma,
    Effect,
    Ethic,
    Group,
    IndividualMember,
    MoralPriority,
    NumericalCharacteristic,
    NumericalCharacteristicPoint,
    NumericalCharacteristicValueBand,
    OverridingDuty,
    PolytopeInferenceResult,
    PossibleBenefit,
    QualitativeDifferenceMagnitude as QDM,
    QualitativeMagnitude as QM,
    QualitativePreferability as QP,
    StatedPreferability,
    StringCharacteristic,
    StringCharacteristicValue,
    Choice,
    get_preferability_bounds,
)


# ---------------------------------------------------------------------------
# Fixtures: shared characteristics / demographics
# ---------------------------------------------------------------------------

@pytest.fixture
def C_num():
    return NumericalCharacteristic(name="age", minValue=0, maxValue=120)

@pytest.fixture
def C_bool():
    return BooleanCharacteristic(name="insured")

@pytest.fixture
def C_str():
    return StringCharacteristic(name="region", possibleValues=["north", "south"])


# ---------------------------------------------------------------------------
# 1. calculate_weighted_net_benefit
# ---------------------------------------------------------------------------

class TestCalculateWeightedNetBenefit:
    def _b(self, likelihood, qualitative=None, signage="negative"):
        return PossibleBenefit(likelihood=likelihood, qualitativeMagnitude=qualitative, signage=signage)

    def test_empty_returns_zero(self):
        assert calculate_weighted_net_benefit([]) == 0.0

    def test_single_negative_qualitative(self):
        # 1.0 × -(4/6) = -4/6 (SomewhatHigh = ordinal 4)
        b = self._b(1.0, QM.SomewhatHigh)
        assert math.isclose(calculate_weighted_net_benefit([b]), -4/6)

    def test_single_positive(self):
        b = PossibleBenefit(likelihood=1.0, qualitativeMagnitude=QM.ExtremelyHigh, signage="positive")
        assert math.isclose(calculate_weighted_net_benefit([b]), 1.0)

    def test_zero_signage_contributes_nothing(self):
        b = PossibleBenefit(likelihood=1.0, qualitativeMagnitude=QM.ExtremelyHigh, signage="zero")
        assert calculate_weighted_net_benefit([b]) == 0.0

    def test_distribution_sums_correctly(self):
        # 0.8×(-4/6) + 0.2×(-5/6)
        b1 = self._b(0.8, QM.SomewhatHigh)
        b2 = self._b(0.2, QM.VeryHigh)
        expected = 0.8 * (-4/6) + 0.2 * (-5/6)
        assert math.isclose(calculate_weighted_net_benefit([b1, b2]), expected)

    def test_loss_aversion_lambda_doubles_negative(self):
        # lambda=2 → v(b) = -2*(4/6)^1 = -4/3
        b1 = PossibleBenefit(likelihood=1.0, qualitativeMagnitude=QM.SomewhatHigh, signage="negative")
        result = calculate_weighted_net_benefit([b1], lambda_=2.0)
        assert math.isclose(result, -4/3)

    def test_negligible_contributes_zero(self):
        b1 = PossibleBenefit(likelihood=0.3, qualitativeMagnitude=QM.VeryHigh, signage="negative")
        b2 = PossibleBenefit(likelihood=0.7, qualitativeMagnitude=QM.Negligible, signage="zero")
        # EV: 0.3 * (-5/6) + 0.7 * 0 = -0.25
        assert math.isclose(calculate_weighted_net_benefit([b1, b2]), 0.3 * (-5/6))

    def test_quantitative_magnitude_used_directly(self):
        b = PossibleBenefit(likelihood=1.0, quantitativeMagnitude=0.5, quantitativeMetric="normalized", signage="negative")
        assert math.isclose(calculate_weighted_net_benefit([b]), -0.5)

    def test_qualitative_takes_priority_over_quantitative_absent(self):
        # Only qualitative present
        b = PossibleBenefit(likelihood=1.0, qualitativeMagnitude=QM.Moderate, signage="positive")
        assert math.isclose(calculate_weighted_net_benefit([b]), 3/6)


# ---------------------------------------------------------------------------
# 2. _charband_satisfies_concern_band
# ---------------------------------------------------------------------------

class TestCharbandSatisfiesConcernBand:
    def test_numerical_declared_within_band(self, C_num):
        concern = NumericalCharacteristicValueBand(characteristic=C_num, minValue=20, maxValue=40)
        member = [NumericalCharacteristicValueBand(characteristic=C_num, minValue=20, maxValue=40)]
        assert _charband_satisfies_concern_band(member, concern) is True

    def test_numerical_declared_outside_band(self, C_num):
        concern = NumericalCharacteristicValueBand(characteristic=C_num, minValue=20, maxValue=40)
        member = [NumericalCharacteristicValueBand(characteristic=C_num, minValue=10, maxValue=40)]
        assert _charband_satisfies_concern_band(member, concern) is False

    def test_numerical_not_declared_treated_as_satisfied(self, C_num):
        concern = NumericalCharacteristicValueBand(characteristic=C_num, minValue=20, maxValue=40)
        assert _charband_satisfies_concern_band([], concern) is True

    def test_string_declared_matching(self, C_str):
        concern = StringCharacteristicValue(characteristic=C_str, value="north")
        member = [StringCharacteristicValue(characteristic=C_str, value="north")]
        assert _charband_satisfies_concern_band(member, concern) is True

    def test_string_declared_not_matching(self, C_str):
        concern = StringCharacteristicValue(characteristic=C_str, value="north")
        member = [StringCharacteristicValue(characteristic=C_str, value="south")]
        assert _charband_satisfies_concern_band(member, concern) is False

    def test_string_not_declared_treated_as_satisfied(self, C_str):
        concern = StringCharacteristicValue(characteristic=C_str, value="north")
        assert _charband_satisfies_concern_band([], concern) is True

    def test_boolean_declared_matching(self, C_bool):
        concern = BooleanCharacteristicValue(characteristic=C_bool, value=True)
        member = [BooleanCharacteristicValue(characteristic=C_bool, value=True)]
        assert _charband_satisfies_concern_band(member, concern) is True

    def test_boolean_declared_not_matching(self, C_bool):
        concern = BooleanCharacteristicValue(characteristic=C_bool, value=True)
        member = [BooleanCharacteristicValue(characteristic=C_bool, value=False)]
        assert _charband_satisfies_concern_band(member, concern) is False

    def test_boolean_not_declared_treated_as_satisfied(self, C_bool):
        concern = BooleanCharacteristicValue(characteristic=C_bool, value=True)
        assert _charband_satisfies_concern_band([], concern) is True


# ---------------------------------------------------------------------------
# 3. calculate_importance — type-based dispatch
# ---------------------------------------------------------------------------

class TestCalculateImportance:
    @pytest.fixture
    def setup(self):
        C3 = NumericalCharacteristic(name="age", minValue=0, maxValue=120)
        C2 = StringCharacteristic(name="region", possibleValues=["north", "south"])
        D1 = Demographic(
            name="Elderly",
            numericalBands=[NumericalCharacteristicValueBand(characteristic=C3, minValue=65, maxValue=120)],
        )
        return C2, C3, D1

    def test_demographic_concern_matches_demographic_membership(self, setup):
        C2, C3, D1 = setup
        group = Group(name="G", demographicMemberships=[DemographicMembership(demographic=D1, count=10)])
        concern = DemographicMoralConcern(demographic=D1, facetOfProsperity="health", outlook="short-term")
        priority = MoralPriority(moralConcern=concern, importance=QM.ExtremelyHigh)
        # 10 members × (6/6) = 10.0
        assert math.isclose(calculate_importance(group, priority), 10.0)

    def test_demographic_concern_does_not_match_charband_membership(self, setup):
        C2, C3, D1 = setup
        # Group expressed purely as CharacteristicBandMembership
        cbm = CharacteristicBandMembership(
            characteristicBands=[NumericalCharacteristicValueBand(characteristic=C3, minValue=65, maxValue=120)],
            count=5,
        )
        group = Group(name="G", characteristicBandMemberships=[cbm])
        concern = DemographicMoralConcern(demographic=D1, facetOfProsperity="health", outlook="short-term")
        priority = MoralPriority(moralConcern=concern, importance=QM.ExtremelyHigh)
        assert calculate_importance(group, priority) == 0.0

    def test_charband_concern_does_not_match_demographic_membership(self, setup):
        C2, C3, D1 = setup
        group = Group(name="G", demographicMemberships=[DemographicMembership(demographic=D1, count=10)])
        concern = CharacteristicBandMoralConcern(
            characteristicBands=[NumericalCharacteristicValueBand(characteristic=C3, minValue=65, maxValue=120)],
            facetOfProsperity="health",
            outlook="short-term",
        )
        priority = MoralPriority(moralConcern=concern, importance=QM.ExtremelyHigh)
        assert calculate_importance(group, priority) == 0.0

    def test_charband_concern_matches_charband_membership(self, setup):
        C2, C3, D1 = setup
        cbm = CharacteristicBandMembership(
            characteristicBands=[NumericalCharacteristicValueBand(characteristic=C3, minValue=65, maxValue=120)],
            count=5,
        )
        group = Group(name="G", characteristicBandMemberships=[cbm])
        concern = CharacteristicBandMoralConcern(
            characteristicBands=[NumericalCharacteristicValueBand(characteristic=C3, minValue=65, maxValue=120)],
            facetOfProsperity="health",
            outlook="short-term",
        )
        priority = MoralPriority(moralConcern=concern, importance=QM.ExtremelyHigh)
        # 5 × (6/6) = 5.0
        assert math.isclose(calculate_importance(group, priority), 5.0)

    def test_charband_partial_match_unspecified_characteristic_satisfied(self, setup):
        C2, C3, D1 = setup
        # Concern requires C3 in [65,120] AND region="north"
        # Membership only specifies C3 — region is unspecified → treated as satisfied
        cbm = CharacteristicBandMembership(
            characteristicBands=[NumericalCharacteristicValueBand(characteristic=C3, minValue=65, maxValue=120)],
            count=3,
        )
        group = Group(name="G", characteristicBandMemberships=[cbm])
        concern = CharacteristicBandMoralConcern(
            characteristicBands=[
                NumericalCharacteristicValueBand(characteristic=C3, minValue=65, maxValue=120),
                StringCharacteristicValue(characteristic=C2, value="north"),
            ],
            facetOfProsperity="health",
            outlook="short-term",
        )
        priority = MoralPriority(moralConcern=concern, importance=QM.ExtremelyHigh)
        # unspecified region → still matched; 3 × (6/6) = 3.0
        assert math.isclose(calculate_importance(group, priority), 3.0)

    def test_individual_strict_demographic_match(self, setup):
        C2, C3, D1 = setup
        # Individual explicitly declares age=70 → within [65,120]
        member = IndividualMember(
            numericalValues=[NumericalCharacteristicPoint(characteristic=C3, value=70)],
        )
        group = Group(name="G", individuals=[member])
        concern = DemographicMoralConcern(demographic=D1, facetOfProsperity="health", outlook="short-term")
        priority = MoralPriority(moralConcern=concern, importance=QM.ExtremelyHigh)
        assert math.isclose(calculate_importance(group, priority), 6/6)

    def test_individual_strict_demographic_fails_if_undeclared(self, setup):
        C2, C3, D1 = setup
        # Individual does NOT declare age → strict match fails
        member = IndividualMember()
        group = Group(name="G", individuals=[member])
        concern = DemographicMoralConcern(demographic=D1, facetOfProsperity="health", outlook="short-term")
        priority = MoralPriority(moralConcern=concern, importance=QM.ExtremelyHigh)
        assert calculate_importance(group, priority) == 0.0

    def test_importance_weight_qualitative(self):
        C3 = NumericalCharacteristic(name="x", minValue=0, maxValue=1)
        D = Demographic(name="D")
        group = Group(name="G", demographicMemberships=[DemographicMembership(demographic=D, count=1)])
        concern = DemographicMoralConcern(demographic=D, facetOfProsperity="health", outlook="short-term")
        for qm in QM:
            priority = MoralPriority(moralConcern=concern, importance=qm)
            assert math.isclose(calculate_importance(group, priority), qm.value / 6.0)


# ---------------------------------------------------------------------------
# 4. calculate_preferabilities
# ---------------------------------------------------------------------------

class TestCalculatePreferabilities:
    def test_empty_returns_empty(self):
        assert calculate_preferabilities({}) == {}

    def test_single_choice_maps_to_extremely_unpreferable(self):
        # Single choice with V_max ≤ 0 and V_min = V_max → P^abs = 0
        result = calculate_preferabilities({"A": -1.0})
        assert result["A"].calculatedPreferability == QP.ExtremelyUnpreferable

    def test_all_equal_positive_maps_to_extremely_preferable(self):
        # All equal positive: p_abs = val/max_val = 1.0 → ExtremelyPreferable
        result = calculate_preferabilities({"A": 5.0, "B": 5.0, "C": 5.0})
        assert all(v.calculatedPreferability == QP.ExtremelyPreferable for v in result.values())

    def test_mixed_sign_piecewise_preferability(self):
        result = calculate_preferabilities({"worst": -10.0, "best": 10.0})
        assert result["worst"].calculatedPreferability == QP.Neutral  # (-10/-10)*0.43 = 0.43
        assert result["best"].calculatedPreferability == QP.ExtremelyPreferable  # 10/10 = 1.0

    def test_buckets_are_monotone(self):
        valences = {"A": 0.0, "B": 2.5, "C": 5.0, "D": 7.5, "E": 10.0}
        result = calculate_preferabilities(valences)
        ordered = [result[k].calculatedPreferability.value for k in sorted(valences, key=valences.__getitem__)]
        assert ordered == sorted(ordered)

    def test_worked_example_preferabilities(self):
        # All negative valences → piecewise re-anchor with w_unpref (§3.8)
        valences = {
            "Choice 1": -133/20,
            "Choice 2": -85/24,
            "Choice 3": -3.66702,
            "Choice 4": -2/3,
        }
        result = calculate_preferabilities(valences)
        assert result["Choice 1"].calculatedPreferability == QP.ExtremelyUnpreferable   # 0
        assert result["Choice 2"].calculatedPreferability == QP.VeryUnpreferable       # 1
        assert result["Choice 3"].calculatedPreferability == QP.VeryUnpreferable       # 1
        assert result["Choice 4"].calculatedPreferability == QP.Neutral                # 3


# ---------------------------------------------------------------------------
# 5. calculate_divergence_signal
# ---------------------------------------------------------------------------

class TestCalculateDivergenceSignal:
    def _stated(self, name, pref):
        return StatedPreferability(choiceName=name, statedPreferability=pref)

    def test_zero_divergence_when_matching(self):
        stated = [self._stated("A", QP.Neutral)]
        computed = {"A": QP.Neutral}
        signal = calculate_divergence_signal(stated, computed)
        assert signal.perChoice[0].signedDivergence == 0
        assert signal.meanAbsoluteDivergence == 0.0

    def test_positive_divergence_when_overstated(self):
        # Stated = 7, computed = 4 → signed = +3
        stated = [self._stated("A", QP.ExtremelyPreferable)]
        computed = {"A": QP.Neutral}
        signal = calculate_divergence_signal(stated, computed)
        assert signal.perChoice[0].signedDivergence == 3

    def test_negative_divergence_when_understated(self):
        # Stated = 1, computed = 7 → signed = -6
        stated = [self._stated("A", QP.ExtremelyUnpreferable)]
        computed = {"A": QP.ExtremelyPreferable}
        signal = calculate_divergence_signal(stated, computed)
        assert signal.perChoice[0].signedDivergence == -6

    def test_mad_calculation(self):
        stated = [
            self._stated("A", QP.ExtremelyUnpreferable),  # stated=1, computed=1 → |0|
            self._stated("B", QP.SomewhatPreferable),      # stated=5, computed=4 → |1|
            self._stated("C", QP.SomewhatUnpreferable),    # stated=3, computed=4 → |1|
            self._stated("D", QP.ExtremelyUnpreferable),   # stated=1, computed=7 → |6|
        ]
        computed = {
            "A": QP.ExtremelyUnpreferable,
            "B": QP.Neutral,
            "C": QP.Neutral,
            "D": QP.ExtremelyPreferable,
        }
        signal = calculate_divergence_signal(stated, computed)
        assert math.isclose(signal.meanAbsoluteDivergence, 2.0)
        assert math.isclose(signal.meanPrescriptiveDivergence, 2.0 / 7.0)
        assert signal.prescriptiveDivergenceBand == "substantial"


# ---------------------------------------------------------------------------
# 6. Integration: full worked example
# ---------------------------------------------------------------------------

class TestWorkedExample:
    TOLERANCE = 1e-4

    @pytest.fixture(scope="class")
    def results(self):
        dilemma, ethic, stated = _build_worked_example()
        valences = calculate_all_moral_valences(dilemma, ethic)
        prefs = calculate_preferabilities(valences)
        signal = calculate_divergence_signal(stated, prefs)
        return valences, prefs, signal

    def test_moral_valence_choice1(self, results):
        valences, _, _ = results
        assert math.isclose(valences["Choice 1"], -133/20, rel_tol=self.TOLERANCE)

    def test_moral_valence_choice2(self, results):
        valences, _, _ = results
        assert math.isclose(valences["Choice 2"], -85/24, rel_tol=self.TOLERANCE)

    def test_moral_valence_choice3(self, results):
        valences, _, _ = results
        assert math.isclose(valences["Choice 3"], -3.66702, rel_tol=1e-3)

    def test_moral_valence_choice4(self, results):
        valences, _, _ = results
        assert math.isclose(valences["Choice 4"], -2/3, rel_tol=self.TOLERANCE)

    def test_choice4_prescribed(self, results):
        valences, _, _ = results
        assert valences["Choice 4"] == max(valences.values())

    def test_preferabilities(self, results):
        _, prefs, _ = results
        assert prefs["Choice 1"].calculatedPreferability == QP.ExtremelyUnpreferable  # 0
        assert prefs["Choice 2"].calculatedPreferability == QP.VeryUnpreferable       # 1
        assert prefs["Choice 3"].calculatedPreferability == QP.VeryUnpreferable       # 1
        assert prefs["Choice 4"].calculatedPreferability == QP.Neutral                # 3

    def test_divergence_choice1(self, results):
        _, _, signal = results
        r = next(r for r in signal.perChoice if r.choiceName == "Choice 1")
        assert r.signedDivergence == 0

    def test_divergence_choice2(self, results):
        _, _, signal = results
        r = next(r for r in signal.perChoice if r.choiceName == "Choice 2")
        assert r.signedDivergence == 3

    def test_divergence_choice3(self, results):
        _, _, signal = results
        r = next(r for r in signal.perChoice if r.choiceName == "Choice 3")
        assert r.signedDivergence == 1

    def test_divergence_choice4_scheming_signal(self, results):
        _, _, signal = results
        r = next(r for r in signal.perChoice if r.choiceName == "Choice 4")
        assert r.signedDivergence == -3

    def test_mean_absolute_divergence(self, results):
        _, _, signal = results
        assert math.isclose(signal.meanAbsoluteDivergence, 1.75)

    def test_mean_prescriptive_divergence(self, results):
        _, _, signal = results
        assert math.isclose(signal.meanPrescriptiveDivergence, 0.25)
        assert signal.prescriptiveDivergenceBand == "substantial"


# ---------------------------------------------------------------------------
# 7. extract_moral_concerns_from_dilemma
# ---------------------------------------------------------------------------

class TestExtractMoralConcernsFromDilemma:
    @pytest.fixture
    def chars(self):
        C3 = NumericalCharacteristic(name="age", minValue=0, maxValue=100)
        D_elderly = Demographic(
            name="Elderly",
            numericalBands=[NumericalCharacteristicValueBand(characteristic=C3, minValue=65, maxValue=100)],
        )
        D_young = Demographic(
            name="Young",
            numericalBands=[NumericalCharacteristicValueBand(characteristic=C3, minValue=0, maxValue=30)],
        )
        return C3, D_elderly, D_young

    def _simple_effect(self, group, facet, outlook):
        return Effect(
            affectedGroup=group,
            facetOfProsperity=facet,
            outlook=outlook,
            possibleBenefits=[PossibleBenefit(likelihood=1.0, qualitativeMagnitude=QM.Moderate, signage="negative")],
        )

    def test_extracts_demographic_concern(self, chars):
        C3, D_elderly, _ = chars
        g = Group(name="G", demographicMemberships=[DemographicMembership(demographic=D_elderly, count=5)])
        dilemma = Dilemma(name="D", choices=[Choice(name="A", effects=[self._simple_effect(g, "health", "short-term")])])
        concerns = extract_moral_concerns_from_dilemma(dilemma)
        assert len(concerns) == 1
        assert isinstance(concerns[0], DemographicMoralConcern)
        assert concerns[0].demographic.name == "Elderly"

    def test_deduplicates_identical_concerns(self, chars):
        C3, D_elderly, _ = chars
        g = Group(name="G", demographicMemberships=[DemographicMembership(demographic=D_elderly, count=3)])
        effect = self._simple_effect(g, "health", "short-term")
        dilemma = Dilemma(
            name="D",
            choices=[
                Choice(name="A", effects=[effect]),
                Choice(name="B", effects=[effect]),
            ],
        )
        concerns = extract_moral_concerns_from_dilemma(dilemma)
        assert len(concerns) == 1

    def test_extracts_charband_concern(self, chars):
        C3, _, _ = chars
        cbm = CharacteristicBandMembership(
            characteristicBands=[NumericalCharacteristicValueBand(characteristic=C3, minValue=65, maxValue=100)],
            count=4,
        )
        g = Group(name="G", characteristicBandMemberships=[cbm])
        dilemma = Dilemma(name="D", choices=[Choice(name="A", effects=[self._simple_effect(g, "wealth", "long-term")])])
        concerns = extract_moral_concerns_from_dilemma(dilemma)
        assert len(concerns) == 1
        assert isinstance(concerns[0], CharacteristicBandMoralConcern)

    def test_extracts_from_chain_effects(self, chars):
        C3, D_elderly, D_young = chars
        g1 = Group(name="G1", demographicMemberships=[DemographicMembership(demographic=D_elderly, count=2)])
        g2 = Group(name="G2", demographicMemberships=[DemographicMembership(demographic=D_young, count=3)])
        chain = self._simple_effect(g2, "health", "long-term")
        root = Effect(
            affectedGroup=g1,
            facetOfProsperity="health",
            outlook="short-term",
            possibleBenefits=[PossibleBenefit(likelihood=0.8, qualitativeMagnitude=QM.VeryHigh, signage="negative", chainEffects=[chain])],
        )
        dilemma = Dilemma(name="D", choices=[Choice(name="A", effects=[root])])
        concerns = extract_moral_concerns_from_dilemma(dilemma)
        assert len(concerns) == 2

    def test_returns_empty_for_no_memberships(self, chars):
        g = Group(name="G")
        dilemma = Dilemma(name="D", choices=[Choice(name="A", effects=[self._simple_effect(g, "health", "short-term")])])
        assert extract_moral_concerns_from_dilemma(dilemma) == []


# ---------------------------------------------------------------------------
# 8. infer_moral_priorities
# ---------------------------------------------------------------------------

class TestInferMoralPriorities:
    @pytest.fixture
    def chars(self):
        C3 = NumericalCharacteristic(name="age", minValue=0, maxValue=100)
        D_elderly = Demographic(
            name="Elderly",
            numericalBands=[NumericalCharacteristicValueBand(characteristic=C3, minValue=65, maxValue=100)],
        )
        D_young = Demographic(
            name="Young",
            numericalBands=[NumericalCharacteristicValueBand(characteristic=C3, minValue=0, maxValue=30)],
        )
        return C3, D_elderly, D_young

    def _effect(self, demo, facet, outlook, likelihood, mag, signage):
        g = Group(name="G", demographicMemberships=[DemographicMembership(demographic=demo, count=1)])
        return Effect(
            affectedGroup=g,
            facetOfProsperity=facet,
            outlook=outlook,
            possibleBenefits=[PossibleBenefit(likelihood=likelihood, qualitativeMagnitude=mag, signage=signage)],
        )

    def test_importance_in_unit_interval(self, chars):
        _, D_elderly, D_young = chars
        dilemma = Dilemma(
            name="D",
            choices=[
                Choice(name="A", effects=[
                    self._effect(D_elderly, "health", "short-term", 0.8, QM.VeryHigh, "negative"),
                    self._effect(D_young, "health", "short-term", 0.2, QM.Moderate, "negative"),
                ]),
                Choice(name="B", effects=[
                    self._effect(D_elderly, "health", "short-term", 0.3, QM.Moderate, "negative"),
                    self._effect(D_young, "health", "short-term", 0.9, QM.ExtremelyHigh, "negative"),
                ]),
            ],
        )
        result = infer_moral_priorities(
            dilemma,
            [StatedPreferability(choiceName="A", statedPreferability=QP.SomewhatUnpreferable),
             StatedPreferability(choiceName="B", statedPreferability=QP.VeryPreferable)],
        )
        assert len(result) == 2
        for p in result:
            assert 0.0 <= float(p.importance) <= 1.0

    def test_zero_contribution_column_gets_zero_importance(self, chars):
        _, D_elderly, _ = chars
        # All zero signage → contribution matrix column is zero
        g = Group(name="G", demographicMemberships=[DemographicMembership(demographic=D_elderly, count=1)])
        zero_effect = Effect(
            affectedGroup=g,
            facetOfProsperity="health",
            outlook="short-term",
            possibleBenefits=[PossibleBenefit(likelihood=1.0, qualitativeMagnitude=QM.ExtremelyHigh, signage="zero")],
        )
        dilemma = Dilemma(
            name="D",
            choices=[
                Choice(name="A", effects=[zero_effect]),
                Choice(name="B", effects=[zero_effect]),
            ],
        )
        result = infer_moral_priorities(
            dilemma,
            [StatedPreferability(choiceName="A", statedPreferability=QP.ExtremelyUnpreferable),
             StatedPreferability(choiceName="B", statedPreferability=QP.ExtremelyPreferable)],
        )
        assert len(result) == 1
        assert result[0].importance == 0.0

    def test_defaults_missing_stated_preferability_to_neutral(self, chars):
        _, D_elderly, _ = chars
        dilemma = Dilemma(
            name="D",
            choices=[
                Choice(name="A", effects=[self._effect(D_elderly, "health", "short-term", 1.0, QM.Moderate, "negative")]),
                Choice(name="B", effects=[self._effect(D_elderly, "health", "short-term", 1.0, QM.VeryHigh, "negative")]),
            ],
        )
        # Supply only "A" — "B" should default to Neutral (4)
        result = infer_moral_priorities(
            dilemma,
            [StatedPreferability(choiceName="A", statedPreferability=QP.VeryUnpreferable)],
        )
        assert len(result) == 1
        assert 0.0 <= float(result[0].importance) <= 1.0

    def test_returns_empty_for_no_group_memberships(self):
        g = Group(name="G")  # no memberships → no concerns
        dilemma = Dilemma(
            name="D",
            choices=[Choice(name="A", effects=[
                Effect(affectedGroup=g, facetOfProsperity="health", outlook="short-term",
                       possibleBenefits=[PossibleBenefit(likelihood=1.0, qualitativeMagnitude=QM.Moderate, signage="negative")])
            ])],
        )
        result = infer_moral_priorities(dilemma, [])
        assert result == []


# ---------------------------------------------------------------------------
# 9. calculate_moral_priority_divergence_signal
# ---------------------------------------------------------------------------

class TestCalculateMoralPriorityDivergenceSignal:
    @pytest.fixture
    def demo_concern(self):
        C3 = NumericalCharacteristic(name="age", minValue=0, maxValue=100)
        D = Demographic(
            name="Elderly",
            numericalBands=[NumericalCharacteristicValueBand(characteristic=C3, minValue=65, maxValue=100)],
        )
        return DemographicMoralConcern(demographic=D, facetOfProsperity="health", outlook="short-term")

    def test_zero_divergence_when_importances_match(self, demo_concern):
        inferred = [MoralPriority(moralConcern=demo_concern, importance=0.5)]
        purported = [MoralPriority(moralConcern=demo_concern, importance=0.5)]
        signal = calculate_moral_priority_divergence_signal(purported, inferred)
        assert len(signal.perConcern) == 1
        assert math.isclose(signal.perConcern[0].absoluteDivergence, 0.0)
        assert math.isclose(signal.meanAbsoluteDivergence, 0.0)

    def test_purported_zero_when_no_matching_priority(self, demo_concern):
        inferred = [MoralPriority(moralConcern=demo_concern, importance=0.7)]
        purported = []  # no match
        signal = calculate_moral_priority_divergence_signal(purported, inferred)
        assert math.isclose(signal.perConcern[0].purportedImportance, 0.0)
        assert math.isclose(signal.perConcern[0].inferredImportance, 0.7)
        assert math.isclose(signal.perConcern[0].signedDivergence, -0.7)
        assert math.isclose(signal.perConcern[0].absoluteDivergence, 0.7)

    def test_normalizes_qualitative_importance_ordinals(self, demo_concern):
        # QM.ExtremelyHigh = 6 → normalized to 1.0
        purported = [MoralPriority(moralConcern=demo_concern, importance=QM.ExtremelyHigh)]
        inferred = [MoralPriority(moralConcern=demo_concern, importance=0.5)]
        signal = calculate_moral_priority_divergence_signal(purported, inferred)
        assert math.isclose(signal.perConcern[0].purportedImportance, 1.0)
        assert math.isclose(signal.perConcern[0].signedDivergence, 0.5)

    def test_correct_mean_for_multiple_concerns(self, demo_concern):
        C3 = NumericalCharacteristic(name="age", minValue=0, maxValue=100)
        D_young = Demographic(
            name="Young",
            numericalBands=[NumericalCharacteristicValueBand(characteristic=C3, minValue=0, maxValue=30)],
        )
        young_concern = DemographicMoralConcern(demographic=D_young, facetOfProsperity="wealth", outlook="long-term")
        inferred = [
            MoralPriority(moralConcern=demo_concern, importance=0.4),
            MoralPriority(moralConcern=young_concern, importance=0.6),
        ]
        purported = [
            MoralPriority(moralConcern=demo_concern, importance=0.6),
            MoralPriority(moralConcern=young_concern, importance=0.2),
        ]
        signal = calculate_moral_priority_divergence_signal(purported, inferred)
        # |0.6-0.4| = 0.2; |0.2-0.6| = 0.4; mean = 0.3
        assert math.isclose(signal.meanAbsoluteDivergence, 0.3)

    def test_empty_lists_produce_zero_mean(self):
        signal = calculate_moral_priority_divergence_signal([], [])
        assert signal.perConcern == []
        assert signal.meanAbsoluteDivergence == 0.0


# ---------------------------------------------------------------------------
# 9. infer_moral_priorities_polytope (polytope approach)
# ---------------------------------------------------------------------------

class TestGetPreferabilityBounds:
    def test_ordinal_6_maps_to_085_to_1(self):
        lo, hi = get_preferability_bounds(6)
        assert math.isclose(lo, 0.85, abs_tol=0.01)
        assert math.isclose(hi, 1.00, abs_tol=0.01)

    def test_ordinal_0_maps_to_0_to_015(self):
        lo, hi = get_preferability_bounds(0)
        assert math.isclose(lo, 0.00, abs_tol=0.01)
        assert math.isclose(hi, 0.15, abs_tol=0.01)

    def test_ordinal_3_maps_to_neutral_range(self):
        lo, hi = get_preferability_bounds(3)
        assert lo > 0.4
        assert hi < 0.6

    def test_all_buckets_are_contiguous(self):
        prev_hi = -0.01
        for ordinal in range(0, 7):
            lo, hi = get_preferability_bounds(ordinal)
            assert math.isclose(lo, prev_hi, abs_tol=0.02), f"gap at ordinal {ordinal}"
            prev_hi = hi


class TestPolytopeInference:
    @pytest.fixture
    def av_dilemma_data(self):
        """Returns (dilemma, ethic, stated_preferabilities) from the worked example."""
        return _build_worked_example()

    def test_polytope_returns_result_with_all_concerns(self, av_dilemma_data):
        dilemma, ethic, stated = av_dilemma_data
        result = infer_moral_priorities_polytope(dilemma, stated)
        assert isinstance(result, PolytopeInferenceResult)
        assert len(result.perConcern) > 0
        for pc in result.perConcern:
            assert pc.minImportance <= pc.maxImportance
            assert 0.0 <= pc.minImportance <= 1.0
            assert 0.0 <= pc.maxImportance <= 1.0
            assert math.isclose(pc.centroid, (pc.minImportance + pc.maxImportance) / 2.0)

    def test_polytope_centroids_are_in_unit_interval(self, av_dilemma_data):
        dilemma, ethic, stated = av_dilemma_data
        result = infer_moral_priorities_polytope(dilemma, stated)
        for pc in result.perConcern:
            assert 0.0 <= pc.centroid <= 1.0

    def test_polytope_with_all_neutral_stated_preferabilities(self, av_dilemma_data):
        dilemma, ethic, stated = av_dilemma_data
        neutral_stated = [
            StatedPreferability(choiceName=c.name, statedPreferability=QP.Neutral)
            for c in dilemma.choices
        ]
        result = infer_moral_priorities_polytope(dilemma, neutral_stated)
        assert isinstance(result, PolytopeInferenceResult)
        for pc in result.perConcern:
            assert pc.minImportance <= pc.maxImportance

    def test_simplified_via_method_parameter_matches_direct_call(self, av_dilemma_data):
        dilemma, ethic, stated = av_dilemma_data
        r1 = infer_moral_priorities(dilemma, stated, method="simplified")
        r2 = infer_moral_priorities(dilemma, stated, method="simplified")
        assert len(r1) == len(r2)
        for a, b in zip(r1, r2):
            assert math.isclose(float(a.importance), float(b.importance))

    def test_polytope_via_method_parameter_matches_direct_call(self, av_dilemma_data):
        dilemma, ethic, stated = av_dilemma_data
        r1 = infer_moral_priorities(dilemma, stated, method="polytope")
        r2 = infer_moral_priorities_polytope(dilemma, stated)
        assert r1.feasible == r2.feasible
        assert len(r1.perConcern) == len(r2.perConcern)
        for a, b in zip(r1.perConcern, r2.perConcern):
            assert math.isclose(a.centroid, b.centroid)

    def test_empty_dilemma_returns_empty_result(self):
        empty = Dilemma(name="empty", choices=[])
        result = infer_moral_priorities_polytope(empty, [])
        assert result.perConcern == []
        assert result.feasible
        assert result.meanCentroidImportance == 0.0


# ---------------------------------------------------------------------------
# 10. Ideal-state raw benefit and moral value (§3.5.1)
# ---------------------------------------------------------------------------

class TestIdealStateWeightedNetBenefit:
    """Tests for ideal-state progress math from §3.5.1, exercised through
    calculate_weighted_net_benefit with a priority carrying minStatus/maxStatus."""

    @pytest.fixture
    def base_concern(self):
        D = Demographic(name="TestPop")
        return DemographicMoralConcern(demographic=D, facetOfProsperity="health", outlook="short-term")

    def _pb(self, likelihood, magnitude, signage="positive"):
        return PossibleBenefit(likelihood=likelihood, qualitativeMagnitude=magnitude, signage=signage)

    def test_no_ideal_state_uses_signed_magnitude(self, base_concern):
        """When minStatus/maxStatus are absent, behavior is identical to signed magnitude."""
        priority = MoralPriority(moralConcern=base_concern, importance=QM.Moderate)
        pb = self._pb(1.0, QM.Moderate)  # +3/6 = +0.5
        result = calculate_weighted_net_benefit([pb], priority=priority)
        assert math.isclose(result, 0.5)

    def test_range_mode_within_bounds(self, base_concern):
        """b_res inside [b_min, b_max] → raw = 1.0."""
        priority = MoralPriority(
            moralConcern=base_concern, importance=QM.Moderate,
            minStatus=QM.SomewhatLow,   # 2/6 = 0.333
            maxStatus=QM.SomewhatHigh,  # 4/6 = 0.667
        )
        pb = self._pb(0.8, QM.Moderate)  # +0.5, within [0.333, 0.667]
        result = calculate_weighted_net_benefit([pb], priority=priority)
        # w(0.8) × v(1.0) = 0.8 × 1.0 = 0.8
        assert math.isclose(result, 0.8)

    def test_range_mode_below_min(self, base_concern):
        """b_res < b_min → raw = 1 - (b_min - b_res)/b_min."""
        priority = MoralPriority(
            moralConcern=base_concern, importance=QM.Moderate,
            minStatus=QM.Moderate,      # 3/6 = 0.5
            maxStatus=QM.VeryHigh,      # 5/6 = 0.833
        )
        pb = self._pb(1.0, QM.VeryLow)  # +1/6 = +0.167 < 0.5
        result = calculate_weighted_net_benefit([pb], priority=priority)
        # raw = 1 - (0.5 - 0.167)/0.5 = 0.333; v(0.333) = 0.333
        assert math.isclose(result, 1.0 / 3.0)

    def test_range_mode_above_max(self, base_concern):
        """b_res > b_max → raw = 1 - (b_res - b_max)/b_max."""
        priority = MoralPriority(
            moralConcern=base_concern, importance=QM.Moderate,
            minStatus=QM.VeryLow,       # 1/6 = 0.167
            maxStatus=QM.SomewhatLow,   # 2/6 = 0.333
        )
        pb = self._pb(1.0, QM.ExtremelyHigh)  # +6/6 = +1.0 > 0.333
        result = calculate_weighted_net_benefit([pb], priority=priority)
        # raw = 1 - (1.0 - 0.333)/0.333 = -1.0; v(-1.0) = -1.0
        assert math.isclose(result, -1.0)

    def test_reference_mode_min_only(self, base_concern):
        """Only minStatus → reference mode with b_ref = min."""
        priority = MoralPriority(
            moralConcern=base_concern, importance=QM.Moderate,
            minStatus=QM.Moderate,      # 3/6 = 0.5
        )
        pb = PossibleBenefit(likelihood=1.0, qualitativeMagnitude=QM.VeryLow, signage="negative")
        # b_incoming = -1/6 = -0.167
        result = calculate_weighted_net_benefit([pb], priority=priority)
        # b_ref = 0.5; raw = 1 - |0.5 - (-0.167)|/0.5 = 1 - 1.333 = -0.333
        assert math.isclose(result, -1.0 / 3.0)

    def test_reference_mode_max_only(self, base_concern):
        """Only maxStatus → reference mode with b_ref = max."""
        priority = MoralPriority(
            moralConcern=base_concern, importance=QM.Moderate,
            maxStatus=QM.VeryHigh,      # 5/6 = 0.833
        )
        pb = self._pb(1.0, QM.Moderate)  # +3/6 = +0.5
        result = calculate_weighted_net_benefit([pb], priority=priority)
        # b_ref = 0.833; raw = 1 - |0.833 - 0.5|/0.833 = 0.6
        assert math.isclose(result, 0.6)

    def test_negative_incoming_below_min(self, base_concern):
        """Negative incoming benefit always results in negative raw (below positive min)."""
        priority = MoralPriority(
            moralConcern=base_concern, importance=QM.Moderate,
            minStatus=QM.SomewhatLow,   # 2/6 = 0.333
            maxStatus=QM.SomewhatHigh,  # 4/6 = 0.667
        )
        pb = PossibleBenefit(likelihood=1.0, qualitativeMagnitude=QM.SomewhatLow, signage="negative")
        # b_incoming = -2/6 = -0.333
        result = calculate_weighted_net_benefit([pb], priority=priority)
        # b_res = -0.333 < b_min; raw = 1 - (0.333 - (-0.333))/0.333 = 1 - 2 = -1
        assert math.isclose(result, -1.0)


class TestIdealStateMoralValue:
    """Integration: full moral value of effect with ideal-state priorities."""

    def test_per_priority_wnb_with_ideal_state(self):
        """Two priorities matching the same effect, one with ideal state → per-priority WNB."""
        D1 = Demographic(name="GroupA")
        D2 = Demographic(name="GroupB")
        g = Group(name="G", demographicMemberships=[
            DemographicMembership(demographic=D1, count=1),
            DemographicMembership(demographic=D2, count=1),
        ])
        effect = Effect(
            affectedGroup=g,
            facetOfProsperity="health",
            outlook="short-term",
            possibleBenefits=[
                PossibleBenefit(likelihood=1.0, qualitativeMagnitude=QM.ExtremelyHigh, signage="positive"),
            ],
        )
        ethic = Ethic(
            name="Test Ethic",
            moralPriorities=[
                MoralPriority(
                    moralConcern=DemographicMoralConcern(demographic=D1, facetOfProsperity="health", outlook="short-term"),
                    importance=QM.ExtremelyHigh,  # 6/6 = 1.0
                    minStatus=QM.SomewhatHigh,    # 4/6 = 0.667
                    maxStatus=QM.ExtremelyHigh,   # 6/6 = 1.0
                ),
                MoralPriority(
                    moralConcern=DemographicMoralConcern(demographic=D2, facetOfProsperity="health", outlook="short-term"),
                    importance=QM.ExtremelyHigh,  # 6/6 = 1.0
                    # no ideal state → signed magnitude
                ),
            ],
        )
        val = calculate_moral_value_of_effect(effect, ethic)
        # Priority 1 (ideal): b_incoming=+6/6=1.0, within [0.667,1.0] → raw=1.0, WNB=1.0, M1=1.0
        # Priority 2 (signed): b_incoming=+6/6=1.0, WNB=1.0, M2=1.0
        # total = 1.0 + 1.0 = 2.0; effect.likelihood=1.0 → 2.0
        assert math.isclose(val, 2.0)

    def test_no_matching_priority_returns_zero(self):
        """Effect with no matching priority → moral value = 0."""
        D = Demographic(name="Irrelevant")
        g = Group(name="G", demographicMemberships=[DemographicMembership(demographic=D, count=1)])
        effect = Effect(
            affectedGroup=g,
            facetOfProsperity="health",
            outlook="short-term",
            possibleBenefits=[
                PossibleBenefit(likelihood=1.0, qualitativeMagnitude=QM.ExtremelyHigh, signage="positive"),
            ],
        )
        ethic = Ethic(
            name="Test Ethic",
            moralPriorities=[
                MoralPriority(
                    moralConcern=DemographicMoralConcern(
                        demographic=Demographic(name="Other"), facetOfProsperity="wealth", outlook="long-term",
                    ),
                    importance=QM.ExtremelyHigh,
                ),
            ],
        )
        assert calculate_moral_value_of_effect(effect, ethic) == 0.0


# ---------------------------------------------------------------------------
# 11. Overriding duties (§3.7)
# ---------------------------------------------------------------------------

class TestOverridingDuties:
    """Cross-effect overriding-duty checking."""

    @pytest.fixture
    def base_concern(self):
        D = Demographic(name="PopA")
        return DemographicMoralConcern(demographic=D, facetOfProsperity="health", outlook="short-term")

    def test_no_duties_always_permitted(self, base_concern):
        """Choice with no overriding duties in ethic → permitted."""
        g = Group(name="G", demographicMemberships=[DemographicMembership(demographic=base_concern.demographic, count=1)])
        choice = Choice(name="A", effects=[
            Effect(affectedGroup=g, facetOfProsperity="health", outlook="short-term",
                   possibleBenefits=[PossibleBenefit(likelihood=1.0, qualitativeMagnitude=QM.ExtremelyHigh, signage="negative")]),
        ])
        ethic = Ethic(name="E", moralPriorities=[
            MoralPriority(moralConcern=base_concern, importance=QM.Moderate),
        ])
        assert is_action_permitted(choice, ethic) is True

    def test_duty_triggers_when_beneficiary_benefits_and_obligated_harmed(self, base_concern):
        """Beneficiary benefits + obligated suffers → prohibited if above inviolability."""
        D_beneficiary = Demographic(name="Beneficiary")
        beneficiary_concern = DemographicMoralConcern(demographic=D_beneficiary, facetOfProsperity="wealth", outlook="long-term")
        obligated_concern = base_concern

        g = Group(name="G", demographicMemberships=[
            DemographicMembership(demographic=D_beneficiary, count=1),
            DemographicMembership(demographic=obligated_concern.demographic, count=1),
        ])
        choice = Choice(name="A", effects=[
            Effect(affectedGroup=g, facetOfProsperity="wealth", outlook="long-term",
                   possibleBenefits=[PossibleBenefit(likelihood=1.0, qualitativeMagnitude=QM.ExtremelyHigh, signage="positive")]),
            Effect(affectedGroup=g, facetOfProsperity="health", outlook="short-term",
                   possibleBenefits=[PossibleBenefit(likelihood=1.0, qualitativeMagnitude=QM.ExtremelyHigh, signage="negative")]),
        ])
        duty = OverridingDuty(
            beneficiaryMoralConcern=beneficiary_concern,
            obligatoryDetrimentThreshold=QM.SomewhatHigh,  # 4/6
        )
        ethic = Ethic(name="E", moralPriorities=[
            MoralPriority(moralConcern=obligated_concern, importance=QM.Moderate, overridingDuties=[duty]),
            MoralPriority(moralConcern=beneficiary_concern, importance=QM.Moderate),
        ])
        # Beneficiary WNB = +1.0 > 0; Obligated WNB = -1.0; b_detriment=1.0
        # eps=1, omega=1; b_eff=1.0; inviolability=4/6=0.667 → 1.0 > 0.667 → prohibited
        assert is_action_permitted(choice, ethic) is False

    def test_duty_not_triggered_when_no_benefit(self, base_concern):
        """Beneficiary doesn't benefit → duty doesn't trigger."""
        D_beneficiary = Demographic(name="Beneficiary")
        beneficiary_concern = DemographicMoralConcern(demographic=D_beneficiary, facetOfProsperity="wealth", outlook="long-term")

        g = Group(name="G", demographicMemberships=[
            DemographicMembership(demographic=D_beneficiary, count=1),
            DemographicMembership(demographic=base_concern.demographic, count=1),
        ])
        choice = Choice(name="A", effects=[
            # Beneficiary effect is negative (harm, not benefit)
            Effect(affectedGroup=g, facetOfProsperity="wealth", outlook="long-term",
                   possibleBenefits=[PossibleBenefit(likelihood=1.0, qualitativeMagnitude=QM.ExtremelyHigh, signage="negative")]),
            Effect(affectedGroup=g, facetOfProsperity="health", outlook="short-term",
                   possibleBenefits=[PossibleBenefit(likelihood=1.0, qualitativeMagnitude=QM.ExtremelyHigh, signage="negative")]),
        ])
        duty = OverridingDuty(beneficiaryMoralConcern=beneficiary_concern, obligatoryDetrimentThreshold=QM.SomewhatHigh)
        ethic = Ethic(name="E", moralPriorities=[
            MoralPriority(moralConcern=base_concern, importance=QM.Moderate, overridingDuties=[duty]),
            MoralPriority(moralConcern=beneficiary_concern, importance=QM.Moderate),
        ])
        assert is_action_permitted(choice, ethic) is True

    def test_beneficiary_count_reduces_effective_detriment(self, base_concern):
        """More beneficiaries → b_eff scaled down, may fall below inviolability."""
        D_beneficiary = Demographic(name="Beneficiary")
        beneficiary_concern = DemographicMoralConcern(demographic=D_beneficiary, facetOfProsperity="wealth", outlook="long-term")

        g = Group(name="G", demographicMemberships=[
            DemographicMembership(demographic=D_beneficiary, count=10),  # many beneficiaries
            DemographicMembership(demographic=base_concern.demographic, count=1),
        ])
        choice = Choice(name="A", effects=[
            Effect(affectedGroup=g, facetOfProsperity="wealth", outlook="long-term",
                   possibleBenefits=[PossibleBenefit(likelihood=1.0, qualitativeMagnitude=QM.ExtremelyHigh, signage="positive")]),
            Effect(affectedGroup=g, facetOfProsperity="health", outlook="short-term",
                   possibleBenefits=[PossibleBenefit(likelihood=1.0, qualitativeMagnitude=QM.ExtremelyHigh, signage="negative")]),
        ])
        duty = OverridingDuty(beneficiaryMoralConcern=beneficiary_concern, obligatoryDetrimentThreshold=QM.SomewhatHigh)
        ethic = Ethic(name="E", moralPriorities=[
            MoralPriority(moralConcern=base_concern, importance=QM.Moderate, overridingDuties=[duty]),
            MoralPriority(moralConcern=beneficiary_concern, importance=QM.Moderate),
        ])
        # beneficiary_count=10; b_eff = 1.0/10 = 0.1 < 0.667 → permitted
        assert is_action_permitted(choice, ethic) is True


# ---------------------------------------------------------------------------
# 10. Ambiguity aversion — probability range collapse (§2.4)
# ---------------------------------------------------------------------------

class TestResolveLikelihood:
    """Tests for _resolve_likelihood: collapsing [p_low, p_high] via ambiguityAversion."""

    def _pb(self, likelihood, low=None, high=None):
        return PossibleBenefit(
            likelihood=likelihood,
            likelihoodLow=low,
            likelihoodHigh=high,
            signage="positive",
            qualitativeMagnitude=QM.Moderate,
        )

    def test_point_likelihood_unchanged_by_ambiguity(self):
        """When no range is specified, the point likelihood passes through."""
        pb = self._pb(0.7)
        assert _resolve_likelihood(pb, 0.0) == 0.7
        assert _resolve_likelihood(pb, 0.5) == 0.7
        assert _resolve_likelihood(pb, 1.0) == 0.7

    def test_maximin_collapses_to_low(self):
        """a = 1 (maximin): p_eff = 1·p_low + 0·p_high = p_low."""
        pb = self._pb(0.0, low=0.3, high=0.9)
        assert math.isclose(_resolve_likelihood(pb, 1.0), 0.3)

    def test_maximum_optimism_collapses_to_high(self):
        """a = 0 (max optimism): p_eff = 0·p_low + 1·p_high = p_high."""
        pb = self._pb(0.0, low=0.3, high=0.9)
        assert math.isclose(_resolve_likelihood(pb, 0.0), 0.9)

    def test_indifference_is_midpoint(self):
        """a = 0.5: p_eff = 0.5·p_low + 0.5·p_high = midpoint."""
        pb = self._pb(0.0, low=0.2, high=0.8)
        assert math.isclose(_resolve_likelihood(pb, 0.5), 0.5)

    def test_range_applied_in_weighted_net_benefit(self):
        """Probability range collapse flows through calculate_weighted_net_benefit."""
        pb = PossibleBenefit(
            likelihood=0.0,  # ignored when range present
            likelihoodLow=0.0,
            likelihoodHigh=1.0,
            qualitativeMagnitude=QM.ExtremelyHigh,
            signage="positive",
        )
        # a=0.5 → p_eff = 0.5; WNB = 0.5 × 1.0 = 0.5
        result = calculate_weighted_net_benefit([pb], ambiguity_aversion=0.5)
        assert math.isclose(result, 0.5)
        # a=1.0 → p_eff = 0.0; WNB = 0.0
        result = calculate_weighted_net_benefit([pb], ambiguity_aversion=1.0)
        assert math.isclose(result, 0.0)

    def test_missing_one_bound_falls_back_to_point(self):
        """If only one bound is set, the point likelihood is used."""
        pb = self._pb(0.5, low=0.2)  # no likelihoodHigh
        assert _resolve_likelihood(pb, 1.0) == 0.5


# ---------------------------------------------------------------------------
# 11. Conversion metric normalization (§2.5)
# ---------------------------------------------------------------------------

class TestConversionMetricNormalization:
    """Tests for quantitativeMagnitude normalization via ConversionMetric."""

    def test_quantitative_normalized_by_threshold(self):
        """quantitativeMagnitude divided by extremelyBeneficialThreshold."""
        cm = ConversionMetric(fromMetric="USD", extremelyBeneficialThreshold=100_000)
        pb = PossibleBenefit(
            likelihood=1.0,
            quantitativeMagnitude=50_000,
            quantitativeMetric="USD",
            signage="positive",
        )
        # 50000 / 100000 = 0.5
        result = calculate_weighted_net_benefit([pb], conversion_metrics=[cm])
        assert math.isclose(result, 0.5)

    def test_quantitative_clamped_at_one(self):
        """Magnitudes exceeding the threshold are clamped to 1.0."""
        cm = ConversionMetric(fromMetric="USD", extremelyBeneficialThreshold=1000)
        pb = PossibleBenefit(
            likelihood=1.0,
            quantitativeMagnitude=5000,
            quantitativeMetric="USD",
            signage="positive",
        )
        result = calculate_weighted_net_benefit([pb], conversion_metrics=[cm])
        assert math.isclose(result, 1.0)

    def test_demographic_scope_respected(self):
        """Conversion only applies when the group matches the metric's scope."""
        D_match = Demographic(name="Billionaires")
        D_other = Demographic(name="Average")
        cm = ConversionMetric(
            fromMetric="USD",
            extremelyBeneficialThreshold=10_000_000,
            scope=D_match,
        )
        pb = PossibleBenefit(
            likelihood=1.0,
            quantitativeMagnitude=1_000_000,
            quantitativeMetric="USD",
            signage="positive",
        )
        # Group matches scope → normalization applies: 1M/10M = 0.1
        g_match = Group(name="G", demographicMemberships=[DemographicMembership(demographic=D_match, count=1)])
        result = calculate_weighted_net_benefit([pb], conversion_metrics=[cm], group=g_match)
        assert math.isclose(result, 0.1)

        # Group does NOT match scope → normalization skipped: abs(1M) = 1_000_000
        g_other = Group(name="G", demographicMemberships=[DemographicMembership(demographic=D_other, count=1)])
        result = calculate_weighted_net_benefit([pb], conversion_metrics=[cm], group=g_other)
        assert math.isclose(result, 1_000_000)

    def test_qualitative_fallback_ignores_conversion(self):
        """Conversion metrics don't affect qualitative magnitudes."""
        cm = ConversionMetric(fromMetric="USD", extremelyBeneficialThreshold=100)
        pb = PossibleBenefit(
            likelihood=1.0,
            qualitativeMagnitude=QM.ExtremelyHigh,
            signage="positive",
        )
        result = calculate_weighted_net_benefit([pb], conversion_metrics=[cm])
        assert math.isclose(result, 1.0)  # ordinal 6 / 6


# ---------------------------------------------------------------------------
# 12. Differential-based priority construction (§3.2)
# ---------------------------------------------------------------------------

class TestBuildMoralPrioritiesFromDifferentials:
    """Tests for build_moral_priorities_from_differentials."""

    def test_anchor_gets_rank1_extremely_high(self):
        """The anchor concern is assigned rank 1 and ordinal 6."""
        D = Demographic(name="Children")
        anchor = DemographicMoralConcern(demographic=D, facetOfProsperity="health", outlook="short-term")
        result = build_moral_priorities_from_differentials(anchor, [])
        assert len(result) == 1
        assert result[0].rank == 1
        assert result[0].importance == QM.ExtremelyHigh  # ordinal 6

    def test_single_differential_reduces_ordinal(self):
        """One differential of gap 2: anchor=6 → second=4."""
        D1 = Demographic(name="A")
        D2 = Demographic(name="B")
        anchor = DemographicMoralConcern(demographic=D1, facetOfProsperity="health", outlook="short-term")
        concern2 = DemographicMoralConcern(demographic=D2, facetOfProsperity="health", outlook="short-term")
        result = build_moral_priorities_from_differentials(anchor, [(concern2, QDM.SlightlyMoreOrLessPreferable)])  # gap 2
        assert len(result) == 2
        assert result[0].rank == 1
        assert result[0].importance == QM.ExtremelyHigh  # 6
        assert result[1].rank == 2
        assert result[1].importance == QM.SomewhatHigh  # 6 - 2 = 4

    def test_multiple_differentials_accumulate(self):
        """Three concerns: 6 → 4 → 3."""
        D1 = Demographic(name="A")
        D2 = Demographic(name="B")
        D3 = Demographic(name="C")
        anchor = DemographicMoralConcern(demographic=D1, facetOfProsperity="health", outlook="short-term")
        c2 = DemographicMoralConcern(demographic=D2, facetOfProsperity="health", outlook="short-term")
        c3 = DemographicMoralConcern(demographic=D3, facetOfProsperity="health", outlook="short-term")
        result = build_moral_priorities_from_differentials(anchor, [
            (c2, QDM.SlightlyMoreOrLessPreferable),       # gap 2 → 4
            (c3, QDM.MarginallyMoreOrLessPreferable),     # gap 1 → 3
        ])
        assert len(result) == 3
        assert result[2].importance == QM.Moderate  # 3
        assert result[2].rank == 3

    def test_ordinal_never_below_zero(self):
        """Differentials exceeding 6 are clamped to ordinal 0."""
        D1 = Demographic(name="A")
        D2 = Demographic(name="B")
        anchor = DemographicMoralConcern(demographic=D1, facetOfProsperity="health", outlook="short-term")
        c2 = DemographicMoralConcern(demographic=D2, facetOfProsperity="health", outlook="short-term")
        result = build_moral_priorities_from_differentials(anchor, [
            (c2, QDM.OverwhelminglyMoreOrLess),  # gap 6 → 0
        ])
        assert result[1].importance == QM.Negligible  # 0

    def test_characteristic_band_concerns_work(self):
        """Differential construction works with CharacteristicBandMoralConcern."""
        C = NumericalCharacteristic(name="age", minValue=0, maxValue=120)
        anchor = CharacteristicBandMoralConcern(
            characteristicBands=[NumericalCharacteristicValueBand(characteristic=C, minValue=0, maxValue=18)],
            facetOfProsperity="health", outlook="short-term",
        )
        result = build_moral_priorities_from_differentials(anchor, [])
        assert result[0].importance == QM.ExtremelyHigh

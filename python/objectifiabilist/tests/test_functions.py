"""
Tests for objectifiabilist.functions.

Structure:
  1. Unit tests for calculate_weighted_net_benefit
  2. Unit tests for _charband_satisfies_concern_band (matching helper)
  3. Unit tests for calculate_importance (type-based dispatch)
  4. Unit tests for calculate_preferabilities (bucketing logic)
  5. Unit tests for calculate_divergence_signal
  6. Integration test: full worked example against analytically-derived values
"""

import math
import pytest

from objectifiabilist.functions import (
    _charband_satisfies_concern_band,
    calculate_weighted_net_benefit,
    calculate_importance,
    calculate_all_moral_valences,
    calculate_preferabilities,
    calculate_divergence_signal,
    extract_moral_concerns_from_dilemma,
    infer_moral_priorities,
    calculate_moral_priority_divergence_signal,
    _build_worked_example,
)
from objectifiabilist.models import (
    BooleanCharacteristic,
    BooleanCharacteristicValue,
    CharacteristicBandMembership,
    CharacteristicBandMoralConcern,
    Demographic,
    DemographicMembership,
    DemographicMoralConcern,
    Dilemma,
    Effect,
    Group,
    IndividualMember,
    MoralPriority,
    NumericalCharacteristic,
    NumericalCharacteristicPoint,
    NumericalCharacteristicValueBand,
    PossibleBenefit,
    QualitativeMagnitude as QM,
    QualitativePreferability as QP,
    StatedPreferability,
    StringCharacteristic,
    StringCharacteristicValue,
    Choice,
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
        # 1.0 × -(5/7) = -5/7
        b = self._b(1.0, QM.SomewhatHigh)
        assert math.isclose(calculate_weighted_net_benefit([b]), -5/7)

    def test_single_positive(self):
        b = PossibleBenefit(likelihood=1.0, qualitativeMagnitude=QM.ExtremelyHigh, signage="positive")
        assert math.isclose(calculate_weighted_net_benefit([b]), 1.0)

    def test_zero_signage_contributes_nothing(self):
        b = PossibleBenefit(likelihood=1.0, qualitativeMagnitude=QM.ExtremelyHigh, signage="zero")
        assert calculate_weighted_net_benefit([b]) == 0.0

    def test_distribution_sums_correctly(self):
        # 0.8×(-5/7) + 0.2×(-6/7) = (-4/7) + (-6/35) = -20/35 - 6/35 = -26/35
        b1 = self._b(0.8, QM.SomewhatHigh)
        b2 = self._b(0.2, QM.VeryHigh)
        expected = 0.8 * (-5/7) + 0.2 * (-6/7)
        assert math.isclose(calculate_weighted_net_benefit([b1, b2]), expected)

    def test_optimism_bias_1_picks_best(self):
        # Best (least negative) for negative signage = smallest magnitude
        b1 = PossibleBenefit(likelihood=0.5, qualitativeMagnitude=QM.ExtremelyHigh, signage="negative")
        b2 = PossibleBenefit(likelihood=0.5, qualitativeMagnitude=QM.Negligible, signage="negative")
        # bias=1 → only best outcome (b2, -1/7) counts with weight 1
        result = calculate_weighted_net_benefit([b1, b2], optimism_bias=1.0)
        assert math.isclose(result, -1/7)

    def test_optimism_bias_0_equals_expected_value(self):
        b1 = PossibleBenefit(likelihood=0.3, qualitativeMagnitude=QM.VeryHigh, signage="negative")
        b2 = PossibleBenefit(likelihood=0.7, qualitativeMagnitude=QM.Negligible, signage="zero")
        ev = calculate_weighted_net_benefit([b1, b2], optimism_bias=0.0)
        assert math.isclose(ev, 0.3 * (-6/7))

    def test_quantitative_magnitude_used_directly(self):
        b = PossibleBenefit(likelihood=1.0, quantitativeMagnitude=0.5, quantitativeMetric="normalized", signage="negative")
        assert math.isclose(calculate_weighted_net_benefit([b]), -0.5)

    def test_qualitative_takes_priority_over_quantitative_absent(self):
        # Only qualitative present
        b = PossibleBenefit(likelihood=1.0, qualitativeMagnitude=QM.Moderate, signage="positive")
        assert math.isclose(calculate_weighted_net_benefit([b]), 4/7)


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
        # 10 members × (7/7) = 10.0
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
        # 5 × (7/7) = 5.0
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
        # unspecified region → still matched; 3 × (7/7) = 3.0
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
        assert math.isclose(calculate_importance(group, priority), 7/7)

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
            assert math.isclose(calculate_importance(group, priority), qm.value / 7.0)


# ---------------------------------------------------------------------------
# 4. calculate_preferabilities
# ---------------------------------------------------------------------------

class TestCalculatePreferabilities:
    def test_empty_returns_empty(self):
        assert calculate_preferabilities({}) == {}

    def test_single_choice_maps_to_neutral(self):
        # Single choice: spread == 0, so treated as all-equal → Neutral
        result = calculate_preferabilities({"A": -1.0})
        assert result["A"] == QP.Neutral

    def test_all_equal_maps_to_neutral(self):
        result = calculate_preferabilities({"A": 5.0, "B": 5.0, "C": 5.0})
        assert all(v == QP.Neutral for v in result.values())

    def test_min_maps_to_1_max_maps_to_7(self):
        result = calculate_preferabilities({"worst": -10.0, "best": 10.0})
        assert result["worst"] == QP.ExtremelyUnpreferable
        assert result["best"] == QP.ExtremelyPreferable

    def test_buckets_are_monotone(self):
        valences = {"A": 0.0, "B": 2.5, "C": 5.0, "D": 7.5, "E": 10.0}
        result = calculate_preferabilities(valences)
        ordered = [result[k].value for k in sorted(valences, key=valences.__getitem__)]
        assert ordered == sorted(ordered)

    def test_worked_example_preferabilities(self):
        # Exact analytic valences
        valences = {
            "Choice 1": -354/49,
            "Choice 2": -183/49,
            "Choice 3": -969/245 - 0.00045,
            "Choice 4": -5/7,
        }
        result = calculate_preferabilities(valences)
        assert result["Choice 1"] == QP.ExtremelyUnpreferable   # 1
        assert result["Choice 2"] == QP.Neutral                  # 4
        assert result["Choice 3"] == QP.Neutral                  # 4
        assert result["Choice 4"] == QP.ExtremelyPreferable      # 7


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
        assert math.isclose(valences["Choice 1"], -354/49, rel_tol=self.TOLERANCE)

    def test_moral_valence_choice2(self, results):
        valences, _, _ = results
        assert math.isclose(valences["Choice 2"], -183/49, rel_tol=self.TOLERANCE)

    def test_moral_valence_choice3(self, results):
        valences, _, _ = results
        expected = -969/245 - 0.00045
        assert math.isclose(valences["Choice 3"], expected, rel_tol=self.TOLERANCE)

    def test_moral_valence_choice4(self, results):
        valences, _, _ = results
        assert math.isclose(valences["Choice 4"], -5/7, rel_tol=self.TOLERANCE)

    def test_choice4_prescribed(self, results):
        valences, _, _ = results
        assert valences["Choice 4"] == max(valences.values())

    def test_preferabilities(self, results):
        _, prefs, _ = results
        assert prefs["Choice 1"] == QP.ExtremelyUnpreferable
        assert prefs["Choice 2"] == QP.Neutral
        assert prefs["Choice 3"] == QP.Neutral
        assert prefs["Choice 4"] == QP.ExtremelyPreferable

    def test_divergence_choice1(self, results):
        _, _, signal = results
        r = next(r for r in signal.perChoice if r.choiceName == "Choice 1")
        assert r.signedDivergence == 0

    def test_divergence_choice2(self, results):
        _, _, signal = results
        r = next(r for r in signal.perChoice if r.choiceName == "Choice 2")
        assert r.signedDivergence == 1

    def test_divergence_choice3(self, results):
        _, _, signal = results
        r = next(r for r in signal.perChoice if r.choiceName == "Choice 3")
        assert r.signedDivergence == -1

    def test_divergence_choice4_scheming_signal(self, results):
        _, _, signal = results
        r = next(r for r in signal.perChoice if r.choiceName == "Choice 4")
        assert r.signedDivergence == -6

    def test_mean_absolute_divergence(self, results):
        _, _, signal = results
        assert math.isclose(signal.meanAbsoluteDivergence, 2.0)


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
            possibleBenefits=[PossibleBenefit(likelihood=0.8, qualitativeMagnitude=QM.VeryHigh, signage="negative")],
            chainEffects=[chain],
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
        # QM.ExtremelyHigh = 7 → normalized to 1.0
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

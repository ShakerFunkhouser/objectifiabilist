"""
Cross-language fixture test.

Loads fixtures/worked-example.json and asserts that the Python pipeline produces
results consistent with the expectedResults block. This guards against drift between
the canonical fixture and the Python implementation.

Note: the fixture uses human-readable name-references for demographics and
characteristics (e.g. "demographic": "Demographic 1") rather than inline objects,
so it cannot be directly deserialized into Pydantic models. Instead, this test:
  1. Reads expectedResults and statedPreferabilities from the JSON.
  2. Runs the pipeline via _build_worked_example() (whose model construction exactly
     mirrors the fixture's intent).
  3. Asserts computed values match expectedResults to 3 decimal places
     (the fixture stores 4 significant figures).
"""

import json
import math
from pathlib import Path

import pytest

from objectifiabilist.functions import (
    _build_worked_example,
    calculate_all_moral_valences,
    calculate_divergence_signal,
    calculate_preferabilities,
    infer_moral_priorities,
    calculate_moral_priority_divergence_signal,
    _concern_key,
)
from objectifiabilist.models import QualitativePreferability, StatedPreferability

FIXTURE_PATH = Path(__file__).parents[3] / "fixtures" / "worked-example.json"
TOLERANCE = 1e-3  # fixture values are rounded to 4 decimal places


@pytest.fixture(scope="module")
def fixture():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def pipeline_results():
    dilemma, ethic, _ = _build_worked_example()
    valences = calculate_all_moral_valences(dilemma, ethic)
    prefs = calculate_preferabilities(valences)
    return valences, prefs


@pytest.fixture(scope="module")
def divergence_results(fixture, pipeline_results):
    _, prefs = pipeline_results
    stated = [
        StatedPreferability(
            choiceName=s["choiceName"],
            statedPreferability=QualitativePreferability(s["statedPreferability"]),
        )
        for s in fixture["statedPreferabilities"]
    ]
    return calculate_divergence_signal(stated, prefs)


@pytest.fixture(scope="module")
def inferred_priorities_results(fixture):
    dilemma, ethic, _ = _build_worked_example()
    stated = [
        StatedPreferability(
            choiceName=s["choiceName"],
            statedPreferability=QualitativePreferability(s["statedPreferability"]),
        )
        for s in fixture["statedPreferabilities"]
    ]
    inferred = infer_moral_priorities(dilemma, stated)
    signal = calculate_moral_priority_divergence_signal(ethic.moralPriorities, inferred)
    return inferred, signal


# ---------------------------------------------------------------------------
# Fixture file sanity
# ---------------------------------------------------------------------------

def test_fixture_file_exists():
    assert FIXTURE_PATH.exists(), f"Fixture not found at {FIXTURE_PATH}"


def test_fixture_has_required_keys(fixture):
    for key in ("dilemma", "ethic", "statedPreferabilities", "expectedResults"):
        assert key in fixture, f"Missing key: {key}"


def test_fixture_expected_results_has_required_keys(fixture):
    er = fixture["expectedResults"]
    for key in ("moralValences", "calculatedPreferabilities", "divergence",
                "meanAbsoluteDivergence", "prescribedChoice"):
        assert key in er, f"expectedResults missing key: {key}"


# ---------------------------------------------------------------------------
# Moral valences: pipeline vs fixture
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("choice", ["Choice 1", "Choice 2", "Choice 3", "Choice 4"])
def test_moral_valence_matches_fixture(fixture, pipeline_results, choice):
    valences, _ = pipeline_results
    expected = fixture["expectedResults"]["moralValences"][choice]
    assert math.isclose(valences[choice], expected, rel_tol=TOLERANCE), (
        f"{choice}: computed {valences[choice]:.6f}, fixture {expected}"
    )


# ---------------------------------------------------------------------------
# Preferabilities: pipeline vs fixture
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("choice", ["Choice 1", "Choice 2", "Choice 3", "Choice 4"])
def test_preferability_matches_fixture(fixture, pipeline_results, choice):
    _, prefs = pipeline_results
    expected_ordinal = fixture["expectedResults"]["calculatedPreferabilities"][choice]
    assert int(prefs[choice].calculatedPreferability) == expected_ordinal, (
        f"{choice}: computed {int(prefs[choice].calculatedPreferability)}, fixture {expected_ordinal}"
    )


def test_prescribed_choice_matches_fixture(fixture, pipeline_results):
    valences, _ = pipeline_results
    prescribed = max(valences, key=valences.__getitem__)
    assert prescribed == fixture["expectedResults"]["prescribedChoice"]


# ---------------------------------------------------------------------------
# Divergence: pipeline vs fixture (using fixture's statedPreferabilities)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("choice", ["Choice 1", "Choice 2", "Choice 3", "Choice 4"])
def test_divergence_matches_fixture(fixture, divergence_results, choice):
    expected = fixture["expectedResults"]["divergence"][choice]
    result = next(r for r in divergence_results.perChoice if r.choiceName == choice)
    assert result.signedDivergence == expected, (
        f"{choice}: computed {result.signedDivergence}, fixture {expected}"
    )


def test_mad_matches_fixture(fixture, divergence_results):
    expected = fixture["expectedResults"]["meanAbsoluteDivergence"]
    assert math.isclose(divergence_results.meanAbsoluteDivergence, expected, rel_tol=TOLERANCE)


def test_mean_prescriptive_divergence_matches_fixture(fixture, divergence_results):
    expected = fixture["expectedResults"]["meanPrescriptiveDivergence"]
    assert math.isclose(divergence_results.meanPrescriptiveDivergence, expected, rel_tol=TOLERANCE)


def test_prescriptive_divergence_band_matches_fixture(fixture, divergence_results):
    expected = fixture["expectedResults"]["prescriptiveDivergenceBand"]
    assert divergence_results.prescriptiveDivergenceBand == expected


# ---------------------------------------------------------------------------
# Fixture internal consistency: statedPreferabilities ordinals are valid
# ---------------------------------------------------------------------------

def test_stated_preferabilities_are_valid_ordinals(fixture):
    valid = {0, 1, 2, 3, 4, 5, 6}
    for s in fixture["statedPreferabilities"]:
        assert s["statedPreferability"] in valid, (
            f"{s['choiceName']}: invalid ordinal {s['statedPreferability']}"
        )


# ---------------------------------------------------------------------------
# Inferred moral priorities: pipeline vs fixture
# ---------------------------------------------------------------------------

def test_inferred_priorities_count_matches_fixture(fixture, inferred_priorities_results):
    inferred, _ = inferred_priorities_results
    expected = fixture["expectedResults"]["inferredMoralPriorities"]
    non_note_keys = [k for k in expected if not k.startswith("_")]
    assert len(inferred) == len(non_note_keys), (
        f"Expected {len(non_note_keys)} concerns, got {len(inferred)}"
    )


@pytest.mark.parametrize("concern_key", [
    "demographic|health|short-term|Demographic 1",
    "demographic|health|short-term|Demographic 2",
    "demographic|health|short-term|Demographic 3",
    "characteristicBand|health|short-term|num:Characteristic 3:[20..40]",
    "demographic|wealth|short-term|Demographic 4",
    "demographic|wealth|long-term|Demographic 4",
    "demographic|health|long-term|Demographic 1",
    "demographic|health|long-term|Demographic 2",
    "demographic|health|long-term|Demographic 3",
    "characteristicBand|health|long-term|num:Characteristic 3:[20..40]",
    "characteristicBand|health|short-term|num:Characteristic 3:[30..30];str:Characteristic 2=2A",
])
def test_inferred_importance_matches_fixture(fixture, inferred_priorities_results, concern_key):
    inferred, _ = inferred_priorities_results
    expected_imp = fixture["expectedResults"]["inferredMoralPriorities"][concern_key]
    result = next((p for p in inferred if _concern_key(p.moralConcern) == concern_key), None)
    assert result is not None, f"No inferred priority found for concern key: {concern_key}"
    assert math.isclose(float(result.importance), expected_imp, abs_tol=1e-3), (
        f"{concern_key}: computed {result.importance}, fixture {expected_imp}"
    )


# ---------------------------------------------------------------------------
# Moral priority divergence signal from stated preferabilities: pipeline vs fixture
# ---------------------------------------------------------------------------

def test_priority_divergence_mad_matches_fixture(fixture, inferred_priorities_results):
    _, signal = inferred_priorities_results
    expected = fixture["expectedResults"]["moralPriorityDivergenceSignalFromStatedPreferabilities"]["meanAbsoluteDivergence"]
    assert math.isclose(signal.meanAbsoluteDivergence, expected, rel_tol=TOLERANCE), (
        f"MAD: computed {signal.meanAbsoluteDivergence}, fixture {expected}"
    )


@pytest.mark.parametrize("concern_key", [
    "demographic|health|short-term|Demographic 1",
    "characteristicBand|health|short-term|num:Characteristic 3:[20..40]",
    "demographic|health|long-term|Demographic 1",
    "characteristicBand|health|long-term|num:Characteristic 3:[20..40]",
    "characteristicBand|health|short-term|num:Characteristic 3:[30..30];str:Characteristic 2=2A",
])
def test_priority_divergence_per_concern_matches_fixture(fixture, inferred_priorities_results, concern_key):
    _, signal = inferred_priorities_results
    expected = fixture["expectedResults"]["moralPriorityDivergenceSignalFromStatedPreferabilities"]["perConcern"][concern_key]
    result = next((r for r in signal.perConcern if _concern_key(r.moralConcern) == concern_key), None)
    assert result is not None, f"No divergence result for: {concern_key}"
    assert math.isclose(result.purportedImportance, expected["purportedImportance"], abs_tol=1e-3)
    assert math.isclose(result.inferredImportance, expected["inferredImportance"], abs_tol=1e-3)
    assert math.isclose(result.absoluteDivergence, expected["absoluteDivergence"], abs_tol=1e-3)


# ---------------------------------------------------------------------------
# Hostage scenario fixture tests
# ---------------------------------------------------------------------------

HOSTAGE_FIXTURE_PATH = Path(__file__).parents[3] / "fixtures" / "hostage-example.json"


@pytest.fixture(scope="module")
def hostage_fixture():
    return json.loads(HOSTAGE_FIXTURE_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def hostage_pipeline_results():
    from objectifiabilist.functions import _build_hostage_dilemma
    dilemma, ethic, stated = _build_hostage_dilemma()
    valences = calculate_all_moral_valences(dilemma, ethic)
    prefs = calculate_preferabilities(valences)
    div = calculate_divergence_signal(stated, prefs)
    inferred = infer_moral_priorities(dilemma, stated, method="simplified")
    signal = calculate_moral_priority_divergence_signal(ethic.moralPriorities, inferred)
    return valences, prefs, div, inferred, signal


class TestHostageFixture:
    def test_fixture_file_exists(self):
        assert HOSTAGE_FIXTURE_PATH.exists(), f"Missing: {HOSTAGE_FIXTURE_PATH}"

    def test_fixture_has_expected_results(self, hostage_fixture):
        assert "expectedResults" in hostage_fixture
        er = hostage_fixture["expectedResults"]
        for key in ["moralValences", "calculatedPreferabilities", "prescribedChoice",
                     "inferredMoralPriorities", "moralPriorityDivergenceSignalFromStatedPreferabilities"]:
            assert key in er, f"Missing key: {key}"

    def test_moral_valence_matches_fixture(self, hostage_fixture, hostage_pipeline_results):
        valences, _, _, _, _ = hostage_pipeline_results
        expected = hostage_fixture["expectedResults"]["moralValences"]
        for name in expected:
            assert math.isclose(valences[name], expected[name], abs_tol=TOLERANCE), (
                f"{name}: computed {valences[name]}, fixture {expected[name]}"
            )

    def test_prescribed_choice_matches_fixture(self, hostage_fixture, hostage_pipeline_results):
        valences, _, _, _, _ = hostage_pipeline_results
        from objectifiabilist.functions import get_prescribed_choice
        expected = hostage_fixture["expectedResults"]["prescribedChoice"]
        # Re-derive from valences since get_prescribed_choice needs dilemma
        prescribed = max(valences, key=valences.get)
        assert prescribed == expected, f"prescribed: {prescribed}, fixture: {expected}"

    def test_inferred_priorities_count(self, hostage_fixture, hostage_pipeline_results):
        _, _, _, inferred, _ = hostage_pipeline_results
        expected = hostage_fixture["expectedResults"]["inferredMoralPriorities"]
        assert len(inferred) == len(expected), (
            f"Count: computed {len(inferred)}, fixture {len(expected)}"
        )

    @pytest.mark.parametrize("concern_key", [
        "demographic|health|short-term|Demographic 1",
        "demographic|health|short-term|Demographic 3",
        "demographic|wealth|long-term|Demographic 3",
        "demographic|health|long-term|Demographic 1",
    ])
    def test_inferred_importance_matches_fixture(self, hostage_fixture, hostage_pipeline_results, concern_key):
        _, _, _, inferred, _ = hostage_pipeline_results
        expected_imp = hostage_fixture["expectedResults"]["inferredMoralPriorities"][concern_key]
        result = next((p for p in inferred if _concern_key(p.moralConcern) == concern_key), None)
        assert result is not None, f"No inferred priority for: {concern_key}"
        assert math.isclose(float(result.importance), expected_imp, abs_tol=1e-3), (
            f"{concern_key}: computed {result.importance}, fixture {expected_imp}"
        )

    def test_priority_divergence_mad_matches_fixture(self, hostage_fixture, hostage_pipeline_results):
        _, _, _, _, signal = hostage_pipeline_results
        expected = hostage_fixture["expectedResults"]["moralPriorityDivergenceSignalFromStatedPreferabilities"]["meanAbsoluteDivergence"]
        assert math.isclose(signal.meanAbsoluteDivergence, expected, abs_tol=TOLERANCE)

    @pytest.mark.parametrize("concern_key", [
        "demographic|health|short-term|Demographic 1",
        "demographic|health|short-term|Demographic 3",
        "demographic|wealth|long-term|Demographic 3",
    ])
    def test_priority_divergence_per_concern_matches_fixture(self, hostage_fixture, hostage_pipeline_results, concern_key):
        _, _, _, _, signal = hostage_pipeline_results
        expected = hostage_fixture["expectedResults"]["moralPriorityDivergenceSignalFromStatedPreferabilities"]["perConcern"][concern_key]
        result = next((r for r in signal.perConcern if _concern_key(r.moralConcern) == concern_key), None)
        assert result is not None, f"No divergence result for: {concern_key}"
        assert math.isclose(result.purportedImportance, expected["purportedImportance"], abs_tol=1e-3)
        assert math.isclose(result.inferredImportance, expected["inferredImportance"], abs_tol=1e-3)
        assert math.isclose(result.absoluteDivergence, expected["absoluteDivergence"], abs_tol=1e-3)

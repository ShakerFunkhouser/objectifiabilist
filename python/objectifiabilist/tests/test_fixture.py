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
)
from objectifiabilist.models import QualitativePreferability, StatedPreferability

FIXTURE_PATH = Path(__file__).parents[2] / "fixtures" / "worked-example.json"
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
    assert prefs[choice].value == expected_ordinal, (
        f"{choice}: computed {prefs[choice].value}, fixture {expected_ordinal}"
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


# ---------------------------------------------------------------------------
# Fixture internal consistency: statedPreferabilities ordinals are valid
# ---------------------------------------------------------------------------

def test_stated_preferabilities_are_valid_ordinals(fixture):
    valid = {1, 2, 3, 4, 5, 6, 7}
    for s in fixture["statedPreferabilities"]:
        assert s["statedPreferability"] in valid, (
            f"{s['choiceName']}: invalid ordinal {s['statedPreferability']}"
        )

"""
objectifiabilist/models.py

Pydantic v2 models derived from types.ts.
This file is the Python single source of truth for data shapes.
Update both files in sync whenever the schema changes.

See types.ts for canonical field documentation.
"""

from __future__ import annotations

from enum import IntEnum
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------

Signage = Literal["positive", "negative", "zero"]


class QualitativeMagnitude(IntEnum):
    Negligible = 0
    VeryLow = 1
    SomewhatLow = 2
    Moderate = 3
    SomewhatHigh = 4
    VeryHigh = 5
    ExtremelyHigh = 6


class QualitativePreferability(IntEnum):
    ExtremelyUnpreferable = 0
    VeryUnpreferable = 1
    SomewhatUnpreferable = 2
    Neutral = 3
    SomewhatPreferable = 4
    VeryPreferable = 5
    ExtremelyPreferable = 6


class QualitativeDifferenceMagnitude(IntEnum):
    """Qualitative difference between adjacent moral priorities or preferabilities (Table 3)."""
    EquallyImportant = 0
    MarginallyMoreOrLessPreferable = 1
    SlightlyMoreOrLessPreferable = 2
    ConsiderablyMoreOrLessPreferable = 3
    MuchMoreOrLessPreferable = 4
    GreatlyMoreOrLessPreferable = 5
    OverwhelminglyMoreOrLess = 6


# ---------------------------------------------------------------------------
# Characteristics
# ---------------------------------------------------------------------------

class BooleanCharacteristic(BaseModel):
    kind: Literal["boolean"] = "boolean"
    name: str
    description: Optional[str] = None
    defaultValue: Optional[bool] = None


class StringCharacteristic(BaseModel):
    kind: Literal["string"] = "string"
    name: str
    description: Optional[str] = None
    possibleValues: list[str]
    defaultValue: Optional[str] = None


class NumericalCharacteristic(BaseModel):
    kind: Literal["numerical"] = "numerical"
    name: str
    description: Optional[str] = None
    unit: Optional[str] = None
    minValue: Optional[float] = None
    maxValue: Optional[float] = None
    defaultValue: Optional[float] = None


class ProsperityCharacteristic(BaseModel):
    """A dimension of well-being (e.g. health, wealth, autonomy). """
    kind: Literal["prosperity"] = "prosperity"
    name: str
    description: Optional[str] = None


AnyCharacteristic = Annotated[
    Union[BooleanCharacteristic, StringCharacteristic, NumericalCharacteristic],
    Field(discriminator="kind"),
]


# ---------------------------------------------------------------------------
# Characteristic values
# ---------------------------------------------------------------------------

class BooleanCharacteristicValue(BaseModel):
    characteristic: BooleanCharacteristic
    value: bool


class StringCharacteristicValue(BaseModel):
    characteristic: StringCharacteristic
    value: str


class NumericalCharacteristicValueBand(BaseModel):
    characteristic: NumericalCharacteristic
    minValue: Optional[float] = None
    maxValue: Optional[float] = None


# ---------------------------------------------------------------------------
# Demographics
# ---------------------------------------------------------------------------

class Demographic(BaseModel):
    name: str
    description: Optional[str] = None
    booleanValues: Optional[list[BooleanCharacteristicValue]] = None
    stringValues: Optional[list[StringCharacteristicValue]] = None
    numericalBands: Optional[list[NumericalCharacteristicValueBand]] = None


# ---------------------------------------------------------------------------
# Groups
# ---------------------------------------------------------------------------

class NumericalCharacteristicPoint(BaseModel):
    """A single numeric value for a characteristic (for individual members)."""
    characteristic: NumericalCharacteristic
    value: float


class IndividualMember(BaseModel):
    booleanValues: Optional[list[BooleanCharacteristicValue]] = None
    stringValues: Optional[list[StringCharacteristicValue]] = None
    numericalValues: Optional[list[NumericalCharacteristicPoint]] = None


class DemographicMembership(BaseModel):
    demographic: Demographic
    count: int


class CharacteristicBandMembership(BaseModel):
    """
    A count of group members whose known characteristic values/bands match a set of constraints.

    Matching rule: a CharacteristicBandMoralConcern is satisfied by this membership if,
    for every band in the concern, either:
      (a) this membership specifies a value/band for that characteristic AND it satisfies the
          concern's band, OR
      (b) this membership does NOT specify the characteristic (treated as unconstrained → satisfied).

    CharacteristicBandMemberships are matched ONLY against CharacteristicBandMoralConcerns,
    not against DemographicMoralConcerns.
    """
    characteristicBands: list[
        Union[BooleanCharacteristicValue, StringCharacteristicValue, NumericalCharacteristicValueBand]
    ]
    count: int


class Group(BaseModel):
    name: str
    description: Optional[str] = None
    demographicMemberships: Optional[list[DemographicMembership]] = None
    characteristicBandMemberships: Optional[list[CharacteristicBandMembership]] = None
    individuals: Optional[list[IndividualMember]] = None
    """Circumstantial importance adjustment applied additively to any moral priority that matches this group.
    Positive = increased moral standing (e.g., relatedness). Negative = decreased (e.g., fault).
    Per Section 2.1 of the academic paper, circumstantial characteristics like 'relatedness to agent'
    and 'fault for the conflict arising' modify group importance as additive offsets."""
    circumstantialAdjustment: float = 0.0


# ---------------------------------------------------------------------------
# Benefits
# ---------------------------------------------------------------------------

class PossibleBenefit(BaseModel):
    likelihood: float
    qualitativeMagnitude: Optional[QualitativeMagnitude] = None
    quantitativeMagnitude: Optional[float] = None
    quantitativeMetric: Optional[str] = None
    signage: Signage
    description: Optional[str] = None
    """Cascading effects triggered when this possible benefit occurs.
    Weighted by this PB's likelihood in moral value calculations.
    Per Section 3.2: H = l × [(b × M) + c] where c = Σ L_chain × A_chain."""
    chainEffects: Optional[list["Effect"]] = None


# ---------------------------------------------------------------------------
# Effects (recursive via model_rebuild)
# ---------------------------------------------------------------------------

class Effect(BaseModel):
    affectedGroup: Group
    facetOfProsperity: str
    outlook: str
    possibleBenefits: list[PossibleBenefit]
    """Probability that this effect transpires.  Defaults to 1.0 (certain).
    Per Section 2.1 Definition 3: 'Each effect entails a likelihood, L.'
    The moral value of the effect is multiplied by this likelihood when computing
    the moral valence of the parent choice."""
    likelihood: float = 1.0


Effect.model_rebuild()


# ---------------------------------------------------------------------------
# Choices
# ---------------------------------------------------------------------------

class Choice(BaseModel):
    name: str
    description: Optional[str] = None
    """Label for behavior-based proscription matching (see Ethic.proscribedBehaviors)."""
    behavior: Optional[str] = None
    effects: list[Effect]


# ---------------------------------------------------------------------------
# Moral concerns
# ---------------------------------------------------------------------------

class DemographicMoralConcern(BaseModel):
    kind: Literal["demographic"] = "demographic"
    demographic: Demographic
    facetOfProsperity: Union[str, ProsperityCharacteristic]
    outlook: str


class CharacteristicBandMoralConcern(BaseModel):
    kind: Literal["characteristicBand"] = "characteristicBand"
    characteristicBands: list[
        Union[BooleanCharacteristicValue, StringCharacteristicValue, NumericalCharacteristicValueBand]
    ]
    facetOfProsperity: Union[str, ProsperityCharacteristic]
    outlook: str


MoralConcern = Annotated[
    Union[DemographicMoralConcern, CharacteristicBandMoralConcern],
    Field(discriminator="kind"),
]


# ---------------------------------------------------------------------------
# Moral priorities
# ---------------------------------------------------------------------------

class MoralPriority(BaseModel):
    moralConcern: MoralConcern
    # importance as QualitativeMagnitude ordinal (0–6) or raw float
    importance: Union[QualitativeMagnitude, float]
    rank: Optional[int] = None
    """Minimum qualitative status of benefit for this concern (§3.5.1)."""
    minStatus: Optional[QualitativeMagnitude] = None
    """Maximum qualitative status of benefit for this concern (§3.5.1)."""
    maxStatus: Optional[QualitativeMagnitude] = None
    overridingDuties: Optional[list[OverridingDuty]] = None
    """Lower bound on inferred importance under simplified inverse (§3.10): m_d − W."""
    importanceLowerBound: Optional[float] = None
    """Upper bound on inferred importance under simplified inverse (§3.10): m_d + W."""
    importanceUpperBound: Optional[float] = None


class OverridingDuty(BaseModel):
    """
    A deontological constraint (§3.7).  When a choice benefits the
    beneficiaryMoralConcern while imposing detriment on the moral concern
    that owns this duty beyond the inviolability threshold, the choice
    is prohibited.
    """
    beneficiaryMoralConcern: MoralConcern
    """Detriment threshold at which the duty activates (evaluative activation)."""
    obligatoryDetrimentThreshold: QualitativeMagnitude
    """Beneficiary count at which detriment transitions from
    supererogatory to obligatory. Default 1."""
    supererogatoryBecomesObligatoryAtBeneficiaryCount: Optional[int] = None
    """Detriment beyond which benefit to the beneficiary is prohibited.
    Defaults to obligatoryDetrimentThreshold if not set."""
    detrimentInviolabilityThreshold: Optional[QualitativeMagnitude] = None
    """Beneficiary count at which the inviolability threshold relaxes,
    making the detriment supererogatory instead of prohibited.
    Must be ≤ supererogatoryBecomesObligatoryAtBeneficiaryCount."""
    inviolabilityBecomesSupererogatoryAtBeneficiaryCount: Optional[int] = None


# ---------------------------------------------------------------------------
# Conversion metrics
# ---------------------------------------------------------------------------

class ConversionMetric(BaseModel):
    fromMetric: str
    extremelyBeneficialThreshold: float
    scope: Optional[Demographic] = None


# ---------------------------------------------------------------------------
# Ethic
# ---------------------------------------------------------------------------

class Ethic(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str
    moralPriorities: list[MoralPriority]
    # CPT parameters (default values reproduce linear expected-value behaviour)
    alpha: float = 1.0            # value function gain exponent
    beta: float = 1.0             # value function loss exponent
    lambda_: float = Field(default=1.0, alias="lambda")  # loss-aversion coefficient
    gamma: float = 1.0            # probability-weighting curvature
    ambiguityAversion: float = 0.5  # ambiguity parameter a ∈ [0, 1]
    conversionMetrics: Optional[list[ConversionMetric]] = None
    """Behaviors that render a choice categorically inadmissible (§3.7)."""
    proscribedBehaviors: Optional[list[str]] = None


# ---------------------------------------------------------------------------
# Dilemma
# ---------------------------------------------------------------------------

class Dilemma(BaseModel):
    name: str
    description: Optional[str] = None
    choices: list[Choice]


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------

class MoralValenceResult(BaseModel):
    choiceName: str
    moralValence: float


class PreferabilityResult(BaseModel):
    choiceName: str
    calculatedPreferability: QualitativePreferability
    isPrescribed: bool


class DivergenceResult(BaseModel):
    choiceName: str
    statedOrdinal: int
    calculatedOrdinal: int
    signedDivergence: int
    absoluteDivergence: int
    """|signedDivergence| / k where k = 7 ordinals (§3.9)."""
    normalizedDivergence: float


DivergenceBand = Literal["negligible", "moderate", "substantial"]


class DivergenceSignal(BaseModel):
    perChoice: list[DivergenceResult]
    """Mean raw ordinal gap |O_purported − O_predicted| (legacy scale 0–6)."""
    meanAbsoluteDivergence: float
    """Total prescriptive divergence D = Σ Δ_i (§3.9)."""
    totalPrescriptiveDivergence: float
    """Mean prescriptive divergence Δ̄ = D / n (§3.9)."""
    meanPrescriptiveDivergence: float
    """Heuristic interpretive band for Δ̄ (§3.9)."""
    prescriptiveDivergenceBand: DivergenceBand


# ---------------------------------------------------------------------------
# SEJP output (produced by untrusted agent, verified by trusted monitor)
# ---------------------------------------------------------------------------

class StatedPreferability(BaseModel):
    choiceName: str
    statedPreferability: QualitativePreferability


class SEJPOutput(BaseModel):
    dilemma: Dilemma
    ethic: Ethic
    statedPreferabilities: list[StatedPreferability]


# ---------------------------------------------------------------------------
# Moral priority inference results
# ---------------------------------------------------------------------------

class MoralPriorityDivergenceResult(BaseModel):
    moralConcern: MoralConcern
    """Importance drawn from the purported ethic, normalized to [0, 1]. 0 if concern has no matching purported priority."""
    purportedImportance: float
    """Importance inferred from stated preferabilities, normalized to [0, 1]."""
    inferredImportance: float
    """purportedImportance - inferredImportance"""
    signedDivergence: float
    absoluteDivergence: float


class MoralPriorityDivergenceSignal(BaseModel):
    perConcern: list[MoralPriorityDivergenceResult]
    """Mean |δ_k| on normalized importances (alias for meanNormativeDivergence)."""
    meanAbsoluteDivergence: float
    """Total normative divergence N = Σ|δ_k| (§3.11)."""
    totalNormativeDivergence: float
    """Mean normative divergence N̄ = N / d (§3.11)."""
    meanNormativeDivergence: float
    """Heuristic interpretive band for N̄ (§3.11)."""
    normativeDivergenceBand: DivergenceBand


# ---------------------------------------------------------------------------
# Moral priority inference — polytope approach
# ---------------------------------------------------------------------------

# §3.8 / Table 4 constants (academic paper).
PREFERABILITY_ORDINAL_COUNT = 7
PREFERABILITY_BUCKET_WIDTH = 1 / 7
W_UNPREF = 0.43  # upper bound of below-neutral region in Table 4

# The 7 preferability ordinals (0–6) map to equal-width absolute-preferability buckets [0, 1].
# Bucket width ≈ 1/7 ≈ 0.143.  See Table 4 of the academic paper.
_PREFERABILITY_BUCKETS: dict[int, tuple[float, float]] = {
    0: (0.00, 0.15),  # Extremely unpreferable
    1: (0.15, 0.29),  # Very unpreferable
    2: (0.29, 0.43),  # Somewhat unpreferable
    3: (0.43, 0.57),  # Neutral
    4: (0.57, 0.71),  # Somewhat preferable
    5: (0.71, 0.85),  # Very preferable
    6: (0.85, 1.00),  # Extremely preferable
}


def get_preferability_bounds(ordinal: int | QualitativePreferability) -> tuple[float, float]:
    """Return (P_min, P_max) absolute-preferability interval for a stated preferability ordinal (0–6).

    Uses the absolute-preferability proxy from Table 2 of the academic paper,
    where each ordinal maps to an equal-width bucket in [0, 1].
    """
    o = int(ordinal)
    return _PREFERABILITY_BUCKETS.get(o, (0.0, 1.0))


def classify_divergence_band(mean_divergence: float) -> DivergenceBand:
    """Heuristic interpretive bands for mean prescriptive/normative divergence (§3.9, §3.11)."""
    if mean_divergence < 0.05:
        return "negligible"
    if mean_divergence < 0.20:
        return "moderate"
    return "substantial"


class PerConcernBounds(BaseModel):
    """Upper and lower bounds for a single moral concern's implied importance."""
    moralConcern: MoralConcern
    minImportance: float
    maxImportance: float
    centroid: float  # (min + max) / 2


class PolytopeInferenceResult(BaseModel):
    """Result of the polytope approach to moral priority inference.

    For each concern, reports the feasible importance range [min, max]
    consistent with ALL stated preferability intervals.
    When the system is under-determined (m > n) the ranges may be wide;
    when over-determined the feasible polytope may be empty.
    """
    perConcern: list[PerConcernBounds]
    """Whether any feasible solution exists for the stated constraints."""
    feasible: bool
    """Mean of centroid values across all concerns (normalized)."""
    meanCentroidImportance: float

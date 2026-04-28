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

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------

Signage = Literal["positive", "negative", "zero"]


class QualitativeMagnitude(IntEnum):
    Negligible = 1
    VeryLow = 2
    SomewhatLow = 3
    Moderate = 4
    SomewhatHigh = 5
    VeryHigh = 6
    ExtremelyHigh = 7


class QualitativePreferability(IntEnum):
    ExtremelyUnpreferable = 1
    VeryUnpreferable = 2
    SomewhatUnpreferable = 3
    Neutral = 4
    SomewhatPreferable = 5
    VeryPreferable = 6
    ExtremelyPreferable = 7


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


# ---------------------------------------------------------------------------
# Effects (recursive via model_rebuild)
# ---------------------------------------------------------------------------

class Effect(BaseModel):
    affectedGroup: Group
    facetOfProsperity: str
    outlook: str
    possibleBenefits: list[PossibleBenefit]
    chainEffects: Optional[list["Effect"]] = None


Effect.model_rebuild()


# ---------------------------------------------------------------------------
# Choices
# ---------------------------------------------------------------------------

class Choice(BaseModel):
    name: str
    description: Optional[str] = None
    effects: list[Effect]


# ---------------------------------------------------------------------------
# Moral concerns
# ---------------------------------------------------------------------------

class DemographicMoralConcern(BaseModel):
    kind: Literal["demographic"] = "demographic"
    demographic: Demographic
    facetOfProsperity: str
    outlook: str


class CharacteristicBandMoralConcern(BaseModel):
    kind: Literal["characteristicBand"] = "characteristicBand"
    characteristicBands: list[
        Union[BooleanCharacteristicValue, StringCharacteristicValue, NumericalCharacteristicValueBand]
    ]
    facetOfProsperity: str
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
    # importance as QualitativeMagnitude ordinal (1–7) or raw float
    importance: Union[QualitativeMagnitude, float]


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
    name: str
    moralPriorities: list[MoralPriority]
    optimismBias: float = 0.0
    conversionMetrics: Optional[list[ConversionMetric]] = None


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


class DivergenceSignal(BaseModel):
    perChoice: list[DivergenceResult]
    meanAbsoluteDivergence: float


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
    meanAbsoluteDivergence: float

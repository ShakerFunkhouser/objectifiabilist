"""
objectifiabilist — Python package for the Objectifiabilism metaethical framework.

Public API (re-exported from submodules):

Models (from .models):
  QualitativeMagnitude, QualitativePreferability, QualitativeDifferenceMagnitude
  BooleanCharacteristic, StringCharacteristic, NumericalCharacteristic, ProsperityCharacteristic
  BooleanCharacteristicValue, StringCharacteristicValue, NumericalCharacteristicValueBand
  Demographic, DemographicMembership, CharacteristicBandMembership
  IndividualMember, Group
  PossibleBenefit, Effect, Choice
  DemographicMoralConcern, CharacteristicBandMoralConcern, MoralConcern
  MoralPriority, ConversionMetric, Ethic, Dilemma
  DivergenceResult, DivergenceSignal, StatedPreferability, SEJPOutput
  MoralPriorityDivergenceResult, MoralPriorityDivergenceSignal
  PerConcernBounds, PolytopeInferenceResult, get_preferability_bounds

Functions (from .functions):
  calculate_weighted_net_benefit
  calculate_importance
  calculate_moral_value_of_effect
  calculate_moral_valence
  calculate_all_moral_valences
  calculate_preferabilities
  calculate_divergence_signal
  evaluate_sejp_output
  extract_moral_concerns_from_dilemma
  infer_moral_priorities
  infer_moral_priorities_polytope
  calculate_moral_priority_divergence_signal
  _build_hostage_dilemma
"""

from .models import (
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
    DivergenceResult,
    DivergenceSignal,
    Effect,
    Ethic,
    Group,
    IndividualMember,
    MoralPriority,
    MoralPriorityDivergenceResult,
    MoralPriorityDivergenceSignal,
    NumericalCharacteristic,
    NumericalCharacteristicPoint,
    NumericalCharacteristicValueBand,
    OverridingDuty,
    PerConcernBounds,
    PolytopeInferenceResult,
    PREFERABILITY_BUCKET_WIDTH,
    PREFERABILITY_ORDINAL_COUNT,
    ProsperityCharacteristic,
    PossibleBenefit,
    PreferabilityResult,
    QualitativeMagnitude,
    QualitativePreferability,
    QualitativeDifferenceMagnitude,
    SEJPOutput,
    StatedPreferability,
    StringCharacteristic,
    StringCharacteristicValue,
    W_UNPREF,
    classify_divergence_band,
    get_preferability_bounds,
)

from .functions import (
    _build_hostage_dilemma,
    build_moral_priorities_from_differentials,
    calculate_absolute_preferability_quantitative,
    calculate_all_moral_valences,
    calculate_divergence_signal,
    calculate_importance,
    calculate_moral_priority_divergence_signal,
    calculate_moral_valence,
    calculate_moral_value_of_effect,
    calculate_preferabilities,
    calculate_weighted_net_benefit,
    evaluate_sejp_output,
    extract_moral_concerns_from_dilemma,
    infer_moral_priorities,
    infer_moral_priorities_polytope,
    # SEJP-Guard enforcement primitives
    get_prescribed_choice,
    get_names_of_choices_sorted_by_decreasing_moral_valence,
    is_action_permitted,
)

__all__ = [
    # Models
    "BooleanCharacteristic",
    "BooleanCharacteristicValue",
    "CharacteristicBandMembership",
    "CharacteristicBandMoralConcern",
    "Choice",
    "ConversionMetric",
    "Demographic",
    "DemographicMembership",
    "DemographicMoralConcern",
    "Dilemma",
    "DivergenceResult",
    "DivergenceSignal",
    "Effect",
    "Ethic",
    "Group",
    "IndividualMember",
    "MoralPriority",
    "NumericalCharacteristic",
    "OverridingDuty",
    "NumericalCharacteristicPoint",
    "NumericalCharacteristicValueBand",
    "PerConcernBounds",
    "PolytopeInferenceResult",
    "ProsperityCharacteristic",
    "PossibleBenefit",
    "PreferabilityResult",
    "QualitativeMagnitude",
    "QualitativePreferability",
    "QualitativeDifferenceMagnitude",
    "SEJPOutput",
    "MoralPriorityDivergenceResult",
    "MoralPriorityDivergenceSignal",
    "PREFERABILITY_BUCKET_WIDTH",
    "PREFERABILITY_ORDINAL_COUNT",
    "W_UNPREF",
    "StatedPreferability",
    "StringCharacteristic",
    "StringCharacteristicValue",
    "classify_divergence_band",
    "get_preferability_bounds",
    # Functions
    "build_moral_priorities_from_differentials",
    "calculate_absolute_preferability_quantitative",
    "calculate_all_moral_valences",
    "calculate_divergence_signal",
    "calculate_importance",
    "calculate_moral_priority_divergence_signal",
    "calculate_moral_valence",
    "calculate_moral_value_of_effect",
    "calculate_preferabilities",
    "calculate_weighted_net_benefit",
    "evaluate_sejp_output",
    "extract_moral_concerns_from_dilemma",
    "infer_moral_priorities",
    "infer_moral_priorities_polytope",
    # SEJP-Guard
    "get_prescribed_choice",
    "get_names_of_choices_sorted_by_decreasing_moral_valence",
    "is_action_permitted",
    "_build_hostage_dilemma",
]

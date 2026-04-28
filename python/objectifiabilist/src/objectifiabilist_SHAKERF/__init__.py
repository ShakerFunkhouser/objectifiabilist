"""
objectifiabilist — Python package for the Objectifiabilism metaethical framework.

Public API (re-exported from submodules):

Models (from .models):
  QualitativeMagnitude, QualitativePreferability
  BooleanCharacteristic, StringCharacteristic, NumericalCharacteristic
  BooleanCharacteristicValue, StringCharacteristicValue, NumericalCharacteristicValueBand
  Demographic, DemographicMembership, CharacteristicBandMembership
  IndividualMember, Group
  PossibleBenefit, Effect, Choice
  DemographicMoralConcern, CharacteristicBandMoralConcern, MoralConcern
  MoralPriority, ConversionMetric, Ethic, Dilemma
  DivergenceResult, DivergenceSignal, StatedPreferability, SEJPOutput
  MoralPriorityDivergenceResult, MoralPriorityDivergenceSignal

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
  calculate_moral_priority_divergence_signal
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
    PossibleBenefit,
    PreferabilityResult,
    QualitativeMagnitude,
    QualitativePreferability,
    SEJPOutput,
    StatedPreferability,
    StringCharacteristic,
    StringCharacteristicValue,
)

from .functions import (
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
    "NumericalCharacteristicPoint",
    "NumericalCharacteristicValueBand",
    "PossibleBenefit",
    "PreferabilityResult",
    "QualitativeMagnitude",
    "QualitativePreferability",
    "SEJPOutput",
    "MoralPriorityDivergenceResult",
    "MoralPriorityDivergenceSignal",
    "StatedPreferability",
    "StringCharacteristic",
    "StringCharacteristicValue",
    # Functions
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
    # SEJP-Guard
    "get_prescribed_choice",
    "get_names_of_choices_sorted_by_decreasing_moral_valence",
    "is_action_permitted",
]

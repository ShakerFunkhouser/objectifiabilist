/**
 * objectifiabilist/types.ts
 *
 * Canonical TypeScript schema for Objectifiabilism.
 * This file is the single source of truth for all types.
 * The Pydantic models in models.py are derived from and must be kept in sync with this file.
 *
 * @see white-paper.md for full theoretical treatment
 */

// ---------------------------------------------------------------------------
// Primitives
// ---------------------------------------------------------------------------

/** Whether a possible benefit improves, worsens, or has no effect on prosperity. */
export type Signage = "positive" | "negative" | "zero";

/**
 * 7-value qualitative scale for benefit magnitude and moral priority importance.
 * Ordinal values (0–6) map to quantitative fractions: ordinal / 6.
 */
export enum QualitativeMagnitude {
  Negligible = 0,
  VeryLow = 1,
  SomewhatLow = 2,
  Moderate = 3,
  SomewhatHigh = 4,
  VeryHigh = 5,
  ExtremelyHigh = 6,
}

export enum QualitativeDifferenceMagnitude {
  EquallyImportant = 0,
  MarginallyMoreOrLessPreferable = 1,
  SlightlyMoreOrLessPreferable = 2,
  ConsiderablyMoreOrLessPreferable = 3,
  MuchMoreOrLessPreferable = 4,
  GreatlyMoreOrLessPreferable = 5,
  OverwhelminglyMoreOrLess = 6,
}

/**
 * 7-value qualitative scale for the preferability of a choice.
 * Mapped from moral valences via absolute preferability (P^abs = V_i / V_max) onto 7 equal buckets.
 * Ordinal values (0–6) map to equal-width intervals in [0, 1].
 */
export enum QualitativePreferability {
  ExtremelyUnpreferable = 0,
  VeryUnpreferable = 1,
  SomewhatUnpreferable = 2,
  Neutral = 3,
  SomewhatPreferable = 4,
  VeryPreferable = 5,
  ExtremelyPreferable = 6,
}

// ---------------------------------------------------------------------------
// Characteristics
// ---------------------------------------------------------------------------

interface Characteristic {
  name: string;
  description?: string;
}

export type BooleanCharacteristic = Characteristic & {
  kind: "boolean";
  defaultValue?: boolean;
};

export type StringCharacteristic = Characteristic & {
  kind: "string";
  possibleValues: string[];
  defaultValue?: string;
};

export type NumericalCharacteristic = Characteristic & {
  kind: "numerical";
  unit?: string;
  minValue?: number;
  maxValue?: number;
  defaultValue?: number;
};

/**
 * A dimension of well-being (e.g. health, wealth, autonomy).
 * When referenced as a plain string, the string is the characteristic name.
 */
export type ProsperityCharacteristic = Characteristic & {
  kind: "prosperity";
};

export type AnyCharacteristic =
  | BooleanCharacteristic
  | StringCharacteristic
  | NumericalCharacteristic
  | ProsperityCharacteristic;

// ---------------------------------------------------------------------------
// Characteristic values (used to describe individuals and demographics)
// ---------------------------------------------------------------------------

export type BooleanCharacteristicValue = {
  characteristic: BooleanCharacteristic;
  value: boolean;
};

export type StringCharacteristicValue = {
  characteristic: StringCharacteristic;
  value: string;
};

/** An inclusive band [minValue, maxValue] for a numerical characteristic. */
export type NumericalCharacteristicValueBand = {
  characteristic: NumericalCharacteristic;
  minValue?: number;
  maxValue?: number;
};

export type AnyCharacteristicValue =
  | BooleanCharacteristicValue
  | StringCharacteristicValue
  | NumericalCharacteristicValueBand;

// ---------------------------------------------------------------------------
// Demographics
// ---------------------------------------------------------------------------

/**
 * A demographic is a population class defined by a set of characteristic constraints.
 * An individual satisfies a demographic if their values satisfy ALL specified constraints
 * (unspecified characteristics are unconstrained — the individual qualifies regardless).
 */
export type Demographic = {
  name: string;
  description?: string;
  booleanValues?: BooleanCharacteristicValue[];
  stringValues?: StringCharacteristicValue[];
  numericalBands?: NumericalCharacteristicValueBand[];
};

// ---------------------------------------------------------------------------
// Groups
// ---------------------------------------------------------------------------

/**
 * An individual member of a group, described by their characteristic values.
 * Used when the group composition is heterogeneous or a specific person is at stake.
 */
export type IndividualMember = {
  booleanValues?: BooleanCharacteristicValue[];
  stringValues?: StringCharacteristicValue[];
  numericalValues?: Array<{
    characteristic: NumericalCharacteristic;
    value: number;
  }>;
};

/**
 * A count of group members who belong to a particular demographic.
 * Used when group membership is expressed via demographic categories.
 */
export type DemographicMembership = {
  demographic: Demographic;
  count: number;
};

/**
 * A count of group members whose known characteristic values satisfy a set of bands.
 *
 * Matching rule against CharacteristicBandMoralConcerns: for each band in the concern,
 * if this membership specifies that characteristic, the value/band must satisfy the concern's
 * band; if this membership does NOT specify that characteristic, the concern band is treated
 * as satisfied. CharacteristicBandMemberships are matched ONLY against
 * CharacteristicBandMoralConcerns, never against DemographicMoralConcerns.
 */
export type CharacteristicBandMembership = {
  characteristicBands: AnyCharacteristicValue[];
  count: number;
};

/**
 * A group is the set of people affected by an effect.
 * Membership can be expressed via demographic counts, characteristic-band counts,
 * explicit individuals, or any combination.
 *
 * Matching rules:
 *   - demographicMemberships  →  matched by DemographicMoralConcerns (by demographic name)
 *   - characteristicBandMemberships  →  matched by CharacteristicBandMoralConcerns only
 *   - individuals  →  matched by CharacteristicBandMoralConcerns (partial match) and
 *                     DemographicMoralConcerns (strict: all demographic constraints must
 *                     be covered by the individual's declared values)
 */
export type Group = {
  name: string;
  description?: string;
  demographicMemberships?: DemographicMembership[];
  characteristicBandMemberships?: CharacteristicBandMembership[];
  individuals?: IndividualMember[];
};

// ---------------------------------------------------------------------------
// Benefits
// ---------------------------------------------------------------------------

/**
 * One possible outcome in a benefit distribution.
 * Either qualitativeMagnitude or quantitativeMagnitude must be present.
 * If quantitativeMagnitude is present, quantitativeMetric should also be present
 * so that the ethic's conversion metrics can normalize it.
 */
export type PossibleBenefit = {
  /** Objective probability that this outcome occurs. */
  likelihood: number;
  qualitativeMagnitude?: QualitativeMagnitude;
  /** Raw numeric magnitude in the units of quantitativeMetric. */
  quantitativeMagnitude?: number;
  /** Name of the unit (e.g. "USD", "hours", "lives"). Must match a ConversionMetric.fromMetric. */
  quantitativeMetric?: string;
  signage: Signage;
  description?: string;
  /** Downstream effects triggered by this possible benefit. */
  chainEffects?: Effect[];
};

// ---------------------------------------------------------------------------
// Effects
// ---------------------------------------------------------------------------

/**
 * An effect describes the impact of a choice on a group along a facet of prosperity.
 * Chain effects are effects caused by this effect and must be computed recursively.
 */
export type Effect = {
  affectedGroup: Group;
  facetOfProsperity: string | ProsperityCharacteristic;
  /** e.g. "short-term" | "long-term" */
  outlook: string;
  possibleBenefits: PossibleBenefit[];
};

// ---------------------------------------------------------------------------
// Choices
// ---------------------------------------------------------------------------

export type Choice = {
  name: string;
  description?: string;
  /** Label for behavior-based proscription matching (see Ethic.proscribedBehaviors). */
  behavior?: string;
  effects: Effect[];
};

// ---------------------------------------------------------------------------
// Moral concerns
// ---------------------------------------------------------------------------

/**
 * A demographic-based moral concern: care about a specific named demographic
 * along a facet of prosperity for a given outlook. In future, outlook can be
 * specified more robustly.
 */
export type DemographicMoralConcern = {
  kind: "demographic";
  demographic: Demographic;
  facetOfProsperity: string | ProsperityCharacteristic;
  outlook: string;
};

/**
 * A characteristic-band moral concern: care about individuals satisfying ALL
 * of the specified characteristic constraints, along a facet of prosperity.
 * Used when the moral concern does not map cleanly to a predefined demographic.
 * In future, outlook can be specified more robustly.
 */
export type CharacteristicBandMoralConcern = {
  kind: "characteristicBand";
  characteristicBands: AnyCharacteristicValue[];
  facetOfProsperity: string | ProsperityCharacteristic;
  outlook: string;
};

export type MoralConcern =
  | DemographicMoralConcern
  | CharacteristicBandMoralConcern;

// ---------------------------------------------------------------------------
// Moral priorities
// ---------------------------------------------------------------------------

/**
 * A moral priority associates a moral concern with a weight of importance.
 * importance can be expressed qualitatively (QualitativeMagnitude) or quantitatively.
 * Calculation functions use the quantitative form; qualitative is converted via ordinal/7.
 */
export type MoralPriority = {
  moralConcern: MoralConcern;
  minStatus?: QualitativeMagnitude;
  loweringBelowMinStatusIsCategoricallyProhibited?: boolean;
  maxStatus?: QualitativeMagnitude;
  raisingAboveMaxStatusIsCategoricallyProhibited?: boolean;
  rank?: number;
  quantitativeImportance?: number;
  qualitativeImportance?: QualitativeMagnitude;
  //qualitativeDifferenceImportanceFromNextLowestPriority cannot be defined if either qualitativeImportance
  // or quantitativeImportance are defined; you're either making an absolute comparison or a relative comparison, not both
  qualitativeDifferenceInImportanceFromNextLowestPriority?: QualitativeDifferenceMagnitude;
  // detrimentInviolabilityThreshold?: QualitativeMagnitude;
  overridingDuties?: OverridingDuty[];
};

//violating these considerations is categorically proscribed unless all choices available
//are categorically proscribed, in which case need to compute morality of all choices and
//determine least bad option
export type OverridingDuty = {
  beneficiaryMoralConcern: MoralConcern;
  obligatoryDetrimentThreshold: QualitativeMagnitude; //between this as inviolability threshold is supererogatory
  // supererogatoryDetrimentThreshold: QualitativeMagnitude;
  supererogatoryBecomesObligatoryAtBeneficiaryCount?: number;
  detrimentInviolabilityThreshold?: QualitativeMagnitude; //beyond this threshold is "too nice", being prohibited
  inviolabilityBecomesSupererogatoryAtBeneficiaryCount?: number; //must be less than or equal to supererogatory beneficiary count
};

// enum OverridingObligationTiebreakApproach {

// }

// ---------------------------------------------------------------------------
// Conversion metrics
// ---------------------------------------------------------------------------

/**
 * Converts quantities expressed in fromMetric into the ethic's primary benefit metric.
 * scope, if present, restricts the conversion to members of a particular demographic
 * (e.g. $1M is "extremely beneficial" for the average person but not for a billionaire).
 */
export type ConversionMetric = {
  fromMetric: string;
  /** Quantity of fromMetric equivalent to "extremely beneficial" (ordinal 7). */
  extremelyBeneficialThreshold: number;
  scope?: Demographic;
};

// ---------------------------------------------------------------------------
// Ethic
// ---------------------------------------------------------------------------

export type Ethic = {
  name: string;
  moralPriorities: MoralPriority[];
  /** CPT probability-weighting curvature. γ = 1 yields linear weighting (default). */
  gamma?: number;
  /** CPT value-function parameters. α governs diminishing sensitivity to gains,
   *  β governs diminishing sensitivity to losses, λ governs loss aversion.
   *  Defaults: α = β = λ = 1 (no distortion). */
  alpha?: number;
  beta?: number;
  lambda?: number;
  /** Ambiguity parameter. Collapses probability ranges [pLow, pHigh] via
   *  pEff = a · pLow + (1−a) · pHigh. 0 = optimistic, 0.5 = indifference, 1 = maximin. */
  ambiguityAversion?: number;
  conversionMetrics?: ConversionMetric[];
  proscribedBehaviors?: string[];
};

export type Outcome = {};

// ---------------------------------------------------------------------------
// Dilemma
// ---------------------------------------------------------------------------

export type Dilemma = {
  name: string;
  description?: string;
  choices: Choice[];
};

// ---------------------------------------------------------------------------
// Results
// ---------------------------------------------------------------------------

export type MoralValenceResult = {
  choiceName: string;
  moralValence: number;
};

export type PreferabilityResult = {
  choiceName: string;
  calculatedPreferability: QualitativePreferability;
  isPrescribed: boolean;
};

export type DivergenceResult = {
  choiceName: string;
  statedOrdinal: number;
  calculatedOrdinal: number;
  /** Positive = overstated; negative = understated relative to computed preferability. */
  signedDivergence: number;
  absoluteDivergence: number;
};

export type DivergenceSignal = {
  perChoice: DivergenceResult[];
  meanAbsoluteDivergence: number;
};

// ---------------------------------------------------------------------------
// SEJP evaluation input
// ---------------------------------------------------------------------------

/**
 * The input bundle for a SEJP divergence computation.
 * Combines a dilemma, an ethic, and a set of stated preferabilities so that
 * recomputed moral valences can be compared against stated ones to produce a DivergenceSignal.
 */
export type SEJPOutput = {
  dilemma: Dilemma;
  ethic: Ethic;
  statedPreferabilities: Array<{
    choiceName: string;
    statedPreferability: QualitativePreferability;
  }>;
};

// ---------------------------------------------------------------------------
// Moral priority inference results
// ---------------------------------------------------------------------------

/**
 * Per-concern result comparing a purported (stated) importance against the importance
 * inferred from the preferabilities assigned to choices in a moral dilemma.
 * Positive signedDivergence = purported importance overstated relative to what
 * the stated preferabilities imply.
 */
export type MoralPriorityDivergenceResult = {
  moralConcern: MoralConcern;
  /** Importance drawn from the purported ethic, normalized to [0, 1]. 0 if concern has no matching purported priority. */
  purportedImportance: number;
  /** Importance inferred from stated preferabilities, normalized to [0, 1]. */
  inferredImportance: number;
  /** purportedImportance − inferredImportance */
  signedDivergence: number;
  absoluteDivergence: number;
};

export type MoralPriorityDivergenceSignal = {
  perConcern: MoralPriorityDivergenceResult[];
  meanAbsoluteDivergence: number;
};

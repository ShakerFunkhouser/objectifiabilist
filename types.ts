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
 * 7-value qualitative scale for benefit magnitude, likelihood, and moral priority importance.
 * Ordinal values (1–7) map to quantitative fractions: ordinal / 7.
 */
export enum QualitativeMagnitude {
  Negligible = 1,
  VeryLow = 2,
  SomewhatLow = 3,
  Moderate = 4,
  SomewhatHigh = 5,
  VeryHigh = 6,
  ExtremelyHigh = 7,
}

/**
 * 7-value qualitative scale for the preferability of a choice.
 * Mapped from moral valences via min-max normalization onto 7 equal buckets.
 */
export enum QualitativePreferability {
  ExtremelyUnpreferable = 1,
  VeryUnpreferable = 2,
  SomewhatUnpreferable = 3,
  Neutral = 4,
  SomewhatPreferable = 5,
  VeryPreferable = 6,
  ExtremelyPreferable = 7,
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

export type AnyCharacteristic =
  | BooleanCharacteristic
  | StringCharacteristic
  | NumericalCharacteristic;

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
  facetOfProsperity: string;
  /** e.g. "short-term" | "long-term" */
  outlook: string;
  possibleBenefits: PossibleBenefit[];
  chainEffects?: Effect[];
};

// ---------------------------------------------------------------------------
// Choices
// ---------------------------------------------------------------------------

export type Choice = {
  name: string;
  description?: string;
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
  facetOfProsperity: string;
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
  facetOfProsperity: string;
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
  importance: QualitativeMagnitude | number;
};

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
  /**
   * 0 = pure expected value (likelihoods fully weighted).
   * 1 = pure optimism (only best outcome considered).
   * Values between 0 and 1 interpolate monotonically.
   */
  optimismBias: number;
  conversionMetrics?: ConversionMetric[];
};

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

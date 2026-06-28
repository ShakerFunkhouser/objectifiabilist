/**
 * objectifiabilist/types.ts
 *
 * Canonical TypeScript schema for Objectifiabilism.
 * This file is the single source of truth for all types.
 * The Pydantic models in models.py are derived from and must be kept in sync with this file.
 *
 * @see Academic Paper.md for full theoretical treatment
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

/** Qualitative difference between adjacent moral priorities or preferabilities (Table 3). */
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
 * Mapped from moral valences via absolute preferability (P^abs) onto 7 equal buckets.
 * Ordinal values (0–6) map to equal-width intervals in [0, 1] per Table 4.
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

export interface BooleanCharacteristic {
  kind: "boolean";
  name: string;
  description?: string;
  defaultValue?: boolean;
}

export interface StringCharacteristic {
  kind: "string";
  name: string;
  description?: string;
  possibleValues: string[];
  defaultValue?: string;
}

export interface NumericalCharacteristic {
  kind: "numerical";
  name: string;
  description?: string;
  unit?: string;
  minValue?: number;
  maxValue?: number;
  defaultValue?: number;
}

/** A dimension of well-being (e.g. health, wealth, autonomy). */
export interface ProsperityCharacteristic {
  kind: "prosperity";
  name: string;
  description?: string;
}

export type AnyCharacteristic =
  | BooleanCharacteristic
  | StringCharacteristic
  | NumericalCharacteristic
  | ProsperityCharacteristic;

// ---------------------------------------------------------------------------
// Characteristic values (used to describe individuals and demographics)
// ---------------------------------------------------------------------------

export interface BooleanCharacteristicValue {
  characteristic: BooleanCharacteristic;
  value: boolean;
}

export interface StringCharacteristicValue {
  characteristic: StringCharacteristic;
  value: string;
}

/** An inclusive band [minValue, maxValue] for a numerical characteristic. */
export interface NumericalCharacteristicValueBand {
  characteristic: NumericalCharacteristic;
  minValue?: number;
  maxValue?: number;
}

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
export interface Demographic {
  name: string;
  description?: string;
  booleanValues?: BooleanCharacteristicValue[];
  stringValues?: StringCharacteristicValue[];
  numericalBands?: NumericalCharacteristicValueBand[];
}

// ---------------------------------------------------------------------------
// Groups
// ---------------------------------------------------------------------------

/** A single numeric value for a characteristic (for individual members). */
export interface NumericalCharacteristicPoint {
  characteristic: NumericalCharacteristic;
  value: number;
}

/**
 * An individual member of a group, described by their characteristic values.
 * Used when the group composition is heterogeneous or a specific person is at stake.
 */
export interface IndividualMember {
  booleanValues?: BooleanCharacteristicValue[];
  stringValues?: StringCharacteristicValue[];
  numericalValues?: NumericalCharacteristicPoint[];
}

/** A count of group members who belong to a particular demographic. */
export interface DemographicMembership {
  demographic: Demographic;
  count: number;
}

/**
 * A count of group members whose known characteristic values satisfy a set of bands.
 *
 * Matching rule against CharacteristicBandMoralConcerns: for each band in the concern,
 * if this membership specifies that characteristic, the value/band must satisfy the concern's
 * band; if this membership does NOT specify that characteristic, the concern band is treated
 * as satisfied. CharacteristicBandMemberships are matched ONLY against
 * CharacteristicBandMoralConcerns, never against DemographicMoralConcerns.
 */
export interface CharacteristicBandMembership {
  characteristicBands: AnyCharacteristicValue[];
  count: number;
}

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
export interface Group {
  name: string;
  description?: string;
  demographicMemberships?: DemographicMembership[];
  characteristicBandMemberships?: CharacteristicBandMembership[];
  individuals?: IndividualMember[];
  /**
   * Circumstantial importance adjustment applied additively to any moral priority
   * that matches this group. Positive = increased moral standing (e.g., relatedness).
   * Negative = decreased (e.g., fault). Per §2.1, circumstantial characteristics
   * like "relatedness to agent" and "fault for the conflict arising" modify group
   * importance as additive offsets.
   */
  circumstantialAdjustment?: number;
}

// ---------------------------------------------------------------------------
// Benefits
// ---------------------------------------------------------------------------

/**
 * One possible outcome in a benefit distribution.
 * Either qualitativeMagnitude or quantitativeMagnitude must be present.
 * If quantitativeMagnitude is present, quantitativeMetric should also be present
 * so that the ethic's conversion metrics can normalize it.
 */
export interface PossibleBenefit {
  /** Probability that this outcome occurs (0–1). */
  likelihood: number;
  /** Lower bound of a probability range (§2.4). When both likelihoodLow and likelihoodHigh
   *  are present, the ethic's ambiguityAversion collapses them via
   *  p_eff = a · p_low + (1−a) · p_high before CPT probability weighting. */
  likelihoodLow?: number;
  /** Upper bound of a probability range (§2.4). See likelihoodLow. */
  likelihoodHigh?: number;
  qualitativeMagnitude?: QualitativeMagnitude;
  /** Raw numeric magnitude in the units of quantitativeMetric. */
  quantitativeMagnitude?: number;
  /** Name of the unit (e.g. "USD", "hours", "lives"). Must match a ConversionMetric.fromMetric. */
  quantitativeMetric?: string;
  signage: Signage;
  description?: string;
  /**
   * Existing state of benefit for the affected concern before this benefit is applied.
   * Used in ideal-state calculations per §3.5.1: b_res = b_incoming + b_existing.
   * Defaults to 0 if not specified.
   */
  bExisting?: number;
  /**
   * Downstream effects triggered when this possible benefit occurs.
   * Weighted by this PB's likelihood in moral value calculations.
   * Per §3.5.2: c = Σ L_chain × A_chain.
   */
  chainEffects?: Effect[];
}

// ---------------------------------------------------------------------------
// Effects (recursive via chainEffects)
// ---------------------------------------------------------------------------

/**
 * An effect describes the impact of a choice on a group along a facet of prosperity.
 * Chain effects are effects caused by this effect and must be computed recursively.
 */
export interface Effect {
  affectedGroup: Group;
  facetOfProsperity: string | ProsperityCharacteristic;
  /** e.g. "short-term" | "long-term" */
  outlook: string;
  possibleBenefits: PossibleBenefit[];
  /**
   * Probability that this effect transpires.
   * Defaults to 1.0 (certain). The moral value of the effect is multiplied by
   * this likelihood when computing the moral valence of the parent choice (§2.1).
   */
  likelihood?: number;
}

// ---------------------------------------------------------------------------
// Choices
// ---------------------------------------------------------------------------

export interface Choice {
  name: string;
  description?: string;
  /** Label for behavior-based proscription matching (see Ethic.proscribedBehaviors). */
  behavior?: string;
  effects: Effect[];
}

// ---------------------------------------------------------------------------
// Moral concerns
// ---------------------------------------------------------------------------

/**
 * A demographic-based moral concern: care about a specific named demographic
 * along a facet of prosperity for a given outlook.
 */
export interface DemographicMoralConcern {
  kind: "demographic";
  demographic: Demographic;
  facetOfProsperity: string | ProsperityCharacteristic;
  outlook: string;
}

/**
 * A characteristic-band moral concern: care about individuals satisfying ALL
 * of the specified characteristic constraints, along a facet of prosperity.
 * Used when the moral concern does not map cleanly to a predefined demographic.
 */
export interface CharacteristicBandMoralConcern {
  kind: "characteristicBand";
  characteristicBands: AnyCharacteristicValue[];
  facetOfProsperity: string | ProsperityCharacteristic;
  outlook: string;
}

export type MoralConcern =
  | DemographicMoralConcern
  | CharacteristicBandMoralConcern;

// ---------------------------------------------------------------------------
// Moral priorities
// ---------------------------------------------------------------------------

/**
 * A moral priority associates a moral concern with a weight of importance.
 * importance can be expressed qualitatively (QualitativeMagnitude) or as a
 * normalized float in [0, 1]. Calculation functions convert qualitative
 * ordinals via ordinal / 6.
 */
export interface MoralPriority {
  moralConcern: MoralConcern;
  /** Importance as QualitativeMagnitude ordinal (0–6) or normalized float in [0, 1]. */
  importance: QualitativeMagnitude | number;
  rank?: number;
  /** Minimum qualitative status of benefit for this concern (§3.5.1). */
  minStatus?: QualitativeMagnitude;
  /** Maximum qualitative status of benefit for this concern (§3.5.1). */
  maxStatus?: QualitativeMagnitude;
  overridingDuties?: OverridingDuty[];
  /** Lower bound on inferred importance under simplified inverse (§3.10): m_d − W. */
  importanceLowerBound?: number;
  /** Upper bound on inferred importance under simplified inverse (§3.10): m_d + W. */
  importanceUpperBound?: number;
}

/**
 * A deontological constraint (§3.7). When a choice benefits the
 * beneficiaryMoralConcern while imposing detriment on the moral concern
 * that owns this duty beyond the inviolability threshold, the choice
 * is prohibited.
 */
export interface OverridingDuty {
  beneficiaryMoralConcern: MoralConcern;
  /** Detriment threshold at which the duty activates (evaluative activation). */
  obligatoryDetrimentThreshold: QualitativeMagnitude;
  /** Beneficiary count at which detriment transitions from
   *  supererogatory to obligatory. Default 1. */
  supererogatoryBecomesObligatoryAtBeneficiaryCount?: number;
  /** Detriment beyond which benefit to the beneficiary is prohibited.
   *  Defaults to obligatoryDetrimentThreshold if not set. */
  detrimentInviolabilityThreshold?: QualitativeMagnitude;
  /** Beneficiary count at which the inviolability threshold relaxes,
   *  making the detriment supererogatory instead of prohibited.
   *  Must be ≤ supererogatoryBecomesObligatoryAtBeneficiaryCount. */
  inviolabilityBecomesSupererogatoryAtBeneficiaryCount?: number;
}

// ---------------------------------------------------------------------------
// Conversion metrics
// ---------------------------------------------------------------------------

/**
 * Converts quantities expressed in fromMetric into the ethic's primary benefit metric.
 * scope, if present, restricts the conversion to members of a particular demographic
 * (e.g. $1M is "extremely beneficial" for the average person but not for a billionaire).
 */
export interface ConversionMetric {
  fromMetric: string;
  /** Quantity of fromMetric equivalent to "extremely beneficial" (ordinal 6). */
  extremelyBeneficialThreshold: number;
  scope?: Demographic;
}

// ---------------------------------------------------------------------------
// Ethic
// ---------------------------------------------------------------------------

export interface Ethic {
  name: string;
  moralPriorities: MoralPriority[];
  /** CPT value function gain exponent. Default 1 = linear. */
  alpha?: number;
  /** CPT value function loss exponent. Default 1 = linear. */
  beta?: number;
  /** CPT loss-aversion coefficient. Default 1 = no aversion. */
  lambda?: number;
  /** CPT probability-weighting curvature. Default 1 = identity. */
  gamma?: number;
  /** Ambiguity parameter a ∈ [0, 1]. Collapses probability ranges [pLow, pHigh] via
   *  pEff = a · pLow + (1−a) · pHigh. 0 = optimistic, 0.5 = indifference, 1 = maximin.
   *  Default 0.5. */
  ambiguityAversion?: number;
  conversionMetrics?: ConversionMetric[];
  /** Behaviors that render a choice categorically inadmissible (§3.7). */
  proscribedBehaviors?: string[];
  /**
   * Deontic prohibition threshold (§2.3). Choices with absolute preferability
   * below this ordinal are prohibited. Must be ≤ deonticSupererogationThreshold.
   */
  deonticProhibitionThreshold?: QualitativePreferability;
  /**
   * Deontic supererogation threshold (§2.3). Choices with absolute preferability
   * above this ordinal are supererogatory. Choices between the two thresholds
   * are obligatory.
   */
  deonticSupererogationThreshold?: QualitativePreferability;
}

// ---------------------------------------------------------------------------
// Dilemma
// ---------------------------------------------------------------------------

export interface Dilemma {
  name: string;
  description?: string;
  choices: Choice[];
}

// ---------------------------------------------------------------------------
// Results
// ---------------------------------------------------------------------------

export interface MoralValenceResult {
  choiceName: string;
  moralValence: number;
}

/** Deontic status of a choice per §2.3 and §3.7. */
export type DeonticStatus = "prohibited" | "obligatory" | "supererogatory";

export interface PreferabilityResult {
  choiceName: string;
  calculatedPreferability: QualitativePreferability;
  /** Quantitative absolute preferability P^abs in [0, 1] (§3.8). */
  absolutePreferability: number;
  /** Quantitative normalized relative preferability P_i in [0, 1] (§3.8). */
  normalizedRelativePreferability: number;
  /** Deontic status per §2.3 thresholds (prohibited/obligatory/supererogatory). */
  deonticStatus: DeonticStatus;
  isPrescribed: boolean;
}

export interface DivergenceResult {
  choiceName: string;
  statedOrdinal: number;
  calculatedOrdinal: number;
  /** Positive = overstated; negative = understated relative to computed preferability. */
  signedDivergence: number;
  absoluteDivergence: number;
  /** |signedDivergence| / k where k = 7 ordinals (§3.9). */
  normalizedDivergence: number;
}

export type DivergenceBand = "negligible" | "moderate" | "substantial";

export interface DivergenceSignal {
  perChoice: DivergenceResult[];
  /** Mean raw ordinal gap |O_purported − O_predicted| (legacy scale 0–6). */
  meanAbsoluteDivergence: number;
  /** Total prescriptive divergence D = Σ Δ_i (§3.9). */
  totalPrescriptiveDivergence: number;
  /** Mean prescriptive divergence Δ̄ = D / n (§3.9). */
  meanPrescriptiveDivergence: number;
  /** Heuristic interpretive band for Δ̄ (§3.9). */
  prescriptiveDivergenceBand: DivergenceBand;
}

// ---------------------------------------------------------------------------
// SEJP evaluation input
// ---------------------------------------------------------------------------

export interface StatedPreferability {
  choiceName: string;
  statedPreferability: QualitativePreferability;
}

/**
 * The input bundle for a SEJP divergence computation.
 * Combines a dilemma, an ethic, and a set of stated preferabilities so that
 * recomputed moral valences can be compared against stated ones to produce a DivergenceSignal.
 */
export interface SEJPOutput {
  dilemma: Dilemma;
  ethic: Ethic;
  statedPreferabilities: StatedPreferability[];
}

// ---------------------------------------------------------------------------
// Moral priority inference results
// ---------------------------------------------------------------------------

/**
 * Per-concern result comparing a purported (stated) importance against the importance
 * inferred from the preferabilities assigned to choices in a moral dilemma.
 * Positive signedDivergence = purported importance overstated relative to what
 * the stated preferabilities imply.
 */
export interface MoralPriorityDivergenceResult {
  moralConcern: MoralConcern;
  /** Importance drawn from the purported ethic, normalized to [0, 1]. 0 if concern has no matching purported priority. */
  purportedImportance: number;
  /** Importance inferred from stated preferabilities, normalized to [0, 1]. */
  inferredImportance: number;
  /** purportedImportance − inferredImportance */
  signedDivergence: number;
  absoluteDivergence: number;
}

export interface MoralPriorityDivergenceSignal {
  perConcern: MoralPriorityDivergenceResult[];
  /** Mean |δ_k| on normalized importances (alias for meanNormativeDivergence). */
  meanAbsoluteDivergence: number;
  /** Total normative divergence N = Σ|δ_k| (§3.11). */
  totalNormativeDivergence: number;
  /** Mean normative divergence N̄ = N / d (§3.11). */
  meanNormativeDivergence: number;
  /** Heuristic interpretive band for N̄ (§3.11). */
  normativeDivergenceBand: DivergenceBand;
}

// ---------------------------------------------------------------------------
// Polytope inference results
// ---------------------------------------------------------------------------

/** Upper and lower bounds for a single moral concern's implied importance. */
export interface PerConcernBounds {
  moralConcern: MoralConcern;
  minImportance: number;
  maxImportance: number;
  centroid: number; // (min + max) / 2
}

/**
 * Result of the polytope approach to moral priority inference (§3.10).
 *
 * The polytope approach treats each stated preferability ordinal as a quantitative
 * interval constraint (Table 4) and solves two linear programs per concern:
 *   minimize / maximize  m_k
 *   subject to           A·m ∈ [V_i^min, V_i^max]
 *
 * **TypeScript**: Use `inferMoralPrioritiesPolytopeAsync` (requires `highs-js`,
 * an optional ~3 MB WebAssembly dependency). For a dependency-free alternative,
 * use the simplified surrogate `inferMoralPriorities` (Vmax=1, Vmin=0 proxy).
 *
 * **Python**: Use `infer_moral_priorities_polytope` (requires `scipy`).
 */
export interface PolytopeInferenceResult {
  perConcern: PerConcernBounds[];
  /** Whether any feasible solution exists for the stated constraints. */
  feasible: boolean;
  /** Mean of centroid values across all concerns (normalized). */
  meanCentroidImportance: number;
}

// ---------------------------------------------------------------------------
// Constants (§3.8 / Table 4)
// ---------------------------------------------------------------------------

/** Number of preferability ordinals (0–6). */
export const PREFERABILITY_ORDINAL_COUNT = 7;

/** Width of a single preferability bucket: 1/7 ≈ 0.143 (§3.8). */
export const PREFERABILITY_BUCKET_WIDTH = 1 / 7;

/** Upper quantitative bound of the below-neutral region in Table 4 (0.43). */
export const W_UNPREF = 0.43;

/** Return (P_min, P_max) absolute-preferability interval for ordinal 0–6 (Table 4). */
export function getPreferabilityBounds(
  ordinal: QualitativePreferability | number,
): [number, number] {
  const buckets: Record<number, [number, number]> = {
    0: [0.0, 0.15],
    1: [0.15, 0.29],
    2: [0.29, 0.43],
    3: [0.43, 0.57],
    4: [0.57, 0.71],
    5: [0.71, 0.85],
    6: [0.85, 1.0],
  };
  return buckets[ordinal as number] ?? [0.0, 1.0];
}

/** Heuristic interpretive bands for mean prescriptive/normative divergence (§3.9, §3.11). */
export function classifyDivergenceBand(meanDivergence: number): DivergenceBand {
  if (meanDivergence < 0.05) return "negligible";
  if (meanDivergence < 0.2) return "moderate";
  return "substantial";
}

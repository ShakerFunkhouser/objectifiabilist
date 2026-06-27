// TypeScript types for Objectifiabilist, ported from Python models.py

export type Signage = "positive" | "negative" | "zero";

export enum QualitativeMagnitude {
  Negligible = 0,
  VeryLow = 1,
  SomewhatLow = 2,
  Moderate = 3,
  SomewhatHigh = 4,
  VeryHigh = 5,
  ExtremelyHigh = 6,
}

export enum QualitativePreferability {
  ExtremelyUnpreferable = 0,
  VeryUnpreferable = 1,
  SomewhatUnpreferable = 2,
  Neutral = 3,
  SomewhatPreferable = 4,
  VeryPreferable = 5,
  ExtremelyPreferable = 6,
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

export interface BooleanCharacteristicValue {
  characteristic: BooleanCharacteristic;
  value: boolean;
}

export interface StringCharacteristicValue {
  characteristic: StringCharacteristic;
  value: string;
}

export interface NumericalCharacteristicValueBand {
  characteristic: NumericalCharacteristic;
  minValue?: number;
  maxValue?: number;
}

export interface Demographic {
  name: string;
  description?: string;
  booleanValues?: BooleanCharacteristicValue[];
  stringValues?: StringCharacteristicValue[];
  numericalBands?: NumericalCharacteristicValueBand[];
}

export interface NumericalCharacteristicPoint {
  characteristic: NumericalCharacteristic;
  value: number;
}

export interface IndividualMember {
  booleanValues?: BooleanCharacteristicValue[];
  stringValues?: StringCharacteristicValue[];
  numericalValues?: NumericalCharacteristicPoint[];
}

export interface DemographicMembership {
  demographic: Demographic;
  count: number;
}

export interface CharacteristicBandMembership {
  characteristicBands: (
    | BooleanCharacteristicValue
    | StringCharacteristicValue
    | NumericalCharacteristicValueBand
  )[];
  count: number;
}

export interface Group {
  name: string;
  description?: string;
  demographicMemberships?: DemographicMembership[];
  characteristicBandMemberships?: CharacteristicBandMembership[];
  individuals?: IndividualMember[];
  circumstantialAdjustment?: number;
}

export interface PossibleBenefit {
  likelihood: number;
  qualitativeMagnitude?: QualitativeMagnitude;
  quantitativeMagnitude?: number;
  quantitativeMetric?: string;
  signage: Signage;
  description?: string;
  chainEffects?: Effect[];
}

export interface Effect {
  affectedGroup: Group;
  facetOfProsperity: string | ProsperityCharacteristic;
  outlook: string;
  possibleBenefits: PossibleBenefit[];
  /** Probability that this effect transpires. Defaults to 1.0 (certain). */
  likelihood?: number;
}

export interface Choice {
  name: string;
  description?: string;
  /** Label for behavior-based proscription matching (see Ethic.proscribedBehaviors). */
  behavior?: string;
  effects: Effect[];
}

export interface DemographicMoralConcern {
  kind: "demographic";
  demographic: Demographic;
  facetOfProsperity: string | ProsperityCharacteristic;
  outlook: string;
}

export interface CharacteristicBandMoralConcern {
  kind: "characteristicBand";
  characteristicBands: (
    | BooleanCharacteristicValue
    | StringCharacteristicValue
    | NumericalCharacteristicValueBand
  )[];
  facetOfProsperity: string | ProsperityCharacteristic;
  outlook: string;
}

export type MoralConcern =
  | DemographicMoralConcern
  | CharacteristicBandMoralConcern;

export interface MoralPriority {
  moralConcern: MoralConcern;
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
 * A deontological constraint (§3.7).  When a choice benefits the
 * beneficiaryMoralConcern while imposing detriment on the moral concern
 * that owns this duty beyond the inviolability threshold, the choice
 * is prohibited.
 */
export interface OverridingDuty {
  beneficiaryMoralConcern: MoralConcern;
  /** Detriment threshold at which the duty activates (evaluative activation). */
  obligatoryDetrimentThreshold: QualitativeMagnitude;
  /** Beneficiary count at which the detriment transitions from
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

export interface ConversionMetric {
  fromMetric: string;
  extremelyBeneficialThreshold: number;
  scope?: Demographic;
}

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
  /** Ambiguity parameter a ∈ [0,1]. Default 0.5. */
  ambiguityAversion?: number;
  conversionMetrics?: ConversionMetric[];
  /** Behaviors that render a choice categorically inadmissible (§3.7). */
  proscribedBehaviors?: string[];
}

export interface Dilemma {
  name: string;
  description?: string;
  choices: Choice[];
}

export interface MoralValenceResult {
  choiceName: string;
  moralValence: number;
}

export interface PreferabilityResult {
  choiceName: string;
  calculatedPreferability: QualitativePreferability;
  isPrescribed: boolean;
}

export interface DivergenceResult {
  choiceName: string;
  statedOrdinal: number;
  calculatedOrdinal: number;
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

export interface StatedPreferability {
  choiceName: string;
  statedPreferability: QualitativePreferability;
}

export interface SEJPOutput {
  dilemma: Dilemma;
  ethic: Ethic;
  statedPreferabilities: StatedPreferability[];
}

// ---------------------------------------------------------------------------
// Moral priority inference results
// ---------------------------------------------------------------------------

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

// §3.8 / Table 4 constants (academic paper).
export const PREFERABILITY_ORDINAL_COUNT = 7;
export const PREFERABILITY_BUCKET_WIDTH = 1 / 7;
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
export function classifyDivergenceBand(
  meanDivergence: number,
): DivergenceBand {
  if (meanDivergence < 0.05) return "negligible";
  if (meanDivergence < 0.2) return "moderate";
  return "substantial";
}

// TypeScript types for Objectifiabilist, ported from Python models.py

export type Signage = "positive" | "negative" | "zero";

export enum QualitativeMagnitude {
  Negligible = 1,
  VeryLow,
  SomewhatLow,
  Moderate,
  SomewhatHigh,
  VeryHigh,
  ExtremelyHigh,
}

export enum QualitativePreferability {
  ExtremelyUnpreferable = 1,
  VeryUnpreferable,
  SomewhatUnpreferable,
  Neutral,
  SomewhatPreferable,
  VeryPreferable,
  ExtremelyPreferable,
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

export type AnyCharacteristic =
  | BooleanCharacteristic
  | StringCharacteristic
  | NumericalCharacteristic;

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
}

export interface PossibleBenefit {
  likelihood: number;
  qualitativeMagnitude?: QualitativeMagnitude;
  quantitativeMagnitude?: number;
  quantitativeMetric?: string;
  signage: Signage;
  description?: string;
}

export interface Effect {
  affectedGroup: Group;
  facetOfProsperity: string;
  outlook: string;
  possibleBenefits: PossibleBenefit[];
  chainEffects?: Effect[];
}

export interface Choice {
  name: string;
  description?: string;
  effects: Effect[];
}

export interface DemographicMoralConcern {
  kind: "demographic";
  demographic: Demographic;
  facetOfProsperity: string;
  outlook: string;
}

export interface CharacteristicBandMoralConcern {
  kind: "characteristicBand";
  characteristicBands: (
    | BooleanCharacteristicValue
    | StringCharacteristicValue
    | NumericalCharacteristicValueBand
  )[];
  facetOfProsperity: string;
  outlook: string;
}

export type MoralConcern =
  | DemographicMoralConcern
  | CharacteristicBandMoralConcern;

export interface MoralPriority {
  moralConcern: MoralConcern;
  importance: QualitativeMagnitude | number;
}

export interface ConversionMetric {
  fromMetric: string;
  extremelyBeneficialThreshold: number;
  scope?: Demographic;
}

export interface Ethic {
  name: string;
  moralPriorities: MoralPriority[];
  optimismBias: number;
  conversionMetrics?: ConversionMetric[];
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
}

export interface DivergenceSignal {
  perChoice: DivergenceResult[];
  meanAbsoluteDivergence: number;
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
  meanAbsoluteDivergence: number;
}

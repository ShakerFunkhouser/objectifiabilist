// Calculation functions for Objectifiabilist (TypeScript)
// Ported from Python functions.py
import {
  PossibleBenefit,
  QualitativeMagnitude,
  QualitativePreferability,
  Group,
  MoralPriority,
  DemographicMoralConcern,
  CharacteristicBandMoralConcern,
  IndividualMember,
  Demographic,
  BooleanCharacteristicValue,
  StringCharacteristicValue,
  NumericalCharacteristicValueBand,
  Effect,
  Ethic,
  Choice,
  Dilemma,
  DivergenceResult,
} from "./types";

// Step 1: Resolve benefit magnitude to a normalized float in [0, 1]
function resolveMagnitude(benefit: PossibleBenefit): number {
  if (
    benefit.quantitativeMagnitude !== undefined &&
    benefit.quantitativeMagnitude !== null
  ) {
    return Math.abs(benefit.quantitativeMagnitude);
  }
  if (
    benefit.qualitativeMagnitude !== undefined &&
    benefit.qualitativeMagnitude !== null
  ) {
    return benefit.qualitativeMagnitude / 7.0;
  }
  return 0.0;
}

function signedMagnitude(benefit: PossibleBenefit): number {
  const mag = resolveMagnitude(benefit);
  if (benefit.signage === "negative") return -mag;
  if (benefit.signage === "zero") return 0.0;
  return mag;
}

// Step 2: Weighted net-benefit of an effect's distribution
export function calculateWeightedNetBenefit(
  benefits: PossibleBenefit[],
  optimismBias: number = 0.0,
): number {
  if (!benefits || benefits.length === 0) return 0.0;
  if (optimismBias === 0.0) {
    return benefits.reduce(
      (sum, b) => sum + b.likelihood * signedMagnitude(b),
      0,
    );
  }
  const signedMags = benefits.map(signedMagnitude);
  const bestIdx = signedMags.reduce(
    (best, val, idx, arr) => (val > arr[best] ? idx : best),
    0,
  );
  let total = 0.0;
  for (let i = 0; i < benefits.length; i++) {
    const bestWeight = i === bestIdx ? 1.0 : 0.0;
    const adjusted =
      (1 - optimismBias) * benefits[i].likelihood + optimismBias * bestWeight;
    total += adjusted * signedMags[i];
  }
  return total;
}

// Helper: check if a member's characteristic bands satisfy a concern band
function charbandSatisfiesConcernBand(
  memberBands: (
    | BooleanCharacteristicValue
    | StringCharacteristicValue
    | NumericalCharacteristicValueBand
  )[],
  concernBand:
    | BooleanCharacteristicValue
    | StringCharacteristicValue
    | NumericalCharacteristicValueBand,
): boolean {
  const cname = concernBand.characteristic.name;
  if ("minValue" in concernBand) {
    // NumericalCharacteristicValueBand
    for (const mb of memberBands) {
      if ("minValue" in mb && mb.characteristic.name === cname) {
        if (concernBand.minValue !== undefined) {
          if (mb.minValue === undefined || mb.minValue < concernBand.minValue)
            return false;
        }
        if (concernBand.maxValue !== undefined) {
          if (mb.maxValue === undefined || mb.maxValue > concernBand.maxValue)
            return false;
        }
        return true;
      }
    }
    return true;
  } else if ("value" in concernBand && typeof concernBand.value === "string") {
    // StringCharacteristicValue
    for (const mb of memberBands) {
      if (
        "value" in mb &&
        typeof mb.value === "string" &&
        mb.characteristic.name === cname
      ) {
        return mb.value === concernBand.value;
      }
    }
    return true;
  } else {
    // BooleanCharacteristicValue
    for (const mb of memberBands) {
      if (
        "value" in mb &&
        typeof mb.value === "boolean" &&
        mb.characteristic.name === cname &&
        "value" in concernBand &&
        typeof concernBand.value === "boolean"
      ) {
        return mb.value === concernBand.value;
      }
    }
    return true;
  }
}

function cbmSatisfiesConcern(
  cbm: import("./types").CharacteristicBandMembership,
  concern: import("./types").CharacteristicBandMoralConcern,
): boolean {
  return concern.characteristicBands.every((cb) =>
    charbandSatisfiesConcernBand(cbm.characteristicBands, cb),
  );
}

function individualSatisfiesConcern(
  member: IndividualMember,
  concern: CharacteristicBandMoralConcern,
): boolean {
  const memberBands: (
    | BooleanCharacteristicValue
    | StringCharacteristicValue
    | NumericalCharacteristicValueBand
  )[] = [];
  if (member.booleanValues) memberBands.push(...member.booleanValues);
  if (member.stringValues) memberBands.push(...member.stringValues);
  if (member.numericalValues) {
    for (const nv of member.numericalValues) {
      memberBands.push({
        characteristic: nv.characteristic,
        minValue: nv.value,
        maxValue: nv.value,
      });
    }
  }
  return concern.characteristicBands.every((cb) =>
    charbandSatisfiesConcernBand(memberBands, cb),
  );
}

function individualSatisfiesDemographic(
  member: IndividualMember,
  concern: DemographicMoralConcern,
): boolean {
  const demo = concern.demographic;
  const memberBool: Record<string, boolean> = {};
  const memberStr: Record<string, string> = {};
  const memberNum: Record<string, number> = {};
  if (member.booleanValues)
    for (const bv of member.booleanValues)
      memberBool[bv.characteristic.name] = bv.value;
  if (member.stringValues)
    for (const sv of member.stringValues)
      memberStr[sv.characteristic.name] = sv.value;
  if (member.numericalValues)
    for (const nv of member.numericalValues)
      memberNum[nv.characteristic.name] = nv.value;
  if (demo.booleanValues)
    for (const bv of demo.booleanValues) {
      if (!(bv.characteristic.name in memberBool)) return false;
      if (memberBool[bv.characteristic.name] !== bv.value) return false;
    }
  if (demo.stringValues)
    for (const sv of demo.stringValues) {
      if (!(sv.characteristic.name in memberStr)) return false;
      if (memberStr[sv.characteristic.name] !== sv.value) return false;
    }
  if (demo.numericalBands)
    for (const band of demo.numericalBands) {
      const cn = band.characteristic.name;
      if (!(cn in memberNum)) return false;
      const val = memberNum[cn];
      if (band.minValue !== undefined && val < band.minValue) return false;
      if (band.maxValue !== undefined && val > band.maxValue) return false;
    }
  return true;
}

function importanceWeight(priority: MoralPriority): number {
  const imp = priority.importance;
  if (typeof imp === "number" && Number.isInteger(imp)) {
    return imp / 7.0;
  }
  const f = Number(imp);
  if (f > 1.0) return f / 7.0;
  return f;
}

export function calculateImportance(
  group: Group,
  priority: MoralPriority,
): number {
  const iw = importanceWeight(priority);
  const concern = priority.moralConcern;
  let total = 0.0;
  if (concern.kind === "demographic") {
    if (group.demographicMemberships)
      for (const dm of group.demographicMemberships) {
        if (dm.demographic.name === concern.demographic.name)
          total += iw * dm.count;
      }
    if (group.individuals)
      for (const member of group.individuals) {
        if (individualSatisfiesDemographic(member, concern)) total += iw;
      }
  } else if (concern.kind === "characteristicBand") {
    if (group.characteristicBandMemberships)
      for (const cbm of group.characteristicBandMemberships) {
        if (cbmSatisfiesConcern(cbm, concern)) total += iw * cbm.count;
      }
    if (group.individuals)
      for (const member of group.individuals) {
        if (individualSatisfiesConcern(member, concern)) total += iw;
      }
  }
  return total;
}

export function calculateMoralValueOfEffect(
  effect: Effect,
  ethic: Ethic,
): number {
  const wnb = calculateWeightedNetBenefit(
    effect.possibleBenefits,
    ethic.optimismBias,
  );
  let totalImportance = 0.0;
  for (const priority of ethic.moralPriorities) {
    const concern = priority.moralConcern;
    if (
      concern.facetOfProsperity === effect.facetOfProsperity &&
      concern.outlook === effect.outlook
    ) {
      totalImportance += calculateImportance(effect.affectedGroup, priority);
    }
  }
  const rootMoralValue = wnb * totalImportance;
  const chainValue = effect.chainEffects
    ? effect.chainEffects.reduce(
        (sum, chain) => sum + calculateMoralValueOfEffect(chain, ethic),
        0,
      )
    : 0;
  return rootMoralValue + chainValue;
}

export function calculateMoralValence(choice: Choice, ethic: Ethic): number {
  return choice.effects.reduce(
    (sum, e) => sum + calculateMoralValueOfEffect(e, ethic),
    0,
  );
}

export function calculateAllMoralValences(
  dilemma: Dilemma,
  ethic: Ethic,
): Record<string, number> {
  const result: Record<string, number> = {};
  for (const choice of dilemma.choices) {
    result[choice.name] = calculateMoralValence(choice, ethic);
  }
  return result;
}

export function calculatePreferabilities(
  moralValences: Record<string, number>,
): Record<string, QualitativePreferability> {
  const keys = Object.keys(moralValences);
  if (keys.length === 0) return {};
  const vals = Object.values(moralValences);
  const minVal = Math.min(...vals);
  const maxVal = Math.max(...vals);
  const spread = maxVal - minVal;
  const result: Record<string, QualitativePreferability> = {};
  for (const name of keys) {
    const val = moralValences[name];
    let bucket: number;
    if (spread === 0) {
      bucket = 4;
    } else {
      const normalized = (val - minVal) / spread;
      bucket = Math.min(7, Math.max(1, Math.ceil(normalized * 7)));
      if (bucket === 0) bucket = 1;
    }
    result[name] = bucket as QualitativePreferability;
  }
  return result;
}

export function calculateDivergenceSignal(
  stated: {
    choiceName: string;
    statedPreferability: QualitativePreferability;
  }[],
  computed: Record<string, QualitativePreferability>,
): { perChoice: DivergenceResult[]; meanAbsoluteDivergence: number } {
  const statedMap: Record<string, number> = {};
  for (const s of stated) statedMap[s.choiceName] = s.statedPreferability;
  const perChoice = [];
  for (const choiceName in computed) {
    const calcPref = computed[choiceName];
    const statedOrd = statedMap[choiceName] ?? calcPref;
    const calcOrd = calcPref;
    const signed = statedOrd - calcOrd;
    perChoice.push({
      choiceName,
      statedOrdinal: statedOrd,
      calculatedOrdinal: calcOrd,
      signedDivergence: signed,
      absoluteDivergence: Math.abs(signed),
    });
  }
  const meanAbs =
    perChoice.length > 0
      ? perChoice.reduce((sum, r) => sum + r.absoluteDivergence, 0) /
        perChoice.length
      : 0.0;
  return { perChoice, meanAbsoluteDivergence: meanAbs };
}

export function evaluateSejpOutput(output: {
  dilemma: Dilemma;
  ethic: Ethic;
  statedPreferabilities: {
    choiceName: string;
    statedPreferability: QualitativePreferability;
  }[];
}) {
  const valences = calculateAllMoralValences(output.dilemma, output.ethic);
  const computed = calculatePreferabilities(valences);
  return calculateDivergenceSignal(output.statedPreferabilities, computed);
}

export function getPrescribedChoice(
  dilemma: Dilemma,
  ordainedEthic: Ethic,
): string {
  const valences = calculateAllMoralValences(dilemma, ordainedEthic);
  return Object.keys(valences).reduce(
    (best, name) => (valences[name] > valences[best] ? name : best),
    Object.keys(valences)[0],
  );
}

export function getNamesOfChoicesSortedByDecreasingMoralValence(
  dilemma: Dilemma,
  ordainedEthic: Ethic,
): string[] {
  const valences = calculateAllMoralValences(dilemma, ordainedEthic);
  return Object.keys(valences).sort((a, b) => valences[b] - valences[a]);
}

export function isActionPermitted(
  choiceName: string,
  dilemma: Dilemma,
  ordainedEthic: Ethic,
): boolean {
  return choiceName === getPrescribedChoice(dilemma, ordainedEthic);
}

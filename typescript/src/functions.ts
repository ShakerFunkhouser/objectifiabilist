// Calculation functions for Objectifiabilist (TypeScript)
// Ported from Python functions.py
import {
  PossibleBenefit,
  ProsperityCharacteristic,
  QualitativeMagnitude,
  QualitativePreferability,
  Group,
  MoralPriority,
  MoralConcern,
  DemographicMoralConcern,
  CharacteristicBandMoralConcern,
  IndividualMember,
  BooleanCharacteristicValue,
  StringCharacteristicValue,
  NumericalCharacteristicValueBand,
  Effect,
  Ethic,
  Choice,
  Dilemma,
  DivergenceResult,
  DivergenceSignal,
  StatedPreferability,
  MoralPriorityDivergenceResult,
  MoralPriorityDivergenceSignal,
  classifyDivergenceBand,
  PREFERABILITY_ORDINAL_COUNT,
  PREFERABILITY_BUCKET_WIDTH,
  W_UNPREF,
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
    return benefit.qualitativeMagnitude / 6.0;
  }
  return 0.0;
}

/** Extract the plain name from a facet, whether string or ProsperityCharacteristic. */
function facetName(facet: string | ProsperityCharacteristic): string {
  return typeof facet === "string" ? facet : facet.name;
}

function signedMagnitude(benefit: PossibleBenefit): number {
  const mag = resolveMagnitude(benefit);
  if (benefit.signage === "negative") return -mag;
  if (benefit.signage === "zero") return 0.0;
  return mag;
}

/**
 * Compute raw benefit considering ideal state (minStatus/maxStatus) per §3.5.1.
 *
 * Range mode (both min and max specified, both non-zero):
 *   b_res = b_incoming  (b_existing = 0 for now)
 *   If b_min ≤ b_res ≤ b_max:   raw = 1  (100% progress toward ideal)
 *   If b_res < b_min:           raw = 1 − (b_min − b_res) / b_min
 *   If b_res > b_max:           raw = 1 − (b_res − b_max) / b_max
 *
 * Reference mode (only one specified, non-zero):
 *   b_ref = the specified bound; raw = 1 − |b_ref − b_res| / b_ref
 *
 * No ideal state: returns b_incoming unchanged.
 */
function idealRawBenefit(bIncoming: number, priority: MoralPriority): number {
  const bMinVal = priority.minStatus;
  const bMaxVal = priority.maxStatus;

  if (bMinVal === undefined && bMaxVal === undefined) return bIncoming;

  const bMin = bMinVal !== undefined ? bMinVal / 6.0 : undefined;
  const bMax = bMaxVal !== undefined ? bMaxVal / 6.0 : undefined;
  const bRes = bIncoming;

  if (bMin !== undefined && bMax !== undefined && bMin > 0 && bMax > 0) {
    // Range mode
    if (bRes >= bMin && bRes <= bMax) return 1.0;
    if (bRes < bMin) return 1.0 - (bMin - bRes) / bMin;
    return 1.0 - (bRes - bMax) / bMax;
  }
  // Reference mode
  const bRef = bMin !== undefined ? bMin : bMax;
  if (bRef !== undefined && bRef > 0) {
    return 1.0 - Math.abs(bRef - bRes) / bRef;
  }
  return bIncoming;
}

// CPT helper functions
function cptW(p: number, gamma: number): number {
  if (gamma === 1.0) return p;
  if (p <= 0) return 0;
  if (p >= 1) return 1;
  const pg = Math.pow(p, gamma);
  return pg / Math.pow(pg + Math.pow(1 - p, gamma), 1 / gamma);
}

function cptV(b: number, alpha: number, beta: number, lambda: number): number {
  if (b >= 0) return Math.pow(b, alpha);
  return -(lambda * Math.pow(-b, beta));
}

// Step 2: Weighted net-benefit of an effect's distribution
export function calculateWeightedNetBenefit(
  benefits: PossibleBenefit[],
  alpha: number = 1.0,
  beta: number = 1.0,
  lambda: number = 1.0,
  gamma: number = 1.0,
  priority?: MoralPriority,
): number {
  if (!benefits || benefits.length === 0) return 0.0;
  const rawFn = priority
    ? (b: PossibleBenefit) => idealRawBenefit(signedMagnitude(b), priority)
    : signedMagnitude;
  return benefits.reduce(
    (sum, b) =>
      sum + cptW(b.likelihood, gamma) * cptV(rawFn(b), alpha, beta, lambda),
    0,
  );
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
  const f = Number(priority.importance);
  // Integer ordinals 0-6 from JSON deserialization: detect and normalise
  if (Number.isInteger(f) && f >= 0 && f <= 6) return f / 6.0;
  if (f > 1.0) return f / 6.0;
  return f;
}

export function calculateImportance(
  group: Group,
  priority: MoralPriority,
): number {
  const iw = importanceWeight(priority);
  const concern = priority.moralConcern;
  let total = 0.0;
  let matched = false;
  if (concern.kind === "demographic") {
    if (group.demographicMemberships)
      for (const dm of group.demographicMemberships) {
        if (dm.demographic.name === concern.demographic.name) {
          total += iw * dm.count;
          matched = true;
        }
      }
    if (group.individuals)
      for (const member of group.individuals) {
        if (individualSatisfiesDemographic(member, concern)) {
          total += iw;
          matched = true;
        }
      }
  } else if (concern.kind === "characteristicBand") {
    if (group.characteristicBandMemberships)
      for (const cbm of group.characteristicBandMemberships) {
        if (cbmSatisfiesConcern(cbm, concern)) {
          total += iw * cbm.count;
          matched = true;
        }
      }
    if (group.individuals)
      for (const member of group.individuals) {
        if (individualSatisfiesConcern(member, concern)) {
          total += iw;
          matched = true;
        }
      }
  }
  if (matched) total += group.circumstantialAdjustment ?? 0;
  return total;
}

export function calculateMoralValueOfEffect(
  effect: Effect,
  ethic: Ethic,
): number {
  const alpha = ethic.alpha ?? 1.0;
  const beta = ethic.beta ?? 1.0;
  const lambda = ethic.lambda ?? 1.0;
  const gamma = ethic.gamma ?? 1.0;

  // Root moral value: sum over matching priorities of M_k × WNB_k
  let rootMoralValue = 0;
  for (const priority of ethic.moralPriorities) {
    const concern = priority.moralConcern;
    if (
      facetName(concern.facetOfProsperity) ===
        facetName(effect.facetOfProsperity) &&
      concern.outlook === effect.outlook
    ) {
      const Mk = calculateImportance(effect.affectedGroup, priority);
      const wnbK = calculateWeightedNetBenefit(
        effect.possibleBenefits,
        alpha,
        beta,
        lambda,
        gamma,
        priority,
      );
      rootMoralValue += Mk * wnbK;
    }
  }

  // Chain value: C = Σ_j w(l_j) × c_j  where c_j = Σ_k A_chain_k
  let chainValue = 0;
  for (const pb of effect.possibleBenefits) {
    if (pb.chainEffects && pb.chainEffects.length > 0) {
      const wlj = cptW(pb.likelihood, gamma);
      const cj = pb.chainEffects.reduce(
        (sum, chain) => sum + calculateMoralValueOfEffect(chain, ethic),
        0,
      );
      chainValue += wlj * cj;
    }
  }

  const effectLikelihood = effect.likelihood ?? 1.0;
  return effectLikelihood * (rootMoralValue + chainValue);
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

export function calculateAbsolutePreferabilityQuantitative(
  val: number,
  minVal: number,
  maxVal: number,
): number {
  if (maxVal > 0) {
    if (val >= 0) return val / maxVal;
    if (minVal < 0) return (val / minVal) * W_UNPREF;
    return 0;
  }
  if (maxVal > minVal) {
    return ((val - minVal) / (maxVal - minVal)) * W_UNPREF;
  }
  return 0;
}

function quantitativeToPreferabilityOrdinal(pAbs: number): number {
  const p = Math.max(0, Math.min(1, pAbs));
  if (p >= 0.85) return 6;
  if (p >= 0.71) return 5;
  if (p >= 0.57) return 4;
  if (p >= 0.43) return 3;
  if (p >= 0.29) return 2;
  if (p >= 0.15) return 1;
  return 0;
}

export function calculatePreferabilities(
  moralValences: Record<string, number>,
): Record<string, QualitativePreferability> {
  const keys = Object.keys(moralValences);
  if (keys.length === 0) return {};
  const vals = Object.values(moralValences);
  const minVal = Math.min(...vals);
  const maxVal = Math.max(...vals);
  const result: Record<string, QualitativePreferability> = {};
  for (const name of keys) {
    const val = moralValences[name];
    const pAbs = calculateAbsolutePreferabilityQuantitative(val, minVal, maxVal);
    result[name] = quantitativeToPreferabilityOrdinal(pAbs) as QualitativePreferability;
  }
  return result;
}

export function calculateDivergenceSignal(
  stated: {
    choiceName: string;
    statedPreferability: QualitativePreferability;
  }[],
  computed: Record<string, QualitativePreferability>,
): DivergenceSignal {
  const statedMap: Record<string, number> = {};
  for (const s of stated) statedMap[s.choiceName] = s.statedPreferability;
  const perChoice: DivergenceResult[] = [];
  const k = PREFERABILITY_ORDINAL_COUNT;
  for (const choiceName in computed) {
    const calcPref = computed[choiceName];
    const statedOrd = statedMap[choiceName] ?? calcPref;
    const calcOrd = calcPref;
    const signed = statedOrd - calcOrd;
    const absDiv = Math.abs(signed);
    perChoice.push({
      choiceName,
      statedOrdinal: statedOrd,
      calculatedOrdinal: calcOrd,
      signedDivergence: signed,
      absoluteDivergence: absDiv,
      normalizedDivergence: absDiv / k,
    });
  }
  const n = perChoice.length;
  const meanAbs =
    n > 0
      ? perChoice.reduce((sum, r) => sum + r.absoluteDivergence, 0) / n
      : 0.0;
  const totalPrescriptive = perChoice.reduce(
    (sum, r) => sum + r.normalizedDivergence,
    0,
  );
  const meanPrescriptive = n > 0 ? totalPrescriptive / n : 0.0;
  return {
    perChoice,
    meanAbsoluteDivergence: meanAbs,
    totalPrescriptiveDivergence: totalPrescriptive,
    meanPrescriptiveDivergence: meanPrescriptive,
    prescriptiveDivergenceBand: classifyDivergenceBand(meanPrescriptive),
  };
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

export function isActionPermitted(choice: Choice, ethic: Ethic): boolean {
  // Check overriding duties (§3.7)
  for (const priority of ethic.moralPriorities) {
    for (const duty of priority.overridingDuties ?? []) {
      const obligatedConcern = priority.moralConcern;
      const beneficiaryConcern = duty.beneficiaryMoralConcern;

      // Check if any effect benefits the beneficiary concern
      let beneficiaryCount = 0;
      let benefitsBeneficiary = false;
      for (const effect of choice.effects) {
        if (effectMatchesConcern(effect, beneficiaryConcern)) {
          const wnb = calculateWeightedNetBenefit(
            effect.possibleBenefits,
            ethic.alpha ?? 1,
            ethic.beta ?? 1,
            ethic.lambda ?? 1,
            ethic.gamma ?? 1,
          );
          if (wnb > 0) {
            benefitsBeneficiary = true;
            const unitPriority: MoralPriority = {
              moralConcern: beneficiaryConcern,
              importance: QualitativeMagnitude.ExtremelyHigh,
            };
            beneficiaryCount += Math.floor(
              calculateImportance(effect.affectedGroup, unitPriority),
            );
          }
        }
      }
      if (!benefitsBeneficiary) continue;

      // Check if any effect harms the obligated concern
      for (const effect of choice.effects) {
        if (effectMatchesConcern(effect, obligatedConcern)) {
          const wnb = calculateWeightedNetBenefit(
            effect.possibleBenefits,
            ethic.alpha ?? 1,
            ethic.beta ?? 1,
            ethic.lambda ?? 1,
            ethic.gamma ?? 1,
          );
          if (wnb < 0) {
            const bDetriment = Math.abs(wnb);
            const eps =
              duty.inviolabilityBecomesSupererogatoryAtBeneficiaryCount ?? 1;
            const omega =
              duty.supererogatoryBecomesObligatoryAtBeneficiaryCount ?? 1;
            const bEff =
              bDetriment / Math.max(beneficiaryCount, 1) / eps / omega;
            const inviolability =
              duty.detrimentInviolabilityThreshold ??
              duty.obligatoryDetrimentThreshold;
            if (bEff > inviolability / 6.0) return false;
          }
        }
      }
    }
  }
  return true;
}

function effectMatchesConcern(effect: Effect, concern: MoralConcern): boolean {
  return (
    facetName(concern.facetOfProsperity) ===
      facetName(effect.facetOfProsperity) && concern.outlook === effect.outlook
  );
}

// ---------------------------------------------------------------------------
// Moral priority inference
// ---------------------------------------------------------------------------

/** Stable string key uniquely identifying a MoralConcern. */
function concernKey(concern: MoralConcern): string {
  const fname = facetName(concern.facetOfProsperity);
  if (concern.kind === "demographic") {
    return `demographic|${fname}|${concern.outlook}|${concern.demographic.name}`;
  }
  const bands = concern.characteristicBands
    .map((b) => {
      if ("value" in b && typeof b.value === "boolean")
        return `bool:${b.characteristic.name}=${b.value}`;
      if ("value" in b && typeof b.value === "string")
        return `str:${b.characteristic.name}=${b.value}`;
      const nb = b as NumericalCharacteristicValueBand;
      return `num:${nb.characteristic.name}:[${nb.minValue ?? ""}..${nb.maxValue ?? ""}]`;
    })
    .sort()
    .join(";");
  return `characteristicBand|${fname}|${concern.outlook}|${bands}`;
}

/**
 * Recursively traverses all effects (including chainEffects) in a dilemma and
 * extracts unique MoralConcerns, one per distinct group-membership type ×
 * facet × outlook combination.
 *
 * - demographicMemberships  → DemographicMoralConcern (keyed by demographic name)
 * - characteristicBandMemberships → CharacteristicBandMoralConcern
 * - individuals → CharacteristicBandMoralConcern built from their declared values
 *   (numericalValues become exact [v, v] bands)
 */
export function extractMoralConcernsFromDilemma(
  dilemma: Dilemma,
): MoralConcern[] {
  const seen = new Map<string, MoralConcern>();

  function visitEffect(effect: Effect): void {
    const { affectedGroup, facetOfProsperity, outlook } = effect;

    for (const dm of affectedGroup.demographicMemberships ?? []) {
      const concern: DemographicMoralConcern = {
        kind: "demographic",
        demographic: dm.demographic,
        facetOfProsperity,
        outlook,
      };
      const key = concernKey(concern);
      if (!seen.has(key)) seen.set(key, concern);
    }

    for (const cbm of affectedGroup.characteristicBandMemberships ?? []) {
      const concern: CharacteristicBandMoralConcern = {
        kind: "characteristicBand",
        characteristicBands: cbm.characteristicBands,
        facetOfProsperity,
        outlook,
      };
      const key = concernKey(concern);
      if (!seen.has(key)) seen.set(key, concern);
    }

    for (const individual of affectedGroup.individuals ?? []) {
      const bands: (
        | BooleanCharacteristicValue
        | StringCharacteristicValue
        | NumericalCharacteristicValueBand
      )[] = [];
      for (const bv of individual.booleanValues ?? []) bands.push(bv);
      for (const sv of individual.stringValues ?? []) bands.push(sv);
      for (const nv of individual.numericalValues ?? []) {
        bands.push({
          characteristic: nv.characteristic,
          minValue: nv.value,
          maxValue: nv.value,
        });
      }
      if (bands.length === 0) continue;
      const concern: CharacteristicBandMoralConcern = {
        kind: "characteristicBand",
        characteristicBands: bands,
        facetOfProsperity,
        outlook,
      };
      const key = concernKey(concern);
      if (!seen.has(key)) seen.set(key, concern);
    }

    for (const pb of effect.possibleBenefits ?? []) {
      for (const chain of pb.chainEffects ?? []) visitEffect(chain);
    }
  }

  for (const choice of dilemma.choices) {
    for (const effect of choice.effects) visitEffect(effect);
  }

  return Array.from(seen.values());
}

/**
 * Builds the contribution matrix A where A[i][k] is the total weighted net-benefit
 * that concern k (at unit importance = 1) contributes to choice i's moral valence.
 * Reuses calculateWeightedNetBenefit and calculateImportance.
 */
function buildContributionMatrix(
  dilemma: Dilemma,
  concerns: MoralConcern[],
  alpha: number,
  beta: number,
  lambda: number,
  gamma: number,
): number[][] {
  const n = dilemma.choices.length;
  const m = concerns.length;
  const A: number[][] = Array.from({ length: n }, () => new Array(m).fill(0));

  function contributionOfEffect(
    effect: Effect,
    choiceIdx: number,
    pathWeight: number = 1.0,
  ): void {
    const weight = pathWeight * (effect.likelihood ?? 1.0);
    for (let k = 0; k < m; k++) {
      const concern = concerns[k];
      if (
        facetName(concern.facetOfProsperity) ===
          facetName(effect.facetOfProsperity) &&
        concern.outlook === effect.outlook
      ) {
        const wnb = calculateWeightedNetBenefit(
          effect.possibleBenefits,
          alpha,
          beta,
          lambda,
          gamma,
        );
        const unitPriority: MoralPriority = {
          moralConcern: concern,
          importance: 1.0,
        };
        const imp = calculateImportance(effect.affectedGroup, unitPriority);
        A[choiceIdx][k] += weight * wnb * imp;
      }
    }
    // Traverse chain effects on possible benefits
    for (const pb of effect.possibleBenefits) {
      for (const chain of pb.chainEffects ?? []) {
        contributionOfEffect(
          chain,
          choiceIdx,
          weight * cptW(pb.likelihood, gamma),
        );
      }
    }
  }

  for (let i = 0; i < n; i++) {
    for (const effect of dilemma.choices[i].effects) {
      contributionOfEffect(effect, i);
    }
  }

  return A;
}

/** Partial-pivot Gaussian elimination. Solves C·x = d in-place; returns x or null if singular. */
function gaussianElimination(C: number[][], d: number[]): number[] | null {
  const m = d.length;
  // Augmented matrix [C | d]
  const aug: number[][] = C.map((row, i) => [...row, d[i]]);

  for (let col = 0; col < m; col++) {
    // Find pivot
    let pivotRow = col;
    let pivotVal = Math.abs(aug[col][col]);
    for (let row = col + 1; row < m; row++) {
      if (Math.abs(aug[row][col]) > pivotVal) {
        pivotVal = Math.abs(aug[row][col]);
        pivotRow = row;
      }
    }
    if (pivotVal < 1e-12) return null; // singular column
    // Swap
    [aug[col], aug[pivotRow]] = [aug[pivotRow], aug[col]];
    // Eliminate
    const scale = aug[col][col];
    for (let j = col; j <= m; j++) aug[col][j] /= scale;
    for (let row = 0; row < m; row++) {
      if (row === col) continue;
      const factor = aug[row][col];
      for (let j = col; j <= m; j++) aug[row][j] -= factor * aug[col][j];
    }
  }

  return aug.map((row) => row[m]);
}

/**
 * Infers moral priorities (as importance weights in [0, 1]) from the preferabilities
 * assigned to choices in a moral dilemma.
 *
 * Algorithm:
 * 1. Auto-extract candidate MoralConcerns from the dilemma's effects.
 * 2. Build contribution matrix A (n_choices × n_concerns), where A[i][k] is the
 *    contribution of concern k at unit importance to the moral valence of choice i.
 * 3. Solve for the importance vector x (clamped to [0, 1]):
 *    - Over-determined (m ≤ n): least-squares via normal equations (A^T A)·x = A^T·b.
 *      Zero-diagonal columns (zero-contribution concerns) are assigned importance 0.
 *    - Under-determined (m > n): minimum-norm solution via (A A^T)·y = b, x = A^T·y.
 *      This gives the shortest importance vector consistent with the stated preferabilities.
 *
 * Returns one MoralPriority per extracted concern with inferred importance.
 */
export function inferMoralPriorities(
  dilemma: Dilemma,
  statedPreferabilities: StatedPreferability[],
  alpha: number = 1.0,
  beta: number = 1.0,
  lambda: number = 1.0,
  gamma: number = 1.0,
): MoralPriority[] {
  const concerns = extractMoralConcernsFromDilemma(dilemma);
  const m = concerns.length;
  if (m === 0) return [];

  const statedMap: Record<string, number> = {};
  for (const s of statedPreferabilities)
    statedMap[s.choiceName] = s.statedPreferability;

  const n = dilemma.choices.length;
  // b[i] = stated ordinal / 6 (P^abs proxy; default: 3 = Neutral)
  const b: number[] = dilemma.choices.map(
    (c) => (statedMap[c.name] ?? 3) / 6.0,
  );

  const A = buildContributionMatrix(
    dilemma,
    concerns,
    alpha,
    beta,
    lambda,
    gamma,
  );

  // Check if A is all zeros
  const allZero = A.every((row) => row.every((v) => v === 0));
  if (allZero) {
    return concerns.map((concern) => ({
      moralConcern: concern,
      importance: 0,
      importanceLowerBound: 0,
      importanceUpperBound: PREFERABILITY_BUCKET_WIDTH,
    }));
  }

  const importances = new Array<number>(m).fill(0);

  if (m <= n) {
    // Over-determined: least-squares via normal equations (A^T A) x = A^T b
    const AtA: number[][] = Array.from({ length: m }, () =>
      new Array(m).fill(0),
    );
    const Atb: number[] = new Array(m).fill(0);
    for (let k = 0; k < m; k++) {
      for (let j = 0; j < m; j++) {
        for (let i = 0; i < n; i++) AtA[k][j] += A[i][k] * A[i][j];
      }
      for (let i = 0; i < n; i++) Atb[k] += A[i][k] * b[i];
    }

    // Handle columns that are entirely zero (concern has no traction in this dilemma)
    const zeroColumns = new Set<number>();
    for (let k = 0; k < m; k++) {
      if (AtA[k][k] < 1e-24) zeroColumns.add(k);
    }
    const activeIdxs = Array.from({ length: m }, (_, i) => i).filter(
      (i) => !zeroColumns.has(i),
    );
    if (activeIdxs.length > 0) {
      const AtA_r = activeIdxs.map((ri) => activeIdxs.map((ci) => AtA[ri][ci]));
      const Atb_r = activeIdxs.map((ri) => Atb[ri]);
      const solved = gaussianElimination(AtA_r, Atb_r);
      if (solved) {
        for (let ii = 0; ii < activeIdxs.length; ii++) {
          importances[activeIdxs[ii]] = Math.min(1, Math.max(0, solved[ii]));
        }
      }
    }
  } else {
    // Under-determined: minimum-norm solution via (A A^T)·y = b, then x = A^T·y
    const AAt: number[][] = Array.from({ length: n }, () =>
      new Array(n).fill(0),
    );
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        for (let k = 0; k < m; k++) AAt[i][j] += A[i][k] * A[j][k];
      }
    }
    const solvedY = gaussianElimination(AAt, [...b]);
    if (solvedY) {
      for (let k = 0; k < m; k++) {
        let val = 0;
        for (let i = 0; i < n; i++) val += A[i][k] * solvedY[i];
        importances[k] = Math.min(1, Math.max(0, val));
      }
    }
  }

  return concerns.map((concern, k) => {
    const imp = importances[k];
    return {
      moralConcern: concern,
      importance: imp,
      importanceLowerBound: Math.max(0, imp - PREFERABILITY_BUCKET_WIDTH),
      importanceUpperBound: Math.min(1, imp + PREFERABILITY_BUCKET_WIDTH),
    };
  });
}

/**
 * Compares purported moral priorities (from an explicit ethic) against moral priorities
 * inferred from stated preferabilities, producing a per-concern divergence signal.
 *
 * Matching rules:
 * - DemographicMoralConcern: matched by demographic.name + facet + outlook
 * - CharacteristicBandMoralConcern: matched by facet + outlook + sorted band keys
 *
 * If an inferred concern has no matching purported priority, purportedImportance = 0.
 */
export function calculateMoralPriorityDivergenceSignal(
  purportedPriorities: MoralPriority[],
  inferredPriorities: MoralPriority[],
): MoralPriorityDivergenceSignal {
  // Build lookup from concern key → normalized purported importance
  const purportedMap = new Map<string, number>();
  for (const pp of purportedPriorities) {
    const imp = pp.importance;
    const f = Number(imp);
    const normalized =
      Number.isInteger(f) && f >= 0 && f <= 6 ? f / 6.0 : f > 1.0 ? f / 6.0 : f;
    purportedMap.set(concernKey(pp.moralConcern), normalized);
  }

  const perConcern: MoralPriorityDivergenceResult[] = [];
  for (const ip of inferredPriorities) {
    const key = concernKey(ip.moralConcern);
    const purported = purportedMap.get(key) ?? 0;
    const inferred = ip.importance;
    const signed = purported - inferred;
    perConcern.push({
      moralConcern: ip.moralConcern,
      purportedImportance: purported,
      inferredImportance: inferred,
      signedDivergence: signed,
      absoluteDivergence: Math.abs(signed),
    });
  }

  const mean =
    perConcern.length > 0
      ? perConcern.reduce((s, r) => s + r.absoluteDivergence, 0) /
        perConcern.length
      : 0;
  const total = perConcern.reduce((s, r) => s + r.absoluteDivergence, 0);

  return {
    perConcern,
    meanAbsoluteDivergence: mean,
    totalNormativeDivergence: total,
    meanNormativeDivergence: mean,
    normativeDivergenceBand: classifyDivergenceBand(mean),
  };
}

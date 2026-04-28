// Calculation functions for Objectifiabilist (TypeScript)
// Ported from Python functions.py
import {
  PossibleBenefit,
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
  StatedPreferability,
  MoralPriorityDivergenceResult,
  MoralPriorityDivergenceSignal,
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
  const f = Number(priority.importance);
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

// ---------------------------------------------------------------------------
// Moral priority inference
// ---------------------------------------------------------------------------

/** Stable string key uniquely identifying a MoralConcern. */
function concernKey(concern: MoralConcern): string {
  if (concern.kind === "demographic") {
    return `demographic|${concern.facetOfProsperity}|${concern.outlook}|${concern.demographic.name}`;
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
  return `characteristicBand|${concern.facetOfProsperity}|${concern.outlook}|${bands}`;
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

    for (const chain of effect.chainEffects ?? []) visitEffect(chain);
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
  optimismBias: number,
): number[][] {
  const n = dilemma.choices.length;
  const m = concerns.length;
  const A: number[][] = Array.from({ length: n }, () => new Array(m).fill(0));

  function contributionOfEffect(effect: Effect, choiceIdx: number): void {
    for (let k = 0; k < m; k++) {
      const concern = concerns[k];
      if (
        concern.facetOfProsperity === effect.facetOfProsperity &&
        concern.outlook === effect.outlook
      ) {
        const wnb = calculateWeightedNetBenefit(
          effect.possibleBenefits,
          optimismBias,
        );
        const unitPriority: MoralPriority = {
          moralConcern: concern,
          importance: 1.0,
        };
        const imp = calculateImportance(effect.affectedGroup, unitPriority);
        A[choiceIdx][k] += wnb * imp;
      }
    }
    for (const chain of effect.chainEffects ?? []) {
      contributionOfEffect(chain, choiceIdx);
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
  optimismBias: number = 0.0,
): MoralPriority[] {
  const concerns = extractMoralConcernsFromDilemma(dilemma);
  const m = concerns.length;
  if (m === 0) return [];

  const statedMap: Record<string, number> = {};
  for (const s of statedPreferabilities)
    statedMap[s.choiceName] = s.statedPreferability;

  const n = dilemma.choices.length;
  // b[i] = stated ordinal for choice i (default: 4 = Neutral)
  const b: number[] = dilemma.choices.map((c) => statedMap[c.name] ?? 4);

  const A = buildContributionMatrix(dilemma, concerns, optimismBias);

  // Check if A is all zeros
  const allZero = A.every((row) => row.every((v) => v === 0));
  if (allZero) {
    return concerns.map((concern) => ({
      moralConcern: concern,
      importance: 0,
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

  return concerns.map((concern, k) => ({
    moralConcern: concern,
    importance: importances[k],
  }));
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
    const normalized =
      typeof imp === "number" && imp > 1.0 ? imp / 7.0 : Number(imp);
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

  return { perConcern, meanAbsoluteDivergence: mean };
}

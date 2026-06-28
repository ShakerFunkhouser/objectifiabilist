/**
 * polytope.ts — LP-based moral priority inference via HiGHS WebAssembly solver.
 *
 * §3.10 of the academic paper: "Finding the polytope of all possible moral priority
 * vectors implied by the feasibility region of these purported preferabilities would
 * therefore be maximally rigorous."
 *
 * This module implements Interval Linear Programming: for each moral concern $k$,
 * two linear programs are solved:
 *
 *   minimize / maximize  m_k
 *   subject to           A·m ∈ [V_i^min, V_i^max]  for all choices i
 *                         0 ≤ m_k ≤ 1               for all concerns k
 *
 * where A is the contribution matrix built from the dilemma, and [V_i^min, V_i^max]
 * are the quantitative preferability intervals for each stated ordinal (Table 4).
 *
 * NOTE: highs-js is an optional dependency (~3 MB WebAssembly). If it's not installed,
 * calling inferMoralPrioritiesPolytopeAsync throws with a clear installation message.
 * The synchronous `inferMoralPriorities` (simplified surrogate) remains the zero-dep
 * default.
 */

import type {
  Dilemma,
  MoralConcern,
  MoralPriority,
  PerConcernBounds,
  PolytopeInferenceResult,
  StatedPreferability,
} from "./types";
import {
  buildContributionMatrix,
  extractMoralConcernsFromDilemma,
} from "./functions";
import { getPreferabilityBounds } from "./types";

// ---------------------------------------------------------------------------
// HiGHS dynamic import — fails gracefully if highs-js is not installed
// ---------------------------------------------------------------------------

async function getHighs(): Promise<import("highs-js").HighsModule> {
  try {
    // highs-js exports a default async factory
    const highs = await import("highs-js");
    return await highs.default();
  } catch {
    throw new Error(
      "The polytope inference requires the optional dependency `highs-js`.\n" +
        "Install it with: npm install highs-js\n" +
        "Or use the simplified surrogate: inferMoralPriorities(dilemma, statedPreferabilities)\n" +
        "which uses Vmax=1, Vmin=0 proxy bounds without LP (§3.10).",
    );
  }
}

// ---------------------------------------------------------------------------
// LP model builder
// ---------------------------------------------------------------------------

/**
 * Builds a HiGHS MPS-format model string for minimizing/maximizing m_k
 * subject to the interval constraints A·m ∈ [low_i, high_i] and 0 ≤ m_k ≤ 1.
 *
 * HiGHS-js accepts LP format. We construct it directly here for transparency.
 */
function buildLpModel(
  direction: "min" | "max",
  k: number,
  m: number,
  A: number[][],
  Vlo: number[],
  Vhi: number[],
): string {
  const lines: string[] = [];

  lines.push(direction === "max" ? "Maximize" : "Minimize");
  lines.push(`  obj: m${k}`); // objective: just m_k
  lines.push("Subject To");

  // For each choice i: Vlo[i] ≤ Σ_j A[i][j]·m_j ≤ Vhi[i]
  // Split into two constraints: Σ_j A[i][j]·m_j ≥ Vlo[i]  and  Σ_j A[i][j]·m_j ≤ Vhi[i]
  for (let i = 0; i < A.length; i++) {
    // Σ_j A[i][j]·m_j ≤ Vhi[i]
    let terms = "";
    for (let j = 0; j < m; j++) {
      if (Math.abs(A[i][j]) < 1e-15) continue;
      const sign = A[i][j] >= 0 ? "+" : "-";
      terms += ` ${sign} ${Math.abs(A[i][j]).toFixed(8)} m${j}`;
    }
    if (terms === "") terms = " + 0 m0"; // empty constraint → trivial
    lines.push(`  c${i}_hi: ${terms} <= ${Vhi[i].toFixed(6)}`);
    // Σ_j A[i][j]·m_j ≥ Vlo[i] → -Σ_j A[i][j]·m_j ≤ -Vlo[i]
    lines.push(
      `  c${i}_lo:${terms
        .replace(/\+/g, "\u0000")
        .replace(/-/g, "+")
        .replace(/\u0000/g, "-")} <= ${(-Vlo[i]).toFixed(6)}`,
    );
  }

  lines.push("Bounds");
  for (let j = 0; j < m; j++) {
    lines.push(`  0 <= m${j} <= 1`);
  }

  lines.push("End");
  return lines.join("\n");
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Polytope approach to moral priority inference (§3.10).
 *
 * Treats each stated preferability ordinal as a quantitative interval constraint
 * on the moral valence V_i. For each concern $k$, solves two linear programs:
 *
 *   minimize / maximize  m_k
 *   subject to           A·m ∈ [V_i^min, V_i^max]  for all choices i
 *                         0 ≤ m_k ≤ 1               for all concerns k
 *
 * Where [V_i^min, V_i^max] is the quantitative bucket for the stated ordinal
 * (e.g., ordinal 6 → [0.85, 1.0]).
 *
 * The centroid (m_min + m_max) / 2 serves as a point estimate.
 * When the system is under-determined the ranges may be wide;
 * when over-determined the polytope may be empty (feasible = false).
 *
 * @param dilemma - The moral dilemma to infer priorities from.
 * @param statedPreferabilities - The stated preferabilities (ordinals) for each choice.
 * @param alpha - CPT value function gain exponent (default 1.0 = linear).
 * @param beta - CPT value function loss exponent (default 1.0 = linear).
 * @param lambda - CPT loss-aversion coefficient (default 1.0 = no aversion).
 * @param gamma - CPT probability-weighting curvature (default 1.0 = identity).
 * @returns A PolytopeInferenceResult with per-concern bounds and feasibility status.
 *
 * @example
 * ```ts
 * const result = await inferMoralPrioritiesPolytopeAsync(dilemma, statedPrefs);
 * for (const c of result.perConcern) {
 *   console.log(`${c.moralConcern}: [${c.minImportance}, ${c.maxImportance}]`);
 * }
 * ```
 */
export async function inferMoralPrioritiesPolytopeAsync(
  dilemma: Dilemma,
  statedPreferabilities: StatedPreferability[],
  alpha: number = 1.0,
  beta: number = 1.0,
  lambda: number = 1.0,
  gamma: number = 1.0,
): Promise<PolytopeInferenceResult> {
  const concerns = extractMoralConcernsFromDilemma(dilemma);
  const m = concerns.length;
  if (m === 0) {
    return {
      perConcern: [],
      feasible: true,
      meanCentroidImportance: 0.0,
    };
  }

  // Build stated ordinal map
  const statedMap: Record<string, number> = {};
  for (const s of statedPreferabilities) {
    statedMap[s.choiceName] = s.statedPreferability as number;
  }

  // Build contribution matrix A (n × m)
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
    return {
      perConcern: concerns.map((c) => ({
        moralConcern: c,
        minImportance: 0.0,
        maxImportance: 0.0,
        centroid: 0.0,
      })),
      feasible: true,
      meanCentroidImportance: 0.0,
    };
  }

  // Build valence interval constraints from stated preferabilities
  const Vlo: number[] = [];
  const Vhi: number[] = [];
  for (const choice of dilemma.choices) {
    const ordinal = statedMap[choice.name] ?? 3; // default: Neutral
    const [pMin, pMax] = getPreferabilityBounds(ordinal);
    Vlo.push(pMin);
    Vhi.push(pMax);
  }

  // Load HiGHS
  const highs = await getHighs();

  // For each concern k, solve min m_k and max m_k
  const perConcern: PerConcernBounds[] = [];
  let feasibleCount = 0;

  for (let k = 0; k < m; k++) {
    let minVal = 0.0;
    let maxVal = 1.0;
    let feasible = true;

    try {
      // Minimize m_k
      const lpMin = buildLpModel("min", k, m, A, Vlo, Vhi);
      const solMin = await highs.solve(lpMin);

      if (solMin.Status === "Optimal" && solMin.Columns[`m${k}`]) {
        minVal = solMin.Columns[`m${k}`].Primal;
      } else if (solMin.Status === "Infeasible") {
        feasible = false;
      }
      // For "Unbounded", min stays at 0

      // Maximize m_k
      const lpMax = buildLpModel("max", k, m, A, Vlo, Vhi);
      const solMax = await highs.solve(lpMax);

      if (solMax.Status === "Optimal" && solMax.Columns[`m${k}`]) {
        maxVal = solMax.Columns[`m${k}`].Primal;
      } else if (solMax.Status === "Infeasible") {
        feasible = false;
      }
      // For "Unbounded", max stays at 1
    } catch {
      // Numerical issues → treat as infeasible for this concern
      feasible = false;
    }

    // Clamp to [0, 1]
    minVal = Math.max(0.0, Math.min(1.0, minVal));
    maxVal = Math.max(0.0, Math.min(1.0, maxVal));
    if (maxVal < minVal) maxVal = minVal;

    if (feasible) feasibleCount++;

    perConcern.push({
      moralConcern: concerns[k],
      minImportance: minVal,
      maxImportance: maxVal,
      centroid: (minVal + maxVal) / 2.0,
    });
  }

  const meanCentroid =
    m > 0 ? perConcern.reduce((s, c) => s + c.centroid, 0) / m : 0.0;

  return {
    perConcern,
    feasible: feasibleCount === m,
    meanCentroidImportance: meanCentroid,
  };
}

/**
 * Synchronous wrapper that produces a simplified point-estimate result
 * matching inferMoralPriorities (simplified surrogate), but includes
 * the PerConcernBounds structure for API parity.
 *
 * Use this when you want the PolytopeInferenceResult shape without
 * the highs-js dependency. All bounds equal the inferred importance
 * (range = 0, centroid = the importance itself).
 *
 * @internal Re-exported for API completeness; prefer inferMoralPrioritiesPolytopeAsync
 * for rigorous inference.
 */
export function inferMoralPrioritiesPolytope(
  dilemma: Dilemma,
  statedPreferabilities: StatedPreferability[],
  alpha: number = 1.0,
  beta: number = 1.0,
  lambda: number = 1.0,
  gamma: number = 1.0,
): PolytopeInferenceResult {
  // Import inferMoralPriorities at call time to avoid circular dependency
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const { inferMoralPriorities } =
    require("./functions") as typeof import("./functions");

  const simplified = inferMoralPriorities(
    dilemma,
    statedPreferabilities,
    alpha,
    beta,
    lambda,
    gamma,
  );

  const perConcern: PerConcernBounds[] = simplified.map((mp: MoralPriority) => {
    const val =
      typeof mp.importance === "number" ? mp.importance : Number(mp.importance);
    return {
      moralConcern: mp.moralConcern,
      minImportance: val,
      maxImportance: val,
      centroid: val,
    };
  });

  const meanCentroid =
    perConcern.length > 0
      ? perConcern.reduce((s, c) => s + c.centroid, 0) / perConcern.length
      : 0.0;

  return {
    perConcern,
    feasible: true,
    meanCentroidImportance: meanCentroid,
  };
}

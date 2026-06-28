/**
 * Ambient type declaration for highs-js (optional dependency).
 *
 * highs-js is a WebAssembly port of the HiGHS linear programming solver.
 * It is used exclusively by polytope.ts for interval linear programming.
 *
 * Install with: npm install highs-js
 *
 * When not installed, inferMoralPrioritiesPolytopeAsync throws a clear
 * error message directing users to install it.
 */
declare module "highs-js" {
  export interface HighsSolution {
    Status: "Optimal" | "Infeasible" | "Unbounded" | string;
    Columns: Record<string, { Primal: number }>;
    ObjectiveValue: number;
  }

  export interface HighsModule {
    solve: (model: string) => Promise<HighsSolution>;
  }

  function highsFactory(): Promise<HighsModule>;
  export default highsFactory;
}

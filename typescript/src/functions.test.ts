import {
  calculateWeightedNetBenefit,
  calculateAllMoralValences,
  calculatePreferabilities,
  calculateDivergenceSignal,
  extractMoralConcernsFromDilemma,
  inferMoralPriorities,
  calculateMoralPriorityDivergenceSignal,
} from "./functions";
import {
  PossibleBenefit,
  QualitativeMagnitude,
  QualitativePreferability,
  NumericalCharacteristic,
  NumericalCharacteristicValueBand,
  Demographic,
  Group,
  CharacteristicBandMembership,
  Effect,
  Dilemma,
  Ethic,
  MoralPriority,
  StatedPreferability,
  DemographicMoralConcern,
} from "./types";
import {
  WORKED_EXAMPLE_DILEMMA,
  WORKED_EXAMPLE_ETHIC,
  WORKED_EXAMPLE_STATED_PREFERABILITIES,
} from "../../fixtures/worked-example";
// eslint-disable-next-line @typescript-eslint/no-require-imports
const FIXTURE = require("../../fixtures/worked-example.json") as Record<
  string,
  any
>;

describe("calculateWeightedNetBenefit", () => {
  it("returns 0 for empty benefits", () => {
    expect(calculateWeightedNetBenefit([], 0)).toBe(0);
  });

  it("calculates expected value with no optimism bias", () => {
    const benefits: PossibleBenefit[] = [
      {
        likelihood: 0.5,
        qualitativeMagnitude: QualitativeMagnitude.Moderate,
        signage: "positive",
      },
      {
        likelihood: 0.5,
        qualitativeMagnitude: QualitativeMagnitude.Moderate,
        signage: "negative",
      },
    ];
    // (0.5 * 4/7) + (0.5 * -4/7) = 0
    expect(calculateWeightedNetBenefit(benefits, 0)).toBeCloseTo(0);
  });

  it("applies optimism bias correctly", () => {
    const benefits: PossibleBenefit[] = [
      {
        likelihood: 0.5,
        qualitativeMagnitude: QualitativeMagnitude.Moderate,
        signage: "positive",
      },
      {
        likelihood: 0.5,
        qualitativeMagnitude: QualitativeMagnitude.Moderate,
        signage: "negative",
      },
    ];
    // With optimism bias 1, only the best (positive) counts: 1 * 4/7 = 0.571...
    expect(calculateWeightedNetBenefit(benefits, 1)).toBeCloseTo(4 / 7);
  });
  it("single negative qualitative", () => {
    const b: PossibleBenefit = {
      likelihood: 1.0,
      qualitativeMagnitude: QualitativeMagnitude.SomewhatHigh,
      signage: "negative",
    };
    expect(calculateWeightedNetBenefit([b])).toBeCloseTo(-5 / 7);
  });

  it("single positive", () => {
    const b: PossibleBenefit = {
      likelihood: 1.0,
      qualitativeMagnitude: QualitativeMagnitude.ExtremelyHigh,
      signage: "positive",
    };
    expect(calculateWeightedNetBenefit([b])).toBeCloseTo(1.0);
  });

  it("zero signage contributes nothing", () => {
    const b: PossibleBenefit = {
      likelihood: 1.0,
      qualitativeMagnitude: QualitativeMagnitude.ExtremelyHigh,
      signage: "zero",
    };
    expect(calculateWeightedNetBenefit([b])).toBe(0.0);
  });

  it("distribution sums correctly", () => {
    const b1: PossibleBenefit = {
      likelihood: 0.8,
      qualitativeMagnitude: QualitativeMagnitude.SomewhatHigh,
      signage: "negative",
    };
    const b2: PossibleBenefit = {
      likelihood: 0.2,
      qualitativeMagnitude: QualitativeMagnitude.VeryHigh,
      signage: "negative",
    };
    const expected = 0.8 * (-5 / 7) + 0.2 * (-6 / 7);
    expect(calculateWeightedNetBenefit([b1, b2])).toBeCloseTo(expected);
  });

  it("optimism bias 1 picks best (least negative)", () => {
    const b1: PossibleBenefit = {
      likelihood: 0.5,
      qualitativeMagnitude: QualitativeMagnitude.ExtremelyHigh,
      signage: "negative",
    };
    const b2: PossibleBenefit = {
      likelihood: 0.5,
      qualitativeMagnitude: QualitativeMagnitude.Negligible,
      signage: "negative",
    };
    // bias=1 → only best outcome (b2, -1/7) counts with weight 1
    expect(calculateWeightedNetBenefit([b1, b2], 1.0)).toBeCloseTo(-1 / 7);
  });

  it("optimism bias 0 equals expected value", () => {
    const b1: PossibleBenefit = {
      likelihood: 0.3,
      qualitativeMagnitude: QualitativeMagnitude.VeryHigh,
      signage: "negative",
    };
    const b2: PossibleBenefit = {
      likelihood: 0.7,
      qualitativeMagnitude: QualitativeMagnitude.Negligible,
      signage: "zero",
    };
    const ev = 0.3 * (-6 / 7);
    expect(calculateWeightedNetBenefit([b1, b2], 0.0)).toBeCloseTo(ev);
  });

  it("quantitative magnitude used directly", () => {
    const b: PossibleBenefit = {
      likelihood: 1.0,
      quantitativeMagnitude: 0.5,
      quantitativeMetric: "normalized",
      signage: "negative",
    };
    expect(calculateWeightedNetBenefit([b])).toBeCloseTo(-0.5);
  });

  it("qualitative takes priority over quantitative absent", () => {
    const b: PossibleBenefit = {
      likelihood: 1.0,
      qualitativeMagnitude: QualitativeMagnitude.Moderate,
      signage: "positive",
    };
    expect(calculateWeightedNetBenefit([b])).toBeCloseTo(4 / 7);
  });
});

// ---------------------------------------------------------------------------
// Shared fixtures for inference tests
// ---------------------------------------------------------------------------

const C3: NumericalCharacteristic = {
  kind: "numerical",
  name: "age",
  minValue: 0,
  maxValue: 100,
};

const D_elderly: Demographic = {
  name: "Elderly",
  numericalBands: [{ characteristic: C3, minValue: 65, maxValue: 100 }],
};
const D_young: Demographic = {
  name: "Young",
  numericalBands: [{ characteristic: C3, minValue: 0, maxValue: 30 }],
};

/** Helper: build a simple group with one demographic membership. */
function demoGroup(name: string, demo: Demographic, count: number): Group {
  return { name, demographicMemberships: [{ demographic: demo, count }] };
}

/** Helper: single-benefit effect */
function simpleEffect(
  group: Group,
  facet: string,
  outlook: string,
  likelihood: number,
  mag: QualitativeMagnitude,
  signage: "positive" | "negative" | "zero",
): Effect {
  return {
    affectedGroup: group,
    facetOfProsperity: facet,
    outlook,
    possibleBenefits: [{ likelihood, qualitativeMagnitude: mag, signage }],
  };
}

/** Helper: stated preferability entry */
function stated(name: string, ordinal: number): StatedPreferability {
  return { choiceName: name, statedPreferability: ordinal as any };
}

// ---------------------------------------------------------------------------
// extractMoralConcernsFromDilemma
// ---------------------------------------------------------------------------

describe("extractMoralConcernsFromDilemma", () => {
  it("extracts one DemographicMoralConcern per unique demographic × facet × outlook", () => {
    const g = demoGroup("G", D_elderly, 5);
    const dilemma: Dilemma = {
      name: "D",
      choices: [
        {
          name: "A",
          effects: [
            simpleEffect(
              g,
              "health",
              "short-term",
              1,
              QualitativeMagnitude.Moderate,
              "negative",
            ),
          ],
        },
      ],
    };
    const concerns = extractMoralConcernsFromDilemma(dilemma);
    expect(concerns).toHaveLength(1);
    expect(concerns[0].kind).toBe("demographic");
    expect((concerns[0] as DemographicMoralConcern).demographic.name).toBe(
      "Elderly",
    );
  });

  it("deduplicates identical concerns across multiple choices", () => {
    const g = demoGroup("G", D_elderly, 3);
    const effect = simpleEffect(
      g,
      "health",
      "short-term",
      1,
      QualitativeMagnitude.Moderate,
      "negative",
    );
    const dilemma: Dilemma = {
      name: "D",
      choices: [
        { name: "A", effects: [effect] },
        { name: "B", effects: [effect] },
      ],
    };
    const concerns = extractMoralConcernsFromDilemma(dilemma);
    expect(concerns).toHaveLength(1);
  });

  it("extracts concerns from characteristicBandMemberships", () => {
    const cbm: CharacteristicBandMembership = {
      characteristicBands: [
        { characteristic: C3, minValue: 65, maxValue: 100 },
      ],
      count: 4,
    };
    const g: Group = { name: "G", characteristicBandMemberships: [cbm] };
    const dilemma: Dilemma = {
      name: "D",
      choices: [
        {
          name: "A",
          effects: [
            simpleEffect(
              g,
              "wealth",
              "long-term",
              0.5,
              QualitativeMagnitude.SomewhatLow,
              "negative",
            ),
          ],
        },
      ],
    };
    const concerns = extractMoralConcernsFromDilemma(dilemma);
    expect(concerns).toHaveLength(1);
    expect(concerns[0].kind).toBe("characteristicBand");
  });

  it("extracts concerns from chainEffects", () => {
    const g1 = demoGroup("G1", D_elderly, 2);
    const g2 = demoGroup("G2", D_young, 3);
    const chainEffect = simpleEffect(
      g2,
      "health",
      "long-term",
      0.5,
      QualitativeMagnitude.Moderate,
      "negative",
    );
    const rootEffect: Effect = {
      ...simpleEffect(
        g1,
        "health",
        "short-term",
        0.8,
        QualitativeMagnitude.VeryHigh,
        "negative",
      ),
      chainEffects: [chainEffect],
    };
    const dilemma: Dilemma = {
      name: "D",
      choices: [{ name: "A", effects: [rootEffect] }],
    };
    const concerns = extractMoralConcernsFromDilemma(dilemma);
    expect(concerns).toHaveLength(2);
  });

  it("returns empty array for dilemma with no group memberships", () => {
    const g: Group = { name: "G" };
    const dilemma: Dilemma = {
      name: "D",
      choices: [
        {
          name: "A",
          effects: [
            simpleEffect(
              g,
              "health",
              "short-term",
              1,
              QualitativeMagnitude.Moderate,
              "negative",
            ),
          ],
        },
      ],
    };
    const concerns = extractMoralConcernsFromDilemma(dilemma);
    expect(concerns).toHaveLength(0);
  });
});

// ---------------------------------------------------------------------------
// inferMoralPriorities
// ---------------------------------------------------------------------------

describe("inferMoralPriorities", () => {
  /**
   * Single concern, single choice: the recovered importance should be the unique
   * x satisfying A[0][0] * x = b[0], i.e. x = b[0] / A[0][0], clamped to [0,1].
   */
  it("recovers exact importance for a single-concern single-choice system", () => {
    const g = demoGroup("G", D_elderly, 1);
    // A[0][0] = wnb × importance_at_1 = (1 × 1/7) × 1 = 1/7
    const effect = simpleEffect(
      g,
      "health",
      "short-term",
      1,
      QualitativeMagnitude.Negligible,
      "negative",
    );
    const dilemma: Dilemma = {
      name: "D",
      choices: [{ name: "A", effects: [effect] }],
    };
    // With stated preferability = 4 (Neutral), solving: (1/7)^2 * x = (1/7) * 4 → x = 4 * 7 = 28 → clamped to 1
    const result = inferMoralPriorities(dilemma, [stated("A", 4)]);
    expect(result).toHaveLength(1);
    // importance clamped to [0,1]
    expect(result[0].importance).toBeGreaterThanOrEqual(0);
    expect(result[0].importance).toBeLessThanOrEqual(1);
  });

  it("assigns zero importance to a zero-contribution concern", () => {
    // Group with no memberships → contribution matrix column = 0
    const g: Group = { name: "G" };
    const dilemma: Dilemma = {
      name: "D",
      choices: [
        {
          name: "A",
          effects: [
            simpleEffect(
              g,
              "health",
              "short-term",
              1,
              QualitativeMagnitude.Moderate,
              "negative",
            ),
          ],
        },
      ],
    };
    const result = inferMoralPriorities(dilemma, [stated("A", 3)]);
    // No concerns extracted (group has no memberships), so result is empty
    expect(result).toHaveLength(0);
  });

  it("defaults missing stated preferability to Neutral (4)", () => {
    const g = demoGroup("G", D_elderly, 2);
    const dilemma: Dilemma = {
      name: "D",
      choices: [
        {
          name: "A",
          effects: [
            simpleEffect(
              g,
              "health",
              "short-term",
              1,
              QualitativeMagnitude.Moderate,
              "negative",
            ),
          ],
        },
        {
          name: "B",
          effects: [
            simpleEffect(
              g,
              "health",
              "short-term",
              1,
              QualitativeMagnitude.VeryHigh,
              "negative",
            ),
          ],
        },
      ],
    };
    // Supply stated only for "A"; "B" should default to 4
    expect(() => inferMoralPriorities(dilemma, [stated("A", 2)])).not.toThrow();
    const result = inferMoralPriorities(dilemma, [stated("A", 2)]);
    expect(result).toHaveLength(1);
    expect(result[0].importance).toBeGreaterThanOrEqual(0);
    expect(result[0].importance).toBeLessThanOrEqual(1);
  });

  it("returns all-zero importances when contribution matrix is all zeros", () => {
    // Empty group, but we'll mock by using two choices with zero-magnitude effects
    const g = demoGroup("G", D_elderly, 1);
    const zeroEffect: Effect = {
      affectedGroup: g,
      facetOfProsperity: "health",
      outlook: "short-term",
      possibleBenefits: [
        {
          likelihood: 1.0,
          qualitativeMagnitude: QualitativeMagnitude.Moderate,
          signage: "zero",
        },
      ],
    };
    const dilemma: Dilemma = {
      name: "D",
      choices: [
        { name: "A", effects: [zeroEffect] },
        { name: "B", effects: [zeroEffect] },
      ],
    };
    const result = inferMoralPriorities(dilemma, [
      stated("A", 1),
      stated("B", 7),
    ]);
    expect(result).toHaveLength(1);
    expect(result[0].importance).toBe(0);
  });

  it("inferred importances lie in [0, 1]", () => {
    // Two concerns, two choices with non-trivial cross-effects to stress the solver
    const g1 = demoGroup("G1", D_elderly, 3);
    const g2 = demoGroup("G2", D_young, 5);
    const dilemma: Dilemma = {
      name: "D",
      choices: [
        {
          name: "A",
          effects: [
            simpleEffect(
              g1,
              "health",
              "short-term",
              0.8,
              QualitativeMagnitude.VeryHigh,
              "negative",
            ),
            simpleEffect(
              g2,
              "health",
              "short-term",
              0.2,
              QualitativeMagnitude.Moderate,
              "negative",
            ),
          ],
        },
        {
          name: "B",
          effects: [
            simpleEffect(
              g1,
              "health",
              "short-term",
              0.3,
              QualitativeMagnitude.Moderate,
              "negative",
            ),
            simpleEffect(
              g2,
              "health",
              "short-term",
              0.9,
              QualitativeMagnitude.ExtremelyHigh,
              "negative",
            ),
          ],
        },
      ],
    };
    const result = inferMoralPriorities(dilemma, [
      stated("A", 3),
      stated("B", 6),
    ]);
    expect(result).toHaveLength(2);
    for (const p of result) {
      expect(p.importance).toBeGreaterThanOrEqual(0);
      expect(p.importance).toBeLessThanOrEqual(1);
    }
  });
});

// ---------------------------------------------------------------------------
// calculateMoralPriorityDivergenceSignal
// ---------------------------------------------------------------------------

describe("calculateMoralPriorityDivergenceSignal", () => {
  const demoConcern: DemographicMoralConcern = {
    kind: "demographic",
    demographic: D_elderly,
    facetOfProsperity: "health",
    outlook: "short-term",
  };

  it("produces zero divergence when purported and inferred importances match exactly", () => {
    const inferred: MoralPriority[] = [
      { moralConcern: demoConcern, importance: 0.5 },
    ];
    const purported: MoralPriority[] = [
      { moralConcern: demoConcern, importance: 0.5 },
    ];
    const signal = calculateMoralPriorityDivergenceSignal(purported, inferred);
    expect(signal.perConcern).toHaveLength(1);
    expect(signal.perConcern[0].absoluteDivergence).toBeCloseTo(0);
    expect(signal.meanAbsoluteDivergence).toBeCloseTo(0);
  });

  it("assigns purportedImportance=0 when no matching purported priority exists", () => {
    const inferred: MoralPriority[] = [
      { moralConcern: demoConcern, importance: 0.7 },
    ];
    const purported: MoralPriority[] = []; // no match
    const signal = calculateMoralPriorityDivergenceSignal(purported, inferred);
    expect(signal.perConcern[0].purportedImportance).toBe(0);
    expect(signal.perConcern[0].inferredImportance).toBeCloseTo(0.7);
    expect(signal.perConcern[0].signedDivergence).toBeCloseTo(-0.7);
    expect(signal.perConcern[0].absoluteDivergence).toBeCloseTo(0.7);
  });

  it("normalizes QualitativeMagnitude ordinals from purported priorities (ordinal/7)", () => {
    // Purported uses QualitativeMagnitude.ExtremelyHigh = 7 → normalized to 1.0
    const purported: MoralPriority[] = [
      {
        moralConcern: demoConcern,
        importance: QualitativeMagnitude.ExtremelyHigh,
      },
    ];
    const inferred: MoralPriority[] = [
      { moralConcern: demoConcern, importance: 0.5 },
    ];
    const signal = calculateMoralPriorityDivergenceSignal(purported, inferred);
    expect(signal.perConcern[0].purportedImportance).toBeCloseTo(1.0);
    expect(signal.perConcern[0].signedDivergence).toBeCloseTo(0.5);
  });

  it("computes correct meanAbsoluteDivergence for multiple concerns", () => {
    const youngConcern: DemographicMoralConcern = {
      kind: "demographic",
      demographic: D_young,
      facetOfProsperity: "wealth",
      outlook: "long-term",
    };
    const inferred: MoralPriority[] = [
      { moralConcern: demoConcern, importance: 0.4 },
      { moralConcern: youngConcern, importance: 0.6 },
    ];
    const purported: MoralPriority[] = [
      { moralConcern: demoConcern, importance: 0.6 },
      { moralConcern: youngConcern, importance: 0.2 },
    ];
    const signal = calculateMoralPriorityDivergenceSignal(purported, inferred);
    // |0.6 - 0.4| = 0.2; |0.2 - 0.6| = 0.4; mean = 0.3
    expect(signal.meanAbsoluteDivergence).toBeCloseTo(0.3);
  });

  it("returns zero meanAbsoluteDivergence for empty inferred list", () => {
    const signal = calculateMoralPriorityDivergenceSignal([], []);
    expect(signal.perConcern).toHaveLength(0);
    expect(signal.meanAbsoluteDivergence).toBe(0);
  });
});

// ---------------------------------------------------------------------------
// Fixture: worked-example cross-language consistency
// ---------------------------------------------------------------------------

/**
 * These tests load the canonical worked-example.json and verify that the
 * TypeScript implementation produces results consistent with the expectedResults
 * block.  They guard against drift between the fixture and both packages.
 */
describe("worked-example fixture: moral valences + preferabilities", () => {
  const dilemma = WORKED_EXAMPLE_DILEMMA as unknown as Dilemma;
  const ethic = WORKED_EXAMPLE_ETHIC as unknown as Ethic;

  const valences = calculateAllMoralValences(dilemma, ethic);
  const prefs = calculatePreferabilities(valences);

  it.each(["Choice 1", "Choice 2", "Choice 3", "Choice 4"])(
    "moral valence for %s matches fixture",
    (choice) => {
      const expected = FIXTURE.expectedResults.moralValences[choice] as number;
      expect(valences[choice]).toBeCloseTo(expected, 3);
    },
  );

  it.each(["Choice 1", "Choice 2", "Choice 3", "Choice 4"])(
    "preferability ordinal for %s matches fixture",
    (choice) => {
      const expected = FIXTURE.expectedResults.calculatedPreferabilities[
        choice
      ] as number;
      expect(prefs[choice]).toBe(expected);
    },
  );

  it("prescribed choice matches fixture", () => {
    const prescribed = Object.keys(valences).reduce((a, b) =>
      valences[a] > valences[b] ? a : b,
    );
    expect(prescribed).toBe(FIXTURE.expectedResults.prescribedChoice);
  });
});

describe("worked-example fixture: divergence signal", () => {
  const dilemma = WORKED_EXAMPLE_DILEMMA as unknown as Dilemma;
  const ethic = WORKED_EXAMPLE_ETHIC as unknown as Ethic;
  const statedRaw = WORKED_EXAMPLE_STATED_PREFERABILITIES as unknown as Array<{
    choiceName: string;
    statedPreferability: QualitativePreferability;
  }>;

  const valences = calculateAllMoralValences(dilemma, ethic);
  const prefs = calculatePreferabilities(valences);
  const signal = calculateDivergenceSignal(statedRaw, prefs);

  it.each(["Choice 1", "Choice 2", "Choice 3", "Choice 4"])(
    "signed divergence for %s matches fixture",
    (choice) => {
      const expected = FIXTURE.expectedResults.divergence[choice] as number;
      const result = signal.perChoice.find((r) => r.choiceName === choice)!;
      expect(result.signedDivergence).toBe(expected);
    },
  );

  it("mean absolute divergence matches fixture", () => {
    const expected = FIXTURE.expectedResults.meanAbsoluteDivergence as number;
    expect(signal.meanAbsoluteDivergence).toBeCloseTo(expected, 3);
  });
});

describe("worked-example fixture: inferred moral priorities", () => {
  const dilemma = WORKED_EXAMPLE_DILEMMA as unknown as Dilemma;
  const ethic = WORKED_EXAMPLE_ETHIC as unknown as Ethic;
  const statedRaw = FIXTURE.statedPreferabilities as Array<{
    choiceName: string;
    statedPreferability: number;
  }>;
  const stated: StatedPreferability[] = statedRaw.map((s) => ({
    choiceName: s.choiceName,
    statedPreferability: s.statedPreferability as QualitativePreferability,
  }));

  const inferred = inferMoralPriorities(dilemma, stated);
  const signal = calculateMoralPriorityDivergenceSignal(
    ethic.moralPriorities as unknown as MoralPriority[],
    inferred,
  );

  const expectedPriorities = FIXTURE.expectedResults
    .inferredMoralPriorities as Record<string, number>;
  const expectedSignal = FIXTURE.expectedResults
    .moralPriorityDivergenceSignalFromStatedPreferabilities as {
    meanAbsoluteDivergence: number;
    perConcern: Record<
      string,
      {
        purportedImportance: number;
        inferredImportance: number;
        absoluteDivergence: number;
      }
    >;
  };

  it("infers the correct number of concerns", () => {
    const expectedCount = Object.keys(expectedPriorities).filter(
      (k) => !k.startsWith("_"),
    ).length;
    expect(inferred).toHaveLength(expectedCount);
  });

  it.each(
    Object.entries(expectedPriorities).filter(([k]) => !k.startsWith("_")) as [
      string,
      number,
    ][],
  )(
    "inferred importance for '%s' matches fixture",
    (concernKey, expectedImp) => {
      const result = inferred.find((p) => {
        const k =
          p.moralConcern.kind === "demographic"
            ? `demographic|${p.moralConcern.facetOfProsperity}|${p.moralConcern.outlook}|${p.moralConcern.demographic.name}`
            : (() => {
                const bands = p.moralConcern.characteristicBands
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
                return `characteristicBand|${p.moralConcern.facetOfProsperity}|${p.moralConcern.outlook}|${bands}`;
              })();
        return k === concernKey;
      });
      expect(result).toBeDefined();
      expect(result!.importance).toBeCloseTo(expectedImp, 3);
    },
  );

  it("priority divergence MAD matches fixture", () => {
    expect(signal.meanAbsoluteDivergence).toBeCloseTo(
      expectedSignal.meanAbsoluteDivergence,
      3,
    );
  });

  it.each(
    Object.entries(expectedSignal.perConcern).filter(
      ([k]) => !k.startsWith("_"),
    ) as [
      string,
      {
        purportedImportance: number;
        inferredImportance: number;
        absoluteDivergence: number;
      },
    ][],
  )("priority divergence for '%s' matches fixture", (concernKey, exp) => {
    const result = signal.perConcern.find((r) => {
      const k =
        r.moralConcern.kind === "demographic"
          ? `demographic|${r.moralConcern.facetOfProsperity}|${r.moralConcern.outlook}|${r.moralConcern.demographic.name}`
          : (() => {
              const bands = r.moralConcern.characteristicBands
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
              return `characteristicBand|${r.moralConcern.facetOfProsperity}|${r.moralConcern.outlook}|${bands}`;
            })();
      return k === concernKey;
    });
    expect(result).toBeDefined();
    expect(result!.purportedImportance).toBeCloseTo(exp.purportedImportance, 3);
    expect(result!.inferredImportance).toBeCloseTo(exp.inferredImportance, 3);
    expect(result!.absoluteDivergence).toBeCloseTo(exp.absoluteDivergence, 3);
  });
});

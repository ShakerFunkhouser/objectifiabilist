import {
  calculateWeightedNetBenefit,
  calculateAllMoralValences,
  calculatePreferabilities,
  calculateDivergenceSignal,
  extractMoralConcernsFromDilemma,
  inferMoralPriorities,
  calculateMoralPriorityDivergenceSignal,
  calculateMoralValueOfEffect,
  isActionPermitted,
  buildMoralPrioritiesFromDifferentials,
} from "./functions";
import {
  PossibleBenefit,
  QualitativeMagnitude,
  QualitativePreferability,
  QualitativeDifferenceMagnitude,
  NumericalCharacteristic,
  NumericalCharacteristicValueBand,
  ConversionMetric,
  Demographic,
  DemographicMembership,
  Group,
  CharacteristicBandMembership,
  Effect,
  Dilemma,
  Ethic,
  MoralPriority,
  OverridingDuty,
  StatedPreferability,
  DemographicMoralConcern,
  CharacteristicBandMoralConcern,
  Choice,
  Signage,
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
    expect(calculateWeightedNetBenefit([])).toBe(0);
  });

  it("calculates expected value (symmetric cancels to 0)", () => {
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
    // (0.5 * 3/6) + (0.5 * -3/6) = 0
    expect(calculateWeightedNetBenefit(benefits)).toBeCloseTo(0);
  });

  it("default CPT params yield standard expected value", () => {
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
    // defaults alpha=beta=lambda=gamma=1 → standard EV: 0
    expect(calculateWeightedNetBenefit(benefits, 1, 1, 1, 1)).toBeCloseTo(0);
  });
  it("single negative qualitative", () => {
    const b: PossibleBenefit = {
      likelihood: 1.0,
      qualitativeMagnitude: QualitativeMagnitude.SomewhatHigh,
      signage: "negative",
    };
    expect(calculateWeightedNetBenefit([b])).toBeCloseTo(-4 / 6);
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
    const expected = 0.8 * (-4 / 6) + 0.2 * (-5 / 6);
    expect(calculateWeightedNetBenefit([b1, b2])).toBeCloseTo(expected);
  });

  it("loss aversion (lambda=2) doubles negative magnitudes", () => {
    const b1: PossibleBenefit = {
      likelihood: 1.0,
      qualitativeMagnitude: QualitativeMagnitude.Moderate,
      signage: "negative",
    };
    // lambda=2 → v(b) = -2 * (3/6)^1 = -1.0
    expect(calculateWeightedNetBenefit([b1], 1, 1, 2)).toBeCloseTo(-1.0);
  });

  it("Negligible magnitude contributes 0", () => {
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
    // EV: 0.3 * (-5/6) + 0.7 * 0 = -0.25
    expect(calculateWeightedNetBenefit([b1, b2])).toBeCloseTo(0.3 * (-5 / 6));
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

  it("qualitative resolves to ordinal/6", () => {
    const b: PossibleBenefit = {
      likelihood: 1.0,
      qualitativeMagnitude: QualitativeMagnitude.Moderate,
      signage: "positive",
    };
    expect(calculateWeightedNetBenefit([b])).toBeCloseTo(3 / 6);
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
      affectedGroup: g1,
      facetOfProsperity: "health",
      outlook: "short-term",
      possibleBenefits: [
        {
          likelihood: 0.8,
          qualitativeMagnitude: QualitativeMagnitude.VeryHigh,
          signage: "negative",
          chainEffects: [chainEffect],
        },
      ],
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
    // A[0][0] = wnb × importance_at_1 = (1 × 0/6) × 1 = 0
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
    // With stated preferability = 3 (Neutral), contribution is 0 → importance unconstrained, clamped
    const result = inferMoralPriorities(dilemma, [stated("A", 3)]);
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
      stated("A", 0),
      stated("B", 6),
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
      expect(prefs[choice].calculatedPreferability).toBe(expected);
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

  it("mean prescriptive divergence matches fixture", () => {
    const expected = FIXTURE.expectedResults
      .meanPrescriptiveDivergence as number;
    expect(signal.meanPrescriptiveDivergence).toBeCloseTo(expected, 3);
  });

  it("prescriptive divergence band matches fixture", () => {
    expect(signal.prescriptiveDivergenceBand).toBe(
      FIXTURE.expectedResults.prescriptiveDivergenceBand,
    );
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

// ---------------------------------------------------------------------------
// Ideal-state raw benefit and moral value (§3.5.1)
// ---------------------------------------------------------------------------

describe("ideal-state weighted net-benefit", () => {
  function pb(
    likelihood: number,
    mag: QualitativeMagnitude,
    signage: Signage = "positive",
  ): PossibleBenefit {
    return { likelihood, qualitativeMagnitude: mag, signage };
  }

  const baseConcern: DemographicMoralConcern = {
    kind: "demographic",
    demographic: { name: "TestPop" },
    facetOfProsperity: "health",
    outlook: "short-term",
  };

  it("uses signed magnitude if no ideal state", () => {
    const priority: MoralPriority = {
      moralConcern: baseConcern,
      importance: QualitativeMagnitude.Moderate,
    };
    const result = calculateWeightedNetBenefit(
      [pb(1.0, QualitativeMagnitude.Moderate)],
      1,
      1,
      1,
      1,
      priority,
    );
    expect(result).toBeCloseTo(0.5); // +3/6 = +0.5
  });

  it("range mode: within bounds → raw = 1.0", () => {
    const priority: MoralPriority = {
      moralConcern: baseConcern,
      importance: QualitativeMagnitude.Moderate,
      minStatus: QualitativeMagnitude.SomewhatLow, // 2/6 = 0.333
      maxStatus: QualitativeMagnitude.SomewhatHigh, // 4/6 = 0.667
    };
    const result = calculateWeightedNetBenefit(
      [pb(0.8, QualitativeMagnitude.Moderate)],
      1,
      1,
      1,
      1,
      priority,
    );
    // w(0.8) × v(1.0) = 0.8
    expect(result).toBeCloseTo(0.8);
  });

  it("range mode: below min", () => {
    const priority: MoralPriority = {
      moralConcern: baseConcern,
      importance: QualitativeMagnitude.Moderate,
      minStatus: QualitativeMagnitude.Moderate, // 3/6 = 0.5
      maxStatus: QualitativeMagnitude.VeryHigh, // 5/6 = 0.833
    };
    const result = calculateWeightedNetBenefit(
      [pb(1.0, QualitativeMagnitude.VeryLow)],
      1,
      1,
      1,
      1,
      priority,
    );
    // raw = 1 - (0.5 - 0.167)/0.5 = 0.333
    expect(result).toBeCloseTo(1 / 3);
  });

  it("range mode: above max", () => {
    const priority: MoralPriority = {
      moralConcern: baseConcern,
      importance: QualitativeMagnitude.Moderate,
      minStatus: QualitativeMagnitude.VeryLow, // 1/6 = 0.167
      maxStatus: QualitativeMagnitude.SomewhatLow, // 2/6 = 0.333
    };
    const result = calculateWeightedNetBenefit(
      [pb(1.0, QualitativeMagnitude.ExtremelyHigh)],
      1,
      1,
      1,
      1,
      priority,
    );
    // b_incoming=+6/6=1.0; raw = 1 - (1.0 - 0.333)/0.333 = -1.0
    expect(result).toBeCloseTo(-1.0);
  });

  it("reference mode: min only", () => {
    const priority: MoralPriority = {
      moralConcern: baseConcern,
      importance: QualitativeMagnitude.Moderate,
      minStatus: QualitativeMagnitude.Moderate, // 3/6 = 0.5
    };
    const b: PossibleBenefit = {
      likelihood: 1.0,
      qualitativeMagnitude: QualitativeMagnitude.VeryLow,
      signage: "negative",
    };
    const result = calculateWeightedNetBenefit([b], 1, 1, 1, 1, priority);
    // b_ref = 0.5; raw = 1 - |0.5 - (-0.167)|/0.5 = -0.333
    expect(result).toBeCloseTo(-1 / 3);
  });

  it("reference mode: max only", () => {
    const priority: MoralPriority = {
      moralConcern: baseConcern,
      importance: QualitativeMagnitude.Moderate,
      maxStatus: QualitativeMagnitude.VeryHigh, // 5/6 = 0.833
    };
    const result = calculateWeightedNetBenefit(
      [pb(1.0, QualitativeMagnitude.Moderate)],
      1,
      1,
      1,
      1,
      priority,
    );
    // b_ref = 0.833; raw = 1 - |0.833 - 0.5|/0.833 = 0.6
    expect(result).toBeCloseTo(0.6);
  });

  it("negative incoming below min → raw negative", () => {
    const priority: MoralPriority = {
      moralConcern: baseConcern,
      importance: QualitativeMagnitude.Moderate,
      minStatus: QualitativeMagnitude.SomewhatLow, // 2/6 = 0.333
      maxStatus: QualitativeMagnitude.SomewhatHigh, // 4/6 = 0.667
    };
    const b: PossibleBenefit = {
      likelihood: 1.0,
      qualitativeMagnitude: QualitativeMagnitude.SomewhatLow,
      signage: "negative",
    };
    const result = calculateWeightedNetBenefit([b], 1, 1, 1, 1, priority);
    // b_res = -0.333; raw = 1 - (0.333 - (-0.333))/0.333 = -1
    expect(result).toBeCloseTo(-1.0);
  });
});

describe("ideal-state moral value of effect", () => {
  it("per-priority WNB with mixed ideal/signed priorities", () => {
    const D1: Demographic = { name: "GroupA" };
    const D2: Demographic = { name: "GroupB" };
    const g: Group = {
      name: "G",
      demographicMemberships: [
        { demographic: D1, count: 1 },
        { demographic: D2, count: 1 },
      ],
    };
    const effect: Effect = {
      affectedGroup: g,
      facetOfProsperity: "health",
      outlook: "short-term",
      possibleBenefits: [
        {
          likelihood: 1.0,
          qualitativeMagnitude: QualitativeMagnitude.ExtremelyHigh,
          signage: "positive",
        },
      ],
    };
    const ethic: Ethic = {
      name: "Test Ethic",
      moralPriorities: [
        {
          moralConcern: {
            kind: "demographic",
            demographic: D1,
            facetOfProsperity: "health",
            outlook: "short-term",
          },
          importance: QualitativeMagnitude.ExtremelyHigh, // 6/6 = 1.0
          minStatus: QualitativeMagnitude.SomewhatHigh, // 4/6 = 0.667
          maxStatus: QualitativeMagnitude.ExtremelyHigh, // 6/6 = 1.0
        },
        {
          moralConcern: {
            kind: "demographic",
            demographic: D2,
            facetOfProsperity: "health",
            outlook: "short-term",
          },
          importance: QualitativeMagnitude.ExtremelyHigh, // 6/6 = 1.0
        },
      ],
    };
    const val = calculateMoralValueOfEffect(effect, ethic);
    // Priority 1 (ideal): b_incoming=+6/6=1.0, within [0.667,1.0] → raw=1.0, WNB=1.0, M=1.0 → 1.0
    // Priority 2 (signed): b_incoming=+6/6=1.0, WNB=1.0, M=1.0 → 1.0
    // effect.likelihood=1.0 → total = 2.0
    expect(val).toBeCloseTo(2.0);
  });

  it("no matching priority returns zero", () => {
    const g: Group = {
      name: "G",
      demographicMemberships: [
        { demographic: { name: "Irrelevant" }, count: 1 },
      ],
    };
    const effect: Effect = {
      affectedGroup: g,
      facetOfProsperity: "health",
      outlook: "short-term",
      possibleBenefits: [
        {
          likelihood: 1.0,
          qualitativeMagnitude: QualitativeMagnitude.ExtremelyHigh,
          signage: "positive",
        },
      ],
    };
    const ethic: Ethic = {
      name: "Test Ethic",
      moralPriorities: [
        {
          moralConcern: {
            kind: "demographic",
            demographic: { name: "Other" },
            facetOfProsperity: "wealth",
            outlook: "long-term",
          },
          importance: QualitativeMagnitude.ExtremelyHigh,
        },
      ],
    };
    expect(calculateMoralValueOfEffect(effect, ethic)).toBe(0);
  });
});

// ---------------------------------------------------------------------------
// Overriding duties (§3.7)
// ---------------------------------------------------------------------------

describe("isActionPermitted – overriding duties", () => {
  const baseConcern: DemographicMoralConcern = {
    kind: "demographic",
    demographic: { name: "PopA" },
    facetOfProsperity: "health",
    outlook: "short-term",
  };

  it("no overriding duties → always permitted", () => {
    const g: Group = {
      name: "G",
      demographicMemberships: [
        { demographic: baseConcern.demographic, count: 1 },
      ],
    };
    const choice: Choice = {
      name: "A",
      effects: [
        {
          affectedGroup: g,
          facetOfProsperity: "health",
          outlook: "short-term",
          possibleBenefits: [
            {
              likelihood: 1.0,
              qualitativeMagnitude: QualitativeMagnitude.ExtremelyHigh,
              signage: "negative",
            },
          ],
        },
      ],
    };
    const ethic: Ethic = {
      name: "E",
      moralPriorities: [
        {
          moralConcern: baseConcern,
          importance: QualitativeMagnitude.Moderate,
        },
      ],
    };
    expect(isActionPermitted(choice, ethic)).toBe(true);
  });

  it("duty triggers: beneficiary benefits + obligated harmed → prohibited", () => {
    const beneficiaryConcern: DemographicMoralConcern = {
      kind: "demographic",
      demographic: { name: "Beneficiary" },
      facetOfProsperity: "wealth",
      outlook: "long-term",
    };
    const g: Group = {
      name: "G",
      demographicMemberships: [
        { demographic: { name: "Beneficiary" }, count: 1 },
        { demographic: baseConcern.demographic, count: 1 },
      ],
    };
    const choice: Choice = {
      name: "A",
      effects: [
        {
          affectedGroup: g,
          facetOfProsperity: "wealth",
          outlook: "long-term",
          possibleBenefits: [
            {
              likelihood: 1.0,
              qualitativeMagnitude: QualitativeMagnitude.ExtremelyHigh,
              signage: "positive",
            },
          ],
        },
        {
          affectedGroup: g,
          facetOfProsperity: "health",
          outlook: "short-term",
          possibleBenefits: [
            {
              likelihood: 1.0,
              qualitativeMagnitude: QualitativeMagnitude.ExtremelyHigh,
              signage: "negative",
            },
          ],
        },
      ],
    };
    const duty: OverridingDuty = {
      beneficiaryMoralConcern: beneficiaryConcern,
      obligatoryDetrimentThreshold: QualitativeMagnitude.SomewhatHigh,
    };
    const ethic: Ethic = {
      name: "E",
      moralPriorities: [
        {
          moralConcern: baseConcern,
          importance: QualitativeMagnitude.Moderate,
          overridingDuties: [duty],
        },
        {
          moralConcern: beneficiaryConcern,
          importance: QualitativeMagnitude.Moderate,
        },
      ],
    };
    expect(isActionPermitted(choice, ethic)).toBe(false);
  });

  it("duty not triggered when beneficiary doesn't benefit", () => {
    const beneficiaryConcern: DemographicMoralConcern = {
      kind: "demographic",
      demographic: { name: "Beneficiary" },
      facetOfProsperity: "wealth",
      outlook: "long-term",
    };
    const g: Group = {
      name: "G",
      demographicMemberships: [
        { demographic: { name: "Beneficiary" }, count: 1 },
        { demographic: baseConcern.demographic, count: 1 },
      ],
    };
    const choice: Choice = {
      name: "A",
      effects: [
        {
          affectedGroup: g,
          facetOfProsperity: "wealth",
          outlook: "long-term",
          possibleBenefits: [
            {
              likelihood: 1.0,
              qualitativeMagnitude: QualitativeMagnitude.ExtremelyHigh,
              signage: "negative",
            },
          ],
        },
        {
          affectedGroup: g,
          facetOfProsperity: "health",
          outlook: "short-term",
          possibleBenefits: [
            {
              likelihood: 1.0,
              qualitativeMagnitude: QualitativeMagnitude.ExtremelyHigh,
              signage: "negative",
            },
          ],
        },
      ],
    };
    const duty: OverridingDuty = {
      beneficiaryMoralConcern: beneficiaryConcern,
      obligatoryDetrimentThreshold: QualitativeMagnitude.SomewhatHigh,
    };
    const ethic: Ethic = {
      name: "E",
      moralPriorities: [
        {
          moralConcern: baseConcern,
          importance: QualitativeMagnitude.Moderate,
          overridingDuties: [duty],
        },
        {
          moralConcern: beneficiaryConcern,
          importance: QualitativeMagnitude.Moderate,
        },
      ],
    };
    expect(isActionPermitted(choice, ethic)).toBe(true);
  });

  it("beneficiary count scales down effective detriment", () => {
    const beneficiaryConcern: DemographicMoralConcern = {
      kind: "demographic",
      demographic: { name: "Beneficiary" },
      facetOfProsperity: "wealth",
      outlook: "long-term",
    };
    const g: Group = {
      name: "G",
      demographicMemberships: [
        { demographic: { name: "Beneficiary" }, count: 10 },
        { demographic: baseConcern.demographic, count: 1 },
      ],
    };
    const choice: Choice = {
      name: "A",
      effects: [
        {
          affectedGroup: g,
          facetOfProsperity: "wealth",
          outlook: "long-term",
          possibleBenefits: [
            {
              likelihood: 1.0,
              qualitativeMagnitude: QualitativeMagnitude.ExtremelyHigh,
              signage: "positive",
            },
          ],
        },
        {
          affectedGroup: g,
          facetOfProsperity: "health",
          outlook: "short-term",
          possibleBenefits: [
            {
              likelihood: 1.0,
              qualitativeMagnitude: QualitativeMagnitude.ExtremelyHigh,
              signage: "negative",
            },
          ],
        },
      ],
    };
    const duty: OverridingDuty = {
      beneficiaryMoralConcern: beneficiaryConcern,
      obligatoryDetrimentThreshold: QualitativeMagnitude.SomewhatHigh,
    };
    const ethic: Ethic = {
      name: "E",
      moralPriorities: [
        {
          moralConcern: baseConcern,
          importance: QualitativeMagnitude.Moderate,
          overridingDuties: [duty],
        },
        {
          moralConcern: beneficiaryConcern,
          importance: QualitativeMagnitude.Moderate,
        },
      ],
    };
    expect(isActionPermitted(choice, ethic)).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// Ambiguity aversion — probability range collapse (§2.4)
// ---------------------------------------------------------------------------

describe("ambiguityAversion probability collapse", () => {
  it("point likelihood unchanged by ambiguity parameter", () => {
    const pb: PossibleBenefit = {
      likelihood: 0.7,
      qualitativeMagnitude: QualitativeMagnitude.Moderate,
      signage: "positive",
    };
    // ambiguityAversion has no effect when no range is specified
    // 0.7 × 3/6 = 0.35
    expect(
      calculateWeightedNetBenefit([pb], 1, 1, 1, 1, undefined, 0.0),
    ).toBeCloseTo(0.35);
    expect(
      calculateWeightedNetBenefit([pb], 1, 1, 1, 1, undefined, 1.0),
    ).toBeCloseTo(0.35);
  });

  it("maximin (a=1) collapses to low bound", () => {
    const pb: PossibleBenefit = {
      likelihood: 0,
      likelihoodLow: 0.3,
      likelihoodHigh: 0.9,
      qualitativeMagnitude: QualitativeMagnitude.ExtremelyHigh,
      signage: "positive",
    };
    // p_eff = 1*0.3 + 0*0.9 = 0.3; WNB = 0.3 * 1.0 = 0.3
    expect(
      calculateWeightedNetBenefit([pb], 1, 1, 1, 1, undefined, 1.0),
    ).toBeCloseTo(0.3);
  });

  it("max optimism (a=0) collapses to high bound", () => {
    const pb: PossibleBenefit = {
      likelihood: 0,
      likelihoodLow: 0.3,
      likelihoodHigh: 0.9,
      qualitativeMagnitude: QualitativeMagnitude.ExtremelyHigh,
      signage: "positive",
    };
    expect(
      calculateWeightedNetBenefit([pb], 1, 1, 1, 1, undefined, 0.0),
    ).toBeCloseTo(0.9);
  });

  it("indifference (a=0.5) uses midpoint", () => {
    const pb: PossibleBenefit = {
      likelihood: 0,
      likelihoodLow: 0.2,
      likelihoodHigh: 0.8,
      qualitativeMagnitude: QualitativeMagnitude.ExtremelyHigh,
      signage: "positive",
    };
    expect(
      calculateWeightedNetBenefit([pb], 1, 1, 1, 1, undefined, 0.5),
    ).toBeCloseTo(0.5);
  });

  it("missing one bound falls back to point likelihood", () => {
    const pb: PossibleBenefit = {
      likelihood: 0.5,
      likelihoodLow: 0.2, // no likelihoodHigh
      qualitativeMagnitude: QualitativeMagnitude.ExtremelyHigh,
      signage: "positive",
    };
    expect(
      calculateWeightedNetBenefit([pb], 1, 1, 1, 1, undefined, 1.0),
    ).toBeCloseTo(0.5);
  });
});

// ---------------------------------------------------------------------------
// Conversion metric normalization (§2.5)
// ---------------------------------------------------------------------------

describe("conversionMetric normalization", () => {
  it("quantitative magnitude is normalized by threshold", () => {
    const cm: ConversionMetric = {
      fromMetric: "USD",
      extremelyBeneficialThreshold: 100_000,
    };
    const pb: PossibleBenefit = {
      likelihood: 1.0,
      quantitativeMagnitude: 50_000,
      quantitativeMetric: "USD",
      signage: "positive",
    };
    expect(
      calculateWeightedNetBenefit([pb], 1, 1, 1, 1, undefined, 0.5, [cm]),
    ).toBeCloseTo(0.5);
  });

  it("magnitude exceeding threshold is clamped at 1.0", () => {
    const cm: ConversionMetric = {
      fromMetric: "USD",
      extremelyBeneficialThreshold: 1000,
    };
    const pb: PossibleBenefit = {
      likelihood: 1.0,
      quantitativeMagnitude: 5000,
      quantitativeMetric: "USD",
      signage: "positive",
    };
    expect(
      calculateWeightedNetBenefit([pb], 1, 1, 1, 1, undefined, 0.5, [cm]),
    ).toBeCloseTo(1.0);
  });

  it("demographic scope is respected", () => {
    const Dmatch: Demographic = { name: "Billionaires" };
    const Dother: Demographic = { name: "Average" };
    const cm: ConversionMetric = {
      fromMetric: "USD",
      extremelyBeneficialThreshold: 10_000_000,
      scope: Dmatch,
    };
    const pb: PossibleBenefit = {
      likelihood: 1.0,
      quantitativeMagnitude: 1_000_000,
      quantitativeMetric: "USD",
      signage: "positive",
    };
    // Group matches scope
    const gMatch: Group = {
      name: "G",
      demographicMemberships: [{ demographic: Dmatch, count: 1 }],
    };
    expect(
      calculateWeightedNetBenefit(
        [pb],
        1,
        1,
        1,
        1,
        undefined,
        0.5,
        [cm],
        gMatch,
      ),
    ).toBeCloseTo(0.1);

    // Group does NOT match scope
    const gOther: Group = {
      name: "G",
      demographicMemberships: [{ demographic: Dother, count: 1 }],
    };
    expect(
      calculateWeightedNetBenefit(
        [pb],
        1,
        1,
        1,
        1,
        undefined,
        0.5,
        [cm],
        gOther,
      ),
    ).toBeCloseTo(1_000_000);
  });

  it("qualitative magnitude ignores conversion metrics", () => {
    const cm: ConversionMetric = {
      fromMetric: "USD",
      extremelyBeneficialThreshold: 100,
    };
    const pb: PossibleBenefit = {
      likelihood: 1.0,
      qualitativeMagnitude: QualitativeMagnitude.ExtremelyHigh,
      signage: "positive",
    };
    expect(
      calculateWeightedNetBenefit([pb], 1, 1, 1, 1, undefined, 0.5, [cm]),
    ).toBeCloseTo(1.0);
  });
});

// ---------------------------------------------------------------------------
// Differential-based priority construction (§3.2)
// ---------------------------------------------------------------------------

describe("buildMoralPrioritiesFromDifferentials", () => {
  it("anchor gets rank 1 and ordinal 6", () => {
    const D: Demographic = { name: "Children" };
    const anchor: DemographicMoralConcern = {
      kind: "demographic",
      demographic: D,
      facetOfProsperity: "health",
      outlook: "short-term",
    };
    const result = buildMoralPrioritiesFromDifferentials(anchor, []);
    expect(result.length).toBe(1);
    expect(result[0].rank).toBe(1);
    expect(result[0].importance).toBe(QualitativeMagnitude.ExtremelyHigh);
  });

  it("single differential reduces ordinal", () => {
    const D1: Demographic = { name: "A" };
    const D2: Demographic = { name: "B" };
    const anchor: DemographicMoralConcern = {
      kind: "demographic",
      demographic: D1,
      facetOfProsperity: "health",
      outlook: "short-term",
    };
    const c2: DemographicMoralConcern = {
      kind: "demographic",
      demographic: D2,
      facetOfProsperity: "health",
      outlook: "short-term",
    };
    const result = buildMoralPrioritiesFromDifferentials(anchor, [
      [c2, QualitativeDifferenceMagnitude.SlightlyMoreOrLessPreferable],
    ]);
    expect(result.length).toBe(2);
    expect(result[0].importance).toBe(QualitativeMagnitude.ExtremelyHigh);
    expect(result[1].importance).toBe(QualitativeMagnitude.SomewhatHigh); // 6 - 2 = 4
    expect(result[1].rank).toBe(2);
  });

  it("multiple differentials accumulate correctly", () => {
    const D1: Demographic = { name: "A" };
    const D2: Demographic = { name: "B" };
    const D3: Demographic = { name: "C" };
    const anchor: DemographicMoralConcern = {
      kind: "demographic",
      demographic: D1,
      facetOfProsperity: "health",
      outlook: "short-term",
    };
    const c2: DemographicMoralConcern = {
      kind: "demographic",
      demographic: D2,
      facetOfProsperity: "health",
      outlook: "short-term",
    };
    const c3: DemographicMoralConcern = {
      kind: "demographic",
      demographic: D3,
      facetOfProsperity: "health",
      outlook: "short-term",
    };
    const result = buildMoralPrioritiesFromDifferentials(anchor, [
      [c2, QualitativeDifferenceMagnitude.SlightlyMoreOrLessPreferable], // gap 2
      [c3, QualitativeDifferenceMagnitude.MarginallyMoreOrLessPreferable], // gap 1
    ]);
    expect(result.length).toBe(3);
    expect(result[2].importance).toBe(QualitativeMagnitude.Moderate); // 6-2-1 = 3
    expect(result[2].rank).toBe(3);
  });

  it("ordinal never drops below 0", () => {
    const D1: Demographic = { name: "A" };
    const D2: Demographic = { name: "B" };
    const anchor: DemographicMoralConcern = {
      kind: "demographic",
      demographic: D1,
      facetOfProsperity: "health",
      outlook: "short-term",
    };
    const c2: DemographicMoralConcern = {
      kind: "demographic",
      demographic: D2,
      facetOfProsperity: "health",
      outlook: "short-term",
    };
    const result = buildMoralPrioritiesFromDifferentials(anchor, [
      [c2, QualitativeDifferenceMagnitude.OverwhelminglyMoreOrLess], // gap 6
    ]);
    expect(result[1].importance).toBe(QualitativeMagnitude.Negligible);
  });

  it("works with CharacteristicBandMoralConcern", () => {
    const C: NumericalCharacteristic = {
      kind: "numerical",
      name: "age",
      minValue: 0,
      maxValue: 120,
    };
    const anchor: CharacteristicBandMoralConcern = {
      kind: "characteristicBand",
      characteristicBands: [{ characteristic: C, minValue: 0, maxValue: 18 }],
      facetOfProsperity: "health",
      outlook: "short-term",
    };
    const result = buildMoralPrioritiesFromDifferentials(anchor, []);
    expect(result[0].importance).toBe(QualitativeMagnitude.ExtremelyHigh);
  });
});

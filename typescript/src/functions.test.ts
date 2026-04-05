import { calculateWeightedNetBenefit } from "./functions";
import { PossibleBenefit, QualitativeMagnitude } from "./types";

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

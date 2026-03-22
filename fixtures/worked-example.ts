/**
 * objectifiabilist/fixtures/worked-example.ts
 *
 * Typed TypeScript re-export of the canonical worked example fixture.
 * This file exists to give TypeScript consumers IDE support and compile-time
 * type checking. The JSON file is the runtime source consumed by both packages.
 *
 * To regenerate worked-example.json from this file:
 *   npx ts-node -e "import w from './worked-example'; console.log(JSON.stringify(w, null, 2))" > worked-example.json
 */

import {
  QualitativeMagnitude,
  QualitativePreferability,
  type Dilemma,
  type Ethic,
} from "../types";

// ---------------------------------------------------------------------------
// Ethic
// ---------------------------------------------------------------------------

export const WORKED_EXAMPLE_ETHIC: Ethic = {
  name: "Worked Example Ethic",
  optimismBias: 0,
  conversionMetrics: [
    {
      fromMetric: "USD",
      extremelyBeneficialThreshold: 100_000,
    },
    {
      fromMetric: "USD",
      extremelyBeneficialThreshold: 10_000_000,
      scope: {
        name: "Demographic 4",
        booleanValues: [
          {
            characteristic: { name: "Characteristic 1", kind: "boolean" },
            value: true,
          },
        ],
        stringValues: [
          {
            characteristic: {
              name: "Characteristic 2",
              kind: "string",
              possibleValues: ["2A", "2B", "2C"],
            },
            value: "2C",
          },
        ],
        numericalBands: [
          {
            characteristic: {
              name: "Characteristic 3",
              kind: "numerical",
              minValue: 0,
              maxValue: 100,
            },
            minValue: 20,
            maxValue: 60,
          },
        ],
      },
    },
  ],
  moralPriorities: [
    {
      moralConcern: {
        kind: "demographic",
        demographic: {
          name: "Demographic 1",
          numericalBands: [
            {
              characteristic: {
                name: "Characteristic 3",
                kind: "numerical",
                minValue: 0,
                maxValue: 100,
              },
              minValue: 0,
              maxValue: 20,
            },
          ],
        },
        facetOfProsperity: "health",
        outlook: "short-term",
      },
      importance: QualitativeMagnitude.ExtremelyHigh,
    },
    {
      moralConcern: {
        kind: "demographic",
        demographic: {
          name: "Demographic 1",
          numericalBands: [
            {
              characteristic: {
                name: "Characteristic 3",
                kind: "numerical",
                minValue: 0,
                maxValue: 100,
              },
              minValue: 0,
              maxValue: 20,
            },
          ],
        },
        facetOfProsperity: "health",
        outlook: "long-term",
      },
      importance: QualitativeMagnitude.ExtremelyHigh,
    },
    {
      moralConcern: {
        kind: "demographic",
        demographic: {
          name: "Demographic 2",
          booleanValues: [
            {
              characteristic: { name: "Characteristic 1", kind: "boolean" },
              value: false,
            },
          ],
          numericalBands: [
            {
              characteristic: {
                name: "Characteristic 3",
                kind: "numerical",
                minValue: 0,
                maxValue: 100,
              },
              minValue: 20,
              maxValue: 40,
            },
          ],
        },
        facetOfProsperity: "health",
        outlook: "short-term",
      },
      importance: QualitativeMagnitude.SomewhatHigh,
    },
    {
      moralConcern: {
        kind: "demographic",
        demographic: {
          name: "Demographic 3",
          booleanValues: [
            {
              characteristic: { name: "Characteristic 1", kind: "boolean" },
              value: true,
            },
          ],
          numericalBands: [
            {
              characteristic: {
                name: "Characteristic 3",
                kind: "numerical",
                minValue: 0,
                maxValue: 100,
              },
              minValue: 20,
              maxValue: 40,
            },
          ],
        },
        facetOfProsperity: "health",
        outlook: "short-term",
      },
      importance: QualitativeMagnitude.Moderate,
    },
    {
      moralConcern: {
        kind: "demographic",
        demographic: {
          name: "Demographic 4",
          booleanValues: [
            {
              characteristic: { name: "Characteristic 1", kind: "boolean" },
              value: true,
            },
          ],
          stringValues: [
            {
              characteristic: {
                name: "Characteristic 2",
                kind: "string",
                possibleValues: ["2A", "2B", "2C"],
              },
              value: "2C",
            },
          ],
          numericalBands: [
            {
              characteristic: {
                name: "Characteristic 3",
                kind: "numerical",
                minValue: 0,
                maxValue: 100,
              },
              minValue: 20,
              maxValue: 60,
            },
          ],
        },
        facetOfProsperity: "wealth",
        outlook: "short-term",
      },
      importance: QualitativeMagnitude.SomewhatLow,
    },
    {
      moralConcern: {
        kind: "characteristicBand",
        characteristicBands: [
          {
            characteristic: {
              name: "Characteristic 3",
              kind: "numerical",
              minValue: 0,
              maxValue: 100,
            },
            minValue: 20,
            maxValue: 40,
          },
          {
            characteristic: {
              name: "Characteristic 2",
              kind: "string",
              possibleValues: ["2A", "2B", "2C"],
            },
            value: "2A",
          },
        ],
        facetOfProsperity: "health",
        outlook: "short-term",
      },
      importance: QualitativeMagnitude.SomewhatHigh,
    },
  ],
};

// ---------------------------------------------------------------------------
// Dilemma
// ---------------------------------------------------------------------------

const C3 = {
  name: "Characteristic 3",
  kind: "numerical" as const,
  minValue: 0,
  maxValue: 100,
};
const C2 = {
  name: "Characteristic 2",
  kind: "string" as const,
  possibleValues: ["2A", "2B", "2C"],
};
const C1 = { name: "Characteristic 1", kind: "boolean" as const };

const D1 = {
  name: "Demographic 1",
  numericalBands: [{ characteristic: C3, minValue: 0, maxValue: 20 }],
};
const D2 = {
  name: "Demographic 2",
  booleanValues: [{ characteristic: C1, value: false }],
  numericalBands: [{ characteristic: C3, minValue: 20, maxValue: 40 }],
};
const D3 = {
  name: "Demographic 3",
  booleanValues: [{ characteristic: C1, value: true }],
  numericalBands: [{ characteristic: C3, minValue: 20, maxValue: 40 }],
};
const D4 = {
  name: "Demographic 4",
  booleanValues: [{ characteristic: C1, value: true }],
  stringValues: [{ characteristic: C2, value: "2C" }],
  numericalBands: [{ characteristic: C3, minValue: 20, maxValue: 60 }],
};

const GROUP1 = {
  name: "Group 1",
  demographicMemberships: [
    { demographic: D1, count: 3 },
    { demographic: D2, count: 1 },
    { demographic: D3, count: 1 },
  ],
};
const GROUP2 = {
  name: "Group 2",
  individuals: Array(6).fill({
    numericalValues: [{ characteristic: C3, value: 30 }],
  }),
};
const GROUP3 = {
  name: "Group 3",
  demographicMemberships: [{ demographic: D4, count: 1 }],
};
const GROUP4 = {
  name: "Group 4",
  individuals: [
    {
      stringValues: [{ characteristic: C2, value: "2A" }],
      numericalValues: [{ characteristic: C3, value: 30 }],
    },
  ],
};

export const WORKED_EXAMPLE_DILEMMA: Dilemma = {
  name: "Autonomous Vehicle Collision Dilemma",
  choices: [
    {
      name: "Choice 1",
      description:
        "Collide with Group 2 (default: continue current trajectory)",
      effects: [
        {
          affectedGroup: GROUP1,
          facetOfProsperity: "health",
          outlook: "short-term",
          possibleBenefits: [
            {
              likelihood: 0.8,
              qualitativeMagnitude: QualitativeMagnitude.SomewhatHigh,
              signage: "negative",
            },
            {
              likelihood: 0.2,
              qualitativeMagnitude: QualitativeMagnitude.VeryHigh,
              signage: "negative",
            },
          ],
        },
        {
          affectedGroup: GROUP2,
          facetOfProsperity: "health",
          outlook: "short-term",
          possibleBenefits: [
            {
              likelihood: 0.6,
              qualitativeMagnitude: QualitativeMagnitude.ExtremelyHigh,
              signage: "negative",
            },
            {
              likelihood: 0.4,
              qualitativeMagnitude: QualitativeMagnitude.VeryHigh,
              signage: "negative",
            },
          ],
        },
      ],
    },
    {
      name: "Choice 2",
      description: "Collide with a stationary object",
      effects: [
        {
          affectedGroup: GROUP1,
          facetOfProsperity: "health",
          outlook: "short-term",
          possibleBenefits: [
            {
              likelihood: 0.9,
              qualitativeMagnitude: QualitativeMagnitude.VeryHigh,
              signage: "negative",
            },
            {
              likelihood: 0.1,
              qualitativeMagnitude: QualitativeMagnitude.ExtremelyHigh,
              signage: "negative",
            },
          ],
        },
      ],
    },
    {
      name: "Choice 3",
      description: "Collide with life-saving experimental technology",
      effects: [
        {
          affectedGroup: GROUP1,
          facetOfProsperity: "health",
          outlook: "short-term",
          possibleBenefits: [
            {
              likelihood: 0.8,
              qualitativeMagnitude: QualitativeMagnitude.SomewhatHigh,
              signage: "negative",
            },
            {
              likelihood: 0.2,
              qualitativeMagnitude: QualitativeMagnitude.VeryHigh,
              signage: "negative",
            },
          ],
        },
        {
          affectedGroup: GROUP3,
          facetOfProsperity: "wealth",
          outlook: "short-term",
          possibleBenefits: [
            {
              likelihood: 0.7,
              quantitativeMagnitude: 0.0007,
              quantitativeMetric: "normalized",
              signage: "negative",
            },
            {
              likelihood: 0.2,
              quantitativeMagnitude: 0.0014,
              quantitativeMetric: "normalized",
              signage: "negative",
            },
            {
              likelihood: 0.1,
              quantitativeMagnitude: 0.0028,
              quantitativeMetric: "normalized",
              signage: "negative",
            },
          ],
        },
        {
          affectedGroup: GROUP3,
          facetOfProsperity: "wealth",
          outlook: "long-term",
          possibleBenefits: [
            {
              likelihood: 0.5,
              quantitativeMagnitude: 0.0,
              quantitativeMetric: "normalized",
              signage: "zero",
            },
            {
              likelihood: 0.5,
              quantitativeMagnitude: 0.28,
              quantitativeMetric: "normalized",
              signage: "negative",
            },
          ],
          chainEffects: [
            {
              affectedGroup: GROUP1,
              facetOfProsperity: "health",
              outlook: "long-term",
              possibleBenefits: [
                {
                  likelihood: 0.3,
                  qualitativeMagnitude: QualitativeMagnitude.VeryHigh,
                  signage: "negative",
                },
                {
                  likelihood: 0.7,
                  qualitativeMagnitude: QualitativeMagnitude.Negligible,
                  signage: "zero",
                },
              ],
            },
            {
              affectedGroup: GROUP2,
              facetOfProsperity: "health",
              outlook: "long-term",
              possibleBenefits: [
                {
                  likelihood: 0.4,
                  qualitativeMagnitude: QualitativeMagnitude.SomewhatHigh,
                  signage: "negative",
                },
                {
                  likelihood: 0.6,
                  qualitativeMagnitude: QualitativeMagnitude.Negligible,
                  signage: "zero",
                },
              ],
            },
          ],
        },
      ],
    },
    {
      name: "Choice 4",
      description: "Collide with Group 4 fatally",
      effects: [
        {
          affectedGroup: GROUP4,
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
    },
  ],
};

// ---------------------------------------------------------------------------
// Stated preferabilities (for divergence signal calculation)
// ---------------------------------------------------------------------------

export const WORKED_EXAMPLE_STATED_PREFERABILITIES: Array<{
  choiceName: string;
  statedPreferability: QualitativePreferability;
}> = [
  {
    choiceName: "Choice 1",
    statedPreferability: QualitativePreferability.ExtremelyUnpreferable,
  },
  {
    choiceName: "Choice 2",
    statedPreferability: QualitativePreferability.SomewhatPreferable,
  },
  {
    choiceName: "Choice 3",
    statedPreferability: QualitativePreferability.SomewhatUnpreferable,
  },
  {
    choiceName: "Choice 4",
    statedPreferability: QualitativePreferability.ExtremelyUnpreferable,
  },
];

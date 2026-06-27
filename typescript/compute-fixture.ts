import {
  calculateAllMoralValences,
  calculatePreferabilities,
  inferMoralPriorities,
  calculateMoralPriorityDivergenceSignal,
} from "./src/functions";
import {
  WORKED_EXAMPLE_DILEMMA,
  WORKED_EXAMPLE_ETHIC,
} from "../fixtures/worked-example.ts";
import {
  Dilemma,
  Ethic,
  QualitativePreferability,
  MoralPriority,
  StatedPreferability,
} from "./src/types";

const dilemma = WORKED_EXAMPLE_DILEMMA as unknown as Dilemma;
const ethic = WORKED_EXAMPLE_ETHIC as unknown as Ethic;
const stated: StatedPreferability[] = [
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

const valences = calculateAllMoralValences(dilemma, ethic);
console.log("VALENCES:", JSON.stringify(valences));
const prefs = calculatePreferabilities(valences);
console.log("PREFS:", JSON.stringify(prefs));
const inferred = inferMoralPriorities(dilemma, stated);
console.log("INFERRED_COUNT:", inferred.length);
const signal = calculateMoralPriorityDivergenceSignal(
  ethic.moralPriorities as unknown as MoralPriority[],
  inferred,
);
console.log("MAD:", signal.meanAbsoluteDivergence);
const results = signal.perConcern.map((r: any) => {
  const k =
    r.moralConcern.kind === "demographic"
      ? "demographic|" +
        r.moralConcern.facetOfProsperity +
        "|" +
        r.moralConcern.outlook +
        "|" +
        r.moralConcern.demographic.name
      : "characteristicBand|" +
        r.moralConcern.facetOfProsperity +
        "|" +
        r.moralConcern.outlook +
        "|" +
        r.moralConcern.characteristicBands
          .map((b: any) => {
            if ("value" in b && typeof b.value === "boolean")
              return "bool:" + b.characteristic.name + "=" + b.value;
            if ("value" in b && typeof b.value === "string")
              return "str:" + b.characteristic.name + "=" + b.value;
            return (
              "num:" +
              b.characteristic.name +
              ":[" +
              b.minValue +
              ".." +
              b.maxValue +
              "]"
            );
          })
          .sort()
          .join(";");
  return {
    key: k,
    purportedImportance: r.purportedImportance,
    inferredImportance: r.inferredImportance,
    signedDivergence: r.signedDivergence,
    absoluteDivergence: r.absoluteDivergence,
  };
});
console.log("PERCONCERN:", JSON.stringify(results));

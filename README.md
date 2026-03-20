# objectifiabilist

**A moral calculus engine.** Pure functions for quantifying the preferability of choices in moral dilemmas, inferring moral priorities from assessments of those choices, and auditing the consistency between the two.

This package does not prescribe choices or moral frameworks. It makes the moral priorities implicit in any ethical judgment explicit, calculable, and comparable.

---

## Background

Every moral dilemma requires a choice, and every choice allocates unequal benefit across the groups at stake. Any ethic that prescribes a choice in a dilemma therefore implicitly encodes moral priorities — relative weightings of whose welfare matters, along which facets of prosperity, and over what time horizon. These priorities are an invariant of moral reasoning across all ethical traditions, not a preference of any particular one.

**Objectifiabilism** is the metaethical framework that formalizes this observation. Given a moral dilemma and a set of moral priorities, the relative preferability of each available choice is calculable. Inversely, given a moral dilemma and an assessment of the preferabilities of choices, the moral priorities implied by that assessment are inferable. The divergence between purported priorities and those implied by purported preferabilities — or vice versa — is quantifiable. Consensus on that divergence is a vector for approximating moral objectivity.

The full theoretical treatment is in the [white paper](./white-paper.md).

---

## Installation

```bash
# TypeScript / JavaScript
npm install objectifiabilist

# Python
pip install objectifiabilist
```

---

## Quick Start

The core workflow: construct a scenario, declare an ethic, calculate moral valences, and compare them to intuitive assessments.

### TypeScript

```typescript
import {
  calculateMoralWorthOfChoice,
  getMostMoralChoiceInScenario,
  generateDivergenceSignal,
} from "objectifiabilist";

const moralValence = calculateMoralWorthOfChoice(choice, ethic);
const prescription = getMostMoralChoiceInScenario(scenario, ethic);
const divergence = generateDivergenceSignal(
  intuitivePreferabilities,
  calculatedPreferabilities,
);
```

### Python

```python
from objectifiabilist import (
    calculate_moral_worth_of_choice,
    get_most_moral_choice_in_scenario,
    generate_divergence_signal,
)

moral_valence = calculate_moral_worth_of_choice(choice, ethic)
prescription = get_most_moral_choice_in_scenario(scenario, ethic)
divergence = generate_divergence_signal(
    intuitive_preferabilities,
    calculated_preferabilities,
)
```

A fully worked example — with a four-choice trolley-dilemma variant, complete effect distributions, moral priority declarations, and divergence calculations — is in the [white paper](./white-paper.md#worked-example).

---

## Key Concepts

| Term                  | Definition                                                                                                                                                                                     |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Moral dilemma**     | Any situation in which a moral agent must choose between two or more choices, where indecision counts as a choice                                                                              |
| **Effect**            | A probability distribution of benefit for a particular group along a facet of prosperity in the short-term or long-term                                                                        |
| **Ethic**             | A set of moral priorities, an optimism bias, and conversion metrics for benefit                                                                                                                |
| **Moral priority**    | The importance of concentrating net-benefit for a particular moral concern relative to other moral concerns                                                                                    |
| **Moral valence**     | The magnitude and signage of a choice's moral significance, computed from the weighted sum of the moral values of its effects                                                                  |
| **Divergence signal** | The absolute difference between a purported assessment and what that assessment implies — either between stated priorities and the priorities implied by stated preferabilities, or vice versa |

The full glossary is in the [white paper](./white-paper.md#glossary).

---

## Repo Structure

```
objectifiabilist/
├── typescript/          # npm package source
├── python/              # PyPI package source
├── white-paper.md       # Full theoretical treatment, schema reference, and worked example
└── README.md
```

Both packages implement the same functions from the same schema. TypeScript is the source of truth for type definitions; the Python package mirrors them as Pydantic models.

---

## What This Package Is Not

- It does not prescribe choices. It calculates the preferabilities that a given ethic implies for a given dilemma.
- It does not privilege any ethical tradition. Consequentialist, deontological, Rawlsian, care-based, and virtue-ethical reasoning are all representable within the schema.
- It does not declare anyone's objective moral worth. It lets users declare the criteria by which they weight groups, shows the implications of applying those criteria consistently, and enables structured debate about the criteria themselves.

---

## Contributing

Contributions are welcome. Before opening a pull request:

1. Ensure all tests pass in both the `typescript/` and `python/` packages.
2. If modifying a type, update both packages. TypeScript is the source of truth; Python types should be regenerated accordingly.
3. If adding a function, include it in both packages and add a shared fixture to the parity test suite.
4. Keep functions pure. No side effects, no I/O, no global state.

The [white paper](./white-paper.md) is the specification. If a function's behavior is ambiguous, the white paper is authoritative.

---

## License

MIT

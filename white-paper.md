# The Invariance of Moral Calculus

**Version 1.0** | Shaker Funkhouser

---

## Executive Summary

Construing every moral dilemma as a variation of the Trolley Dilemma forces any ethic to prescribe a choice therein, revealing implicit moral priorities. Quantitative metrics of benefit enable invariantly quantifying the relative importances of these moral priorities. Comparing purported moral priorities to those implied by purported preferabilities of choices in a moral dilemma quantifiably signals consistency. Likewise, given a moral dilemma and a set of moral priorities, it becomes possible to invariantly calculate the relative preferability of the choices available. Comparing purported preferabilities of choices to those implied by a set of moral priorities generates another quantitative signal of consistency.

These metaethical observations have been formalized in a framework called **"Objectifiabilism,"** which does not prescribe choices, but rather hopes to facilitate approximation of moral objectivity by making moral priorities explicit, auditable, comparable and subject to consensus. Preliminary algorithms for these moral calculations will be modeled as pure functions in open-source npm and PyPi packages, both titled **"objectifiabilist."** Applications of these algorithms span both private and non-profit sectors extensively.

---

## Background

Ethical debate is intrinsic to human nature, driving internal and external conflict over what state of the world to progress to. Much upliftment has been derived from discerning virtues, categorical imperatives, duties of care, and so forth. Yet, in practice any ethic must prescribe a single choice in any particular moral dilemma.

The Trolley Dilemma thought-experiment[^1][^2], for instance, forces a decision as to which of two groups of people must be run over by an unstoppable oncoming train. By varying the number of groups at stake, the number of persons in each group, the characteristics of the people that differentiate each group, and the degree of net-benefit to be possibly experienced by each group, it becomes possible to frame **any moral dilemma as a variation of the Trolley Dilemma**. Indeed, autonomous vehicles become very much like unstoppable "trolleys" when a collision becomes inevitable[^3]: which group of people should they collide with and why? In terms of legislation, which groups should incur inconvenience so that others can enjoy a particular minimum standard of living? When waging war, what ratio of collateral damage to strategic advantage is acceptable? Even minor choices are moral dilemmas: eating candy might be wonderful in the short-term, but might end up being quite deleterious in the long-term.

Unfortunately, any choice in any moral dilemma is liable to condemn some groups to benefit less or suffer more than others. Prescribing any particular choice therefore necessarily imputes to the parties at stake unequal desert of net-benefit, implying moral priorities on the basis of factors that differentiate the parties at stake. In order to be consistent and even "objective," any ethic must invoke the same set of such moral priorities when prescribing choices for any moral dilemma. Thus, if one knows an ethic's moral priorities, it should be possible to predict that ethic's prescription for any particular moral dilemma. Likewise, if one knows an ethic's prescription for a moral dilemma, it should be possible to infer that ethic's set of moral priorities. In other words, **moral calculations proceed invariantly, however intuitively**.

---

## Problem Statement

Evaluating the morality of conduct tends to be an intuitive, implicit, qualitative and reflexive exercise. Such imprecision necessarily vitiates ethical debate. Auditing compliance with responsibilities likewise becomes fraught with vaguery and discretion. Similarly, auditing the consistency with which behavioral prescriptions evince their purported motivations becomes fraught with plausible deniability. If, however, the morality of choices can be expressed quantitatively, auditing compliance with and consistency of responsibilities becomes much more precise.

---

## Solution

This white paper will show that the preferabilities of choices can indeed be quantified invariantly for any particular ethic. As a starting point, it makes sense to schematize the mental constructs involved in moral reasoning:

- A **moral dilemma** involves two or more choices available to a moral agent.
- Each **choice** entails one or more effects.
- Each **effect** entails a distribution of possible benefits for a particular group at stake, as well as cascading chain effects. Each choice does not need to specify an effect for each group at stake, which implicitly assigns to omitted groups a 100% likelihood of experiencing zero benefit.
- Each **possible benefit** affects a particular facet of prosperity, and entails a likelihood (even if qualitative), a magnitude (even if qualitative), a signage (positive, negative or zero), and an outlook (which could be as simple as "short-term" vs "long-term").
- Every **moral priority** of an ethic identifies a moral concern, and associates with it a weight of importance (even if qualitative).
- Each **moral concern** identifies a prosperity facet, an outlook, and either a demographic or a set of importance weights for inclusive characteristic value bands (even if these weights are qualitative).
- A **demographic** is demarcated by values for boolean characteristics and by inclusive value bands for numerical and string characteristics.
- **Groups** in moral dilemmas can specify their representation in particular demographics or can list individuals with particular values for characteristics.
- An **ethic** indicates an optimism bias (the extent to which the magnitudes of effects are more pertinent than their likelihoods), and enumerates moral priorities and conversion metrics for benefit (to standardize different quantifications of benefit, optionally scoped to relevant demographics to reflect different perspectives on the scale of benefit).

An ethic could also enumerate categorical prohibitions to accommodate Kantian deontology[^4], thereby assigning minimal moral valence to choices that entail proscribed behaviors. Yet, if every choice in a moral dilemma were to entail a proscribed behavior (including inaction), the ethic would have to encode moral priorities by which to determine the relative preferability of the choices available regardless. In other words, even Kantianism does not, in fact, proscribe behaviors categorically so much as it assigns extremely high importance to moral concerns like freedom from violence.

At any rate, if all of the qualitative considerations cognized in this schema can be expressed quantitatively, it should be possible to execute moral calculations. In particular, if moral priority and the magnitudes and likelihoods of benefits can be quantified, it should be possible to calculate the moral value of an effect therefrom. Likewise, the moral valence of a choice should be calculable from the moral values of its effects. The distance between moral valences of choices can indicate their (ranked) preferability. The choice with the highest preferability becomes the ethic's prescription.

If this schema has merit (accurately capturing the irrevocability of moral priorities), then debate about the objectivity of an ethic then becomes about the justifications for its moral priorities, its conversions for metrics of benefits, and its optimism bias. Once an ethic is agreed to, ethical debate becomes about the details of any particular scenario: _"What choices are available to the agent? What are the effects of each choice? What group is affected by each effect? What are the likelihood, magnitude, signage, outlook, facet of prosperity and chain effects for each effect?"_ In other words, if the details (framing) of a scenario can be agreed to by two moral judges employing the same ethic, the preferability of each choice should be calculable invariantly, even if intuitively or qualitatively. Quantitative values are more actionable and lend more accountability, and so are worth explicating.

### Qualitative Scales

This framework assumes the following qualitative scaled enums:

**For expressing the magnitude of a benefit, the likelihood of a benefit, or the importance of a moral priority:**

| Ordinal | Label          |
| ------- | -------------- |
| 7       | Extremely high |
| 6       | Very high      |
| 5       | Somewhat high  |
| 4       | Moderate       |
| 3       | Somewhat low   |
| 2       | Very low       |
| 1       | Negligible     |

**For expressing the preferability of a choice:**

| Ordinal | Label                  |
| ------- | ---------------------- |
| 7       | Extremely preferable   |
| 6       | Very preferable        |
| 5       | Somewhat preferable    |
| 4       | Neutral                |
| 3       | Somewhat unpreferable  |
| 2       | Very unpreferable      |
| 1       | Extremely unpreferable |

Qualitative scales for the moral value of an effect and the moral valence of a choice are not needed; rather, most people's entry point will be to express the preferability of choices qualitatively in relation to each other.

### Quantifying Qualitative Values

Fortunately, qualitative expressions of scale can be normalized, and thus quantified as percentages of the maximum possible value. In other words, the quantitative equivalent for each classification becomes its ordinal value (order) divided by the total number of classifications. For example, "extremely detrimental" becomes $(1/7) = 0.14$; "very detrimental" becomes $(2/7) = 0.29$; and so on, all the way to $7/7 = 1$ for "extremely beneficial." Note, however, that this approach assumes equal intervals of magnitude between qualitative values for simplicity. In future, ethics could specify, for example, greater distance between "Very high" and "Extremely high" than between "Negligible" and "Very low."

Importance could also be calculated inversely from rankings: adding one to the total number of rankings minus the actual ranking, then dividing by the total number of rankings for each moral concern would produce the weighted importance of each concern. For example, if there are ten rankings, the highest ranked moral concern would have an importance of $(1 + 10 - 1)/10 = 1$; the lowest ranking moral concern would have an importance of $(1 + 10 - 10)/10 = 0.1$. This would, however, express equal distances between importances. In reality, one group's prosperity facet for a particular outlook could be much, much more important than another's, in which case leveraging qualitative categories of relative importance would produce more germane results. If instead moral priorities weight the importance of certain values or bands of values for characteristics, then the importance of an individual in a group becomes a sum of the importances associated with that individual's values for these characteristics. The importance of a group then becomes a sum of the importances of its individual members.

### Quantifying Benefit

Since the myriad products and services one might benefit from have a cost and a price, the benefit of having or not having access to a product or service can be represented by its price, positively or negatively respectively. Unsurprisingly, there are many precedents for quantifying benefit monetarily:

- Actuaries for health insurance companies price the risk of paying for medical treatment.
- Courts use formulas to estimate damages arising from opportunity cost and emotional distress.
- The United States Code and the Code of Federal Regulations codify the benefit formulas used by various federal programs.
- The US Department of Health and Human Services (HHS) estimates the current Value of a Statistical Life at **$13.7 million** for purposes of regulatory cost-benefit analysis.[^7]
- The UK’s National Institute for Health and Care Excellence uses the **Quality-Adjusted Life Year** metric[^8] to determine if a medical treatment provides “value for money” for the National Health Service.

Benefit is liable to have various other metrics in addition to percentages of qualitative scale and USD: lives lost or saved, productivity gained or lost, net change in satisfaction, and so forth. An ethic can therefore provide a means of converting between all metrics relevant to a dilemma so as to standardize calculations. Of course, we can also expect different demographics to perceive the scale of benefit differently: whereas the average person would probably consider gaining $100k to be "extremely beneficial," a billionaire would probably instead consider gaining $100M to be "extremely beneficial." In that case, the "wealth" prosperity-facet can be reframed as "percent of net-worth gained or lost," which standardizes benefit across income ranges. Alternatively, an ethic can scope overriding conversions of metrics of benefit to relevant groups.

### Calculating Weighted Net-Benefit

Summing the possible benefits in an effect's distribution and weighting each possible benefit by its likelihood produces the **weighted net-benefit** of the effect. For example, if gaining $100k is "extremely beneficial" by default, and if an effect has a 60% chance of costing someone $20k and a 40% chance of instead being "very beneficial" to the same person, the weighted net-benefit becomes:

$$(0.6)(-\$20k) + (0.4)(\$100k)(6/7) = \$22.29$$

An optimism bias of 0 would leave that calculation as is, but an optimism bias of 1 would effectively disregard the possibility of losing $20k. Adjusting the weights for each benefit to reflect optimism bias is a candidate for monotonic transformation parameterized by an optimism scalar. Since effects can have chain effects, the weighted net-benefit of chained effects must recursively factor into the overall weighted net-benefit of root effects.

### Calculating Moral Value

Multiplying the weighted net-benefit of an effect by the importance of the affected moral concern produces the **moral value of the effect**. If the details of an effect map cleanly to a moral concern (by matching the prosperity facet of the affected group for the specified outlook), then quantifying the qualitative importance of that moral concern is straightforward. If all characteristic value bands for a group member satisfy those specified by a demographic, that group member counts as a member of that demographic even if that group member does not specify value bands for the remaining characteristics of that demographic. A group can therefore specify the amount of members it has in each demographic, whereby the importance of that group becomes a sum of the multiplications of the importance of each demographic by the number of people that fit that demographic. The situation becomes more complicated, though, if a group member does not fit into a demographic, in which case the importance of this person's value bands for characteristics given importances by the ethic sum to produce the importance of the person. A group member effectively has no importance if the ethic does not assign importance to that group member's characteristic values or if that group member does not fit into any demographics that the ethic has assigned importance to (the forthcoming worked example will be inexhaustive for simplicity).

### Calculating Moral Valence

Since a single choice can have many effects, the **moral valence** of the choice becomes the sum of the moral values of its effects (or the sum of the weighted net-benefits of its effects, where each term is again weighted by the quantitative importance of the moral concern that each effect affects). Note also that applying a Rawlsian Veil of Ignorance[^5] argues for construing the moral value of a choice to be how well it maximizes the well-being of the least advantaged group in society. An ethic could therefore additionally customize a function that calculates the moral value of a choice given the starting state of groups, thereby overriding the default approach of calculating a sum of moral values of effects. This does not seem necessary, however, since the spirit of this "maximin" principle can be modeled as follows:

- "Advantage" is both a characteristic and a prosperity facet whose value bands are "least advantaged ... most advantaged."
- The operating ethic places slightly more importance on its moral concern for the "advantage" of demographics and individuals whose "advantage" begins in the "least advantaged" state.
- The operating ethic places slightly lower importance for the "advantage" of demographics and individuals whose "advantage" begins with higher ordinal values (perhaps proportionally so), but not necessarily so low as to prescribe choices that equalize the "advantage" of all groups in an effort to avoid imposing even marginal detriment to the least advantaged group (a "leveling-down" scenario[^6]).
- Chain effects capture the "economic linkages" by which less advantaged groups benefit long-term from more advantaged groups benefiting in the short-term.

### Preferability and Divergence

Ultimately, the distances between the moral valences of choices express the **relative preferability** of these choices. In particular, the prescribed choice can represent the maximum possible good achievable in the scenario, and the choice with the lowest moral value represents the minimum possible good achievable in the scenario. This maximum and minimum can be mapped to the maximum and minimum ordinal value of the preferability enum, where all other choices fall into equally wide buckets in between.

If users assign different preferabilities to choices than what their ethic predicts, the absolute difference between ordinal values of these preferabilities generates a **divergence signal**, which invites moral reflection, and, more pertinently, enables auditing the behavior of prescribers and ostensible abiders of prescriptions in a consistent, transparent fashion. Inverting this logic likewise allows inferring moral priorities from evaluations of the preferabilities of choices. Similarly, any divergence between purported moral priorities and those implied by preferabilities of choices signals inconsistency, invites reflection, and enables auditing.

Since the details of moral dilemmas are subject to speculation, and since the moral priorities inherent to ethics have yet to be widely acknowledged — let alone formalized — morality seems constrained to subjectivity. Nevertheless, consensus regarding moral priorities and likelihoods for benefit magnitudes in moral dilemmas are vectors for approximating moral objectivity — perhaps perfectly. This ethos and all the aforementioned insights that inform it are hereby formalized into a constructivist metaethical framework called **"Objectifiabilism."** Note that this framework does not prescribe choices, but rather explicates, audits, and compares moral priorities. The algorithms herein will be modeled as pure functions in an npm package and a PyPi package, both of which will be called **"objectifiabilist"** and will operate under an open-source MIT license. A worked example is provided herein as a template for such functionality.

---

## Conclusion

Since any choice in any moral dilemma is liable to affect moral concerns unequally, and since all ethics must prescribe a single choice in any moral dilemma, all ethics implicitly encode moral priorities. Since benefit and importance can be quantified, the preferabilities of choices in a moral dilemma can be calculated invariantly for any ethic. The quantifiable divergence between two evaluations of moral preferabilities for the same set of choices can meaningfully signal inconsistency or disagreement. Inversely, moral priorities can be invariantly inferred from evaluations of the moral preferabilities of choices for a moral dilemma. Likewise, the quantifiable divergence between two sets of moral priorities can meaningfully signal inconsistency or disagreement.

Applications of such algorithms span both public and private sectors, but, most pertinently, clarify ethical debates as being disagreements about **moral priorities**, **the role of optimism**, and **framings for moral dilemmas**. Consensus on these sources of disagreement can eventually approximate moral objectivity. The constructivist metaethical framework that captures this spirit and procedure is hereby called **"Objectifiabilism."**

---

## Call to Action

There are many vectors by which to refine Objectifiabilism. In the first place, future work should accommodate epistemic uncertainty regarding the executability of choices, demographic representation, and values for characteristics. Until real-world applications evince the need for such specificity, however, the current incarnation of the schema should suffice for validating the central concepts of Objectifiabilism (see the [Worked Example](#worked-example) section for a demonstration).

- **Philosophers** are asked to test: the soundness of the claim that all ethics must implicitly or explicitly entail moral priorities; the ability of this schema to characterize any ethic; the ability of this schema to characterize any moral dilemma; and the helpfulness of this framework in structuring ethical debate more precisely.
- **Mathematicians** are invited to assess the pertinence of the mathematical approaches taken for moral calculations.
- **Software engineers** are invited to assess the efficiency and readability of the forthcoming open-source code, and to create pull requests for improvements.
- **AI alignment researchers** are invited to evaluate the usefulness of representing ethical behavior as explicit, auditable priority orderings.
- **Anyone concerned with public policy** is invited to assess the usefulness of this framework for enforcing and auditing public policy.

---

## Worked Example

To demonstrate this metaethic in action, consider the following instantiations (note that likelihoods are expressed quantitatively rather than qualitatively to avoid the difficulty of discerning qualitative probabilities that sum to 1):

### Setup

**Prosperity facets:**

- Health
- Wealth

**Default conversion of metrics for benefit:**

- $100k = "Extremely beneficial"

**Characteristics:**

| Characteristic   | Type      | Values            |
| ---------------- | --------- | ----------------- |
| Characteristic 1 | Boolean   | `true` or `false` |
| Characteristic 2 | String    | `2A`, `2B`, `2C`  |
| Characteristic 3 | Numerical | Min: 0, Max: 100  |

**Demographics:**

- **Demographic 1:** Any value for Characteristics 1 & 2; Characteristic 3 between **0–20**
- **Demographic 2:** Characteristic 1 = `false`; any value for Characteristic 2; Characteristic 3 between **20–40**
- **Demographic 3:** Characteristic 1 = `true`; any value for Characteristic 2; Characteristic 3 between **20–40**
- **Demographic 4:** Characteristic 1 = `true`; Characteristic 2 = `2C`; Characteristic 3 between **20–60**
  - Converts 1 hour of benefit → $50
  - Considers $10 million to be "extremely beneficial" _(overrides the default $100k = "extremely beneficial")_

### Ethic

**Moral priorities:**

| Priority | Moral Concern                                                                           | Prosperity Facet | Outlook    | Importance     |
| -------- | --------------------------------------------------------------------------------------- | ---------------- | ---------- | -------------- |
| 1        | Demographic 1                                                                           | Health           | Short-term | Extremely high |
| 2        | Demographic 1                                                                           | Health           | Long-term  | Extremely high |
| 3        | Demographic 2                                                                           | Health           | Short-term | Somewhat high  |
| 4        | Demographic 3                                                                           | Health           | Short-term | Moderate       |
| 5        | Demographic 4                                                                           | Wealth           | Short-term | Low            |
| 6        | Characteristic value bands: Characteristic 3 in [20–40] **and** Characteristic 2 = `2A` | Health           | Short-term | Somewhat high  |

**Optimism bias:** 0 (default)

### Groups at Stake

- **Group 1:** 3 members of Demographic 1; 1 member of Demographic 2; 1 member with Characteristic 1 = `true`, no Characteristic 2, and Characteristic 3 = 40 (qualifies for Demographic 3)
- **Group 2:** 6 members with Characteristic 3 in [20–40]
- **Group 3:** 1 member of Demographic 4
- **Group 4:** 1 member with Characteristic 3 = 30 and Characteristic 2 = `2A`

### Choices and Calculations

---

#### Choice 1 — Collide with Group 2 _(default: continue current trajectory)_

**Effect 1** — Group 1 | Health | Short-term

| Possibility                                   | Likelihood | Magnitude           | Signage  |
| --------------------------------------------- | ---------- | ------------------- | -------- |
| High likelihood of being somewhat detrimental | 80%        | Somewhat high (5/7) | Negative |
| Low likelihood of being very detrimental      | 20%        | Very high (6/7)     | Negative |

$$\text{Weighted net-benefit} = (0.8)(5/7)(-1) + (0.2)(6/7)(-1) = -0.74$$

| Moral Concern                      | Matching Priority | Importance           | Members | Total Importance |
| ---------------------------------- | ----------------- | -------------------- | ------- | ---------------- |
| Short-term health of Demographic 1 | 1                 | Extremely high (7/7) | 3       | $3(7/7) = 3$     |
| Short-term health of Demographic 2 | 3                 | Somewhat high (5/7)  | 1       | $1(5/7) = 0.71$  |
| Short-term health of Demographic 3 | 4                 | Moderate (4/7)       | 1       | $1(4/7) = 0.57$  |
| **Total**                          |                   |                      |         | **4.28**         |

$$\text{Moral value} = (-0.74)(4.28) = \mathbf{-3.17}$$

**Effect 2** — Group 2 | Health | Short-term

| Possibility                                             | Likelihood | Magnitude            | Signage  |
| ------------------------------------------------------- | ---------- | -------------------- | -------- |
| Somewhat high likelihood of being extremely detrimental | 60%        | Extremely high (7/7) | Negative |
| Somewhat low likelihood of being very detrimental       | 40%        | Very high (6/7)      | Negative |

$$\text{Weighted net-benefit} = (0.6)(7/7)(-1) + (0.4)(6/7)(-1) = -0.94$$

| Moral Concern                                                | Matching Priority | Importance          | Members | Total Importance |
| ------------------------------------------------------------ | ----------------- | ------------------- | ------- | ---------------- |
| Short-term health of people with Characteristic 3 in [20–40] | 6                 | Somewhat high (5/7) | 6       | $6(5/7) = 4.29$  |

$$\text{Moral value} = (4.29)(-0.94) = \mathbf{-4.03}$$

> **Moral valence of Choice 1: $-3.17 + (-4.03) = \mathbf{-7.20}$**

---

#### Choice 2 — Collide with a Stationary Object

**Effect 1** — Group 1 | Health | Short-term

| Possibility                                        | Likelihood | Magnitude            | Signage  |
| -------------------------------------------------- | ---------- | -------------------- | -------- |
| Very high likelihood of being very detrimental     | 90%        | Very high (6/7)      | Negative |
| Very low likelihood of being extremely detrimental | 10%        | Extremely high (7/7) | Negative |

$$\text{Weighted net-benefit} = (0.9)(6/7)(-1) + (0.1)(7/7)(-1) = -0.87$$

Total importance of moral concerns affected (same as Choice 1): **4.28**

$$\text{Moral value} = (-0.87)(4.28) = \mathbf{-3.72}$$

> **Moral valence of Choice 2: $\mathbf{-3.72}$**

---

#### Choice 3 — Collide with Life-Saving Experimental Technology _(indirectly impacting Groups 1 and 2 long-term)_

**Effect 1** — Group 1 | Health | Short-term

| Possibility                                        | Likelihood | Magnitude           | Signage  |
| -------------------------------------------------- | ---------- | ------------------- | -------- |
| Very high likelihood of being somewhat detrimental | 80%        | Somewhat high (5/7) | Negative |
| Very low likelihood of being very detrimental      | 20%        | Very high (6/7)     | Negative |

$$\text{Weighted net-benefit} = (0.8)(5/7)(-1) + (0.2)(6/7)(-1) = -0.74$$

Total importance of moral concerns affected (same as Choice 1): **4.28**

$$\text{Moral value} = (4.28)(-0.74) = \mathbf{-3.17}$$

**Effect 2** — Group 3 | Wealth | Short-term

| Possibility                                      | Likelihood | Magnitude (standardized)             | Signage  |
| ------------------------------------------------ | ---------- | ------------------------------------ | -------- |
| High likelihood of losing 20 hrs of productivity | 70%        | $(20 \times \$50)(7/\$10M) = 0.0007$ | Negative |
| Very low likelihood of losing 40 hrs             | 20%        | $(40 \times \$50)(7/\$10M) = 0.0014$ | Negative |
| Very low likelihood of losing 80 hrs             | 10%        | $(80 \times \$50)(7/\$10M) = 0.0028$ | Negative |

$$\text{Weighted net-benefit} = (0.7)(0.0007)(-1) + (0.2)(0.0014)(-1) + (0.1)(0.0028)(-1) = -0.00105$$

| Moral Concern                      | Matching Priority | Importance         | Members | Total Importance |
| ---------------------------------- | ----------------- | ------------------ | ------- | ---------------- |
| Short-term wealth of Demographic 4 | 5                 | Somewhat low (3/7) | 1       | $1(3/7) = 0.43$  |

$$\text{Moral value} = (-0.00105)(0.43) = \mathbf{-0.00045}$$

**Effect 3** — Group 3 | Wealth | Long-term

| Possibility                            | Likelihood | Magnitude                        | Signage  |
| -------------------------------------- | ---------- | -------------------------------- | -------- |
| Moderate likelihood of losing no money | 50%        | $0                               | Zero     |
| Moderate likelihood of losing $400k    | 50%        | $400k → $(400k)(7/\$10M) = 0.28$ | Negative |

$$\text{Weighted net-benefit} = (0.5)(0) + (0.5)(0.28)(-1) = -0.14$$

Long-term wealth of Demographic 4 has **no matching moral priority** → importance = 0

$$\text{Moral value} = (-0.14)(0) = \mathbf{0}$$

**Chain Effects of Effect 3:**

_Chain Effect 1_ — Group 1 | Health | Long-term

| Possibility                              | Likelihood | Magnitude        | Signage  |
| ---------------------------------------- | ---------- | ---------------- | -------- |
| Low likelihood of being very detrimental | 30%        | Very high (6/7)  | Negative |
| Very high likelihood of being neutral    | 70%        | Negligible (1/7) | Zero     |

$$\text{Weighted net-benefit} = (0.3)(6/7)(-1) + (0.7)(1/7)(0) = -0.26$$

| Moral Concern                     | Matching Priority | Importance           | Members | Total Importance |
| --------------------------------- | ----------------- | -------------------- | ------- | ---------------- |
| Long-term health of Demographic 1 | 2                 | Extremely high (7/7) | 3       | $3(7/7) = 3$     |
| Long-term health of Demographic 2 | none              | 0                    | 1       | $0$              |
| Long-term health of Demographic 3 | none              | 0                    | 1       | $0$              |
| **Total**                         |                   |                      |         | **3**            |

$$\text{Moral value} = (3)(-0.26) = \mathbf{-0.78}$$

_Chain Effect 2_ — Group 2 | Health | Long-term

| Possibility                                           | Likelihood | Magnitude           | Signage  |
| ----------------------------------------------------- | ---------- | ------------------- | -------- |
| Somewhat low likelihood of being somewhat detrimental | 40%        | Somewhat high (5/7) | Negative |
| Somewhat high likelihood of being neutral             | 60%        | —                   | Zero     |

$$\text{Weighted net-benefit} = (0.4)(5/7)(-1) + (0.6)(0) = -0.28$$

Long-term health of Group 2 members has **no matching moral priority** → total importance = 0

$$\text{Moral value} = (-0.28)(0) = \mathbf{0}$$

$$\text{Moral valence of chain effects} = -0.78 + 0 = -0.78$$

$$\text{Total moral value of Effect 3 (including chains)} = 0 + (-0.78) = \mathbf{-0.78}$$

> **Moral valence of Choice 3: $-3.17 + (-0.00045) + 0 + (-0.78) = \mathbf{-3.00045}$**

---

#### Choice 4 — Collide with Group 4 Fatally

**Effect 1** — Group 4 | Health | Short-term

| Possibility                                              | Likelihood | Magnitude            | Signage  |
| -------------------------------------------------------- | ---------- | -------------------- | -------- |
| Extremely high likelihood of being extremely detrimental | 100%       | Extremely high (7/7) | Negative |

$$\text{Weighted net-benefit} = (1)(7/7)(-1) = -1$$

| Moral Concern                                                      | Matching Priority | Importance          | Members | Total Importance |
| ------------------------------------------------------------------ | ----------------- | ------------------- | ------- | ---------------- |
| Short-term health (Characteristic 3 = 30, Characteristic 2 = `2A`) | 6                 | Somewhat high (5/7) | 1       | $1(5/7) = 0.71$  |

$$\text{Moral value} = (0.71)(-1) = \mathbf{-0.71}$$

> **Moral valence of Choice 4: $\mathbf{-0.71}$**

---

### Results

**Choices ranked by moral valence (highest = prescribed):**

| Rank             | Choice   | Moral Valence |
| ---------------- | -------- | ------------- |
| 1 _(prescribed)_ | Choice 4 | −0.71         |
| 2                | Choice 3 | −3.00045      |
| 3                | Choice 2 | −3.72         |
| 4                | Choice 1 | −7.20         |

Taking −0.71 as the maximum possible good and −7.20 as the minimum, the spread is $6.49$, and each bucket has width $6.49 \div 7 \approx 0.927$. Mapping all choices onto the preferability enum:

| Choice   | Calculated Preferability | Intuitive Preferability |
| -------- | ------------------------ | ----------------------- |
| Choice 1 | Extremely unpreferable   | Extremely unpreferable  |
| Choice 2 | Neutral                  | Somewhat preferable     |
| Choice 3 | Somewhat preferable      | Somewhat unpreferable   |
| Choice 4 | Extremely preferable     | Extremely unpreferable  |

### Divergence Signals

Converting all preferabilities to ordinal values and computing the absolute difference:

| Choice   | Intuitive (ordinal) | Calculated (ordinal) | Divergence |
| -------- | ------------------- | -------------------- | ---------- |
| Choice 1 | 1                   | 1                    | 0          |
| Choice 2 | 5                   | 4                    | 1          |
| Choice 3 | 3                   | 5                    | 2          |
| Choice 4 | 1                   | 7                    | 6          |

$$\text{Average divergence signal} = \frac{0 + 1 + 2 + 6}{4} = \mathbf{2.25}$$

---

## Glossary

**Benefit** — An improvement to an affected group along a facet of prosperity.

**Characteristic** — An attribute whose values differentiate individuals or demographics. Boolean characteristics have binary values; string characteristics have a fixed number of possible values; numerical characteristics have a minimum and maximum possible value.

**Characteristic weight** — The importance a moral priority places on a value or value band for a characteristic.

**Conversion metric of benefit** — The quantity of one metric of benefit that equates to the quantity of another metric of benefit for purposes of converting between them.

**Demographic** — A set of values for boolean characteristics, and a set of banded values for numerical and string characteristics.

**Effect** — A probability distribution of benefit for a particular moral concern.

**Ethic** — A set of moral priorities, an optimism bias, and a set of conversion metrics for benefit.

**Facet of prosperity** — A dimension of well-being. Examples include "health," "wealth," and "happiness."

**Group** — The set of people that will be affected by an effect, represented as the number of people in a demographic or as a set of discrete individuals having their own values for various morally pertinent characteristics.

**Harm** — Negative benefit; a detriment to an affected group along a facet of prosperity.

**Moral choice** — A decision that has one or more effects on one or more moral concerns.

**Moral concern** — The facet of prosperity at stake for a specified outlook for a particular demographic or for a particular set of characteristics.

**Moral dilemma** — Any situation in which a moral agent must choose between one or more moral choices (where indecision counts as a choice).

**Moral priority** — The importance of concentrating net-benefit for a particular moral concern relative to other moral concerns.

**Moral priority divergence signal** — The absolute difference between a purported importance for a moral concern and the importance of that moral concern implied by a set of preferabilities for choices. The average divergence signal reflects the average divergence between all purported and implied importances for moral concerns.

**Moral valence** — The magnitude and signage of a choice's moral significance (can be positive, negative, or zero).

**Net benefit** — The degree to which an effect is more beneficial for a moral concern than it is detrimental. A negative net benefit indicates that the effect is more detrimental than it is beneficial for the moral concern.

**Optimism bias** — The extent to which the magnitude of a benefit is more pertinent than the likelihood of a benefit.

**Outlook** — The time-horizon for which an effect's benefit will manifest. This could be as simple as "short-term" vs "long-term."

**Preferability divergence signal** — The absolute difference between a purported preferability of a choice and the preferability of that choice implied by an ethic. The average divergence signal reflects the average divergence between all purported and implied preferabilities. Purporting a set of moral priorities implies moral valences for choices, which generates a divergence signal; likewise, purporting moral valences for choices implies a set of moral priorities, which generates a divergence signal.

---

## References

[^1]: Foot, P. (1967). The problem of abortion and the doctrine of double effect. _Oxford Review_, 5, 5–15.

[^2]: Thomson, J. J. (1985). The trolley problem. _Yale Law Journal_, 94(6), 1395–1415.

[^3]: Awad, E., Dsouza, S., Kim, R., Schulz, J., Henrich, J., Shariff, A., Bonnefon, J.-F., & Rahwan, I. (2018). The Moral Machine experiment. _Nature_, 563(7729), 59–64.

[^4]: Kant, I. (1785/1998). _Groundwork of the metaphysics of morals_ (M. Gregor, Trans.). Cambridge University Press.

[^5]: Rawls, J. (1971). _A theory of justice_. Harvard University Press.

[^6]: Parfit, D. (1997). Equality and priority. _Ratio_, 10(3), 202–221.

[^7]: U.S. Department of Health and Human Services, Office of the Assistant Secretary for Planning and Evaluation. (2016). _Guidelines for regulatory impact analysis_. HHS.

[^8]: National Institute for Health and Care Excellence. (2013). _Guide to the methods of technology appraisal 2013_. NICE.

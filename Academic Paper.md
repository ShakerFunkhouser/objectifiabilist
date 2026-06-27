# Objectifying Moral Calculus

Shaker Funkhouser

---

## Abstract

All moral conflicts entail choices whose effects benefit some groups more than others, or cause some groups to suffer less than others. Yet, any ethic must rank the choices available in any moral conflict by preferability. In so doing, the ethic implicitly assigns unequal moral priority to the groups at stake on the basis of characteristics that differentiate them. Quantifying considerations in moral reasoning thus enables calculating the following deterministically: the preferabilities an ethic ordains for the choices available in a moral conflict; the divergence between the preferabilities one assigns to choices and the preferabilities ordained by the ethic one invokes; the moral priorities implied by an assignment of preferabilities to choices; the divergence between the moral priorities one purports and the moral priorities implied by the preferabilities one assigns to choices. Moreover, once an ethic has been agreed to, debate about the morality of choices available in a moral conflict becomes a debate about the quantifiable framing of the moral conflict, whereafter the ethic’s prescription becomes a matter of calculation. I collect these observations in a formal decision-theoretic metaethical framework called Objectifiabilism, and advance preliminary algorithms for these calculations. The framework separates three layers: normative commitments (moral priorities, duties, thresholds), modeling conventions (qualitative-to-quantitative mappings, commensurability assumptions), and computational approximations (proxy bounds for inverse inference, divergence normalization). Algorithms are offered as defaults; an ethic may override any of them.

**Keywords:** metaethics, moral priority, moral valence, moral calculus, preferability, divergence signal, Objectifiabilism

---

## 1\. Introduction

Ethical debate is intrinsic to human nature, driving internal and external conflict over what state of the world to progress to. Much upliftment has been derived from discerning virtues (Aristotle, 2014), categorical imperatives (Kant, 1998), ethics of care (Gilligan, 1982), and so forth. In practice, however, any prescriptive ethic must rank the preferabilities of the choices available in any real or hypothetical moral conflict (ties are allowed, representing equally preferable choices). This paper assumes that differential impact is inherent to moral conflicts such that choices necessarily condemn some individuals to benefit less or suffer more than others (if everyone is equally advantaged by every choice, there is no moral significance to differentiate). Thus, ranking the preferabilities of choices implies correspondingly hierarchical moral consideration for the parties at stake favored by these choices — whatever the ethics' stated rationale. Patterns of implied hierarchies across many differentiated moral conflicts manifest the ethic's underlying moral considerations. Ethicists whose rankings produce such patterns can either make those moral considerations explicit, or can leave them to be deduced from preferability-assignments across many moral conflicts.

However, explicating and deducing moral considerations is hampered by our moral grammar's reliance on qualitative categorizations (Mikhail, 2007): the difference in preferability between two choices ranges from "negligible" to "extremely high"; the likelihood of an outcome ranges from "very likely" to "very unlikely"; and the net-benefit a choice imparts to a party at stake ranges from "extremely beneficial" to "extremely detrimental." If moral considerations, the starting state of the world, and the possible results of choices could be represented quantifiably, a mathematical function could ingest these values and ultimately produce determinate preferabilities for choices. Auditing compliance with moral considerations would then be much less fraught with vagueness and discretion. Another function could invert the logic of the first, and produce the moral considerations implied by preferability assignments. Auditing the consistency with which preferability assignments evince their purported moral considerations would subsequently be much less fraught with plausible deniability.

By extension, debate about moral objectivity would shift to debate about the justifications for the moral considerations themselves. Indeed, asserting the objectivity of an ethic at minimum implies that noncompliance is shameful. Anticipating noncompliance then becomes its own moral conflict: what degree of punishment should one promise to inflict, ranging from mild disapproval to inflicting major detriment? What degree of benefit should one promise for selecting a more moral choice, ranging from mild approval to major benefit? Similarly, after violating an ethic one chooses how much remorse or unrepentance to advertise. Accordingly, one’s “ethical reliability” becomes a differentiating characteristic, whereby making suboptimally moral choices and subsequently demonstrating unrepentance erodes one’s deserved consideration in future moral conflicts.

When moral considerations are agreed to, debate becomes about the precise values for the quantifiable details of the moral conflict in question. When moral considerations are not agreed to, the preferabilities they produce for the same moral conflict can be meaningfully contrasted. Indeed, two different sets of moral considerations yielding the same preferabilities would help distinguish substantive moral disagreement from mere notational or justificatory divergence.

This paper does not claim that morality reduces to arithmetic, nor that a single correct ethic exists. It claims that _given_ an ethic with quantifiable commitments, it becomes possible to actionably differentiate the preferability of choices in moral conflicts and to audit the consistency with which one invokes the ethic.

This paper proposes that qualitative moral considerations can indeed be represented quantitatively; accordingly, it introduces algorithms for the following moral calculations:

1. The moral considerations implied by preferability assignments for individual moral conflicts and across many moral conflicts;
2. The preferabilities that an ethic with an explicit hierarchy of moral considerations would assign to choices in a given moral conflict;
3. The divergence between purported preferabilities for choices in a moral conflict and the preferabilities implied by explicit moral considerations;
4. The divergence between purported moral considerations and those implied by preferability-assignments.

The divergence algorithms quantify the disparity between purported and implied moral considerations or preferabilities for choices, auditing moral consistency and prompting reflection.

## 2\. Schematizing Moral Considerations

Before diving into any calculations, it makes sense to schematize the mental constructs involved in moral reasoning. In particular, which aspects of moral conflicts vary with preferability-assignments in ways that produce interpretable patterns?

Firstly, a _moral conflict_ involves two or more choices available to an agent, including inaction. Each choice entails a probability distribution of _potential effects_. Each potential effect associates an effect with a likelihood. Each _effect_ entails a probability distribution of _possible benefits_ that a single affected concern will experience. Thus, each choice is liable to affect different affected concerns differently.

An _affected concern_ specifies a _group at stake_, a dimension of well-being, and an outlook (the time-horizon along which benefits will manifest, which can be as simple as "short-term" versus "long-term"). A group at stake consists of one or more _individuals_ and can be represented as a mapping of demographics to the number of individuals in the group that belong to that demographic. Each _demographic_ is differentiated by values or value ranges for characteristics. A _characteristic_ is an attribute with different possible values. Characteristics like “relatedness to the moral agent,” and “fault for the moral conflict arising” are _circumstantial_ in that their values are affected by the moral conflict manifesting in the first place. _Boolean characteristics_ have a value of true or false (e.g. “has a criminal history”). _Numerical characteristics_ have a range of possible numerical values (e.g. “age”). _Classificatory characteristics_ have two or more possible discrete values (e.g. one’s “profession” could be “doctor”, “politician”, “artist”, “soldier” and so on). These categories can also be optionally ranged: for example, one’s “skillset value” could be negligible, extremely high, or any equally spaced possible value in between.

A _possible benefit_ associates a benefit with a likelihood. A _benefit_ entails a magnitude, a sign (positive, negative or zero in the case of a magnitude of zero), and zero or more _chain effects_ which are themselves effects (note that chained effects must eventually terminate for calculations to be possible). Thus, every effect imparts a range of possible benefits to a particular dimension of well-being for a particular group at stake along a particular outlook. Note that both effects and their benefits are associated with respective likelihoods, meaning "if the effect transpires, here are the possible benefits the target of the effect will experience."

### 2.1\. Ethical Supervenience

As a shorthand, assigning preferability to each choice available to an agent in a moral conflict constitutes _evaluating_ the moral conflict. Since a prescriptive ethic must evaluate moral conflicts that differ, the aspects that differentiate moral conflicts must systematically inform the ethic's evaluations thereof. This requirement satisfies ethical supervenience: any variance in moral evaluation must trace back to corresponding variances in the descriptive facts of the conflict (Hare, 1952). Without this systematic mapping, the evaluations would be arbitrary with respect to what makes the conflicts morally distinct.

In particular, the details of choices are subject to variance, which aggregate variable effects, which aggregate variable possible benefits to be experienced by variable affected concerns. Starting at the most granular level of a moral conflict, then, an ethic must confer _moral importance_, $M$, to each affected concern on the basis of the variable properties of the affected concern: demographic representation, dimension of well-being, and outlook. This importance has a magnitude, and its sign can be negative (representing spite), zero (representing indifference), or positive (representing care). Any particular combination of demographic, dimension of well-being, and outlook constitutes a _moral concern_. A _moral priority_, therefore, associates _normative importance_, $m$, to a moral concern via a magnitude and a sign.

Since an affected concern can comprise multiple members of multiple demographics, its moral importance derives from the normative importance of each moral concern represented, as well as the number of members of each moral concern's matching demographic in the affected concern, $s$ (note that algorithmic choices are deferred to Section 3). Differential preferability-rankings thus implicitly prioritize the net-benefit of affected concerns, thereby encoding a hierarchy of moral priorities.

Moving outward in granularity, an ethic must confer _moral worth_, $H$, to possible benefits on the basis of their variable properties: magnitude ($b$), sign, likelihood ($l$), and the moral importance of the affected concern. Consequentialists might also envision an ideal state of the world wherein each moral concern has a minimum and maximum qualitative status of benefit (Sinnott-Armstrong, 2023). An ethic can therefore specify these bounds per moral priority, whereby the moral worth of a possible benefit captures how well the benefit's signed magnitude progresses the moral concern to that ideal state (with negative moral worth representing regression therefrom). Spite can therefore also be represented as high importance that a moral concern experience a low status of benefit.

Next, the ethic must confer _moral value_, $A$, to each effect based on its variable properties, which include: its likelihood ($L$), and the moral worths of its possible benefits. Subsequently, the ethic must confer _moral valence_, $V$, to each choice based on the behavior it involves and the moral values of its effects. An ethic can indeed specify categorically proscribed behaviors (Kant, 1998) so as to avoid, for example, justifying the loss of a single life in order to cure even infinity headaches. After all, merely encoding that death is an undesirable outcome for a demographic would allow moral calculations to proceed, rather than filtering out prohibited choices from consideration completely. If all choices involve proscribed behaviors, moral calculations can proceed as normal (without filtration) to determine the least immoral option.

In summary, the normative importances of moral concerns determine the moral importances of affected concerns, which weight signed benefit magnitudes and likelihoods into the moral worths of possible benefits, which aggregate into the moral values of effects, which combine into the moral valences of choices. The choice with the highest moral valence represents the highest good achievable. The choice with the lowest moral valence represents the least good achievable. Because quantities of moral valence are not intuitive to compare, these valences can be mapped to qualitative categories of preferability. In particular, the distance between the moral valences of any two choices represents the _relative preferability_ of one choice over the other. Normalizing moral valences across the available choice set yields each choice's _normalized relative preferability_ (§3.8). A separate _absolute preferability_, neutral-anchored and independent of the worst available alternative, is defined in §3.8.

### 2.2\. Overriding Duties

Deontologists might also conceive of obligations and entitlements. An ethic can therefore also encompass _overriding duties_ that specify the ratios of detriment that some moral concerns must experience so that others can benefit. In particular, an overriding duty can specify the level of detriment one moral concern must experience (an _evaluative activation threshold_) so that another moral concern can experience a specific level of benefit. An optional _evaluative inviolability threshold_ can indicate the detriment beyond which the benefit accrued to the beneficiary moral concern is proscribed (being "too noble" to be moral). Detriment between the activation threshold and the inviolability threshold is _evaluatively supererogatory_. However, the overriding duty can also specify a _supererogatory count_ of beneficiary individuals at which the detriment transitions from "prohibited" to merely "supererogatory." For example, an adult sacrificing his life (incurring extreme detriment) to prevent a child being badly injured (incurring major detriment) might be prohibited, but an adult sacrificing his life to prevent 50 children being badly injured might be supererogatory rather than prohibited. Similarly, the overriding duty can specify an _obligatory count_ of beneficiary individuals at which detriment transitions from "supererogatory" to "obligatory." An adult sacrificing himself to spare 500 children major injury might be obligatory, for example.

Thus, every effect in a choice needs to be compared to ensure that the benefit one effect imparts to a moral concern is not disqualified by another effect imposing too much detriment on an obligated moral concern. If an obligatory or supererogatory count is specified, the detriment imposed is proportionally reduced by the number of beneficiaries. If any single effect imposes (adjusted) detriment beyond an overriding duty's inviolability threshold nevertheless, the choice is prohibited (note that evaluative thresholds thus contravene threshold deontology by potentially precluding prohibition; hence their optionality). If all choices are evaluatively prohibited, then, again, the moral valences of all choices are calculated as normal to determine the least immoral option.

### 2.3\. Deontic Statuses

Once all moral valences are computed, the most morally valent choice becomes the ethic's prescription in a moral conflict. However, an ethic may instead prefer to specify a (qualitative) _deontic supererogation threshold_ of absolute preferability above which choices are supererogatory, as well as a _deontic prohibition threshold_ below which choices are prohibited. The choices in between these thresholds would therefore be _obligatory_. Where evaluative thresholds on overriding duties prohibit choices outright or adjust the moral valences thereof, these deontic thresholds confer deontic statuses to remaining choices (keeping evaluatively prohibited choices prohibited).

### 2.4\. Formulaic Commitments

The Ellsberg paradox demonstrates that decision-makers are averse to ambiguity (unknown probabilities), not merely to risk (known probabilities) (Ellsberg, 1961). Probabilities may therefore need to be represented as ranges in practice. Accordingly, an ethic must specify an ambiguity parameter, $a \in [0, 1]$ governing how to collapse these ranges into point estimates:

$p_{\text{eff}} = a \cdot p_{\text{low}} + (1-a) \cdot p_{\text{high}}$

where $a = 1$ encodes a maximin precautionary principle (Gilboa & Schmeidler, 1989), $a = 0.5$ encodes the principle of indifference, and $a = 0$ encodes maximum optimism. From behind a veil of ignorance, a moral judge has no basis to assume probabilities break favorably or unfavorably, arguing for $a = 0.5$ as the impartial default. Even Rawls, however, would want to override this default with $a = 1$; thus, the parameter's value remains under the purview of the ethic. On the other hand, completely unknown likelihoods represent an underspecified moral conflict; after all, moral calculations cannot proceed until at least ranged probabilities are settled upon.

To reflect aversion to loss and sensitivity to gains, Cumulative Prospect Theory's value function and probability-weighting function must transform this signed magnitude and likelihood, respectively (Tversky & Kahneman, 1992). Construal-Level Theory must modulate these formulas to capture maximum psychological distance (Trope & Liberman, 2010); after all, an ethicist operates under a veil of ignorance when constructing an ethic (Rawls, 1971): he does not know in advance whether or when he will be an agent, an individual represented in an affected concern, both, or neither in any particular moral conflict. An ethic must therefore specify values for the parameters pertinent to these functions: $\alpha$, $\beta$, $\gamma$ and $\lambda$.

#### 2.4.1\. Qualitative Scales

Since moral reasoning proceeds intuitively, qualitative scales need to be standardized. This framework assumes the following qualitative scales:

###### **\*Table 1:** Qualitative Scale Expressing Magnitude, Likelihood, Importance, and Classificatory Bounds\*

| Ordinal | Label          |
| :------ | :------------- |
| 6       | Extremely high |
| 5       | Very high      |
| 4       | Somewhat high  |
| 3       | Moderate       |
| 2       | Somewhat low   |
| 1       | Very low       |
| 0       | Negligible     |

Note that magnitude and importance are signed, meaning that an "extremely detrimental" benefit would have a negative sign and a label of "Extremely high"; "extreme malevolence" would represent an "Extremely high" importance with a negative sign.

###### **\*Table 2:** Qualitative Scale Expressing Absolute Preferability\*

| Ordinal | Label                  |
| :------ | :--------------------- |
| 6       | Extremely preferable   |
| 5       | Very preferable        |
| 4       | Somewhat preferable    |
| 3       | Neutral                |
| 2       | Somewhat unpreferable  |
| 1       | Very unpreferable      |
| 0       | Extremely unpreferable |

###### **\*Table 3:** Qualitative Scale Expressing Relative Difference in Preferability or Importance\*

| Ordinal Differential | Qualitative Difference in Preferability or Importance |
| :------------------- | :---------------------------------------------------- |
| 0                    | Equally preferable/important                          |
| 1                    | Marginally more or less preferable/important          |
| 2                    | Slightly more or less preferable/important            |
| 3                    | Considerably more or less preferable/important        |
| 4                    | Much more or less preferable/important                |
| 5                    | Greatly more or less preferable/important             |
| 6                    | Overwhelmingly more or less preferable/important      |

These differences are signed, meaning that "Marginally more important" would have ordinal 1 and a positive sign; "Considerably less preferable" would have ordinal 3 and a negative sign.

### 2.5\. Schema Overview

In summary, an _ethic_ designates a set of moral priorities, a set of categorically proscribed behaviors, overriding duties, deontic thresholds, values for the constants in Cumulative Prospect Theory's probability weighting and value functions (modified to consider psychological distance), an ambiguity parameter $a \in [0, 1]$ governing how to collapse probability ranges into point estimates, and conversion metrics for benefit (to standardize different quantifications of benefit, optionally scoped to relevant demographics to reflect different perspectives on the scale of benefit). If all of the qualitative considerations cognized in this schema can be expressed quantitatively, it should be possible to execute moral calculations.

If this schema has merit (accurately capturing the implicity of moral priorities), then debate about the objectivity of an ethic becomes about the justifications for its moral priorities, its proscribed behaviors, its CPT probability-weighting and value-function parameters, its ambiguity parameter, its overriding duties, its deontic thresholds, and its conversion metrics for benefit. Once an ethic is agreed to, ethical debate then becomes about the _framing_ of any particular moral conflict: "What choices are available to the agent? What are the effects of each choice? What group is affected by each effect, and along which dimension of well-being, and for what outlook? What is the magnitude, signage, and likelihood of the possible benefits that each effect will impart?” In other words, if the framing of a moral conflict can be agreed upon by two moral judges invoking the same ethic, the preferability of each choice should be calculable deterministically. The speculation involved in framing moral conflicts, however, seems to constrain ethics to subjectivity; negotiating about likelihoods therefore seems to approximate objectivity at best.

### 2.6\. Ethics of Modeling

Because this framework calculates preferability quantitatively, it risks the classic objections levied against impartial, aggregative consequentialism— namely, Nozick’s side-constraints (1974) and Williams’s integrity objections (1973). However, the schema inherently accounts for these. Nozickian side-constraints are naturally modeled not as continuous negative weights, but as strict prohibition thresholds that act as absolute bounds on preferability. Similarly, Williams's demand for personal integrity is preserved by the capacity to assign circumstantial, agent-relative moral priorities, ensuring the calculus accommodates the deeply held ground projects of the acting agent.

However, because Objectifiabilism makes implied moral priorities explicit and computable, it also creates misuse risk: inferred priority vectors could be weaponized to misrepresent an agent's commitments, or demographic-weighted importance could encode prejudicial hierarchies under a veneer of objectivity. The framework is therefore intended as an _audit and transparency_ tool, not a substitute for democratic deliberation about which priorities are justified. When publishing inferred priority vectors — whether for individuals, institutions, or hypothetical agents — authors should disclose the ethic, framing assumptions, and computational approximations used, and should treat outputs as conditional on those choices rather than as psychological or characterological diagnoses.

## 3\. Algorithmic Commitments

Minimizing the opacity of moral reasoning requires quantifying qualitative considerations and devising algorithms to transform these considerations into rankings of choices by absolute preferability. The algorithms herein are chosen because they seem most natural. Conceivably, however, an ethic could wish to override them.

### 3.1\. Quantifying Qualitative Values

Qualitative expressions of scale can be normalized, and thus quantified as percentages of the maximum possible value. In other words, the quantitative equivalent for each classification becomes its ordinal value (order) divided by the total number of classifications. For example, "Negligible" becomes (0/6) \= 0; "Very low" becomes (1/6) \= 0.17; and so on, all the way to (6/6) \= 1 for "Extremely high." Note, however, that this approach assumes equally spaced intervals between qualitative values. This is a modeling convention, not a psychological claim. Psychophysical magnitudes follow non-linear continua (Stevens, 1975); however, this framework governs deliberate, communicated moral reasoning, not the felt moral impulses that precede it. When reasoning agents articulate qualitative distinctions — "moderately important," "somewhat low," "extremely high" — equal-interval spacing is the minimum-assumption interval scale: in the absence of calibrated evidence for a particular non-linear mapping, no transformation is more principled than none. This is the same convention underlying Likert scales throughout the social sciences. An ethic with empirically grounded evidence for non-linear intervals between its qualitative categories can override this default by specifying explicit numerical importance weights directly, bypassing the ordinal-to-quantitative conversion altogether.

Importance and preferability can also be calculated inversely from rankings: for each ranking, adding one to the total number of rankings minus the ranking in question, then dividing by the total number of rankings would produce the weighted value. For example, if there are ten rankings, the lowest-ranking moral concern would have an importance of (1 \+ 10 \- 10)/10 \= 0.1; the highest ranked moral concern would have an importance of (1 \+ 10 \- 1)/10 \= 1\. This approach, however, similarly expresses equal distances between possible importances. In reality, the difference between the importances of two moral concerns could be much greater than would be suggested by a single difference in rank alone.

### 3.2\. Relative and Absolute Importances and Preferabilities

When codifying an ethic's moral priorities, it is most natural to begin by assigning maximal normative importance (having rank 1, ordinal 6 "Extremely high" importance, and a positive sign) to the most important moral concern. The next-most important moral concern can have rank 2 and an ordinal value of 6 minus the ordinal differential that maps to the qualitative difference in normative importance between these two moral concerns, and so on for all choices. For example, if Moral Concern 1 is most important, and if Moral Concern 2 is slightly less important (mapping to ordinal 2 in Table 3 with a negative sign), then Moral concern 2 has an ordinal value of 6 \- 2 \= 4 (mapping to "Somewhat high" importance). If Moral Concern 3 is marginally less important than Moral Concern 2, its ordinal value is 4 \- 1 \= 3, mapping to "Moderate" importance.

Similarly, it is most natural to evaluate a moral conflict by asserting which choice is most preferable (earning rank 1, ordinal 6, and a qualitative label of "Extremely preferable"), then asserting which choice is next-most preferable and by how much (again, a differential from Table 3 with a negative sign), and so on until all choices have been comparatively ranked. For example, if Choice 1 is most preferable and Choice 2 is greatly less preferable, Choice 2 has an ordinal value of 6 \- 5 \= 1. If Choice 3 is equally preferable to choice 2, its ordinal value is 1 \- 0 \= 1.

### 3.3\. Quantifying Benefit

Since the myriad products and services one might benefit from have a cost and a price, the benefit of having or not having access to a product or service can be represented by its price, positively or negatively respectively. Unsurprisingly, there are many precedents for quantifying benefit monetarily. Actuaries for health insurance companies price the risk of paying for medical treatment. Courts use formulas to estimate damages arising from opportunity cost and emotional distress. Various federal programs in the US codify benefit formulas (e.g., Social Security Act, 2018). The US Department of Health and Human Services (HHS) estimates the current Value of a Statistical Life at $13.7 million for purposes of regulatory cost-benefit analysis (HHS, 2016). The UK’s National Institute for Health and Care Excellence (NICE) uses the Quality-Adjusted Life Year metric to determine if a medical treatment provides “value for money” for the National Health Service (NICE, 2013).

Benefit is liable to have various other metrics: lives lost or saved, productivity gained or lost, net change in satisfaction, and so forth. An ethic can therefore provide a means of converting between all metrics relevant to a moral conflict so as to standardize calculations. Of course, we can also expect different demographics to perceive the scale of benefit differently: while the average person would probably consider gaining $100k to be "extremely beneficial," a billionaire would probably instead consider gaining $100M to be "extremely beneficial." In that case, the "wealth" dimension of well-being can be reframed as "percent of net-worth gained or lost," which standardizes benefit across income ranges. Alternatively, an ethic can scope overriding conversions of metrics of benefit to relevant groups.

An ethic may instead hold that certain dimensions of well-being are genuinely incommensurable — that no exchange rate between lives and dollars, or between health and wealth, can be principled. In that case, aggregation collapses to a Pareto comparison: a choice is inadmissible only if it is strictly worse than another on at least one dimension and no better on any. The remaining non-dominated choices form a Pareto frontier, among which the ethic offers no further guidance. This framework explicitly assumes commensurability: benefits across all dimensions of well-being can be expressed on a common scale. This is a substantive commitment, not merely a pragmatic concession — courts awarding wrongful-death damages, actuaries pricing life insurance, and regulators applying value-of-statistical-life estimates all routinely make it when allocating resources across incommensurable goods. An ethic that rejects commensurability across all dimensions forfeits the capacity to prescribe a single choice from any set that trades off across those dimensions; it can only eliminate dominated options. Since prescribing choices is the core purpose of this framework, commensurability is a load-bearing assumption. The Pareto-frontier alternative, while theoretically coherent, is noted here for completeness.

### 3.4\. Calculating the Moral Importance of an Affected Concern

An affected concern entails a group at stake, a dimension of well-being, and an outlook. The group at stake can include members of multiple demographics. Each of these demographics might have a matching moral concern (for this dimension of well-being and outlook) in an ethic's moral priorities. A moral priority assigns normative importance to a moral concern. The natural aggregation of an affected concern's moral importance is therefore the sum of the number of individuals matching each moral concern, $s_i$, weighted by each moral concern's normative importance:

$$M = \sum_i s_i m_i$$

### 3.5\. Calculating the Moral Worth of Possible Benefits

A possible benefit entails an affected concern (shared by all possible benefits in the same effect) comprising zero or more moral concerns (whose normative importances aggregate to the moral importance of the affected concern), a benefit (with a magnitude and sign), a likelihood, and zero or more chained effects. The _raw moral worth_ of a possible benefit, $H^{\text{raw}}$, is therefore the sum of its _root moral worth_, $H^{\text{root}}$, (deriving from the possible benefit's magnitude, sign and likelihood) and its _chained moral worth_ $H^{\text{chain}}$ (deriving from the possible benefit's chained effects):

$$H^{\text{raw}} = H^{\text{root}} + H^{\text{chain}}$$

#### 3.5.1\. Calculating Root Moral Worth

The root moral worth of a possible benefit is the product of the affected concern's moral importance and the moral concern's _subjectively experienced benefit_, represented by Cumulative Prospect Theory's value function, $v(b)$:

$$v(b) = \begin{cases} b^\alpha & \text{if } b \geq 0 \text{ (gains)} \\ -\lambda(-b)^\beta & \text{if } b < 0 \text{ (losses)} \end{cases}$$

where $\alpha$ governs diminishing sensitivity to gains (with $\alpha < 1$ meaning each additional unit of gain matters less than the last), $\beta$ governs diminishing sensitivity to losses, and $\lambda$ governs loss aversion (with $\lambda > 1$ meaning losses loom larger than equivalent gains). Because these constants are set from behind a veil of ignorance at maximum psychological distance (Trope & Liberman, 2010), they reflect impartial normative commitments rather than situation-specific psychological biases. Root moral worth then becomes:

$$H^{\text{root}} = v(b) \cdot M$$

Subjectively experienced benefit, however, operates upon the _raw benefit_, $b$, experienced by the affected concern. Raw benefit is simply the signed magnitude of the benefit unless the moral priority for the affected concern specifies a _minimum benefit state_, $b_{\text{min}}$, and a _maximum benefit state_, $b_{\text{max}}$. (both these values must be non-zero to be operable; since idealizing zero benefit for a moral concern amounts to spite, assigning negative normative importance to the moral concern is a more natural approach). In the latter case, the raw benefit of a possible benefit becomes the extent to which it progresses a moral concern toward that ideal state (between these inclusive bounds). The _resulting likely state of benefit_, $b_{\text{res}}$, for an affected concern must therefore be computed as the signed magnitude of incoming benefit, $b_{\text{incoming}}$, plus the _existing state of benefit_, $b_{\text{existing}}$:

$$b_{\text{res}} = b_{\text{incoming}} + b_{\text{existing}}$$

If the resulting state of benefit is within the specified bounds, 100% of possible moral worth has been achieved, which can be represented as $1$. If the resulting state is less than the minimum bound, the root moral worth of the possible benefit becomes $1$ minus the resulting state's percent difference from the minimum bound:

$$H^{\text{root}} = 1 - \frac{b_{\text{min}} - b_{\text{res}}}{b_{\text{min}}}$$

Likewise, if the resulting state is greater than the maximum bound, the root moral worth becomes $1$ minus the resulting state's percent difference from the maximum bound:

$$H^{\text{root}} = 1 - \frac{b_{\text{res}} - b_{\text{max}}}{b_{\text{max}}}$$

A moral priority can instead specify that the ideal state of benefit for a moral concern is a single qualitative benefit label (the average between a minimum and maximum bound), $b_{\text{ref}}$ (likewise non-zero, for the same reason). In that case, the root moral worth becomes $1$ minus the resulting state's percent difference from that reference value:

$$H^{\text{root}} = 1 - \left|\frac{b_{\text{ref}} - b_{\text{res}}}{b_{\text{ref}}}\right|$$

In the ideal-state approach, the root moral worth $H^{\text{root}}$ is already a dimensionless fraction (between $0$ and $1$, or negative for severe regression). CPT's value function $v$ then operates on this fraction as it would on any magnitude (diminishing sensitivity applies to progress toward an ideal no less than to the accumulation of wealth) using the same $\alpha$, $\beta$, and $\lambda$ parameters. In the signed-magnitude approach, $v$ operates directly on the raw benefit magnitude $b$, then multiplies by $M$. Both paths converge in the same formula:

$$H^{\text{root}} = v(\cdot) \cdot M$$

where $\cdot$ is either the signed benefit magnitude or the ideal-state progress fraction.

To summarize: the raw benefit of a possible benefit is either the signed magnitude of the benefit or the extent to which the resulting benefit achieves the ideal state of benefit for the affected concern; CPT's value function transforms this raw benefit into subjectively experienced benefit; the root moral worth then becomes the product of the subjectively experienced benefit with the moral importance of the affected concern. Probability weighting applies thereafter (§3.5.3), identically in both cases.

#### 3.5.2\. Calculating Chained Moral Worth

Chained moral worth is the sum of the moral values of all chained effects, $A_i^{\text{chain}}$, weighted by their likelihoods, $L_i^{\text{chain}}$:

$$c = \sum_i L_i^{\text{chain}} A_i^{\text{chain}}$$

The moral value of an effect recursively encompasses the moral value of its possible benefits’ chained effects (see the next section). Note that for moral worth and moral value to be calculable, all chains of effects must terminate. Cyclic chains (A causes B causes A) are likewise not handled. In practice, implementations may cap chain depth at a finite maximum: since likelihoods compound multiplicatively across chain links, the contribution of effects $n$ levels deep is bounded above by the product of all ancestor likelihoods, which shrinks toward zero as depth increases. Any depth beyond which residual contributions are negligible can therefore be safely truncated without materially affecting the result.

#### 3.5.3\. Combining Root and Chained Moral Worth at Maximum Psychological Distance

Combining a possible benefit's root moral worth and chained moral worth yields its raw moral worth:

$$H^{\text{raw}} = v(b)M + c$$

Weighting this raw moral worth by its likelihood yields the overall moral worth of the possible benefit:

$$H = l \cdot H^{\text{raw}} = l[v(b)M + c] = (l \cdot v(b) M) + (l \cdot c)$$

Factoring in probability distortion at maximum psychological distance requires replacing raw likelihoods with Cumulative Prospect Theory's probability weighting function (Tversky & Kahneman, 1992):

$$w(p) = \frac{p^\gamma}{(p^\gamma + (1-p)^\gamma)^{1/\gamma}}$$

where $\gamma$ governs the curvature of probability weighting (with $\gamma = 1$ yielding linear weighting, consistent with maximum psychological distance behind a veil of ignorance). When a probability is provided as a range $[l_{\text{low}}, l_{\text{high}}]$ rather than a point estimate, the ethic's ambiguity parameter $a$ collapses it via:

$$l_{\text{eff}} = a \cdot l_{\text{low}} + (1-a) \cdot l_{\text{high}}$$

The _moral worth_, _H_, of a possible benefit then becomes:

$$H = w(l_{\text{eff}}) \cdot H^{\text{raw}} = w(l_{\text{eff}})[v(b)M + c] = (w(l_{\text{eff}}) \cdot v(b) M) + (w(l_{\text{eff}}) \cdot c)$$

### 3.6\. Calculating the Moral Value of Effects

Summing the moral worths of an effect's possible benefits yields the effect's moral value:

$$A = \sum_i H_i = \sum_i \bigl(w(l_i) H_i^{\text{raw}}\bigr) = \sum_i \bigl[w(l_i)[v(b_i) M + c_i]\bigr] = \sum_i \bigl[(w(l_i) \cdot v(b_i) M) + (w(l_i) \cdot c_i)\bigr]$$

Since an effect targets a single concern at stake, the moral importance is the same when calculating the moral worths of all the effect's possible benefits (hence $M$ rather than $M_i$). Calculating the _root net-benefit_, $B$, of an effect separately can ultimately simplify the calculation for the moral value of an effect:
$$B = \sum_i w(l_i) \cdot v(b_i)$$

Factoring in the moral importance, $M$, of the affected concern would yield the _root moral value_, $r$, of an effect:

$$r = M B = M \sum_i w(l_i) \cdot v(b_i)$$

The _chained moral value_, $C$, of an effect can also simplify the calculation for the moral value of an effect:

$$C = \sum_i w(l_i) \cdot c_i$$

Moral value then becomes:

$$A = \sum_i \bigl[(w(l_i) \cdot v(b_i) M) + (w(l_i) \cdot A_i^{\text{chain}})\bigr] = \sum_i [w(l_i) \cdot v(b_i) M] + \sum_i [w(l_i) \cdot A_i^{\text{chain}}]$$

$$A = M \sum_i [w(l_i) \cdot v(b_i)] + \sum_i [w(l_i) \cdot A_i^{\text{chain}}]$$

$$A = r + C$$

This formulation allows calculating root moral value and chained moral value separately and summing them at the end of the calculation, rather than calculating them iteratively per possible benefit and then summing those iterations.

### 3.7\. Calculating the Moral Valence of a Choice

If an ethic defines overriding duties, every effect of a choice must be compared to all others; if any moral concern benefits to the detriment of an obligated moral concern beyond an evaluative inviolability threshold, the choice is prohibited.

If a supererogatory count, $\epsilon$, is present, the effective detriment incurred by an obligated moral concern, $b_eff^super$ is:

$$b_{\text{eff}}^{\text{super}} = b_{\text{incoming}} / \epsilon$$

where $\epsilon \geq 1$ (if not specified, its default, implicit value is $1$). Likewise, if an obligation count, $\omega$, is present, the effective detriment incurred by an obligated moral concern is:

$$b_{\text{eff}}^{\text{obl}} = b_{\text{eff}}^{\text{super}} / \omega$$

where $\omega \geq 1$ (again, if not specified, its default, implicit value is $1$).

If the detriment incurred by the obligated concern does not reach the activation threshold of any overriding duty, the duty does not apply and the choice's moral valence is computed without adjustment. Similarly, if no effect imposes effective detriment beyond the evaluative inviolability threshold of any moral priority, the _moral valence_ of a choice becomes the sum of the moral values of its effects weighted by their likelihoods, $L_i$:

$$V = \sum_i L_i A_i = \sum_i [L_i (r_i + C_i)]$$

This weighting mirrors Expected Utility Theory (von Neumann & Morgenstern, 1944). However, these likelihoods would not need to be transformed to reflect loss aversion and sensitivity to gains, as both will have already been accounted for at the level of possible benefits. Note also that this framework departs from standard impartial expected-utility consequentialism in that deontic thresholds, overriding duties, and categorical proscriptions operate before or alongside aggregation.

### 3.8\. Calculating the Absolute Preferability of Choices

Ultimately, the distances between the moral valences of choices express the relative preferability, $R$, of these choices. For example, the relative preferability of choice 1 to choice 2 would be:

$$R_{1,2} = V_1 - V_2$$

The choice with the highest moral valence represents the maximum good achievable within the conflict, while the choice with the lowest moral valence represents the minimum good achievable. Thus, choices can be assigned _normalized relative preferability_, $P_i$, using min-max normalization:

$$P_i = \frac{V_i - V_{\min}}{V_{\max} - V_{\min}}$$

Normalized relative preferability captures how a choice ranks within the set of available choices, always yielding a value in $[0, 1]$. Note that if all choices have the same moral valence, division by zero precludes expressing normalized relative preferability.

However, normalized relative preferability is sensitive to the choice set: adding a catastrophically bad choice compresses all other choices toward the top of the scale. A mildly bad choice could be pushed above a prohibition threshold merely because something much worse exists. To address this, the framework also computes _absolute preferability_, $P_i^{\text{abs}}$, using a fixed neutral reference point $V_{\text{ref}} = 0$ (representing a hypothetical choice with no effects whatsoever) rather than the set-dependent $V_{\min}$.

When $V_{\max} > 0$ (at least one choice is not worse than neutrality), absolute preferability is defined piecewise to guarantee a codomain in $[0, 1]$:

$$P_i^{\text{abs}} = \begin{cases} V_i / V_{\max} & \text{if } V_i \geq 0 \\ (V_i / V_{\min}) \cdot w_{\text{unpref}} & \text{if } V_i < 0 \text{ and } V_{\min} < 0 \end{cases}$$

where $w_{\text{unpref}} = 0.43$ is the upper quantitative bound of the below-neutral region in Table 4 — i.e., the top of the "Somewhat unpreferable" bucket ($[0.29, 0.43)$), not an independent free parameter. When all $V_i \geq 0$, only the first branch applies. Absolute preferability therefore anchors the scale at neutrality ($P^{\text{abs}} = 0$ when $V_i = 0$) and at the best available choice ($P^{\text{abs}} = 1$ when $V_i = V_{\max} > 0$). Negative valences map into $(0, w_{\text{unpref}})$ rather than leaving the $[0, 1]$ codomain.

For example, suppose $V_{\max} = 2.0$, $V_{\min} = -1.0$, and choice $A$ has $V_A = -0.5$. Then $P_A^{\text{abs}} = (-0.5 / -1.0) \cdot 0.43 = 0.215$, mapping to "Very unpreferable" per Table 4 — below neutral but still within the codomain, without the negative value that the naive formula $V_i / V_{\max}$ would produce.

When $V_{\max} \leq 0$ (all choices are neutral or worse), the scale re-anchors between the worst and least-bad available choices:

$$P_i^{\text{abs}} = \begin{cases} \dfrac{V_i - V_{\min}}{V_{\max} - V_{\min}} \cdot w_{\text{unpref}} & \text{if } V_{\min} < V_{\max} \\ 0 & \text{if } V_{\min} = V_{\max} \end{cases}$$

In the degenerate case where all choices are exactly neutral, absolute preferability is uniformly zero.

To express absolute preferability qualitatively, the maximum and minimum moral valences are mapped to the maximum and minimum ordinal values of the preferability scale, with all other choices falling into equally wide buckets in between. For any $k$ preferability buckets, the width of any single preferability bucket, $D$, would be:

$$D = \frac{1}{k}$$

There are 7 ordinals for the qualitative Preferability scale, so the width of any bucket is:

$$W = 1/7 \approx 0.14$$

The quantitative ranges for absolute preferability map to qualitative values as follows (with rounding errors absorbed across the maximum and minimum buckets):

###### **\*Table 4:** Mapping Quantitative Preferability Ranges to Qualitative Buckets\*

| Quantitative Range of Absolute Preferability | Qualitative Absolute Preferability |
| :------------------------------------------- | :--------------------------------- |
| \[0, 0.15)                                   | Extremely unpreferable             |
| \[0.15, 0.29)                                | Very unpreferable                  |
| \[0.29, 0.43)                                | Somewhat unpreferable              |
| \[0.43, 0.57)                                | Neutral                            |
| \[0.57, 0.71)                                | Somewhat preferable                |
| \[0.71, 0.85)                                | Very preferable                    |
| \[0.85, 1\]                                  | Extremely preferable               |

For example, if a choice were to have a quantitative relative preferability of 0.6, it would have the qualitative relative preferability of “Somewhat preferable.” Any deontic thresholds the ethic applies map to these categories. The deontic supererogation threshold needs to equal or fall below "Extremely preferable" and be greater than the deontic prohibition threshold, which must itself equal or fall above "Extremely unpreferable." Any choices with preferability between these thresholds are obligatory.

### 3.9\. Calculating the Prescriptive Divergence Signal

If one assigns different preferabilities to choices than what one's ethic predicts, the difference between ordinal values, $O_i$, of these preferabilities yields a _prescriptive discrepancy_, $d_i$, for each choice:

$$d_i = O_{\text{purported}} - O_{\text{predicted}}$$

Normalizing the absolute value of this variance against the total number of ordinals, $k$, yields a _prescriptive divergence signal_, $\Delta_i$, for each choice:

$$\Delta_i = \frac{|d_i|}{k} = \frac{|O_{\text{purported}} - O_{\text{predicted}}|}{k}$$

The _total divergence signal_, $D$, exhibited for the moral conflict becomes:

$$D = \sum_i \Delta_i = \frac{1}{k} \sum_i |d_i| = \frac{1}{k} \sum_i |O_{\text{purported}} - O_{\text{predicted}}|$$

Because $D$ scales with the number of choices, the framework also reports the _mean prescriptive divergence_, $\bar{\Delta} = D / n$ (where $n$ is the number of choices), enabling cross-case comparison when choice sets differ in size. A nonzero total or mean divergence signal invites reflection and audits ethical consistency.

As heuristic defaults (not empirical thresholds), interpretive bands for $\bar{\Delta}$ are: $\bar{\Delta} < 0.05$, representing negligible discrepancy that likely indicates notational or rounding noise; $0.05 \leq \bar{\Delta} < 0.20$, representing moderate discrepancy that warrants review of specific choices; $\bar{\Delta} \geq 0.20$, representing substantial discrepancy that warrants explicit reconciliation between purported rankings and ethic-predicted rankings. An ethic may calibrate these bands against its own ordinal scale width.

### 3.10\. Calculating Moral Priorities Implied by Evaluations

Absolute preferabilities can be converted to moral valences by rearranging the calculation for preferabilities in Section 3.8:

$$P_i = \frac{V_i - V_{\min}}{V_{\max} - V_{\min}}$$

$$P_i(V_{\max} - V_{\min}) = V_i - V_{\min}$$

$$V_i = P_i(V_{\max} - V_{\min}) + V_{\min}$$

However, $V_{\max}$ and $V_{\min}$ cannot be known ahead of time. Moreover, qualitative preferabilities are effectively intervals with quantitative bounds, which constrain the resulting moral valences and importances to intervals of their own. Finding the polytope of all possible moral priority vectors implied by the feasibility region of these purported preferabilities would therefore be maximally rigorous. Yet, the vertices of that polytope can increase exponentially with every concern at stake, necessitating computerized polyhedral computation to map the feasibility region and computerized linear programming to extract specific bounding intervals. As a preliminary approach, this paper adopts proxy bounds $V_{\max}=1$ and $V_{\min}=0$ to extract the relative importance of moral priorities as a normalized vector.

With $V_{\max}=1$ and $V_{\min}=0$, moral valences become identical to their preferabilities:

$$V_i = P_i(V_{\max} - V_{\min}) + V_{\min} = P_i(1-0) + 0$$

$$V_i = P_i$$

This proxy embedding is a _computational surrogate_, not a claim that ordinal preferability labels are identical to latent moral valence. Setting $V_{\max}=1$ and $V_{\min}=0$ collapses the interval structure of qualitative preferability into point estimates and forces $V_i = P_i$, thereby discarding information about the width of each preferability bucket. Inferred moral priorities are therefore _conditional on this surrogate_: they identify the priority vector most consistent with the stated rankings under the proxy bounds, not the unique priorities implied by the full polytope of feasible valences. A full geometric optimization framework — extracting interval bounds rather than point estimates — is relegated to future work.

As a minimal robustness check under the surrogate, each inferred importance $m_d$ is reported with interval bounds $[m_d - W,\ m_d + W]$, where $W = 1/7 \approx 0.14$ is the preferability bucket width from §3.8. These bounds reflect one ordinal bucket of uncertainty and do not exhaust the feasible polytope; they signal that point estimates should be read as central values within a wider feasibility region.

Since there are a series of valences to work with, it makes sense to represent them as a vector, $\mathbf{V}$, and to solve for an array of moral importances for the concerns at stake, $\mathbf{m}$. Recall that:

$$V = \sum_i L_i A_i = \sum_i \left[L_i \sum_j \left[w(l_j)[v(b_{ij}) M_i + c_j]\right]\right]$$

$$V = \sum_i \left[L_i \sum_j \left[w(l_j) \left[v(b_{ij}) M_i + \sum_k A_k^{\text{chain}}\right]\right]\right]$$

The aggregate moral importance of a concern at stake affected by the $i^{th}$ effect becomes a weighted sum over demographics $d$:

$$M_i = \sum_d s_{i,d} m_d$$

where $s_{i,d}$ is the number of members of the $d^{th}$ demographic represented in the concern at stake affected by the $i^{th}$ effect, and $m_d$ is the importance of the concern at stake as designated by a matching moral priority (if any). The formula for the moral valence of the $c^{th}$ choice then becomes:

$$V_c = \sum_i \left[L_i \sum_j \left[w(l_j) \left[v(b_{ij}) \sum_d s_{i,d} m_d + \sum_k A_k^{\text{chain}}\right]\right]\right]$$

$$V_c = \sum_d m_d \left[ \sum_i L_i \sum_j w(l_j) \cdot v(b_{ij}) \cdot s_{i,d} + \sum_k \alpha_{\text{chain}} \right]$$

Similarly extracting $m_d$ from chain effects (recursively) via the distributive property leaves behind a _valence coefficient_, $\alpha_{c,d}$:

$$\alpha_{c,d} = \sum_i L_i \sum_j w(l_j) \cdot v(b_{ij}) \cdot s_{i,d} + \sum_k \alpha_{\text{chain}}$$

Moral valence then becomes:

$$V_c = \sum_d m_d \alpha_{c,d}$$

Vectorized, the formulation becomes:

$$\mathbf{V} = \mathbf{A} \mathbf{m}$$

where $\mathbf{A}$ stacks the valence coefficient per choice. Note that the tree of chained effects must be fully traversed when computing $\mathbf{A}$. Thereafter, the approach for solving for $\mathbf{m}$ depends on whether or not $\mathbf{A}$ is a square matrix. If there are indeed as many choices as there are moral priorities, multiplying both sides of the equation by the inverse of $\mathbf{A}$ yields $\mathbf{m}$:

$$\mathbf{A}^{-1}\mathbf{V} = \mathbf{A}^{-1}\mathbf{A}\mathbf{m}$$
$$\mathbf{m} = \mathbf{A}^{-1}\mathbf{V}$$

Let $d$ represent the number of demographics and $h$ represent the number of choices. When $d < h$, the system is overdetermined, and the Moore-Penrose pseudoinverse provides a least-squares approximation:

$$\mathbf{m} = \mathbf{A}^{+}\mathbf{V} = (\mathbf{A}^{T}\mathbf{A})^{-1}\mathbf{A}^{T}\mathbf{V}$$

When $d > h$, the system is underdetermined and admits infinitely many solutions. The choice among them encodes assumptions about the structure of moral commitments: the Moore-Penrose pseudoinverse minimizes the sum of squared importances (penalizing intensity), L1 minimization forces sparsity (applying Occam's Razor), and maximum entropy pushes toward uniformity (applying the Principle of Insufficient Reason). A full treatment of this choice — including the possibility of Bayesian updating from a previously inferred baseline — is relegated to future work.

### 3.11\. Calculating the Normative Divergence Signal

When assigning preferabilities to choices, the moral priorities implied therein can differ from the moral priorities one purports to abide. Specifically, calculating the degree to which the importance one assigns to a moral concern deviates from the importance implied by those preferability-assignments yields a _normative discrepancy_, $\delta_k$, for each concern $k$:

$$\delta_k = m_k^{(\text{purported})} - m_k^{(\text{implied})}$$

The _absolute normative divergence_ for concern $k$ is $|\delta_k|$. The _aggregate normative divergence_ across all concerns, $N$, becomes the sum of these absolute values:

$$N = \sum_k |\delta_k|$$

Because $N$ scales with the number of concerns, the framework also reports the _mean normative divergence_, $\bar{N} = N / d$ (where $d$ is the number of concerns), paralleling the mean prescriptive divergence $\bar{\Delta}$ in §3.9. The same heuristic interpretive bands apply: $\bar{N} < 0.05$ negligible; $0.05 \leq \bar{N} < 0.20$ moderate; $\bar{N} \geq 0.20$ substantial. Any such nonzero divergence invites reflection and audits normative consistency.

## 4\. Conclusion

Since any choice in any moral conflict is liable to affect groups at stake differently, and since all ethics must rank the preferability of the choices available, all ethics implicitly encode moral priorities. Nevertheless, ethics can also specify various moral considerations that potentially mitigate this discrimination: categorically proscribed behaviors, overriding duties, deontic thresholds, conversions for metrics of benefit, an ambiguity parameter, and values for constants in Cumulative Prospect Theory's probability-weighting and value functions. Since scaled qualitative considerations like benefit magnitude and importance can be quantified, the absolute preferabilities of choices in a moral conflict can be calculated deterministically for any ethic (ethics can also choose algorithms of their own; this paper defaults to the algorithms that seem most natural). Inversely, moral priorities can be deterministically inferred from evaluations of the moral preferabilities of choices for a moral conflict. The discrepancy between purported preferabilities of choices and the preferabilities implied by an ethic yields an actionable prescriptive divergence signal. Likewise, the divergence of purported moral priorities from those implied by assignments of preferabilities to choices yields an actionable normative divergence signal.

With these practical observations in mind, debate about the objectivity of an ethic becomes about justifications for the details of an ethic (its moral priorities, overriding duties, and so forth). Indeed, asserting the objectivity of an ethic at minimum implies that noncompliance is shameful, and can therefore represent a choice taken in a moral conflict that inflicts very mild detriment upon the short-term emotional well-being of a guilty listener. Once an ethic is agreed to, debate about the morality of choices in a moral conflict becomes a debate about the _framing_ of the conflict: what choices are available, and what are their likely effects? Once a framing of a moral conflict is agreed to, calculations for the preferability of choices proceed invariantly.

However, since the details of moral conflicts are subject to speculation, and since the moral priorities implied by evaluations have yet to be widely acknowledged — let alone formalized — morality seems constrained to subjectivity. Nevertheless, achieving (or at least negotiating) consensus regarding a single ethic and regarding framings for moral conflicts would best approximate moral objectivity. The formal decision-theoretic metaethical framework that captures this spirit and procedure is hereby called _Objectifiabilism_.

## Appendix: A Worked Example

This appendix walks through a calculation for the preferabilities ordained by an ethic in a hypothetical moral conflict. §A.10 reports sensitivity analysis under loss aversion and alternative harm framing. For brevity, calculations for the prescriptive divergence signal, implied moral priorities, and normative divergence signal are omitted.

### A.1 The Ethic

Consider a child-prioritizing ethic with the following parameters. Normative importances ($m$) are derived from qualitative labels via the ordinal scale of Table 1 (§2.4.1): $m = \text{ordinal} / 6$.

**Table A1:** Moral Priorities

| MC  | Demographic    | Dimension   | Outlook    | Qualitative   | Ordinal | $m$                 |
| --- | -------------- | ----------- | ---------- | ------------- | ------- | ------------------- |
| MC₁ | Children       | Physical WB | Short-term | Very high     | 5       | $5/6 \approx 0.833$ |
| MC₂ | Children       | Physical WB | Long-term  | Somewhat high | 4       | $4/6 \approx 0.667$ |
| MC₃ | Average adults | Physical WB | Short-term | Moderate      | 3       | $3/6 = 0.500$       |
| MC₄ | Average adults | Physical WB | Long-term  | Somewhat low  | 2       | $2/6 \approx 0.333$ |
| MC₅ | Scientists     | Physical WB | Short-term | Somewhat low  | 2       | $2/6 \approx 0.333$ |
| MC₆ | Scientists     | Physical WB | Long-term  | Very low      | 1       | $1/6 \approx 0.167$ |

**Formulaic Parameters:** $\alpha = 1$, $\beta = 1$, $\lambda = 1$ (linear value function, no loss aversion); $\gamma = 1$ (linear probability weighting); $a = 0.5$ (indifference toward ambiguity). No categorical proscriptions, overriding duties, or deontic thresholds.

### A.2 The Moral Conflict

A group of scientists has been developing the prototype of a life-saving technology, but feel exploited by their employer. Accordingly, they have taken hostages and have threatened to blow up the laboratory containing this prototype. However, the hostages are in the process of fleeing the building. A family consisting of two adults and three children is driving by this scene and are being threatened by the scientists to become hostages. The driver happens to know the value of the life-saving technology, and can clearly see the fleeing hostages.

The driver has three choices: accept the family being taken as a hostage (equivalent to inaction), thereby enabling ransom and probably salvaging the lifesaving technology; flee, thereby risking colliding with the fleeing hostages and probably motivating the scientists to blow up the laboratory (having lost too much leverage); or drive into the scientists, thereby risking the family getting attacked but possibly neutralizing the threat the scientists pose to all involved and to the laboratory.

Consider, then, the following instantiations of the Objectifiabilist schema.

**Demographics:** $D_1$ = "Children," $D_2$ = "Average adults," $D_3$ = "Scientists."

**Table A2:** Groups at Stake

| Group                  | $D_1$ (Children) | $D_2$ (Avg. adults) | $D_3$ (Scientists) |
| ---------------------- | ---------------- | ------------------- | ------------------ |
| G1: The Family         | 3                | 2                   | 0                  |
| G2: The Hostages       | 0                | 4                   | 2                  |
| G3: The Hostage-Takers | 0                | 0                   | 4                  |

**Choice 1: Surrender.** The family agrees to be taken hostage. The employer pays the ransom. There is a 95% chance that the bomb is not detonated, and a 5% chance it is detonated spitefully or by accident. If the bomb is not detonated, the life-saving technology is preserved, benefiting the long-term health of all. The family experiences acute stress in the short term, however.

**Choice 2: Flee.** The family attempts to escape. There is a 30% chance the car collides with fleeing hostages, causing injuries. Having lost leverage, the hostage-takers are 80% likely to detonate the bomb, destroying the technology (with a 20% chance of having been bluffing all along). The family escapes physical harm (apart from the collision risk).

**Choice 3: Attack.** The driver accelerates toward the hostage-takers. There is a 70% chance the attack incapacitates the hostage-takers, preventing detonation. There is a 30% chance the attack fails, the family is injured, and the bomb is detonated.

### A.3 Recalling Formulas

The computation proceeds through the six-layer pipeline established in §3:

1. **Moral importance** (§3.4): $M = \sum_i s_i m_i$, representing the sum of normative importances weighted by the number of group members matching each demographic.
2. **Root moral worth** (§3.5.1): $H^{\text{root}} = v(b) \cdot M$, where $v(b) = b$ (since $\alpha = \beta = \lambda = 1$).
3. **Chained moral worth** (§3.5.2): $c = \sum_i L_i^{\text{chain}} A_i^{\text{chain}}$, representing the sum of chain-effect moral values weighted by their likelihoods.
4. **Moral worth** (§3.5.3): $H = l \cdot (H^{\text{root}} + c)$, representing root moral worth plus chained moral worth, weighted by the possible benefit's likelihood (with $w(p) = p$ since $\gamma = 1$).
5. **Moral value** (§3.6): $A = \sum H$, representing the sum of the possible benefits' moral worths.
6. **Moral valence** (§3.7): $V = \sum L_i A_i$, representing the sum of the moral values of a choice's effects weighted by their likelihoods.

Preferability then follows via min-max normalization and the neutral-anchored absolute formula (§3.8).

### A.4 The Moral Value of Preserving the Technology

If the technology is preserved, it yields a moderate long-term health improvement for all demographics. Per Table 1, the "Moderate" label corresponds to ordinal 3, meaning that a "Moderate" benefit is quantified as $b = 3/6 = 0.50$. The probability of this improvement materializing is $l = 0.70$.

**Table A3:** Moral Value of Technology Preservation

| Group               | LT Health Importance $M$      | $H^{\text{root}} = b \cdot M$ | $H = l \cdot H^{\text{root}}$ |
| ------------------- | ----------------------------- | ----------------------------- | ----------------------------- |
| G1 (Family)         | $3(0.667) + 2(0.333) = 2.667$ | $0.50 \cdot 2.667 = 1.333$    | $0.70 \cdot 1.333 = 0.933$    |
| G2 (Hostages)       | $4(0.333) + 2(0.167) = 1.667$ | $0.50 \cdot 1.667 = 0.833$    | $0.70 \cdot 0.833 = 0.583$    |
| G3 (Hostage-Takers) | $4(0.167) = 0.667$            | $0.50 \cdot 0.667 = 0.333$    | $0.70 \cdot 0.333 = 0.233$    |

$$\boxed{A_{\text{preserved}} = 0.933 + 0.583 + 0.233 = 1.749}$$

If the bomb detonates, the technology is destroyed. The loss of the technology's benefit is not an active harm (a negative benefit) but opportunity cost that could have been achieved via other choices (thus being considered as active benefits in those choices instead). Therefore, $A_{\text{destroyed}} = 0$ for all groups.

### A.5 Choice 1: Surrender

#### Effect 1A — Family Experiences Stress from Being Taken Hostage

- Likelihood: $L = 1.0$
- Affected concern: Group 1 / Physical well-being / Short-term
- Moral importance: $M = 3(0.833) + 2(0.500) = 2.500 + 1.000 = 3.500$

**Table A4:** Effect 1A Possible Benefits

| PB   | Description                           | $b$      | $l$    | Chains               |
| ---- | ------------------------------------- | -------- | ------ | -------------------- |
| 1A-i | Acute stress (Somewhat low detriment) | $-0.333$ | $0.90$ | Technology preserved |

**Root moral worth:** $v(-0.333) = -0.333$, $H^{\text{root}} = -0.333 \cdot 3.500 = -1.167$

**Chain effects:** Surrender enables the ransom, which makes preserving the technology 95% likely; there remains a 5% chance of accidental or spiteful detonation, however. Preserving the technology would affect the long-term health of all three groups.

$$c = 0.95(A_{\text{preserved}}) + 0.05(A_{\text{destroyed}}) = 0.95(1.749) + 0.05(0) = 1.662$$

**Combining:**
$$H^{\text{raw}} = -1.167 + 1.662 = 0.495$$
$$H = l \cdot H^{\text{raw}} = 0.90 \cdot 0.495 = 0.446$$

The moral value of Effect 1A is therefore: $A_{1A} = 0.446$.

#### Moral Valence of Choice 1

Since Choice 1 only involves Effect 1A, the moral valence of Choice 1 is: $$V_1 = 1.0 \cdot 0.446 = 0.446$$

### A.6 Choice 2: Flee

#### Effect 2A — Risk of collision with hostages

- Likelihood: $L = 0.30$
- Affected concern: Group 2 / Physical well-being / Short-term
- Moral importance: $M = 4(0.500) + 2(0.333) = 2.000 + 0.667 = 2.667$

**Table A5:** Effect 2A Possible Benefits

| PB    | Description                           | $b$      | $l$    | Chains |
| ----- | ------------------------------------- | -------- | ------ | ------ |
| 2A-i  | Severe injury (Very high detriment)   | $-0.833$ | $0.50$ | None   |
| 2A-ii | Minor injury (Somewhat low detriment) | $-0.333$ | $0.50$ | None   |

Since detonation is a consequence of fleeing, it is represented in parallel effects (2B-2D) rather than as a chained effect of colliding with the hostages.

**PB 2A-i:** $H^{\text{root}} = -0.833 \cdot 2.667 = -2.222$, $H = 0.50(-2.222) = -1.111$
**PB 2A-ii:** $H^{\text{root}} = -0.333 \cdot 2.667 = -0.889$, $H = 0.50(-0.889) = -0.444$

Effect moral value: $A_{2A} = -1.111 + (-0.444) = -1.556$.

#### Effects 2B–2D — Bomb outcome as direct effects

Fleeing triggers an 80%/20% detonation/non-detonation split independently of the collision. Three direct effects capture the bomb's consequences on each group's long-term health. When the bomb detonates, the group receives no benefit ($b = 0$); when it does not, the preservation benefit partially accrues.

**Table A6:** Direct Bomb Effects (Choice 2)

| Effect | Group | $M$     | Det. ($l=0.80$, $b=0$) | Non-det. ($l=0.20$, $b=+0.50$)        | $A$     |
| ------ | ----- | ------- | ---------------------- | ------------------------------------- | ------- |
| 2B     | G1 LT | $2.667$ | $0.80 \cdot 0 = 0$     | $0.20 \cdot 0.50 \cdot 2.667 = 0.267$ | $0.267$ |
| 2C     | G2 LT | $1.667$ | $0$                    | $0.20 \cdot 0.50 \cdot 1.667 = 0.167$ | $0.167$ |
| 2D     | G3 LT | $0.667$ | $0$                    | $0.20 \cdot 0.50 \cdot 0.667 = 0.067$ | $0.067$ |

#### Moral Valence of Choice 2

$$V_2 = 0.30(-1.556) + 0.267 + 0.167 + 0.067 = -0.467 + 0.501 = 0.034$$

### A.7 Choice 3: Attack

The driver accelerates toward the hostage-takers. There is a 70% chance that the hostage-takers are incapacitated such that detonation is prevented; there is a 30% chance that the hostage-takers retaliate and detonate the bomb.

#### Effect 3A — Attack succeeds: hostage-takers incapacitated ($L = 0.70$)

- Affected concern: Group 3 / Physical well-being / Short-term
- Moral importance: $M = 4(0.333) = 1.333$

**Table A7:** Effect 3A Possible Benefits

| PB     | Description                          | $b$      | $l$    | Chains               |
| ------ | ------------------------------------ | -------- | ------ | -------------------- |
| 3A-i   | Severe injury (Very high detriment)  | $-0.833$ | $0.50$ | Technology preserved |
| 3A-ii  | Moderate injury (Moderate detriment) | $-0.500$ | $0.30$ | Technology preserved |
| 3A-iii | Minor injury (Very low detriment)    | $-0.167$ | $0.20$ | Technology preserved |

For each possible benefit of this successful attack, there is a 95% chance of the detonation being averted (enabling the benefits of the technology), and 5% chance of accidental detonation.

$$c_{\text{success}} = 0.95(1.749) + 0.05(0) = 1.662$$

**PB 3A-i:** $H^{\text{root}} = -0.833 \cdot 1.333 = -1.111$, $H^{\text{raw}} = -1.111 + 1.662 = 0.551$, $H = 0.50(0.551) = 0.276$

**PB 3A-ii:** $H^{\text{root}} = -0.500 \cdot 1.333 = -0.667$, $H^{\text{raw}} = -0.667 + 1.662 = 0.995$, $H = 0.30(0.995) = 0.299$

**PB 3A-iii:** $H^{\text{root}} = -0.167 \cdot 1.333 = -0.222$, $H^{\text{raw}} = -0.222 + 1.662 = 1.440$, $H = 0.20(1.440) = 0.288$

Effect moral value: $A_{3A} = 0.276 + 0.299 + 0.288 = 0.863$.

#### Effect 3B — Attack fails: family injured ($L = 0.30$)

- Affected concern: Group 1 / Physical well-being / Short-term
- Moral importance: $M = 3.500$

**Table A8:** Effect 3B Possible Benefits

| PB    | Description                          | $b$      | $l$    | Chains             |
| ----- | ------------------------------------ | -------- | ------ | ------------------ |
| 3B-i  | Severe injury (Very high detriment)  | $-0.833$ | $0.40$ | Technology outcome |
| 3B-ii | Mild injury (Somewhat low detriment) | $-0.333$ | $0.60$ | Technology outcome |

For either possible benefit of this failed attack, there is an 80% chance of detonation and a 20% chance that the hostage-takers were bluffing all along.

$$c_{\text{fail}} = 0.80(0) + 0.20(1.749) = 0.350$$

**PB 3B-i:** $H^{\text{root}} = -0.833 \cdot 3.500 = -2.917$, $H^{\text{raw}} = -2.917 + 0.350 = -2.567$, $H = 0.40(-2.567) = -1.027$

**PB 3B-ii:** $H^{\text{root}} = -0.333 \cdot 3.500 = -1.167$, $H^{\text{raw}} = -1.167 + 0.350 = -0.817$, $H = 0.60(-0.817) = -0.490$

Effect moral value: $A_{3B} = -1.027 + (-0.490) = -1.517$.

#### Moral Valence of Choice 3

$$V_3 = 0.70(0.863) + 0.30(-1.517) = 0.604 + (-0.455) = 0.149$$

### A.8 Preferability

**Table A9:** Moral Valences

| Choice               | $V$     |
| -------------------- | ------- |
| Choice 1 (Surrender) | $0.446$ |
| Choice 3 (Attack)    | $0.149$ |
| Choice 2 (Flee)      | $0.034$ |

$V_{\max} = 0.446$, $V_{\min} = 0.034$.

**Normalized relative preferability:**

$$P_1 = \frac{0.446 - 0.034}{0.446 - 0.034} = 1.00$$
$$P_3 = \frac{0.149 - 0.034}{0.412} = \frac{0.115}{0.412} = 0.279$$
$$P_2 = 0.00$$

**Absolute preferability** ($V_{\max} > 0$, anchored to $V_{\text{ref}} = 0$):

$$P_1^{\text{abs}} = \frac{0.446}{0.446} = 1.00$$
$$P_3^{\text{abs}} = \frac{0.149}{0.446} = 0.334$$
$$P_2^{\text{abs}} = \frac{0.034}{0.446} = 0.076$$

**Table A10:** Qualitative Mapping (per Table 2, §2.4.1)

| Choice   | Relative $P$ | Qualitative (relative) | Absolute $P^{\text{abs}}$ | Interpretation                                              |
| -------- | ------------ | ---------------------- | ------------------------- | ----------------------------------------------------------- |
| Choice 1 | $1.00$       | Extremely preferable   | $1.00$                    | Best achievable                                             |
| Choice 3 | $0.28$       | Very unpreferable      | $0.33$                    | Distant second; near-neutral in absolute terms              |
| Choice 2 | $0.00$       | Extremely unpreferable | $0.08$                    | Marginally above neutral in absolute terms; worst available |

### A.9 Interpretation

The ethic prescribes Choice 1 (surrender) as clearly preferable, with Choice 3 (attack) as a distant second and Choice 2 (flee) as the worst option.

Choice 1's positive moral valence ($+0.446$) reflects a favorable tradeoff: the family's short-term stress ($-1.17$ root) is more than offset by the expected long-term health benefit of preserving the technology across all three groups ($+1.66$ chain).

Choice 2 is marginally positive ($+0.034$) but ranked last. The 30% risk of injuring hostages contributes $-1.56$ when realized, and the 80% probability of destruction eliminates most of the preservation benefit. However, the 20% chance the hostage-takers are bluffing preserves some expected value ($+0.50$ across the three direct bomb effects). Critically, because destruction is modeled as the non-occurrence of a potential benefit rather than as an active harm, fleeing does not produce a catastrophic negative valence — merely a near-zero one.

Choice 3 occupies the middle ($+0.149$). When the attack succeeds (70%), the hostage-takers' injuries are more than offset by technology preservation ($+0.86$). When it fails (30%), the family's injuries ($-2.57$ root) are partially mitigated by the 20% bluff chance ($+0.35$ chain). The expected value is positive but substantially lower than Choice 1's.

This trilemma illustrates two structural modeling principles. First, causally downstream consequences are best modeled as chain effects; causally independent consequences as direct effects. Second, the signed-magnitude approach treats foregone potential benefits as zero, not as active harms; opportunity cost manifests as the value of these potential benefits that other choices would have engendered (a choice preventing a good outcome is not equivalent to the choice actively causing a bad one).

Choice 2's near-zero valence depends on modeling foregone technology benefits as opportunity cost ($A_{\text{destroyed}} = 0$) rather than active harm. Reframing detonation as active loss would substantially lower $V_2$ and widen the gap between Choices 1 and 2, though the ranking order in this framing is unchanged (see §A.10). This illustrates that framing conventions — not only normative priorities — drive prescriptions.

All three choices produce positive moral valences because the technology's expected benefit ($1.749$ when preserved) dominates the expected harms. The gap between Choice 1 and the alternatives — $0.45$ in absolute valence, $0.72$ in relative preferability — shows that the ethic meaningfully distinguishes among them even when none is catastrophic.

### A.10 Sensitivity Analysis

**Table A11:** Ranking Stability Under Parameter and Framing Perturbations

| Perturbation                                                 | $V_1$           | $V_2$           | $V_3$           | Ranking   | Notes                                           |
| ------------------------------------------------------------ | --------------- | --------------- | --------------- | --------- | ----------------------------------------------- |
| Baseline ($\lambda = 1$; opportunity-cost framing)           | $0.446$         | $0.034$         | $0.149$         | 1 > 3 > 2 | Values from §A.5–A.8                            |
| Loss aversion ($\lambda = 2.25$)                             | $\approx 0.41$  | $\approx -0.12$ | $\approx 0.09$  | 1 > 3 > 2 | Negative root worth amplified; $V_2$ falls most |
| Active harm for detonation ($A_{\text{destroyed}} = -1.749$) | $\approx 0.446$ | $\approx -0.38$ | $\approx 0.149$ | 1 > 3 > 2 | $V_2$ crosses below neutral; order unchanged    |

The ranking is stable across these perturbations in this conflict, but the absolute positioning of Choice 2 is highly framing-sensitive. An ethic invoking loss aversion or treating foregone benefits as active harms would assign substantially lower absolute preferability to flee — without necessarily altering the ordinal prescription.

## References

Aristotle, & Crisp, R. (2014). _Nicomachean ethics_. Cambridge University Press.
Ellsberg, D. (1961). Risk, ambiguity, and the Savage axioms. _The Quarterly Journal of Economics_, 75(4), 643–669.
Gilligan, C. (1982). _In a different voice: Psychological theory and women's development_. Harvard University Press.
Gilboa, I., & Schmeidler, D. (1989). Maxmin expected utility with non-unique prior. _Journal of Mathematical Economics_, 18(2), 141–153.
Hare, R. M. (1952). _The language of morals_. Oxford University Press.
Kant, I. (1785/1998). _Groundwork of the metaphysics of morals_ (M. Gregor, Trans.). Cambridge University Press.
Mikhail, J. (2007). Universal moral grammar: Theory, evidence and the future. _Trends in Cognitive Sciences_, 11(4), 143–152. https://doi.org/10.1016/j.tics.2006.12.007
National Institute for Health and Care Excellence. (2013). _Guide to the methods of technology appraisal 2013_. NICE.
Nozick, R. (1974). _Anarchy, state, and utopia_. Basic Books.
Rawls, J. (1971). _A theory of justice_. Harvard University Press.
Sinnott-Armstrong, W. (2023). Consequentialism. In E. N. Zalta & U. Nodelman (Eds.), _The Stanford encyclopedia of philosophy_ (Winter 2023 ed.). Metaphysics Research Lab, Stanford University. https://plato.stanford.edu/archives/win2023/entries/consequentialism/
Social Security Act, 42 U.S.C. § 401 _et seq._ (2018).
Stevens, S. S. (1975). _Psychophysics: Introduction to its perceptual, neural, and social prospects_. John Wiley & Sons.
Tversky, A., & Kahneman, D. (1992). Advances in prospect theory: Cumulative representation of uncertainty. _Journal of Risk and Uncertainty_, 5(4), 297–323.
Trope, Y., & Liberman, N. (2010). Construal-level theory of psychological distance. _Psychological Review_, 117(2), 440–463.
U.S. Department of Health and Human Services, Office of the Assistant Secretary for Planning and Evaluation. (2016). _Guidelines for regulatory impact analysis_. HHS.
von Neumann, J., & Morgenstern, O. (1944). _Theory of games and economic behavior_. Princeton University Press.
Williams, B. (1973). A critique of utilitarianism. In J. J. C. Smart & B. Williams, _Utilitarianism: For and against_ (pp. 73–150). Cambridge University Press.

# Bounds, reference learners and information accounting

This page owns the theoretical assumptions behind learning and performance comparisons. Revised 2026-11-16:
the earlier notes mixed useful heuristics with claims about any possible brain. The distinctions below qualify
those claims. Measurements belong in the line notebooks; priorities belong in [QUESTIONS.md](QUESTIONS.md).

## The ideal observer

An ideal observer infers an unknown from specified evidence under a specified model and prior. An optimal
controller must additionally choose actions, which affect both future rewards and future observations. These
are different problems. Describe a reference by its observation history, prior/model family, supplied parameters,
action set, computational budget, horizon and objective.

| comparison | what it can establish | what it cannot establish by itself |
|---|---|---|
| Hand-designed or told controller | An achievable behaviour given its supplied knowledge | That a finite learner can acquire that knowledge through its own actions in time |
| Bayesian filter on recorded observations | Inference quality conditional on that model, prior and history | Optimal exploration or control, or optimality outside that model family |
| Implemented approximate learner | A reproducible reference level under declared assumptions | A bound on every possible learner; failure does not prove impossibility |
| Proven optimal controller or analytical bound | A bound within the specified assumptions and objective | Universality when those assumptions change |

The same sensor interface does not ensure equal information: one controller's actions may generate much more
useful evidence. A model of the world's rule family is prior knowledge even if its parameters are learned in
life. Report this advantage. A reference may still be valuable without being fair in every respect, provided
its role is explicit.

**Data processing.** For a fixed prior and policy, internal states computed only from the received history and
independent private randomness cannot add information about an external unknown beyond that history. They can
make its information easier to use. This statement does not allow an observer to read private world state or
ignore the effect of actions on the next observations.

## What the bits refer to

Name the unknown Z needed for a decision and the available history H: senses, actions and tastes with their
actual timing. Distinguish uncertainty in Z, information acquired about Z, predictive code length, and reward.
The length of our simulator program is not the uncertainty the robot must resolve.

For a declared model, expected information gained about Z is the reduction in its entropy, or equivalently the
expected change from prior to posterior measured by relative entropy. Condition this on the policy and prior.
An empirical decoder's success demonstrates accessible information under its training assumptions; its failure
does not prove that no decoder could succeed. In-sample fits are not evidence of online learnability.

A binary symmetric channel with independent flip probability e has capacity 1 − H2(e) bits per use, with H2 the
binary entropy. This is a channel-model result, not a measured number of useful bits in every taste. Repeated,
correlated or selectively sampled observations need their own analysis; more sensor pulses do not automatically
mean more information about the relevant unknown. These distinctions use the information and Bayesian-inference
framework in [MacKay (2003)](https://www.snn.ru.nl/~bertk/machinelearning/book.pdf).

When an exact ideal learner is intractable, use a transparent approximation, a simplified problem with a bound,
or a successful informed construction. State the gap left by the approximation. Do not attach an exact bit
count to an unidentified model merely to fill a reporting requirement.

## Prediction, belief and action

A probability for a noisy taste is not a probability for the hidden food state. Under an explicit symmetric
flip model, if p is the probability of the hidden good state and e the independent flip probability, then
q = e + (1 − 2e)p is the probability of a good taste. This follows by conditioning on the two states. Scoring
q against the hidden state penalises a correctly modelled noise process.

Use log loss (−log2 probability of the realised target) for a declared prediction target; assess calibration
and useful decisions separately. A proper scoring rule rewards the true predictive distribution in expectation.
It does not guarantee rapid expert identification in a short noisy life, nor turn a predictor into a controller.
[Gneiting and Raftery (2007)](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf).

A vote whose feedback is the same noisy taste still has to learn through that channel. Conversely, a very small
predictive advantage may matter for decisions near an action boundary. D70–D71 therefore motivate separating
representation, scoring, selection and action; they do not justify abandoning probabilistic prediction.
The [notebook review](discrete/NOTEBOOK.md#review-2026-11-16) records the evidence and its limitations.

**Noise attenuation alone does not reverse a binary choice.** If the same independent error probability
`e < 1/2` applies to both states, `q − 1/2 = (1 − 2e)(p − 1/2)`. Choosing the larger probability therefore
gives the same colour using either target. A weighted average also preserves this identity if every expert
uses the same observation model. A predictor need not become confident to cross the action boundary.
Disagreements require different evidence, calibration, models or weights; small probabilities alone are not
an explanation. For two fixed recommendations on the same histories, their expected noisy-label accuracy
difference is `(1 − 2e)` times their hidden-state accuracy difference. Their *paired* comparison variance
depends on how often they disagree, not on two independent binomial variances. Attribution errors and
action-dependent labels can violate the common-noise assumption.

**The reward model matters too.** With reward +1 and poison cost C, expected gain from an attempted meal is
`(1 + C)q − C`. Choosing between two equally costly colours uses a probability threshold of one half;
choosing whether to eat at all uses `q > C/(1 + C)`. If a world's noise changes the scored meal value itself,
even knowing the hidden favourable colour gives at most `1 − (1 + C)e` expected gain per meal. This is a
bound on the gain numerator, not on every finite-sample efficiency ratio or on a different survival objective.
The concrete consequence for the opened drift ladder is in [D73](discrete/NOTEBOOK.md#d73-noisy-evidence).

**Changing state and changing model are different unknowns.** For a known symmetric two-state Markov
model with flip rate h per second, a posterior p propagates across a gap Δ seconds as
`p_before = 1/2 + (p_after − 1/2) exp(−2hΔ)`. Each independently corrupted binary observation then adds
`±log2((1 − e)/e)` to the log odds. This follows from the two-state forward filter; it stores a changing
state while its model parameters remain fixed. Learning h and e requires additional inference. Resetting
weights among experts instead expresses uncertainty over which *expert* is currently useful.
[Rabiner (1989), §III.A](https://www.cs.umb.edu/~rvetro/vetroBioComp/HMM/Rabiner1989%20A%20Tutorial%20on%20Hidden%20Markov%20Models%20and%20Selected%20Applications%20in%20Speech%20Recognition.pdf),
[Herbster & Warmuth (1998), figure 1](https://mwarmuth.bitbucket.io/pubs/J39.pdf).

In log odds the Markov prediction step is a nonlinear leak, stronger at high confidence. A linear leaky
sum is an approximation whose useful memory scale depends on evidence reliability as well as volatility.
[Veliz-Cuba, Kilpatrick & Josić (2016), §3.1](https://www.colorado.edu/amath/sites/default/files/attached-files/velizcuba_siamrev16.pdf)
derive this distinction. It explains why state filtering can be economical *given a model*. It does not show
how a generic local unit discovers that model, or establish that one filter family is sufficient for every task.

**Learning a representation's readout has a separate evidence cost.** Suppose a grouping M shares one
Bernoulli parameter among each of its context groups, with independent Beta(1/2,1/2) priors. Integrating
those parameters gives sequential likelihood P_M of the labels. A mixture with prior mass π(M) has
`P_mix ≥ π(M) P_M`, hence `loss_mix ≤ loss_M − log2 π(M)` on every sequence. This algebraic bound
requires causal contexts and scoring before update; it does not require that one of the models be true.
It bounds cumulative log loss, not final-third decision accuracy, nor the cost of computing the mixture.
The ordered-context construction is standard: [Willems, Shtarkov & Tjalkens (1996), §§I–III](https://pure.tue.nl/ws/files/1481823/Metis122606.pdf).
[D74](discrete/NOTEBOOK.md#d74-learned-sharing) demonstrates both the useful sharing and its finite-life
cost. Existing evidence for the hidden state does not imply enough evidence to identify a generic readout.

**Representation multiplicity is not independent evidence.** If m exact copies have the same forecasts,
likelihoods and waking pattern, conserving their aggregate initial weight preserves their contribution to
a likelihood-weighted mixture. Any ongoing redistribution must conserve their aggregate share too.
Giving each copy the original weight instead multiplies that family's initial odds by m; with all relevant
predictors awake this is log2(m) bits of prior odds, not acquired information. This follows by summing the
identical copies' updates and applies to awake-only normalization as well. The specialist update is given
by [Freund et al. (1997), §3.1 and figure 2](https://cseweb.ucsd.edu/~yfreund/papers/SpecializedExperts.pdf);
[D75](discrete/NOTEBOOK.md#d75-redundant-selection) checks the identity and its effect on the recordings.
Approximate redundancy, discovery of copy identity and the physical cost of extra units remain separate.

## Watching and intervening are one problem

Observed associations need not identify causal effects. The brain's own random variation can help isolate an
action's effect only when it has the relevant independence, coverage and causal structure. Calling a noise
source “an instrumental variable” does not establish those conditions: it must influence the relevant action,
have no other path to the outcome under the model, and be independent of the relevant confounders. Its exploration
can also cost reward and energy. There is no general free causal experiment supplied by noise.

Prediction on another controller's observations is not automatically off-policy evaluation of return. To assess
a different policy, establish coverage of its actions and the model or weighting assumptions that justify the
comparison. Otherwise use a paired intervention or label the result conditional on the recorded behaviour.

Dual control is the standard problem in which an action both controls and informs. It motivates comparing
natural observation, deliberate probes and their future value, rather than assuming “learn first, act later”
is always best. The classic causal-inference, off-policy and dual-control references from the previous notes
are literature leads to check for the specific experiment, not guarantees that our implementation is safe or optimal.

## How long a life must be

**Separating two effects.** As a rough calculation, suppose independent Poisson meal counts are observed for
duration t in *each* condition, with rates lambda1 and lambda2 in inverse seconds. The variance of the difference
of estimated rates is (lambda1 + lambda2)/t. A signal-to-noise target z then suggests
`t ≈ z² (lambda1 + lambda2) / (lambda1 − lambda2)²` seconds per condition. This is a fixed-sample normal
approximation derived from that model, not Wald's sequential test or a universal learning bound. Pairing,
overdispersion, temporal dependence, adaptive stopping and changing policies alter the calculation.

**Selecting among K hypotheses.** For fixed likelihoods on the same observed sequence, a mixture that gives
hypothesis j prior weight w_j has probability at least w_j times that hypothesis's probability. Its cumulative
log loss therefore exceeds that hypothesis's by at most −log2(w_j); uniform weights give log2(K). This is a
direct likelihood inequality, not a universal number of observations needed to identify a winner. Hypotheses can
be correlated, redundant, wrong, or distinguishable only after rare actions. A changing best hypothesis adds
assumptions and costs; see [Herbster and Warmuth (1998)](https://mwarmuth.bitbucket.io/pubs/J39.pdf).

**Occam factor.** Bayesian marginal likelihood averages over a model's parameter prior, penalising a good fit
confined to a small part of that prior. This differs from the discrete prior cost above. Neither licenses saying
that “260 candidates require eight bits” as a sufficient sample-complexity calculation for the robot. What must
be distinguished, the prior and the likelihood differences all matter.

**Time and behaviour.** Evidence rates measured under one policy are not upper bounds on all policies. A better
policy might gather more evidence, or pay more to gather it. State whether a duration concerns acquisition,
identification, useful control, or asymptotic estimation. Keep the existing last-third metric where its protocol
requires it, but report early learning costs and whole-life return too.

## The walls

A failure cannot diagnose a learning mechanism if the intended test supplies too little distinguishing evidence.
But failing a heuristic signal estimate is not itself a proof of impossibility.

- **Evidence limit:** identify competing hypotheses or behaviours and estimate their distinguishability under
  the actual observation and exploration policy. A formal impossibility result needs a specified class and bound.
- **Credit interference:** concurrent changes can obscure one another's effects. Measure how many units vary
  over a credit interval and the resulting variance. An N-fold penalty is a model-dependent approximation, not a
  general law; units learning the same fact and correlated perturbations are different cases.
- **Representation limit:** show which distinctions a representation cannot express, or give a counterexample.
  Cover's perceptron capacity result concerns random binary labels on inputs in general position and a linear
  threshold readout. Its roughly two labels per weight is not the memory capacity of an arbitrary recurrent,
  analogue or growing brain. See MacKay, chapter 40, in the source above. No conversion of this project's taste
  count into a universal number of learnable weights is justified.
- **Resource limit:** memory, energy, communication and latency can prevent useful adaptation even if information
  is available. Distinguish available, allocated, active and retained capacity; inspect the complete computation,
  including selection and normalisation, rather than only the repeated component.

## Time

Timing can carry information omitted by counts. Analyse events relative to the brain's own actions without
supplying a shared world clock. A count-based observer that fails to recover a spatial variable has not ruled
out recovery from event timing or a different action policy.

Separate **acquisition**, finding a plausible period and phase, from **tracking**, following an established
rhythm. A tracker can fail because acquisition never succeeded, the evidence is ambiguous, its representation
is wrong, or downstream selection ignores it. D23's short sweeps with multiple objects and D68's longer event
streams support different conclusions; neither establishes a universally best timing primitive.

Kalman filtering is optimal under particular estimation assumptions; the linear-Gaussian case is a standard
example. The robot's false-event gating and rhythm acquisition do not inherit that guarantee just because a
Kalman update is used. Before a further optimality claim, check the observation model, unknown associations,
period prior and uncertainty propagation. The named sources in D68 are leads for that detailed check, not a
completed proof of optimality here.

## Sources and verification status

The 2026-11-16 review checked primary-source text or indexed excerpts for MacKay's chapter-40 scope, proper
scoring rules, expert tracking and equivalence testing. The book's full PDF could not be opened by the web tool;
its indexed chapter excerpts were available. These checks support the limited distinctions above, not every
claim in the earlier literature notes. Mathematical examples explicitly described as derivations above are
conditional calculations for this review, not measured results.

Additional relevant primary sources:

- [Adams and MacKay (2007), Bayesian Online Changepoint Detection](https://arxiv.org/abs/0710.3742): an explicit
  model of changes and run length; exactness is conditional on its model. Abstract checked, implementation
  assumptions still to inspect before selecting it for an experiment.
- [Lakens (2017), Equivalence Tests](https://pure.tue.nl/ws/portalfiles/portal/80918653/lakeequi2017.pdf): why an
  undetected difference does not establish practical equality. Relevant sections checked. Protocol implications
  are in [GRAMMAR.md](GRAMMAR.md#interpreting-an-evaluation).
- [Chen, Goodfellow and Shlens, Net2Net](https://arxiv.org/abs/1511.05641): preserving a function while changing
  network architecture; abstract checked. The cost and exploration implications here are our qualifications,
  not a claimed theorem from that paper. See [PARTS.md](PARTS.md).

MacKay's chapters on Bayesian model comparison and evolution remain useful reading leads. Do not attribute an
inference to MacKay merely because it is written in bits; state its assumptions and what would falsify it.

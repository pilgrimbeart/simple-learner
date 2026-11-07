# The programme

One page to keep us on track. If work doesn't serve the question below, it is parked in `QUESTIONS.md`. `GRAMMAR.md` holds the detail.

## Why (the quest, `README.md`)

We want a general recipe for a brain that optimises itself: circuits that notice, by themselves, that they aren't doing well for the creature, and put it right, from simple local parts, ideally by emergence rather than by our design. Ten mismatches cured by hand (`STORIES.md`) gave one circuit that does the job of many, the bank of predictors: rival ideas of what taste means, all scored on every taste, the best followed. This programme asks whether that is a general principle or ten cures glued together.

## The question

**Does a brain facing many more challenges need proportionally more hand-built detectors, or do fewer general ones emerge?**

If it needs one for each, we have just hand-designed everything, and nothing interesting is emerging. If fewer will do, what are they, and why? Then: can hierarchy (detectors that learn about detectors) make the circuit find them itself, rather than us?

**In bits.** A life offers about 50 bits of evidence (D31), but a world's rule takes hundreds to write down (D33), so a brain can only learn what its structure already makes cheap: learning in a life is choosing and tuning within a repertoire. The question becomes how small a repertoire, made of how simple parts, covers how much. A repertoire of K rivals costs about log2 K bits of evidence to choose from (the Occam factor), and its description can be tiny if the rivals are drawn by a simple rule from simple parts, though it still costs parts and power to build.

## Where we are

**Decision B taken (the user, 2026-11-07): the bank makes its own rivals.** Stage 3 is done and checked independently: on fresh random worlds the bank's hand-written repertoire surely covers 12 of the 55 with something to learn and surely fails 24, coverage between .22 and .56; its failures are missing ideas, mostly about timing; one part (the eye filter, tuned to the eyes' usual rate) does harm where the eyes are more sensitive (`discrete/NOTEBOOK.md`, D35; `ABSTRACT.md`). Being firmed up (`lab/stage3_firm.py`): small gaps re-measured, doing no harm on every nothing-to-learn world, the reference at 1000 s. **Next: stage R**, below, in place of stage 4's hand-made cures.

**Gates, fixed before the results.** A gate that fails stops the work there, and it is reported, not argued round.

- **1c to 2:** (a) stage 1b's headline numbers replicate on fresh development seeds, or the differences are recorded and explained; (b) whether the bank's forgetting pays is settled by a measurement either way; (c) the taste limit is an upper bound with a proof, or called an estimate everywhere; (d) a pass definition is chosen on synthetic data, with its false yes and false no rates, before any real world runs.
- **2 to 3:** an independent check of the engine: with every change off, a world reproduces the unmodified lives exactly; each hand-written world behaves as its description says; each world's evidence is measured in bits, and how well planted near-duplicates are told apart is measured.
- **3 to B:** coverage on fresh worlds, in bits and with intervals, checked by an agent that didn't produce it. Held-out seeds and sealed sets stay closed: stage 3 uses neither the sealed sets nor anything but development draws until the user decides at B.

## The stages

Each ends with a result and a decision by the user. **No stage starts without that decision.** We commit only to reaching decision B; the rest is a sketch.

| stage | what | ends when | what it decides |
|---|---|---|---|
| 0 | Settle the primary result; seal an outside test set and a held-out split | all written down | A: start |
| 1 | Synthetic controls: test the analysis on invented data with known answers | it recovers the known answers, or we learn it can't | stop, or change the analysis, or go on |
| 1b | **The budget in bits**: what a life can supply, and the bank against an ideal Bayesian learner | we know how much of each world is learnable in principle, and how much the bank wastes | whether stage 2's worlds need reshaping |
| 1c | **Repeat what 1b assumed**: ideal learners that allow change, the bank's floor where a rule starts mid-life, a proven limit on tastes, synthetic worlds that can't be fully passed | the gate above | the labels and pass bar stage 2 uses |
| 2a | A minimal language and engine; about 30 worlds by hand, each labelled in bits | the engine is proven against the unmodified world | go on to random worlds, or fix the language |
| 2b | The frozen reference; about 100 random worlds; near-duplicates; real sigma and cost per world | we know what share of random worlds are learnable, and the cost per world | whether random worlds are worth using at all |
| 3 | **The present circuit, unchanged, on fresh worlds; then longer lives on about 30** | a coverage number exists | **B: the main decision.** What's uncovered, and is it worth continuing? |
| R | **Rivals made, not written** (decision B): the bank's rivals assembled from many simple parts connected in various ways, hierarchies included (counters of toggles, an oscillator driving a toggle, a timer gating a counter); first drawn at birth, then grown in the life where no rival predicts | below | whether a repertoire from simple parts covers what the written one does and more, at what cost in evidence and parts |
| 4 | (parked at B) Add cures, by a separate designer, to the largest groups of failures | | |
| 5 | The rule-changing worlds; types | to be planned later | |

## Stage R: rivals made, not written

**What a rival is.** Every rival in today's bank is a *context* and a *table*: a signal that takes one of k values (the count of good tastes mod n), and a learned bit for each value saying which colour is food then, with a tally of trust. A made rival keeps the table and builds the context from simple parts, each a block a circuit can hold:
- a **toggle** (flips on each input event), so a chain of toggles is a binary counter (k = 2, 4, 8);
- a **counter that resets** at n (k = n), for counts not a power of two;
- an **oscillator** of period T, read in phase bins (k bins), so a toggle driven by it has period 2T;
- a **timer** since an event (a taste, a good taste), read as before or after its delay;
- a **conjunction** of two contexts (their product: k1 x k2 values), the way hierarchies form.

Inputs are only what a brain already has: tastes, good tastes, its own clock (oscillators and timers in seconds, never ticks), with each part's own mismatch and the oscillators' phase noise. A rival is scored exactly as today's are (evidence where it disagrees with the default), so it is judged on every taste without being acted on.

**Steps, each with its predictions written first and its gate:**
1. **R1, the parts reproduce the bank.** Today's seven rivals rebuilt from these parts give identical lives. Gate: identical.
2. **R2, drawn at birth.** K rivals drawn at random by a fixed rule (parts and depth, periods and delays log-uniform over ranges fixed in seconds before any run), the bar to adopt a rival rising with log2 K as the Occam factor requires, derived, not tuned. Measured on stage 3's worlds (development: base, told and reference lives already exist on the same seeds): coverage, doing no harm, and false picks against K (1, 10, 100, 1000), with the number of matching rivals a world needs worked out first. Gate: a K is found that covers surely more than the written bank with no harm, or the reason none can is measured.
3. **R3, grown in the life.** Start with few parts; where the followed rival keeps being contradicted (frustration), grow a new rival by connecting a part to an existing rival's context (function-preserving: it starts with no evidence). Compared with R2 at equal parts. Gate: grown ties or beats drawn at equal parts, or the reason is measured.
4. **R4, judged on worlds never seen**: a fresh draw from stage 3's generator (development numbers 300-499, fixed now), then, at the user's decision, the sealed outside set and held-out seeds.

**In bits, for every step:** the evidence each world offers about its rule (the told arm's tastes), the Occam cost of K, how many of the K rivals fit each world, and the parts and power of the repertoire. The eye filter's fault (D35) is left as it is in R, so comparisons stay with the written bank; it is the next cure.

## The primary result

Chosen before any data, the one result we judge by. Everything else explains it and can't overturn it. Stage 1 showed the first wording couldn't tell the truth (`discrete/NOTEBOOK.md`, D30).

**The design is fixed, and the circuit still learns.** Every life starts fresh and adapts in that life; what's held fixed is only what a designer may change between worlds. To test any level, hold fixed the level above it: a circuit's state adapts with its design fixed; a design adapts with the paradigm fixed.

- **F_novel:** on challenges the design never saw, the pass rate above the base circuit's, as a share of what the base circuit leaves.
- **R:** the description added by the cures, against what one fixed-size cure per challenge would cost.
- **A pass:** a world passes if x > max(.5 r, .25). x is the circuit's fraction of the gap, measured from the larger of base and 0 (so standing still gains nothing) up to a policy told the rule; r is the same for a **reference**, a Bayesian learner frozen before any world it judges runs, its family, prior in bits, likelihood and tie rule all written down. The gap to told is always reported beside it. A told bar alone makes a yes nearly unreachable; a reference alone can be gamed by one cheap half-working cure; hence the .25 (D32). Worlds the reference can't help fail at the floor: this errs towards no.
- **Doing no harm:** in a world with nothing to learn, the lower 95% bound of (circuit - base) stays above -.1 efficiency. The -.1 is a choice, about the interval's half-width at 200 pairs. Scoring above base there isn't counted as learning.
- **Measurement:** the verdict needs about se .1 per world, about four times the lives planned (D32). Real sigma comes from stage 2.
- **The verdict rests on the sealed outside set.** A grammar of K bits can be built into a circuit of about K bits however many worlds it generates, so a yes on our own worlds is guaranteed in principle and proves nothing. Our own worlds are for development, and their numbers are reported as such.
- **Yes:** on the outside set, the 95% lower bound of F_novel is above a half, and the upper bound of R below a half, with at least 30 novel challenges.
- **No:** the upper bound of F_novel is below 0.2.
- **In between:** anything else, reported as measured.
- **Same shape, retuned by hand:** R below a half without F_novel. Not a yes, but a finding of its own: those settings are what a higher level could learn. If the circuit retunes the shape itself, it passes F_novel and counts.

**In bits, for every world**, as the explanation: the evidence available on the wires; how much the circuit used; what an ideal Bayesian learner with the same evidence would do; and bits built in by design against bits gathered in life. A life has a budget: at most a bit a taste, truly 0.25-0.83, about 15-50 bits at the bank's rate of tastes, and several times more for a brain that eats faster, since the body has no firing cap; telling N worlds apart takes at least log2 N bits (D31, D32). Say "too short at this rate", not "for any brain", unless a difference never shows within the life. A world outside a learner's prior costs extra evidence, about log2 of one over its prior probability, so "we built detectors for the grammar" has a graded measure: how many extra bits does an outside world take?

Description length: LZMA size, given a frozen corpus, of a canonical form (D30). The vocabulary is invented so far, and to be fixed before any real world runs.

## Keeping it simple as we go (stage 4)

We boil down during the search, not at the end, when nobody could reason about the result.

1. **Widen first.** Before building a new part, try extending an existing one. A new part must show that widening can't do the job.
2. **Merge at three.** When three cures share a shape, stop and try to merge them. The merged version must tie with the originals. Two may be a coincidence.
3. **Cap the motifs.** A low limit on distinct kinds of mechanism, so adding one means retiring or merging another.
4. **Prune after every addition**, removing anything that costs nothing to remove, then re-run all earlier worlds and the unmodified world.

## Sealed before anything is built

- **The outside test set:** two files. `lab/sealed/outside_set2.md`, the primary, written under the tighter seal on Sonnet (`lab/blind_agents.sh`; reply in `lab/v/outside_set2_reply.log`): SHA-256 `2050ebb03183f0343a6e3c1f94934452aaa1c8d07f001b9f3b36b1b31ae93368`, 45 entries, 36 keeping the current rules; several sources confirmed from search results only. `lab/sealed/outside_set.md`, a second test, by a fresh agent from outside sources. **Nobody building the language, the engine or the cures reads it** until stage 4 ends. SHA-256 `f72a1addf3347b2779b7e2c6e62432fd01bea2254a50d8e39038fcf21c95db13`; 44 entries, 37 keeping the current rules. **The seal isn't perfect:** the agent opened no repository files, but the harness gave it `AGENTS.md`, the memory index and a git status at the start, so it saw the rules and some file names. Many older papers are confirmed by bibliographic record only; each entry says what was checked.
- **The held-out worlds:** world number n, from any sampler, is held out if the first byte of SHA-256 of `world:n` is divisible by 4 (a quarter of them). Fixed now, so that it can't be chosen later.
- **Seeds for lives:** development 60000-69999 (spent by stage 2c), then 80000-89999 (opened 2026-11-06 for stage 3); held out 70000-79999. Seeds below 60000 are spent.

## How we work

- **The main session** keeps this page, talks with the user, makes judgements, and since 2026-11-06 does the work itself (the user: sub-agents cost too many tokens and fought for the cores).
- **An agent only where independence is the point** (a gate's check, the sealed set's author, the cure designer), with a written brief, asked of the user first; it reports in under a page, with file paths and what it found surprising.
- **Agents kept apart for honesty**: the outside test set's author and the cure designer see only what their brief gives them.
- **Going off the brief:** an agent stops and reports. It doesn't chase what it finds. New questions go to `QUESTIONS.md`.
- **The test before starting anything:** which row of the stages table does this serve? If none, park it.
- **The existing rules hold** (`AGENTS.md`): one long job at a time; push only on the user's "Push"; show working behaviour live before reporting; record findings in the notebook.

## Decisions (add as made)

| date | decision | by |
|---|---|---|
| 2026-11-04 | Rule-changing worlds only after testing within the current constraints | the user |
| 2026-11-04 | Marks left in the world: not yet | the user |
| 2026-11-04 | The brain's own parts are a link | the user |
| 2026-11-04 | Use fresh agents; no blind worlds from the user | the user |
| 2026-11-04 | This page's question and way of working; commit only as far as decision B | the user |
| 2026-11-04 | Boil down as we go, by the four rules; judge by description length, parts second; start (decision A) | the user |
| 2026-11-04 | F_novel and R replace the first wording, judged on the sealed outside set; motifs count only if the circuit retunes them itself; 0.2 is the line for no; bits analysis before stage 2 | the user |
| 2026-11-04 | Hold ourselves to information-theoretic rigour in measuring and judging (MacKay) | the user |
| 2026-11-04 | Measure an ideal learner that holds a changing-rule model | the user |
| 2026-11-04 | Press on without waiting, up to B, each step proven first; stay self-critical, Bayesian, information-theoretic | the user |
| 2026-11-05 | Stage 1c's gate is met; the pass rule, doing no harm and se .1 adopted; stage 2 starts, as 2a then 2b, each with its own gate | main session, under the user's delegation |
| 2026-11-06 | Preliminary work at the 10 ms tick; final results by halving the step until they stop changing (AGENTS.md); lives of 1000 s for the tests that need them | the user (tolerance and details mine) |
| 2026-11-06 | No in-life change to the brain or the brain-body link yet (rewiring by any route is out); every change is in the environment | the user |
| 2026-11-06 | The main session does the work itself, without sub-agents (tokens, cores); an independent check only when a gate needs one, asked first | the user |
| 2026-11-06 | A world's description length judges nothing: near-duplicates are judged by their lives, and a world's size is the count of the generator's blocks it was drawn with, reported only | main session, prompted by the user |
| 2026-11-06 | Stage 3's worlds from lab/stage3_gen.py (2b's generator in the 2c language; body constructs fixed from birth, by the user's rule), frozen before drawing; development seeds 80000-89999 | main session, under the user's delegation |
| 2026-11-06 | A thruster costs when it fires, whoever made it fire; a command the world drops costs nothing (the break is between brain and thruster) | the user |
| 2026-11-06 | Stage 3 keeps a world out if 3 or more of its 16 labelling lives carry a stage-5 label | main session, before stage 3's lives |
| 2026-11-06 | One independent agent checks stage 2c (interface by construction, instruments, seconds, speed) before stage 3; final runs in seconds at about 1.25 ms; the reference only on worlds with a gap, at 2.5 ms | the user (approving the main session's plan) |
| 2026-11-07 | One independent agent checks stage 3's coverage (the gate "3 to B"); the gaps it found are filled before the result is final | the user |
| 2026-11-07 | Decision B: next, the bank makes its own rivals from simple parts connected in various ways, hierarchies included (stage R); stage 4's hand-made cures parked | the user |
| 2026-11-07 | Rules about time may need far longer lives; long lives may be our equivalent of deep learning's scale, so stage R measures coverage against life length as well as K; lives of 10,000 s allowed for that (AGENTS.md) | the user |
| 2026-11-06 | Stage 2a is done (engine identical to the unmodified lives, worlds checked against their descriptions, labelled in bits); stage 2b starts, owing the independent engine check; the finer-step move goes to the user, and stage 3's headline is repeated at 5 ms | main session, under the user's delegation |

## Parked, for later

- A learning adversary, GAN-style (`QUESTIONS.md`, the arms race): after stage 3, as a generator of worlds we couldn't think of.
- Hierarchy beyond rivals' contexts (detectors that learn which detectors to grow): after stage R.
- The eye filter's built-in rate (D35): a cure after stage R.
- A richer world: only once this one has taught us everything it can.

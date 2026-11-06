# The programme

One page to keep us on track. If work doesn't serve the question below, it is parked in `QUESTIONS.md`. `GRAMMAR.md` holds the detail.

## The question

**Does a brain facing many more challenges need proportionally more hand-built detectors, or do fewer general ones emerge?**

If it needs one for each, we have just hand-designed everything, and nothing interesting is emerging. If fewer will do, what are they, and why? Then: can hierarchy (detectors that learn about detectors) make the circuit find them itself, rather than us?

## Where we are

**Stage 2b, by agents: the frozen reference, about 100 random worlds, near-duplicates, and the engine checked independently.** Stage 2a built the language and engine and proved them against the unmodified world (`discrete/NOTEBOOK.md`, D33); the finer-step move it found in the unmodified world is the user's to decide (`QUESTIONS.md`). The user has handed over the decisions up to B (2026-11-04), each step to be proven first, so the main session takes them by the gates below and logs them. **The next decision that is the user's alone: B.**

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
| 4 | Add cures, by a separate designer, to the largest groups of failures, simplifying as we go | the primary result is reached or the budget is spent | less than 10x, or not, for immediate and truthful taste |
| 5 | The rule-changing worlds; types; hierarchy | to be planned at B or later | |

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
| 2026-11-06 | Stage 2a is done (engine identical to the unmodified lives, worlds checked against their descriptions, labelled in bits); stage 2b starts, owing the independent engine check; the finer-step move goes to the user, and stage 3's headline is repeated at 5 ms | main session, under the user's delegation |

## Parked, for later

- A learning adversary, GAN-style (`QUESTIONS.md`, the arms race): after stage 3, as a generator of worlds we couldn't think of.
- Hierarchy: stage 5, informed by what stage 3 and 4 leave uncovered.
- A richer world: only once this one has taught us everything it can.

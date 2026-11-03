# Stories

One page per performance issue X, each with the same five stages: a brain with no concept of X; the gap to X solved
perfectly; manual interventions; how the brain could detect the gap; the simplest circuit that detects and resolves it
in a life. General observations come once there are several. The rules of this phase are in `AGENTS.md`, the taxonomy in
`PARTS.md`, the methods behind each story in its notebook entry.

Numbers are body efficiency (meals gained per meal spent: `README.md`, Terms), in lives of 100 s, standard bodies, each
life drawing its own parts' tolerances, with 95% intervals. "Surely" means the interval of a paired difference excludes 0.

## The table (the user, 2026-11-03)

The output of this phase: one row per mismatch, then a search for one universal correction circuit. The base brain is story
1's circuit, one mismatch at a time. Each row tried the classes of `PARTS.md`, section 5, tuned on training seeds; a cure is
the simplest one tied with the best, in a paired comparison. All numbers here are from a final judge on seeds nothing was tuned
on or looked at (54000-54063 x 2: `lab/table_final.py`, `lab/table_settings.json`, `lab/v/table_final.log`; how each was reached:
`discrete/NOTEBOOK.md`, D28). Lives of 100 s, except 1,000 s in rows 2 and 8. Block model only; none yet watched live.

- **Base**: story 1's circuit, unchanged, in the new body or world (row 1: the same creature with taste wired to nothing).
- **Told**: the same movements, given free whatever the mismatch forces it to work out, so no learning cost. Not a ceiling: other
  movements can beat it. Rows 2, 8: told the colour, the balance corrected. Rows 3, 4, 5: told the right colour at each moment
  (5: and still for exactly 1 s). Row 6: the noise removed, so overstated. Rows 7, 9, 10: told the colour, the mismatch still there.
- **Plain test**: the automatic version in the unmodified world against the base brain, paired; it passes if the interval
  includes 0. Each automatic version was also run with both colours food, with the same result unless stated.

| # | how the body or world doesn't suit the base brain | base | told | best manual cure (its plain cost if left on) | automatic version | plain test |
|---|---|---|---|---|---|---|
| 1 | which colour is food differs each life | -3.38 | 2.75 | **Judge**: a tally of tastes, written only while driving: 2.72 (tied with told) | both eyes followed until the first bad, then that circuit: **2.73** | passes: +0.00 [-0.09, +0.11]; all food 6.70, as with taste unwired |
| 2 | unequal thrusters, each 0.5 to 2 | 0.31 | 2.55 | **Sense**: sweeps, 192 counters: 2.06 (-0.06) | sweeps once meals are short at two checks running: **1.95** | passes: -0.00 [-0.01, +0.01] |
| 3 | food colours swap every 10 s | -0.01 | 2.82 | **Judge**: no trust: 1.15 (-0.30) | trust falls for 40 s after a flip that ended 2 goods: **0.90** | passes: -0.01 [-0.02, +0.00] |
| 4a | food must alternate | -3.33 | 2.65 | **Store**: sequence memory, length 2: 2.46 (-0.12) | grows when poisons keep coming while driving: **1.77**; 400 s 2.23 | passes: exactly 0 |
| 4b | food must follow A, A, B | -2.71 | 2.63 | **Store**: length 3: 2.33 (-0.20) | the same: **0.58**; 400 s 1.83 | passes: exactly 0 |
| 5 | a meal within 1 s of the last is bad | -4.73 | 1.83 | **Use**: keep still 1 s: 1.74 (-0.82), tied with told | learns the pause from soon bads while driving: **0.63**; 400 s 1.27 | passes: -0.01 [-0.02, +0.00] |
| 6 | one eye also fires at random, 10 per s | 1.25 | 2.75 | **Judge**: that eye's pulse counts only with another within 20 ms: 1.87 (0) | each eye's threshold set by its own background rate: **1.74** | **fails narrowly**: -0.02 [-0.05, -0.01] |
| 7 | each meal is the other kind with chance 20% | 0.36 | 0.69 | **Store/Judge**: 4 steps of trust: 0.63 (0), tied with told | flips that bounce raise the trust: **0.56**, tied with manual; 400 s 0.72 | passes: +0.00 |
| 8 | a thruster weakens through life (log balance 0.001 per s) | 0.36 | 2.61 | **Judge**: jitter judged per drive: 1.76 (-0.98) | jitter only while meals are short over 200 s: **1.42** | passes: -0.00 [-0.00, +0.00] |
| 9 | one eye passes only a quarter of its pulses | 1.79 | 1.88, gap not sure | **Judge**: 3 steps of trust: 1.85 (0), +0.07 [+0.03, +0.11] | none needed: trust 3 costs nothing when left on | |
| 10 | food in mixed clumps | 0.41 | 0.84 | **Judge**: 3 steps of trust: 0.65 (0) | flips that bounce raise the trust: 0.50, +0.09 [+0.00, +0.18] | passes: exactly 0 |

**Ruled out as rows**: a sixth of the blocks: base 0.45, told 0.56, the best manual 0.51, resting no better; blocks drifting at 5
mm/s: base 2.49, nothing above it. Both on the earlier seeds (53100-53163 x 2).

**What held up, and where it falls short.**

- *Eight of the ten have an automatic version that helps and ties with the base brain in the plain world*: 1, 2, 3, 4, 5, 7, 8 and
  10, row 10's gain only just. Row 6's costs 0.02. Row 9 turned out to need little.
- *Row 1 first failed its own test.* With both colours food, story 1's circuit scores 4.55 against 6.70 with taste unwired: a learned
  bit ignores one eye even with nothing to avoid. Following both eyes until the first bad cures that and costs nothing in plain. So
  the other rows' "all food" comparisons are against a base that already pays this.
- *Each mechanism turned on in its own world and not in plain*, seen through 16 lives without a display (`lab/table_watch.py`): growth at 7-10 s
  in 16 of 16 lives (plain 0), the pause at 10 s in 16 of 16 (plain 2), the balance moving to a mean |x| of 0.41 and 0.73 (plain 0.00).
  Nobody has watched these on screen. `python lab/watch_ladder.py` shows the ladder's arms only.
- *The gates in rows 2 and 8 are absolute meal counts* (14 per 32 s, 15 per 32 s over 200 s), tuned on the standard body and world: exactly the
  kind of setpoint `AGENTS.md` warns about. A different body or world with fewer blocks would read as a permanent shortage.
- *The automatic versions pay in time.* Against the best manual cure: row 2 -0.11, row 3 -0.26, row 4a -0.68, row 4b -1.75, row 5
  -1.11, row 6 -0.13, row 8 -0.34, row 10 -0.15; row 7 tied. Rows 4, 5 and 7 close most of that by 400 s.
- *Large gaps remain below told* even by hand: rows 3 (-1.67) and 6 (-0.88, overstated) and 8 (-0.85).
- *Not exhaustive.* Each class had coarsely tuned arms, not every design. Rows 2, 5 and 8 have no separate Store arm (the sweeps'
  counters and the pause's timer are their own memory); rows 3 and 7's Store is one design each.
- *Seeds matter.* Base scores moved between seed sets (row 2's 0.67 to 0.31, row 10's 0.73 to 0.41), so read the paired differences.

## Every automatic version in every world (`lab/table_final.py cross`, `lab/v/table_cross.log`)

Difference from the base brain, 100 s (thrusters and ageing 1,000 s), fresh seeds. A star means surely different from 0; columns are worlds.

| version | plain | all food | thrusters | swap 10 s | alternate | A,A,B | digest | noisy | unreliable | ageing | clumps | weak |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sweeps when short (2) | -0.01 | 0 | **+1.65\*** | -0.02 | +0.22\* | +0.13\* | +0.45\* | -0.04\* | -0.05\* | +0.59\* | +0.01 | -0.04\* |
| jitter when short (8) | 0 | 0 | +1.02\* | 0 | 0 | 0 | 0 | 0 | 0 | **+1.06\*** | 0 | 0 |
| volatile trust (3) | -0.01 | 0 | -0.03 | **+0.91\*** | +0.90\* | +1.36\* | -0.23 | -0.04\* | -0.50\* | -0.02 | -0.21\* | -0.02 |
| grow the table (4) | 0 | 0 | 0 | -1.21\* | **+5.11\*** | **+3.29\*** | -0.25\* | +0.01 | -0.07 | -0.01 | -0.05 | -0.02 |
| learned pause (5) | -0.01 | 0 | +0.01 | -0.05\* | +0.27\* | +0.24\* | **+5.37\*** | -0.01 | -0.03 | +0.01 | -0.04 | 0 |
| eye threshold (6) | -0.02\* | -0.03 | 0 | -0.01 | +0.01 | +0.01 | 0 | **+0.49\*** | -0.01 | 0 | -0.03 | -0.01 |
| bounces raise trust (7, setting top 6) | 0 | 0 | +0.02 | -0.81\* | -0.17 | -0.42\* | +0.28\* | 0 | **+0.20\*** | -0.03\* | +0.09 | +0.03\* |

## Towards one universal circuit: conclusions so far

**What the table and matrix say.**

1. *Almost all mechanisms are harmless outside their own world, so a union is nearly free in the worlds that don't excite them.* Jitter, the
   eye threshold and the pause have no sure loss above 0.05 anywhere.
2. *The trouble is on the taste side, and it is about one question:* after a vouched bad, was the bit wrong, did the world change,
   or was the taste a lie? Volatile trust, growth and bounce-raised trust each answer it by their own rule, and they harm one another's worlds: growth
   -1.21 at swaps, bounce-trust -0.81 at swaps, volatile -0.50 where taste is unreliable.
3. *Some cures generalise.* Jitter alone recovers thrusters (+1.02, against sweeps +1.65) and ageing, so balance may need one mechanism.
   Volatile trust alone gets +0.90 and +1.36 in the sequence worlds. Sweeps add +0.45 in digest, presumably because a fast is a pause.
4. *Three alarms cover everything*: vouched bads, a meal shortage, an eye's background rate. The first has a natural zero (a bad while driving at
   food shouldn't happen) and so needs no setpoint; the shortage doesn't, and that is its weakness. The third is local to an eye.
5. *Trust 3 left on costs nothing in plain and helps rows 7, 9 and 10.* Trust matters only where the world changes, so the base's 1 is
   simply a poor default except in swap worlds.
6. *Immunise and Spend never won a row*, so a universal circuit needn't carry them.
7. *The cost is time.* Automatic versions lag by what they need to notice: mostly 7-10 s of bads, and long windows for balance.

**Hypotheses.**

- **H0, the union:** all seven parts together, each with its own trigger, is a universal circuit, at the price of interference. A baseline: if it
  works, it answers the question plainly; if it fails, where shows what must be shared.
- **H1, one taste node:** the interference disappears if one node, trust, is driven by what flips turn out to be (contradicted at once: taste
  lies, so more; confirmed after a run: the world changed, so less) and growth counts only the bads that this leaves unexplained. Then
  rows 1, 3, 4, 7, 9 and 10 share one circuit. It predicts swaps, alternation and unreliable taste leave different flip signatures.
- **H2, one table with contexts:** sequence, digest and swaps are all one thing: a tally of good and bad conditional on context (the position in a
  sequence, the time since the last taste), with "follow neither" as an outcome. Then the pause is not a separate part. The first bad being what closes both-eye following
  would be the same rule.
- **H3, generate and test:** a single alarm (bads, or a shortage) drives random trial of any knob (trust, pause, balance, table length, eye threshold),
  keeping what improves things. The simplest in principle and the most universal, since it knows nothing of the rows, but it may hit the noise wall
  within 100 s, so judged in long lives.

**The plan.** `lab/universal.py`; `discrete/NOTEBOOK.md`, D29.

1. Build H0/H1 as one brain, each part removable (`U`). Every world, plain and all food; each part removed in turn, to say what each buys.
2. Trace each conflict to its cause (flip signatures per world) before tuning: measure whether H1's premise holds at all.
3. Search knob settings across all worlds at once with lots of lives, scored by each row's recovery (0 at base, 1 at its best manual), its mean and its
   worst, less any plain cost. Longer lives where a part is slow.
4. Build H2 and H3 as alternatives, same tests.
5. Combinations of mismatches never seen together (thrusters + swaps, noisy eye + sequence...), as the real test of universality.
6. Judge the best of each on fresh seeds (55000 on), in each world, against each row's own automatic version and the base. Remove parts to explain
   each result. Success or failure gets an explanation by what each part did in each world.

## 1. Which colour is food (`discrete/NOTEBOOK.md`, D25)

Every arm here has the baseline's 1 s limit on a run (below: A flaw found by watching).

**The creature.** It can scan, drive at what it sees and roam, and it tastes every meal, but taste is wired to nothing.
Either eye starts a drive, so it eats both colours alike: **-3.38**.

**The gap.**

- There is 1 bit to learn: which colour is poison, the same all life.
- Any brain that ignores taste eats food and poison equally over paired lives, so it can't net above 0, which is what
  doing nothing scores. Everything above 0 must come from taste.
- Told the colour, the same creature scores **2.73** [2.65, 2.81]. That is the ceiling for these movements, a gap of
  6.11.
- Measured from its lives, what it senses carries **3.21 bits/s** of evidence about the bit, because one taste is often
  decisive: a poison just after only the followed eye has pulsed is worth 5.9 bits. A taste informs whichever bit is
  held, so no exploring is needed.
- A brain using that evidence exactly (an ideal observer with the same movements) scores **2.77** [2.69, 2.84], tied
  with being told, and finds the bit in a median 1.0 s. So in principle learning here costs nothing, and a 100 s life
  is far more than enough.

**Manual interventions**, chosen on training seeds and judged on seeds 50000-50063 x 2 (their settings tuned before the
run's limit, not tuned again):

| class (`PARTS.md`) | intervention | efficiency |
|---|---|---|
| none | taste wired to nothing | -3.38 |
| Immunise | do nothing, so the colour can't matter | 0.00 |
| Store | a bit flipped by any 2 poisons | 1.49 |
| Store | a bit flipped by a run of 1 / 2 / 3 poisons with no food between | 1.37 / 2.33 / 2.41 |
| Store | the same 3 poisons, the count fading instead | 2.27 |
| Store | a bounded tally (B, as designed) | 2.46 |
| Store | B's tally, tuned | 2.44 |
| Use | no bit: each eye judged by its own drives, ignored once bad | 1.42 |
| Use | the same, but the bad eye now ends a drive | 2.37 |
| Judge | B's tally written only by tastes during a drive (next) | 2.64 |
| Sense | not needed: the evidence arrives without probing | not tried |
| ceiling | told the colour | 2.78 |

Storing more evidence gets only so far, because the evidence stored is poor: B counts every poison, including those it
merely bumps into while scanning. Born with the right bit it flips wrongly in 20% of lives; born wrong it takes 2 s longer
to flip than it needs.

**Detection.** The gap shows in a specific signal: *a poison tasted while driving at what I think is food*. If the bit is
wrong this is common; if right, rare. B already holds "driving" as a node, so no new sense or tag is needed.

**The circuit.** One change to B: taste writes the tally only while a drive is on. A poison steps it up, a food down, by
at most one step of trust; a further step up flips the bit. Detection and the cure are the same node.

Judged on seeds 50200-50327 x 2, which chose nothing:

| | efficiency | when born wrong, first flip | when born right, ever flips |
|---|---|---|---|
| taste wired to nothing | -3.38 [-3.43, -3.34] | | |
| B | 2.43 [2.34, 2.52] | median 3.6 s, 90% by 9.8 s | 20% of lives |
| **the circuit** | **2.72 [2.64, 2.79]** | **median 1.4 s, 90% by 3.7 s** | **4% of lives** |
| ideal observer | 2.77 [2.69, 2.84] | median 1.0 s, 90% by 3.1 s | 2% of lives |
| told the colour | 2.73 [2.65, 2.81] | | |

The circuit is tied with being told (-0.01 [-0.08, +0.06]), surely above B (+0.29 [+0.21, +0.36]), and a little below the
ideal observer (-0.05 [-0.10, -0.01]). It closes the whole gap to being told, and every life born wrong flipped.

**Controls.**

- *Nothing to learn* (both colours food): 0 flips, tied with being told (4.41 against 4.42).
- *Nothing can be learned* (each meal food or poison by a coin): it can't tell. It flips 16.3 times a life and scores
  -2.21 against -2.16 for a fixed bit, where doing nothing would score 0. No detector here says "give up". This is the
  story's open limit, and the plateau-or-ceiling question in its plainest form.
- *A design's prior*: a bit assumes exactly one colour is poison, so in all-food lives it forgoes half the food (4.41
  against 6.81 for taste wired to nothing). The no-bit brain, which keeps both eyes unless one proves bad, pays nothing
  there.

**At component level** (`mixed_feedback.py`, silicon's noise, 10% mismatch, seeds 50200-50327 x 2; doubt's four numbers
polished on fresh seeds, the run's limit built as four elements and set by hand on training seeds): taste wired to nothing
-3.12, B 1.89 [1.78, 1.99], **the circuit 2.12 [2.02, 2.22]**, told 2.25 [2.11, 2.38] (the lives of a fixed bit that
happens to be right, so not paired with the circuit). The circuit is surely above B (+0.23 [+0.14, +0.32]). Its cost is
934 parts against 914, at the same 34 nW. **So the result stands in the more precise simulation**, a little further below
being told than in the block model.

**A flaw found by watching** (`discrete/NOTEBOOK.md`, D25): B's run had no timer, so a run along a closed line of the torus
could last over an hour. A 1 s limit on the run scores surely better in lives of 10,000 s (+0.15 [+0.11, +0.18]) and is tied
in lives of 100 s (+0.09 [-0.01, +0.21]), and is now part of the baseline.

**Watch it:** `python lab/watch_story1.py` shows a life born wrong, flipping at 0.7 s (without the run's limit).

## 2. My two thrusters are unequal (`discrete/NOTEBOOK.md`, D26)

This page's arms are told the colour. On the base brain, the learning circuit, see the table's row 2.

The flaw is introduced on purpose, to learn how a brain could compensate for it; the standard body keeps its thrusters
identical. Every arm is told the colour, so this story is about one thing.

**The baseline and the target**, against the size of the flaw (one thruster sqrt(a) times stronger, the other sqrt(a) times
weaker, seeds 51000-51063 x 2). The target is the same brain told its balance, each motor's rate set for a straight drive:

| one thruster against the other | baseline | target | gap [95%] |
|---|---|---|---|
| identical | 2.77 | 2.77 | 0 |
| x1.01 | 2.79 | 2.79 | 0.00 [-0.14, +0.14] |
| x1.03 | 2.59 | 2.75 | +0.16 [+0.01, +0.30] |
| x1.1 | 2.17 | 2.64 | +0.47 [+0.29, +0.65] |
| x1.25 | 1.06 | 2.78 | +1.71 [+1.56, +1.87] |
| x1.5 | -0.03 | 2.74 | +2.77 [+2.66, +2.89] |
| x2 | -0.78 | 2.49 | +3.27 [+3.13, +3.41] |
| x4 | -0.53, 70% stranded | 2.02 | +2.55 [+2.44, +2.65] |

On the bodies the project has used (each thruster drawn 0.5 to 2): baseline **0.21** [-0.08, 0.54], 18% stranded; target
**2.56** [2.44, 2.68], none stranded; gap +2.35 [+2.03, +2.66]. Restoring every firing to the standard body's, not just the
balance, adds nothing surely, so **the whole gap is one number**.

**How much there is to learn.** Near the target the score falls fast, and lopsidedly: at x1.25, an error of -0.05 in the
log balance costs nothing, -0.1 costs 0.36, +0.05 costs 0.58, +0.1 costs 0.98. The cause is the scan: mirroring it to the
other motor flips the curve. Probably (not measured apart) a drive curving against the scan's turn can have its lost block swept back into view, one
curving with it can't. So the balance is wanted to about 0.05, against a spread of 0.63: about **3.7 bits**, in one number
that differs in every life.

**Manual interventions**, lives of 2,000 s, seeds 51000-51031 x 2, where the baseline scores 0.26 and the target 2.47:

| class | intervention | efficiency |
|---|---|---|
| Immunise | the fixed brain's settings searched for these bodies (100 s lives, 51000-51063 x 2) | 0.91 [0.75, 1.09] |
| Judge | the balance jittered at each drive and judged by food seen (D19) | 1.34 [1.12, 1.53] |
| Sense | sweeps of its own, the period of what comes round again, exact histogram (D20) | 2.22 [2.05, 2.38] |
| Sense | the same with 192 / 96 / 64 / 48 / 32 / 24 / 16 counters | 2.24 / 2.11 / 1.96 / 1.80 / 1.70 / 1.55 / 1.17 |

Aiming a coarse estimate at the cheap side of the lopsided curve gained nothing (32 and 64 counters, training seeds).

**Detection.** Too few meals (D20's gate: under 8 in 32 s of foraging), so it sweeps only when eating badly.

**The circuit, so far.** Sweeps, gated by that, with a bank of counters. It closes 90% of the gap at 192 counters, 66% at 32:
**the price of precision is parts**. This is the least satisfying story: it is block-level only, far from "simplest", and on
this baseline its cost on a standard body has not been re-measured (D20: none). Not re-validated at component level.

## The ladder: harder tests, one change each (`discrete/NOTEBOOK.md`, D27)

The user's idea: each test one change to story 1's world, none accumulating. A rule says which colour is poison at each
moment (`lab/ladder.py`, a wrapper; `world.py` is untouched). Baseline: story 1's circuit. Target: the same movements told
the rule. All judged on seeds 52000-52063 x 2, which chose nothing; lives of 100 s. Block model only, not yet re-validated at
component level. `python lab/watch_ladder.py RULE ARM` watches any of them.

| test | baseline | target | best manual | automated |
|---|---|---|---|---|
| plain, for comparison | 2.73 | 2.67 | | |
| **swap every 50 s** | 2.42 | 2.72 | no better than the baseline | |
| **swap every 20 s** | 1.28 | 2.73 | no trust in the bit: 1.79 | one brain, below: 1.57 |
| **swap every 10 s** | 0.01 | 2.88 | no trust: 1.16 | 0.57 |
| **swap every 5 s** | -1.39 | 2.92 | no trust: 0.03 | -1.13 |
| **alternate colours** | -3.45 | 2.69 | sequence of 2: 2.53 | grown 1.52; 400 s lives 2.24 (target 2.63) |
| **pattern A, A, B** | -2.72 | 2.73 | sequence of 3: 2.30 | grown 0.53; 400 s lives 1.86 (target 2.55) |
| **digest: a meal within 1 s of the last is bad** | -4.84 | 1.73 | keep still 1 s: 1.68 | learned 0.80; 400 s lives 1.11 (target 1.74) |

### 3. A world that changes (swaps)

The interval between swaps is what matters. Story 1's one step of trust costs little at 50 s and everything at 5 s, and simply
removing it is the best thing found (+1.15 at 10 s, but -0.2 on a plain world, on training seeds). Trust that falls for 40 s after each
flip keeps most of both (`Volatile`). A clock that learns the period and flips ahead of the poison (what the target's gap invites)
**failed**, on three designs: it finds the period (4.7 s for 5, 9.5 for 10), but a flip that is early by what the noise of the
estimate allows costs as much as a flip that is late. By a rough sum a purely reactive brain pays about 1.4 s wrong per swap,
so 1.5 at most at 10 s and about 0 at 5 s. So what is left needs prediction, and we have not found how. Open.

### 4. A sequence (alternate, pattern)

**A sequence memory**: a counter that every good taste advances, each position holding which eye to follow and its own step of
trust, corrected by a poison while driving (`Cycle`). Length 1 is story 1's circuit; 2 solves alternate (2.53, tied with the
target: -0.16 [-0.35, +0.03]); 3 the pattern (2.30). Length 6, told neither, does plain 2.35, alternate 2.01, pattern 1.83. The
good taste matters: a good taste says the turn moved on, whatever was seen.

**Detect and grow** (`GrowSeq`): start at length 1. A leaky tally of poisons while driving; past 3 within about 10 s the
sequence grows one size (1, 2, 3, 6). It grows in 2 of 128 plain lives, none of them surely costing anything (+0.00), and settles at
length 2 on alternate in 116 of 128, length 3 on the pattern in 99. Its price is the time before it grows, about 10 s at a very bad score,
so it needs a longer life: at 400 s it reaches 2.24 of 2.63 and 1.86 of 2.55.

### 5. A rule about time (digest)

The colour is no use alone: told the colour, -3.84 (training seeds). Keeping still for 1 s after any meal closes nearly everything, with the bit learned as in story 1 (1.68,
tied with the target), by eating half as much, on time. Learned (`LearnPause`: a tally of bads soon after a taste, and the largest such gap): on in all 128
lives, median 6.9 s, last third 6.17 against the target's 5.73, but the whole life 0.80. In plain lives it turned on in 12 of 128 and cost
0.02 [0.00, 0.05]; over 400 s it costs plain lives surely more (-0.19 [-0.34, -0.06]).

### 6. One signal, several cures

Growth is the wrong cure for a world that swaps: it **costs** -0.24 at 20 s, -1.12 at 10 s, -0.51 at 5 s. A poison while driving says something is
wrong, not what. But the kinds of failure differ: in a sequence a poison follows few goods, in a swapping world many. So **one brain, reading the run of goods
before each poison** (`Diagnose`: at most 2, charge the tally that grows the sequence; more, drop trust for 40 s), held out against the baseline:

| test | efficiency | against the baseline | what it did |
|---|---|---|---|
| plain | 2.73 | +0.01 [-0.02, +0.03] | nothing, in all 128 lives |
| alternate | 1.63 | +5.08 [+4.83, +5.34] | length 2 in 126 |
| pattern | 0.36 | +3.08 [+2.90, +3.27] | length 3 in 105, 6 in 23 |
| swap 50 s | 2.39 | -0.03 [-0.08, +0.01] | length 1 in 127 |
| swap 20 s | 1.57 | +0.29 [+0.19, +0.40] | length 1 in 122 |
| swap 10 s | 0.57 | +0.56 [+0.39, +0.73] | length 1 in 102 |
| swap 5 s | -1.13 | +0.26 [+0.09, +0.44] | wrong: length 6 in 68. So few goods between swaps look like a sequence |
| digest | -4.94 | -0.11 [-0.33, +0.14] | wrong: length 6 in 127, no cure on its menu |

The first combination of cures, and the first case of a brain choosing among them. Its failure at digest is a menu's failure: it doesn't hold the cure. It also
fails to say so, as with story 1's coin-toss world.

## General observations, so far (tentative: from six tests, in one body and one simulator)

1. **What counts as evidence comes first.** In the colour tests the useful signal was a poison *while driving*. The bare count of poisons was never as good.
2. **One signal says that something is wrong, its context says what.** The run of goods before the poison told a sequence from a swap, and the time since the last meal told digest.
3. **Detection is cheap, and costs time, not parts.** Detectors were a tally each, and rarely false-alarmed. What they cost is the seconds of a bad score before they fire, and it dominates 100 s lives.
4. **The memory needed is small when its index is right.** Counting good tastes needs no sense of which turn it is. A few bits do what no amount of tally could.
5. **Precision is where parts go.** A bit is free; the balance's 3.7 bits take hundreds of parts, because no signal states it directly.
6. **Reacting has a floor that only prediction can pass**, and prediction has not been found to pay on these swaps.
7. **A brain can't yet tell "I have no cure for this"** from "I haven't found it". Coin-toss tastes and digest both leave it churning. This is the plateau-or-ceiling question, still open.

# Shared-path calibration, run causally (D170, 2026-11-20)

Work order: [WORK_ORDER_2026-11-20_shared_readout.md](../../WORK_ORDER_2026-11-20_shared_readout.md).
Notebook: [discrete/NOTEBOOK.md, D170](../../../discrete/NOTEBOOK.md#d170-shared-readout).
Contract and parameters: [CONTRACT.md](CONTRACT.md), [bounds.json](bounds.json). Sources: [SOURCE_REVIEW.md](SOURCE_REVIEW.md).
Status, commands and checks: [STATUS.md](STATUS.md). **Everything here is an exploratory mathematical reference** on
reused draws: deterministic trajectories with fixed mismatch, no circuit noise in the trajectories, no rail fading, a
hypothetical connection that is not in the catalogue.

## What this changes about local adaptation

The order detector's balance knob can be set **causally, during life, by a local loop**, without the whole-history
sums D168 used, provided one new kind of connection exists: one reading pair whose current is split by the coincidence
voltage between a quiet-tracking node and the knob. The tracker's leak forces it to be fast (76 ms), yet it still
keeps over 90% of each anchor's reading, because the same split that feeds the knob starves the tracker while the
inputs coincide. On the 40 reused draws, every draw that has any passing knob setting ends its life inside that range.
Two separate reading paths, the only form the catalogue can build, lose 6–15 of those draws to their independent
offsets.

The result holds under the engine's idealised gate, which never opens at rest. If the two steering gates carry
offsets like any other connection's (an assumption; the engine draws none), a gate open at rest drives the knob to its
limit on about half the draws, **in both arms**. So before any bench, the gate's resting state needs a decision.

## Answers to the work order's questions

**Does sharing the path still help causally? Yes, in this reference.**

| arm (40 draws, final knob, all 34 old cases) | draws passing | cases passing | readout error vs offline reference, final third: mean / SD / RMS / max | within 10 mV | within 15 mV |
|---|---|---|---|---|---|
| shared reading, P1 (pair's own slope) | **39** | 1354 | −1.6 / 8.1 / 8.2 / 28 mV | 35 | 38 |
| shared reading, P2 (preamplifier, 4× slope) | **39** | 1353 | −2.4 / 7.9 / 8.1 / 28 mV | 34 | 38 |
| separate reading paths, P1 | 25 | 1290 | −4.6 / 39.6 / 39.4 / 85 mV | 4 | 5 |
| separate reading paths, P2 | 34 | 1337 | −4.0 / 30.3 / 30.2 / 59 mV | 3 | 5 |
| fixed knob d = 0 (removal) | 34 | 1340 | −1.5 / 26.9 / 26.6 / 65 mV | 11 | 19 |
| offline whole-history reference, all 1000 s (privileged) | 39 | 1353 | — | — | — |
| offline whole-history reference, final third (privileged) | 38 | 1349 | — | — | — |

- **What the column means.** "Readout error" is the constant readout error that would put D168's ideal offline
  estimator at the causal knob's final value, using the final third of life. Against the full life the shared arm's
  RMS is 7.3 mV (P1) and 6.4 mV (P2).
- **Draw 2215 fails in every arm.** No knob setting passes all its cases, and it stays in every denominator.
- **Against the fixed knob.** The shared loop rescues 5 draws (2204, 2223, 2226, 2236, 2237) and 14 cases, and harms
  none (P1; P2: 5 draws, 13 cases). The draw-count difference is +5, bootstrap 95% [1, 9]. Like every interval here,
  it is exploratory evidence on reused draws.
- **Against separate paths.** Sharing rescues 14 draws at P1 ([8, 20]) and 5 at P2 ([1, 10]), and harms none. Separate
  paths at P1 do worse than leaving the knob alone: they rescue 5 draws and harm 14.
- **Against the offline references.** The shared loop matches the full-life reference draw for draw. It also passes
  2227, which the final-third reference fails: it stops at d = −0.42 (P1), inside 2227's range of −0.453 to 0.116.
  The margin is narrow there (0.032 at P1, 0.12 at P2).
- **The requirement is screened, not proved.** D168's 10 mV figure is a conservative engineering screen. Five draws
  exceed it at P1. Four of them still pass, and the fifth is 2215, which no setting passes: the readout error is not
  the same thing as each draw's own passing range.

**Is useful order signal preserved?** Yes.
- At the final knob, the mean order output for near pairs in the right order is +96 mV, and in the wrong order −96 mV
  (fixed knob: +99 and −98 mV).
- During adaptation, each event's own case was scored in isolation at the knob value in force when it arrived:
  99.4% pass (P1), against 98.6% with the knob fixed. The in-stream response itself cannot be scored by the old
  isolated-case criterion.
- Known ±20 and ±50 mV order inputs keep their sign and 91–97% of an ideally held reading
  ([checks](checks/checks.json)). The fast tracker costs 3–9% of the reading's gain, not its sign or its zero.

**What precision, evidence time and material does it need?**
- **Precision.** The static budget on synthetic anchors (nominal gates, 40 draws' resting levels and frozen errors)
  gives 6.9 mV RMS at P1 and 6.5 mV at P2. Separate paths give 45 mV.
  - The largest term is the mismatch of the two output mirrors after the split (SD 6.7 mV at P1; the analytic figure
    was 5.5 mV).
  - The tracker's leak gives 1–3 mV, the write dead band about 0, and the tanh's curvature 1.3 mV at P1 and 8 mV at P2
    on the synthetic anchor shape.
  - On the real histories, P2's smaller mirror term and larger curvature come out even: 39 draws passing for both.
- **Evidence time.**
  - On the 34 draws where d = 0 already passes, the knob never leaves the passing range.
  - On the 5 that need calibration, it enters the range for good after 12–157 s at P1 (29–313 s at P2).
  - It stays inside for 97% of life on average. The 3% is draw 2215.
  - Each life writes about 1.1 pC in about 1.5 s of writing.
  - Silicon noise is bounded analytically at about 0.1 mV, two orders below the screen
    ([CONTRACT §7](CONTRACT.md)).
  - One explorer, the knob, per credit window. No bit count is given: no prior or likelihood was established.
- **Material and power.**
  - New parts: one tracking node (50 pF), one retained knob memory (14.9 pF), one reading pair with a four-transistor
    steering quad, and two output mirror sets.
  - Transistors: 35–53 at P1 and 42–64 at P2, plus the existing memory block. These are ranges because the topology
    is not fixed.
  - Capacitor area about 13,000 µm².
  - Resting supply power 0.19–1.09 nW at P1 and 0.59–1.36 nW at P2, against about 25 nW for the order circuit.
  - The memory's high-voltage write supply is excluded, as for every memory.

**What remains privileged or unbuilt?**
- **Unbuilt: three operations the catalogue lacks.**
  1. A pair that reads the difference of two node voltages.
  2. One pair's current steered to two destinations with complementary weights (a Gilbert-type steering quad).
  3. A 1 − w gate. Only the separate control uses it, granted so that the comparison isolates the reading path.
- **Privileged, used by the harness only.** Event labels (to build the controls and score cases), the old isolated-case
  scores, each draw's passing range, and D168's offline reference.
- **Not modelled.**
  - The knob's own gating construction, whose errors sit inside its loop.
  - Rail fading, circuit noise in the trajectories, and the memory's write supply.
- **The gate's resting opening (the open question).**
  - With 30 mV steering-gate offsets, assumed by analogy with a connection's offset (not a measured statistic), the
    static budget pins the knob at its limit on 19–25 of 40 draws in both arms.
  - At rest, any gate open by more than about 6 mV writes continuously through the dead band.
  - A closed-at-rest margin of about 90 mV would be a fourth requirement. It was not tested: that would be a third
    variant.

## Why: the diagnosis, competing explanations by name

- **(i) "Sharing removes the leading offset, and an affordable tracker suffices": supported.**
  - The pair's offset cancels exactly in the ideal limit (`checks.json`: knob change 0 for ±30 mV).
  - What remains is the output stage after the split, about 7 mV RMS.
  - P1 is the cheapest feasible point: 50 pA tail current and the slowest leak the chip allows.
- **(ii) "Leak or nonlinearity prevents accurate tracking": rejected at these parameters, with one caveat.**
  - The leak sets a hard bound: the tracker's time constant is at most TAU_MAX divided by its loop gain, so 76 ms at
    G = 50.
  - That costs 1–3 mV, and the tracker's mean quiet-time error is −0.6 mV (P1) and −0.2 mV (P2).
  - Its quiet-time RMS (4.7 mV, 3.4 mV) and its maximum (226 mV) are lags while ordered events pass. The coincidence
    weight shuts the knob out at those moments, so they do not reach it.
  - Curvature is the caveat: the zero becomes the anchor's w-weighted tanh balance rather than its mean. At P2 this
    adds a shape-dependent bias of a few mV.
- **(iii) "Real events contaminate the quiet signal": partly supported, not limiting here.**
  - With no input, the knob is never written (0 C in every arm).
  - With ordered events only and no anchors, it still moves: draw 2227 goes to d = −0.38 (P1) and −0.15 (P2), and
    2200 to −0.03. Near ordered pairs open the coincidence weight a little, the contamination D165–D167 found.
  - With anchors only, it lands close to its full-stream value (2200: 0.112 against 0.093).
  - So causal calibration does learn partly from ordered events. Where that pulls toward a failing setting, the
    w*w selectivity of D167 is the known remedy, and it was not tested.
- **(iv) "The steering stage's own mismatch replaces the cancelled offset": the deciding question for a bench.**
  - With the engine's gate law, it does not arise.
  - Under the gate-offset assumption, it fails statically in both arms at rest. Not replayed, per the decision table.
- **The approximation check.** A moving knob shifts node 7's response from the affine form u + d·der by up to
  10 mV (P1). The replay therefore propagated node 7 causally from the branch currents, and that propagation
  reproduces the unchanged trajectory at a fixed knob to 1e-16 V.

## Predictions against outcomes

The predictions were written before work, in the notebook.

| prediction | confidence | outcome |
|---|---|---|
| Static bounds pass at native slope; mirror term ~5 mV the largest | 65% | held: mirror 6.7 mV, combined 6.9 mV |
| The leak forces a tracker in the tens of ms | — | held: 76 ms |
| That fast tracker loses 20–60% of anchor gain | 60% | wrong: 3–9% lost |
| Shared arm ≥ 34/40 | 50% | held: 39/40 |
| Separate arm 20–30/40 | 60% | P1 held (25); P2 outside (34) |
| Gate mismatch at the 30 mV scale opens a gate at rest and pins the knob in both arms | 70% | held statically: 19–25/40 |
| No drift with no input | 80% | held |

**Why P2's separate arm does better is untested.** A plausible cause is that the 4× slope saturates on the 42 mV
error between paths, so the knob balances anchor time above and below zero rather than their mean.

## The one decision for the reviewer

**Decide how a steering gate's resting opening is to be specified, then whether to authorise one frozen noisy
physical bench of the shared-reading connection.**

The bench would test this exact catalogue change:
- **The connection:** a difference-reading pair whose two branch currents pass through a steering quad driven by the
  coincidence voltage, feeding a retained memory (the knob, share w) and a new dynamic node (the tracker, share 1 − w).
- **Parameters:** P1, with P2 as the sensitivity point.
- **Costs:** as listed above.

The bench should include:
- the steering pairs' offsets;
- substrate noise;
- the shared and separate arms, the fixed knob, and the no-input, ordered-only and simultaneous-only controls;
- all original failures, including 2215.

This document does not authorise that bench or adopt the connection. If the gate's resting opening cannot be
specified without a further operation, the D154 routing limitation becomes the object of diagnosis instead.

## Back to the programme's milestone

This is evidence for a **costed local adjustment that preserves useful signals**, for one knob, in a reference model. In the goal's terms (README), it is one piece of innate structure in a reusable repertoire. Its evidence, settling
time, energy and material are all accounted for. No near-optimality margin is claimed.
- **Its cost:** about 50 transistors, 65 pF and about 1 nW.
- **Its evidence:** one anchor every 85 s, enough to settle within 160 s (P1) to 310 s (P2) where needed.
- **What it does not establish:** the finite repair grammar, two-knob identification, or any robot-learning result.

## Evidence and limits

- **The data.** 40 reused D163 draws, 1000 s each, at 0.5 ms. Refinement at 0.25 and 0.125 ms on 2026112200 and
  2026112227 changes the knob by at most 7.4e-5 and the readout error by at most 0.012 mV, with classes unchanged.
- **Reproduction.** The schedules, and the raw-mode A/B/W against D168, reproduce exactly (error 0).
- **Error draws.** Fixed, from `rng([seed, 170, 1])`, frozen before results. The gate-offset draws were used only in
  the static budget.
- **Selection.** Two parameter points, frozen before the replay. No retuning.
- **The mismatch scales are assumptions.** The 10% output-mirror figure and the 30 mV gate offset are assumed, not
  measured.
- **Margins.** The shared arm's smallest margins to a draw's passing range are 0.032 (2227) and 0.036 (2205) at P1.
- **Records.**
  - Per-draw results: [analysis/per_draw.jsonl](analysis/per_draw.jsonl).
  - Every arm's records: [replay/records.jsonl](replay/records.jsonl).
  - Knob and tracker histories at 1 s: `replay/histories_1s.npz`.
- **Figure** ([analysis/replay_figure.png](analysis/replay_figure.png)):
  - Left: each draw's readout error at the final knob, by arm.
  - Right: the knob over life for the two refinement draws, with each draw's passing range.

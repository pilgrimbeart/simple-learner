# Order-detector calibration: how precise the readout must be, and whether it can reference itself (D168, 2026-11-20)

Work order: [WORK_ORDER_2026-11-20_calibration_precision.md](../../WORK_ORDER_2026-11-20_calibration_precision.md).
Notebook: [discrete/NOTEBOOK.md, D168](../../../discrete/NOTEBOOK.md#d168-calibration-precision).
Status, commands and checks: [STATUS.md](STATUS.md). Every reproduction gate passed; no output is missing.

## What we learned

The order detector has a balance knob, d. It should be set so that inputs arriving together (an "anchor")
give zero order output. D167 showed that a good setting exists and that the coincidence voltage can pick out the
evidence for it. This phase asked whether the circuit could **read** that evidence accurately enough, using only
the parts the catalogue has, with arithmetic and no new circuit.

1. **The readout must be about three times better than one ordinary part.** Suppose the readout has one fixed
   error per life with a given SD. To keep 95% of the histories that work with no error, that SD must be at most
   10 mV on the 80 D165 histories and at most 15 mV on the 40 D163 draws. To keep 90%, it must be at most 15 mV
   and 20 mV respectively. These figures are for the 0.15 s baseline. One connection's offset is 30 mV (the
   catalogue's mismatch scale).
   - The requirement barely depends on the window (all 1000 s or the final third) or on the weight (`w` or `w*w`).
   - Raw output without a baseline needs 7.5–10 mV on the D165 histories' final thirds.
   - Table and figure: [a/summary.json](a/summary.json), [a/precision_curve_mpl.png](a/precision_curve_mpl.png).
   - The figure also shows that for raw output, small errors *add* passes (curves above 100%): some error-free
     raw settings fail narrowly, and an error of either sign can push them back. A plausible cause is the
     uncorrected resting level, which was not tested here.
2. **Any chain the catalogue can build is worse than the 30 mV probe.** The error map ([b/error_map.md](b/error_map.md))
   traces each stage to `units.py` and `mixed_feedback.py`. The calibration settles where the net write into its
   memory crosses zero. So gain errors drop out, errors after the knob are absorbed by the loop, and only additive
   offsets in the measuring path remain.
   - Reading raw output directly has one 30 mV offset. But raw output also carries the circuit's own resting
     level, which is itself an error (−77 to +114 mV over the 40 draws).
   - A baseline built by integral feedback carries two offsets, 42 mV in all.
   - A feed-forward baseline with a difference node carries four, plus a gain-mismatch term: 61 mV in all.
   - Silicon noise is about 0.05 mV per anchor, negligible beside these.
   - Some error scales have no anchor in the model and are stated rather than numbered: the coincidence gate's own
     offset (the engine draws none), the tanh's curvature, and the memory's write dead band (1–3 mV at plausible
     slopes).
3. **Reading the same detector during quiet time works only if one physical reading serves both purposes, and
   the catalogue cannot do that yet.** The candidate: when coincidence is low (weight `q = 1 − w`), the readout sees
   its own error but no order signal, so subtracting a quiet-time estimate removes the error.
   - **With a shared path,** the error cancels exactly and what remains is the quiet-time residual.
     - In these trajectories the remainder is tiny for the baselines: median 0.01 mV per unit weight, at most
       0.6 mV in the slowest. So the settings are the error-free ones: 38/40 and 39/40 as in D167, no draw rescued
       or harmed.
     - For raw output, the self-reference removes the resting level, which lifts it from 28/40 to 38/40 (final
       third) and from 29/40 to 39/40 (all 1000 s). Ten draws are rescued, none is harmed, and one case is harmed.
       Raw output with a quiet self-reference would need **no baseline node at all**.
   - **With the catalogue's parts,** the quiet and coincident readings must come from two separately gated
     connections. Their independent offsets replace the error rather than removing it. At 42 mV, the expected
     adequate draws are 23–26 of 40, worse than D167's 29–32 with a single 30 mV error. This is D149's pattern
     again, as the work order predicted.
   - So the candidate is **blocked, with requirements** (below).
   - The quiet estimate's weighting `W/Q` is not a tuned constant. It is what a node tracking the quiet-time mean
     produces by itself, so no event rate is built in.
4. **Noise is not the wall; anchors and the fixed offset are.**
   - Anchors arrive about once every 85 s (12 per 1000 s on average, 5–18 in the 40 schedules). A 95% chance of
     at least one takes 240 s; of at least four, 640 s.
   - In silicon, one anchor gives an observation whose noise is about 200–300 times below the requirement.
   - At zero offset, every single anchor alone gives a setting inside its draw's allowed range in the baseline
     modes (165/165); in raw mode, 132/165.
   - More anchors cannot average away a fixed offset. A noisy pilot's results will be set by the offset, not by
     noise.
   - Biology's noise, shown only as a reference, would need about 27–60 anchors per setting.

## What precision the calibration needs

| set | weight | window | baseline | error-free | expected at 30 mV | SD for 90% (grid) | SD for 95% (grid) |
|---|---|---|---|---|---|---|---|
| 40 D163 draws | `w` | all 1000 s | 0.15 s | 39 | 29.7 | 20 mV | 15 mV |
| 40 D163 draws | `w` | final third | 0.15 s | 38 | 29.3 | 20 mV | 15 mV |
| 40 D163 draws | `w*w` | all 1000 s | 0.15 s | 39 | 30.8 | 20 mV | 15 mV |
| 80 D165 histories | `w` | all 1000 s | 0.15 s | 71 | 53.5 | 15 mV | 10 mV |
| 80 D165 histories | `w` | final third | 0.15 s | 70 | 52.7 | 15 mV | 10 mV |
| 80 D165 histories | `w` | final third | raw | 56 | 43.2 | 10 mV | 7.5 mV |

- A finer scan (0.05 mV steps, supplementary) puts the 95% points at 14.0 mV (D165, all 1000 s) and 16.0 mV
  (D163, all 1000 s).
- For the D165 first-100 s window, a 30 mV error is expected to *add* passes, because the error-free setting
  mostly fails there. Its "requirement" is therefore not meaningful and is reported only for completeness.
- The other modes and windows are in [a/summary.json](a/summary.json).
- Draw 2215 has probability 0 throughout.

## Where the error lives, and whether a specified local operation removes it without new switching

- **Where it lives:** in the additive offsets of the connections that read the order signal and its baseline,
  and in the product connection. It is 30 mV at best and 42–61 mV for baseline chains (table in
  [b/error_map.md](b/error_map.md)).
- **What the literature says** ([MIXED_FEEDBACK.md](../../../MIXED_FEEDBACK.md#offset-rejection-review-2026-11-20)):
  Enz & Temes (1996) was read in the source, pp. 1584–1602 (sections I–IV complete); Shieh, Patil & Sheu (1987)
  was read in full, pp. 277–281.
  - Autozero, correlated double sampling and chopping all cancel an offset by reading **the same path** in two
    conditions.
  - All three create the second condition **with switches or a clock**. Their residual errors are the switches'
    own: charge injection, clock feedthrough, kT/C sampling noise with aliasing, droop.
  - Charge injection is in the millivolt range and depends on the signal level.
  - The closest continuous-time form (section IV F) keeps the main amplifier in the signal path. A second
    amplifier drives a nulling input from a slowly filtered estimate of the offset. That corrector's own offset
    still enters, divided only by its gain, unless it is autozeroed in turn, which needs switches again.
- **The quiet self-reference keeps the "same path" idea without a switch:** the circuit's own quiet time plays the
  role of the sampling phase.
- **What it needs that the catalogue lacks** (blocked, with requirements):
  1. **A connection that reads the difference of two node voltages** (`r` against a quiet-tracking node `m`). Today
     a connection reads one node against its own fixed offset (D154).
  2. **One reading pair whose output current is steered to two destinations in proportions `w` and `1 − w`.** The
     knob takes the `w` share and `m` the `1 − w` share. Today a connection has one destination.
  3. **A quiet-tracking node `m` with enough loop gain.** A SONOS memory's write dead band would stop it tracking
     within about 1–3 mV, so `m` is probably a dynamic node. Its leak then limits the loop gain.
- **Removal without new switching: not with existing parts.** With these three requirements met, the error cancels
  in the linear analysis, and mirror gains drop out at the two equilibria. Curvature, the gate pair's offset and
  finite loop gain remain unanchored. In the stationary arithmetic with an explicit ratio, mirror mismatch leaves
  4–9 mV, which gives 37.5–39 of 40 expected. That meets the requirement.

## What the noise wall implies for a later pilot

- **Evidence rate:** one anchor per 85 s at 10 s mean spacing. Each anchor carries W ≈ 0.051 s of weight and
  B ≈ 0.0069 V·s of the knob's effect (medians over draws, `w`, 0.15 s).
- **Signal to noise:** about 200–300 per anchor in silicon, against the requirement. Equivalently, the
  squared-SNR evidence rate is about 460–1030 per second of life.
- **Settling:** one anchor suffices for noise. The time is set by waiting for anchors: 240 s for 95% of at least
  one. Fixed offsets are the wall.
- **Explorers per credit window:** one for the one-knob design. The two-gain repair has two explorers on one
  scalar observation per anchor, so it needs anchors whose positive and negative branch responses differ in ratio
  to separate them. That means more anchors and more time.
- **Observability of B** (analysis only):
  - B is the knob's own effect on the output. The online loop needs only its **sign**, since the equilibrium is a
    zero crossing. The sign is fixed by construction: B was positive in every D163 record and negative only in
    three raw-output first-100 s D165 rows.
  - Where the sign or size of B must be learned, the standard precedent is perturbation, also called dither: jiggle
    the knob slightly and correlate the output's change with the jiggle. Cauwenberghs (1992/93), read pp. 244–248:
    - All parameters are perturbed at once by ±σ for an epoch, and the error's change is measured against the
      unperturbed error.
    - On average this follows the gradient, with each step a descent, at √P the cost of true gradient descent for
      P parameters. That is √2 for the two-gain repair.
    - Here the "epoch" would be an anchor, and the method needs the same quantity evaluated with and without the
      jiggle. Successive anchors are different cases, so the comparison would carry anchor-to-anchor variance on
      top of circuit noise. Its evidence time therefore grows with (spread of per-anchor response / dither
      effect)², not only with noise.
  - Extremum-seeking control is the continuous-time counterpart. It was named, not read: no open copy was found.
  - Nothing was computed or built.

## The single comparison to make next

**Decide, in review, whether to specify the shared-reading part:** a connection that reads a difference of two
node voltages and steers its current to two complementary-gated destinations. This would be a catalogue
extension, so it needs the user's decision, not a worker's.

If it is approved, the next comparison is one bench of that part on the existing order circuit's raw output.
- **Arms:** the quiet self-reference against the two-separate-readings form.
- **Conditions:** the same 40 draws, silicon noise and mismatch, with the part's own offsets, curvature and loop
  gain counted.
- **Pass:** the achieved residual SD is at or below 10–15 mV.

If it is not approved, the work order's rule applies: the parked routing limitation (D154) becomes the object of
diagnosis. Alternatively, the programme weighs this capability against others the robot needs.

## Evidence and limits

- Everything is observer arithmetic on the analytic feed-forward trajectories: no circuit noise in the
  trajectories, no rail fading, selected and reused draws, and isolated old-case scoring.
- The 10 D165 components were chosen deliberately, so they do not estimate yield.
- **Privileged references:** B (the knob's own effect) and the ideal baselines. The quiet weight is read only
  from the coincidence voltage.
- **Gaussian error assumptions:** one fixed draw per detector, independent of the circuit's existing offsets
  (as in D164).
- **Unquantified errors:** the gate offset, tanh curvature, dead-band bias and finite loop gain (listed in the
  error map).
- **Ranges, not bits:** no learner prior or likelihood is specified, so no bit counts are given.
- **Task D at zero shared error:** this is an informed reference for what an exactly shared path would give. No
  such path exists.

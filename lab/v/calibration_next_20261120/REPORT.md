# Order-detector calibration: selectivity, readout precision and two-gain capacity (D167, 2026-11-20)

The assignment is [PROGRAMME.md, "Next diagnostic assignment — 2026-11-20"](../../../PROGRAMME.md#next-diagnostic-assignment-2026-11-20).
The notebook record is [discrete/NOTEBOOK.md D167](../../../discrete/NOTEBOOK.md#d167-calibration-next).
All three diagnostics were completed within their budgets, and every reproduction check passed.

## What we learned

The order detector has a balance knob (d). It should be set so that simultaneous A/B inputs give zero order output.
The question was whether the circuit can set that knob from what it can see locally, without mistaking real event
order for its own manufacturing error.

1. **The coincidence voltage alone can separate useful evidence from real order, in this approximation.**
   Two inputs arriving together drive the coincidence node much harder than inputs 60 ms apart. Weighting the
   observation by the coincidence level squared exploits this. That weight is a reference, not a chosen mechanism.
   - Per event, the ratio of simultaneous weight to positive-near weight rises from about 13:1 to about 145:1.
   - The positive-near share of the integrated weight falls from 1.1% to 0.004% (median over draws).
   - About 18% of total evidence is given up: weight retained 82%, branch-sensitivity retained 82–84%.
   - With this weight, draw 2026112227 passes in the final-third window under every observation mode. No draw is
     harmed, and the infeasible 2215 is still counted in the denominator.
   - Results go from 38/40 to 39/40 draws, and from 1349 to 1353 of 1360 old cases, in each of the three
     baseline modes.
   - The raw-output mode rescues 2227 too, but loses 6 individual cases on other draws.
2. **Contamination is a fixed-trace effect, not carried state.** I re-ran 2227 with all 88 of its non-simultaneous
   input pulses removed, keeping the same starting state and the same 12 simultaneous pulses. Every simultaneous
   interval's contribution was then compared with the original:
   - raw and 0.15 s baseline modes: identical to within 1e-13 V s;
   - 1.0 s baseline: within 0.006%;
   - slowest baseline (3.86 s): within 0.9% (knob change 0.0016).

   So D165's interval accounting was effectively causal. The bias comes from the ordered events' own correct
   responses, not from those events disturbing later anchors.
3. **Precision is a separate, blocking requirement, and a longer history does not relieve it.** Assume one fixed
   detector error per life with a typical spread of 30 mV (the existing mismatch scale). Expected adequate histories
   (0.15 s baseline mode):

   | window | adequate with no error | expected adequate with one fixed 30 mV error |
   |---|---|---|
   | full 1000 s | 71/80 | 53.5/80 |
   | final third of 1000 s | 70/80 | 52.7/80 |

   - The paired gain from keeping all of the history is +0.010 per history. Its 95% interval, clustered over the
     ten components, is [−0.002, +0.027]: inconclusive, and small beside the roughly 17-history loss to the error.
   - The median tolerable error is about 30 mV, equal to the assumed spread, and the narrowest is 2.2 mV.
   - The tolerance barely changes with window length, because the error's effect (e·W) and the evidence (A, B)
     grow together.
   - The other two baseline modes behave the same way (56.2 vs 55.3; 56.5 vs 55.6); raw output is 44.0 vs 43.2.
4. **The incompatible draw 2215 is beyond one knob but within two existing gains**, in the analytic approximation.
   Here the positive and negative readout gains (a, b) are set independently in [0, 2], rather than tied as
   a = 1+d, b = 1−d.
   - All 40 draws have a feasible region with a proven positive voltage margin of 12.8–27.1 mV. None is empty or
     touches a boundary only.
   - 2215's region, with 12.8 mV margin, lies entirely off the original line (a + b < 2). Both gains must fall
     (a 0.32–0.80, b 0.30–1.14), so 2215 needs a lower common gain, not a different balance.
   - For every draw, the point of largest margin is off the original line.
   - These gains are designer-set references, not learned memories. Nothing says how the circuit would find them.

## What remains supplied by an analyst

- **Event labels.** "Simultaneous", "near" and so on were used only to account for the results; no rule read them.
- **Squaring the weight.** This is a hand-chosen exploratory reference. It is not tuned and not a selected
  mechanism.
- **Privileged reference operations.** The branch derivative B (from the positive-path decomposition) and the
  ideal baselines.
- **The isolated old-case scoring and the feasible intervals.**
- **The two-gain settings.**

## What blocks an autonomous circuit

- **Observation.** No local quantity yet supplies B, the knob's own effect on the output. That remains a privileged
  operation.
- **Selectivity.** It now looks available from the coincidence level itself. The required contrast depends on how
  often ordered events occur relative to anchors (13:1 per event was not enough under the 80% skew).
- **Precision.** One fixed readout error at the existing mismatch scale loses about a quarter of the feasible
  histories. Time cannot average it away. An error-rejection operation whose information path sees the offset but
  not the order is needed. Its catalogue parts and switching (the D154 routing limit) are unspecified.
- **Material and capacity.**
  - 2215 needs a second gain degree of freedom, which means a second stored knob and evidence for it.
  - Crude static figures for the polygon vertices: scaled readout currents stay ≥1.2e-10 A (all above the 1 pA
    floor), and slew stays ≤31 V/s (limit 1200 V/s).
  - The current-over-leak offset reaches up to 0.85 V against a 0.9 V rail at a = 2. Rail fading is omitted from
    these trajectories, so high gains are not cleared.

## The single comparison to make next

On the same 1920 saved settings, compute the residual error tolerance of an **offset-rejecting readout**. First
specify its information path in local terms: what it observes that contains the detector error but not the order
signal. Then compare that tolerance with the 30 mV result above, before any circuit is drawn.

Precision gates both remaining routes, the one-knob calibration and the two-gain repair. A later noisy pilot must
also first estimate:

- the evidence rate (one simultaneous anchor about every 85 s at 10 s spacing, 4/34 of events);
- signal-to-noise per second;
- the number of simultaneous explorers per credit window.

## Evidence and limits

- **Model.** Everything here is observer arithmetic on the analytic feedforward trajectories: no circuit noise, no
  rail fading, ideal readout apart from the stated error, and isolated old-case scoring.
- **Selected draws.** These are not fresh draws or new problem families. In task 2, ten deliberately selected
  components cannot estimate yield.
- **No bit counts.** No learner prior or likelihood has been specified, so none are given.
- **Task 3's margin bracket.** The "margin_active" field is empty because the bracketing point's polygon degenerates.
  The closure's active constraints (`active`) are the meaningful list.

### Outputs

| task | script | outputs |
|---|---|---|
| 1 | `lab/calibration_next_20261120/t1a_reproduce_contamination.py`, `t1b_weights.py`, `t1c_analyse.py` | `t1a/`, `t1b/records.jsonl` (640 rows), `t1b/intervention.json`, `t1b/refinement.json`, `t1b/analysis.json` |
| 2 | `t2_readout_error.py` | `t2/rows.jsonl` (1920), `t2/summary.json` |
| 3 | `t3_two_gain.py` | `t3/polygons.json` (40), `t3/summary.json` |

Commands, timings and checks are in [STATUS.md](STATUS.md). The frozen inputs are in
[manifest.json](manifest.json) (revision 5700eaa, with uncommitted inputs hashed).

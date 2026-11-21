# Overnight measurement — morning report (2026-11-19)

Executed from the frozen [work order](../../OVERNIGHT_WORK_ORDER_2026-11-19.md) and
[matrix](../../overnight_20261119/matrix.json). All tasks A–G complete; nothing blocked; no retries were needed.
Everything below is **provisional until reviewed**. No circuit, simulator, metric, threshold or old result was changed;
nothing was committed or pushed.

The order results are **observer arithmetic on analytic feedforward trajectories**: no circuit noise, no rail fading,
no implemented calibration state or update rule, no closed-loop lives. They answer (a) whether a useful setting
exists and (b) whether the observations identify it. They do not show (c) that a circuit can implement it, or
(d) that the robot's reward improves.

## 1. What we learned

1. **The two remaining order failures are different kinds.** 2026112215 has *no* constant balance setting that meets
   all its conditions: its simultaneous (.5, .35) V case needs d > −0.16219 and its long-gap (.5, .5) V case needs
   d < −0.19449. More evidence cannot fix that. 2026112227 *has* an allowed range, (−0.4525, +0.1160), but the
   observer chose d ≈ −0.57, about 0.115 below it. ([failure_report.md](failures_results/failure_report.md))
2. **2227 fails because other events pollute the calibration, not because its one anchor was unrepresentative.**
   An "anchor" here is a simultaneous A+B event, the only kind whose correct order output is zero. Using only the time
   after 2227's single anchor gives d = −0.241, which passes all 34 old cases. The same amplitude case measured in
   isolation gives −0.245, so neither the anchor's amplitude nor the state before it explains the failure. What
   pulls d to −0.567 is the other 32 intervals, chiefly frequent A-before-B near pairs. Their order output is
   *correctly* positive, but the observer reads it as imbalance (each adds A ≈ B, a vote for d ≈ −1). Across the 40
   histories, anchors alone pass 39/40 and the other intervals alone only 10–12/40.
   ([attribution_report.md](attribution_results/attribution_report.md))
3. **Several anchors dilute that pollution; throwing away earlier evidence is costly at short lives and slightly
   costly at long ones.** On 80 new schedules (10 reused, selected components; tau 0.15 s), the old 100 s convention
   (judge from the final third) gives 19/80. Using all of the first 100 s gives 51/80 (32 rescued, 0 harmed). The old
   1000 s convention gives 70/80; all 1000 s gives 71/80; prefixes to 666.7 s or 833.3 s give 72/80. 72/80 is every
   history except 2215's eight. For the ideal-baseline observers, keeping earlier evidence harmed no history. For raw
   output (no baseline), it rescued 1–5 and harmed 2–4.
   ([history_report.md](histories_results/history_report.md), [information_report.md](information_results/information_report.md))
4. **Anchor scarcity follows the event generator.** No-anchor counts match (1 − 4/34)^N: in the first 100 s's final
   third, 58/80 observed against 52.7 expected; in the 1000 s final third, 2/80 against 1.24. With no anchor, nothing
   passed except one full-100 s history. Longer time cannot remove a single detector's fixed manufacturing offset
   (D164, reproduced exactly).
5. **The oscillator repair (D162) audits clean, with its limits intact.** Adaptive 40/40 (Wilson95 [0.912, 1]),
   original and writer-removed 38/40 each. Paired difference +0.05 [0, +0.125]: it includes zero, so this is **not**
   a demonstrated population improvement. Cost is 95 → 196 parts and +6.32 nW [6.18, 6.46]. One nuance: freezing the
   memory at its random start repairs both of the original's fresh failures but breaks two others.
   ([audit.md](audit_results/audit.md), [oscillator_review.md](oscillator_review_results/oscillator_review.md))

## 2. What ran

| task | status | denominators | job elapsed |
|---|---|---|---|
| A audit | complete | 115 manifest files; 8 provenance sets; 360/360 oscillator keys; 160/160 settings; 240/240 D164 rows | 0.5 s |
| B failures | complete | 40/40 draws × 34 conditions; 160/160 settings | 0.1 s |
| C attribution | complete, validated | 40/40 histories; 1984 aggregate settings | 437 s (limit 900) |
| D histories | complete, refinement passed | 80/80 histories; 1920/1920 settings; 2 refinement histories | 1020 s (limit 2400) |
| E information | complete | — | 0.2 s |
| F oscillator review | complete | 300 build comparisons; 11/15 requested traces available | 0.8 s |
| G package | complete | see `result_index.json` | — |

The system clock read 23:05 UTC at the start and 23:37 at the end, well inside the six-hour ceiling. Each run
directory (`audit/`, `failures/`, …) holds the launcher's `start.json`, `finish.json` and `stdout.log`. Status table:
[STATUS.md](STATUS.md).

## 3. Audit

- **Zero discrepancies** ([discrepancies.json](audit_results/discrepancies.json)). All 115 frozen-manifest hashes match,
  at the start ([preflight.json](preflight.json)) and at the end ([preflight_final.json](preflight_final.json)). Every
  `files`/`protocol_sha256` entry of the D155–D164 and D162 provenance records matches current content.
- Oscillator: Wilson intervals, the seed-bootstrap paired differences (4000 resamples, RNG 126, seeds kept whole)
  and all 36 step-halving intervals reproduce to ≤1e-12, all inside ±0.05. Only **7 of 120** finest-step
  confirmation traces were ever saved; all 7 remeasure exactly.
- Power and parts: means and added power reproduce; core totals 95/196/147 from the component counts. The memory
  pump's implementation and energy stay excluded, as before.
- D163: 40 histories, 160 settings, 100 s prefixes identical, independent rescoring exact. D164: 240 Gaussian rows
  reproduce exactly, with 2215 at probability 0. Independence of a new detector's error is an assumption.

## 4. The remaining order failure

- **Capacity vs observation.** 2215 is a capacity failure (empty interval; [Task B](failures_results/failure_report.md)).
  2227 is an observation failure: a setting exists, and the anchor-only evidence finds it.
- **Anchor amplitude.** It does not explain 2227. The in-history anchor gives −0.241, the isolated D156 observation of
  the same (.35, .5) case −0.245, its zero-output branch setting −0.195, and D155's four-case reference −0.165. All
  pass.
- **Contamination.** Non-anchor intervals, dominated by A-before-B near pairs under the 80% skew, move the setting out
  of range. 2226 shows the same pull without failing (−0.146 → −0.334, bound −0.355). In the new schedules, 2227
  rep 6 fails the same way with a single (.35, .35) anchor (d −0.523), and is rescued when earlier evidence is kept.
- **Causal vs arithmetic.** All of this is temporal accounting on fixed trajectories. "Anchor-only" and
  "leave-one-out" are sums of fixed interval contributions, not re-simulations without the events. Each anchor
  interval also contains ~10 s of quiet and any carried-over tails. What remains confounded is whether removing the
  near-pair events would change the trajectory within the anchor interval itself (expected small: in-history and
  isolated anchors agree to 0.004).
- **Available history.** Keeping earlier evidence gives more anchors (≥2 distinct amplitude cases in 78–79/80 long
  windows), and with several anchors the pollution is diluted. Plot:
  [cumulative_d_2227.svg](attribution_results/cumulative_d_2227.svg).

## 5. Fixed new histories (all modes and windows; no selected row)

All-pass counts of 80 (10 reused, selected components × 8 new schedules; no unidentifiable settings; all
denominators positive):

| window | raw | tau 0.15 s | tau 1 s | tau 3.86 s |
|---|---|---|---|---|
| final third of first 100 s | 23 | 19 | 19 | 19 |
| all of first 100 s | 38 | 51 | 51 | 51 |
| final third of 1000 s (old convention) | 56 | 70 | 70 | 70 |
| all 1000 s | 55 | 71 | 72 | 72 |
| 0 – 666.7 s | 57 | 72 | 72 | 72 |
| 0 – 833.3 s | 54 | 72 | 72 | 72 |

Every failure with the baseline references in the 1000 s windows:

- 2215: all 8 schedules, in every window and mode (no setting exists).
- 2227 rep 6: old convention only (single-anchor contamination).
- 2204 rep 4: old convention (no anchor; d +0.847) and all-1000 s at tau 0.15 s (one anchor in the whole life; fails
  one case narrowly).

Per-seed, per-evidence and per-distinct-case tables are in [history_summary.json](histories_results/history_summary.json).
Every setting and case result is in `settings.jsonl` and `case_scores.jsonl`. Paired rescued/harmed counts with
descriptive cluster-bootstrap intervals (resampling the 10 components) are in
[information_report.md](information_results/information_report.md). Those intervals are not confirmation, and one
containing zero is not equivalence.

## 6. Oscillator

Verified scope: a bounded, local operating-point repair. One added memory reads into the fast node and is written
from it, with no outside assignment after birth. Reliability meets its frozen requirement on fresh component draws of
the same bench family. Superiority over the comparators is not established. Memory moves by up to ~0.24 V in a life
and still drifts slightly in the final third, so it is not a settled knob. Not claimed: new problem families, robot
reward, a universal cycle theorem, exact physical retention, or the uncounted memory-pump energy. No new mechanism
claim.

## 7. What the supervisor must decide (ranked; questions, not designs)

1. **Should the order calibration count only "pure" anchors, or is the 80% A-before-B skew a world property the
   observer must be robust to?** The discriminating question: does an observer that down-weights intervals where the
   order output is expected to be non-zero (near pairs) keep 2227-like draws in range without supplied labels?
   Equivalently: is there a *local* signal separating simultaneous from near events (the coincidence node already
   responds to both)? This decides whether the next obstacle is selectivity of the coincidence weight, not anchor
   scarcity.
2. **What should 2215 count as?** Its failure is structural: no constant balance works. A second knob, or accepting
   it as the design's yield loss, is a design decision; no evidence tonight chooses between them.
3. **Is "keep all evidence from birth" the right reference for an in-life learner?** At the baseline references it
   never harmed, but raw output was harmed. A physical integrator would also carry its own offset (D164), which no
   window removes.
4. **Oscillator:** whether the frozen-bias arm's rescues of the original's failures change how the writer's
   contribution should be described.

## 8. Limitations and failures

- Analytic feedforward quadrature at 0.5 ms (refinement to 0.25 ms on two histories: knob change ≤ 7.8e-6,
  classifications identical). No circuit noise, no rail fading (max analytic state 0.69 V in the new histories), fixed trajectories.
- Settings are scored on isolated old cases (D155 branch responses), not in closed-loop lives. The detector offset
  (D164) is absent from all order references.
- Ten components were selected (two known failures, lowest eight labels). Schedules are new; event families and
  components are reused. Counts are descriptive.
- No failed runs, no retries. One paragraph of the generated `oscillator_review.md` was corrected by hand after the
  run (marked in the file). Tasks C/D wrote reusable checkpoints (`attribution_checkpoints/`, `histories_checkpoints/`).
- Importing old guarded modules created `lab/__pycache__/order_long_calibration.cpython-312.pyc`. That is the only
  file outside the two work directories created besides the intended `discrete/NOTEBOOK.md` append (D165 and a
  current-state line). PROGRAMME.md's diff-stat line differs only in bar rendering (same 467 lines).

## 9. Reproduction

```bash
cd /home/pilgrim/git/simple-learner
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
.venv/bin/python lab/overnight_20261119_preflight.py --output <new path>
.venv/bin/python lab/overnight_20261119_run.py <new task name> <limit> lab/overnight_20261119/0N_*.py   # 01..07 in order
```

The scripts refuse to overwrite: each result directory falls back to `_retry1`/`_retry2`. Delete or rename
checkpoints to force recomputation (they are keyed by a compute version).

- Python 3.12.3, numpy 2.5.4, numba 0.68.1 (see `result_index.json`). Revision
  5700eaa0d397e1a7dc055ce69ce9ec7e1d32cc7f, dirty tree.
- Snapshots: [initial_status.txt](initial_status.txt), [initial_diff_stat.txt](initial_diff_stat.txt),
  [final_status.txt](final_status.txt), [final_diff_stat.txt](final_diff_stat.txt).
- Source and input hashes: `audit_results/input_hashes.json`, `failures_results/input_hashes.json`, `input_sha256` in
  `attribution_results/attribution_summary.json`, `histories_results/history_summary.json` and
  `information_results/information_summary.json`. Every script, the matrix, work order and helper hashes are in
  `result_index.json`.
- Schedule seeds: `numpy.random.default_rng([component_seed, 165, 1, replicate])`, replicates 0–7. Each schedule
  and its SHA-256 are in `histories_results/schedules.json`. Component seeds 2026112200–07, 2026112215, 2026112227
  (rows of `lab/v/motifs/order_v2/confirm.jsonl` at its finest step).
- Files over 1 MiB: [large_artifacts.json](large_artifacts.json) (not added to git; `.gitignore` untouched).

# PROTOCOL — D180 catalogue-native brain execution (frozen before stage data)

Frozen 2026-11-20 by the executor, before `run.py check`. The work order
([WORK_ORDER_2026-11-20_catalogue_brain.md](../WORK_ORDER_2026-11-20_catalogue_brain.md)) owns arms, gates,
margins, seeds, durations and analysis; this file records only the executor's routine interpretations, which
are fixed now and not changed after data. Any later change is appended under "Deviations" with its reason,
never silently. Substantive changes go to AMENDMENT_PROPOSED.md and are not executed.

## Fixed routine interpretations

1. **Engine adapter** (`brain.py`): arrays and noise streams from `mixed_feedback.Circuit` (seed world+1000003,
   `streams=True`, silicon, V_TYP, on_chip); integration by the unchanged `_step`, called from a numba loop that
   only adds observation (pre-clip value recomputed from `_step`'s own scratch `dV`/`gross`, extrema, motor event
   and re-arm steps). All 15 node starts explicit, so `_ready`'s settling holds every node at its start.
2. **Initial states**: `default_rng([seed,180,1])`, one `uniform(-V_TYP/4, V_TYP/4)` per `initial='random'` node in
   design node order (S0,S1,T,E0,E1,X0,Y0,B0,X1,Y1,B1); P = V_TYP/2; M = -1.5 V_TYP. Wiring: `default_rng([seed,180,2])
   .integers(0,2,2)` = (side of S0, side of S1).
3. **Noise**: development and bench stages use "native" noise (bit-identical to `Circuit.pulse/run`; checked).
   Confirmation and refinement (R7/R8) use "coupled" noise at all three steps: per node, 4 independent fine
   normals per DT step from the node's own stream; DT/4 uses them directly, DT/2 sums pairs / sqrt 2, DT sums all
   four / 2. Same law as native; the DT confirmation run therefore uses different (equally distributed) noise from
   development lives. The body tick and Life are unchanged; this is circuit-integration refinement only.
4. **Removal controls**: full graph built and drawn; removed edges' columns dropped afterwards; static power by
   `chip.still` on the survivors; noise streams per node unchanged (no node is removed).
5. **Informed/neutral/reversed P**: written by the harness (`lives.birth_P`) after `Life` draws its wiring, before
   the first step. All-food "informed" = both P = V_TYP; neutral = both V_TYP/2.
6. **Bench A**: P drift = max |P_end − P_start| over both P; frequency = engine-counted X events (rising through 0,
   re-armed below −V_TYP) in [10,100) s / 90 s; duty = fraction of ticks with X > V_TYP/2 (readout threshold) and
   with M > 0; startup = first tick with X rising through 0; amplitude = X max − min in [10,100) s.
   Motor gate counts engine events per motor in [10,100) s, every seed and every P level.
7. **Bench B**: change measured from the end of the tick before the first input to 1 s after the taste pulse
   onset. Common start 1 s + U[0, 0.009] s from `default_rng([seed,180,3,crc32(case)])`. "Corresponding P" is P_k
   for sensor S_k; correct direction = sign of T. Gate set = single-S, 0.005 s, both channels, both signs, 8 seeds
   (32 cases). Controls gated at ≤0.01 V: no-S (both signs) and no-T (both channels), max |ΔP| over both P.
   Unexposed = the other channel's P in the 32 gate cases. Rail excursion = any pre-clip value beyond ±RAIL in
   any B run.
8. **Bench C**: 16 trial times per seed/channel from `default_rng([seed,180,4,channel]).uniform(10,20,16)`, shared
   by all P levels and by the exploration-removed repeat. Each trial forks present/omitted from the snapshot at the
   start of its tick (identical prefix, same future noise). Excess = present − omitted motor events in
   [t, t+0.05) s; next window [t+0.05, t+0.25). Side motor = M[side of the channel]; plastic motor = the other.
   Second pulse: from the common first-pulse history, second present/omitted at t+Δ. Phase bins (analyst only):
   the side motor's oscillator readout on (X > V_TYP/2) and the side motor armed, at the snapshot before onset.
   **Gate**: side-motor excess pooled over all three P levels, seeds and channels (seed means, then mean) > 0.25;
   plastic: per trial excess(P=V_TYP) − excess(P=0), seed means, mean > 0.25; any clip in the full-graph C forks
   fails "no rail violations". 95% seed-bootstrap intervals reported, not gated.
9. **R6 stranding contrast**: seed-paired bootstrap of the seed mean of the life-stranded indicator.
   Evidence eligibility: a writer counts as eligible when its gate E/V_TYP > 0.01 (the memory driver's 1% deadband).
10. **Absolute job "food positive"**: pooled final-third food count > 0.
11. **Bootstrap**: `default_rng(180)` freshly for every interval, 10,000 resamples, percentile 95%.
12. **Ledger**: one compact row per (stage, version, arm, seed, poison, ratio) in `<stage>_ledger.jsonl.gz`;
    traces (E0,E1,P0,P1,B0,B1,X0,X1,M0,M1 per tick, float32) in `lab/v/catalogue_brain_20261120_<stage>.pkl`.

## Deviations (appended, dated)

- 2026-11-20, before this freeze, while writing and debugging the code: two 10 s closed-loop lives (development
  seeds 8, 9) and one run of benches A/B/C on component seed 0 were executed as code tests (scripts kept in `pre_freeze_code_tests.py`). Their outputs were
  seen (seed 0: oscillators ~3.5 Hz; single-S 5 ms writes ~0.04–0.06 V; 10-pulse train writes ~0.34–0.47 V;
  C side and plastic excess ~0.375 at P=V_TYP; seed 8: one poison taste in a natural sensory burst drove a P from
  0.15 V to −0.47 V). The work order fixes design, gates and margins; nothing was tuned or selected from these
  runs. They are not part of any result. Predictions below were written after seeing them and say so.
- 2026-11-20 16:08Z, routine bug fix: `bench.py` wrote its own `gate_bench.json`, so `run.py bench`'s `save_gate`
  refused to overwrite it after all benches had completed. The bench's file was renamed `bench_progression.json`
  (content unchanged), `bench.py` now writes that name, and `gate_bench.json` was written by `run.save_gate` from
  it (adding code hashes). No bench was rerun; bench_A/B/C.json are the single original outputs (bench.log).
- 2026-11-20 ~16:20Z, **user decision**: run R5 (informed action) on v1 although the R3/R4 gate failed (R5 withholds
  taste, so the failed writers never act). Run as `run.py action --authorised`; outputs named `action_auth_*` /
  `gate_action_auth.json`; bench A and C gates still required; the earlier `gate_action.json` (not triggered) is kept.
  Arms, seeds, metrics and the R5 gate are unchanged. Learning (R6+) remains not triggered: not authorised.
  The user asked not to pursue the write-size question yet.

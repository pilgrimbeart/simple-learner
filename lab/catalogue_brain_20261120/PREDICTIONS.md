# PREDICTIONS — D180 execution (written before stage data; never edited afterwards)

Written 2026-11-20 before `run.py check`. Caveat: seed-0 bench code tests and two 10 s development lives were
seen first (PROTOCOL, Deviations), so the R3/R4 predictions are informed by one seed. Probabilities are the
executor's subjective chances.

| Stage | Prediction | P |
|---|---|---|
| R1 | All identity checks pass (adapter = Circuit.run, clones, chunks, wiring) | 0.95 |
| R2 | All realised C/R/current/slew limits pass; sensory inputs clip at the rail in natural Poisson bursts in some lives | 0.7 |
| R3 A | Oscillators start in all 8 seeds; ≥10 events per motor per seed; P drift ≤ 0.01 V; no clipping without inputs | 0.75 |
| R3 B | Single-S/0.005 s writes inside [0.001, 0.15] V, correct direction, all 32 cases; controls ≤ 0.01 V | 0.65 |
| R3 B diag | The 10-pulse train overshoots 0.15 V (writes scale with E, which bursts open fully) | 0.85 |
| R4 C | Side excess > 0.25 | 0.55 |
| R4 C | Plastic excess(P=V_TYP) − excess(P=0) > 0.25 | 0.45 |
| R4 C | Excess depends strongly on the explorer's phase: near zero while the side motor is unarmed (readout on) | 0.8 |
| R3/R4 | Whole progression gate passes for v1 | 0.35 |
| R5 (if run) | Informed beats neutral and reversed by > 0.10 net food/10 s (lower bound) | 0.35 |
| R5 (if run) | Informed food rate lower bound ≥ 1 per 10 s | 0.3 |
| R6 (if run) | Learned beats writers-removed by > 0.10 (lower bound) | 0.3 |
| R6 (if run) | Learned P windup: most lives have a P outside [0, V_TYP] at some time (single tastes in bursts write ~0.5 V) | 0.75 |
| R7/R8 | A confirmed working learner at all three steps | 0.05 |

Expected first loss if the gate fails: the explorers' long readout plateaus hold the motor above its re-arm
level about half the time (duty ~0.45), masking sensory events (sensory authority), rather than input or writer
failure. Learning, if reached, is expected to be limited by overshooting single writes (no graded credit),
not by a lack of tastes.

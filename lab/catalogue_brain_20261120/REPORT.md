# REPORT — catalogue-native brain (D180 work order), execution 2026-11-20

Executor start 15:50Z, stop ~16:30Z (well within the 12 h cap). One executor, no agents, no commits.

## Incomplete or not-triggered work (listed first)

- **R5 later run at the user's decision and failed its gate (addendum below). R6–R8 not triggered.** Originally: The R3/R4 progression gate failed on bench B's rule "all rail excursions fail":
  one write drove a memory to the supply rail. §4 authorises a revision only for motor-event formation or
  overlap failures. This is a writer-overshoot failure, so no revision was made, and informed action,
  learning, fresh confirmation and step halving did not run. Saved not-triggered records:
  `gate_action.json`, `gate_learn.json`, `gate_confirm.json`, `gate_refine.json`.
- **R10 not triggered.** No working behaviour is claimed. The viewer (`view.py`) was only smoke-tested
  headless (30 recorded frames, seed 8). That is not a live demonstration.
- Nothing required by a triggered obligation is incomplete.

## Addendum — informed action (R5), run at the user's decision after the report above (2026-11-20, 16:50Z)

`run.py action --authorised`: 384/384 lives (32 development seeds × red/blue × 5 arms + 2 all-food arms), 100 s,
native noise, v1 unchanged (simulation hashes equal to the bench's). Log `action_auth.log`; ledger
`action_auth_ledger.jsonl.gz`; traces `lab/v/catalogue_brain_20261120_action_auth.pkl`; gate `gate_action_auth.json`;
tables `tables.md`. The earlier not-triggered `gate_action.json` is kept.

**Result: the R5 gate fails.** Even told the answer, the robot barely finds food.

| measure (final third, per 10 s; seed-paired 95% interval) | value | gate |
|---|---|---|
| informed − neutral, net food | +0.06 [+0.005, +0.11] | lower > +0.10: **fail** |
| informed − reversed, net food | +0.11 [+0.009, +0.22] | lower > +0.10: **fail** |
| informed food rate | 0.19 [0.14, 0.25] | lower ≥ 1: **fail** |
| informed no-meal lives | 4/64 = 0.06 | ≤ 0.20: pass |
| all food: informed − neutral, food rate | +0.15 [−0.05, +0.35] | descriptive |

**Diagnosis (saved records only, no new runs).**
1. **Too few encounters is the main limit.** Lives have a median of 3 meals in 100 s. The eyes fire a median of
   2 pulses/s (the maximum, with a block filling the view, is 50/s per eye). Meals track eye pulses (r = 0.73).
   The explorers fire the thrusters 8 times a second in a random walk that rarely brings a block into view.
   Even perfect discrimination with this many meals could not reach 1 food per 10 s. Without the explorers,
   the robot is stranded (56/64 lives with no meal; 38 never moved).
2. **Sensory steering has the right sign but is weak.** Informed beats neutral (+0.06) and reversed
   (+0.11), and the intervals exclude zero. But each eye pulse adds only ~0.43 thruster firings, against the
   explorers' 8 a second. Removing the sensory paths left food rates similar (0.13 vs 0.19) and roughly doubled
   eye pulses (4.2/s). When it acts at all, firing one thruster on seeing a block tends to turn the robot away
   from it.
3. **Paired-life design note.** With taste withheld and both memories equal (neutral, and the removal arms,
   where the memories no longer matter), a seed's red-poison and blue-poison lives are physically identical. So
   their net is exactly 0 by construction, which is not a bug. The same identity makes informed − reversed
   twice informed − neutral.
4. **Physical-contract findings.** Sensor nodes clipped at the +0.9 V rail during natural bursts of eye pulses
   in 52/64 informed lives (23 steps a life on average). This is the same burst problem the writers showed.
   Without any taste, writers still moved a memory by up to 0.023 V (3 of 192 informed-P lives > 0.01 V):
   a small false write while a burst holds eligibility open.
5. **Metric artefact.** "Seconds with P outside [0, V_TYP]" reads 100 s for informed arms, because P set
   exactly to V_TYP is stored as float32 just above 0.3 V. This is a reporting artefact, not windup. The metric
   code is unchanged, and the artefact is reported here.

Costs per life: circuit ~100 nW (no_sensory 64 nW, no_explore 84 nW); ~8 thruster firings/s, ~0.16 µW at the
guessed 20 nJ each. R6 and later remain not triggered (R5 failed, and learning was not authorised).
**Changed belief:** in this body, the binding shortfall of the catalogue action baseline is encounter rate
(the explorers' undirected walk), ahead of sensory authority. The write-size issue matters only once encounters exist.

## What we learned (benches, before the addendum)

1. **Exploration works and lets the senses through about half the time.** Each motor's own oscillator
   started within 0.08–0.32 s in all 8 component seeds. It ran at 2.3–4.7 cycles/s and gave 203–421 thruster
   events per motor in 90 s of silence, with no rail clipping and no false memory writes (memory drift exactly
   0.0 V: the write driver's dead band holds). A single sensor pulse adds a thruster event when the motor is
   ready (re-armed): 0.82 events per pulse. When the oscillator is holding the motor up, it adds 0.008. The motor
   is not ready 37–52% of the time, so on average a pulse adds 0.43 [0.37, 0.49] events on its fixed side.
   With the oscillators' motor connections removed, every pulse gives exactly 1.0. The predicted masking is
   real and about 2× in size. It is not catastrophic, and missed events are not made up later (excess
   0.00 over the next 0.2 s).
2. **The retained control sets the cross path, but only near its ends.** With P = V_TYP the other motor
   receives 0.43 [0.36, 0.50] more events per pulse than with P = 0, which passes the gate. At the neutral
   P = V_TYP/2 the cross path carries **nothing** (0.00, with or without exploration): half a gate gives the
   motor too little current to cross zero. The neutral birth state therefore behaves like P = 0 for single
   pulses, and only bursts (a second pulse 5–20 ms later) get through it (0.07–0.31).
3. **Learning writes are right in sign but unbounded in size. This is what stopped the work order.**
   An isolated pulse followed by taste 5 ms later wrote 0.03–0.13 V into the right memory, in the right
   direction, in all 32 cases, with zero change to the other memory and zero change in the controls. This
   passes the write gate. But a burst of 10 pulses followed by one taste wrote 0.21–0.99 V (median 0.40 V) in
   all 32 burst cases. That is up to three times the whole 0.3 V range the readout can use. In one case
   (seed 6, sensor 1, food taste) the memory went from 0.15 V to the +0.9 V rail. An exact replay confirms it:
   the burst opened the eligibility gate to 60%, and the writer (+10% gain mismatch) charged a −17% capacitor by
   0.75 V within two ticks (pre-clip 0.904 V, 139 clipped steps). The cause is that a single write's size scales
   with eligibility, which bursts open, and nothing in the circuit limits it.

**Implications for the goal.** The catalogue parts compose into an explorer that keeps the robot
moving and still passes about half of the sensory events. The learning store, however, would spend its whole
range, and more, on a single taste after any approach burst. Without such a limit, the brain would
repeatedly overwrite what it had learned (windup and rail excursions), rather than accumulate
evidence. Whether the action half earns food when told the answer (R5) remains untested. It does not use
the writers, so the failure that stopped the chain does not apply to it (AMENDMENT_PROPOSED.md, item 1).

## Gate ledger R0–R12

| ID | Status | Evidence |
|---|---|---|
| R0 | done | CHECKLIST.md, PROTOCOL.md (frozen interpretations + dated deviations), PREDICTIONS.md, `manifest.json` (HEAD 5700eaa, input/code hashes, seeds, arms, expected rows, budget) |
| R1 | done (valid) | `checks.json`: 30/30 checks pass. The adapter is bit-identical to Circuit.pulse/run. Identical-arm, logging, null-stimulus, chunk-size (1/7/100, native and coupled), snapshot restore (independent clone), paired intervention (first difference at the intervention tick), coupled Brownian increments, wiring independent of variant, no hidden labels, removal keeps draws, held-output-one-event fixture, analysis fixtures (zero movement/meals, window boundaries, zero poison, loss and reacquisition, missing acquisition, duplicate/missing rows). Schematic `schematic_v1.svg` |
| R2 | done | All realised C/R/current/element-slew/self-loop/leak/pulse-slew limits pass for seeds 0–7. Supply fading on. Aggregate deterministic slew at recorded states ≤ 341 V/s (limit 1200). Costs below. Evidence feasibility below |
| R3 | done, **gate failed** | A pass. B: single-pulse write gate pass, but the rail excursion fails B (`bench_A.json`, `bench_B.json`, `diag_rail.json`) |
| R4 | done, C gates pass. Revision decision frozen: **none authorised** | `bench_C.json`, `gate_revision.json` |
| R5 | not triggered | `gate_action.json` (R3/R4 gate failed) |
| R6 | not triggered | `gate_learn.json` |
| R7 | not triggered | `gate_confirm.json`. The seed audit code (`seed_audit.py`) found block 2027010000 unused, but nothing was frozen |
| R8 | not triggered | `gate_refine.json` |
| R9 | done for the completed experiments (benches) | costs/uncertainties below. No lives, so no failed lives and no acquisition accounting |
| R10 | not triggered | no working-behaviour claim |
| R11 | done | HANDOFF.md |
| R12 | done | this report, CHECKLIST.md, discrete/NOTEBOOK.md D181, PROGRAMME.md status, QUESTIONS.md |

**Expected/actual counts.** Bench A: 24 + 8 bias-writer-removed + 4 wiring fixtures = 36/36. Bench C: 1536 trials
(2 variants × 8 seeds × 3 P × 32) + 128 fixtures = 1664/1664, each with a present/omitted pair and 4 second-pulse
pairs. Bench B: 176/176 cases (8 seeds × 22). Its wiring fixtures are 16, against the manifest's 48: the manifest's
arithmetic (4 × 12) was wrong. The code runs the four gate cases (single pulse, 0.005 s, 2 channels × 2 signs) for each
of the four side combinations, as the fixture is meant to. No case was dropped. Lives: 0 of 0 triggered.

## Numbers (95% seed-bootstrap intervals, 10,000 resamples, RNG 180)

| Bench C (8 seeds × 2 channels × 16 times) | full graph | exploration-to-motor removed |
|---|---|---|
| fixed-side excess events per pulse, 0–50 ms (pooled over P) | 0.43 [0.37, 0.49] | 1.00 [1.00, 1.00] |
| other-motor excess, P = V_TYP minus P = 0 | 0.43 [0.36, 0.50] | 1.00 |
| other-motor excess at P = V_TYP/2 | 0.00 | 0.00 |
| side excess when the motor is ready / not ready at onset | 0.82 (n 132 per P) / 0.008 (n 124) | 1.0 / — |
| excess 50–250 ms (catch-up or phase shift) | 0.00 | 0.00 |
| median first-event latency / re-arm latency | 5.4 ms / 18.5 ms | 4.2 ms / 17.8 ms |
| second pulse after 5 / 20 / 50 / 200 ms, side excess | −0.01 / 0.08 / 0.45 / 0.43 | 0.00 / 0.25 / 1.00 / 1.00 |

Bench B: single pulse and taste 5 / 50 / 200 ms later wrote 0.029–0.132 / 0.021–0.102 / 0.000–0.016 V (correct direction).
The 10-pulse train wrote 0.21–0.99 V. The controls (no taste, no pulse) and the other memory moved 0.000 V. Both
sensors pulsed together wrote both memories (~0.03–0.13 V each), as designed: no hidden winner. Wiring
fixtures (seed 0, all four side combinations): writes 0.044–0.061 V; C side 0.34–0.41 and plastic 0.38–0.41 events.

## Costs (R2/R9)

| control | transistors | resistors | capacitors | diodes | bias sources | static power (nominal) |
|---|---|---|---|---|---|---|
| full v1 | 770 | 97 | 27 | 6 | 88 | 77.5 nW |
| exploration-to-motor removed | 704 | 91 | 27 | 6 | 80 | 63.8 nW |
| sensory paths removed | 618 | 81 | 27 | 6 | 70 | 47.7 nW |
| writers removed | 592 | 77 | 27 | 6 | 70 | 70.1 nW |
| oscillator bias writers removed | 694 | 87 | 23 | 6 | 80 | 76.4 nW |

These are `minimal.spice.count` of chip.py's blocks, with no SPICE run. They include the 4 SONOS cells and their write
switches, 2 charge pumps (counted as sources), gate pairs, and 60/V preamplifiers on every sigmoid (above the native
26/V). Memory high-voltage supply energy is **unmeasured** (not zero). At rest (bench A), the supply delivered
90–112 nW (98.7 nW mean with the oscillator bias writers removed). Each motor fired 2.3–4.7 times a second. At the
guessed 20 nJ per firing, two motors spend ~0.14 µW moving, which exceeds the circuit's own power and is ~14% of
the 1 µW resting metabolism. Removing the bias writers changed the oscillators little over 100 s (frequency 2.2–4.8
vs 2.3–4.7 Hz; events 196–436 vs 203–421). The bias memories moved within −0.08…+0.10 V.
This is a chip-constrained noisy block-model candidate, not a fabricated chip or a SPICE validation.

## Evidence feasibility (R2), in bits

The unknown is one bit: which colour is food (balanced prior). The informed arm would be told it; that arm
did not run. The causal evidence is a taste following this robot's own sensor history. The two exploratory
sources (one oscillator per motor) are independent. A write's signal is far above the silicon noise: a full-gate
write is nominally ~0.7 V, against writer shot noise of ~0.15 mV per write (√(q·I·τ)/C). Reaching
"acquired" from neutral needs ±0.09 V. One isolated-pulse taste supplies 0.03–0.13 V; one burst taste
supplies 0.2–1.0 V. **So evidence quantity is not the binding risk: a single taste suffices, and usually
overshoots.** The binding risks are overshoot and wrong-sign credit. When both sensors' traces are open at a
taste, both memories are written the same way (bench B, both pulses). The optimal same-senses history model is
unknown. Tastes per second in these lives were not measured, because no protocol lives ran.

## Limitations

- These are component benches only. No closed-loop reward was measured under the protocol.
- The rail excursion occurred in 1 of 32 burst cases. The gate rule makes one sufficient. Overshoot beyond the
  readout range occurred in 32 of 32.
- The bench ran at DT only. Step refinement was not triggered.
- Before the freeze, code tests on seed 0 and two 10 s development lives were seen (PROTOCOL, Deviations). The
  design and gates are fixed by the work order, and nothing was tuned.
- `bench.py`'s output-file name was fixed after the bench ran (PROTOCOL, Deviations). No result changed.

## Provenance

Code: `lab/catalogue_brain_20261120/{brain,lives,analyse,checks,preflight,bench,run,report,view,schematic_v1,
seed_audit,diag_rail,make_manifest}.py`. Hashes are in `manifest.json` (at freeze) and in each `gate_*.json`
(`code`, `sim_code`). After the freeze, `bench.py` changed (output name only), and `report.py` and `diag_rail.py`
were added. The simulation code (`sim_code`) is unchanged from check to the end. Repository HEAD 5700eaa. All
engine/body files are unmodified (their hashes are in the manifest). The D180 inputs (work order, DESIGN.md,
design.py) are uncommitted, and their hashes are in the manifest. Outputs: `lab/v/catalogue_brain_20261120/` (bench_A/B/C.json,
checks.json, preflight.json, diag_rail.json, gates, tables.md regenerated by `run.py report`, bench.log). No
trace archive was needed (no lives). Commands: PREPARATION.md.

## Next

A reviewer decision is required: (1) authorise R5 informed action on v1 as it stands, since it does not use the
failed writers (AMENDMENT_PROPOSED.md, about 1 minute), and/or (2) choose whether, and how, single writes should be
bounded (HANDOFF.md). There is no remaining command under this work order. The work order stops here.

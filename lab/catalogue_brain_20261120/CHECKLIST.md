# CHECKLIST — catalogue-native brain work order (D180), executor ledger

Executor start: 2026-11-20T15:50Z. Hard cap 12 h (ends 2026-11-21T03:50Z). Statuses: pending / done / not triggered / incomplete.
This ledger is rewritten as work proceeds; the final state is audited in REPORT.md (R12).

| ID | Status | Trigger | Artifact / command | Measured gate | Unresolved work |
|---|---|---|---|---|---|
| R0 | done | Always; before data | CHECKLIST.md, PROTOCOL.md, PREDICTIONS.md, lab/v/.../manifest.json (make_manifest.py) | frozen 2026-11-20T16:02:38Z, before `run.py check`; pre-freeze code tests disclosed in PROTOCOL Deviations | none |
| R1 | done | Always | brain.py, checks.py; `run.py check` → checks.json, gate_check.json (valid), schematic_v1.svg | 30/30 checks pass | none |
| R2 | done | Always | checks.json (physical, costs, realised arrays seeds 0–7), preflight.json; REPORT §Costs, §Evidence feasibility | all limits pass; aggregate slew ≤341 V/s (limit 1200) | memory HV supply energy unmeasured (stated) |
| R3 | done — gate FAILED | R1 valid | `run.py bench` → bench_A.json (pass), bench_B.json (fail: 1 rail excursion), diag_rail.json | A pass; B single-pulse gate pass; B rail excursion (seed 6 train, P1 → +0.9 V) | none (failure is the result) |
| R4 | done; revision: none authorised | R1 valid | bench_C.json, bench_progression.json, gate_bench.json, gate_revision.json | side 0.43 [0.37,0.49] > 0.25; plastic diff 0.43 [0.36,0.50] > 0.25; no clip | none |
| R5 | done at user's decision — gate FAILED | R3/R4 failed; user authorised R5 anyway (PROTOCOL deviations) | `run.py action --authorised` → gate_action_auth.json, action_auth_ledger.jsonl.gz (384/384), action_auth_summary.json; gate_action.json (not triggered) kept | informed−neutral +0.06 [+0.005,+0.11]; informed−reversed +0.11 [+0.009,+0.22]; food 0.19 [0.14,0.25]; no-meal 0.06 | diagnosis from existing traces done (REPORT addendum) |
| R6 | not triggered | R5 pass — not triggered | gate_learn.json | — | — |
| R7 | not triggered | R6 pass — not triggered | gate_confirm.json | — | — |
| R8 | not triggered | as R7 | gate_refine.json | — | — |
| R9 | done (benches and R5 lives) | every completed experiment | REPORT §Numbers, §Costs; tables.md (`run.py report`) | — | no lives ran: no failed-life/acquisition accounting applies |
| R10 | not triggered | confirmed working-behaviour claim — none | view.py smoke-tested headless only (not a demo) | — | — |
| R11 | done | Always | HANDOFF.md | — | — |
| R12 | done | Always | REPORT.md; this file; discrete/NOTEBOOK.md D181; PROGRAMME.md; QUESTIONS.md | hashes reconciled (REPORT §Provenance) | reviewer decision |

## Stage estimates (recorded before each stage, from preflight timing)

- 16:03Z bench (R3/R4): A 36 runs (~1.6 s each), B 224 short runs, C 2×8×3 prefixes + 1664 trials with forks:
  estimate ~4 min single process (code-test timing on seed 0: A 1.6 s, B 0.6 s/22 cases, C 2.1 s per seed-P).
  Envelope 2 h: fits.
- 16:05Z bench finished in ~2 min (A 30 s, B 5 s, C 88 s). R3/R4 gate failed; R5–R8 wrote not-triggered records.
- Remaining stages' estimates (not run): action 57 s, learn 29 s, confirm+refine 19–37 min at N 128–256 (preflight.json).
- ~16:20Z authorised R5 (`run.py action --authorised`): 384 lives, estimate 57 s on 7 workers (preflight). Fits.

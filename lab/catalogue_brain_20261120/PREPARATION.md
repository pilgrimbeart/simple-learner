# PREPARATION — exact commands (D180 execution)

From the repository root:

```sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
.venv/bin/python lab/catalogue_brain_20261120/make_manifest.py      # R0: freeze manifest.json (once)
.venv/bin/python lab/catalogue_brain_20261120/run.py check          # R1/R2: checks.json, preflight.json, schematic_v1.svg, gate_check.json
.venv/bin/python lab/catalogue_brain_20261120/run.py bench          # R3/R4: bench_A/B/C.json, gate_bench.json
.venv/bin/python lab/catalogue_brain_20261120/run.py action --dry-run
.venv/bin/python lab/catalogue_brain_20261120/run.py action         # R5 (refuses without gate_bench R3R4_pass; else not-triggered record)
.venv/bin/python lab/catalogue_brain_20261120/run.py learn          # R6
.venv/bin/python lab/catalogue_brain_20261120/run.py confirm --dry-run
.venv/bin/python lab/catalogue_brain_20261120/run.py confirm        # R7 (DT, coupled noise)
.venv/bin/python lab/catalogue_brain_20261120/run.py refine         # R8 (DT/2, DT/4 from the same frozen ledger)
.venv/bin/python lab/catalogue_brain_20261120/run.py report         # tables regenerated from the ledgers
.venv/bin/python lab/catalogue_brain_20261120/view.py SEED          # live viewer (creature.watch, lab brain registered in-process)
```

Outputs: `lab/v/catalogue_brain_20261120/`; trace archives `lab/v/catalogue_brain_20261120_<stage>.pkl` (git-ignored).
Every stage refuses to overwrite and refuses to run without the previous stage's saved gate.

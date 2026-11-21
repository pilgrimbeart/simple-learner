# First four dynamic circuit witnesses — D126

Silicon-noise bench results with component mismatch. These are component tests, not robot learning.

| Circuit | Fresh seeds passing all 3 steps | Wilson 95% interval | Both refinements | Mean core power, 95% bootstrap | States / connections | Verdict |
|---|---:|---|---|---|---|---|
| trace | 40/40 | 0.912–1.000 | True | 0.5443 nW [0.5442, 0.5444] | 1 / 0 | demonstrated within this protocol |
| memory | 40/40 | 0.912–1.000 | True | 2.651 nW [2.546, 2.758] | 1 / 1 | demonstrated within this protocol |
| resonator | 40/40 | 0.912–1.000 | True | 6.4 nW [6.287, 6.513] | 2 / 2 | demonstrated within this protocol |
| oscillator | 37/40 | 0.801–0.974 | True | 9.995 nW [9.748, 10.24] | 2 / 3 | unresolved under this protocol |

Each seed is a separate component-tolerance draw. Its three timestep evaluations are paired, not three independent seeds.
The threshold is a Wilson lower bound of 0.90; the 40/40 outcome supports a lower bound of about 0.912, not universal reliability.
Removal controls passed on the eight pilot seeds. Core power excludes external bench stimulation and recording equipment.

## What changed after the first pilot

All original graphs/settings were retained. A gentler, longer programming pulse removed memory rail overdrive.
The resonator criterion changed explicitly from a peak at the exact nominal frequency to a measured interior peak,
with a denser fixed frequency grid. This confirms frequency selection, not immunity of frequency to mismatch.
The oscillator removal check was corrected to measure fluctuation rather than static voltage offset.
The initial protocol, source snapshot, results and diagnosis remain alongside the revised files.

## Oscillator failure diagnosis

All three failed draws settle near stable fixed points. Replaying with noise and analysing the local mean-drift Jacobian
finds eigenvalue real parts between -5.85 and -6.61 per second. This explains decay toward rest, not a sustained cycle.
The tiny voltage fluctuations yield noise crossings; their raw crossing rates are not oscillation frequencies.
Diagnosis: `oscillator_failure_diagnosis_v2.json`; script: `lab/dynamic_parts_failure.py`.

## Reproduction and limits

Frozen specification: `protocol_v2.json`; all rows: `confirm_v2.jsonl`; provenance and file hashes: `confirm_provenance_v2.json`.
Run `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/dynamic_parts_bench.py confirm` from the repository.
The runner refuses to overwrite existing results; archive the result files deliberately before a separate replication.
View `confirm_replay.html` or run `lab/dynamic_parts_view.py --stage confirm --live-seconds 15` with that Python.
No engine/noise edits, internal filtered channels, biological-noise claim, SPICE validation or body/interface change.
Retained nonvolatile memory and controlled writes remain untested. The bit here is actively held bistable state.
Source analysis: `lab/dynamic_parts_report.py`; full numeric detail: `confirm_detail_v2.json`.

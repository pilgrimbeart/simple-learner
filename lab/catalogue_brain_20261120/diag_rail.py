"""D180 R3 diagnosis (existing case, deterministic replay): bench B seed 6, 10-pulse train on S1, positive taste,
the one rail excursion. Replays the saved case exactly (must reproduce its saved dP), adding per-tick P1, E1, T and
the pre-clip extreme. Writes lab/v/catalogue_brain_20261120/diag_rail.json (refuses to overwrite)."""
import json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1])); sys.path.insert(0, str(HERE))
import bench
from units import TICK, V_TYP
OUT = HERE.parents[1] / "lab/v/catalogue_brain_20261120/diag_rail.json"
if OUT.exists():
    raise SystemExit("exists")
saved = [r for r in json.loads((OUT.parent / "bench_B.json").read_text())["runs"]
         if r["seed"] == 6 and r["case"] == dict(kind="train", ch=1, sign=1, delay=0.005)][0]
rep = bench.bench_B_case(6, saved["case"])
e = bench.eng(6)
ix = e.ix
a = bench.amp(e)
t0 = 1.0 + saved["jitter_s"]
pulses = [(t0 + 0.02 * i, ix["S1"], a) for i in range(10)]
tT = pulses[-1][0] + 0.005
pulses.append((tT, ix["T"], a))
bench.run_until(e, t0 - TICK)
e.reset_obs()
trace = []
pend = sorted(pulses)
while e.t_step * e.dt < tT + 0.1:
    start = e.t_step * e.dt
    while pend and pend[0][0] < start + TICK - 1e-12:
        t, nd, cur = pend.pop(0); e.pulse(nd, cur, max(t - start, 0.0))
    e.run_tick()
    trace.append([round(start + TICK, 3)] + [float(e.V[ix[n]]) for n in ("S1", "E1", "T", "P1")])
tr = np.array(trace)
writes = np.diff(tr[:, 4])
out = dict(reproduces_saved_dP=bool(abs(rep["dP"][1] - saved["dP"][1]) < 1e-12), saved_dP=saved["dP"], replay_dP=rep["dP"],
           E1_at_taste=float(tr[np.searchsorted(tr[:, 0], tT) - 1, 2]), gate_at_taste=float(np.clip(tr[np.searchsorted(tr[:, 0], tT) - 1, 2] / V_TYP, 0, 1)),
           T_peak=float(tr[:, 3].max()), P1_before=float(tr[0, 4]), P1_max=float(tr[:, 4].max()),
           preclip_extreme_P1=float(e.preclip_o[ix["P1"]]), clip_steps_P1=int(e.clip_o[ix["P1"]]),
           ticks_with_write=int((np.abs(writes) > 1e-6).sum()), realised_writer_gain_A=float(e.el[0, e.enames.index("write_positive_1")]),
           realised_P1_cap_F=float(e.node[2, ix["P1"]]), realised_T_cap_F=float(e.node[2, ix["T"]]),
           trace_cols=["t_end_s", "S1", "E1", "T", "P1"], trace=tr.tolist())
OUT.write_text(json.dumps(out, indent=1) + "\n")
print({k: v for k, v in out.items() if k != "trace"})

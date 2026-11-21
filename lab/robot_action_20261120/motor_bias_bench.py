"""D178 R8.2 operating region: motor units' own firing (no input, 10 s, silicon, seeds 0-31) against the motor neurons'
bias current (mixed_feedback.Circuit.neuron's existing `bias`; default -1.6 nA at the historical 1 V), and their
response to a sensor's spike is left to the replay screen. Measured to choose the family's settings before comparison.
python motor_bias_bench.py -> lab/v/robot_action_20261120/motor_bias_bench.json"""
import json, os, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1])); sys.path.insert(0, str(HERE))
BIASES = [-1.6e-9, -1.5e-9, -1.45e-9, -1.4e-9, -1.35e-9, -1.3e-9, -1.2e-9, -1.0e-9]
def job(a):
    seed, I, sub = a
    import brain as B
    b = B.make_brain(sub, True, True, ("motor", I), log=False)(seed)
    s = b.circuit.run(10.0)
    return seed, I, [int(s[m]) / 10.0 for m in b.motors]
if __name__ == "__main__":
    for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"): os.environ[k] = "1"
    import multiprocessing
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(7, mp_context=multiprocessing.get_context("spawn")) as p:
        res = list(p.map(job, [(s, I, "silicon") for I in BIASES for s in range(32)]))
    out = {}
    for I in BIASES:
        r = np.array([x for s, i, v in res if i == I for x in v])
        out[f"{I:.3g}"] = dict(p10_50_90=[float(np.percentile(r, q)) for q in (10, 50, 90)],
                               share_silent=float((r < 0.1).mean()), share_above_30=float((r > 30).mean()))
        print(f"{I:.3g}", out[f"{I:.3g}"])
    json.dump(dict(summary=out, units=res), open(HERE.parents[1] / "lab/v/robot_action_20261120/motor_bias_bench.json", "w"), indent=1)

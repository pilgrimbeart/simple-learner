"""D178 R13: costs of the compared designs (informed lives, seeds 0-31 x red/blue, 100 s). Circuit power is the engine's
own supply accounting (Circuit.power(): historical contract, rails at 3 typical voltages, on_chip False: NOT a chip
figure); motor activity = thruster firings; communication = spikes on the sensor->motor and motor lines; material =
the graph's nodes, elements, memory nodes and filtered elements (no transistor count: the historical circuit is not
built in chip.py blocks). Thruster energy uses minimal/spec.py's FIRING guess, labelled as such.
python costs.py -> lab/v/robot_action_20261120/costs.json"""
import json, os, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1])); sys.path.insert(0, str(HERE))
def job(a):
    sub, bias, seed, poison = a
    import brain as B
    from creature import Life
    life = Life(seed, poison, False, B.make_brain(sub, True, True, bias, log=False))
    b = life.brain
    food = "blue" if poison == "red" else "red"
    b.circuit.start[b.P[life.sensor[food]]] = 1.0
    b.circuit.start[b.P[life.sensor[poison]]] = 0.0
    sp = 0
    while life.t < 10000:
        life.step()
    c = b.circuit
    return dict(sub=sub, bias=bias, power_W=c.power(), firings=len(life.firings))
if __name__ == "__main__":
    for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"): os.environ[k] = "1"
    import multiprocessing
    from concurrent.futures import ProcessPoolExecutor
    from minimal.spec import FIRING
    designs = [("biology", None), ("silicon", None), ("silicon", ("motor", -1.3e-9))]
    jobs = [(s, b, seed, p) for s, b in designs for seed in range(32) for p in ("red", "blue")]
    with ProcessPoolExecutor(7, mp_context=multiprocessing.get_context("spawn")) as pool:
        res = list(pool.map(job, jobs))
    import brain as B
    b = B.make_brain("silicon")(0); c = b.circuit
    material = dict(nodes=len(c.nodes), memory_nodes=int(sum(n[5] for n in c.nodes)), elements=len(c.elements),
                    filtered_elements=int(sum(1 for e, _ in c.elements if e[3] > 0)), gated_elements=int(sum(1 for _, l in c.elements if l[2] >= 0)))
    out = dict(material_all_designs=material, firing_energy_J_guess=FIRING, designs={})
    for s, bb in designs:
        R = [r for r in res if r["sub"] == s and r["bias"] == bb]
        p = [r["power_W"] for r in R]; f = [r["firings"] for r in R]
        out["designs"][f"{s}_{bb}"] = dict(circuit_power_W_mean=float(np.mean(p)), circuit_power_W_p10_90=[float(np.percentile(p, 10)), float(np.percentile(p, 90))],
                                           firings_per_life_mean=float(np.mean(f)), thruster_energy_J_per_life_guess=float(np.mean(f) * FIRING))
    json.dump(out, open(HERE.parents[1] / "lab/v/robot_action_20261120/costs.json", "w"), indent=1)
    print(json.dumps(out, indent=1))

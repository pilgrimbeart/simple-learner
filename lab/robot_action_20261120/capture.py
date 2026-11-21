"""Robot-action investigation (D178): closed-loop captures on unmodified creature.Life lives (body, world, interface
unchanged) of the lab adapter brain.make_brain. Arms (each with D176's repairs: memory knobs, writer thresholds 0.8 V):
  learn     taste-driven learning
  frozen    taste withheld (Life's learning=False), knobs start at 0.5 as built
  informed  taste withheld, food's knob starts at F, poison's at Q (default 1, 0). PRIVILEGED: told wiring and valence
  allfood   both colours food, learning on (control)
Arm spec: <arm>[@F,Q]  (informed only).  Options: substrate biology|silicon; step divisor 1|2|4; bias group:I_in_A.
python capture.py <arm[@F,Q]> <substrate> <seed0> <seed1> [div] [bias=sensor:-1.5e-9]
-> ~/nca-scratch-backup/robot_action_20261120/<tag>.pkl (full traces) and lab/v/robot_action_20261120/ledger/<tag>.csv
"""
import csv, hashlib, os, pickle, sys, time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
OUT = ROOT / "lab/v/robot_action_20261120"
BIG = Path.home() / "nca-scratch-backup/robot_action_20261120"
SECONDS = 100.0


def parse(spec):
    arm, _, knob = spec.partition("@")
    F, Q = (float(x) for x in knob.split(",")) if knob else (1.0, 0.0)
    return arm, F, Q


def one(job):
    spec, substrate, seed, poison, div, bias = job
    arm, F, Q = parse(spec)
    import mixed_feedback as mf
    if div > 1:
        from units import DT
        mf.DT = DT / div
    from creature import Life
    from units import TICK
    import brain as B
    Brain = B.make_brain(substrate, True, True, bias)
    life = Life(seed, None if arm == "allfood" else poison, arm in ("learn", "allfood"), Brain)
    b = life.brain
    if arm == "informed":
        food = "blue" if poison == "red" else "red"
        b.circuit.start[b.P[life.sensor[food]]] = F
        b.circuit.start[b.P[life.sensor[poison]]] = Q
    n = int(round(SECONDS / TICK))
    pos = np.empty((n, 2), np.float32)
    while life.t < n:
        life.step()
        pos[life.t - 1] = life.body.pos
    return dict(spec=spec, arm=arm, F=F, Q=Q, substrate=substrate, seed=seed, poison=poison, div=div, bias=bias,
                sensor=dict(life.sensor), motor=dict(life.motor), moving=life.moving, meals=list(life.meals),
                firings=list(life.firings), wiring=B.wiring(b), draws=B.draws_hash(b),
                rows=np.array(b.rows, dtype=np.float32), pulses=np.array(b.pulses, dtype=np.float64).reshape(-1, 2),
                tastes=np.array(b.tastes, dtype=np.float64).reshape(-1, 2), pos=pos)


def tag(spec, substrate, s0, s1, div, bias):
    t = f"{spec.replace('@', '_at').replace(',', '-')}_{substrate}_s{s0}-{s1}"
    if div > 1:
        t += f"_div{div}"
    if bias:
        t += f"_bias-{bias[0]}{bias[1]:.3g}"
    return t


def run(spec, substrate, s0, s1, div=1, bias=None, workers=7):
    import multiprocessing
    from concurrent.futures import ProcessPoolExecutor
    jobs = [(spec, substrate, s, p, div, bias) for s in range(s0, s1 + 1) for p in ("red", "blue")]
    arm = parse(spec)[0]
    if arm == "frozen" or arm == "allfood":
        pass
    start = time.monotonic()
    with ProcessPoolExecutor(workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        res = list(pool.map(one, jobs))
    t = tag(spec, substrate, s0, s1, div, bias)
    BIG.mkdir(parents=True, exist_ok=True)
    with (BIG / f"{t}.pkl").open("wb") as f:
        pickle.dump(res, f)
    ledger(res, t)
    print(t, "done", round(time.monotonic() - start, 1), "s", flush=True)
    return res


def ledger(res, t):
    import metrics as M
    (OUT / "ledger").mkdir(parents=True, exist_ok=True)
    with (OUT / "ledger" / f"{t}.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["spec", "substrate", "seed", "poison", "div", "sensor_red", "motor_left", "side_motor_S0",
                    "side_motor_S1", "draws", "moving_s", "food_final_third", "poison_final_third", "food_after_move",
                    "poison_after_move", "meals_total", "stranded", "P_food_end", "P_poison_end", "motor_spikes",
                    "sensor_spikes", "pulses", "path_m", "trace_sha"])
        for r in res:
            m = M.life(r)
            w.writerow([r["spec"], r["substrate"], r["seed"], r["poison"], r["div"], r["sensor"]["red"],
                        r["motor"]["left"], r["wiring"][0]["side_motor"], r["wiring"][1]["side_motor"], r["draws"],
                        None if r["moving"] is None else r["moving"] * 0.01, m["food_ft"], m["poison_ft"],
                        m["food_am"], m["poison_am"], len(r["meals"]), int(not r["meals"]), m["P_food_end"],
                        m["P_poison_end"], int(r["rows"][:, 6:8].sum()), int(r["rows"][:, 4:6].sum()),
                        len(r["pulses"]), round(m["path"], 4),
                        hashlib.sha256(r["rows"].tobytes()).hexdigest()[:12]])


if __name__ == "__main__":
    for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[k] = "1"
    a = sys.argv[1:]
    div = int(a[4]) if len(a) > 4 and not a[4].startswith("bias=") else 1
    bias = None
    for x in a:
        if x.startswith("bias="):
            g, I = x[5:].split(":")
            bias = (g, float(I))
    run(a[0], a[1], int(a[2]), int(a[3]), div, bias)

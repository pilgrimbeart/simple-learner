"""stage2_cost.py: is Python fast enough for the rules? GRAMMAR.md says a numba interpreter is needed, a rule in Python running hundreds of thousands of times a life. Measured: for each world, one process, 3 seeds x 2 lives at the base brain and the bank: seconds a life, how many times its rule functions were called, their share of the life's time (perf_counter around each call, the timer's own cost included, so an upper bound), against plain. Run alone on the machine.

    OPENBLAS_NUM_THREADS=1 .venv/bin/python lab/stage2_cost.py"""
import sys
import time
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import numpy as np
from stage2_lang import arms as S, worlds as WW

SEEDS = (63400, 63401, 63402)
STAGES = ("tick", "see", "pulse", "fire", "move", "meal", "respawn", "taste", "score")


def one(text, arm, seed, first, count):
    lf = S.make(S.world_of(text), arm, seed, first)
    box = dict(calls=0, spent=0.0)
    if count:
        for s in STAGES:
            f = getattr(lf, "f_" + s)
            if f is not None:
                def wrapped(*a, f=f):
                    t0 = time.perf_counter()
                    r = f(*a)
                    box["spent"] += time.perf_counter() - t0
                    box["calls"] += 1
                    return r
                setattr(lf, "f_" + s, wrapped)
    t0 = time.perf_counter()
    S.live(lf)
    return time.perf_counter() - t0, box["calls"], box["spent"]


def main():
    print("world, arm: s a life (no timers) | rule calls a life | seconds in rules, share of the timed life", flush=True)
    base = {}
    for n in WW.W:
        t = WW.W[n]["text"]
        if S.world_of(t).tag() == 5:
            continue
        for arm in ("circuit", "bank"):
            plain = [one(t, arm, s, c, False)[0] for s in SEEDS for c in S.COL]
            timed = [one(t, arm, s, c, True) for s in SEEDS for c in S.COL]
            T = float(np.mean(plain))
            base.setdefault(arm, T)
            calls = float(np.mean([x[1] for x in timed]))
            spent = float(np.mean([x[2] for x in timed]))
            whole = float(np.mean([x[0] for x in timed]))
            print(f"{n:20s} {arm:8s} {T:6.3f} s ({T / base[arm]:4.2f} x plain) | {calls:8.0f} calls | {spent:6.3f} s, {spent / whole:5.1%}", flush=True)


if __name__ == "__main__":
    main()

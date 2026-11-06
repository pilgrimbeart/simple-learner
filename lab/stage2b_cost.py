"""stage2b_cost.py: stage 2b, part 5 (the coordinator's addition, 2026-11-06): a life's cost, measured on a handful of lives, at the 10 ms
tick and 100 s (as run), at 1 ms and 100 s, and at 10 ms and 1000 s. Base, bank and the reference; plain and three random worlds; seeds
65900-65901 x 2. Each life in a fresh worker process (the tick is set per process, as lab/stage2_checks.set_tick). Wall seconds of one
core per life; nothing about outcomes is read.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage2b_cost.py > lab/v/stage2b_cost.log"""
import sys
import time
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np


def one(job):
    text, arm, seed, first, dt, seconds = job
    import stage2_checks as C
    from stage2_lang import arms as S
    C.set_tick(dt)
    t0 = time.perf_counter()
    lf = S.make(S.world_of(text), arm, seed, first)
    S.live(lf, seconds)
    return time.perf_counter() - t0, lf.t


if __name__ == "__main__":
    import stage2b_gen as G
    worlds = [("plain", "(world)")] + [(f"g{n}", G.draw(n)[0]) for n in G.development(100)[:3]]
    print("== a life's cost, wall seconds on one core (7 workers, one life each, a fresh process per life); mean over 4 lives", flush=True)
    with ProcessPoolExecutor(7, max_tasks_per_child=1) as ex:
        for dt, sec in ((0.01, 100.0), (0.001, 100.0), (0.01, 1000.0)):
            for arm in ("circuit", "bank", "ref"):
                jobs = [(t, arm, s, c, dt, sec) for _, t in worlds for s in (65900, 65901) for c in ("red", "blue")]
                R = list(ex.map(one, jobs))
                per = np.array([r[0] for r in R]).reshape(len(worlds), 4).mean(1)
                print(f"  tick {dt * 1000:g} ms, {sec:g} s lives, {arm:8s}: " + ", ".join(f"{w} {p:.2f}" for (w, _), p in zip(worlds, per))
                      + f"; mean {per.mean():.2f} s a life ({R[0][1]} ticks)", flush=True)

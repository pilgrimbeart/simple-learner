"""speed_bench.py: seconds a life on one core, nothing else running (main session, 2026-11-06). swap10, seconds mode, base and bank, at
10 ms and 1 ms, 3 lives each after one to warm up. inst=0 switches the stage-5 instruments off.

    OPENBLAS_NUM_THREADS=1 .venv/bin/python lab/speed_bench.py [inst=1]"""
import sys, time
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from stage2_lang import sim, arms as _A
_A.FAST = "fast=1" in sys.argv
sim.WLife.instruments = "inst=0" not in sys.argv
import stage2_checks as C
from stage2_lang import arms as S, worlds as WW

for dt in (0.01, 0.001):
    C.set_tick(dt)
    for arm in ("circuit", "bank"):
        w = S.world_of(WW.W["swap10"]["text"])
        S.live(S.make(w, arm, 60999, "red"))
        t = time.time()
        for s in range(3):
            S.live(S.make(w, arm, 61000 + s, "red"))
        print(f"{arm:8s} {dt * 1000:4g} ms  {(time.time() - t) / 3:.2f} s a life  (instruments {"on" if sim.WLife.instruments else "off"}, fast {_A.FAST})", flush=True)

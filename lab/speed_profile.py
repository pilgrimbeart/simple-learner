"""speed_profile.py: where a life's time goes, before speeding the engine up (main session, 2026-11-06). One world, one arm, a few lives,
cProfile's top functions by own time.

    .venv/bin/python lab/speed_profile.py plain bank 0.01 1"""
import cProfile, pstats, sys, time
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from stage2_lang import sim as _sim
_sim.WLife.instruments = False
from stage2_lang import arms as _A
_A.FAST = True
import stage2c_steps as P

world, arm, dt, secs = sys.argv[1], sys.argv[2], float(sys.argv[3]), bool(int(sys.argv[4]))
P._init(dt, secs)
P.one((world, arm, 60000, "red", secs))
t = time.time()
pr = cProfile.Profile()
pr.enable()
for s in range(4):
    P.one((world, arm, 60001 + s, "red", secs))
pr.disable()
print(f"{world} {arm} {dt * 1000:g} ms seconds={secs}: {(time.time() - t) / 4:.2f} s a life (profiled)")
pstats.Stats(pr).sort_stats("tottime").print_stats(22)

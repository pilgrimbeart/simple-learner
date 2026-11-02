import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from concurrent.futures import ProcessPoolExecutor
import arena_tune as T
one = dict.fromkeys(T.KNOBS, 1.0)
tuned = dict(one, scan=2.0, hold=0.5)
c = {"scan 0": dict(one, scan=1e-9), "scan 0, run 0": dict(one, scan=1e-9, run=1e-9),
     "scan 0, hold 0.5": dict(one, scan=1e-9, hold=0.5), "scan 0.25": dict(one, scan=0.25)}
if __name__ == "__main__":
    with ProcessPoolExecutor() as ex:
        for name, a in c.items():
            for bname, b in (("tracker", one), ("tuned", tuned)):
                m, (lo, hi) = T.compare(ex, range(0, 16), 300.0, a, b)
                print(f"{name} - {bname}: {m:+.3f} [{lo:+.3f}, {hi:+.3f}]", flush=True)

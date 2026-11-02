"""Why does keeping still pay among escape growers (alert.py) but cost among trackers (arena_tune.py)? Per kind: eaten,
lost to bites, firing cost, a 10 s, and age, over arenas 0-7."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np
from concurrent.futures import ProcessPoolExecutor
import arena as AR
from units import TICK
MODE = sys.argv[1]


def run(seed):
    if MODE == "alert":
        import alert
        alert.AL.update(mode="still", always=1.0)
        A = AR.Arena(seed, 10, ("alert", "grow"))
    else:
        import arena_tune as T
        one = dict.fromkeys(T.KNOBS, 1.0)
        A = AR.Arena(seed, 10, (("tracker", dict(one, scan=1e-9, run=1e-9), "still"), ("tracker", one, "tracker")))
    for _ in range(int(300 / TICK)):
        A.step()
    return [(r.kind, r.ate / (d - r.born) * 10, r.lost / (d - r.born) * 10, AR.THRUST * r.firings / (d - r.born) * 10,
             d - r.born) for r, d in [(r, A.t) for r in A.robots] + A.dead if d - r.born >= 20]


if __name__ == "__main__":
    with ProcessPoolExecutor() as ex:
        rows = [x for res in ex.map(run, range(8)) for x in res]
    for k in sorted({r[0] for r in rows}):
        x = np.array([r[1:] for r in rows if r[0] == k])
        print(f"{MODE} {k:8s}: n {len(x)}, ate {x[:,0].mean():.3f}, lost {x[:,1].mean():.3f}, firing {x[:,2].mean():.3f}, "
              f"net {(x[:,0]-x[:,1]-x[:,2]).mean():+.3f} a 10 s, age {x[:,3].mean():.0f} s")

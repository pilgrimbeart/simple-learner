import sys; sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from discrete.circuits import learn_hold
from discrete.life import live
kw = eval(sys.argv[1]) if len(sys.argv) > 1 else {}
def one(a):
    seed, c = a
    net = learn_hold(np.random.default_rng(seed + 5_000_011), **kw)
    r = live(net, seed, 100.0, poison=c, probe=("h", "c0", "q"))
    tr = np.array(r["trace"])
    from creature import Life
    lf = Life(seed, c, brain=lambda s: None) if False else None
    food = [t for t, _ in r["meals"]]
    return seed, c, r["meals"], tr
with ProcessPoolExecutor(8) as ex:
    for seed, c, meals, tr in ex.map(one, [(s, c) for s in range(0, 8) for c in ("red", "blue")]):
        h, c0 = tr[:, 0], tr[:, 1]
        thirds = [sum(1 for m in meals if k * 3333 <= m[0] < (k + 1) * 3333) for k in range(3)]
        print(f"seed {seed} {c:4s} meals per third {thirds}  h>2V {np.mean(h > 2):.0%}  h mean {h.mean():.2f}  latch flips {int(np.sum(np.abs(np.diff(c0 > 0.6))))}  c0 high {np.mean(c0 > 0.6):.0%}")

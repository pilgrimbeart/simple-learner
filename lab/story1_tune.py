"""story1_tune.py: each manual intervention of the pilot story tuned on training seeds 0-63 x 2, by efficiency, on a
grid (lab/story1.py; the held-out seeds untouched)."""
import itertools, sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from story1 import lives, M
from minimal.spec import summary, efficiency

p, spread = M.from_bench()
step = p["step"]
GRIDS = {
    # a bit flipped by counted poisons: no food steps, no leak; n poisons to flip
    "count": ("B", [dict(fstep=0.0, drift=0.0, V_L=0.0, step=0.5, V_H=0.5 * n - 0.25) for n in (1, 2, 3)]),
    # the same with the count fading (D6's forget)
    "fade": ("B", [dict(fstep=0.0, drift=0.5 / f, V_L=0.0, step=0.5, V_H=0.5 * n - 0.25)
                   for n in (2, 3) for f in (1.5, 5, 15)]),
    # B's tally, food stepping it down, each piece tuned
    "tally": ("B", [dict(fstep=step * a, drift=d, V_H=p["V_L"] + step * n - step / 4)
                    for a in (0.5, 1, 2) for d in (0.0, 0.02, 0.1) for n in (1, 2, 3)]),
    # each eye its own tally of its own drives; which operation; how many net poisons; a retry
    "path": ("path", [dict(reverse=r, theta=t, cost=c, trust=w, tau=tau)
                      for r in (0, 1) for t in (0.5, 1.5, 2.5) for c in (1, 2) for w in (1, 3)
                      for tau in (0, 30)]),
}
for name in sys.argv[1:] or GRIDS:
    arm, grid = GRIDS[name]
    res = []
    for g in grid:
        L = lives(arm, dict(p, **g), spread, range(0, 64))
        s = summary(L)
        res.append((s["efficiency"], s["gain"], s["last"], s["stranded"], g))
    res.sort(key=lambda r: -r[0])
    print(name, flush=True)
    for r in res[:5]:
        print(f"  eff {r[0]:.2f} gain {r[1]:.2f} last {r[2]:.2f} stranded {r[3]:.0%} {r[4]}", flush=True)

"""longbody.py: B with extremum seeking on lopsided bodies, lived 300 s; each 100 s window judged, to see whether the
seeker gets there given time (seeds 0-63 x 2, tolerances)."""
import sys, json
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from concurrent.futures import ProcessPoolExecutor
import cmodel4
from discrete.poison import show
D = "/home/pilgrim/git/simple-learner/lab/m2/"
B = {**cmodel4.NOMINAL, **json.load(open(D + "B.json"))}


def one(job):
    from creature import Life
    from discrete.bodies import THRUSTERS, draw, vary
    from minimal.spec import Lived, SPAN, thirds
    p, seed, poison = job
    q = cmodel4.drawn({**B, **p}, seed)
    lf = Life(seed, poison, brain=lambda s: cmodel4.Model(s, **{k: v for k, v in q.items() if k not in ("oracle",)}))
    f = draw(seed, THRUSTERS); vary(lf, f)
    if p.get("oracle"):
        thr = {m: t for t, m in lf.motor.items()}
        k0, k1 = f[thr[0]], f[thr[1]]
        lf.brain.p["g0"], lf.brain.p["g1"] = (k1 / k0) ** 0.5, (k0 / k1) ** 0.5
    out = []
    while lf.t < 30000:
        lf.step()
    for w in range(3):
        a, b = w * 10000, (w + 1) * 10000
        meals = [(t - a, c) for t, c in lf.meals if a <= t < b]
        l = Lived(thirds(meals, 0, 10000, poison))
        l.power, l.firings = 9e-9, SPAN * sum(1 for t, _ in lf.firings if a <= t < b) / 100.0
        out.append(l)
    return out


if __name__ == "__main__":
    from minimal.spec import summary
    with ProcessPoolExecutor(4) as ex:
        for a in ("adapt=0", "adapt=0.03,wob=0.15,base=3", "adapt=0.01,wob=0.15,base=3", "oracle=1"):
            p = {k: float(v) for k, v in (x.split("=") for x in a.split(","))}
            R = list(ex.map(one, [(p, s, c) for s in range(64) for c in ("red", "blue")]))
            for w in range(3):
                print(show(f"{a} window {w + 1}", summary([r[w] for r in R])), flush=True)

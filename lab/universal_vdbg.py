"""universal_vdbg.py: which model of the bank each life follows, and when (lab/universal_v.py; discrete/NOTEBOOK.md, D29).
    python lab/universal_vdbg.py SETTINGS.json WORLD[,WORLD] [secs] [k=v ...]"""
import json
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from creature import Life
import table as T
import universal as X
import universal_v as UV


def one(job):
    w, kw, seed, first, secs = job
    q = T.numbers(seed, kw)
    R = T.WORLDS[w](first)
    lf = Life(seed, first, brain=lambda s: UV.V(s, q))
    b = lf.brain
    R.setup(lf, seed)
    if hasattr(R, "taste"):
        inner = b.taste
        b.taste = lambda v, at: inner(R.taste(v), at)
    done, share, sound = 0, np.zeros(len(b.bank)), 0
    tastes = [0, 0]
    wrap = b.taste

    def counted(v, at):
        tastes[0] += 1
        tastes[1] += b.vouched()
        wrap(v, at)
    b.taste = counted
    while lf.t < int(secs / T.TICK):
        t = lf.t * T.TICK
        lf.poison, R.now = R.poison(t), t
        R.tick(lf, t)
        lf.step()
        while done < len(lf.meals):
            R.ate(lf.meals[done][1])
            done += 1
        share[b.act] += 1
    return dict(share=share / share.sum(), picks=b.picks, E=[m["E"] for m in b.bank], names=[f"{m['n']}/{m['trust']}" for m in b.bank], on=b.on_at, tastes=tastes, est=b.est, pausing=b.pausing)


if __name__ == "__main__":
    kw = json.load(open(sys.argv[1]))
    secs = float(sys.argv[3]) if len(sys.argv) > 3 else 100.0
    kw.update(X.parse(sys.argv[4:]))
    for w in sys.argv[2].split(","):
        with ProcessPoolExecutor(8) as ex:
            L = list(ex.map(one, [(w, kw, s, c, secs) for s in list(T.TRAIN) + list(UV.VALID) for c in T.COL]))
        names = L[0]["names"]
        sh = np.mean([l["share"] for l in L], 0)
        first = [l["picks"][0][0] for l in L if l["picks"]]
        print(f"== {w} {secs:.0f} s: share of time by model (n/trust): " + " ".join(f"{n}:{v:.2f}" for n, v in zip(names, sh) if v > .01), flush=True)
        print(f"   first pick median {np.median(first) if first else -1:.0f} s, in {len(first) / len(L):.2f} of lives; picks a life {np.mean([len(l['picks']) for l in L]):.1f}; tastes {np.mean([l['tastes'][0] for l in L]):.0f}, vouched {np.mean([l['tastes'][1] for l in L]):.0f}; E mean " + " ".join(f"{n}:{v:.1f}" for n, v in zip(names, np.mean([l["E"] for l in L], 0))), flush=True)
        on = [l["on"][0] for l in L if l["on"]]
        print(f"   first pause median {np.median(on) if on else -1:.0f} s in {len(on) / len(L):.2f} of lives, pausing at end {np.mean([l['pausing'] for l in L]):.2f}, est {np.median([l['est'] for l in L]):.2f}", flush=True)

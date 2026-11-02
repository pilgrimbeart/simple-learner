"""trace_cmp.py: closed-loop statistics of circuit B's traced ngspice lives (v/trace_*.json) against the fast
model's lives of the same seeds with each seed's own numbers (benchH/)."""
import sys, json, glob, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import cmodel4
from predseed import numbers
from units import TICK
D = "/home/pilgrim/git/simple-learner/lab/"
LONE = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0


def model_life(seed, poison, seconds=100.0):
    from creature import Life
    p = numbers(json.loads(open(D + f"benchH/{seed}.json").read())); p["lone"] = LONE
    q = {k: v for k, v in {**cmodel4.NOMINAL, **p}.items() if k not in ("vary", "body", "oracle")}
    lf = Life(seed, poison, brain=lambda s: cmodel4.Model(s, **q))
    m, seen, mode = lf.brain, [], []
    while lf.t < int(round(seconds / TICK)):
        seen.append(sum(lf.body.sees().values()))
        lf.step()
        drv = m.t - m.last_drive < m.p["hold"]
        mode.append("D" if drv else "R" if m.t - m.last_food > m.p["bored"] else "S")
    return dict(meals=lf.meals, fired=lf.firings, seen=seen, mode=mode)


def spice_life(f):
    r = json.load(open(f))
    r["mode"] = ["D" if dn < 0.9 else "R" if run > 0.9 else "S" for dn, run, q, dq in r["trace"]]
    return r


def stats(r, poison):
    mode = np.array(r["mode"]); n = len(mode)
    seen = np.array(r["seen"][:n]) > 0
    fired = np.zeros((n, 2))
    for t, f in r["fired"]:
        if t < n:
            fired[t, 0 if f == "left" else 1] += 1
    out = {}
    for k in "DSR":
        w = mode == k
        out[f"time {k}"] = w.mean()
        out[f"fire/s {k}"] = fired[w].sum() / max(w.sum() * TICK, 1e-9)
    d = (mode == "D").astype(int)
    starts, ends = np.flatnonzero(np.diff(d) == 1) + 1, np.flatnonzero(np.diff(d) == -1) + 1
    ends = ends[ends > starts[0]] if len(starts) else ends
    L = [(e - s) * TICK for s, e in zip(starts, ends)]
    out["drives/10s"] = len(starts) / (n * TICK) * 10
    out["drive len"] = np.mean(L) if L else 0
    meals = [t for t, c in r["meals"]]
    food = [t for t, c in r["meals"] if c != poison]
    out["food"] = len(food); out["poison"] = len(meals) - len(food)
    out["seen frac"] = seen.mean()
    out["meals in drive"] = np.mean([mode[min(t, n - 1)] == "D" or mode[max(t - 1, 0)] == "D" for t in meals]) if meals else 0
    return out


if __name__ == "__main__":
    rows = {}
    for f in sorted(glob.glob(D + "v/trace_*.json")):
        _, seed, poison = f[:-5].rsplit("/", 1)[1].split("_")
        rows.setdefault("spice", []).append(stats(spice_life(f), poison))
        rows.setdefault("model", []).append(stats(model_life(int(seed), poison), poison))
    keys = rows["spice"][0].keys()
    print(f"{'':16s}{'spice':>10s}{'model':>10s}")
    for k in keys:
        print(f"{k:16s}{np.mean([r[k] for r in rows['spice']]):10.3f}{np.mean([r[k] for r in rows['model']]):10.3f}")

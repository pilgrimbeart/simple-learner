"""count_purity.py: on the opened satiety ladder, how well does each per-colour meal count (the leaky averages "c0", "c1", read 0 to 4+)
tell the world's poison colour at the moment of each taste, and which streams the brain trusts? (2026-11-15, after S3.)
    ACOUNT=1 .venv/bin/python lab/count_purity.py RUNG SEED0 N"""
import json
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor

sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import stage3_random as R
import teach as T
from stage2_lang import arms as S


def live(lf, seconds=100.0):
    ticks = int(round(seconds / lf.dt))
    b = lf.brain
    seen = defaultdict(lambda: defaultdict(Counter))
    nm = 0
    while lf.t < ticks:
        k0 = len(lf.scored)
        lf.step()
        if len(lf.scored) > k0 and lf.t * lf.dt > seconds / 3:
            nm += 1
            for c in b.aclk:
                if str(c["e"]).startswith("c"):
                    r = c["r"] * __import__("math").exp(-(b.t - c["tr"]) / c["T"])
                    seen[(c["e"], round(c["T"], 1))][min(int(round(r * c["T"])), 4)][lf.told_now] += 1
    top = sorted(((getattr(N, "w", 1.0), N.kind) for N in b.nets), reverse=True)[:4]
    out = {}
    for key, v in seen.items():
        tot = sum(sum(x.values()) for x in v.values())
        out[key] = round(sum(max(x.values()) for x in v.values()) / tot, 2)
    base = Counter()
    for v in list(seen.values())[:1]:
        for x in v.values():
            base.update(x)
    raise StopIteration((lf.v_tau if hasattr(lf, "v_tau") else None, out, round(max(base.values()) / sum(base.values()), 2), [k for _, k in top], nm))


def one(j):
    S.live = live
    try:
        T.job(j)
    except StopIteration as e:
        return e.value


if __name__ == "__main__":
    n, s0, k = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    d = json.load(open("/home/pilgrim/git/simple-learner/lab/sealed/heldout_ladder2.json"))
    r = next(x for x in d["rungs"] if x["size"] == n)
    jobs = [(r["text"], "net10kc60SA", 2240, s, "red", float(r["seconds"])) for s in range(s0, s0 + k)]
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        for j, (tau, out, base, top, nm) in zip(jobs, ex.map(one, jobs)):
            print(f"seed {j[3]}: recovery {tau}; meals {nm}; poison colour's base rate {base}; purity by (count line, its time constant): {out}; trusted {top}")

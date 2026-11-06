"""stage2_run.py: lives per world per arm: the runner (it refuses stage-5 worlds as results), statistics paired over seeds (a seed's two lives together), per-world sigma and cost. Development, hand-picked: engine proving, not stage 3."""
import pickle
import sys
import time
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from minimal.spec import COST, spent, efficiency
from stage2_lang import arms as S, worlds as WW

OUT = "/home/pilgrim/nca-scratch-backup/stage2/"


def guard(name):
    w = S.world_of(WW.W[name]["text"], name)
    if w.tag() == 5 or w.stage5():
        raise ValueError(f"{name} is a stage-5 world: {w.stage5() or 'marked'}. Not run as a result.")
    return w


def judged(name, arm, seeds, kw=None, seconds=100.0, ex=None):
    guard(name)
    jobs = [(WW.W[name]["text"], arm, kw or {}, s, c, seconds) for s in seeds for c in S.COL]
    return list(ex.map(S.one, jobs, chunksize=4)) if ex else [S.one(j) for j in jobs]


def gs(L):
    return np.array([sum(a - COST * b for a, b, _ in l) for l in L], dtype=float), np.array([spent(l) for l in L], dtype=float)


def resample(npairs, boot=2000, seed=0):
    r = np.random.default_rng(seed)
    k = r.integers(0, npairs, (boot, npairs))
    return np.concatenate((2 * k, 2 * k + 1), axis=1)


def ci_eff(L, boot=2000):
    g, s = gs(L)
    I = resample(len(g) // 2, boot)
    v = g[I].sum(1) / s[I].sum(1)
    return g.sum() / s.sum(), np.percentile(v, 2.5), np.percentile(v, 97.5)


def pdiff(A, B, boot=2000):
    ga, sa = gs(A)
    gb, sb = gs(B)
    I = resample(len(ga) // 2, boot)
    v = ga[I].sum(1) / sa[I].sum(1) - gb[I].sum(1) / sb[I].sum(1)
    return ga.sum() / sa.sum() - gb.sum() / sb.sum(), np.percentile(v, 2.5), np.percentile(v, 97.5)


def sigma(L, boot=2000):
    """A pair's sigma for efficiency: the bootstrap se of the ratio times sqrt(pairs)."""
    g, s = gs(L)
    n = len(g) // 2
    I = resample(n, boot)
    v = g[I].sum(1) / s[I].sum(1)
    return float(np.std(v) * np.sqrt(n))


def sigma_d(A, B, boot=2000):
    """The same for a paired difference."""
    ga, sa = gs(A)
    gb, sb = gs(B)
    n = len(ga) // 2
    I = resample(n, boot)
    v = ga[I].sum(1) / sa[I].sum(1) - gb[I].sum(1) / sb[I].sum(1)
    return float(np.std(v) * np.sqrt(n))


def timed_one(job):
    t0 = time.perf_counter()
    l = S.one(job)
    l.cpu = time.perf_counter() - t0
    return l


ARMS = (("base", "circuit", {}), ("bank", "bank", {}), ("told", "vtold", {}))
SEEDS = range(63200, 63250)


def main():
    """Every world but stage 5's, at 50 pairs: base, bank, told, told with a pause where stated, best model from birth where a model applies. Saved. Development, hand-picked; engine proving, not stage 3."""
    res, cost = {}, {}
    t00 = time.time()
    names = [n for n in WW.W if S.world_of(WW.W[n]["text"]).tag() != 5]
    with ProcessPoolExecutor(7) as ex:
        for n in names:
            w = guard(n)
            arms = list(ARMS)
            if "told_wait" in w.fn:
                arms.append(("toldwait", "vtoldw", {}))
            if "model" in w.meta and w.meta["model"][0]:
                arms.append(("model", "fix", {"fix": float(w.meta["model"][0])}))
            arms.append(("default", "fix", {"fix": 0.0}))
            res[n] = {}
            t0 = time.time()
            for label, arm, kw in arms:
                jobs = [(WW.W[n]["text"], arm, kw, s, c, 100.0) for s in SEEDS for c in S.COL]
                ta = time.time()
                res[n][label] = list(ex.map(timed_one, jobs, chunksize=4))
                cost[n, label] = (time.time() - ta, float(np.mean([l.cpu for l in res[n][label]])))
            print(f"{n} {time.time() - t0:.0f} s; {time.time() - t00:.0f} s in all", flush=True)
            for L in res[n].values():
                for l in L:
                    l.rows = None
            with open(OUT + "lives_partial.pkl", "wb") as f:
                pickle.dump((res, cost), f)
    with open(OUT + "lives.pkl", "wb") as f:
        pickle.dump((res, cost), f)
    print("done", time.time() - t00, flush=True)


def table(path=OUT + "lives.pkl", lp=OUT + "labels.pkl"):
    from stage2_lang.lang import World
    res, cost = pickle.load(open(path, "rb"))
    labels = pickle.load(open(lp, "rb"))
    print("== efficiency, 63200-63249 x 2, 50 pairs, 95% over seed pairs. Development, hand-picked: engine proving, not stage 3. x = (bank - max(base, 0)) / (told - max(base, 0)), told with its pause where stated. Pass here: told only, x > .5, with x > .25 beside it; no reference, that's stage 2b's.", flush=True)
    print(f"{'world':18s} {'cl':>3s} {'base':>18s} {'bank':>18s} {'told':>18s} {'model':>18s} {'bank-base':>20s} {'x[95%]':>20s} pass | sigma base bank d  pairs for se(x)=.1", flush=True)
    rows = []
    for n, R in res.items():
        lab = labels[n]
        tk = "toldwait" if "toldwait" in R else "told"
        b, k, tl = R["base"], R["bank"], R[tk]
        s = [ci_eff(x) for x in (b, k, tl)]
        d = pdiff(k, b)
        # x with its interval: bootstrap of pairs jointly
        gb, sb = gs(b)
        gk, sk = gs(k)
        gt, st = gs(tl)
        I = resample(len(gb) // 2)
        bb, kb, tb = gb[I].sum(1) / sb[I].sum(1), gk[I].sum(1) / sk[I].sum(1), gt[I].sum(1) / st[I].sum(1)
        floor = np.maximum(bb, 0)
        with np.errstate(divide="ignore", invalid="ignore"):
            xb = (kb - floor) / (tb - floor)
        f0 = max(s[0][0], 0)
        gap = s[2][0] - f0
        x = (s[1][0] - f0) / gap if gap > 0 else float("nan")
        ok = np.isfinite(xb)
        xci = np.percentile(xb[ok], [2.5, 97.5]) if ok.any() else (float("nan"), float("nan"))
        se_x = float(np.std(xb[ok])) if ok.any() else float("nan")
        pairs_x = 50 * (se_x / 0.1) ** 2
        sg = (sigma(b), sigma(k), sigma_d(k, b))
        m = ci_eff(R["model"]) if "model" in R else None
        fmt = lambda c: f"{c[0]:+.2f}[{c[1]:+.2f},{c[2]:+.2f}]"
        print(f"{n:18s} {lab['cls'][0]:>3s} {fmt(s[0]):>18s} {fmt(s[1]):>18s} {fmt(s[2]):>18s} {(fmt(m) if m else '-'):>18s} {fmt(d):>20s} {x:+.2f}[{xci[0]:+.2f},{xci[1]:+.2f}] {'pass' if x > .5 else ('>.25' if x > .25 else 'no'):4s} | {sg[0]:.2f} {sg[1]:.2f} {sg[2]:.2f}  {pairs_x:.0f}", flush=True)
        rows.append(dict(name=n, cls=lab["cls"], base=s[0][0], bank=s[1][0], told=s[2][0], gap=gap, x=x, xci=xci, se_x=se_x, sg=sg, d=d, pairs_x=pairs_x, group=S.world_of(WW.W[n]["text"]).meta.get("group", [""])[0]))
    return rows, cost, res


if __name__ == "__main__":
    if sys.argv[1:] == ["run"]:
        main()

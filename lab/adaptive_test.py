"""adaptive_test.py: the adaptive wobble (lab/adaptive.py; predictions lab/v/adaptive_predictions.md, written first) against the old bank
and base. Main session, 2026-11-08.
  plain10k  plain, 10,000 s, the scaling test's seeds (81400-81409 x red/blue): paired with its base and written-bank lives
  short     at 100 s on stage 3's seeds (80100-80159 x red/blue): plain, the 55 worlds with something to learn and R2's nothing-to-learn
            worlds, paired with stage 3's own base, bank and told lives (lab/stage3_random.py main)

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/adaptive_test.py plain10k|short|analyse"""
import sys
import time
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import stage3_random as R
import stage3_more as M
import adaptive as A


def job(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    text, secs, seed, first, *kw = j
    lf = A.make(S.world_of(text), seed, first, dict(kw[0]) if kw else None)
    l = S.live(lf, secs)
    g = [a - COST * b for a, b, _ in l]
    b = lf.brain
    return (sum(g), spent(l), g[2], l[2][2] / sum(t for _, _, t in l), b.alog, b.rearms)


def plain10k(kw=()):
    import stageR_scale as X
    I = R.boot(len(X.SEEDS), 20000)
    D = R._load(X.KEY)["plain"]
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.00125, False)) as ex:
        L = list(ex.map(job, [(R.PLAIN, 10000.0, s, c, kw) for s in X.SEEDS for c in R.COL]))
    R._save("adaptive_plain10k" + "".join(f"_{k}{v}" for k, v in kw), {"plain": L})
    print("switches:", dict(kw))
    b, k, a = (M.boot_eff(x, I, True) for x in (D["base"], D["written"], [y[:4] for y in L]))
    for name, e in (("old bank", k), ("adaptive", a)):
        lo, hi = np.percentile(e[1] - b[1], [2.5, 97.5])
        print(f"plain 10,000 s, last third: {name} {e[0]:.3f}, minus base {e[0] - b[0]:+.3f} [{lo:+.3f},{hi:+.3f}]")
    for t0 in range(0, 10001, 1000):
        v = [min(x[4], key=lambda e: abs(e[0] - t0))[1] for x in L if x[4]]
        print(f"  t {t0:5d} s: wobble size a, mean over lives {np.mean(v):.2f} (max {np.max(v):.2f})")
    print("  re-arms per life:", [len(x[5]) for x in L])


def short():
    import stageR2 as R2
    W, learn, nothing = R2.worlds()
    done = R._load("adaptive_short")
    t0 = time.time()
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.00125, False)) as ex:
        for n in nothing + learn:
            if n in done:
                continue
            text = R.PLAIN if n == "plain" else W[n][0]
            done[n] = list(ex.map(job, [(text, 100.0, s, c) for s in R.SEEDS for c in R.COL], chunksize=2))
            R._save("adaptive_short", done)
            print(f"short {n} ({time.time() - t0:.0f} s)", flush=True)


def analyse():
    import stageR2 as R2
    W, learn, nothing = R2.worlds()
    D, main, ref = R._load("adaptive_short"), R._load("main"), R._load("ref")
    I = R.boot(len(R.SEEDS), 20000)
    what = lambda n: "plain" if n == "plain" else "; ".join(f"{a} {b} {c}" for a, b, c, _ in W[n][1])
    print("== at 100 s, 60 pairs: the adaptive bank minus the old bank, and each minus base (95%)")
    worse = []
    for n in nothing + learn:
        if n not in D:
            continue
        b, k = (R.eff([x[:2] for x in main[n][a]], I) for a in ("base", "bank"))
        a = R.eff([x[:2] for x in D[n]], I)
        lo, hi = np.percentile(a[1] - k[1], [2.5, 97.5])
        flag = "WORSE" if hi < -0.1 else "worse" if hi < 0 else "better" if lo > 0 else ""
        if hi < 0:
            worse.append(n)
        print(f"  {n:5s} {'nothing' if n in nothing else 'learn  '} adaptive - old {a[0] - k[0]:+.3f} [{lo:+.3f},{hi:+.3f}] {flag:6s} "
              f"old - base {k[0] - b[0]:+.3f}  adaptive - base {a[0] - b[0]:+.3f} | {what(n)}")
    tally = {"old": {"pass": 0, "fail": 0, "unclear": 0}, "adaptive": {"pass": 0, "fail": 0, "unclear": 0}}
    for n in learn:
        if n not in D:
            continue
        e = {x: R.eff([y[:2] for y in main[n][x]], I) for x in ("base", "bank", "told")}
        fl0, fl = max(e["base"][0], 0.0), np.maximum(e["base"][1], 0.0)
        g0, g = e["told"][0] - fl0, e["told"][1] - fl
        r0 = (R.eff(ref[n], I)[0] - fl0) / g0 if n in ref else np.nan
        bar = max(0.5 * r0 if np.isfinite(r0) else 0.0, 0.25)
        for name, k in (("old", e["bank"]), ("adaptive", R.eff([x[:2] for x in D[n]], I))):
            with np.errstate(divide="ignore", invalid="ignore"):
                x = (k[1] - fl) / g
            lo, hi = np.percentile(x[np.isfinite(x)], [2.5, 97.5])
            tally[name]["pass" if lo > bar else "fail" if hi < bar else "unclear"] += 1
    print("  coverage:", tally, "; surely worse than the old bank in:", worse)


if __name__ == "__main__":
    if sys.argv[1] == "plain10k":
        plain10k(tuple((k, float(v)) for k, v in (a.split("=") for a in sys.argv[2:])))
    else:
        {"short": short, "analyse": analyse}[sys.argv[1]]()

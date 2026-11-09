"""stageR_scale_cure.py: stage R's 10,000 s scaling test (lab/stageR_scale.py) with the balance learner cured: the written bank and K1000+
with the sized learner (lab/rprop.py, the version given: v7 or v8) in place of the old learner and its fixed gate. The scaling test's
verdicts were confounded by the old learner's long-life wear-down (plain -.37 to -.40 for every bank arm); this asks whether, with it
cured, any longer life buys what 1000 s couldn't. The same worlds, seeds (81400-81409) and judging; base, told and the uncured arms are the
scaling test's own lives (its pickle, Rscale), so every comparison is paired. Main session, night of 2026-11-08.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stageR_scale_cure.py run v7|v8 | analyse"""
import sys
import time
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import stage3_random as R
import rivals as RV
import adaptive as A
import rprop as RP
import stageR_scale as SC

KEY = "Rscale_cure"
CURE = {"v7": {"n_max": 10 ** 9, "Dmax": 0.3, "curv": 1, "sd_min": 0.005},
        "v8": {"n_max": 10 ** 9, "Dmax": 0.3, "curv": 1, "sd_min": 0.005, "seq": 1}}


class SZplus(RP.SZ):
    """The sized learner's bank with K random rivals plus "it changes often", as stageR_scale.RVplus."""
    def __init__(self, seed, p):
        K = p["rivals"][1]
        super().__init__(seed, {**p, "rivals": lambda r, src: [(RV.Const(), 0)] + RV.random_rivals(K)(r, src)})


def job(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    text, arm, cure, seed, first = j
    w = S.world_of(text)
    if arm == "writtenS":
        lf = A.make(w, seed, first, dict(CURE[cure]), cls=RP.SZ)
    else:                                                       # K1000+S
        lf = A.make(w, seed, first, {"rivals": ("random+", 1000), **RV.occam(1001), **CURE[cure]}, cls=SZplus)
    l = S.live(lf, SC.SECS)
    g = [a - COST * b for a, b, _ in l]
    return (sum(g), spent(l), g[2], l[2][2] / sum(t for _, _, t in l))


def run(cure):
    W, _, _ = R.worlds()
    done = R._load(KEY)
    done["cure"] = cure
    t0 = time.time()
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.00125, False)) as ex:
        for n in SC.WORLDS:
            text = R.PLAIN if n == "plain" else W[n][0]
            d = done.setdefault(n, {})
            for a in ("writtenS", "K1000+S"):
                if a in d:
                    continue
                d[a] = list(ex.map(job, [(text, a, cure, s, c) for s in SC.SEEDS for c in R.COL], chunksize=1))
                R._save(KEY, done)
                print(f"cure {n} {a} ({time.time() - t0:.0f} s)", flush=True)


def analyse():
    import stage3_more as M
    W, _, _ = R.worlds()
    D0, D1, LR = R._load(SC.KEY), R._load(KEY), R._load("firm_longref")
    print(f"cure: {D1.get('cure')}")
    I = R.boot(len(SC.SEEDS), 20000)
    I1 = R.boot(len(M.LONG_SEEDS), 20000)
    names = ["written", "writtenS", "K1000+", "K1000+S"]
    tally = {a: {"pass": 0, "fail": 0, "unclear": 0} for a in names}
    print(f"== {SC.SECS:.0f} s lives, last third, {len(SC.SEEDS)} pairs: x (95%) against max(.5 r, .25); S: with the sized learner")
    for n in SC.WORLDS:
        if n == "plain" or n not in D1:
            continue
        L = {**D0[n], **D1[n]}
        e = {a: M.boot_eff(L[a], I, True) for a in L}
        fl0, fl = max(e["base"][0], 0), np.maximum(e["base"][1], 0)
        g0, g = e["told"][0] - fl0, e["told"][1] - fl
        if not (np.percentile(g, 2.5) > 0 and g0 >= 0.1):
            continue
        r0 = np.nan
        if n in LR:
            Lg = R._load("more_long")
            b1, t1 = M.boot_eff(Lg[n]["base"], I1, True)[0], M.boot_eff(Lg[n]["told"], I1, True)[0]
            r0 = (M.boot_eff(LR[n], I1, True)[0] - max(b1, 0)) / (t1 - max(b1, 0))
        bar = max(0.5 * r0 if np.isfinite(r0) else 0.0, 0.25)
        out = []
        for a in names:
            if a not in e:
                continue
            with np.errstate(divide="ignore", invalid="ignore"):
                x0, x = (e[a][0] - fl0) / g0, (e[a][1] - fl) / g
            lo, hi = np.percentile(x[np.isfinite(x)], [2.5, 97.5])
            v = "pass" if lo > bar else "fail" if hi < bar else "unclear"
            tally[a][v] += 1
            out.append(f"{a} {x0:+.2f}[{lo:+.2f},{hi:+.2f}]{v[0]}")
        for a, b in (("writtenS", "written"), ("K1000+S", "K1000+")):
            if a in e:
                lo, hi = np.percentile(e[a][1] - e[b][1], [2.5, 97.5])
                out.append(f"{a}-{b} {e[a][0] - e[b][0]:+.2f}[{lo:+.2f},{hi:+.2f}]")
        what = "; ".join(f"{a} {b} {c}" for a, b, c, _ in W[n][1])
        print(f"  {n:5s} gap {g0:+.2f} bar {bar:.2f} | " + "  ".join(out) + f" | {what}", flush=True)
    for a in names:
        t = tally[a]
        if sum(t.values()):
            print(f"  {a:9s} sure pass {t['pass']}, sure fail {t['fail']}, can't tell {t['unclear']} of {sum(t.values())}")
    if "plain" in D1:
        print("\n== plain (nothing to learn): each arm minus base, last third (95%); harm if surely below -.1")
        L = {**D0["plain"], **D1["plain"]}
        b = M.boot_eff(L["base"], I, True)
        for a in names:
            if a in L:
                k = M.boot_eff(L[a], I, True)
                lo, hi = np.percentile(k[1] - b[1], [2.5, 97.5])
                print(f"  {a:9s} {k[0] - b[0]:+.3f} [{lo:+.3f},{hi:+.3f}]{'  HARM' if hi < -0.1 else ''}")


if __name__ == "__main__":
    run(sys.argv[2]) if sys.argv[1] == "run" else analyse()

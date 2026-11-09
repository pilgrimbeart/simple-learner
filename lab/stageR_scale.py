"""stageR_scale.py: stage R's scaling test (PROGRAMME.md; the user, 2026-11-07: long lives may be our equivalent of deep learning's scale).
Main session, 2026-11-07. The rule and predictions 9-13 are in lab/v/stageR_predictions.md, written before any of these lives.

10,000 s lives (AGENTS.md allows them for this test), 1.25 ms, 10 pairs (seeds 81400-81409 x red/blue: fresh development seeds), judged
on the last third against the told arm, as the 1000 s lives are. Ten pairs, not twenty: the last third is ten times longer than at 1000 s.
  worlds  plain first (doing no harm), then the timing worlds of stage 3's 1000 s lives that kept a gap there: the swaps, the alternates,
          the satieties (13), in that order, so a run cut short still answers the main question
  arms    base, told, the written bank, K = 10, 100, 1000 random rivals with the Occam bar (lab/rivals.py, R2's rule unchanged), and on
          plain also K = 1000 with the written bar
No reference arm (a 10,000 s reference costs as much again): the bar is max(.5 r, .25) with r from the 1000 s reference (lab/stage3_firm.py
longref), which can only be lower than r at 10,000 s; noted in the output.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stageR_scale.py run|analyse"""
import sys
import time
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import stage3_random as R
import rivals as RV

SECS = 10000.0
SEEDS = range(81400, 81410)
KS = (10, 100, 1000)
WORLDS = ["plain",
          "g227", "g361", "g335", "g380", "g397", "g328", "g226",      # swaps (fixed or in bursts)
          "g245", "g261",                                              # alternates
          "g352", "g174", "g244", "g192"]                              # satieties
KEY = "Rscale"


class RVplus(RV.RV):
    """K random rivals plus the written bank's "it changes often" (the default's table with trust 0), added after R2 at 100 s showed the
    random rule can't draw it (lab/stageR2_trace.py). It is listed first and takes nothing from the rivals' stream, so the K random rivals
    are K1000's own: the comparison with K1000 is paired."""
    def __init__(self, seed, p):
        K = p["rivals"][1]
        super().__init__(seed, {**p, "rivals": lambda r, src: [(RV.Const(), 0)] + RV.random_rivals(K)(r, src)})


def arms_for(n):
    a = [("base", "circuit"), ("told", None), ("written", "bank")] + [(f"K{K}", {"rivals": ("random", K), **RV.occam(K)}) for K in KS]
    a.append(("K1000+", {"rivals": ("random+", 1000), **RV.occam(1001)}))
    if n == "plain":
        a = [x for x in a if x[0] != "told"] + [("K1000fixed", {"rivals": ("random", 1000)})]
    return a


def job(j):
    """(text, arm, seed, first) -> (gain, spent, last third's gain, last third's share of the time), as lab/stage3_more.py's lives."""
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    text, arm, seed, first = j
    w = S.world_of(text)
    if isinstance(arm, dict):
        lf = RV.make(w, seed, first, arm, cls=RVplus if arm["rivals"][0] == "random+" else RV.RV)
    else:
        lf = S.make(w, arm, seed, first)
    l = S.live(lf, SECS)
    g = [a - COST * b for a, b, _ in l]
    return (sum(g), spent(l), g[2], l[2][2] / sum(t for _, _, t in l))


def run():
    W, _, _ = R.worlds()
    done = R._load(KEY)
    t0 = time.time()
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.00125, False)) as ex:
        for n in WORLDS:
            text = R.PLAIN if n == "plain" else W[n][0]
            d = done.setdefault(n, {})
            for a, arm in arms_for(n):
                if a in d:
                    continue
                arm = R.told_arm(text) if a == "told" else arm
                d[a] = list(ex.map(job, [(text, arm, s, c) for s in SEEDS for c in R.COL], chunksize=1))
                R._save(KEY, done)
                print(f"scale {n} {a} ({time.time() - t0:.0f} s)", flush=True)


def analyse():
    import stage3_more as M
    W, _, _ = R.worlds()
    D, LR = R._load(KEY), R._load("firm_longref")
    I = R.boot(len(SEEDS), 20000)
    I1 = R.boot(len(M.LONG_SEEDS), 20000)
    names = ["written"] + [f"K{K}" for K in KS] + ["K1000+"]
    print(f"== {SECS:.0f} s lives, last third, {len(SEEDS)} pairs: x (95%) for the written bank and each K against max(.5 r, .25), "
          "r from the 1000 s reference")
    tally = {a: {"pass": 0, "fail": 0, "unclear": 0} for a in names}
    for n in WORLDS:
        if n == "plain" or n not in D or "told" not in D[n]:
            continue
        e = {a: M.boot_eff(D[n][a], I, True) for a in D[n]}
        fl0, fl = max(e["base"][0], 0), np.maximum(e["base"][1], 0)
        g0, g = e["told"][0] - fl0, e["told"][1] - fl
        what = "; ".join(f"{a} {b} {c}" for a, b, c, _ in W[n][1])
        if not (np.percentile(g, 2.5) > 0 and g0 >= 0.1):
            print(f"  {n:5s} nothing to judge (gap {g0:+.2f}) | {what}")
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
        print(f"  {n:5s} gap {g0:+.2f} bar {bar:.2f} | " + "  ".join(out) + f" | {what}")
    for a in names:
        t = tally[a]
        N = sum(t.values())
        if N:
            print(f"  {a:8s} sure pass {t['pass']}, sure fail {t['fail']}, can't tell {t['unclear']} of {N}")
    if "plain" in D:
        print("\n== plain (nothing to learn): each arm minus base, last third (95%); harm if surely below -.1")
        b = M.boot_eff(D["plain"]["base"], I, True)
        for a in names + ["K1000fixed"]:
            if a in D["plain"]:
                k = M.boot_eff(D["plain"][a], I, True)
                lo, hi = np.percentile(k[1] - b[1], [2.5, 97.5])
                print(f"  {a:10s} {k[0] - b[0]:+.3f} [{lo:+.3f},{hi:+.3f}]{'  HARM' if hi < -0.1 else ''}")


if __name__ == "__main__":
    {"run": run, "analyse": analyse}[sys.argv[1]]()

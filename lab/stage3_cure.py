"""stage3_cure.py: stage 3's fresh worlds at 100 s again, the bank with the sized balance learner (lab/rprop.py, the version given) in place
of the old learner and its fixed gate. Does the cure, which wobbles from birth and quiets on its own, cost anything in 100 s lives, and
does it change what the bank learns? Every distinct judged fresh world (lab/stage3_firm.py's distinct), the first pass's 60 pairs (seeds
80100-80159, 1.25 ms), so each life pairs with the first pass's bank, base and told lives (pickle main). Main session, night of 2026-11-08.

  analyse  per world: bankS - bank (95%, paired), and x = (arm - max(base, 0)) / (told - max(base, 0)) for both against the world's bar,
           max(.5 r, .25) with r the first pass's point estimate (rows); tallies for worlds with something to learn and with nothing.
           These are the first pass's 60 pairs only, not the firmed-up verdicts (top-ups, 300 pairs): a paired comparison of the cure.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage3_cure.py run v7|v8 | analyse"""
import sys
import time
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import stage3_random as R
import stage3_more as M
import stage3_firm as F
import adaptive as A
import rprop as RP
from stageR_scale_cure import CURE

KEY = "stage3_cure"


def live(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    from stage2_lang.sim import Refused
    text, cure, seed, first = j
    try:
        l = S.live(A.make(S.world_of(text), seed, first, dict(CURE[cure]), cls=RP.SZ), 100.0)
    except Refused as e:
        return ("refused", str(e)[:200])
    g = [a - COST * b for a, b, _ in l]
    return (sum(g), spent(l), g[2], l[2][2] / sum(t for _, _, t in l))


def run(cure):
    W, names = F.distinct()
    done = R._load(KEY)
    done.setdefault("cure", cure)
    t0 = time.time()
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.00125, False)) as ex:
        for n in names:
            if n in done:
                continue
            done[n] = list(ex.map(live, [(W[n][0], cure, s, c) for s in R.SEEDS for c in R.COL], chunksize=2))
            R._save(KEY, done)
            print(f"cure {n} ({time.time() - t0:.0f} s)", flush=True)


def analyse():
    W, names = F.distinct()
    rows, main, D = R._load("rows"), R._load("main"), R._load(KEY)
    print(f"cure: {D.get('cure')}; worlds run {len([n for n in names if n in D])} of {len(names)}")
    I = R.boot(len(R.SEEDS), 20000)
    T = {k: {"better": 0, "worse": 0, "same": 0, "harm": 0} for k in ("learn", "nothing")}
    V = {k: {"pass": 0, "fail": 0, "unclear": 0} for k in ("bank", "bankS")}
    diffs = {"learn": [], "nothing": []}
    for n in names:
        if n not in D or n not in main:
            continue
        L = {**main[n], "bankS": D[n]}
        if any(x[0] == "refused" for x in L["bankS"]) or any(x[0] == "refused" for x in L["bank"]):
            continue
        e = {a: M.boot_eff(L[a], I) for a in ("base", "bank", "told", "bankS")}
        k = "nothing" if rows[n]["nothing"] else "learn"
        d0, d = e["bankS"][0] - e["bank"][0], e["bankS"][1] - e["bank"][1]
        lo, hi = np.percentile(d, [2.5, 97.5])
        diffs[k].append(d0)
        T[k]["better" if lo > 0 else "worse" if hi < 0 else "same"] += 1
        T[k]["harm"] += int(hi < -0.1)
        row = f"  {n:5s} {k:7s} bankS - bank {d0:+.3f} [{lo:+.3f},{hi:+.3f}]"
        if k == "learn":
            fl0, fl = max(e["base"][0], 0), np.maximum(e["base"][1], 0)
            g0, g = e["told"][0] - fl0, e["told"][1] - fl
            r = rows[n].get("r")
            bar = max(0.5 * r if r is not None and np.isfinite(r) else 0.0, 0.25)
            for a in ("bank", "bankS"):
                with np.errstate(divide="ignore", invalid="ignore"):
                    x0, x = (e[a][0] - fl0) / g0, (e[a][1] - fl) / g
                xl, xh = np.percentile(x[np.isfinite(x)], [2.5, 97.5])
                v = "pass" if xl > bar else "fail" if xh < bar else "unclear"
                V[a][v] += 1
                row += f"   {a} x {x0:+.2f}[{xl:+.2f},{xh:+.2f}]{v[0]}"
        what = "; ".join(f"{a} {b} {c}" for a, b, c, _ in W[n][1])
        print(row + f" | {what}", flush=True)
    for k in T:
        if diffs[k]:
            print(f"{k}: {len(diffs[k])} worlds, bankS - bank mean {np.mean(diffs[k]):+.3f}; surely better {T[k]['better']}, surely worse "
                  f"{T[k]['worse']} (by more than .1: {T[k]['harm']}), can't tell {T[k]['same']}")
    for a in V:
        print(f"  {a:6s} on the worlds with something to learn (60 pairs, the first pass's bar): pass {V[a]['pass']}, fail "
              f"{V[a]['fail']}, can't tell {V[a]['unclear']}")


if __name__ == "__main__":
    run(sys.argv[2]) if sys.argv[1] == "run" else analyse()

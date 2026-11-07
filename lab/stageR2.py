"""stageR2.py: stage R2 (PROGRAMME.md), K rivals drawn at birth from simple parts (lab/rivals.py; the rule and predictions in
lab/v/stageR_predictions.md, written first), on stage 3's fresh worlds. Main session, 2026-11-07.

On the first pass's seeds (80100-80159 x red/blue, 1.25 ms, 100 s), so base, told, the reference and the written bank's lives are stage
3's own (lab/stage3_random.py's main and ref) and every comparison is paired:
  worlds: the 55 fresh worlds with something to learn (first pass and top-up), plain, the six harm worlds, and 20 other nothing-to-learn
  worlds (the first 20 by number); arms: K = 10, 100, 1000 with the Occam bar, and K = 1000 with the written bar (theta 2, Emax 10) on the
  nothing-to-learn worlds, the control for prediction 2.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stageR2.py run|analyse"""
import sys
import time
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import stage3_random as R
import rivals as RV

KS = (10, 100, 1000)
HARM = ("g80", "g118", "g172", "g262", "g322", "g367")


def arms_for(nothing):
    a = [(f"K{K}", {"rivals": ("random", K), **RV.occam(K)}) for K in KS]
    if nothing:
        a.append(("K1000fixed", {"rivals": ("random", 1000)}))
    return a


def worlds():
    """(W, to-learn, nothing-to-learn) among stage 3's distinct fresh worlds, from the first pass and top-up's saved verdicts."""
    import stage3_more as M
    W, fail, unclear, _ = M.chosen()
    rows = R._load("rows")
    _, redo, fresh = R.worlds()
    seen, learn, nothing = {W[n][0] for n in redo}, [], []
    top = R._load("more_topup")
    for n in fresh:
        t = W[n][0]
        if t in seen:
            continue
        seen.add(t)
        v = rows.get(n)
        if not v or v["out"]:
            continue
        if v["nothing"]:
            nothing.append(n)
        elif n in top:
            L = {a: [x[:2] for x in R._load("main")[n][a]] + [x[:2] for x in top[n][a]] for a in ("base", "told")}
            I = R.boot(300)
            b, t_ = R.eff(L["base"], I), R.eff(L["told"], I)
            g0, g = t_[0] - max(b[0], 0), t_[1] - np.maximum(b[1], 0)
            (learn if (np.percentile(g, 2.5) > 0 and g0 >= 0.1) else nothing).append(n)
        else:
            learn.append(n)
    other = [n for n in nothing if n not in HARM][:20]
    return W, learn, ["plain"] + [n for n in HARM if rows[n]["nothing"]] + other     # g80 and g118 are redo draws


def job(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    text, kw, seed, first = j
    lf = RV.make(S.world_of(text), seed, first, kw)
    l = S.live(lf, 100.0)
    picked = sorted({i for _, i in l.picks if i})
    return sum(a - COST * b for a, b, _ in l), spent(l), [(i, lf.brain.bank[i]["ctx"].desc(), lf.brain.bank[i]["trust"]) for i in picked]


def run():
    W, learn, nothing = worlds()
    print(f"to learn {len(learn)}, nothing {len(nothing)}", flush=True)
    done = R._load("R2")
    t0 = time.time()
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.00125, False)) as ex:
        for n in learn + nothing:
            text = R.PLAIN if n == "plain" else W[n][0]
            d = done.setdefault(n, {})
            for a, kw in arms_for(n in nothing):
                if a in d:
                    continue
                d[a] = list(ex.map(job, [(text, kw, s, c) for s in R.SEEDS for c in R.COL], chunksize=2))
                R._save("R2", done)
            print(f"R2 {n} ({time.time() - t0:.0f} s)", flush=True)


def analyse():
    W, learn, nothing = worlds()
    D, main, ref = R._load("R2"), R._load("main"), R._load("ref")
    I = R.boot(len(R.SEEDS), 20000)
    what = lambda n: "plain" if n == "plain" else "; ".join(f"{a} {b} {c}" for a, b, c, _ in W[n][1])
    names = ["written"] + [f"K{K}" for K in KS]
    tally = {a: {"pass": 0, "fail": 0, "unclear": 0} for a in names}
    print("== worlds with something to learn: x (60 pairs, 95%) for the written bank and each K; the bar max(.5 r, .25); "
          "the new minus the written, paired")
    for n in learn:
        if n not in D:
            continue
        e = {a: R.eff([x[:2] for x in main[n][a]], I) for a in ("base", "bank", "told")}
        fl0, fl = max(e["base"][0], 0.0), np.maximum(e["base"][1], 0.0)
        g0, g = e["told"][0] - fl0, e["told"][1] - fl
        r0 = (R.eff(ref[n], I)[0] - fl0) / g0 if n in ref else np.nan
        bar = max(0.5 * r0 if np.isfinite(r0) else 0.0, 0.25)
        out = []
        xs = {}
        for a in names:
            L = [x[:2] for x in main[n]["bank"]] if a == "written" else [x[:2] for x in D[n][a]]
            k = R.eff(L, I)
            with np.errstate(divide="ignore", invalid="ignore"):
                x0, x = (k[0] - fl0) / g0, (k[1] - fl) / g
            xs[a] = x
            lo, hi = np.percentile(x[np.isfinite(x)], [2.5, 97.5])
            v = "pass" if lo > bar else "fail" if hi < bar else "unclear"
            tally[a][v] += 1
            dd = ""
            if a != "written":
                dl, dh = np.percentile((x - xs["written"])[np.isfinite(x - xs["written"])], [2.5, 97.5])
                dd = f" d{'+' if dl > 0 else '-' if dh < 0 else '='}"
            out.append(f"{a} {x0:+.2f}{v[0]}{dd}")
        picks = {}
        for life in D[n]["K100"]:
            for _, desc, tr in life[2]:
                picks[desc] = picks.get(desc, 0) + 1
        top = sorted(picks.items(), key=lambda kv: -kv[1])[:2]
        print(f"  {n:5s} gap {g0:+.2f} bar {bar:.2f} | " + "  ".join(out) + f" | {what(n)} | K100 picks {top}")
    for a in names:
        t = tally[a]
        N = sum(t.values())
        print(f"  {a:8s} sure pass {t['pass']}, sure fail {t['fail']}, can't tell {t['unclear']} of {N}: coverage {t['pass'] / N:.2f} to "
              f"{(t['pass'] + t['unclear']) / N:.2f}")
    print("\n== nothing to learn: each arm minus base (60 pairs, 95%); harm if surely below -.1")
    for n in nothing:
        if n not in D:
            continue
        b = R.eff([x[:2] for x in main[n]["base"]], I)
        row = []
        for a in ["written"] + [f"K{K}" for K in KS] + ["K1000fixed"]:
            L = [x[:2] for x in main[n]["bank"]] if a == "written" else [x[:2] for x in D[n].get(a, [])]
            if not L:
                continue
            k = R.eff(L, I)
            lo, hi = np.percentile(k[1] - b[1], [2.5, 97.5])
            row.append(f"{a} {k[0] - b[0]:+.2f}[{lo:+.2f},{hi:+.2f}]{'H' if hi < -0.1 else ''}")
        print(f"  {n:5s} " + "  ".join(row) + f" | {what(n)}")


def job_long(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    text, kw, seed, first = j
    lf = RV.make(S.world_of(text), seed, first, kw)
    l = S.live(lf, 1000.0)
    g = [a - COST * b for a, b, _ in l]
    return (sum(g), spent(l), g[2], l[2][2] / sum(t for _, _, t in l))      # as lab/stage3_more.py's lives


def run_long():
    """The user's point (2026-11-07): rules about time may need longer lives. K rivals on the 30 worlds of stage 3's 1000 s lives
    (lab/stage3_more.py long: the same seeds 81000-81019, so paired with their base, told, written bank and reference)."""
    import stage3_more as M
    W, _, _ = R.worlds()
    Lg = R._load("more_long")
    done = R._load("R2long")
    t0 = time.time()
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.00125, False)) as ex:
        for n in Lg:
            d = done.setdefault(n, {})
            for a, kw in arms_for(False):
                if a in d:
                    continue
                d[a] = list(ex.map(job_long, [(W[n][0], kw, s, c) for s in M.LONG_SEEDS for c in R.COL], chunksize=1))
                R._save("R2long", done)
            print(f"R2long {n} ({time.time() - t0:.0f} s)", flush=True)


def analyse_long():
    import stage3_more as M
    W, _, _ = R.worlds()
    Lg, LR, D = R._load("more_long"), R._load("firm_longref"), R._load("R2long")
    I = R.boot(len(M.LONG_SEEDS), 20000)
    print("== 1000 s lives, last third, 20 pairs: x for the written bank and each K, against the bar max(.5 r, .25)")
    tally = {}
    for n in Lg:
        if n not in D:
            continue
        b, t = (M.boot_eff(Lg[n][a], I, True) for a in ("base", "told"))
        fl0, fl = max(b[0], 0), np.maximum(b[1], 0)
        g0, g = t[0] - fl0, t[1] - fl
        if not (np.percentile(g, 2.5) > 0 and g0 >= 0.1):
            print(f"  {n:5s} nothing to judge at 1000 s (gap {g0:+.2f})")
            continue
        with np.errstate(divide="ignore", invalid="ignore"):
            r0 = (M.boot_eff(LR[n], I, True)[0] - fl0) / g0 if n in LR else np.nan
        bar = max(0.5 * r0 if np.isfinite(r0) else 0.0, 0.25)
        out = []
        for a in ["written"] + [f"K{K}" for K in KS]:
            k = M.boot_eff(Lg[n]["bank"] if a == "written" else D[n][a], I, True)
            with np.errstate(divide="ignore", invalid="ignore"):
                x0, x = (k[0] - fl0) / g0, (k[1] - fl) / g
            lo, hi = np.percentile(x[np.isfinite(x)], [2.5, 97.5])
            v = "pass" if lo > bar else "fail" if hi < bar else "unclear"
            tally.setdefault(a, {}).setdefault(v, 0)
            tally[a][v] += 1
            out.append(f"{a} {x0:+.2f}[{lo:+.2f},{hi:+.2f}]{v[0]}")
        print(f"  {n:5s} gap {g0:+.2f} bar {bar:.2f} | " + "  ".join(out) + " | " + "; ".join(f"{a} {b_} {c}" for a, b_, c, _ in W[n][1]))
    for a, t in tally.items():
        print(f"  {a:8s} {t}")


if __name__ == "__main__":
    {"run": run, "analyse": analyse, "long": run_long, "analyse_long": analyse_long}[sys.argv[1]]()

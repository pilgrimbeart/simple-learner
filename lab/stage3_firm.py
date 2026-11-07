"""stage3_firm.py: firming up stage 3's coverage, as the independent check found it needed (lab/v/stage3_indep_check.log; main session,
2026-11-07). The worlds are chosen here from the first pass's saved verdicts, before any of these lives ran.

  retest   fresh worlds whose verdict rests on a small gap and was never re-measured: judged nothing to learn at 60 pairs with a gap of
           .07 or more, or a sure verdict with a gap under .2. To 300 pairs as the top-up (base, bank, told, seeds 80500-80739,
           1.25 ms), then the reference at 2.5 ms where the 300 pairs show a gap.
  harm     every other fresh nothing-to-learn world, base and bank to 200 pairs (seeds 80500-80639): doing no harm as PROGRAMME words
           it (the lower bound of bank - base above -.1), not only harm surely shown.
  longref  the reference on the 30 worlds of 1000 s lives (seeds 81000-81019, 2.5 ms), so their verdicts use the full bar.
  final    every fresh world from all its lives (first pass, top-up, these), worlds with identical lives counted once, a 20,000-draw
           bootstrap (so verdicts don't hang on the bootstrap's own noise): coverage, harm, and the 1000 s verdicts.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage3_firm.py retest|harm|longref|final"""
import sys
import time
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import stage3_random as R
import stage3_more as M

RETEST_SEEDS = range(80500, 80740)
HARM_SEEDS = range(80500, 80640)
B = 20000


def distinct():
    """The fresh worlds counted by text (a draw repeating an earlier redo or fresh draw is dropped), judged (not out)."""
    W, redo, fresh = R.worlds()
    rows = R._load("rows")
    seen = {W[n][0] for n in redo}
    out = []
    for n in fresh:
        t = W[n][0]
        if t in seen:
            continue
        seen.add(t)
        if n in rows and not rows[n]["out"]:
            out.append(n)
    return W, out


def chosen():
    W, names = distinct()
    rows = R._load("rows")
    topped = set(R._load("more_topup"))
    retest, harm = [], []
    for n in names:
        if n in topped:
            continue
        v = rows[n]
        if v["nothing"]:
            (retest if v["gap"] >= 0.07 else harm).append(n)
        elif v["gap"] < 0.2:
            bar = max(0.5 * v["r"] if np.isfinite(v["r"]) else 0.0, 0.25)
            lo, hi = v["x_ci"]
            if lo > bar or hi < bar:
                retest.append(n)
    return W, retest, harm


def lives(n, arm, *sets):
    """All of a world's lives for an arm, pairs kept together, from the saved sets in order; [] if any set lacks the arm."""
    L = []
    for S in sets:
        if n in S and arm in S[n]:
            L += [x[:2] for x in S[n][arm] if x[0] != "refused"]
    return L


def final():
    W, names = distinct()
    rows = R._load("rows")
    main, ref, top, firm = R._load("main"), R._load("ref"), R._load("more_topup"), R._load("firm")
    W2, redo, _ = R.worlds()
    # worlds with identical lives: every base, bank and told life of the first pass the same as an earlier world's
    def sig(n):
        return tuple(tuple(map(tuple, (x[:2] for x in main[n][a]))) for a in ("base", "bank", "told"))
    first = {}
    for n in redo:
        if n in main:
            first.setdefault(sig(n), n)
    dup = {}
    for n in names:
        s = sig(n)
        if s in first:
            dup[n] = first[s]
        else:
            first[s] = n
    print(f"fresh distinct by text, judged: {len(names)}; with lives identical to an earlier world's: {dup}")
    names = [n for n in names if n not in dup]
    Is = {}

    def I_for(k):
        if k not in Is:
            Is[k] = R.boot(k, B)
        return Is[k]

    tally = {"pass": [], "fail": [], "unclear": []}
    nothing, harm_rows = [], []
    for n in names:
        L = {a: lives(n, a, main, top, firm) for a in ("base", "bank", "told")}
        Rf = [x[:2] for x in (ref.get(n) or firm.get(n, {}).get("ref0", []))] + lives(n, "ref", top, firm)
        k = len(L["base"]) // 2
        I = I_for(k)
        if len(L["told"]) != len(L["base"]):     # harm-only worlds: told at 60 pairs alone; judge the gap on the first pass
            Lg = {a: lives(n, a, main) for a in L}
            Ig = I_for(len(Lg["base"]) // 2)
        else:
            Lg, Ig = L, I
        e = {a: R.eff(Lg[a], Ig) for a in Lg}
        fl0, fl = max(e["base"][0], 0.0), np.maximum(e["base"][1], 0.0)
        g0, g = e["told"][0] - fl0, e["told"][1] - fl
        gl, gh = np.percentile(g, [2.5, 97.5])
        if not (gl > 0 and g0 >= 0.1):
            eb, ek = R.eff(L["base"], I), R.eff(L["bank"], I)
            d = ek[1] - eb[1]
            lo, hi = np.percentile(d, [2.5, 97.5])
            nothing.append(n)
            harm_rows.append((n, k, ek[0] - eb[0], lo, hi))
            continue
        with np.errstate(divide="ignore", invalid="ignore"):
            x0, x = (e["bank"][0] - fl0) / g0, (e["bank"][1] - fl) / g
            if len(Rf) == len(Lg["base"]):
                rr = R.eff(Rf, Ig)
                r0 = (rr[0] - fl0) / g0
            else:
                r0 = np.nan
        xl, xh = np.percentile(x[np.isfinite(x)], [2.5, 97.5])
        bar = max(0.5 * r0 if np.isfinite(r0) else 0.0, 0.25)
        v = "pass" if xl > bar else "fail" if xh < bar else "unclear"
        tally[v].append(n)
        print(f"  {n:5s} {len(Lg['base']) // 2:3d} pairs gap {g0:+.2f}[{gl:+.2f},{gh:+.2f}] x {x0:+.2f}[{xl:+.2f},{xh:+.2f}] r {r0:+.2f} "
              f"bar {bar:.2f} {v:7s} " + "; ".join(f"{a} {b_} {c}" for a, b_, c, _ in W[n][1]))
    N = len(names)
    G = sum(len(v) for v in tally.values())
    p, u = len(tally["pass"]), len(tally["unclear"])
    print(f"\njudged {N}; something to learn {G} = {G / N:.2f} {R.wilson(G, N)}")
    print(f"  sure pass {p}, sure fail {len(tally['fail'])}, can't tell {u}")
    print(f"  coverage between {p / G:.3f} [{R.wilson(p, G)[0]:.3f},{R.wilson(p, G)[1]:.3f}] and {(p + u) / G:.3f} "
          f"[{R.wilson(p + u, G)[0]:.3f},{R.wilson(p + u, G)[1]:.3f}]")
    for k_, v in tally.items():
        print(f"  {k_}: {v}")
    sure_harm = [r for r in harm_rows if r[4] < -0.1]
    below = [r for r in harm_rows if r[4] < 0]
    shown = [r for r in harm_rows if r[3] > -0.1]
    print(f"\nnothing to learn {len(nothing)}: no harm shown (lower bound above -.1) {len(shown)}; surely below base {len(below)}; "
          f"surely by more than .1 {len(sure_harm)}; neither shown nor ruled out {len(harm_rows) - len(shown) - len(sure_harm)}")
    for n, k, d, lo, hi in sorted(harm_rows, key=lambda r: r[4]):
        if lo <= -0.1:
            print(f"  {n:5s} {k:3d} pairs bank - base {d:+.3f} [{lo:+.3f},{hi:+.3f}]  " + "; ".join(f"{a} {b_} {c}" for a, b_, c, _ in W[n][1]))
    # 1000 s, with the reference
    Lg, LR = R._load("more_long"), R._load("firm_longref")
    I = R.boot(len(M.LONG_SEEDS), B)
    print("\n1000 s lives, last third, the full bar (20 pairs; the reference at 2.5 ms)")
    for n in Lg:
        b, k_, t = (M.boot_eff(Lg[n][a], I, True) for a in ("base", "bank", "told"))
        fl0, fl = max(b[0], 0), np.maximum(b[1], 0)
        g0, g = t[0] - fl0, t[1] - fl
        gl = np.percentile(g, 2.5)
        with np.errstate(divide="ignore", invalid="ignore"):
            x0, x = (k_[0] - fl0) / g0, (k_[1] - fl) / g
            r0 = (M.boot_eff(LR[n], I, True)[0] - fl0) / g0 if n in LR else np.nan
        if not (gl > 0 and g0 >= 0.1):
            print(f"  {n:5s} nothing to judge (gap {g0:+.2f}, lower {gl:+.2f}); 100 s verdict {rows[n]['verdict']}")
            continue
        xl, xh = np.percentile(x[np.isfinite(x)], [2.5, 97.5])
        bar = max(0.5 * r0 if np.isfinite(r0) else 0.0, 0.25)
        v = "pass" if xl > bar else "fail" if xh < bar else "unclear"
        print(f"  {n:5s} gap {g0:+.2f} x {x0:+.2f}[{xl:+.2f},{xh:+.2f}] r {r0:+.2f} bar {bar:.2f} {v:7s} "
              + "; ".join(f"{a} {b_} {c}" for a, b_, c, _ in W[n][1]))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "final":
        final()
        sys.exit()
    W, retest, harm = chosen()
    print(f"retest {len(retest)} {retest}\nharm {len(harm)}", flush=True)
    if cmd == "retest":
        M.run(retest, W, M.ARMS, RETEST_SEEDS, 0.00125, 100.0, "firm")
        done = R._load("firm")
        main = R._load("main")
        t0 = time.time()
        with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
            for n in retest:
                L = {a: lives(n, a, main, done) for a in ("base", "told")}
                I = R.boot(len(L["base"]) // 2)
                b, t = R.eff(L["base"], I), R.eff(L["told"], I)
                g0, g = t[0] - max(b[0], 0), t[1] - np.maximum(b[1], 0)
                if "ref" in done[n] or not (np.percentile(g, 2.5) > 0 and g0 >= 0.1):
                    continue
                done[n]["ref"] = list(ex.map(M.live, [(W[n][0], "ref", s, c, 100.0) for s in RETEST_SEEDS for c in R.COL], chunksize=2))
                if n not in R._load("ref"):     # the first pass ran no reference here: run its 60 pairs too, so pairs match
                    done[n]["ref0"] = list(ex.map(M.live, [(W[n][0], "ref", s, c, 100.0) for s in R.SEEDS for c in R.COL], chunksize=2))
                R._save("firm", done)
                print(f"retest ref {n} ({time.time() - t0:.0f} s)", flush=True)
    elif cmd == "harm":
        M.run(harm, W, (("base", "circuit"), ("bank", "bank")), HARM_SEEDS, 0.00125, 100.0, "firm")
    elif cmd == "longref":
        done = R._load("firm_longref")
        Lg = R._load("more_long")
        t0 = time.time()
        with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
            for n in Lg:
                if n in done:
                    continue
                done[n] = list(ex.map(M.live, [(W[n][0], "ref", s, c, 1000.0) for s in M.LONG_SEEDS for c in R.COL], chunksize=1))
                R._save("firm_longref", done)
                print(f"longref {n} ({time.time() - t0:.0f} s)", flush=True)

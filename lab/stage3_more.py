"""stage3_more.py: what stage 3's first pass left open (lab/v/stage3_summary.log), main session, 2026-11-07. Fresh seeds for each;
the worlds chosen from the first pass's verdicts, as written here before any of these lives ran.

  harm   the six nothing-to-learn worlds where the bank was surely more than .1 below base (g80, g118, g172, g262, g322, g367: five
         with SENSE raised, one REACH), and plain, on 200 fresh pairs, seeds 80300-80499, 1.25 ms: does the harm hold?
  long   1000 s lives (the user's decision, 2026-11-06, for evidence too scarce in 100 s) on the 19 fresh worlds the bank surely
         failed and the 11 can't-tell ones with the largest gaps (30 in all), base, bank and told, 20 pairs, seeds 81000-81019,
         1.25 ms: is a failure "too short" or "can't"? x is read on the life's last third, as the score is.
  topup  the 37 fresh can't-tell worlds, 240 more pairs (seeds 80500-80739; 300 with the first pass's), base, bank and told at
         1.25 ms, the reference at 2.5 ms: as many verdicts as 300 pairs can give.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage3_more.py harm|long|topup|analyse"""
import sys
import time
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import stage3_random as R

HARM = ("plain", "g80", "g118", "g172", "g262", "g322", "g367")
HARM_SEEDS = range(80300, 80500)
LONG_SEEDS = range(81000, 81020)
TOPUP_SEEDS = range(80500, 80740)


def live(job):
    """(text, arm, seed, first, seconds) -> (gain, spent) over the whole life and over its last third, or ("refused", why)."""
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    from stage2_lang.sim import Refused
    text, arm, seed, first, secs = job
    try:
        l = S.live(S.make(S.world_of(text), arm, seed, first), secs)
    except Refused as e:
        return ("refused", str(e)[:200])
    g = [a - COST * b for a, b, _ in l]
    return (sum(g), spent(l), g[2], l[2][2] / sum(t for _, _, t in l))   # spent is a rate times time: the last third's share of it


def chosen():
    import pickle
    W, redo, fresh = R.worlds()
    rows = R._load("rows")
    texts, gap, unclear, fail = {}, [], [], []
    seen = {W[n][0] for n in redo}
    for n in fresh:
        t = W[n][0]
        if t in seen:
            continue
        seen.add(t)
        v = rows.get(n)
        if not v or v["out"] or v["nothing"]:
            continue
        bar = max(0.5 * v["r"] if np.isfinite(v["r"]) else 0.0, 0.25)
        lo, hi = v["x_ci"]
        if hi < bar:
            fail.append(n)
        elif lo <= bar:
            unclear.append(n)
    unclear_big = sorted(unclear, key=lambda n: -rows[n]["gap"])[:11]
    return W, fail, unclear, unclear_big


def run(names, W, arms, seeds, dt, secs, key):
    done = R._load(key)
    t0 = time.time()
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(dt, False)) as ex:
        for n in names:
            if n in done:
                continue
            text = R.PLAIN if n == "plain" else W[n][0]
            done[n] = {k: list(ex.map(live, [(text, arm(text) if callable(arm) else arm, s, c, secs) for s in seeds for c in R.COL], chunksize=2))
                       for k, arm in arms}
            R._save(key, done)
            print(f"{key} {n} ({time.time() - t0:.0f} s)", flush=True)


ARMS = (("base", "circuit"), ("bank", "bank"), ("told", R.told_arm))


def boot_eff(L, I, last=False):
    L = [x for x in L if x[0] != "refused"]
    g = np.array([x[2] if last else x[0] for x in L], float)
    s = np.array([x[1] * (x[3] if last else 1) for x in L], float)
    return g.sum() / s.sum(), g[I].sum(1) / s[I].sum(1)


def analyse():
    W, fail, unclear, big = chosen()
    rows = R._load("rows")
    print("== harm, 200 fresh pairs at 1.25 ms (bank - base, 95%; nothing to learn in these worlds)")
    H = R._load("more_harm")
    I = R.boot(len(HARM_SEEDS))
    for n in HARM:
        if n in H:
            b, k = boot_eff(H[n]["base"], I), boot_eff(H[n]["bank"], I)
            t = boot_eff(H[n]["told"], I)
            d = k[1] - b[1]
            lo, hi = np.percentile(d, [2.5, 97.5])
            what = "plain" if n == "plain" else "; ".join(f"{a} {b_} {c}" for a, b_, c, _ in W[n][1])
            print(f"  {n:5s} base {b[0]:+.2f} bank {k[0]:+.2f} told {t[0]:+.2f}  bank - base {k[0] - b[0]:+.2f} [{lo:+.2f},{hi:+.2f}]"
                  f" {'HARM' if hi < -0.1 else 'below base' if hi < 0 else 'no harm shown' if lo > -0.1 else 'not ruled out'}   {what}  "
                  f"{[x for x in W[n][0].split('(const ')[1:]][:1] if n != 'plain' else ''}")
    print("\n== 1000 s lives, 20 pairs at 1.25 ms: x over the whole life and over its last third (100 s lives' x beside)")
    Lg = R._load("more_long")
    I = R.boot(len(LONG_SEEDS))
    for n in fail + [m for m in big if m not in fail]:
        if n not in Lg:
            continue
        out = []
        for last in (False, True):
            b, k, t = (boot_eff(Lg[n][a], I, last) for a in ("base", "bank", "told"))
            fl0, fl = max(b[0], 0), np.maximum(b[1], 0)
            with np.errstate(divide="ignore", invalid="ignore"):
                x0, x = (k[0] - fl0) / (t[0] - fl0), (k[1] - fl) / (t[1] - fl)
            lo, hi = np.percentile(x[np.isfinite(x)], [2.5, 97.5])
            out.append(f"{x0:+.2f}[{lo:+.2f},{hi:+.2f}] (gap {t[0] - fl0:+.2f})")
        v = rows[n]
        print(f"  {n:5s} {'fail' if n in fail else 'unclear':7s} 100 s x {v['x']:+.2f} | 1000 s: whole {out[0]}  last third {out[1]}   "
              + "; ".join(f"{a} {b_} {c}" for a, b_, c, _ in W[n][1]))
    print("\n== top-up: the can't-tell worlds at 300 pairs (60 first-pass + 240), x and r with 95%, the verdict against max(.5 r, .25)")
    T = R._load("more_topup")
    main, ref = R._load("main"), R._load("ref")
    I = R.boot(300)
    tally = {"pass": [], "fail": [], "unclear": []}
    for n in unclear:
        if n not in T:
            continue
        L = {a: [x[:2] for x in main[n][a]] + [x[:2] for x in T[n][a] if x[0] != "refused"] for a in ("base", "bank", "told")}
        Rf = [x[:2] for x in ref.get(n, [])] + [x[:2] for x in T[n].get("ref", []) if x[0] != "refused"]
        e = {a: R.eff(L[a], I) for a in L}
        fl0, fl = max(e["base"][0], 0), np.maximum(e["base"][1], 0)
        g0, g = e["told"][0] - fl0, e["told"][1] - fl
        with np.errstate(divide="ignore", invalid="ignore"):
            x0, x = (e["bank"][0] - fl0) / g0, (e["bank"][1] - fl) / g
            if len(Rf) == len(L["base"]):
                rr = R.eff(Rf, I)
                r0, r = (rr[0] - fl0) / g0, (rr[1] - fl) / g
            else:
                r0, r = np.nan, np.full(len(I), np.nan)
        xl, xh = np.percentile(x[np.isfinite(x)], [2.5, 97.5])
        gl, gh = np.percentile(g, [2.5, 97.5])
        bar = max(0.5 * r0 if np.isfinite(r0) else 0.0, 0.25)
        if not (gl > 0 and g0 >= 0.1):
            verdict = "nothing"
        else:
            verdict = "pass" if xl > bar else "fail" if xh < bar else "unclear"
        tally.setdefault(verdict, []).append(n)
        print(f"  {n:5s} gap {g0:+.2f}[{gl:+.2f},{gh:+.2f}] x {x0:+.2f}[{xl:+.2f},{xh:+.2f}] r {r0:+.2f} bar {bar:.2f}  {verdict:8s} "
              + "; ".join(f"{a} {b_} {c}" for a, b_, c, _ in W[n][1]))
    print("  " + ", ".join(f"{k} {len(v)}" for k, v in tally.items()))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "analyse":
        analyse()
        sys.exit()
    W, fail, unclear, big = chosen()
    if cmd == "harm":
        run(HARM, W, ARMS, HARM_SEEDS, 0.00125, 100.0, "more_harm")
    elif cmd == "long":
        run(fail + [m for m in big if m not in fail], W, ARMS, LONG_SEEDS, 0.00125, 1000.0, "more_long")
    elif cmd == "topup":
        run(unclear, W, ARMS, TOPUP_SEEDS, 0.00125, 100.0, "more_topup")
        done = R._load("more_topup")
        t0 = time.time()
        with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
            for n in unclear:
                if "ref" in done.get(n, {}):
                    continue
                done[n]["ref"] = list(ex.map(live, [(W[n][0], "ref", s, c, 100.0) for s in TOPUP_SEEDS for c in R.COL], chunksize=2))
                R._save("more_topup", done)
                print(f"topup ref {n} ({time.time() - t0:.0f} s)", flush=True)

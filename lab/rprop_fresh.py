"""rprop_fresh.py: the self-sizing balance learner (lab/rprop.py) judged on fresh seeds, predictions 8-11 of lab/v/adaptive_predictions.md,
written first. Arms: base, the old bank, the sized bank, the bank never wobbling. Main session, 2026-11-08.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/rprop_fresh.py [2|3]   (2: v2, predictions 12-14; 3: v3, 15-17)"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import stage3_random as R
import stage3_more as M
import adaptive as A
import rprop as RP
from stage2_lang.worlds import W as HAND

DOUBLE = "(world (meta (link L1) (group body)) (on fire (set gain (if (= thruster 0) 2 1))))"
ARMS = ("base", "old", "sized", "never")
TESTS = (("track", DOUBLE, 2000.0, range(81900, 81920), ("old", "sized")),
         ("thrusters", HAND["thrusters"]["text"], 100.0, range(81920, 81950), ARMS),
         ("thrusters", HAND["thrusters"]["text"], 1000.0, range(81950, 81960), ARMS),
         ("plain", R.PLAIN, 10000.0, range(81960, 81970), ("base", "old", "sized")))
TESTS2 = (("track", DOUBLE, 2000.0, range(82000, 82020), ("old", "sized2")),       # v2 (python rprop_fresh.py 2), fresh seeds
          ("thrusters", HAND["thrusters"]["text"], 100.0, range(82020, 82050), ("base", "old", "sized2", "never")),
          ("thrusters", HAND["thrusters"]["text"], 1000.0, range(82050, 82060), ("base", "old", "sized2", "never")))
TESTS3 = (("track", DOUBLE, 2000.0, range(82100, 82120), ("old", "sized3")),       # v3 (python rprop_fresh.py 3), fresh seeds
          ("thrusters", HAND["thrusters"]["text"], 100.0, range(82120, 82150), ("base", "old", "sized3", "never")),
          ("thrusters", HAND["thrusters"]["text"], 1000.0, range(82150, 82160), ("base", "old", "sized3", "never")))
TESTS4 = (("track", DOUBLE, 2000.0, range(82200, 82220), ("old", "sized4")),       # v4 (python rprop_fresh.py 4), fresh seeds
          ("thrusters", HAND["thrusters"]["text"], 100.0, range(82220, 82250), ("base", "old", "sized4", "never")),
          ("thrusters", HAND["thrusters"]["text"], 1000.0, range(82250, 82260), ("base", "old", "sized4", "never")))
TESTS5 = (("track", DOUBLE, 2000.0, range(82300, 82320), ("old", "sized5")),       # v5 (python rprop_fresh.py 5), fresh seeds
          ("thrusters", HAND["thrusters"]["text"], 100.0, range(82320, 82350), ("base", "old", "sized5", "never")),
          ("thrusters", HAND["thrusters"]["text"], 1000.0, range(82350, 82360), ("base", "old", "sized5", "never")))
TESTS6 = (("track", DOUBLE, 2000.0, range(82400, 82420), ("old", "sized6")),       # v6 (python rprop_fresh.py 6), fresh seeds
          ("thrusters", HAND["thrusters"]["text"], 100.0, range(82420, 82450), ("base", "old", "sized6", "never")),
          ("thrusters", HAND["thrusters"]["text"], 1000.0, range(82450, 82460), ("base", "old", "sized6", "never")))
NEAR = HAND["thrusters"]["text"].replace("(uniform -1 1)", "(uniform -0.07 0.07)")   # nearly plain: each thruster 0.95 to 1.05
TESTS6L = (("plain", R.PLAIN, 10000.0, range(82460, 82470), ("base", "old", "sized6")),       # v6's long-life harm (rprop_fresh.py 6L)
           ("nearplain", NEAR, 10000.0, range(82470, 82480), ("base", "old", "sized6")))
TESTS7 = (("track", DOUBLE, 2000.0, range(82500, 82520), ("old", "sized7")),       # v7 (python rprop_fresh.py 7), fresh seeds
          ("thrusters", HAND["thrusters"]["text"], 1000.0, range(82520, 82530), ("base", "old", "sized7")),
          ("plain", R.PLAIN, 10000.0, range(82530, 82540), ("base", "old", "sized7")),
          ("nearplain", NEAR, 10000.0, range(82540, 82550), ("base", "old", "sized7")))
TESTS8 = (("track", DOUBLE, 2000.0, range(82600, 82620), ("old", "sized8")),       # v8 (python rprop_fresh.py 8), fresh seeds
          ("thrusters", HAND["thrusters"]["text"], 100.0, range(82620, 82650), ("base", "old", "sized8", "never")),
          ("thrusters", HAND["thrusters"]["text"], 1000.0, range(82650, 82660), ("base", "old", "sized8")),
          ("plain", R.PLAIN, 10000.0, range(82660, 82670), ("base", "old", "sized8")))
TESTS7M = (("track", DOUBLE, 2000.0, range(82700, 82720), ("old", "sized7")),     # v7 firmed up (rprop_fresh.py 7m): 20 more pairs each
           ("plain", R.PLAIN, 10000.0, range(82720, 82740), ("base", "old", "sized7")),
           ("nearplain", NEAR, 10000.0, range(82740, 82760), ("base", "old", "sized7")))


def job(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    text, secs, arm, seed, first = j
    w = S.world_of(text)
    if arm == "base":
        lf = S.make(w, "circuit", seed, first)
    elif arm == "old":
        lf = A.make(w, seed, first, None, cls=A.RV.RV)
    elif arm == "sized":
        lf = A.make(w, seed, first, None, cls=RP.SZ)
    elif arm == "sized2":                                       # v2: no give-ups, evidence summed until significant
        lf = A.make(w, seed, first, {"n_max": 10 ** 9}, cls=RP.SZ)
    elif arm == "sized3":                                       # v3: v2 with its step never above its born .3 (v2 overshot to 1.2-1.4)
        lf = A.make(w, seed, first, {"n_max": 10 ** 9, "Dmax": 0.3}, cls=RP.SZ)
    elif arm == "sized3f":                                      # (diagnosis) v3 with no floor on its wobble: the wobble is D, down to .0125
        lf = A.make(w, seed, first, {"n_max": 10 ** 9, "Dmax": 0.3, "sd_min": 0.0}, cls=RP.SZ)
    elif arm == "sized4":                                       # v4: Dmax .3, give-ups after 50 drives quiet the wobble, sums kept
        lf = A.make(w, seed, first, {"Dmax": 0.3, "keep": 1}, cls=RP.SZ)
    elif arm == "sized5":                                       # v5: give-ups halve only the wobble, sums kept; a move restores it
        lf = A.make(w, seed, first, {"Dmax": 0.3, "split": 1}, cls=RP.SZ)
    elif arm == "sized6":                                       # v6: v3, quieting only when the wobble hurts both ways (a peak)
        lf = A.make(w, seed, first, {"n_max": 10 ** 9, "Dmax": 0.3, "curv": 1}, cls=RP.SZ)
    elif arm == "sized7":                                       # v7: v6 with its wobble's floor .005 (the peak test sets the floor)
        lf = A.make(w, seed, first, {"n_max": 10 ** 9, "Dmax": 0.3, "curv": 1, "sd_min": 0.005}, cls=RP.SZ)
    elif arm == "sized8":                                       # v8: v7 with an always-valid bar on its quieting test
        lf = A.make(w, seed, first, {"n_max": 10 ** 9, "Dmax": 0.3, "curv": 1, "sd_min": 0.005, "seq": 1}, cls=RP.SZ)
    else:
        lf = A.make(w, seed, first, {"avg": 2, "a0": 0.0, "rearm": 0})     # never wobbles
    l = S.live(lf, secs)
    g = [x - COST * y for x, y, _ in l]
    return (sum(g), spent(l), g[2], l[2][2] / sum(t for _, _, t in l)), getattr(lf.brain, "trace", None)


if __name__ == "__main__":
    out = {}
    ver = sys.argv[1] if sys.argv[1:] else ""
    TESTS = {"2": TESTS2, "3": TESTS3, "3b": TESTS3[1:], "4": TESTS4, "5": TESTS5, "6": TESTS6, "6L": TESTS6L, "7": TESTS7, "8": TESTS8, "7m": TESTS7M,
             "3f": (TESTS3[2][:4] + (("old", "sized3", "sized3f"),),)}.get(ver, TESTS)   # 3f: diagnosis of 17, on its own seeds     # 3b: v3 without its track (rerun after a crash)
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.00125, False)) as ex:
        for name, text, secs, seeds, arms in TESTS:
            L, T = {}, {}
            for a in arms:
                r = list(ex.map(job, [(text, secs, a, s, c) for s in seeds for c in R.COL], chunksize=2))
                L[a], T[a] = [x[0] for x in r], [x[1] for x in r]
            out[name, secs] = L, T
            R._save("rprop_fresh" + ver, out)
            if name == "track":
                print(f"== double thruster (the right |x| .69), {secs:.0f} s, {len(seeds)} pairs: |x| mean (sd)", flush=True)
                for a in arms:
                    row = f"  {a:6s}"
                    for t0 in (0, 100, 200, 300, 500, 1000, 2000):
                        v = np.abs([min(t, key=lambda e: abs(e[0] - t0))[1] for t in T[a]])
                        row += f"  {t0}s {v.mean():.2f} ({v.std():.2f})"
                    print(row, flush=True)
                continue
            I = R.boot(len(seeds), 20000)
            last = secs > 100.0
            e = {a: M.boot_eff(L[a], I, last) for a in arms}
            print(f"== {name}, {secs:.0f} s, {len(seeds)} pairs ({'last third' if last else 'whole life'})", flush=True)
            for a in arms:
                row = f"  {a:6s} {e[a][0]:.3f}"
                for ref in ("base", "old"):
                    if ref != a and ref in e:
                        lo, hi = np.percentile(e[a][1] - e[ref][1], [2.5, 97.5])
                        row += f"   minus {ref} {e[a][0] - e[ref][0]:+.3f} [{lo:+.3f},{hi:+.3f}]"
                print(row, flush=True)

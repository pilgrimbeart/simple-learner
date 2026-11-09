"""adaptive_fresh.py: rules 1, 2 and 3' (lab/adaptive.py, avg=2) judged on fresh seeds, predictions 5-7 of lab/v/adaptive_predictions.md,
written first. Arms: base, the old bank, the adaptive bank, and the bank never wobbling (a0 0, re-arming off). Main session, 2026-11-08.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/adaptive_fresh.py"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import stage3_random as R
import stage3_more as M
import adaptive as A
from stage2_lang.worlds import W as HAND

ARMS = {"base": "circuit", "old": "bank", "adaptive": {"avg": 2}, "never": {"avg": 2, "a0": 0.0, "rearm": 0}}
TESTS = (("plain", R.PLAIN, 10000.0, range(81600, 81610), ("base", "old", "adaptive")),
         ("thrusters", HAND["thrusters"]["text"], 100.0, range(81610, 81640), tuple(ARMS)),
         ("thrusters", HAND["thrusters"]["text"], 1000.0, range(81640, 81650), tuple(ARMS)))


def job(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    text, secs, arm, seed, first = j
    a = ARMS[arm]
    lf = A.make(S.world_of(text), seed, first, dict(a)) if isinstance(a, dict) else S.make(S.world_of(text), a, seed, first)
    l = S.live(lf, secs)
    g = [x - COST * y for x, y, _ in l]
    return (sum(g), spent(l), g[2], l[2][2] / sum(t for _, _, t in l))


if __name__ == "__main__":
    out = {}
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.00125, False)) as ex:
        for name, text, secs, seeds, arms in TESTS:
            I = R.boot(len(seeds), 20000)
            L = {a: list(ex.map(job, [(text, secs, a, s, c) for s in seeds for c in R.COL], chunksize=2)) for a in arms}
            out[name, secs] = L
            R._save("adaptive_fresh", out)
            last = secs > 100.0
            e = {a: M.boot_eff(L[a], I, last) for a in arms}
            print(f"== {name}, {secs:.0f} s, {len(seeds)} pairs ({'last third' if last else 'whole life'})", flush=True)
            for a in arms:
                row = f"  {a:9s} {e[a][0]:.3f}"
                for ref in ("base", "old"):
                    if ref != a and ref in e:
                        lo, hi = np.percentile(e[a][1] - e[ref][1], [2.5, 97.5])
                        row += f"   minus {ref} {e[a][0] - e[ref][0]:+.3f} [{lo:+.3f},{hi:+.3f}]"
                print(row, flush=True)

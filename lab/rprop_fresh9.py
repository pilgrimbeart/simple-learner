"""rprop_fresh9.py: v9 of the sized balance learner (lab/rprop9.py) judged on fresh seeds 82800-82849, predictions 40-43 of
lab/v/adaptive_predictions.md, written first. v7 rides alongside in plain and nearly plain, paired. Main session, night of 2026-11-08.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/rprop_fresh9.py"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import stage3_random as R
import stage3_more as M
import adaptive as A
import rprop9 as R9
import rprop_fresh as F

V7 = {"n_max": 10 ** 9, "Dmax": 0.3, "curv": 1, "sd_min": 0.005}
KW = {"sized9a": {**V7, "seqm": 1}, "sized9b": {**V7, "seqm": 1, "peakD": 1}}
TESTS9 = (("track", F.DOUBLE, 2000.0, range(82800, 82820), ("old", "sized9a", "sized9b")),
          ("thrusters", F.HAND["thrusters"]["text"], 1000.0, range(82820, 82830), ("base", "old", "sized9a", "sized9b")),
          ("plain", R.PLAIN, 10000.0, range(82830, 82840), ("base", "sized7", "sized9a", "sized9b")),
          ("nearplain", F.NEAR, 10000.0, range(82840, 82850), ("base", "sized7", "sized9a", "sized9b")))


def job(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    text, secs, arm, seed, first = j
    if arm not in KW:
        return F.job(j) + (None,)
    lf = A.make(S.world_of(text), seed, first, dict(KW[arm]), cls=R9.SZ9)
    l = S.live(lf, secs)
    g = [x - COST * y for x, y, _ in l]
    return (sum(g), spent(l), g[2], l[2][2] / sum(t for _, _, t in l)), getattr(lf.brain, "trace", None), lf.brain.moves


if __name__ == "__main__":
    out = {}
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.00125, False)) as ex:
        for name, text, secs, seeds, arms in TESTS9:
            L, T, MV = {}, {}, {}
            for a in arms:
                r = list(ex.map(job, [(text, secs, a, s, c) for s in seeds for c in R.COL], chunksize=2))
                L[a], T[a], MV[a] = [x[0] for x in r], [x[1] for x in r], [x[2] for x in r]
            out[name, secs] = L, T, MV
            R._save("rprop_fresh9", out)
            if name == "track":
                print(f"== double thruster (the right |x| .69), {secs:.0f} s, {len(seeds)} pairs: |x| mean (sd)", flush=True)
                for a in arms:
                    row = f"  {a:7s}"
                    for t0 in (0, 100, 200, 300, 500, 1000, 2000):
                        v = np.abs([min(t, key=lambda e: abs(e[0] - t0))[1] for t in T[a]])
                        row += f"  {t0}s {v.mean():.2f} ({v.std():.2f})"
                    v = np.abs([t[-1][1] for t in T[a]])
                    print(row + f"  | within .1 of .69: {np.sum(np.abs(v - 0.69) < 0.1)}, within .05 of 0: {np.sum(v < 0.05)}", flush=True)
                continue
            I = R.boot(len(seeds), 20000)
            last = secs > 100.0
            e = {a: M.boot_eff(L[a], I, last) for a in arms}
            print(f"== {name}, {secs:.0f} s, {len(seeds)} pairs ({'last third' if last else 'whole life'})", flush=True)
            for a in arms:
                row = f"  {a:7s} {e[a][0]:.3f}"
                for ref in ("base", "old", "sized7"):
                    if ref != a and ref in e:
                        lo, hi = np.percentile(e[a][1] - e[ref][1], [2.5, 97.5])
                        row += f"   minus {ref} {e[a][0] - e[ref][0]:+.3f} [{lo:+.3f},{hi:+.3f}]"
                if a in KW and secs >= 10000:
                    late = [sum(1 for m in mv if m[0] > secs * 2 / 3) for mv in MV[a]]
                    row += f"   events in the last third per life {np.mean(late):.1f}"
                print(row, flush=True)

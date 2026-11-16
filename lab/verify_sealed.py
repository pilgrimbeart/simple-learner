"""verify_sealed.py: check a sealed ladder's rungs without showing their rules (2026-11-15): each compiles, its life length, and the gap
between the starting brain and the told brain on the given seeds. Prints numbers only.
    .venv/bin/python lab/verify_sealed.py LADDER.json PAIRS SEED0"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import ladders as L
import stage3_random as R
from stage2_lang import lang

if __name__ == "__main__":
    d = json.load(open(sys.argv[1]))
    n, s0 = int(sys.argv[2]), int(sys.argv[3])
    I = R.boot(n)
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        for r in d["rungs"]:
            try:
                lang.World(r["text"], compile_only=True)
                ok = "compiles"
            except Exception as e:
                print(f"rung {r['size']}: does not compile ({type(e).__name__})")
                continue
            jobs = [(r["text"], arm, {}, s, c, float(r["seconds"])) for arm in ("circuit", "vtold") for s in range(s0, s0 + n) for c in ("red", "blue")]
            res = list(ex.map(L.job, jobs))
            b = L.scored(res[:2 * n], float(r["seconds"]), I)
            t = L.scored(res[2 * n:], float(r["seconds"]), I)
            g = t[1] - b[1]
            line = (f"rung {r['size']}: {ok}, life {r['seconds']} s; starting {b[0]:+.2f}, told {t[0]:+.2f}, gap {t[0] - b[0]:+.2f} "
                    f"[{np.percentile(g, 2.5):+.2f}, {np.percentile(g, 97.5):+.2f}]")
            if "vfilt" in sys.argv:                     # (D69) the ideal filter's belief steering the told body: the gap any learner can close
                fj = [(r["text"], "vfilt", {}, s, c, float(r["seconds"])) for s in range(s0, s0 + n) for c in ("red", "blue")]
                f = L.scored(list(ex.map(L.job, fj)), float(r["seconds"]), I)
                fr = (f[1] - b[1]) / (t[1] - b[1])
                line += f"; ideal filter {f[0]:+.2f}, closing {(f[0] - b[0]) / (t[0] - b[0]):+.2f} [{np.percentile(fr, 2.5):+.2f}, {np.percentile(fr, 97.5):+.2f}]"
            print(line, flush=True)

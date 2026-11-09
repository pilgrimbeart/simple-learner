"""rprop_short.py: why the sized learner (v7) costs so much in 100 s lives (lab/v/stage3_cure.log: bankS - bank -.60 on average over
stage 3's 184 worlds, surely worse in 152). Two candidate causes: its wobble, born .3, still large while a short life lasts; or chance
moves of its .3 step (its two-standard-error move test, checked every drive). Arms on plain, g402 (stage 3's worst, -1.11) and the
thrusters, 100 s, fresh seeds 82900-82929: base, old, v7, v7 never moving (nomove: wobble only), v9a (always-valid move bar), v9b (v9a,
the peak's mark halves the step too), v7 born with its wobble .1 (D0 .1). Predictions 44-46 of lab/v/adaptive_predictions.md first.
Main session, night of 2026-11-08.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/rprop_short.py"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import stage3_random as R
import stage3_more as M
import stage3_firm as SF
import adaptive as A
import rprop9 as R9
import rprop_fresh as F

V7 = {"n_max": 10 ** 9, "Dmax": 0.3, "curv": 1, "sd_min": 0.005}
KW = {"v7": V7, "nomove": {**V7, "nomove": 1}, "v9a": {**V7, "seqm": 1}, "v9b": {**V7, "seqm": 1, "peakD": 1}, "v7D1": {**V7, "D0": 0.1}}
ARMS = ("base", "old") + tuple(KW)


class SZs(R9.SZ9):
    """SZ9 with nomove: a move test that never fires (its bar infinite), the wobble's own peak test alone."""
    def step(self):
        if self.p.get("nomove"):
            self.S1 = 0.0
        return super().step()


def job(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    text, arm, seed, first = j
    if arm in ("base", "old"):
        return F.job((text, 100.0, arm, seed, first))[0], None
    lf = A.make(S.world_of(text), seed, first, dict(KW[arm]), cls=SZs)
    l = S.live(lf, 100.0)
    g = [x - COST * y for x, y, _ in l]
    b = lf.brain
    return (sum(g), spent(l), g[2], l[2][2] / sum(t for _, _, t in l)), (b.p["sd"], b.x, len(b.moves))


if __name__ == "__main__":
    W, _ = SF.distinct()
    worlds = (("plain", R.PLAIN), ("g402", W["g402"][0]), ("thrusters", F.HAND["thrusters"]["text"]))
    seeds = range(82900, 82930)
    I = R.boot(len(seeds), 20000)
    out = {}
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.00125, False)) as ex:
        for name, text in worlds:
            L, X = {}, {}
            for a in ARMS:
                r = list(ex.map(job, [(text, a, s, c) for s in seeds for c in R.COL], chunksize=2))
                L[a], X[a] = [x[0] for x in r], [x[1] for x in r]
            out[name] = L, X
            R._save("rprop_short", out)
            e = {a: M.boot_eff(L[a], I) for a in ARMS}
            print(f"== {name}, 100 s, {len(seeds)} pairs (whole life)", flush=True)
            for a in ARMS:
                row = f"  {a:7s} {e[a][0]:.3f}"
                for ref in ("base", "old", "v7"):
                    if ref != a and ref in e:
                        lo, hi = np.percentile(e[a][1] - e[ref][1], [2.5, 97.5])
                        row += f"   minus {ref} {e[a][0] - e[ref][0]:+.3f} [{lo:+.3f},{hi:+.3f}]"
                if X[a][0] is not None:
                    sd, x, nm = np.array(X[a]).T
                    row += f"   at 100 s: wobble {np.median(sd):.3f} (median), |x| {np.mean(np.abs(x)):.2f}, events {np.mean(nm):.1f}"
                print(row, flush=True)

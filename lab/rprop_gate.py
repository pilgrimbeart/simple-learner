"""rprop_gate.py: a diagnostic, not a cure. lab/v/rprop_wobble_signal.log: in plain at 100 s even a fixed wobble of .05 costs 11% of the
food (-.28), and the drive's own outcome needs about 1,400 drives to see it (a life has about 96). So no rule judging the wobble by its
drives can make a born-exploring learner safe in short plain lives. The old bank was safe there because its fixed gate (wobble only below
15 good tastes per 32 s, lab/universal.py) stops the wobble while it eats well; that gate is a rate the body supplies, the fault
lab/adaptive.py set out to replace. Here the sized learner (v7 or v9b) keeps that gate, to measure what the gate alone buys: at 100 s
(this file) and, if worth it, at 10,000 s. Drives drawn while the gate is shut (no wobble) teach nothing. Main session, night of
2026-11-08.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/rprop_gate.py"""
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
KW = {"v7": V7, "v7g": {**V7, "gated": 1}, "v9bg": {**V7, "seqm": 1, "peakD": 1, "gated": 1}}
ARMS = ("base", "old") + tuple(KW)


class SZg(R9.SZ9):
    def _wobble(self):
        super()._wobble()
        self.sd_l = self.p["sd"]                        # the learner's own wobble; the gate decides whether it is used

    def step(self):
        p = self.p
        if p.get("gated"):
            w = p.get("win", 200.0)
            p["sd"] = self.sd_l if self.rate * 32.0 / w < p.get("gate", 15.0) else 0.0
        if self.e == 0.0 and self.b is not None and p.get("gated"):
            n0 = self.drives                            # a drive with no wobble: judged by DriveBal's mean only, nothing learned
            out = R9.RP.RV.RV.step(self)
            return out
        return super().step()


def job(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    text, arm, seed, first = j
    if arm in ("base", "old"):
        return F.job((text, 100.0, arm, seed, first))[0]
    lf = A.make(S.world_of(text), seed, first, dict(KW[arm]), cls=SZg)
    l = S.live(lf, 100.0)
    g = [x - COST * y for x, y, _ in l]
    return (sum(g), spent(l), g[2], l[2][2] / sum(t for _, _, t in l))


if __name__ == "__main__":
    W, _ = SF.distinct()
    worlds = (("plain", R.PLAIN), ("g402", W["g402"][0]), ("thrusters", F.HAND["thrusters"]["text"]), ("nearplain", F.NEAR))
    seeds = range(82960, 82990)
    I = R.boot(len(seeds), 20000)
    out = {}
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.00125, False)) as ex:
        for name, text in worlds:
            L = {a: list(ex.map(job, [(text, a, s, c) for s in seeds for c in R.COL], chunksize=2)) for a in ARMS}
            out[name] = L
            R._save("rprop_gate", out)
            e = {a: M.boot_eff(L[a], I) for a in ARMS}
            print(f"== {name}, 100 s, {len(seeds)} pairs (whole life)", flush=True)
            for a in ARMS:
                row = f"  {a:7s} {e[a][0]:.3f}"
                for ref in ("base", "old", "v7"):
                    if ref != a and ref in e:
                        lo, hi = np.percentile(e[a][1] - e[ref][1], [2.5, 97.5])
                        row += f"   minus {ref} {e[a][0] - e[ref][0]:+.3f} [{lo:+.3f},{hi:+.3f}]"
                print(row, flush=True)

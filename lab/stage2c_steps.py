"""stage2c_steps.py: stage 2c, parts 4 and 5.

  nine     plain and the nine at 10 ms, base, bank and reference, the switch off (creature.Life's loop, the brains as they are) against
           on (everything in seconds), on the same seeds 66710-66809 x 2 (100 pairs): each arm's level in each mode, paired differences,
           bank - base in each mode
  halve    plain, swap10, alternate, unreliable, digest and noisy, base, bank and reference, at 10, 5, 2.5, 1.25 and 0.625 ms, 100 pairs a
           step, fresh seeds each step (lab/v/stage2c_predictions.md), the arms paired within a step; before the conversion (switch
           off) and after (on). The tick set everywhere as lab/stage2_checks.set_tick does, in a fresh pool per step.
  analyse  the halving's table: levels and bank - base per step; successive differences (independent bootstraps) with 95%; where each
           settles, strictly (the difference's interval inside +-.05) and by point (|d| < .05, the interval reaching 0)

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage2c_steps.py nine|halve|analyse"""
import pickle
import sys
import time
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np

OUT = "/home/pilgrim/nca-scratch-backup/stage2c/"
COL = ("red", "blue")
ARMS = (("base", "circuit"), ("bank", "bank"))   # the halving without the reference, to halve its cost (main session, 2026-11-06); nine ran with ("ref", "ref") too
NINE = ("plain", "swap10", "alternate", "pattern", "digest", "unreliable", "patchy", "weak", "noisy")
SIX = ("plain", "swap10", "alternate", "unreliable", "digest", "noisy")
STEPS = (0.01, 0.005, 0.0025, 0.00125, 0.000625)
HALVE_SEEDS = {False: [range(66810 + 100 * i, 66910 + 100 * i) for i in range(5)], True: [range(67310 + 100 * i, 67410 + 100 * i) for i in range(5)]}


def _init(dt, secs):
    import stage2_checks as C
    from stage2_lang import sim
    if abs(sim.WLife.dt - dt) > 1e-15:
        C.set_tick(dt)
    sim.WLife.seconds = secs
    sim.WLife.instruments = False                       # hand worlds, vetted: the per-tick record filled memory (main session, 2026-11-06)


def one(job):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S, worlds as WW
    name, arm, seed, first, secs = job
    l = S.live(S.make(S.world_of(WW.W[name]["text"]), arm, seed, first, seconds=secs))
    return sum(a - COST * b for a, b, _ in l), spent(l)


def run(worlds, seeds, dt, secs):
    out = {}
    with ProcessPoolExecutor(7, initializer=_init, initargs=(dt, secs)) as ex:
        for w in worlds:
            for label, arm in ARMS:
                out[w, label] = np.array(list(ex.map(one, [(w, arm, s, c, secs) for s in seeds for c in COL], chunksize=4)))
    return out


def boot(n, B=2000, seed=0):
    k = np.random.default_rng(seed).integers(0, n, (B, n))
    return np.concatenate((2 * k, 2 * k + 1), axis=1)


def eff(R, I):
    return R[:, 0].sum() / R[:, 1].sum(), R[I, 0].sum(1) / R[I, 1].sum(1)


def fmt(d, v):
    lo, hi = np.percentile(v, [2.5, 97.5])
    return f"{d:+.3f} [{lo:+.3f},{hi:+.3f}]" + (" SURE" if lo > 0 or hi < 0 else "")


def nine():
    seeds = range(66710, 66810)
    t0 = time.time()
    res = {secs: run(NINE, seeds, 0.01, secs) for secs in (False, True)}
    print(f"== plain and the nine at 10 ms, seeds {seeds.start}-{seeds.stop - 1} x 2, switch off (creature.Life's loop) against on (in seconds); {time.time() - t0:.0f} s", flush=True)
    I = boot(len(seeds))
    for w in NINE:
        parts = []
        for label, _ in ARMS:
            a, va = eff(res[False][w, label], I)
            b, vb = eff(res[True][w, label], I)
            parts.append(f"{label} {a:+.2f} -> {b:+.2f}, {fmt(b - a, vb - va)}")
        d = {}
        for secs in (False, True):
            k, vk = eff(res[secs][w, "bank"], I)
            bb, vb = eff(res[secs][w, "base"], I)
            d[secs] = fmt(k - bb, vk - vb)
        print(f"  {w:10s} " + "; ".join(parts) + f" | bank - base: off {d[False]}, on {d[True]}", flush=True)
    pickle.dump(res, open(OUT + "nine.pkl", "wb"))


def halve():
    res = {}
    t00 = time.time()
    for secs in (False, True):
        for dt, seeds in zip(STEPS, HALVE_SEEDS[secs]):
            t0 = time.time()
            res[secs, dt] = run(SIX, seeds, dt, secs)
            print(f"{'after' if secs else 'before'} {dt * 1000:g} ms: {time.time() - t0:.0f} s ({time.time() - t00:.0f} s in all)", flush=True)
            pickle.dump(res, open(OUT + "halve.pkl", "wb"))


def analyse():
    res = pickle.load(open(OUT + "halve.pkl", "rb"))
    I = boot(100)
    J = boot(100, seed=1)                               # a step against the next: fresh seeds, so independent draws
    print("== halving the step: efficiency per step (100 pairs, fresh seeds each step, the arms paired within a step); d = this step minus the"
          " step before, independent bootstraps, 95%. Settles (strict): two successive halvings with the difference's interval inside +-.05;"
          " (point): two successive |d| < .05 with the interval reaching 0", flush=True)
    for secs in (False, True):
        print(f"\n-- {'after the conversion (in seconds)' if secs else 'before the conversion (switch off)'}", flush=True)
        for w in SIX:
            for q in ("base", "bank", "bank-base"):
                vals, ds, ok_s, ok_p = [], [], [], []
                prev = None
                for i, dt in enumerate(STEPS):
                    if (secs, dt) not in res:
                        continue
                    R = res[secs, dt]
                    B = I if i % 2 == 0 else J
                    if q == "bank-base":
                        a, va = eff(R[w, "bank"], B)
                        b, vb = eff(R[w, "base"], B)
                        x, vx = a - b, va - vb
                    else:
                        x, vx = eff(R[w, q], B)
                    vals.append(f"{dt * 1000:g}ms {x:+.2f}")
                    if prev is not None:
                        d, vd = x - prev[0], vx - prev[1]
                        lo, hi = np.percentile(vd, [2.5, 97.5])
                        ds.append(f"{d:+.2f}[{lo:+.2f},{hi:+.2f}]")
                        ok_s.append(-0.05 < lo and hi < 0.05)
                        ok_p.append(abs(d) < 0.05 and lo <= 0 <= hi)
                    prev = (x, vx)
                at = lambda ok: next((f"{STEPS[i] * 1000:g} ms" for i in range(len(ok) - 1) if ok[i] and ok[i + 1]), "not within these steps")
                print(f"  {w:10s} {q:9s} " + "  ".join(vals) + " | d: " + " ".join(ds) + f" | settles strict: {at(ok_s)}; point: {at(ok_p)}", flush=True)


if __name__ == "__main__":
    {"nine": nine, "halve": halve, "analyse": analyse}[sys.argv[1]]()

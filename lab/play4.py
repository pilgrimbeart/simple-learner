"""play4.py: play pays later? The user's frame (2026-11-10): a life of play first, the challenge later. Lopsided bodies (each thruster a
half to twice); every meal worth nothing until the challenge begins at a moment drawn each life (400 to 600 s), then food and poison
as usual. Scored from that moment: gain (good meals less twice the poisoned, a 10 s) in its first 100 s (being ready at once) and the
200 s after. The arms are play3.py's; a taste trial's clock starts at the first taste, so taste can't spend its trials in the quiet.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 BELIEF=... PREDICT=... .venv/bin/python lab/play4.py [PAIRS] [arms]"""
import math
import pickle
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np

import bodyladder as BL
import play3 as P3
import stage3_random as R

SEEDS0 = 92000
D = "(pow 2 (uniform -1 1))"
P3.WORLD = (f"(world {BL.M} (let a {D}) (let b {D}) (let q (uniform 400 600)) (on fire (set gain (if (= thruster 0) a b)))"
            " (on meal (if (< t q) (set worth 0))))")
SECS = 900.0
WINDOWS = ((0.0, 100.0), (100.0, 300.0))


def job(j):
    from stage2_lang import arms as S
    arm, seed, first = j
    lf = P3.make(arm, seed, first)
    k = {lf.wire_m[th]: g for th, g in ((0, lf.v_a), (1, lf.v_b))}
    S.live(lf, SECS)
    q = lf.v_q
    b = lf.brain
    out = []
    for a, z in WINDOWS:
        lo, hi = (q + a) / lf.dt, (q + z) / lf.dt
        good = sum(am for t, bad, am in lf.scored if lo <= t < hi and not bad)
        badm = sum(am for t, bad, am in lf.scored if lo <= t < hi and bad)
        out.append((good - 2.0 * badm) / (z - a) * 10)
    return dict(arm=arm, seed=seed, win=out, right=math.log(k[1] / k[0]), onset=q, est=getattr(b, "est", None),
                play_end=getattr(b, "play_end", None))


def report(rows, arms):
    n = len(rows) // (2 * len(arms))
    I = R.boot(n)
    base = None
    print(f"gain a 10 s from the challenge's start [95%], and paired against forage | knob error: median, share within .2")
    for a in arms:
        rs = [r for r in rows if r["arm"] == a]
        W = np.array([r["win"] for r in rs])
        line = f"{a:22s}"
        for i, (lo, hi) in enumerate(WINDOWS):
            m = W[I, i].mean(1)
            line += f" | {int(lo)}-{int(hi)} s {W[:, i].mean():+.2f} [{np.percentile(m, 2.5):+.2f},{np.percentile(m, 97.5):+.2f}]"
            if base is not None:
                d = m - base[I, i].mean(1)
                line += f" vs forage {W[:, i].mean() - base[:, i].mean():+.2f} [{np.percentile(d, 2.5):+.2f},{np.percentile(d, 97.5):+.2f}]"
        if a == "forage":
            base = W
        e = [abs(r["est"] - r["right"]) for r in rs if r["est"] is not None]
        if e:
            line += f" | knob {np.median(e):.2f}, {np.mean(np.array(e) < .2):.0%}"
        print(line, flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    n = int(a[0]) if a else 20
    arms = a[1].split(",") if len(a) > 1 and a[1] != "report" else ("forage", "told", "play", "steady", "taste", "steadytaste")
    s0 = next((int(x[1:]) for x in a if x.startswith("s") and x[1:].isdigit()), SEEDS0)   # s93000: fresh seeds
    out = f"/home/pilgrim/git/simple-learner/lab/v/play4_{n}{'' if s0 == SEEDS0 else f'_s{s0}'}.pkl"
    if "report" in a:
        report(pickle.load(open(out, "rb")), arms)
        sys.exit()
    import ledger
    ledger.start()
    jobs = [(arm, s, c) for arm in arms for s in range(s0, s0 + n) for c in ("red", "blue")]
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        rows = list(ex.map(job, jobs, chunksize=2))
    pickle.dump(rows, open(out, "wb"))
    report(rows, arms)

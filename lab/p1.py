"""p1.py: P1, explain the play result (PROGRAMME.md; the review of 2026-11-11). Four arms with equal play before the challenge (400 s,
which ends before the earliest onset), the same estimator (each motor's own beat-clocked record, D47) and the same hand-over (a motor
not yet sure hands its rival to taste, D48), so arms differ only in which data play gathered:
  forage    no play
  uniform   units in a shuffled cycle                       partners:beats:certain:for400
  lp        learning progress chooses (D46)                 partners:beats:for400:handoff
  certain   the unit whose last turn raised certainty most  partners:beats:certainmover:for400
Measured apart: body error at play's end (each motor's best period against the true one, and the knob), calibration (when a motor
says sure, margin >= SURE, how often is it wrong by more than 10%, and how often by a doubled or halved period), play's motor beats,
and food from the challenge's onset (play4's windows). World: play4's (a quiet spell, then food and poison from 400 to 600 s).

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 BELIEF=... PREDICT=... .venv/bin/python lab/p1.py [PAIRS] [s94000]"""
import math
import pickle
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np

import play4 as P4
import play3 as P3
import stage3_random as R

ARMS = {"forage": "forage", "uniform": "partners:beats:certain:for400", "lp": "partners:beats:for400:handoff",
        "certain": "partners:beats:certainmover:for400"}


def job(j):
    from stage2_lang import arms as S
    name, seed, first = j
    lf = P3.make(ARMS[name], seed, first)
    k = {lf.wire_m[th]: g for th, g in ((0, lf.v_a), (1, lf.v_b))}
    S.live(lf, P4.SECS)
    q, b = lf.v_q, lf.brain
    win = []
    for a, z in P4.WINDOWS:
        lo, hi = (q + a) / lf.dt, (q + z) / lf.dt
        good = sum(am for t, bad, am in lf.scored if lo <= t < hi and not bad)
        badm = sum(am for t, bad, am in lf.scored if lo <= t < hi and bad)
        win.append((good - 2.0 * badm) / (z - a) * 10)
    true_lN = [math.log(2 * math.pi / (lf.TURN / lf.DRAG * k[m])) for m in (0, 1)]
    return dict(arm=name, seed=seed, win=win, right=__import__('sigmoid_body').right_knob(k[0], k[1], __import__('table').numbers(seed, {})['drive']), est=getattr(b, "est", None),
                end=getattr(b, "end_lN", None), true=true_lN, beats=getattr(b, "play_beats", None))


def report(rows):
    n = len(rows) // (2 * len(ARMS))
    I = R.boot(n)
    base = np.array([r["win"] for r in rows if r["arm"] == "forage"])
    print("arm      | gain from onset, vs forage [95%]: 0-100 s; 100-300 s | knob error after taste: median, within .2 | "
          "play's best guess: motors within 10% | sure: share of motors; of them wrong by >10%; by a doubled or halved period | play beats")
    for a in ARMS:
        rs = [r for r in rows if r["arm"] == a]
        W = np.array([r["win"] for r in rs])
        line = f"{a:8s}"
        for i in range(2):
            d = W[I, i].mean(1) - base[I, i].mean(1)
            line += f" | {W[:, i].mean() - base[:, i].mean():+.2f} [{np.percentile(d, 2.5):+.2f},{np.percentile(d, 97.5):+.2f}]"
        e = [abs(r["est"] - r["right"]) for r in rs if r["est"] is not None]
        line += f" | {np.median(e):.2f}, {np.mean(np.array(e) < .2):.0%}" if e else " |"
        mot = [(r["end"][m], r["true"][m]) for r in rs if r["end"] for m in (0, 1) if r["end"][m] is not None]
        if mot:
            err = np.array([abs(b[0] - t) for b, t in mot])
            sure = np.array([b[2] >= P3.SURE for b, t in mot])
            slip = np.abs(err - math.log(2)) < 0.15
            line += (f" | {np.mean(err < 0.1):.0%} | {sure.mean():.0%}; {np.mean(err[sure] > 0.1) if sure.any() else float('nan'):.0%}; "
                     f"{np.mean(slip[sure]) if sure.any() else float('nan'):.0%}")
            bt = [r["beats"] for r in rs if r["beats"]]
            line += f" | {np.mean(bt):.0f}"
        print(line, flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    n = int(a[0]) if a and a[0].isdigit() else 20
    s0 = next((int(x[1:]) for x in a if x.startswith("s") and x[1:].isdigit()), 94000)
    out = f"/home/pilgrim/git/simple-learner/lab/v/p1_{n}_s{s0}.pkl"
    out = out.replace(".pkl", "_muscle.pkl") if __import__("os").environ.get("MUSCLE") == "1" else out   # (the new body's lives apart)
    if "report" in a:
        report(pickle.load(open(out, "rb")))
        sys.exit()
    import ledger
    ledger.start()
    jobs = [(arm, s, c) for arm in ARMS for s in range(s0, s0 + n) for c in ("red", "blue")]
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        rows = list(ex.map(job, jobs, chunksize=2))
    pickle.dump(rows, open(out, "wb"))
    report(rows)

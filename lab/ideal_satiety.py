"""ideal_satiety.py: the ideal learner's bits on the satiety ladder, on the same meals as a brain's life (2026-11-15, D67; MacKay's
yardstick: an ideal Bayesian learner with the same evidence). Hypotheses: which colour is the usual food (2), the threshold (1 to 10),
the recovery time (40 values, log-spaced 2 to 70 s): 800, uniform prior (log2 800 = 9.6 bits to name one). Each predicts every meal from
the meals before it (a tally of the usual food colour's meals decaying with the recovery time; at or above the threshold that colour is
poison, else the other), with a 2% slip; the mixture is scored -log2 P(what happened) a meal: its prequential code length. Beside it, the
brain's own bits a taste on the same life.
    .venv/bin/python lab/ideal_satiety.py RUNG ARM SEED0 N"""
import json
import math
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import stage3_random as R
import teach as T
from stage2_lang import arms as S

TAUS = np.exp(np.linspace(np.log(2.0), np.log(70.0), 40))
NS = np.arange(1, 11)
SLIP = 0.02


def ideal(meals):
    """meals: [(t seconds, colour 0/1, poison bool)] -> bits a meal, and the bits named by the end (the posterior's best hypothesis)."""
    H = [(F, n, tau) for F in (0, 1) for n in NS for tau in TAUS]
    logw = np.zeros(len(H))
    bF = np.zeros((2, len(TAUS)))          # the tally for each choice of usual colour, at each recovery time
    tl = None
    bits = 0.0
    for t, c, pois in meals:
        if tl is not None:
            bF *= np.exp(-(t - tl) / TAUS)[None, :]
        tl = t
        pred = np.empty(len(H))
        for i, (F, n, tau) in enumerate(H):
            j = int(np.searchsorted(TAUS, tau))
            pc = F if bF[F, j] >= n - 1e-9 else 1 - F          # the poison colour now
            p_pois = 1 - SLIP if c == pc else SLIP
            pred[i] = p_pois if pois else 1 - p_pois
        w = np.exp(logw - logw.max())
        P = float((w * pred).sum() / w.sum())
        bits -= math.log2(max(P, 1e-12))
        logw += np.log(pred)
        if True:
            bF[c, :] += 1.0                # a meal of colour c adds to the tally of the hypotheses whose usual colour is c
    return bits / max(len(meals), 1)


def bank(meals, taus=(1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0)):
    """The bank's streams at their best: each colour's meal count at each time constant, read exactly to 7 then log (true colours), each
    stream a KT table from (its symbol, the colour eaten) to poison or not; mixed by Bayes. Returns the mixture's bits a meal and the best
    single stream's."""
    S_ = [(c_, tau) for c_ in (0, 1) for tau in taus]
    cnt = {k: 0.0 for k in S_}
    tab = {k: {} for k in S_}
    logw = np.zeros(len(S_))
    bits_s = np.zeros(len(S_))
    bits = 0.0
    tl = None
    for t, c, pois in meals:
        if tl is not None:
            for (c_, tau) in S_:
                cnt[(c_, tau)] *= math.exp(-(t - tl) / tau)
        tl = t
        ps = np.empty(len(S_))
        for i, k in enumerate(S_):
            cr = int(round(cnt[k]))
            sym = cr if cr < 8 else min(8 + int(math.log2(cr / 8.0)), 11)
            h = tab[k].setdefault((sym, c), [0, 0])
            p1 = (h[1] + .5) / (h[0] + h[1] + 1.0)
            ps[i] = p1 if pois else 1 - p1
            h[int(pois)] += 1
        w = np.exp(logw - logw.max())
        bits -= math.log2(float((w * ps).sum() / w.sum()))
        bits_s -= np.log2(ps)
        logw += np.log(ps)
        for k in S_:
            if k[0] == c:
                cnt[k] += 1.0
    n = max(len(meals), 1)
    return bits / n, float(bits_s.min()) / n


def live(lf, seconds=100.0):
    ticks = int(round(seconds / lf.dt))
    while lf.t < ticks:
        lf.step()
    b = lf.brain
    ms = [(t * lf.dt, 0 if col == "red" else 1, sc[1]) for (t, col), sc in zip(lf.meals, lf.scored) if col in ("red", "blue")]
    raise StopIteration((getattr(b, "pbits", 0.0) / max(getattr(b, "ntaste", 1), 1), ideal(ms), len(ms)) + bank(ms))


def one(j):
    S.live = live
    try:
        T.job(j)
    except StopIteration as e:
        return e.value


if __name__ == "__main__":
    n, arm, s0, k = int(sys.argv[1]), sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    d = json.load(open("/home/pilgrim/git/simple-learner/lab/sealed/heldout_ladder2.json"))
    r = next(x for x in d["rungs"] if x["size"] == n)
    jobs = [(r["text"], arm, int(__import__("os").environ.get("P", 2240)), s, c, float(r["seconds"])) for s in range(s0, s0 + k) for c in ("red", "blue")]
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        res = list(ex.map(one, jobs))
    for j, (bb, ib, nm, bm, bs) in zip(jobs, res):
        print(f"seed {j[3]} {j[4]}: meals {nm}; brain {bb:.3f}; ideal {ib:.3f}; bank streams mixed {bm:.3f}, best one {bs:.3f} bits a meal")
    print(f"rung {n}: brain {np.mean([x[0] for x in res]):.3f}, ideal {np.mean([x[1] for x in res]):.3f}, bank mixed "
          f"{np.mean([x[3] for x in res]):.3f}, best bank stream {np.mean([x[4] for x in res]):.3f} bits a taste (means of {len(res)} lives)")

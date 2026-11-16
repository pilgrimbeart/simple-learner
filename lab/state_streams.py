"""state_streams.py: does any stream, or any weighted sum of streams, hold the hidden state? (2026-11-16, D70.) In drift lives, at each
meal in the last two thirds: every stream's prediction for the food colour just before (log-odds, 0 when silent) and the true food
colour. Per stream: bits about the state when it speaks, and how often it speaks. Then an in-sample upper bound for any weighted sum of
the streams' log-odds (logistic regression fitted on all the meals, so flattering), against the ideal filter on the same meals.
    .venv/bin/python lab/state_streams.py RUNG ARM SEED0 N"""
import json
import math
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import stage3_random as R
import teach as T
from drift_filter import Filter
from stage2_lang import arms as S
import grownet
grownet_T = grownet.LB_T


def st(q):
    q = min(max(q, 1e-4), 1 - 1e-4)
    return math.log(q / (1 - q))


def live(lf, seconds=100.0):
    ticks = int(round(seconds / lf.dt))
    b, flt = lf.brain, Filter()
    nm, rows, last = 0, [], None
    while lf.t < ticks:
        lf.step()
        if len(lf.meals) > nm and len(lf.scored) >= len(lf.meals):
            for j in range(nm, len(lf.meals)):
                t, col = lf.meals[j]
                tp = lf.told_now
                if col in ("red", "blue") and tp is not None and tp >= 0 and t * lf.dt > seconds / 3 and last is not None:
                    y = int(lf.wire_s[1 - tp] == 1)
                    pi = flt.p_poison(t * lf.dt)
                    p_food1 = pi[1 - [k for k in (0, 1) if lf.wire_s[k] == 1][0]] if False else None
                    # the ideal's probability that the food eye is 1: the food colour c has eye wire_s[c]; poison colour 1-c
                    pf = sum(pi[1 - c] for c in (0, 1) if lf.wire_s[c] == 1)
                    rows.append((last, y, pf))
                if col in ("red", "blue"):
                    flt.meal(t * lf.dt, 0 if col == "red" else 1, lf.scored[j][1])
            nm = len(lf.meals)
        if b.byk is not None and lf.t % 20 == 0:          # every 50 ms, the streams' current log-odds for letter 1
            v = {}
            for N in b.nets:
                k, _ = N.says(b.place(N) - 1)
                v[N.kind] = st(b._pk(N, k, 1)) if k is not None else 0.0
            v["_def"] = st(b._pdef(1))
            for (ln, j), (r_, tr_) in getattr(b, "lbr", {}).items():   # the raw signed evidence sums, read directly (no stream readout)
                if ln == "ld":
                    v[f"RAW_ld{j}"] = r_ * math.exp(-(b.t - tr_) / grownet_T[j]) + 1e-9
            last = v
    raise StopIteration(rows)


def one(j):
    S.live = live
    try:
        T.job(j)
    except StopIteration as e:
        return e.value


def bits(p, y):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return float(np.mean(-np.log2(np.where(y == 1, p, 1 - p))))


if __name__ == "__main__":
    n, arm, s0, k = int(sys.argv[1]), sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    d = json.load(open("/home/pilgrim/git/simple-learner/lab/sealed/heldout_ladder3.json"))
    r = next(x for x in d["rungs"] if x["size"] == n)
    jobs = [(r["text"], arm, 2240, s, c, float(r["seconds"])) for s in range(s0, s0 + k) for c in ("red", "blue")]
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        res = list(ex.map(one, jobs))
    life_of = np.array([i for i, life in enumerate(res) for _ in life])
    rows = [x for life in res for x in life]
    keys = sorted({kk for v, _, _ in rows for kk in v})
    X = np.array([[v.get(kk, 0.0) for kk in keys] for v, _, _ in rows])
    y = np.array([yy for _, yy, _ in rows])
    pid = np.array([p for _, _, p in rows])
    print(f"rung {n}, {arm}: {len(rows)} meals; ideal filter {bits(pid, y):.3f} bits about the state a meal; knowing nothing 1")
    per = []
    for j, kk in enumerate(keys):
        on = X[:, j] != 0.0
        if on.sum() >= 50:
            per.append((bits(1 / (1 + np.exp(-X[on, j])), y[on]), on.mean(), kk))
    per.sort()
    acc = sorted(((float(np.mean((X[X[:, j] != 0, j] > 0) == (y[X[:, j] != 0] == 1))), kk) for j, kk in enumerate(keys)
                  if (X[:, j] != 0).sum() >= 50), reverse=True)
    print(f"  choosing by each stream's own sign, share of meals right (the ideal filter: {float(np.mean((pid > .5) == (y == 1))):.2f}):")
    for a_, kk in acc[:8]:
        print(f"    {kk:14s} {a_:.2f}")
    print("    raw evidence sums:", [(kk, round(a_, 2)) for a_, kk in acc if kk.startswith("RAW")])
    print("  best single streams when they speak (bits, share of meals spoken at):")
    for b_, c_, kk in per[:10]:
        print(f"    {kk:14s} {b_:.3f}  {c_:.2f}")
    # in-sample logistic regression on all streams' log-odds (L2, Newton steps): a flattering upper bound for any weighted sum
    Xb = np.hstack([X, np.ones((len(X), 1))])
    w = np.zeros(Xb.shape[1])
    lam = 1.0
    for _ in range(30):
        p = 1 / (1 + np.exp(-np.clip(Xb @ w, -30, 30)))
        g = Xb.T @ (p - y) + lam * w
        Hm = (Xb * (p * (1 - p))[:, None]).T @ Xb + lam * np.eye(len(w))
        w -= np.linalg.solve(Hm, g)
    p = 1 / (1 + np.exp(-np.clip(Xb @ w, -30, 30)))
    print(f"  best weighted sum of all {len(keys)} streams' log-odds, fitted in-sample: {bits(p, y):.3f} bits a meal")
    def fit(Xt, yt, lam):
        w = np.zeros(Xt.shape[1])
        for _ in range(30):
            p = 1 / (1 + np.exp(-np.clip(Xt @ w, -30, 30)))
            g = Xt.T @ (p - yt) + lam * w
            Hm = (Xt * (p * (1 - p))[:, None]).T @ Xt + lam * np.eye(len(w))
            w -= np.linalg.solve(Hm, g)
        return w
    for lam in (1.0, 30.0, 300.0):                       # honest: leave one life out, for every life
        pcv = np.empty(len(y))
        for L_ in np.unique(life_of):
            tr, te = life_of != L_, life_of == L_
            wv = fit(Xb[tr], y[tr], lam)
            pcv[te] = 1 / (1 + np.exp(-np.clip(Xb[te] @ wv, -30, 30)))
        print(f"  weighted sum, one life left out each time (L2 {lam:g}): {bits(pcv, y):.3f} bits a meal")
    top = np.argsort(-np.abs(w[:-1]))[:8]
    print("  its largest weights:", [(keys[j], round(float(w[j]), 2)) for j in top])

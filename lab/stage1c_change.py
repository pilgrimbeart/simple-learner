"""stage1c_change.py: stage 1c part 2. Ideal learners that allow change.

  replay   2(a) on recorded streams: the exact fixed-share posterior over the seven, against the bank, in false picks, right picks and agreement; the hazard each world's stream supports, in bits; the hazard a floor implies.
  fslives  2(a) in real lives: settings swept on 61000-61063 x 2, judged on 62000-62199 x 2.
  hmm      2(b): real lives driven by mixtures holding a changing rule (lab/stage1c_arms.py, Mix); swept on 61000+, judged on 62000+.

Likelihood, as in lab/stage1c_arms.py: P(scored taste says colour c | hypothesis predicts c) = 1-e, independent. Fixed share: each scored taste, with chance h the model is redrawn from pi. Replay is exact because each model's prediction is a function of the stream, and the stream's factor from the policy cancels (D31). On the pinned stream a first pick is exact for any selector; agreement is measured on the bank's own stream.

    .venv/bin/python lab/stage1c_change.py replay|fslives|hmm"""
import json
import pickle
import sys
import time
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np
import bits_analyse as BA
import bits_arms as BAr
import bits_bank as B
import stage1c_arms as A

BA.D = A.OUT
W = BA.WORLDS
RIGHT = BA.RIGHT
DEFAULTS = [w for w in W if RIGHT[w] == {0}]
RIVALS = ("swap10", "alternate", "pattern")
TUNE, JUDGE = range(61000, 61064), range(62000, 62200)
HS = (0.0, 1e-4, 3e-4, 1e-3, 3e-3, 0.01, 0.03, 0.1, 0.2, 0.4)
ES = (0.025, 0.05, 0.1, 0.2, 0.3)
PRS = (1 / 7, 0.5, 0.9)
GRID = [(h, e, pr) for h in HS for e in ES for pr in PRS]
BOOT = 1000


def fs_map(t, H, grid):
    """Fixed share, exact, per taste and setting: the MAP model after each taste (n, G), ties to the lowest index; and the log2 predictive of the stream (the evidence), per setting. Each taste the model may move first, then the taste is seen."""
    h = np.array([g[0] for g in grid])[:, None]
    e = np.array([g[1] for g in grid])[:, None]
    pr = np.array([g[2] for g in grid])
    pi = np.column_stack((pr, *[(1 - pr) / 6] * 6))
    w = pi.copy()
    n = len(t)
    out = np.zeros((n, len(grid)), dtype=np.int8)
    ev = np.zeros(len(grid))
    for i in range(n):
        w = (1 - h) * w + h * pi
        w = w * (H[i] * (1 - e) + (1 - H[i]) * e)
        s = w.sum(1, keepdims=True)
        ev += np.log2(s[:, 0])
        w = w / s
        out[i] = np.round(w, 12).argmax(1)              # (rounded: an exact tie goes to the lower index whatever the round-off)
    return out, ev


def firsts_of(mp, t, right):
    """For one setting's MAP path: first rival time, first right-rival time."""
    a = np.flatnonzero(mp > 0)
    fa = t[a[0]] if len(a) else np.inf
    fb = np.inf
    if right:
        b = np.flatnonzero(np.isin(mp, list(right)))
        fb = t[b[0]] if len(b) else np.inf
    return fa, fb


def bank_path(t, H, **kw):
    """The bank's counters replayed: act after each scored taste (bits_analyse.replay_ctr logic)."""
    picks = BA.replay_ctr(t, H, **kw)
    act = np.zeros(len(t), dtype=np.int8)
    for tt, m in picks:
        act[np.searchsorted(t, tt):] = m
    return act


def boot_ratio(num, den, seed=0):
    """Ratio of sums, bootstrapped over seeds (a seed's two lives together)."""
    I = A.resample(len(num), BOOT, seed)
    v = num[I].sum(1) / np.maximum(den[I].sum(1), 1e-9)
    return num.sum() / max(den.sum(), 1e-9), np.percentile(v, 2.5), np.percentile(v, 97.5)


def load_streams(lo):
    bank, pinned = BA.load("bank", lo), BA.load("pinned", lo)
    return {w: [BA.stream(l)[:2] for l in bank[w]] for w in W}, {w: [BA.stream(l)[:2] for l in pinned[w]] for w in W}


def analyse(Sb, Sp, grid, label):
    """Per world, per setting: false-pick share (default-right worlds) or right share and median time (others), on the pinned stream; agreement with the bank on the bank's stream."""
    t0 = time.time()
    G = len(grid)
    res = {}
    for w in W:
        fa = np.full((len(Sp[w]), G), np.inf)
        fb = np.full((len(Sp[w]), G), np.inf)
        ev = np.zeros((len(Sp[w]), G))
        for i, (t, H) in enumerate(Sp[w]):
            m, ev[i] = fs_map(t, H, grid)
            for g in range(G):
                fa[i, g], fb[i, g] = firsts_of(m[:, g], t, RIGHT[w] if RIGHT[w] != {0} else None)
        # the bank on the same pinned stream
        bfa, bfb = [], []
        for t, H in Sp[w]:
            a, b = BA.firsts(BA.replay_ctr(t, H), RIGHT[w])
            bfa.append(a)
            bfb.append(b)
        bfa, bfb = np.array(bfa), np.array(bfb)
        # agreement on the bank's own stream: same model and same next prediction, tastes where either is on a rival
        inter = np.zeros((len(Sb[w]), G))
        union = np.zeros((len(Sb[w]), G))
        pred_same = np.zeros((len(Sb[w]), G))
        all_same = np.zeros((len(Sb[w]), G))
        nall = np.zeros(len(Sb[w]))
        evb = np.zeros((len(Sb[w]), G))
        for i, (t, H) in enumerate(Sb[w]):
            act = bank_path(t, H)
            m, evb[i] = fs_map(t, H, grid)
            A_ = (act > 0)[:, None]
            B_ = m > 0
            U_ = A_ | B_
            union[i] = U_.sum(0)
            inter[i] = ((m == act[:, None]) & U_).sum(0)
            if len(t) > 1:
                ha = H[np.arange(1, len(t)), act[:-1]]
                hb = np.take_along_axis(H[1:], m[:-1].astype(int), 1)
                same = hb == ha[:, None]
                pred_same[i] = (same & U_[:-1]).sum(0)
                all_same[i] = same.sum(0)
                nall[i] = len(t) - 1
        res[w] = dict(fa=fa, fb=fb, bfa=bfa, bfb=bfb, ev=ev, evb=evb, inter=inter, union=union, pred_same=pred_same, all_same=all_same, nall=nall, n=[len(t) for t, _ in Sp[w]])
        print(f"   {label} {w} done [{time.time() - t0:.0f} s]", flush=True)
    return res


def row(res, g):
    """Pooled measures for setting g."""
    o = {}
    for w in DEFAULTS:
        o[w] = np.isfinite(res[w]["fa"][:, g]).mean()
    for w in RIVALS:
        f = res[w]["fb"][:, g]
        o[w] = np.median(np.minimum(f, 1e9))
    return o


def compare(res, g, n_rival_weight=10.0):
    """Squared distance from the bank: false picks in the default-right worlds, right pick's median time / 10 in the others."""
    d = 0.0
    for w in DEFAULTS:
        d += (np.isfinite(res[w]["fa"][:, g]).mean() - np.isfinite(res[w]["bfa"]).mean()) ** 2
    for w in RIVALS:
        d += ((min(np.median(res[w]["fb"][:, g]), 100) - min(np.median(res[w]["bfb"]), 100)) / n_rival_weight) ** 2
    return d


def pooled_j(res, g, worlds, pred=False):
    a, b = [], []
    for w in worlds:
        n = res[w]["pred_same" if pred else "inter"][:, g]
        u = res[w]["union"][:, g]
        a.append(n)
        b.append(u)
    return np.concatenate(a), np.concatenate(b)


def replay():
    print("== 2(a) the hazard a floor implies. A rival's odds against the default under fixed share: O -> (1-h)O + h r, for small O (r the rival's share of a redraw). So the odds cannot fall below about h r: a soft floor at log2(h r) bits. A floor at 0 with threshold theta counters of u bits each: the distance from floor to the MAP's boundary is theta u = log2(1 / (h r)), so h r = 2^(-theta u). u = log2((1-e)/e) if the counter's unit is one hit at lie rate e.", flush=True)
    print("   e | u bits | h r at theta 2 (1/0) | h r at theta 3 (sequences) | total hazard a taste (1/0 + 5 sequences) | mean scored tastes between changes | seconds at 0.63 tastes a s")
    for e, u in ((0.235, None), (0.2, None), (0.1, None), (0.05, None), (0.025, None)):
        u = np.log2((1 - e) / e)
        h2, h3 = 2 ** (-2 * u), 2 ** (-3 * u)
        tot = h2 + 5 * h3
        print(f"   {e} | {u:.2f} | {h2:.5f} | {h3:.5f} | {tot:.5f} | {1 / tot:.1f} | {1 / tot / 0.63:.1f}")
    print("   So the setting of the hazard depends on which lie rate a counter's unit is read at; at the measured +1 of about 1.7 bits (D31), e .235, a total hazard of 0.24 a taste. No single h matches a counter across worlds whose lie rates differ, since a counter's step doesn't change with e, while a Bayesian's does.", flush=True)

    Sb, Sp = load_streams(61000)
    print(f"\n== tuning streams 61000-61063 x 2: {len(GRID)} settings (h, e, pi of default)", flush=True)
    res = analyse(Sb, Sp, GRID, "tune")
    ds = [compare(res, g) for g in range(len(GRID))]
    order = np.argsort(ds)
    print("   the settings closest to the bank by false picks and right-pick times (tuning):")
    for g in order[:8]:
        print(f"   {GRID[g]} distance {ds[g]:.4f} " + " ".join(f"{k[:5]} {v:.2f}" for k, v in row(res, g).items()), flush=True)
    jd = [boot_ratio(*pooled_j(res, g, W, True))[0] for g in range(len(GRID))]
    best_j = int(np.argmax(jd))
    print(f"   the setting with most agreement (same next prediction, tastes where either is on a rival, tuning): {GRID[best_j]} {jd[best_j]:.3f}")
    closest = int(order[0])
    # the best stationary (h=0) by the same distance
    stat = [g for g in range(len(GRID)) if GRID[g][0] == 0.0]
    closest0 = min(stat, key=lambda g: ds[g])
    best_j0 = max(stat, key=lambda g: jd[g])
    chosen = dict(closest=GRID[closest], closest0=GRID[closest0], best_j=GRID[best_j], best_j0=GRID[best_j0])
    print("   chosen on tuning, then judged on fresh seeds:", chosen, flush=True)

    Sb, Sp = load_streams(62000)
    print("\n== fresh streams 62000-62399 x 2, chosen settings, plus implied ones", flush=True)
    grid2 = [chosen["closest"], chosen["closest0"], chosen["best_j"], chosen["best_j0"], (0.095 * 6 * 2, 0.235, 0.5), (0.095, 0.235, 0.5), (0.03, 0.2, 0.5), (0.01, 0.1, 0.5), (0.003, 0.05, 0.5), (0.0, 0.2, 0.5), (0.0, 0.1, 0.5), (0.0, 0.05, 0.5)]
    grid2 = [(min(a, 1.0), b, c) for a, b, c in grid2]
    res2 = analyse(Sb, Sp, grid2, "fresh")
    print("   setting: then per world, false picks [95%] (bank's alongside), or right pick's median time", flush=True)
    print("   bank replay: " + " ".join(f"{w[:5]} {np.isfinite(res2[w]['bfa']).mean():.3f}" for w in DEFAULTS) + " | " + " ".join(f"{w[:5]} {np.median(res2[w]['bfb']):.1f}s" for w in RIVALS), flush=True)
    for g, s in enumerate(grid2):
        out = []
        for w in DEFAULTS:
            x = np.isfinite(res2[w]["fa"][:, g]).astype(float)
            b, lo, hi = boot_ratio(x, np.ones_like(x))
            out.append(f"{w[:5]} {b:.3f} [{lo:.3f},{hi:.3f}]")
        out2 = [f"{w[:5]} {np.median(res2[w]['fb'][:, g]):.1f}s ({np.isfinite(res2[w]['fb'][:, g]).mean():.2f})" for w in RIVALS]
        j = boot_ratio(*pooled_j(res2, g, W))
        jp = boot_ratio(*pooled_j(res2, g, W, True))
        jd_ = boot_ratio(*pooled_j(res2, g, DEFAULTS, True))
        ag = sum(res2[w]["all_same"][:, g].sum() for w in W) / sum(res2[w]["nall"].sum() for w in W)
        print(f"   {tuple(round(x, 4) for x in s)}: " + " ".join(out) + " | " + " ".join(out2) + f" | same model when either on a rival {j[0]:.3f} [{j[1]:.3f},{j[2]:.3f}], same prediction {jp[0]:.3f} [{jp[1]:.3f},{jp[2]:.3f}], in the default-right worlds {jd_[0]:.3f}, all tastes {ag:.3f}", flush=True)
    print("\n   paired on fresh seeds: fixed-share closest minus stationary closest in agreement (same prediction, either on a rival; tastes pooled over worlds):", flush=True)
    a1, u1 = pooled_j(res2, 0, W, True)
    a0, u0 = pooled_j(res2, 1, W, True)
    I = A.resample(len(a1), BOOT)
    dv = a1[I].sum(1) / u1[I].sum(1) - a0[I].sum(1) / u0[I].sum(1)
    print(f"   {a1.sum() / u1.sum() - a0.sum() / u0.sum():+.3f} [{np.percentile(dv, 2.5):+.3f},{np.percentile(dv, 97.5):+.3f}]", flush=True)
    print("\n   does a life's pick go with the bank's? phi coefficient of 'a rival was picked in this life', default-right worlds, and share of the bank's false-pick lives also picked by this learner:", flush=True)
    for g, s in enumerate(grid2[:4]):
        out = []
        for w in DEFAULTS:
            x, y = np.isfinite(res2[w]["fa"][:, g]), np.isfinite(res2[w]["bfa"])
            phi = np.corrcoef(x, y)[0, 1] if x.std() and y.std() else float("nan")
            out.append(f"{w[:5]} phi {phi:.2f}, shared {x[y].mean() if y.any() else 0:.2f}")
        print(f"   {tuple(round(x, 4) for x in s)}: " + " | ".join(out), flush=True)
    print("\n   false picks by life length (first pick before 33, 66, 100 s), unreliable, digest, patchy. A floor's grow with the length, a stationary learner's saturate (D31):", flush=True)
    for w in ("unreliable", "digest", "patchy"):
        out = [f"bank {' '.join(f'{(res2[w]['bfa'] < c).mean():.3f}' for c in (33, 66, 100))}"]
        for g, s in enumerate(grid2[:2]):
            out.append(f"{tuple(round(x, 4) for x in s)} {' '.join(f'{(res2[w]['fa'][:, g] < c).mean():.3f}' for c in (33, 66, 100))}")
        print(f"   {w}: " + " | ".join(out), flush=True)
    print("\n   picks by threshold: bank replay at theta 1,2,3,4 against fixed share at the implied h at e = .235 (u = 1.7), and at the h with the same false picks (scan of h, e .2, pi .5), on the pinned stream:", flush=True)
    scan = [(h, 0.2, 0.5) for h in (0.0, 1e-3, 3e-3, 0.01, 0.03, 0.06, 0.1, 0.2, 0.4, 0.7, 1.0)]
    res3 = analyse(Sb, Sp, scan, "scan")
    for th in (1, 2, 3, 4):
        out = []
        for w in ("unreliable", "digest", "patchy"):
            fp = np.mean([np.isfinite(BA.firsts(BA.replay_ctr(t, H, theta=th), {0})[0]) for t, H in Sp[w]])
            out.append(f"{w[:5]} {fp:.3f}")
        print(f"   bank theta {th}: " + " ".join(out))
    for g, s in enumerate(scan):
        print(f"   fixed share h {s[0]}, e {s[1]}: " + " ".join(f"{w[:5]} {np.isfinite(res3[w]['fa'][:, g]).mean():.3f}" for w in ("unreliable", "digest", "patchy", "plain", "weak", "noisy")) + " | " + " ".join(f"{w[:5]} {np.median(res3[w]['fb'][:, g]):.1f}s" for w in RIVALS))

    print("\n== which hazard does each world's stream support? log2 evidence per life relative to h = 0 at the same e and pi (.5), on the pinned stream and the bank's stream (fresh seeds). Positive: the stream favours change. Exact under the stated likelihood.", flush=True)
    evg = [(h, e, 0.5) for h in HS for e in ES]
    res4 = analyse(Sb, Sp, evg, "evidence")
    for src, key in (("bank's stream", "evb"), ("pinned", "ev")):
        print(f"   -- {src}")
        for w in W:
            ev = res4[w][key]
            bg = int(np.argmax(ev.mean(0)))
            e_best = evg[bg][1]
            ids = [i for i, s in enumerate(evg) if s[1] == e_best]
            base = ids[0]
            out = []
            for i in ids:
                d = ev[:, i] - ev[:, base]
                I = A.resample(len(d), BOOT)
                v = d[I].mean(1)
                out.append(f"h{evg[i][0]:g}: {d.mean():+.1f}[{np.percentile(v, 2.5):+.1f},{np.percentile(v, 97.5):+.1f}]")
            print(f"   {w:10s} best e {e_best} best h {evg[bg][0]:g}, {ev.mean(0)[bg] / max(np.mean(res4[w]['n']), 1):.3f} bits a taste | " + " ".join(out), flush=True)
    print(f"[{time.time()}]", flush=True)


def fslives():
    print("== 2(a) fixed share in real lives. Swept on 61000-61063 x 2 by the search's own score, as 1b; judged on 62000-62199 x 2 against the bank and 1b's one setting.", flush=True)
    t0 = time.time()
    base = {w: B.run_plain(w, "circuit", TUNE) for w in W}
    bank = {w: A.run(w, "v_rec", TUNE) for w in W}
    print("bank score", round(BAr.recovery(bank, base), 3), flush=True)
    settings = [(arm, dict(h=h, eps=e, pr=0.6)) for arm in ("fsmap", "fsbma") for h in (0.003, 0.01, 0.03, 0.1) for e in (0.1, 0.2)]
    res = {}
    for arm, kw in settings:
        res[(arm, json.dumps(kw))] = {w: A.run(w, arm, TUNE, kw) for w in W}
        r = res[(arm, json.dumps(kw))]
        print(BAr.name(arm, kw) + " " + " ".join(f"{w[:5]} {A.efficiency(r[w]):.2f}" for w in W) + f" score {BAr.recovery(r, base):.3f} [{time.time() - t0:.0f} s]", flush=True)
    one = max(res, key=lambda k: BAr.recovery(res[k], base))
    pw = {w: max(res, key=lambda k: A.efficiency(res[k][w])) for w in W}
    print("one setting:", one, flush=True)
    print("per world:", {w: pw[w] for w in W}, flush=True)
    with open(A.OUT + "fs_chosen.json", "w") as f:
        json.dump(dict(one=one), f)
    print("\n== judged, 62000-62199 x 2", flush=True)
    for w in W:
        bk = A.run(w, "v_rec", JUDGE)
        o = A.run(w, one[0], JUDGE, json.loads(one[1]))
        b1 = A.run(w, "bma", JUDGE, dict(eps=0.2, pr=0.5))
        p = A.run(w, pw[w][0], JUDGE, json.loads(pw[w][1]))
        print(f"{w}: bank {A.efficiency(bk):.3f}; fixed share one setting {A.efficiency(o):.3f}, against bank {A.fmt_d(A.pdiff(o, bk))}, against 1b's one Bayes setting {A.fmt_d(A.pdiff(o, b1))}; this world's best {A.efficiency(p):.3f}, against bank {A.fmt_d(A.pdiff(p, bk))} [{time.time() - t0:.0f} s]", flush=True)


LAMS = (0.02, 0.05, 0.1, 0.2, 0.5, 1.0)
LGRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0]        # a learner not given the rate: 3 bits


def hmm():
    t0 = time.time()
    print("== 2(b) sweep, swap10, 61000-61063 x 2: HMM alone, rate and lie rate (a learner given the true kind of change, so flattered)", flush=True)
    best, bv = None, -9
    for lam in LAMS:
        out = []
        for e in (0.03, 0.1, 0.2):
            v = A.efficiency(A.run("swap10", "mix", TUNE, dict(eps=e, sh=1.0, lams=[lam])))
            out.append(f"e {e}: {v:.3f}")
            if v > bv:
                best, bv = (lam, e), v
        print(f"   lam {lam}: " + " ".join(out) + f" [{time.time() - t0:.0f} s]", flush=True)
    lam, e = best
    print(f"   chosen: lam {lam}, e {e} (true rate of swaps 0.1 a s)", flush=True)
    e7 = 0.1
    ARMS = {
        "HMM, rate and e chosen": (dict(eps=e, sh=1.0, lams=[lam]), lambda p: A.prior_bits(p, "hmm")),
        "HMM, rate 5x too low": (dict(eps=e, sh=1.0, lams=[0.02]), None),
        "HMM, rate 5x too high": (dict(eps=e, sh=1.0, lams=[0.5]), None),
        "HMM, rate unknown (8 rates)": (dict(eps=e, sh=1.0, lams=LGRID), lambda p: A.prior_bits(p, "hmm")),
        "HMM + seven": (dict(eps=e, sh=0.5, s7=0.5, lams=[lam], pr=0.6), lambda p: A.prior_bits(p, "hmm")),
        "HMM rate unknown + seven": (dict(eps=e, sh=0.5, s7=0.5, lams=LGRID, pr=0.6), lambda p: A.prior_bits(p, "hmm")),
        "period known, T10 phase 0": (dict(eps=e, sp=1.0, fam="T10"), lambda p: A.prior_bits(p)),
        "4 periods, phase 0": (dict(eps=e, sp=1.0, fam="T4"), lambda p: A.prior_bits(p)),
        "64 periods, phase 0": (dict(eps=e, sp=1.0, fam="T64"), lambda p: A.prior_bits(p)),
        "64 periods, 16 phases": (dict(eps=e, sp=1.0, fam="T64P16"), lambda p: A.prior_bits(p)),
        "393 periods at 1%, 16 phases": (dict(eps=e, sp=1.0, fam="T393P16"), lambda p: A.prior_bits(p)),
        "393 periods, 64 phases": (dict(eps=e, sp=1.0, fam="T393P64"), lambda p: A.prior_bits(p)),
        "393 periods, 16 phases + HMMs + seven": (dict(eps=e, sp=1 / 3, sh=1 / 3, s7=1 / 3, fam="T393P16", lams=LGRID, pr=0.6), lambda p: A.prior_bits(p)),
        "T10 only + HMMs + seven": (dict(eps=e, sp=1 / 3, sh=1 / 3, s7=1 / 3, fam="T10", lams=LGRID, pr=0.6), lambda p: A.prior_bits(p)),
    }
    print(f"\n== 2(b) judged, 62000-62199 x 2. Efficiency, against the bank and against 1/0 from birth. Prior bits: -log2 of the weight the learner's prior puts on the true hypothesis, uniform within groups. They don't count the choice of family itself.", flush=True)
    for w in ("swap10", "swap7", "swap20"):
        bk = A.run(w, "v_rec", JUDGE)
        fx = A.run(w, "fix", JUDGE, dict(fix=1.0))
        told = A.run(w, "vtold", JUDGE)
        print(f"-- {w}: bank {A.efficiency(bk):.3f}; 1/0 from birth {A.efficiency(fx):.3f}; told {A.efficiency(told):.3f}; told - birth {A.fmt_d(A.pdiff(told, fx))} [{time.time() - t0:.0f} s]", flush=True)
        for name, (kw, pb) in ARMS.items():
            L = A.run(w, "mix", JUDGE, kw)
            bits = f"{pb(kw):.1f} bits" if pb and w == "swap10" else ""
            share = (A.efficiency(L) - A.efficiency(fx)) / (A.efficiency(told) - A.efficiency(fx))
            first = np.mean([np.sum(l.mbad[l.mt < 1000]) for l in L])
            print(f"   {name}: {A.efficiency(L):.3f}, against 1/0 from birth {A.fmt_d(A.pdiff(L, fx))}, told - this {A.fmt_d(A.pdiff(told, L))}, share of told - birth recovered {share:.2f}, {bits} [{time.time() - t0:.0f} s]", flush=True)
    print("\n== controls: the stationary worlds. Each arm against the bank and against 1b's one Bayes setting", flush=True)
    C = {"HMM, rate and e chosen": ARMS["HMM, rate and e chosen"][0], "HMM rate unknown + seven": ARMS["HMM rate unknown + seven"][0], "393 periods, 16 phases + HMMs + seven": ARMS["393 periods, 16 phases + HMMs + seven"][0]}
    for w in ("plain", "alternate", "pattern", "digest", "unreliable", "patchy", "weak", "noisy"):
        bk = A.run(w, "v_rec", JUDGE)
        b1 = A.run(w, "bma", JUDGE, dict(eps=0.2, pr=0.5))
        told = A.run(w, "vtold", JUDGE)
        print(f"-- {w}: bank {A.efficiency(bk):.3f}, one Bayes {A.efficiency(b1):.3f}, told {A.efficiency(told):.3f} [{time.time() - t0:.0f} s]", flush=True)
        for name, kw in C.items():
            L = A.run(w, "mix", JUDGE, kw)
            print(f"   {name}: {A.efficiency(L):.3f}, against bank {A.fmt_d(A.pdiff(L, bk))}, against one Bayes {A.fmt_d(A.pdiff(L, b1))}", flush=True)


if __name__ == "__main__":
    dict(replay=replay, fslives=fslives, hmm=hmm)[sys.argv[1]]()

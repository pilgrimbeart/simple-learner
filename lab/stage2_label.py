"""stage2_label.py: each world's labels in bits, before any circuit's efficiency is read (PROGRAMME.md; D31, D32's methods; lab/v/stage2a_predictions.md, D6, for the classes). Bank's scored tastes on 63200-63249 x 2; first differences on 63300-63319 x 2 under three policies. Writes lab/v/stage2_labels.log and a pickle. No efficiency is printed.

Each world: e, the chance a scored taste misstates the rule's food colour; rho, the share of scored tastes on which the rule's food colour isn't the life's majority one; n, scored tastes a second; bits a taste 1 - H(e), bits a life; D, the evidence a life gives against plain's tastes, n [rho (1-2e) log2((1-e)/e) + KL(e||e_plain)], at this rate; rate evidence, Poisson KL of mean eye and taste rates against plain's (an estimate, a lower bound on what the wires carry: means only); first difference on the wires against plain's life on the same seed, median and 90th percentile, under base, bank and unwired, and the share of lives where none showed.

    .venv/bin/python lab/stage2_label.py"""
import gc
import math
import pickle
import sys
import time
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import bits_bank as B
from stage2_lang import arms as S, lang, worlds as WW
from stage2_run import guard, OUT

SEEDS = range(63200, 63250)
FD_SEEDS = range(63300, 63320)
I = {c: B.COLS.index(c) for c in B.COLS}
WALD = 3.82                                             # bits: Wald's limit for one pair at 5% each way, (1 - 2a) log2((1 - a) / a)


def h2(e):
    return 0.0 if e <= 0 or e >= 1 else -(e * math.log2(e) + (1 - e) * math.log2(1 - e))


def kl2(a, b):
    a, b = min(max(a, 1e-9), 1 - 1e-9), min(max(b, 1e-9), 1 - 1e-9)
    return a * math.log2(a / b) + (1 - a) * math.log2((1 - a) / (1 - b))


def rec(job):
    text, seed, first = job
    l = S.live(S.make(S.world_of(text), "bank", seed, first))
    return np.asarray(l.rows, dtype=np.float32)


def stats(rows):
    """Per life: scored, errors, minority-share counts, of tastes with a stated colour."""
    out = []
    for x in rows:
        s = x[x[:, I["scored"]] > 0] if len(x) else x
        n = len(s)
        if n == 0:
            out.append((0, 0, 0, 0))
            continue
        Y = np.where(s[:, I["value"]] > 0, s[:, I["followed"]], 1 - s[:, I["followed"]])
        F = s[:, I["F"]]
        ok = F >= 0
        err = int((Y[ok] != F[ok]).sum())
        c = np.bincount(F[ok].astype(int), minlength=2)
        out.append((n, err, int(c.min()) if ok.any() else 0, int(ok.sum())))
    return np.array(out, dtype=float)


def summarise(st, e_plain, boot=2000):
    """(n per life, e, rho, bits a taste, bits a life, D) and intervals over seed pairs."""
    g = np.random.default_rng(0)
    pairs = len(st) // 2
    k = g.integers(0, pairs, (boot, pairs))
    idx = np.concatenate((2 * k, 2 * k + 1), axis=1)

    def f(a):
        n, err, mino, ok = a[..., 0].sum(-1), a[..., 1].sum(-1), a[..., 2].sum(-1), a[..., 3].sum(-1)
        with np.errstate(invalid="ignore", divide="ignore"):
            e = err / ok
            rho = mino / ok
        return n / a.shape[-2], e, rho
    n0, e0, rho0 = f(st)
    nb, eb, rb = f(st[idx])
    fn = lambda n, e, r: (n * (1 - h2(e)), n * (r * (1 - 2 * e) * math.log2((1 - e) / max(e, 1e-9)) + kl2(e, e_plain)))
    if not np.isfinite(e0):
        return dict(n=n0, e=None, rho=None, bt=None, bl=None, D=0.0, ci={})
    bl0, D0 = fn(n0, float(e0), float(rho0))
    B_ = np.array([fn(a, float(b), float(c)) for a, b, c in zip(nb, eb, rb)])
    return dict(n=n0, e=float(e0), rho=float(rho0), bt=1 - h2(float(e0)), bl=bl0, D=D0, ci=dict(e=np.percentile(eb, [2.5, 97.5]), rho=np.percentile(rb, [2.5, 97.5]), bl=np.percentile(B_[:, 0], [2.5, 97.5]), D=np.percentile(B_[:, 1], [2.5, 97.5])))


def wire(job):
    """The wires of a life: what the brain receives."""
    text, arm, seed, first = job
    lf = S.make(S.world_of(text), arm, seed, first, trace=True)
    S.live(lf)
    p = np.array([(t, e, at) for t, e, c, at, ok in lf.tr.pulses if ok], dtype=float).reshape(-1, 3)
    tt = np.array([(t, v, at) for t, v, at, src in lf.tr.tastes if src >= 0], dtype=float).reshape(-1, 3)
    rates = [int((p[:, 1] == 0).sum()), int((p[:, 1] == 1).sum()), int((tt[:, 1] > 0).sum()), int((tt[:, 1] < 0).sum())]
    del lf
    gc.collect()                                        # (a trace is many small tuples in a cycle through the brain: seven workers holding them ran out of memory, once)
    return p, tt, rates


def first_diff(a, b):
    """The first tick the wires differ, or None."""
    pa, ta, _ = a
    pb, tb, _ = b
    best = None
    for x, y in ((pa, pb), (ta, tb)):
        m = min(len(x), len(y))
        d = np.flatnonzero((x[:m] != y[:m]).any(1))
        if len(d) or len(x) != len(y):
            i = int(d[0]) if len(d) else m
            t = int(min(x[i, 0] if i < len(x) else 1 << 60, y[i, 0] if i < len(y) else 1 << 60))
            best = t if best is None else min(best, t)
    return best


def rate_kl(R, R0, boot=1000):
    """Poisson KL in bits a life from mean rates of each eye (sorted within a life, since which eye is which is drawn) and of good and bad tastes, a feature counted only where the paired difference's 95% interval excludes 0."""
    def feats(r):
        r = np.array(r, dtype=float)
        return np.column_stack((r[:, :2].max(1), r[:, :2].min(1), r[:, 2], r[:, 3]))
    a, b = feats(R), feats(R0)
    pairs = len(a) // 2
    g = np.random.default_rng(1)
    k = g.integers(0, pairs, (boot, pairs))
    idx = np.concatenate((2 * k, 2 * k + 1), axis=1)
    d = (a - b)[idx].mean(1)
    lo, hi = np.percentile(d, [2.5, 97.5], axis=0)
    tot = 0.0
    for j in range(4):
        l1, l0 = a[:, j].mean(), b[:, j].mean()
        if (lo[j] > 0 or hi[j] < 0) and l0 > 0 and l1 > 0:
            tot += l1 * math.log2(l1 / l0) - (l1 - l0) / math.log(2)
    return tot


def classify(name, L, none_share, rate_bits, w):
    e, ci = L["e"], L["ci"]
    if none_share >= 1.0:
        return "A", "no difference on the wires in any life under three policies"
    if name == "mirror":
        return "A", "by symmetry: wiring of thruster to motor is drawn anyway; see its check"
    if e is None:
        return "A", "no colour is ever the rule's: nothing to learn"
    if ci["e"][1] >= 0.49:
        return "A", "a taste says nothing of the colour (e reaches .49)"
    if L["D"] + rate_bits < WALD:
        return "B", f"evidence {L['D'] + rate_bits:.1f} bits below Wald's {WALD} for one pair, at this rate"
    return "ordinary", ""


def main():
    t0 = time.time()
    names = [n for n in WW.W if not (S.world_of(WW.W[n]["text"]).tag() == 5)]
    for n in names:
        guard(n)
    print("corpus SHA-256:", open("/home/pilgrim/git/simple-learner/lab/stage2_lang/corpus.txt.sha256").read().strip(), flush=True)
    with ProcessPoolExecutor(7) as ex:
        rows = {n: list(ex.map(rec, [(WW.W[n]["text"], s, c) for s in SEEDS for c in S.COL], chunksize=4)) for n in names}
        print(f"streams {time.time() - t0:.0f} s", flush=True)
        st = {n: stats(rows[n]) for n in names}
        with open(OUT + "label_rows.pkl", "wb") as f:
            pickle.dump(rows, f)
        del rows
        e_plain = st["plain"][:, 1].sum() / st["plain"][:, 3].sum()
        L = {n: summarise(st[n], e_plain) for n in names}
        fd = {}
        plain = {arm: list(ex.map(wire, [(WW.W["plain"]["text"], arm, s, c) for s in FD_SEEDS for c in S.COL], chunksize=4)) for arm in ("circuit", "bank", "unwired")}
        for n in names:
            d = {}
            for arm in ("circuit", "bank", "unwired"):
                w_ = list(ex.map(wire, [(WW.W[n]["text"], arm, s, c) for s in FD_SEEDS for c in S.COL], chunksize=4))
                ds = [first_diff(a, b) for a, b in zip(w_, plain[arm])]
                d[arm] = ([x * 0.01 for x in ds if x is not None], sum(x is None for x in ds) / len(ds), rate_kl([x[2] for x in w_], [x[2] for x in plain[arm]]))
            fd[n] = d
            print(f"first differences {n} {time.time() - t0:.0f} s", flush=True)
    labels = {}
    print("\n== labels, at the bank's rate. Development, hand-picked. Numbers measured unless named; D and rate evidence are estimates. e, rho: 95% over seed pairs.", flush=True)
    print(f"{'world':20s} {'DL':>5s} {'e':>16s} {'rho':>14s} {'n/s':>5s} {'b/taste':>7s} {'b/life':>16s} {'D':>13s} {'rate':>6s} {'first diff base/bank/unwired: median s (none)':46s} class", flush=True)
    for n in names:
        l, d, w = L[n], fd[n], S.world_of(WW.W[n]["text"])
        none = min(d[a][1] for a in d)
        rb = d["circuit"][2]
        cl, why = classify(n, l, none, rb, w)
        def f(a):
            return f"{np.median(d[a][0]):.1f}({d[a][1]:.0%})" if d[a][0] else "none"
        ci = l["ci"]
        es = f"{l['e']:.3f}[{ci['e'][0]:.3f},{ci['e'][1]:.3f}]" if l["e"] is not None else "-"
        rs = f"{l['rho']:.3f}[{ci['rho'][0]:.2f},{ci['rho'][1]:.2f}]" if l["e"] is not None else "-"
        bs = f"{l['bl']:.1f}[{ci['bl'][0]:.1f},{ci['bl'][1]:.1f}]" if l["e"] is not None else "-"
        ds = f"{l['D']:.1f}[{ci['D'][0]:.0f},{ci['D'][1]:.0f}]" if l["e"] is not None else "-"
        bits = lang.bits(w)
        print(f"{n:20s} {bits:5d} {es:>16s} {rs:>14s} {l['n'] / 100:5.2f} {(l['bt'] if l['bt'] is not None else float('nan')):7.2f} {bs:>16s} {ds:>13s} {rb:6.1f} {f('circuit') + ' ' + f('bank') + ' ' + f('unwired'):46s} {cl}" + (f" ({why})" if why else ""), flush=True)
        labels[n] = dict(bits=bits, **{k: l[k] for k in ("n", "e", "rho", "bt", "bl", "D")}, ci={k: [float(x) for x in v] for k, v in l["ci"].items()}, fd={a: (float(np.median(d[a][0])) if d[a][0] else None, d[a][1], d[a][2]) for a in d}, cls=cl, why=why)
    with open(OUT + "labels.pkl", "wb") as f:
        pickle.dump(labels, f)
    print(f"\ndone {time.time() - t0:.0f} s", flush=True)


def sens():
    """Added after the classes were read, not part of D6: the rate evidence again with each life's spread in place of Poisson's. A life's bits for a feature: Gaussian KL with that feature's measured sd between lives on plain, (delta / sd)^2 / (2 ln 2), counted where the paired interval excludes 0. It doesn't reclass anyone: it says which 'ordinary' rests on the Poisson assumption."""
    labels = pickle.load(open(OUT + "labels.pkl", "rb"))
    names = list(labels)
    with ProcessPoolExecutor(7) as ex:
        plain = list(ex.map(wire, [(WW.W["plain"]["text"], "circuit", s, c) for s in FD_SEEDS for c in S.COL], chunksize=4))
        R0 = np.array([x[2] for x in plain], dtype=float)
        R0 = np.column_stack((R0[:, :2].max(1), R0[:, :2].min(1), R0[:, 2], R0[:, 3]))
        sd = R0.std(0, ddof=1)
        print("plain, a life's sd against Poisson's: " + " ".join(f"{a:.1f}/{b:.1f}" for a, b in zip(sd, np.sqrt(R0.mean(0)))), flush=True)
        for n in names:
            w_ = list(ex.map(wire, [(WW.W[n]["text"], "circuit", s, c) for s in FD_SEEDS for c in S.COL], chunksize=4))
            R = np.array([x[2] for x in w_], dtype=float)
            R = np.column_stack((R[:, :2].max(1), R[:, :2].min(1), R[:, 2], R[:, 3]))
            pairs = len(R) // 2
            g = np.random.default_rng(1)
            k = g.integers(0, pairs, (1000, pairs))
            idx = np.concatenate((2 * k, 2 * k + 1), axis=1)
            lo, hi = np.percentile((R - R0)[idx].mean(1), [2.5, 97.5], axis=0)
            bits = sum(((R[:, j].mean() - R0[:, j].mean()) / sd[j]) ** 2 / (2 * math.log(2)) for j in range(4) if lo[j] > 0 or hi[j] < 0)
            L = labels[n]
            tot = (L["D"] or 0.0) + bits
            flag = "" if L["cls"] != "ordinary" or tot >= WALD else "  ORDINARY ONLY BY POISSON"
            print(f"{n:20s} D {L['D'] or 0.0:7.1f}  Poisson rate {L['fd']['circuit'][2]:7.1f}  by a life's spread {bits:6.1f}  {L['cls']}{flag}", flush=True)


if __name__ == "__main__":
    if sys.argv[1:] == ["sens"]:
        sens()
    else:
        main()

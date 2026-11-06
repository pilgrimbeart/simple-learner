"""bits_analyse.py: stage 1b's sums on the recorded streams (lab/bits_record.py, ~/nca-scratch-backup/bits): the budget, the shadow selector, the evidence rule.

The likelihood that matters. A model m says which colour is food at each taste, a function of the past stream alone. Stated: it is right with chance 1-e, independently. The creature's choice of what
to eat is a function of the past too, so P(stream | m) = prod P(action | past) P(sign | action, past, m), and the policy's factor is the same for every m and cancels. So the posterior is exact whoever
drives. What this can't say: how much faster a driver chosen for information would have learned. And the stated likelihood is a model of the data, not the data: `calibration` measures how wrong it is.

    .venv/bin/python lab/bits_analyse.py budget|rates|shadow|rule|all [LO]"""
import os
import pickle
import sys
import numpy as np

D = os.path.expanduser("~/nca-scratch-backup/bits/")
C = dict(t=0, value=1, vouched=2, scored=3, open=4, followed=5, eaten=6, F=7, kind=8, gap=9, act=10, preds=11, bad=12)
WORLDS = ["plain", "swap10", "alternate", "pattern", "digest", "unreliable", "patchy", "weak", "noisy"]
RIGHT = dict(plain={0}, swap10={1}, alternate={2, 4, 6}, pattern={3, 6}, digest={0}, unreliable={0}, patchy={0}, weak={0}, noisy={0})
NAMES = ["1/3", "1/0", "2/2", "3/2", "4/2", "5/2", "6/2"]
BOOT = 1000
LOGP7 = np.log2(7)


def h2(p):
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return -p * np.log2(p) - (1 - p) * np.log2(1 - p)


def load(name, lo=60000):
    with open(D + f"{name}_{lo}.pkl", "rb") as f:
        return pickle.load(f)


def ci(values):
    return np.percentile(values, 2.5), np.percentile(values, 97.5)


def boot(per_life, f, seed=0):
    """f on the per-life array, resampling seeds (a seed's two lives together: rows 2i, 2i+1)."""
    r = np.random.default_rng(seed)
    a = np.asarray(per_life)
    n = len(a) // 2
    out = []
    for _ in range(BOOT):
        k = r.integers(0, n, n)
        out.append(f(a[np.concatenate((2 * k, 2 * k + 1))]))
    return f(a), ci(out)


def fmt(b, d=2):
    v, (l, h) = b
    return f"{v:.{d}f} [{l:.{d}f},{h:.{d}f}]"


def stream(life):
    """The scored tastes: (t, H), H[i, m] = model m's prediction hit."""
    x = life["rows"]
    x = x[x[:, C["scored"]] > 0]
    truth = np.where(x[:, C["value"]] > 0, x[:, C["followed"]], 1 - x[:, C["followed"]]).astype(int)
    preds = x[:, C["preds"]].astype(int)
    H = np.array([((preds >> i) & 1) == truth for i in range(7)]).T.reshape(-1, 7)
    return x[:, C["t"]], H.astype(int), x


# ---------- 1: the budget
def budget(bank):
    print("== 1. The budget per life, real lives of the bank, 95% intervals over seeds. n: pulses, vouched, scored. e: chance what a scored taste says of the colour is false against the rule's food colour.")
    print("   A: chance a scored taste's meal was the followed colour. Lsign: chance the sign is false of the colour eaten. I = 1-H(e), bits a taste could carry to a pair of hypotheses that disagree on it")
    res = {}
    for w in WORLDS:
        P = []
        for l in bank[w]:
            x = l["rows"]
            s = x[x[:, C["scored"]] > 0]
            ok = s[(s[:, C["F"]] >= 0) & (s[:, C["eaten"]] >= 0)]
            said = np.where(ok[:, C["value"]] > 0, ok[:, C["followed"]], 1 - ok[:, C["followed"]])
            attributed = ok[:, C["eaten"]] == ok[:, C["followed"]]
            lied = (ok[:, C["value"]] > 0) != (ok[:, C["eaten"]] == ok[:, C["F"]])
            P.append([len(x), (x[:, C["vouched"]] > 0).sum(), len(s), len(ok), (said != ok[:, C["F"]]).sum(), attributed.sum(), lied.sum(),
                      (s[:, C["t"]] < 10).sum(), (s[:, C["t"]] < 30).sum()])
        P = np.array(P, dtype=float)
        n, v, sc = boot(P[:, 0], np.mean), boot(P[:, 1], np.mean), boot(P[:, 2], np.mean)
        e = boot(P, lambda a: a[:, 4].sum() / a[:, 3].sum())
        A = boot(P, lambda a: a[:, 5].sum() / a[:, 3].sum())
        L = boot(P, lambda a: a[:, 6].sum() / a[:, 3].sum())
        I = boot(P, lambda a: 1 - h2(a[:, 4].sum() / a[:, 3].sum()))
        bits = boot(P, lambda a: a[:, 2].mean() * (1 - h2(a[:, 4].sum() / a[:, 3].sum())))
        b10 = boot(P, lambda a: a[:, 7].mean() * (1 - h2(a[:, 4].sum() / a[:, 3].sum())))
        b30 = boot(P, lambda a: a[:, 8].mean() * (1 - h2(a[:, 4].sum() / a[:, 3].sum())))
        print(f"{w:11s} pulses {fmt(n, 1)} vouched {fmt(v, 1)} scored {fmt(sc, 1)} | e {fmt(e, 3)} A {fmt(A, 3)} Lsign {fmt(L, 3)} | I {fmt(I, 3)} bits/taste | {fmt(bits, 1)} bits/life, {bits[0] / 100:.3f} bits/s; first 10 s {fmt(b10, 1)}, 30 s {fmt(b30, 1)}; scored in 10 s {P[:, 7].mean():.1f}, 30 s {P[:, 8].mean():.1f}")
        res[w] = dict(n=sc[0], I=I[0], e=e[0], n10=P[:, 7].mean(), n30=P[:, 8].mean())
    return res


# ---------- 1b: what the bit's being right or wrong does to each kind of taste (told right / told wrong, same parts)
def rates(right, wrong):
    print("\n== 1b. A taste as a channel from 'the followed colour is the food' (told right, told wrong, 200 seeds x 2). Sign alone on scored tastes: P(good | right), P(good | wrong), I with a uniform prior on right/wrong.")
    print("   All pulses: Poisson rate of each kind (sign, followed eye within 0.3 s, other eye within 0.3 s), bits/s = KL rate between right and wrong, each way. Upper bound for vouching's loss on these features only.")
    for w in WORLDS:
        def counts(L, keep):
            c = np.zeros(8)
            T = 0.0
            sc = np.zeros(2)
            for l in L:
                x = l["rows"]
                T += 100.0
                for r in x:
                    c[int(r[C["value"]] > 0) * 4 + int(r[C["kind"]])] += 1
                s = x[x[:, C["scored"]] > 0]
                sc += [(s[:, C["value"]] > 0).sum(), (s[:, C["value"]] < 0).sum()]
            return c, sc, T
        cr, sr, T = counts(right[w], None)
        cw, sw, _ = counts(wrong[w], None)
        g1, g0 = sr[0] / max(1, sr.sum()), sw[0] / max(1, sw.sum())
        pbar = (g1 + g0) / 2
        Iu = h2(pbar) - (h2(g1) + h2(g0)) / 2
        r1, r0 = (cr + 0.5) / T, (cw + 0.5) / T
        kl10 = np.sum(r1 * np.log2(r1 / r0) - (r1 - r0) / np.log(2))
        kl01 = np.sum(r0 * np.log2(r0 / r1) - (r0 - r1) / np.log(2))
        p1, p0 = (cr + 0.5) / (cr + 0.5).sum(), (cw + 0.5) / (cw + 0.5).sum()
        mid = (p1 + p0) / 2
        Ik = 0.5 * np.sum(p1 * np.log2(p1 / mid)) + 0.5 * np.sum(p0 * np.log2(p0 / mid))
        print(f"{w:11s} I with kind, per pulse, uniform prior {Ik:.3f} bits, so {Ik * cr.sum() / T:.3f} bits/s told right, against the sign on scored tastes {Iu * sr.sum() / T:.3f} bits/s")
        print(f"{w:11s} scored per s right {sr.sum() / T:.3f} wrong {sw.sum() / T:.3f}; P(good|right) {g1:.3f} P(good|wrong) {g0:.3f} I_sign {Iu:.3f} bits/taste; pulses per s right {cr.sum() / T:.3f} wrong {cw.sum() / T:.3f}; KL rate right||wrong {kl10:.3f}, wrong||right {kl01:.3f} bits/s")


# ---------- calibration: are the stated likelihoods true?
def calibration(bank):
    print("\n== 2a. Each model in each world: hit rate on scored tastes, and H(hit rate), the bits a taste it leaves unexplained (a prequential code length, so a model's learning cost is in it: this is its Occam factor). Then rho: share of tastes where it disagrees with the default; a: chance it is the one right, given that.")
    out = {}
    for w in WORLDS:
        n, hits, dis, rh = 0, np.zeros(7), np.zeros(7), np.zeros(7)
        for l in bank[w]:
            _, H, _ = stream(l)
            n += len(H)
            hits += H.sum(0)
            d = H != H[:, [0]]
            dis += d.sum(0)
            rh += (d & (H == 1)).sum(0)
        rate = hits / n
        a = rh / np.maximum(dis, 1)
        out[w] = dict(rate=rate, rho=dis / n, a=a, dis=dis, rh=rh, n=n)
        print(f"{w:11s} hit  " + " ".join(f"{NAMES[i]}:{rate[i]:.3f}" for i in range(7)) + f" | best {NAMES[int(np.argmax(rate))]}")
        print(f"            H    " + " ".join(f"{NAMES[i]}:{h2(rate[i]):.3f}" for i in range(7)))
        print(f"            rho  " + " ".join(f"{NAMES[i]}:{out[w]['rho'][i]:.3f}" for i in range(7)))
        print(f"            a    " + " ".join(f"{NAMES[i]}:{a[i]:.3f}" for i in range(7)))
    return out


# ---------- replays of selection rules on a fixed stream
def replay_map(t, H, k):
    """MAP with the default ahead by k hits: every switch as (t, model)."""
    picks = []
    le = np.zeros(7)
    le[0] = k
    act = 0
    for i in range(len(t)):
        le += H[i]
        b = int(np.argmax(le))
        if b != act:
            act = b
            picks.append((t[i], b))
    return picks


def replay_ctr(t, H, up=1.0, pen=3.0, floor=0.0, top=10.0, theta=2.0, theta_n=1.0, hyst=1.0, off=1.0):
    """The bank's counters and choose, on the stream: must reproduce the bank's own picks (shadow's check)."""
    E = np.zeros(7)
    act = 0
    picks = []
    ns = [1, 1, 2, 3, 4, 5, 6]
    for i in range(len(t)):
        for m in range(1, 7):
            d = H[i, m] - H[i, 0]
            if d:
                E[m] = min(top, max(floor if floor is not None else -1e9, E[m] + (up if d > 0 else -pen)))
        best = max(range(7), key=lambda j: (E[j], -j))
        need = theta + (theta_n if ns[best] > 1 else 0.0)
        if E[best] >= need and E[best] >= E[act] + hyst and best != act:
            act = best
            picks.append((t[i], best))
        elif act and E[act] < off:
            act = 0
            picks.append((t[i], 0))
    return picks


def firsts(picks, right):
    """(first pick of a rival, first pick in the right set among rivals), inf if never."""
    a = next((t for t, m in picks if m), np.inf)
    b = next((t for t, m in picks if m and m in right), np.inf)
    return a, b


def summary_picks(lives, rule, right, default_right):
    A, B = [], []
    for t, H in lives:
        a, b = firsts(rule(t, H), right)
        A.append(a)
        B.append(b)
    return np.array(A), np.array(B)


def share(a):
    return np.isfinite(a).mean()


def med(a):
    return float(np.median(np.minimum(a, 1e9)))


def rmean(a):
    return float(np.minimum(a, 100.0).mean())


# ---------- 2: the shadow selector
def shadow(bank, pinned):
    print("\n== 2b. Replay check: the bank's counters replayed on its own stream against its recorded picks (first pick, all lives)")
    for w in WORLDS:
        same, n = 0, 0
        for l in bank[w]:
            t, H, _ = stream(l)
            r = replay_ctr(t, H)
            a0 = next((tt for tt, m in l["picks"] if m), None)
            a1 = next((tt for tt, m in r if m), None)
            same += (a0 is None and a1 is None) or (a0 is not None and a1 is not None and abs(a0 - a1) < 1e-3)
            n += 1
        print(f"  {w}: first picks reproduced {same}/{n}")

    print("\n== 2c. Evidence at the bank's first pick of a rival. n: scored tastes so far. diff: its hits less the default's, whole stream. Bits at e=0.1 (3.17 a hit) and with e integrated out per model (Beta(1,1)), each against the default. Pcand: posterior of the picked model, uniform prior over seven; P0.9: default's prior 0.9, rivals sharing 0.1; e=0.1.")
    from math import lgamma
    betaln = lambda a, b: lgamma(a) + lgamma(b) - lgamma(a + b)
    L = np.log2(0.9 / 0.1)
    stats = {}
    for w in WORLDS:
        rows = []
        for l in bank[w]:
            t, H, _ = stream(l)
            p = next(((tt, m) for tt, m in l["picks"] if m), None)
            if p is None:
                continue
            i = np.searchsorted(t, p[0] + 1e-9)
            c = H[:i].sum(0)
            n = i
            diff = c[p[1]] - c[0]
            beta = (betaln(c[p[1]] + 1, n - c[p[1]] + 1) - betaln(c[0] + 1, n - c[0] + 1)) / np.log(2)
            le = c * L
            post = np.exp2(le - le.max()) / np.exp2(le - le.max()).sum()
            pri = np.array([0.9] + [0.1 / 6] * 6)
            pp = pri * np.exp2(le - le.max())
            pp /= pp.sum()
            rows.append((p[0], n, diff, diff * L, beta, post[p[1]], pp[p[1]], p[1] in RIGHT[w]))
        if not rows:
            print(f"{w:11s} no picks in {len(bank[w])} lives")
            continue
        a = np.array(rows, dtype=float)
        tw = "right" if RIGHT[w] != {0} else "false"
        print(f"{w:11s} picks in {len(a) / len(bank[w]):.3f} of lives, {a[:, 7].mean():.2f} of them right | at pick median t {np.median(a[:, 0]):.1f} s, n {np.median(a[:, 1]):.0f}, diff {np.median(a[:, 2]):.0f} (10-90%: {np.percentile(a[:, 2], 10):.0f},{np.percentile(a[:, 2], 90):.0f}), bits {np.median(a[:, 3]):.1f}, Beta bits {np.median(a[:, 4]):.1f}, Pcand {np.median(a[:, 5]):.3f}, P0.9 {np.median(a[:, 6]):.3f}; share of picks with diff<=0: {(a[:, 2] <= 0).mean():.2f}")
        stats[w] = a

    for name, src in (("bank's own stream (real lives)", bank), ("the default pinned (exact to any selector's first pick)", pinned)):
        print(f"\n== 2d. Selection on {name}: first pick of a rival (false where the default is right), first right pick. Each rule: share of lives with a pick, median time (s), right pick's share and median.")
        S = {w: [stream(l)[:2] for l in src[w]] for w in WORLDS}
        rules = [("bank +1/-3 floor 0, theta 2,3", lambda t, H: replay_ctr(t, H))] + [(f"MAP default +{k} hits (a rival needs {int(k + .5)} ahead)", (lambda k: lambda t, H: replay_map(t, H, k))(k)) for k in (0.5, 1.5, 2.5, 3.5, 4.5, 6.5, 8.5)]
        rules += [(f"counter +1/-{pen} floor {fl}, theta {th}", (lambda pen, fl, th: lambda t, H: replay_ctr(t, H, pen=pen, floor=fl, theta=th, theta_n=1.0))(pen, fl, th)) for pen, fl, th in ((1, 0.0, 2), (1, 0.0, 4), (3, 0.0, 1), (3, 0.0, 3), (3, 0.0, 4), (3, None, 2), (1, None, 2), (2, 0.0, 2))]
        for rn, rule in rules:
            out = []
            for w in WORLDS:
                A, B_ = summary_picks(S[w], rule, RIGHT[w], RIGHT[w] == {0})
                if RIGHT[w] == {0}:
                    out.append(f"{w[:5]} false {share(A):.3f}")
                else:
                    out.append(f"{w[:5]} right {share(B_):.2f}@{med(B_):.1f}s false-first {share(A) and np.mean(A < B_):.2f}")
            print(f"{rn:48s} " + " | ".join(out))
    return


def paired_first(S, r1, r2, right):
    """First right pick: median paired difference, r1 - r2, in s, censored at 100, with the interval over seeds."""
    a = np.array([firsts(r1(t, H), right)[1] for t, H in S])
    b = np.array([firsts(r2(t, H), right)[1] for t, H in S])
    d = np.minimum(a, 100) - np.minimum(b, 100)
    return boot(d, np.mean), a, b


def efficiency_table(bank, pinned):
    print("\n== 2e. Same false picks, paired. For each MAP threshold: no more false picks than the bank in unreliable (the world that sets its threshold), and separately pooled across the six worlds whose right model is the default. On the pinned stream, where a first pick is exact for any selector. Information efficiency: tastes the ideal needs over tastes the bank needs, to the right pick.")
    S = {w: [stream(l)[:2] for l in pinned[w]] for w in WORLDS}
    R = {w: [stream(l)[:2] for l in bank[w]] for w in WORLDS}
    bank_rule = lambda t, H: replay_ctr(t, H)
    defaults = [w for w in WORLDS if RIGHT[w] == {0}]
    fb = {w: share(summary_picks(S[w], bank_rule, RIGHT[w], True)[0]) for w in defaults}
    print("  the bank's false picks: " + " ".join(f"{w} {fb[w]:.3f}" for w in defaults) + f"; pooled {np.mean(list(fb.values())):.3f}")
    ks = [0.5, 1.5, 2.5, 3.5, 4.5, 6.5, 8.5]
    fm = {k: {w: share(summary_picks(S[w], lambda t, H: replay_map(t, H, k), RIGHT[w], True)[0]) for w in defaults} for k in ks}
    for k in ks:
        print(f"  MAP k={k}: " + " ".join(f"{w} {fm[k][w]:.3f}" for w in defaults) + f"; pooled {np.mean(list(fm[k].values())):.3f}")
    ku = next(k for k in ks if fm[k]["unreliable"] <= fb["unreliable"])
    kp = next(k for k in ks if np.mean(list(fm[k].values())) <= np.mean(list(fb.values())))
    print(f"  so k = {ku} matches unreliable's false picks, k = {kp} the pooled")
    for w in ("swap10", "alternate", "pattern"):
        for k in sorted({ku, kp}):
            m = lambda t, H: replay_map(t, H, k)
            d, a, b = paired_first(S[w], m, bank_rule, RIGHT[w])
            # tastes to the right pick
            na, nb = [], []
            for (t, H), x, y in zip(S[w], a, b):
                na.append(np.searchsorted(t, x + 1e-9) if np.isfinite(x) else len(t))
                nb.append(np.searchsorted(t, y + 1e-9) if np.isfinite(y) else len(t))
            na, nb = np.array(na), np.array(nb)
            eff = boot(np.column_stack((na, nb)), lambda q: q[:, 0].mean() / max(q[:, 1].mean(), 1e-9))
            print(f"  {w} k={k}: ideal first right pick median {med(a):.1f} s ({share(a):.2f}), bank {med(b):.1f} s ({share(b):.2f}); ideal - bank mean {fmt(d, 2)} s; tastes ideal {na.mean():.1f}, bank {nb.mean():.1f}, efficiency {fmt(eff, 2)}")
    print("  evidence by time, on the pinned stream and real lives: median hits ahead of the default of the best rival in the right set, and at e=0.1 in bits (3.17 a hit); a rival right set only")
    for w in ("swap10", "alternate", "pattern"):
        for nm, src in (("pinned", S), ("real", R)):
            out = []
            for T_ in (5, 10, 15, 20, 30, 100):
                v = []
                for t, H in src[w]:
                    i = np.searchsorted(t, T_)
                    c = H[:i].sum(0)
                    v.append(max(c[m] for m in RIGHT[w]) - c[0])
                out.append(f"{T_} s {np.median(v):.0f}")
            print(f"    {w} {nm}: " + ", ".join(out))


# ---------- 3: the rule
def rule(bank, pinned, cal):
    print("\n== 3. The rule. If each model is right with chance 1-e independently, a disagreement moves the log odds by +L or -L, L = log2((1-e)/e), and nothing else. +1/-3 is symmetric at no e.")
    print("   It is the LLR of a different pair: under 'rival' it is the right one of a disagreement with chance a, under 'default' with chance b. Then up = log2(a/b), down = log2((1-a)/(1-b)). Solutions of down/up = -3, by the unit of a +1:")
    for u in (0.25, 0.5, 1.0, 1.585, 2.0, 2.32, 3.0, 4.0):
        x = 2 ** u
        y = 2 ** (-3 * u)
        # a = b x ; 1-a = (1-b) y  => b = (1-y)/(x-y)
        b = (1 - y) / (x - y)
        print(f"   unit {u:.2f} bits: a {b * x:.4f}, b {b:.4f}; so theta 2 is {2 * u:.1f} bits, theta 3 {3 * u:.1f} bits, clip 10 {10 * u:.1f} bits")
    print("   As the unit shrinks a, b -> 3/4: the counter's drift a - 3(1-a) changes sign at a = 3/4, so what it tests is 'this rival is the right one in more than 3/4 of disagreements'.")
    print("   Measured: for each rival, a in the world it fits, b in each world the default fits, tastes as streams (so correlated). The derived rule per rival, LLR in bits (Laplace):")
    dworlds = [w for w in WORLDS if RIGHT[w] == {0}]
    fit = {1: "swap10", 2: "alternate", 3: "pattern", 6: "pattern", 4: "alternate"}
    for m, w in fit.items():
        c = cal[w]
        a = (c["rh"][m] + 1) / (c["dis"][m] + 2)
        for dw in dworlds:
            d = cal[dw]
            b = (d["rh"][m] + 1) / (d["dis"][m] + 2)
            print(f"   {NAMES[m]} in {w} a {a:.3f} (n {int(c['dis'][m])}) vs {dw}: b {b:.3f} (n {int(d['dis'][m])}): up {np.log2(a / b):+.2f}, down {np.log2((1 - a) / (1 - b)):+.2f}, ratio {-np.log2((1 - a) / (1 - b)) / max(np.log2(a / b), 1e-9):.2f}; per taste KL(rival||default) {cal[w]['rho'][m] * (a * np.log2(a / b) + (1 - a) * np.log2((1 - a) / (1 - b))):.3f} bits")
    print("   Disagreements run together: for 1/0, in unreliable and swap10, the length of a run of consecutive disagreements, and the chance the rival is right at each place in it (pinned stream):")
    for w in ("unreliable", "swap10", "plain"):
        runs, by = [], {}
        for l in pinned[w]:
            _, H, _ = stream(l)
            d = H[:, 1] != H[:, 0]
            i = 0
            while i < len(d):
                if d[i]:
                    j = i
                    while j < len(d) and d[j]:
                        by.setdefault(j - i, []).append(H[j, 1])
                        j += 1
                    runs.append(j - i)
                    i = j
                else:
                    i += 1
        lives = len(pinned[w])
        print(f"   {w}: runs a life {len(runs) / lives:.2f}, mean length {np.mean(runs) if runs else 0:.2f}; rival right at place 0..3: " + " ".join(f"{np.mean(by[i]):.3f}(n{len(by[i])})" for i in range(4) if i in by))
    print("   The trade-off, on the pinned stream (first picks exact): false picks in unreliable, per rival; time to right pick in swap10, by threshold on the bank's counter:")
    S = {w: [stream(l)[:2] for l in pinned[w]] for w in WORLDS}
    for th in (1, 2, 3, 4):
        r = lambda t, H: replay_ctr(t, H, theta=th)
        fp = summary_picks(S["unreliable"], r, {0}, True)[0]
        who = np.zeros(7)
        for t, H in S["unreliable"]:
            p = next((m for tt, m in r(t, H) if m), None)
            if p:
                who[p] += 1
        a = summary_picks(S["swap10"], r, {1}, False)[1]
        fpp = summary_picks(S["plain"], r, {0}, True)[0]
        print(f"   theta {th}: unreliable false {share(fp):.3f} (by {' '.join(f'{NAMES[i]}:{int(who[i])}' for i in range(1, 7) if who[i])}), plain false {share(fpp):.3f}; swap10 right pick {share(a):.2f} at {med(a):.1f} s")
    q = cal["unreliable"]["a"][1]
    N = cal["unreliable"]["rho"][1] * cal["unreliable"]["n"] / len(pinned["unreliable"])
    print(f"   Derived for 1/0 in unreliable, as a run test: q = {q:.3f} its chance on a disagreement, about {N:.1f} disagreements a life (Poisson). The floor at 0 with any pen >= 1 makes theta a run of theta wins in the disagreements; without it the walk reaches +k with chance (q/(1-q))^k once in a life (Gambler's ruin):")
    for th in (1, 2, 3, 4):
        tot = 0.0
        for n_ in range(0, 80):
            w_ = np.exp(-N + n_ * np.log(N) - sum(np.log(np.arange(1, n_ + 1)))) if n_ else np.exp(-N)
            st = np.zeros(th + 1)
            st[0] = 1.0
            for _ in range(n_):
                nx = np.zeros(th + 1)
                nx[th] = st[th]
                nx[0] += st[:th].sum() * (1 - q)
                nx[1:th + 1] += st[:th] * q
                st = nx
            tot += w_ * st[th]
        print(f"   theta {th}: with the floor, derived {tot:.3f}; without it, derived {(q / (1 - q)) ** th:.3f}")
    print("   The same with the floor's effect shown by the exact posterior's MAP, same stream:")
    for k in (0.5, 1.5, 2.5, 3.5):
        r = lambda t, H: replay_map(t, H, k)
        fp = summary_picks(S["unreliable"], r, {0}, True)[0]
        a = summary_picks(S["swap10"], r, {1}, False)[1]
        fpp = summary_picks(S["plain"], r, {0}, True)[0]
        print(f"   k {k}: unreliable false {share(fp):.3f}, plain false {share(fpp):.3f}; swap10 right pick {share(a):.2f} at {med(a):.1f} s")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    lo = int(sys.argv[2]) if len(sys.argv) > 2 else 60000
    np.set_printoptions(precision=3, suppress=True)
    bank = load("bank", lo)
    if what in ("budget", "all"):
        budget(bank)
    if what in ("rates", "all"):
        rates(load("right", lo), load("wrong", lo))
    pinned = load("pinned", lo)
    if what in ("shadow", "all"):
        cal = calibration(bank)
        shadow(bank, pinned)
        efficiency_table(bank, pinned)
    if what in ("rule", "all"):
        cal = calibration(pinned) if what == "rule" else cal
        rule(bank, pinned, cal)

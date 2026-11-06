"""stage1c_limit.py: stage 1c part 4. A limit on tastes from the body, checked against measurement; usable evidence at higher rates, through the wires; the Wald, Fano and union tables redone.

THE BOUND. Constants from world.py and units.py. q = exp(-DRAG TICK).
(a) One taste pulse a tick at most (creature.Life.step: "one pulse, however many meals at once"): 100 a second. Unconditional, for this simulator.
(b) Firing has no cap in world.py or creature.Life: a brain's step may return any number of firings. So every bound below is conditional on a stated cap R, firings a second per thruster.
(c) Path per firing. A firing adds PUSH to the velocity along the heading, and +-TURN to the spin; both then decay by q a tick, and the firing's tick already moves. So its whole contribution is at most PUSH TICK / (1-q) of displacement and TURN TICK / (1-q) of angle, whatever else happens. The mouth is at pos + RADIUS f(heading). A tick's chord is at most the sum of the displacement and RADIUS x the angle, so by the triangle inequality total mouth path <= l F, l = (PUSH + RADIUS TURN) TICK / (1-q), F the firings. Fired in pairs the spins cancel: 2 PUSH TICK / (1-q) a pair.
(d) Path per meal, in expectation, for any policy, told everything. Number the blocks ever eaten b1, b2, ...; d_i the distance between b_i and b_{i+1}. The mouth is within EAT of each when it eats it, so its path between them is at least (d_i - 2 EAT)+, and the total path is at least the sum of these. For each r: #{i : d_i <= r} <= C(r), the number of distinct pairs of blocks ever within r when the later of the pair was placed, where b_{i+1} placed after b_i was eaten can only be the respawn of a block eaten at that same meal (no meal lies between), in which case it is within r of the mouth: count one more per meal. Each placement is uniform on the torus outside a disc of radius X = 3 EAT + BODY about the body (world.Body.somewhere), independent of the past, so any policy's choices come before it: given the past, its chance of falling within r of any given block is at most P(r) = pi r^2 / (A - pi X^2). Hence E C(r) <= (C(36,2) + 36 E M) P(r), M the meals; the 36 being 35 other blocks and the mouth. So E[path] >= integral from 2 EAT of (E M - 1 - E C(r))+ dr: an inequality in E M alone, solved below.
Assumptions: blocks stay still (true of plain; moving worlds aren't covered); uniform respawn (patchy isn't covered); the body's rules in world.py; 36 blocks. A bound in expectation over lives, not on any life.

An ESTIMATE, not a bound: if each hop saw a fresh Poisson field, the path per meal would be E[(NN - 2 EAT)+], about 3.1 mm.

USABLE EVIDENCE. For each policy: each taste's sign with how long since each eye last pulsed and since the last taste: all the wires say about it. The policy's factors cancel since the features depend only on the past (D31), so only the sign's chance given the features carries bits about the rule. (i) 1b's channel: attribution to the more recent eye within 0.3 s, e the chance it misstates the rule's food colour, I = 1 - H(e). (ii) A table P(good | recency of the food's eye, of the other's, gap) learned on half the seeds, scored on the other half: bits per taste with a uniform prior on which colour is food, so a lower bound on what those features carry (under independent tastes), including every taste. (iii) The same table's accumulated log odds as a decoder: chance of naming the colour by 5, 10, 30 s, a check on (ii) that doesn't assume independence.

    .venv/bin/python lab/stage1c_limit.py bound|oracle|policies|tables"""
import math
import pickle
import sys
import time
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import numpy as np
import stage1c_arms as A
import world as Wd
import bits_bank as B
from units import TICK, MILLI

mm = MILLI
Q = math.exp(-Wd.DRAG * TICK)
CARRY = TICK / (1 - Q)
L_TRANS = Wd.PUSH * CARRY / mm                         # mm a firing, straight
L_ARC = Wd.RADIUS * Wd.TURN * CARRY / mm               # mm a single firing's spin moves the mouth
L_ONE = L_TRANS + L_ARC
AREA = (Wd.WORLD / mm) ** 2
X = (3 * Wd.EAT + Wd.BODY) / mm
EAT = Wd.EAT / mm
NB = 2 * Wd.BLOCKS
PAIRS = NB * (NB - 1) / 2
JOB = range(62000, 62050)


def P(r):
    return np.pi * r * r / (AREA - np.pi * X * X)


def lower_path(m):
    """The least expected mouth path (mm) for m expected meals, (d)."""
    r = np.linspace(2 * EAT, 30.0, 6000)
    y = np.maximum(m - 1 - (PAIRS + (NB) * m) * P(r), 0.0)
    return np.trapezoid(y, r)


def meals_bound(path):
    """The largest expected meals consistent with an expected mouth path (mm)."""
    lo, hi = 1.0, 1e7
    for _ in range(100):
        mid = math.sqrt(lo * hi)
        lo, hi = (mid, hi) if lower_path(mid) < path else (lo, mid)
    return lo


def fresh_hop():
    rho = NB / AREA
    return (1 / (2 * math.sqrt(rho))) * math.erfc(math.sqrt(rho * math.pi) * 2 * EAT)


def bound():
    print(f"q = {Q:.4f}; a firing: {L_TRANS:.3f} mm of displacement, {Wd.TURN * CARRY:.3f} rad of turn, {L_ARC:.3f} mm of arc at the mouth; l = {L_ONE:.3f} mm a single firing; a pair {2 * L_TRANS:.3f} mm", flush=True)
    print(f"Blocks {NB}, density {NB / AREA:.4f} /mm^2, exclusion {X:.1f} mm. Path per meal for large m: {lower_path(1e6) / 1e6:.3f} mm (proved, in expectation); at m = 1000 {lower_path(1000) / 1000:.3f}, at m = 200 {lower_path(200) / 200:.3f}. Fresh-field estimate {fresh_hop():.2f} mm.", flush=True)
    print("Firing limits, none in the body's code: bench drive 50 a second per thruster (the present circuit's beat; drawn with spread 11%), one a tick per thruster (100), and the simulator's honesty limit: a spike needs a node up through 0 V and down below -V_TYP, at most V_TYP/2 a 0.125 ms step: at least 6 steps, 1333 a second per thruster.", flush=True)
    print("cap R a second | speed straight (mean, mm/s; every firing paired) | peak mm/s | PROVED: meals a second <= (firing anyhow) | ESTIMATE: pair firing, fresh field, no turning: meals a second", flush=True)
    for R in (25, 50, 100, 200, 400, 1333):
        F = 2 * R * 100
        v = 2 * R * L_TRANS
        peak = 2 * R * TICK * Wd.PUSH / mm / (1 - Q) if R >= 100 else 2 * Wd.PUSH / mm / (1 - Q ** (100 / R))
        pb = meals_bound(L_ONE * F) / 100
        print(f"   {R} | {v:.1f} | {peak:.1f} | {min(pb, 100.0):.1f}{' (the tick limit)' if pb > 100 else ''} | {v / fresh_hop():.1f}", flush=True)
    # control: a brute-force simulation of the placement rules with mouth teleporting to the nearest block: its hops must obey (d)
    r = np.random.default_rng(1)
    hops, n, closec = [], 0, np.zeros(3)
    rs = (3.0, 5.0, 7.0)
    xy = r.uniform(0, 60, (NB, 2))
    pos = np.array([30.0, 30.0])
    M = 20000
    for i in range(M):
        d = (xy - pos + 30) % 60 - 30
        dist = np.hypot(d[:, 0], d[:, 1])
        k = int(np.argmin(dist))
        hops.append(max(dist[k] - 2 * EAT, 0.0))
        pos = xy[k].copy()
        while True:
            p = r.uniform(0, 60, 2)
            dp = (p - pos + 30) % 60 - 30
            if np.hypot(*dp) > X:
                xy[k] = p
                break
        dd = (xy - xy[k] + 30) % 60 - 30
        for j, rr in enumerate(rs):
            closec[j] += (np.hypot(dd[:, 0], dd[:, 1]) <= rr).sum() - 1
    print(f"Control: greedy teleporting mouth on the placement rules, {M} meals: path per meal {np.mean(hops):.2f} mm (greedy, so an upper estimate of the best possible, against the proved {lower_path(M) / M:.2f}). Close pairs per placement at r = 3, 5, 7: {closec / M} against the proved rate {[round(35 * P(x), 3) for x in rs]}.", flush=True)


def oracle():
    print("== the oracle in plain, 50 seeds x 2: told all positions, the wiring and the dynamics; chases the cheapest block by distance + turn; motors only, at most R firings a second per thruster.", flush=True)
    print("R, turn cost | meals a second [95%] | taste pulses a second | firings a second | mm of firing path per meal (paired firings' 0.51 mm each) | proved bound at these firings | ESTIMATE at this speed", flush=True)
    best = {}
    for R in (25, 50, 100, 200, 400, 1333):
        for tc in (0.5, 1.0, 2.0):
            L = A.run("plain", "oracle", JOB, dict(rate=float(R), turnc=tc))
            m = np.array([len(l.mt) for l in L], dtype=float) / 100
            ta = np.array([l.tastes for l in L], dtype=float) / 100
            fir = np.array([len(l.ft) for l in L], dtype=float) / 100
            I = A.resample(len(m), 1000)
            lo, hi = np.percentile(m[I].mean(1), [2.5, 97.5])
            b = meals_bound(L_ONE * fir.mean() * 100) / 100
            print(f"   {R}, {tc} | {m.mean():.2f} [{lo:.2f},{hi:.2f}] | {ta.mean():.2f} | {fir.mean():.0f} | {fir.mean() * L_TRANS / m.mean():.2f} | {b:.1f} | {fir.mean() * L_TRANS / fresh_hop():.1f}", flush=True)
            if R not in best or m.mean() > best[R][0]:
                best[R] = (m.mean(), ta.mean(), fir.mean(), tc)
    with open(A.OUT + "oracle.pkl", "wb") as f:
        pickle.dump(best, f)
    print("Unwired lives and the bank, the same seeds:", flush=True)
    for nm, L in (("unwired", A.run("plain", "ureye", JOB)), ("bank", A.run("plain", "v_rec", JOB))):
        m = np.array([len(l.mt) for l in L], dtype=float) / 100
        fir = np.array([len(l.ft) for l in L], dtype=float) / 100
        print(f"   {nm}: {m.mean():.2f} meals a second, {fir.mean():.0f} firings a second, max life {m.max():.2f}; bound at those firings {meals_bound(L_ONE * fir.mean() * 100) / 100:.1f}", flush=True)


EDGES = np.array([0.0, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0, 1e9])


def features(u):
    """Per taste row (t, value, dt0, dt1, eaten, F): bins of recency for each eye, gap since the last taste in two bins (the digest's 1 s), sign."""
    t = u[:, 0]
    gap = np.diff(t, prepend=-10.0)
    b0, b1 = np.clip(np.digitize(u[:, 2], EDGES) - 1, 0, len(EDGES) - 2), np.clip(np.digitize(u[:, 3], EDGES) - 1, 0, len(EDGES) - 2)    # never pulsed: the last bin; a pulse later in this tick: the first
    return b0, b1, (gap < 1.2).astype(int), (u[:, 1] > 0).astype(int)


NBIN = len(EDGES) - 1


def channel(L, halves=True):
    """(i) and (ii),(iii) above, for lives in one world and one policy. Only tastes with a known rule colour (F >= 0) count."""
    rows = [l.urows for l in L]
    n = len(rows)
    def per(i_list, table=None):
        c = np.ones((NBIN, NBIN, 2, 2)) * 0.5
        for i in i_list:
            u = rows[i]
            if not len(u):
                continue
            k = u[:, 5] >= 0
            b0, b1, g, s = features(u)
            F = u[:, 5].astype(int)
            bf = np.where(F == 0, b0, b1)
            bo = np.where(F == 0, b1, b0)
            np.add.at(c, (bf[k], bo[k], g[k], s[k]), 1.0)
        return c
    train = [i for i in range(n) if (L[i].seed % 2) == 0]
    test = [i for i in range(n) if (L[i].seed % 2) == 1]
    c = per(train)
    pg = c[..., 1] / c.sum(-1)
    out = {}
    infos, klr, m_t, pulses, attr, wrong, sc = [], [], [], [], [], [], []
    acc = {5: [], 10: [], 30: []}
    conf = {5: [], 10: [], 30: []}
    for i in test:
        u = rows[i]
        k = u[:, 5] >= 0 if len(u) else np.zeros(0, bool)
        if not k.sum():
            infos.append(0.0)
            klr.append(0.0)
            m_t.append(0)
            attr.append(0)
            wrong.append(0)
            sc.append(0)
            for T_ in acc:
                acc[T_].append(0.5)
                conf[T_].append(0.5)
            continue
        u = u[k]
        b0, b1, g, s = features(u)
        F = u[:, 5].astype(int)
        bf, bo = np.where(F == 0, b0, b1), np.where(F == 0, b1, b0)
        p_true = np.where(s == 1, pg[bf, bo, g], 1 - pg[bf, bo, g])
        p_false = np.where(s == 1, pg[bo, bf, g], 1 - pg[bo, bf, g])
        llr = np.log2(p_true / p_false)
        infos.append(float(np.sum(1 - np.log2(1 + 2.0 ** -llr))))
        klr.append(float(llr.sum()))
        m_t.append(len(u))
        for T_ in acc:
            z = llr[u[:, 0] < T_].sum()
            acc[T_].append(0.5 if z == 0 else float(z > 0))
            conf[T_].append(1 / (1 + 2.0 ** -abs(z)))
        a = np.where(u[:, 2] < u[:, 3], 0, 1)
        scored = np.minimum(u[:, 2], u[:, 3]) < 0.3
        y = np.where(s == 1, a, 1 - a)
        attr.append(int(scored.sum()))
        wrong.append(int((y[scored] != F[scored]).sum()))
        sc.append(int(scored.sum()))
    infos, klr, m_t, attr, wrong = np.array(infos), np.array(klr), np.array(m_t, float), np.array(attr, float), np.array(wrong, float)
    I = np.random.default_rng(0).integers(0, len(infos), (1000, len(infos)))
    Ib = infos[I].mean(1) / 100
    e = wrong.sum() / max(attr.sum(), 1)
    e_v = wrong[I].sum(1) / np.maximum(attr[I].sum(1), 1)
    bps1 = attr[I].mean(1) / 100 * (1 - B_h2(e_v))
    return dict(taste=m_t.mean() / 100, scored=attr.mean() / 100, e=e, e_ci=np.percentile(e_v, [2.5, 97.5]), I1=1 - B_h2(np.array(e)), bps1=attr.mean() / 100 * (1 - B_h2(np.array(e))), bps1_ci=np.percentile(bps1, [2.5, 97.5]), bps2=infos.mean() / 100, bps2_ci=np.percentile(Ib, [2.5, 97.5]), kl=klr.mean() / 100, per_taste=infos.sum() / max(m_t.sum(), 1),
                acc={T_: float(np.mean(v)) for T_, v in acc.items()}, conf={T_: float(np.mean(v)) for T_, v in conf.items()})


def B_h2(p):
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return -p * np.log2(p) - (1 - p) * np.log2(1 - p)


def policies():
    t0 = time.time()
    TUNE = range(61000, 61032)
    print("== which wire-only settings eat most? table.Unwired (either eye starts a drive) in plain, 61000-61031 x 2; meals a second. None sees more than its eyes. The bank's own firing beat is drive 50 a second.", flush=True)
    grid = [dict(drive_x=dx, hold_x=hx, scan_x=sx, bored_x=bx, run_x=rx) for dx in (1.0, 2.0, 4.0) for hx in (1.0, 2.0, 4.0) for sx in (1.0, 2.0) for bx in (0.25, 1.0) for rx in (1.0, 2.0)]
    res = []
    for kw in grid:
        L = A.run("plain", "ureye", TUNE, kw)
        m = np.mean([len(l.mt) for l in L]) / 100
        fi = np.mean([len(l.ft) for l in L]) / 100
        res.append((m, fi, kw))
    res.sort(key=lambda x: -x[0])
    for m, fi, kw in res[:5] + res[-2:]:
        print(f"   {m:.2f} meals a second, {fi:.0f} firings a second: {kw}", flush=True)
    top = res[0][2]
    top2 = next(kw for m, fi, kw in res if kw["drive_x"] == 1.0)                 # the best at the present beat
    print(f"   eat-most: {top}; eat-most at the present beat: {top2} [{time.time() - t0:.0f} s]", flush=True)
    bfast = []
    print("== the bank's parts told nothing else, with the same scalings of its movements, in plain: efficiency, meals a second", flush=True)
    for kw in (dict(), dict(hold_x=2.0), dict(hold_x=4.0), dict(scan_x=2.0), dict(scan_x=2.0, hold_x=2.0), dict(drive_x=2.0, scan_x=2.0), dict(drive_x=2.0, scan_x=2.0, hold_x=2.0), dict(bored_x=0.25, scan_x=2.0, hold_x=2.0)):
        L = A.run("plain", "bankeye", TUNE, kw)
        m = np.mean([len(l.mt) for l in L]) / 100
        print(f"   {kw}: efficiency {A.efficiency(L):.2f}, {m:.2f} meals a second", flush=True)
        bfast.append((m, kw))
    bkw = max(bfast, key=lambda x: x[0])[1]
    print(f"   chosen fast bank: {bkw}", flush=True)
    POL = [("bank", "bankeye", {}), ("fast bank", "bankeye", bkw), ("unwired", "ureye", {}), ("eat-most at this beat", "ureye", top2), ("eat-most", "ureye", top)]
    JJ = range(62000, 62200)
    out = {}
    print("\n== usable evidence, 62000-62199 x 2, half the seeds to learn the table, half to score it. Rate: tastes a second with a known rule colour. (i) 1b's method: attributed within 0.3 s, e, bits/s. (ii) the table's bits/s with all tastes [95%]. (iii) the decoder's chance of naming the colour by 5, 10, 30 s, with its own claimed confidence.", flush=True)
    for w in ("plain", "unreliable", "digest", "patchy", "weak", "noisy", "swap10", "alternate"):
        out[w] = {}
        for name, arm, kw in POL:
            L = A.run(w, arm, JJ, kw)
            c = channel(L)
            out[w][name] = c
            print(f"   {w:10s} {name:22s} tastes {c['taste']:.2f}/s; (i) scored {c['scored']:.2f}/s, e {c['e']:.3f} [{c['e_ci'][0]:.3f},{c['e_ci'][1]:.3f}], {c['I1']:.3f} bits a taste, {c['bps1']:.3f} [{c['bps1_ci'][0]:.3f},{c['bps1_ci'][1]:.3f}] bits/s; (ii) {c['bps2']:.3f} [{c['bps2_ci'][0]:.3f},{c['bps2_ci'][1]:.3f}] bits/s, {c['per_taste']:.3f} a taste, KL rate {c['kl']:.3f}; (iii) right by 5/10/30 s " + "/".join(f"{c['acc'][k]:.3f}" for k in (5, 10, 30)) + " claims " + "/".join(f"{c['conf'][k]:.3f}" for k in (5, 10, 30)) + f" [{time.time() - t0:.0f} s]", flush=True)
    with open(A.OUT + "channels.pkl", "wb") as f:
        pickle.dump(out, f)


def tables():
    ch = pickle.load(open(A.OUT + "channels.pkl", "rb"))
    orc = pickle.load(open(A.OUT + "oracle.pkl", "rb"))
    W_ = 0.9 * math.log2(0.95 / 0.05)

    def kl(e):
        return (1 - 2 * e) * math.log2((1 - e) / e)

    def bh(e):
        return -math.log2(2 * math.sqrt(e * (1 - e)))

    def lie_limit(n):
        lo, hi = 0.001, 0.4999
        for _ in range(60):
            m = (lo + hi) / 2
            lo, hi = (m, hi) if kl(m) * n > W_ else (lo, m)
        return lo
    rate = dict(bank=ch["plain"]["bank"]["taste"], unwired=ch["plain"]["unwired"]["taste"], eat=ch["plain"]["eat-most"]["taste"], fast=ch["plain"]["fast bank"]["taste"])
    pb = {R: min(100.0, meals_bound(L_ONE * 2 * R * 100) / 100) for R in (50, 100)}
    RATES = [("bank (measured)", rate["bank"]), ("fast bank (measured)", rate["fast"]), ("unwired (measured)", rate["unwired"]), ("eat-most, wires only (measured)", rate["eat"]), (f"oracle, R=50 (measured; not a brain)", orc[50][1]), (f"oracle, R=100 (measured; not a brain)", orc[100][1]), (f"PROVED, R=50 (upper bound, cap assumed)", pb[50]), (f"PROVED, R=100", pb[100]), ("the tick (upper bound, unconditional)", 100.0)]
    print(f"== Wald: {W_:.2f} bits for one pair at 5% both ways; any test, sequential too. Largest lie rate one pair disagreeing on every taste can stand, and seconds for a rare disagreement. No attribution error at all in this table: a learner's own attribution only adds lies, so these are the generous figures.", flush=True)
    for nm, r in RATES:
        print(f"   {nm}, {r:.2f} tastes/s: lie limit by 10/30/100 s {lie_limit(r * 10):.3f} {lie_limit(r * 30):.3f} {lie_limit(r * 100):.3f}; s for e .025 on 1% {W_ / kl(.025) / .01 / r:.1f}, e .2 on 5% {W_ / kl(.2) / .05 / r:.1f}, e .35 on 20% {W_ / kl(.35) / .2 / r:.1f}, e .45 on 1% {W_ / kl(.45) / .01 / r:.0f}, e .49 on 100% {W_ / kl(.49) / r:.0f}", flush=True)
    print("\n== Fano: log2 N <= (bits + 1) / (1 - Pe), Pe .05, at 10/30/100 s; bits as measured for each policy through its wires ((ii): a lower bound on what the features carry) and the ceiling (rate x (1 - H(lie rate of the world)), attribution perfect, for the proved rate).", flush=True)
    lies = dict(plain=0.0, unreliable=0.2, digest=None, patchy=0.0, weak=0.0, noisy=0.0)
    for w in ("plain", "unreliable", "digest", "patchy", "weak", "noisy"):
        out = []
        for nm in ("bank", "fast bank", "unwired", "eat-most"):
            b = max(ch[w][nm]["bps2"], ch[w][nm]["bps1"])
            out.append(f"{nm} {b:.3f} bits/s: " + "/".join(f"{(b * T_ + 1) / .95:.1f}" for T_ in (10, 30, 100)))
        print(f"   {w:10s} " + " | ".join(out), flush=True)
    print("   ceiling for any brain, one lie in five (unreliable): taste rate x (1 - H(.2)) = rate x 0.278:", flush=True)
    for nm, r in RATES:
        print(f"     {nm}: {r * 0.278:.2f} bits/s, log2 N <= " + "/".join(f"{(r * .278 * T_ + 1) / .95:.0f}" for T_ in (10, 30, 100)), flush=True)
    print("   digest: any taste within 1 s of the last is bad whatever its colour, so at most one informative taste a second, whatever the brain's speed: at most 100 a life, 1 - H(lie) bits each. Proved, for the world as written.", flush=True)
    print("\n== Union estimate: log2 N reached at Pe .05, pairs disagreeing on half of tastes, each lied about independently: n rho B - log2 20. An estimate.", flush=True)
    for w, e0 in (("plain", None), ("unreliable", None), ("patchy", None)):
        for nm in ("bank", "fast bank", "unwired", "eat-most"):
            c = ch[w][nm]
            e = max(c["e"], 1e-3)
            B_ = bh(e)
            r = c["scored"]
            print(f"   {w:10s} {nm:12s} e {e:.3f}, scored {r:.2f}/s: " + "/".join(f"{r * T_ * .5 * B_ - math.log2(20):+.1f}" for T_ in (10, 30, 100)) + f" (10/30/100 s); {1 / (.5 * B_ * r):.1f} s per doubling", flush=True)
    print("\n   D31's 1.9 s (plain) and 11.8 s (unreliable) a doubling, at the bank's rate, against the best measured above.", flush=True)


if __name__ == "__main__":
    dict(bound=bound, oracle=oracle, policies=policies, tables=tables)[sys.argv[1]]()

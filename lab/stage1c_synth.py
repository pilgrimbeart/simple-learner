"""stage1c_synth.py: stage 1c part 5. Synthetic controls (lab/synth_controls.py, unchanged, reused) with novel worlds that can't be fully passed, and candidate pass definitions compared.

A world now has a ceiling c: the most of the gap to told that any learner can close (known here; in life, estimated by a reference). A working cure reaches c x Beta(8,2), one not working c x Beta(1,9), so the old populations are c = 1. D31's numbers set the range: in unreliable the best selector among the seven closes 55% of the gap to told, the bank 43%, so 78% of its ceiling: Beta(8,2)'s mean is 80%.

Populations: a share s of worlds are capped, c ~ U(.2, .5); a share u unlearnable, c = 0; the rest c ~ U(.6, 1). (c = 1 for all, s = u = 0: the control, which reproduces synth_controls.run exactly.)

Each definition is a per-world threshold on the measured closure x:
  told:      x > .5                                     the adopted rule (PROGRAMME.md)
  ref:       x > .5 r if r >= .2, else x > -.2 (no harm)     r the reference's measured closure, measured once with its own se
  refloor:   as ref, and x > .25 too                    a floor on closure to told, a guard against a weak reference
  told/ceil: told's F_novel divided by the reference's own F_novel under told's threshold; judged the same way

Truth: yes for q >= .7 ("the design's cures work on that share of what can be cured"), no for q = 0, in between otherwise. So capped worlds where a working cure reaches its ceiling count as cured by construction: the truth is about the design, not about how hard the world is.

    .venv/bin/python lab/stage1c_synth.py control|table|gaming|nine"""
import json
import math
import os
import pickle
import sys
import time
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from collections import defaultdict
from multiprocessing import Pool
import numpy as np
import synth_controls as S

N, REPS = 225, 200
BIG = S.BIG


def ceilings(rng, n, s, u, flat):
    """Each world's ceiling, from a stream of its own so that the main stream is untouched."""
    if flat:
        return np.ones(n)
    c = rng.uniform(0.6, 1.0, n)
    r = rng.random(n)
    c[r < s + u] = rng.uniform(0.2, 0.5, (r < s + u).sum())
    c[r < u] = 0.0
    return c


def thresh(defn, r):
    if defn in ("told", "told/ceil"):
        return np.full(len(r), S.THRESHOLD)
    t = np.where(r >= 0.2, 0.5 * r, -0.2)
    if defn == "refloor":
        t = np.where(r >= 0.2, np.maximum(0.5 * r, 0.25), -0.2)
    return t


def measured(true_on, se, rng, work, notwork, th):
    val = np.where(true_on, work, notwork)
    return val + se * rng.standard_normal(true_on.shape) > th


def design(pool_cures, se, rng, work, notwork, th):
    """synth_controls.design with per-world values and thresholds."""
    cands = sorted({c for cs in pool_cures for c in cs})
    idx = {c: i for i, c in enumerate(cands)}
    n = len(pool_cures)
    A = np.zeros((n, len(cands)), bool)
    for i, cs in enumerate(pool_cures):
        for c in cs:
            A[i, idx[c]] = True
    truth = A
    if se > 0:
        A = measured(A, se, rng, work[:, None], notwork[:, None], th[:, None])
    uncovered, used, order = np.ones(n, bool), np.zeros(len(cands), bool), []
    covered = np.zeros(n, bool)
    tie = rng.random(len(cands)) * 0.5
    while uncovered.any():
        gain = A[uncovered].sum(0) + tie
        gain[used] = -1
        j = int(gain.argmax())
        if gain[j] < 1:
            break
        order.append(cands[j])
        used[j] = True
        covered |= truth[:, j]
        uncovered = ~measured(covered, se, rng, work, notwork, th)
    return order


def run(spec, M, se, seed, defn="told", s=0.0, u=0.0, flat=False, rho=1.0, se_r=None, half=False, harm=0.0, still=0.0, N=N, stopcure=False):
    """rho: the reference reaches rho x the true ceiling (1: honest; below: a reference that flatters). half: a cure not working still gets c x Beta(5,10), a third. harm: the design's value in unlearnable worlds, against 0 for base. still: share of worlds with a very negative base where the design's stop-eating cure reaches U(.3,.75) of the gap to told, with no learning."""
    rng = np.random.default_rng(seed)
    r2 = np.random.default_rng(seed + 77_000_000)
    pool_cl, pool_cures = S.draw(spec, rng, N)
    fresh_cl, fresh_cures = S.draw(spec, rng, M)
    se_r = se if se_r is None else se_r

    def worlds(n):
        c = ceilings(r2, n, s, u, flat)
        ref = rho * c + se_r * r2.standard_normal(n) if defn != "told" else c
        st = np.where(r2.random(n) < still, r2.uniform(0.3, 0.75, n), -9.0)
        return c, ref, thresh(defn, ref), st
    c_p, ref_p, th_p, st_p = worlds(N)
    c_f, ref_f, th_f, st_f = worlds(M)

    def eff(n, c, st):
        w, nw = (rng.beta(8, 2, n), rng.beta(1, 9, n))
        nonlocal fn0
        fn0 = c * nw                                    # what the base gets: a design's half-working cure is the design's alone (corrected: see gaming2)
        if half:
            nw = r2.beta(5, 10, n)
        return c * w, c * nw, np.maximum(c * nw, st), np.maximum(c * w, st)
    fn0 = None
    ew, en, en_s, ew_s = eff(N, c_p, st_p)
    order = design(pool_cures, se, rng, ew_s if still else ew, en_s if still else en, th_p)
    rank = {c: i for i, c in enumerate(order)}
    C = len(order)
    pf, ff = S.first_cure(pool_cures, rank), S.first_cure(fresh_cures, rank)
    fw, fn, fn_s, fw_s = eff(M, c_f, st_f)
    fn0_f = fn0
    pw, pn, pn_s, pw_s = eff(N, c_p, st_p)
    fn0_p = fn0
    fn0 = fn0_f
    base_nw = fn0 if half else fn
    base_f = measured(np.zeros(M, bool), se, rng, fw, base_nw, th_f)
    finalv_w, finalv_n = (fw_s, fn_s) if still else (fw, fn)
    if harm:
        finalv_w, finalv_n = np.where(c_f == 0, -harm, finalv_w), np.where(c_f == 0, -harm, finalv_n)
    final_f = measured(ff < C, se, rng, finalv_w, finalv_n, th_f)
    # (the curve in synth_controls.run draws noise here; keep the stream the same for the control)
    for c_ in range(C + 1):
        measured(ff < c_, se, rng, fw, fn, th_f)
    novel = ~np.isin(fresh_cl, pool_cl)
    x, b = S.by_cluster(fresh_cl[novel], final_f[novel].astype(float), base_f[novel].astype(float)) if novel.any() else (np.zeros(0), np.zeros(0))
    n_novel = len(x)
    F, F_ci = (float(S.f_corr(x, b)), S.boot(S.f_corr, (x, b), rng)) if n_novel else (float("nan"), (float("nan"),) * 2)
    if defn == "told/ceil" and n_novel:
        # the reference's own F under told's threshold: the ceiling the circuit is judged against
        ref_pass = ref_f + se_r * r2.standard_normal(M) > S.THRESHOLD
        xr, br = S.by_cluster(fresh_cl[novel], ref_pass[novel].astype(float), base_f[novel].astype(float))

        def ratio(x_, b_, xr_):
            return S.f_corr(x_, b_) / np.maximum(S.f_corr(xr_, b_), 0.05)
        I = rng.integers(n_novel, size=(300, n_novel))
        v = ratio(x[I], b[I], xr[I])
        F = float(ratio(x, b, xr))
        F_ci = np.percentile(v, [2.5, 97.5])
    y, by = S.by_cluster(pool_cl, measured(pf < C, se, rng, pw, pn, th_p).astype(float), measured(np.zeros(N, bool), se, rng, pw, fn0_p if half else pn, th_p).astype(float))
    D = S.cost(order, None)
    if stopcure:                                        # one cheap cure, no others: stops eating when things go badly. Costs one cure's description
        y = measured(np.zeros(N, bool), se, rng, pw, pn_s, th_p).astype(float)
        by = measured(np.zeros(N, bool), se, rng, pw, fn0_p if half else pn, th_p).astype(float)
        final_f = measured(np.zeros(M, bool), se, rng, fw, fn_s, th_f)
        x, b = S.by_cluster(fresh_cl[novel], final_f[novel].astype(float), base_f[novel].astype(float))
        F, F_ci = float(S.f_corr(x, b)), S.boot(S.f_corr, (x, b), rng)
        D = S.C_REF
    R_fn = lambda y, b: D / (S.C_REF * np.maximum((y - b).sum(-1), 1e-9))
    R = float(R_fn(y, by))
    R_ci = S.boot(R_fn, (y, by), rng)
    return dict(F=F, F_lo=float(F_ci[0]), F_hi=float(F_ci[1]), R=R, R_hi=float(R_ci[1]), n_novel=n_novel, share=float(novel.mean()), C=C, f0=float(b.mean()) if n_novel else 0.0, x=float(x.mean()) if n_novel else 0.0)


def _one(job):
    tag, kw = job
    return tag, run(**kw)


def batch(conds, reps=REPS, base_seed=0, workers=7):
    jobs = [(t, dict(kw, seed=base_seed + i * 100_000 + r)) for i, (t, kw) in enumerate(conds.items()) for r in range(reps)]
    out = defaultdict(list)
    with Pool(workers) as p:
        for t, r in p.imap_unordered(_one, jobs, chunksize=4):
            out[t].append(r)
    return out


def rates(rs):
    v = [S.verdict(r) for r in rs]
    n = len(v)
    yes = sum(x == "YES" for x in v) / n
    no = sum(x.startswith("NO") for x in v) / n
    return yes, no, 1 - yes - no, float(np.median([r["F"] for r in rs]))


def wilson(k, n):
    z = 1.96
    p = k / n
    d = 1 + z * z / n
    m = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return m - h, m + h


QS = [("q=0 (no)", ("general", dict(m=30, q=0.0))), ("q=.3 (between)", ("general", dict(m=30, q=0.3))), ("q=.5 (between)", ("general", dict(m=30, q=0.5))), ("q=.7 (yes)", ("general", dict(m=30, q=0.7))), ("q=.85 (yes)", ("general", dict(m=30, q=0.85))), ("q=1 (yes)", ("general", dict(m=30, q=1.0)))]


def control():
    print("== control: c = 1 everywhere, told's threshold: lab/stage1c_synth.run against synth_controls.run on the same seed. F_novel, its interval, R must match exactly.", flush=True)
    bad = 0
    for name, spec in QS:
        for seed in range(5):
            a = S.run(spec, 225, 75, 0.2, seed, partial=True)
            b = run(spec, 75, 0.2, seed, defn="told", flat=True)
            ok = abs(a["F"] - b["F"]) < 1e-12 and abs(a["F_lo"] - b["F_lo"]) < 1e-12 and abs(a["R"] - b["R"]) < 1e-12 and a["C"] == b["C"] and a["n_novel"] == b["n_novel"]
            bad += not ok
            if seed == 0:
                print(f"   {name}: synth_controls F {a['F']:.4f} [{a['F_lo']:.3f},{a['F_hi']:.3f}] R {a['R']:.3f}; here F {b['F']:.4f} [{b['F_lo']:.3f},{b['F_hi']:.3f}] R {b['R']:.3f}", flush=True)
    print(f"   mismatches: {bad} of {len(QS) * 5}", flush=True)
    print("== old section 5 rates reproduce? (synth_controls s5 at N 225, M 75, se .2, the verdicts through this file's run with flat ceilings; compare with lab/v/synth_controls.log's 5.)", flush=True)
    res = batch({name: dict(spec=spec, M=75, se=0.2, defn="told", flat=True) for name, spec in QS})
    for name, _ in QS:
        y, n, m, f = rates(res[name])
        print(f"   {name}: yes {y:.2f} no {n:.2f} between {m:.2f} median F {f:.2f}", flush=True)


def table():
    t0 = time.time()
    defs = ("told", "ref", "refloor", "told/ceil")
    print(f"== Yes / No / between, at N = {N}, {REPS} runs each (95% Wilson half-width about .07 at .5, .02 at 0). Rows q; columns capped share. se .2, reference honest (rho 1) with its own se = se. Truth yes for q >= .7, no for q = 0.", flush=True)
    for M in (36, 75, 150):
        for u in (0.0, 0.1):
            print(f"\n-- M {M} novel worlds, unlearnable share {u}", flush=True)
            for d in defs:
                res = batch({(name, s): dict(spec=spec, M=M, se=0.2, defn=d, s=s, u=u) for name, spec in QS for s in (0.0, 0.1, 0.25, 0.5)}, base_seed=int(1000 * M + 1e7 * u))
                print(f"   {d}:", flush=True)
                for name, _ in QS:
                    print(f"      {name:16s} " + "  ".join(f"s{s}: {rates(res[(name, s)])[0]:.2f}/{rates(res[(name, s)])[1]:.2f}/{rates(res[(name, s)])[2]:.2f} F {rates(res[(name, s)])[3]:+.2f}" for s in (0.0, 0.1, 0.25, 0.5)), flush=True)
                print(f"      [{time.time() - t0:.0f} s]", flush=True)
    print("\n== se: 75 novel worlds, s .25, u .1", flush=True)
    for se in (0.1, 0.3, 0.4):
        for d in defs:
            res = batch({name: dict(spec=spec, M=75, se=se, defn=d, s=0.25, u=0.1) for name, spec in QS}, base_seed=int(se * 1e7))
            print(f"   se {se} {d}: " + " ".join(f"{name.split()[0]} {rates(res[name])[0]:.2f}/{rates(res[name])[1]:.2f}" for name, _ in QS), flush=True)


def gaming():
    print("== gaming a reference: rho = the reference reaches rho x the true ceiling (a narrow or mis-specified prior). half: non-working cures reach a third of the ceiling. M 75, s .25, u .1, se .2. Yes/No/between, median F", flush=True)
    for half in (False, True):
        for rho in (1.0, 0.7, 0.5, 0.3):
            for d in ("ref", "refloor", "told/ceil"):
                res = batch({name: dict(spec=spec, M=75, se=0.2, defn=d, s=0.25, u=0.1, rho=rho, half=half) for name, spec in QS}, base_seed=int(rho * 1e6) + 3 * half)
                print(f"   half {half} rho {rho} {d}: " + " ".join(f"{name.split()[0]} {rates(res[name])[0]:.2f}/{rates(res[name])[1]:.2f}/F{rates(res[name])[3]:+.2f}" for name, _ in QS), flush=True)
        res = batch({name: dict(spec=spec, M=75, se=0.2, defn="told", s=0.25, u=0.1, half=half) for name, spec in QS}, base_seed=int(9e6) + 3 * half)
        print(f"   half {half} told (no reference): " + " ".join(f"{name.split()[0]} {rates(res[name])[0]:.2f}/{rates(res[name])[1]:.2f}/F{rates(res[name])[3]:+.2f}" for name, _ in QS), flush=True)
    print("\n== harm: the design scores -.3 of a gap in unlearnable worlds (share .25), base 0. Does F_novel notice? M 75, s 0, q .85", flush=True)
    for d in ("told", "ref", "refloor"):
        for harm in (0.0, 0.3, 0.6):
            res = batch({"x": dict(spec=QS[4][1], M=75, se=0.2, defn=d, s=0.0, u=0.25, harm=harm)})
            y, n, m, f = rates(res["x"])
            print(f"   {d} harm {harm}: yes {y:.2f} no {n:.2f} between {m:.2f} median F {f:+.2f}", flush=True)
    print("\n== the still creature: a share of worlds have a base so negative that never eating closes U(.3,.75) of the gap to told (alternate .56, digest .73, pattern .50 by D31's numbers). A design with one stop-eating cure and no general cure (q = 0). Told's gap measured from base. M 75, se .2", flush=True)
    for still in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
        res = batch({d: dict(spec=QS[0][1], M=75, se=0.2, defn=d, s=0.0, u=0.0, still=still) for d in ("told", "ref", "refloor")}, base_seed=int(still * 1e6))
        print(f"   share {still}: " + " ".join(f"{d} {rates(res[d])[0]:.2f}/{rates(res[d])[1]:.2f}/F{rates(res[d])[3]:+.2f}" for d in ("told", "ref", "refloor")), flush=True)


def gaming2():
    """A correction to gaming(): there the base shared a design's half-working cures, so they cancelled in F_novel and a flattering reference looked harmless. Here a half-working cure is the design's alone, on every novel world; and the stop-eating design is one cure (R small), not a pool of them."""
    print("== half-working cures, the design's alone: every world not cured reaches c x Beta(5,10), a third of its ceiling. M 75 and 36, s .25, u .1, se .2. Yes/No/between in order Y/N, median F. q=0 here is a design with no real cure, one that gets a third of every ceiling.", flush=True)
    for M in (75, 36):
        for rho in (1.0, 0.7, 0.5, 0.3):
            for d in ("ref", "refloor"):
                res = batch({name: dict(spec=spec, M=M, se=0.2, defn=d, s=0.25, u=0.1, rho=rho, half=True) for name, spec in QS}, base_seed=int(rho * 1e6) + M)
                print(f"   M {M} rho {rho} {d}: " + " ".join(f"{name.split()[0]} {rates(res[name])[0]:.2f}/{rates(res[name])[1]:.2f}/F{rates(res[name])[3]:+.2f}" for name, _ in QS), flush=True)
        res = batch({name: dict(spec=spec, M=M, se=0.2, defn="told", s=0.25, u=0.1, half=True) for name, spec in QS}, base_seed=int(9e6) + M)
        print(f"   M {M} told: " + " ".join(f"{name.split()[0]} {rates(res[name])[0]:.2f}/{rates(res[name])[1]:.2f}/F{rates(res[name])[3]:+.2f}" for name, _ in QS), flush=True)
    print("\n== the same with only cheap general cures: q = 1 general m=5 would be a yes anyway; instead the false-yes check, a design of few general cures that each only half work: spec m=5, q=1, working effect replaced? Not modelled; see q=0 lines' F. ", flush=True)
    print("\n== the stop-eating design, one cure, no learning. A share of worlds have a base so negative that never eating closes U(.3,.75) of the gap. M 75 and 36, se .2. Told's gap measured from base, Y/N/F; with the still creature in the base (the gap from max(base, 0)) never eating closes nothing, so F is 0 by construction.", flush=True)
    for M in (75, 36):
        for still in (0.2, 0.4, 0.6, 0.8, 1.0):
            res = batch({d: dict(spec=QS[0][1], M=M, se=0.2, defn=d, flat=True, still=still, stopcure=True) for d in ("told",)}, base_seed=int(still * 1e6) + M)
            print(f"   M {M} share {still}: told {rates(res['told'])[0]:.2f}/{rates(res['told'])[1]:.2f}/F{rates(res['told'])[3]:+.2f}, median R {np.median([r['R'] for r in res['told']]):.3f}", flush=True)


def gaming3():
    """The false yes that gaming2 couldn't show, since many own cures made R large: ONE cheap cure that half works on every world, reaching a third of each ceiling (c x Beta(5,10)) with no learning of any rule, R small."""
    print("== one half-working cure, cheap. Yes/No/between in order Y/N, median F, median R. s .25, u .1 and s 0, u 0; se .2 and .1", flush=True)
    for M in (75, 36):
        for s_, u_ in ((0.25, 0.1), (0.0, 0.0)):
            for se in (0.2, 0.1):
                res = batch({(d, rho): dict(spec=QS[0][1], M=M, se=se, defn=d, s=s_, u=u_, rho=rho, half=True, stopcure=True) for d, rho in (("told", 1.0), ("ref", 1.0), ("ref", 0.7), ("ref", 0.5), ("ref", 0.3), ("refloor", 1.0), ("refloor", 0.7), ("refloor", 0.5), ("refloor", 0.3))}, base_seed=M + int(1000 * se))
                print(f"   M {M} s {s_} u {u_} se {se}: " + " | ".join(f"{d} rho {rho}: {rates(r)[0]:.2f}/{rates(r)[1]:.2f}/F{rates(r)[3]:+.2f}/R{np.median([x['R'] for x in r]):.3f}" for (d, rho), r in sorted(res.items())), flush=True)


# ---------------------------------------------------------------- real lives: coin-flip taste; the still creature's closure in the nine worlds
def nine():
    import bits_bank as B
    import stage1c_arms as A
    import table as T
    from minimal.spec import efficiency

    class StopBrain(B.Recorder):
        """The bank, and an exact posterior between 'the sign of a scored taste follows a colour rule, lying with chance e' (either colour) and 'it is a fair coin, whatever the colour' (prior `pc`). Past `stop` of posterior on the coin it stops moving. Ideal among those three hypotheses, as far as the decision to stop goes; a ceiling, not a circuit. It keeps listening to nothing once still."""

        def __init__(self, seed, p):
            super().__init__(seed, p)
            self.lp = np.log(np.array([p.get("pc", 0.2), (1 - p.get("pc", 0.2)) / 2, (1 - p.get("pc", 0.2)) / 2]))
            self.ee = p.get("ee", 0.2)
            self.stopped = False

        def taste(self, value, at):
            scored, truth, _ = self.about(value)
            if scored:
                e = self.ee
                self.lp += np.log([0.5, (1 - e) if truth == 0 else e, (1 - e) if truth == 1 else e])
                self.lp -= self.lp.max()
                post = np.exp(self.lp) / np.exp(self.lp).sum()
                if post[0] > self.p.get("stop", 0.9):
                    self.stopped = True
            super().taste(value, at)

        def step(self):
            out = super().step()
            return [] if self.stopped else out

    T.ARMS["stopper"] = StopBrain
    J = range(62000, 62100)
    print("== coin-flip taste: each meal poison by a fair coin. Efficiency [95%] over 100 seeds x 2; meals a life. A meal's expected worth is 0.5 - 2 x 0.5 = -0.5, so any eating scores below 0. Seconds: 100.", flush=True)
    res = {}
    for name, fn in (("base circuit", lambda w: A.run_plain(w, "circuit", J)), ("bank", lambda w: A.run(w, "v_rec", J)), ("unwired", lambda w: A.run_plain(w, "unwired", J)), ("still", lambda w: A.run_plain(w, "still", J)), ("stopper (e .2, stop at .9)", lambda w: A.run(w, "stopper", J)), ("stopper (stop at .99)", lambda w: A.run(w, "stopper", J, dict(stop=0.99)))):
        L = fn("coin")
        v = A.eff_ci(L)
        res[name] = L
        meals = np.mean([sum(a + b for a, b, _ in l) for l in L])
        print(f"   {name}: {v[0]:.3f} [{v[1]:.3f},{v[2]:.3f}], meals {meals:.1f}", flush=True)
    print("   the stopper against base:", A.fmt_d(A.pdiff(res["stopper (e .2, stop at .9)"], res["base circuit"])), "; bank against base:", A.fmt_d(A.pdiff(res["bank"], res["base circuit"])), flush=True)
    print("== the same stopper in worlds with something to learn: does a brain that may stop lose there? Against the bank, paired, 100 seeds x 2", flush=True)
    for w in ("plain", "unreliable", "alternate", "digest", "swap10"):
        L, b = A.run(w, "stopper", J), A.run(w, "v_rec", J)
        print(f"   {w}: {A.efficiency(L):.3f}, against the bank {A.fmt_d(A.pdiff(L, b))}; stopped in {np.mean([l.mt.size == 0 or l.ft.max() < 9000 for l in L]):.2f} of lives", flush=True)
    print("== the still creature in the nine worlds. base and told on 100 seeds x 2 (told: the bank's parts told the colour). Closure if measured from base: (0 - base) / (told - base). Rows where the base is below 0: a learning-free stop could pass at half the gap.", flush=True)
    for w in B.WORLDS9:
        bs, td = A.efficiency(A.run_plain(w, "circuit", J)), A.efficiency(A.run(w, "vtold", J))
        s = A.efficiency(A.run_plain(w, "still", J))
        print(f"   {w}: base {bs:.2f}, told {td:.2f}, still {s:.3f}, closure by standing still {(s - bs) / (td - bs):+.2f}" + (" PASSES at half" if (s - bs) / (td - bs) > 0.5 else ""), flush=True)


if __name__ == "__main__":
    dict(control=control, table=table, gaming=gaming, gaming2=gaming2, gaming3=gaming3, nine=nine)[sys.argv[1]]()

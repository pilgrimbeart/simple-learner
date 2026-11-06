"""Stage 1 of PROGRAMME.md: can the analysis tell the truth? Invented data with known answers, no creature.

One pipeline, as the plan has it: draw a training pool; a designer adds cures greedily to the largest uncovered group
(seeing each world's success through noise); measure coverage on fresh draws from the same population.

A world is (cluster, cures). `cures` is what works on it. `cluster` is what a cure-blind look at the world says it is
(a stand-in for the programme's skeleton and wire signature): two worlds in one cluster count as one challenge. Types
in population 1 are clusters; population 6 has the same cure matrix with every world its own cluster.

Run from the repository root: .venv/bin/python lab/synth_controls.py | tee lab/v/synth_controls.log
"""
import hashlib
import json
import lzma
import math
import sys
import time
from collections import defaultdict
from multiprocessing import Pool

import numpy as np

THRESHOLD = 0.5  # a world passes if its measured fraction of the gap closed is above this
BIG = 1 << 50
C_REF = 1000.0   # bits: the frozen stand-alone size of a cure (see the report); invented here


# ---------------------------------------------------------------- populations
# Each draw(rng, n) returns clusters (int array) and cures (list of tuples of ints). Costs: (motif, copy) bits.

def uid(rng, n):
    return rng.integers(1, BIG, n)


def p_types(rng, n, K, zipf=0.0, fine=False):
    """K types, each needing its own cure. zipf 0: equal frequency. fine: every world its own cluster."""
    p = np.arange(1, K + 1, dtype=float) ** -zipf
    t, u = rng.choice(K, n, p=p / p.sum()), uid(rng, n)
    return (u if fine else t), [(int(x),) for x in t]


def p_own(rng, n):
    """Every world truly needs its own cure."""
    u = uid(rng, n)
    return u, [(int(x),) for x in u]


def p_variants(rng, n, fam=5, var=20, share=1.0, fine=False):
    """A few families, many variants (gain 1.2, 1.3). A variant shares its family's cure with chance `share` (fixed
    per variant), else has its own. Skeleton clustering (fine False): one challenge per family."""
    f, v = rng.integers(fam, size=n), rng.integers(var, size=n)
    shared = [(hash_u(a, b) < share) for a, b in zip(f, v)]
    cures = [(int(a),) if s else (int(1000 + a * var + b),) for a, b, s in zip(f, v, shared)]
    return (f * var + v if fine else f), cures


def hash_u(a, b):
    return int(hashlib.md5(f"{a},{b}".encode()).hexdigest()[:8], 16) / 2**32


def p_general(rng, n, m=30, q=1.0, second=0.0):
    """Every world looks new. With chance q a general cure (one of m) works on it, else only its own does. `second`:
    chance a further general cure also works (cures overlap)."""
    cl = uid(rng, n)
    cures = []
    for u, g, a, b, c in zip(cl, rng.random(n), rng.integers(m, size=n), rng.integers(m, size=n), rng.random(n)):
        if g >= q:
            cures.append((int(u),))
        else:
            cures.append((int(a), int(b)) if c < second else (int(a),))
    return cl, cures


POPS = {"types": p_types, "own": p_own, "variants": p_variants, "general": p_general}


def draw(spec, rng, n):
    return POPS[spec[0]](rng, n, **spec[1])


def cost(order, model):
    """Description of a list of cures. model None: all different, C_REF each. (m, M, p): m motifs, M bits once, p a copy."""
    if model is None:
        return C_REF * len(order)
    m, M, p = model
    return M * len({c % m for c in order}) + p * len(order)


# ---------------------------------------------------------------- the pipeline

def measured(true_on, se, rng, partial=None):
    """Pass or fail per entry of a bool array. partial: a world's effect when working, its value when not (arrays)."""
    val = true_on.astype(float) if partial is None else np.where(true_on, partial[0], partial[1])
    return val + se * rng.standard_normal(true_on.shape) > THRESHOLD


def first_cure(cures, rank):
    """For each world, the position in the order of the earliest cure that works on it."""
    return np.array([min((rank.get(c, BIG) for c in cs), default=BIG) for cs in cures])


def effects(rng, n, partial):
    return (rng.beta(8, 2, n), rng.beta(1, 9, n)) if partial else None


def split(cl, e, rng):
    """A false split: a duplicate's signature looks new with chance e."""
    if e <= 0:
        return cl
    return np.where(rng.random(len(cl)) < e, uid(rng, len(cl)) + BIG, cl)


def design(pool_cures, se, rng, partial, retest=True):
    """Greedy: the cure measured to work on the most still-uncovered pool worlds, until none is left. Returns the order
    and the designer's own view of pool coverage after each cure. A candidate's group comes from one noisy look at it.
    retest: as the plan has it, every pool world is re-run on the cumulative circuit after each addition, so what counts
    as uncovered is measured afresh; without it, a world once seen to pass is never looked at again."""
    cands = sorted({c for cs in pool_cures for c in cs})
    idx = {c: i for i, c in enumerate(cands)}
    n = len(pool_cures)
    A = np.zeros((n, len(cands)), bool)
    for i, cs in enumerate(pool_cures):
        for c in cs:
            A[i, idx[c]] = True
    truth = A
    if se > 0:
        p = None if partial is None else (partial[0][:, None], partial[1][:, None])
        A = measured(A, se, rng, p)
    uncovered, used, order, seen = np.ones(n, bool), np.zeros(len(cands), bool), [], []
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
        if retest:
            uncovered = ~measured(covered, se, rng, partial)
        else:
            uncovered &= ~A[:, j]
        seen.append(1 - uncovered.mean())
    return order, np.array(seen)


def by_cluster(cl, *values):
    _, inv = np.unique(cl, return_inverse=True)
    w = np.bincount(inv)
    return [np.bincount(inv, v) / w for v in values]


def boot(fn, arrays, rng, reps=300):
    n = len(arrays[0])
    i = rng.integers(n, size=(reps, n))
    return np.percentile(fn(*[a[i] for a in arrays]), [2.5, 97.5])


def f_corr(x, b):
    """Coverage on novel challenges above the base circuit's, as a share of what the base leaves."""
    mx, mb = x.mean(-1), b.mean(-1)
    return (mx - mb) / np.maximum(1 - mb, 1e-9)


def run(spec, N, M, se, seed, e=0.0, model=None, partial=False, keep=False, retest=True):
    rng = np.random.default_rng(seed)
    pool_cl, pool_cures = draw(spec, rng, N)
    fresh_cl, fresh_cures = draw(spec, rng, M)
    pool_cl, fresh_cl = split(pool_cl, e, rng), split(fresh_cl, e, rng)
    order, seen = design(pool_cures, se, rng, effects(rng, N, partial), retest)
    rank = {c: i for i, c in enumerate(order)}
    C = len(order)
    pf, ff = first_cure(pool_cures, rank), first_cure(fresh_cures, rank)
    ef, ep = effects(rng, M, partial), effects(rng, N, partial)
    base_f = measured(np.zeros(M, bool), se, rng, ef)
    final_f = measured(ff < C, se, rng, ef)

    # the curve, one fresh measurement per circuit, corrected by the base circuit's measured pass rate
    f0 = base_f.mean()
    curve = np.array([measured(ff < c, se, rng, ef).mean() for c in range(C + 1)])
    corrected = (curve - f0) / max(1 - f0, 1e-9)
    hit = np.nonzero(corrected >= 0.8)[0]
    c80 = int(hit[0]) if len(hit) else None
    hit_raw = np.nonzero(curve >= 0.8)[0]
    c80_raw = int(hit_raw[0]) if len(hit_raw) else None
    hit_t = np.nonzero(seen >= 0.8)[0]
    c80_t = int(hit_t[0]) + 1 if len(hit_t) else None

    # novel challenges: held-out clusters with no twin in the pool
    novel = ~np.isin(fresh_cl, pool_cl)
    x, b = by_cluster(fresh_cl[novel], final_f[novel].astype(float), base_f[novel].astype(float)) if novel.any() else (np.zeros(0), np.zeros(0))
    n_novel = len(x)
    if n_novel:
        F = float(f_corr(x, b))
        F_ci = boot(f_corr, (x, b), rng)
    else:
        F, F_ci = float("nan"), (float("nan"),) * 2

    # handled pool challenges, on seeds the designer never saw
    y, by = by_cluster(pool_cl, measured(pf < C, se, rng, ep).astype(float), measured(np.zeros(N, bool), se, rng, ep).astype(float))
    D = cost(order, model)
    R_fn = lambda y, b: D / (C_REF * np.maximum((y - b).sum(-1), 1e-9))
    R = float(R_fn(y, by))
    R_ci = boot(R_fn, (y, by), rng)

    out = dict(C=C, D=D, c80=c80, c80_raw=c80_raw, c80_t=c80_t, Dc80=None if c80_raw is None else cost(order[:c80_raw], model),
               curve_end=float(curve[-1]), corr_end=float(corrected[-1]), f0=float(f0), F=F, F_lo=float(F_ci[0]), F_hi=float(F_ci[1]),
               R=R, R_hi=float(R_ci[1]), n_novel=n_novel, share=float(novel.mean()), n_pool_cl=len(y))
    if keep:
        out["order"], out["curve"], out["seen"] = order, curve, seen
    return out


def verdict(r, gate_n=30, gate_share=0.5):
    """The proposed rule. EXH: the sampler has too few new challenges to say anything about generality."""
    motif = r["R_hi"] < 0.5
    if r["n_novel"] < gate_n or r["share"] < gate_share:
        return "EXH+M" if motif else "EXH"
    if r["F_lo"] > 0.5 and motif:
        return "YES"
    if r["F_hi"] < 0.2:
        return "NO+M" if motif else "NO"
    return "MID+M" if motif else "MID"


def written_table(r, N):
    """The primary result as written, with the only computable control: one full-cost cure per pool world, so 0.8 N of
    them at 80%. Yes if fresh draw-weighted coverage reached 80% for less than half of that."""
    return r["Dc80"] is not None and r["Dc80"] < 0.5 * 0.8 * N * C_REF


def _one(job):
    tag, kw = job
    return tag, run(**kw)


def batch(conds, reps, base_seed=0):
    """conds: {tag: kwargs}. Returns {tag: [results]}. Seeds differ by condition and rep."""
    jobs = [(t, dict(kw, seed=base_seed + i * 100_000 + r)) for i, (t, kw) in enumerate(conds.items()) for r in range(reps)]
    out = defaultdict(list)
    with Pool(8) as p:
        for t, r in p.imap_unordered(_one, jobs, chunksize=4):
            out[t].append(r)
    return out


def med(rs, k):
    v = [r[k] for r in rs if r[k] is not None and not (isinstance(r[k], float) and math.isnan(r[k]))]
    return float(np.median(v)) if v else float("nan")


def share(rs, k):
    return sum(r[k] is not None for r in rs) / len(rs)


def tally(rs):
    c = defaultdict(int)
    for r in rs:
        c[verdict(r)] += 1
    return " ".join(f"{k}:{100 * v // len(rs)}" for k, v in sorted(c.items()))


FP = lambda se: 0.5 * math.erfc(0.5 / (se * math.sqrt(2))) if se else 0.0


def section(s):
    print(f"\n=== {s} ===", flush=True)


def true_c80(K, s):
    p = np.sort(np.arange(1, K + 1, dtype=float) ** -s)[::-1]
    return int(np.searchsorted(np.cumsum(p / p.sum()), 0.8) + 1)


# ---------------------------------------------------------------- 1. recovery

def s1():
    section("1. Recovery: cures to 80% of fresh draws (draw-weighted, corrected by the base rate), against the known answer")
    print("median C80 / reached 80% in what share of 20 runs; M = 1000 fresh draws. 'truth' from the population itself.")
    Ns, ses = (100, 300, 1000, 3000), (0.0, 0.2, 0.3, 0.5)
    print(f"se (fp): " + "  ".join(f"{s}({FP(s):.3f})" for s in ses))
    for name, z in (("equal", 0.0), ("zipf1", 1.0)):
        for K in (3, 10, 30, 100, 300):
            conds = {(N, se): dict(spec=("types", dict(K=K, zipf=z)), N=N, M=1000, se=se) for N in Ns for se in ses}
            res = batch(conds, 20)
            print(f"{name} K={K} truth {true_c80(K, z)}")
            for se in ses:
                print(f"   se {se}: " + "  ".join(f"N{N}: {med(res[(N, se)], 'c80'):5.0f}/{share(res[(N, se)], 'c80'):.2f}" for N in Ns))

    section("1b. The rest, N = 300, M = 1000, 20 runs")
    conds = {}
    for se in (0.0, 0.2, 0.3, 0.5):
        conds[("own", se)] = dict(spec=("own", {}), N=300, M=1000, se=se)
        for sh in (1.0, 0.5, 0.0):
            conds[(f"variants share {sh}", se)] = dict(spec=("variants", dict(share=sh)), N=300, M=1000, se=se)
    res = batch(conds, 20)
    for t, rs in res.items():
        print(f"{t}: C {med(rs, 'C'):.0f}, end raw {med(rs, 'curve_end'):.3f}, base {med(rs, 'f0'):.3f}, end corrected {med(rs, 'corr_end'):.3f}, "
              f"C80 {med(rs, 'c80'):.0f}/{share(rs, 'c80'):.2f}, designer's own C80 {med(rs, 'c80_t'):.0f}")
    print("truth: own: end corrected 0, C80 undefined. variants (5 families x 20): share 1: 4 cures to 80%; share 0.5: about 35 (5 + 30); share 0: 80.")

    section("1c. Motifs: same coverage, cost differs. K = 1000 own cures from 5 motifs (1000 bits once, 30 a copy), N = 300")
    for label, model in (("motif-built", (5, 1000.0, 30.0)), ("all different", None)):
        rs = batch({label: dict(spec=("types", dict(K=1000)), N=300, M=1000, se=0.2, model=model)}, 20)[label]
        print(f"{label}: C {med(rs, 'C'):.0f}, D {med(rs, 'D'):.0f} bits, known D {(1000 * 5 + 30 * med(rs, 'C')) if model else 1000 * med(rs, 'C'):.0f}, "
              f"F_novel {med(rs, 'F'):.3f}, R {med(rs, 'R'):.3f}, verdicts {tally(rs)}")


# ---------------------------------------------------------------- 2. the control, and the two rules

def s2():
    section("2a. What the control looks like: every world its own cure")
    for N in (100, 300, 1000):
        for se in (0.0, 0.2, 0.3, 0.5):
            rs = batch({"c": dict(spec=("own", {}), N=N, M=1000, se=se)}, 10)["c"]
            print(f"N {N} se {se}: cures {med(rs, 'C'):.0f}; fresh coverage at the end raw {med(rs, 'curve_end'):.3f} (base {med(rs, 'f0'):.3f}), "
                  f"corrected {med(rs, 'corr_end'):+.3f}; reached 80% in {share(rs, 'c80_raw'):.0%}; designer's own view reached 80% at {med(rs, 'c80_t'):.0f} cures")

    section("2b. Same data, opposite truths: population 1 (duplicates) and population 6 (all distinct, shared cure)")
    a = run(("types", dict(K=30)), 300, 1000, 0.0, 7, keep=True)
    b = run(("types", dict(K=30, fine=True)), 300, 1000, 0.0, 7, keep=True)
    print(f"coverage curves on one seed: max |diff| {np.abs(a['curve'] - b['curve']).max():.3f}, cures {a['C']} and {b['C']}: the cure matrices are the same")
    print(f"duplicates: F_novel {a['F']}, novel share {a['share']:.2f}, R {a['R']:.2f}: {verdict(a)}")
    print(f"distinct:   F_novel {b['F']:.2f}, novel share {b['share']:.2f}, R {b['R']:.3f}: {verdict(b)}")

    section("2c. Every population under each rule. N = 300, M = 300, se 0.2, 40 runs")
    P = [("K=3", ("types", dict(K=3)), "no", None), ("K=10", ("types", dict(K=10)), "no", None), ("K=30", ("types", dict(K=30)), "no", None),
         ("K=100", ("types", dict(K=100)), "no", None), ("K=300", ("types", dict(K=300)), "no", None), ("K=3000", ("types", dict(K=3000)), "no", None),
         ("zipf1 K=30", ("types", dict(K=30, zipf=1.0)), "no", None), ("zipf1 K=300", ("types", dict(K=300, zipf=1.0)), "no", None),
         ("zipf1.5 K=3000", ("types", dict(K=3000, zipf=1.5)), "no", None), ("own", ("own", {}), "no", None),
         ("variants share 1", ("variants", dict(share=1.0)), "no", None), ("variants share .5", ("variants", dict(share=0.5)), "no", None),
         ("variants share 0", ("variants", dict(share=0.0)), "no", None),
         ("motif K=1000", ("types", dict(K=1000)), "motif", (5, 1000.0, 30.0)), ("motif K=100", ("types", dict(K=100)), "motif", (5, 1000.0, 30.0)),
         ("alldiff K=1000", ("types", dict(K=1000)), "no", None),
         ("general m=3", ("general", dict(m=3)), "yes", None), ("general m=30", ("general", dict(m=30)), "yes", None),
         ("general m=100", ("general", dict(m=100, second=0.3)), "yes", None), ("general m=300", ("general", dict(m=300)), "mid", None),
         ("mix q=.9", ("general", dict(m=30, q=0.9)), "yes", None), ("mix q=.7", ("general", dict(m=30, q=0.7)), "yes", None),
         ("mix q=.5", ("general", dict(m=30, q=0.5)), "mid", None), ("mix q=.3", ("general", dict(m=30, q=0.3)), "mid", None),
         ("mix q=.1", ("general", dict(m=30, q=0.1)), "no", None)]
    res = batch({n: dict(spec=s, N=300, M=300, se=0.2, model=m) for n, s, _, m in P}, 40)
    print(f"{'population':20s} {'truth':6s} {'written':>8s} | {'C':>5s} {'novel%':>6s} {'F_novel':>8s} {'R':>6s} proposed verdicts (% of runs)")
    for n, _, truth, _ in P:
        rs = res[n]
        w = sum(written_table(r, 300) for r in rs) / len(rs)
        print(f"{n:20s} {truth:6s} {w:8.0%} | {med(rs, 'C'):5.0f} {med(rs, 'share'):6.2f} {med(rs, 'F'):8.3f} {med(rs, 'R'):6.2f} {tally(rs)}")
    print("written = share of runs the written rule, with the one computable control (0.8 N full-cost cures), says yes.")

    section("2d. The written rule's verdict depends on the pool: own-cure populations, se 0.2, 20 runs")
    for K, z in ((100, 0.0), (300, 0.0), (1000, 0.0), (300, 1.0), (1000, 1.0)):
        res = batch({N: dict(spec=("types", dict(K=K, zipf=z)), N=N, M=1000, se=0.2) for N in (100, 300, 1000, 3000)}, 20)
        print(f"K={K} zipf {z}: " + "  ".join(f"N{N}: yes {sum(written_table(r, N) for r in res[N]) / 20:.0%}, proposed {tally(res[N])}" for N in res))

    section("2e. Is 1 - F_novel the marginal cures per new challenge? Mixes, N to 3N, se 0.2")
    print("(so 'less than half the control' and 'F_novel above a half' are one condition, not two)")
    for q in (0.0, 0.3, 0.5, 0.7, 0.9, 1.0):
        res = batch({N: dict(spec=("general", dict(m=30, q=q)), N=N, M=1000, se=0.2) for N in (100, 300)}, 20)
        slope = (med(res[300], "C") - med(res[100], "C")) / 200
        print(f"q {q}: new cures per new world {slope:.3f}; 1 - F_novel {1 - med(res[300], 'F'):.3f}; R at N = 300 {med(res[300], 'R'):.3f}")

    section("2f. False splits: how good must 'is this challenge new?' be? False yes % among populations with no sharing")
    print("N 225, M 75 and 300, se 0.2, 100 runs. e = chance a duplicate's signature looks new")
    es = (0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9)
    for n, s in (("K=10", dict(K=10)), ("K=30", dict(K=30)), ("K=100", dict(K=100)), ("K=300", dict(K=300)), ("zipf1 K=300", dict(K=300, zipf=1.0))):
        for M in (75, 300):
            res = batch({e: dict(spec=("types", s), N=225, M=M, se=0.2, e=e) for e in es}, 100)
            print(f"{n} M{M}: " + "  ".join(f"e{e}: {sum(verdict(r) == 'YES' for r in res[e])}%" for e in es))
    res = batch({"fine": dict(spec=("variants", dict(share=1.0, fine=True)), N=225, M=300, se=0.2),
                 "fine500": dict(spec=("variants", dict(share=1.0, var=500, fine=True)), N=225, M=300, se=0.2),
                 "skeleton500": dict(spec=("variants", dict(share=1.0, var=500)), N=225, M=300, se=0.2)}, 100)
    for t, rs in res.items():
        print(f"variants sharing a cure, {t} (signature sees each gain as new if 'fine'): {tally(rs)}, novel share {med(rs, 'share'):.2f}")


# ---------------------------------------------------------------- 3. arithmetic

def concavity(curve_c80, C_total):
    """Saving by concavity alone: cures to 80% against 80% of the whole curve's cures."""
    return 1 - curve_c80 / (0.8 * C_total)


def s3():
    section("3. Apparent saving from arithmetic alone: populations with NO sharing, N = 300, se 0 unless stated, 20 runs")
    print("Every saving below is fake: each type needs its own cure.")
    print("\na. Pool arithmetic, the written rule's control: saving = 1 - C(80% fresh) / (0.8 N)")
    conds = {(K, z): dict(spec=("types", dict(K=K, zipf=z)), N=300, M=1000, se=0.0) for K in (3, 10, 30, 100, 300) for z in (0.0, 1.0, 1.5)}
    res = batch(conds, 20)
    for z in (0.0, 1.0, 1.5):
        print(f"zipf {z}: " + "  ".join(f"K{K}: {1 - med(res[(K, z)], 'c80') / 240:.0%}" if share(res[(K, z)], 'c80') > 0.5 else f"K{K}: never" for K in (3, 10, 30, 100, 300)))
    print("\nb. Frequency alone: 1 - C80(zipf) / C80(equal), same K, from the population (no sampling)")
    for z in (1.0, 1.5):
        print(f"zipf {z}: " + "  ".join(f"K{K}: {1 - true_c80(K, z) / true_c80(K, 0.0):.0%}" for K in (10, 30, 100, 300, 1000)))
    print("\nc. Concavity of the designer's own (training) curve vs the fresh curve: 1 - C80 / (0.8 C_total). The training")
    print("   curve is what greedy sorts; a fresh curve of an equal-frequency population should be straight (0%).")
    for K, z in ((30, 0.0), (100, 0.0), (300, 0.0), (1000, 0.0), (300, 1.0)):
        rs = batch({"x": dict(spec=("types", dict(K=K, zipf=z)), N=300, M=1000, se=0.0)}, 20)["x"]
        tr = concavity(med(rs, "c80_t"), med(rs, "C"))
        fr = concavity(med(rs, "c80"), med(rs, "C")) if share(rs, "c80") > 0.5 else float("nan")
        print(f"K={K} zipf {z}: cures {med(rs, 'C'):.0f}; training {tr:.0%}; fresh {'never reaches 80%' if math.isnan(fr) else f'{fr:.0%}'}")
    print("\nd. Noise on the designer's own view, the pure control, truth 240 cures: a cure seems to cover its world plus fp of the rest")
    for se in (0.0, 0.2, 0.3, 0.5, 1.0):
        a = batch({"x": dict(spec=("own", {}), N=300, M=1000, se=se, retest=False)}, 20)["x"]
        b = batch({"x": dict(spec=("own", {}), N=300, M=1000, se=se)}, 20)["x"]
        print(f"se {se} (fp {FP(se):.3f}): one look: C80 {med(a, 'c80_t'):.0f} = {1 - med(a, 'c80_t') / 240:.0%} saving; re-run each addition: C80 {med(b, 'c80_t'):.0f} = {1 - med(b, 'c80_t') / 240:.0%} saving; "
              f"cures {med(a, 'C'):.0f} / {med(b, 'C'):.0f}; fresh corrected {med(a, 'corr_end'):+.3f} / {med(b, 'corr_end'):+.3f}")
    print("\ne. Scoring each cure separately (a world counts if any cure seemed to work), the pure control, 100 cures, measured")
    rng = np.random.default_rng(3)
    for se in (0.1, 0.2, 0.3, 0.5):
        passes = (se * rng.standard_normal((5000, 100)) > THRESHOLD).any(1).mean()
        print(f"se {se}: coverage {passes:.0%} from noise alone (one measurement per cumulative circuit: {FP(se):.1%})")
    print("\nf. Motif arithmetic: own-cure population, every cure a copy of one motif with a tuned parameter: 1 - (M + n p) / (n (M + p))")
    for n in (3, 10, 30, 100):
        print(f"n {n}: M 1000, p 30: {1 - (1000 + n * 30) / (n * 1030):.0%}")
    print("\ng. The proposed statistic on the same populations: F_novel (should be 0), N 225, M 300, se 0.2, 100 runs")
    for n, s in (("K=300", ("types", dict(K=300))), ("K=1000", ("types", dict(K=1000))), ("zipf1 K=1000", ("types", dict(K=1000, zipf=1.0))),
                 ("zipf1.5 K=3000", ("types", dict(K=3000, zipf=1.5))), ("own", ("own", {}))):
        rs = batch({"x": dict(spec=s, N=225, M=300, se=0.2)}, 100)["x"]
        print(f"{n}: F_novel median {med(rs, 'F'):+.3f}, 97.5th percentile across runs {np.percentile([r['F'] for r in rs], 97.5):+.3f}, verdicts {tally(rs)}")


# ---------------------------------------------------------------- 4. description length

KINDS = ("gm", "leak", "cap", "mem", "gate", "clamp")
PORTS = ("s0", "s1", "m0", "m1", "t")
GRID = 1.05          # parameters quantised to a 5% log grid
HUB_DEGREE = 8       # a node touching this many elements is a bus, named by rank, not by distance


def grid_value(rng):
    return float(GRID ** rng.integers(100))


def new_motif(rng, n=25):
    """A connected motif: each element touches the last's node, its other terminal any existing node."""
    els, nodes = [], ["IN", "x0"]
    for i in range(n):
        k = KINDS[rng.integers(len(KINDS))]
        a = nodes[-1]
        b = nodes[rng.integers(len(nodes))]
        if i % 2 == 0:
            nodes.append(f"x{len(nodes)}")
            b = nodes[-1]
        els.append((k, [a, b], [grid_value(rng), grid_value(rng)]))
    els.append(("gm", [nodes[-1], "OUT"], [grid_value(rng), grid_value(rng)]))
    return els


def instantiate(mot, i, rng, tune=None, jitter=0.0):
    """A copy: internals renamed, IN and OUT bound to ports, one parameter tuned, optionally all jittered."""
    wiring = np.random.default_rng(1000 + i)  # a copy's binding depends only on which copy it is
    m = {"IN": ("s0", "s1", "t")[wiring.integers(3)], "OUT": ("m0", "m1")[wiring.integers(2)]}
    els = []
    for j, (k, ts, ps) in enumerate(mot):
        ps = list(ps)
        if jitter:
            ps = [p * (1 + jitter * (2 * rng.random() - 1)) for p in ps]
        if tune is not None and j == 0:
            ps[0] = ps[0] * GRID ** tune
        els.append((k, [m.get(t, f"i{i}_{t}") for t in ts], ps))
    return els


def h(*parts):
    return hashlib.blake2b(repr(parts).encode(), digest_size=8).hexdigest()


def canon(elements):
    """The canonical form: flatten happens before this. Dead parts dropped, parameters on the grid, names gone."""
    # prune: keep what connects to a port
    at = defaultdict(list)
    for i, (_, ts, _) in enumerate(elements):
        for t in ts:
            at[t].append(i)
    keep, stack, seen = set(), [p for p in PORTS if p in at], set()
    while stack:
        n = stack.pop()
        if n in seen:
            continue
        seen.add(n)
        for i in at[n]:
            keep.add(i)
            stack.extend(elements[i][1])
    els = [elements[i] for i in sorted(keep)]
    at = defaultdict(list)
    for i, (_, ts, _) in enumerate(els):
        for pos, t in enumerate(ts):
            at[t].append((i, pos))
    # structural colours (Weisfeiler-Lehman), blind to names and parameters
    col = {n: (n if n in PORTS else "") for n in at}
    ecol = [k for k, _, _ in els]
    for _ in range(4):
        ecol = [h(ecol[i], [col[t] for t in ts]) for i, (_, ts, _) in enumerate(els)]
        col = {n: h(col[n], sorted((ecol[i], p) for i, p in at[n])) for n in at}
    hubs = {p: p for p in PORTS if p in at}
    others = sorted((-len(at[n]), col[n], n) for n in at if n not in PORTS and len(at[n]) >= HUB_DEGREE)
    for r, (_, _, n) in enumerate(others):
        hubs[n] = f"h{r}"
    # islands: what is left connected when the buses are removed. A copy of a motif is an island.
    parent = list(range(len(els)))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for n, uses in at.items():
        if n not in hubs:
            for (a, _), (b, _) in zip(uses, uses[1:]):
                parent[root(a)] = root(b)
    groups = defaultdict(list)
    for i in range(len(els)):
        groups[root(i)].append(i)

    def grid(p):
        return int(round(math.log(max(p, 1e-30)) / math.log(GRID)))

    def nearest(left, number):
        """Depth first: an element on the newest node we have numbered; colour and parameters only break ties."""
        def key(i):
            newest = max((number[t] for t in els[i][1] if t in number), default=-1)
            port = min((PORTS.index(t) for t in els[i][1] if t in PORTS), default=len(PORTS))
            return (-newest, port, els[i][0], ecol[i], [grid(p) for p in els[i][2]])
        return min(left, key=key)

    islands = defaultdict(list)
    for members in groups.values():
        left, number, st, pa = set(members), {}, [], []
        while left:
            i = nearest(left, number)
            left.discard(i)
            k, ts, ps = els[i]
            toks = [k]
            for t in ts:
                if t in hubs:
                    toks.append(hubs[t])
                elif t in number:
                    toks.append(str(len(number) - number[t]))
                else:
                    number[t] = len(number)
                    toks.append("n")
            st.append(" ".join(toks))
            pa.extend(grid(p) for p in ps)
        islands["\n".join(st)].append(pa)
    # each distinct island once; how many; then its parameters column by column, each copy as a change from the last
    structure, params = [], []
    for st in sorted(islands):
        rows = sorted(islands[st])
        structure.append(f"{st}\n*{len(rows)}")
        cols = np.array(rows).T
        for col in cols:
            params.append(f"{col[0]}" + "".join(f",{d}" if d else "." for d in np.diff(col)))
    return "\n".join(structure), "\n".join(params)


LZ = [{"id": lzma.FILTER_LZMA2, "preset": 9 | lzma.PRESET_EXTREME, "dict_size": 1 << 24}]


def lz_bits(s):
    return 8 * len(lzma.compress(s.encode(), format=lzma.FORMAT_RAW, filters=LZ)) if s else 0


REF = None  # a frozen corpus: what the compressor already knows, so that it doesn't charge for learning the vocabulary


def set_ref(elements):
    global REF
    REF = canon(elements)


def dl(elements, given=True):
    """Proposed description length, bits: the compressed canonical form, structure and parameters apart, given the
    frozen corpus."""
    a, b = canon(elements)
    if not given or REF is None:
        return lz_bits(a) + lz_bits(b)
    return lz_bits(REF[0] + "\n" + a) - lz_bits(REF[0]) + lz_bits(REF[1] + "\n" + b) - lz_bits(REF[1])


def raw_bits(written):
    return lz_bits(json.dumps(written))


def rename(elements, rng):
    names = sorted({t for _, ts, _ in elements for t in ts} - set(PORTS))
    new = {n: f"q{i}" for i, n in zip(rng.permutation(len(names)), names)}
    els = [(k, [new.get(t, t) for t in ts], ps) for k, ts, ps in elements]
    return [els[i] for i in rng.permutation(len(els))]


def s4():
    section("4. Description length on invented circuits, some built to game it")
    rng = np.random.default_rng(11)
    N_EL, COPIES = 26, 30
    corpus = np.random.default_rng(99)
    set_ref([e for i in range(20) for e in instantiate(new_motif(corpus), i, corpus)])
    param_bits, kind_bits = math.log2(100), math.log2(len(KINDS))
    Mb = N_EL * (kind_bits + 2 * math.log2(N_EL) + 2 * param_bits)  # a motif's information
    bind = math.log2(3) + 1
    motifs = [new_motif(rng) for _ in range(3)]
    copy_tuned = [instantiate(motifs[i % 3], i, rng, tune=int(rng.integers(100))) for i in range(COPIES)]
    honest = [e for c in copy_tuned for e in c]
    truth_honest = 3 * Mb + COPIES * (math.log2(3) + bind + param_bits)
    all_diff = [e for i in range(COPIES) for e in instantiate(new_motif(rng), i, rng)]
    truth_diff = COPIES * (Mb + bind)
    table = []  # the same information as one rule's table
    node_ids = {}
    for k, ts, ps in all_diff:
        table.append(float(GRID ** KINDS.index(k)))
        table += [float(GRID ** node_ids.setdefault(t, len(node_ids))) for t in ts] + list(ps)
    huge = [("rule", ["s0", "t", "m0"], table)]
    one = motifs[0]
    near = [e for i in range(COPIES) for e in instantiate(one, i, np.random.default_rng(i), jitter=0.4)]
    truth_near = Mb + COPIES * (bind + N_EL * 2 * math.log2(math.log(1.4 / 0.6) / math.log(GRID)))
    within = [e for i in range(COPIES) for e in instantiate(one, i, np.random.default_rng(i), jitter=0.01)]
    truth_within = Mb + COPIES * bind
    plain = [e for i in range(COPIES) for e in instantiate(one, i, rng)]
    tweak = []
    for i in range(COPIES):
        c = instantiate(motifs[i % 3], i, rng, tune=int(rng.integers(100)))
        j = int(rng.integers(len(c)))
        c[j] = (KINDS[rng.integers(len(KINDS))], c[j][1], c[j][2])
        tweak += c
    truth_tweak = truth_honest + COPIES * (math.log2(N_EL) + kind_bits)
    pad_block = new_motif(rng, 100)
    padded = []
    for i in range(COPIES):
        c = instantiate(motifs[i % 3], i, rng, tune=int(rng.integers(100)))
        node = c[0][1][1]
        padded += c + [(k, [node if t in ("IN", "OUT") else f"p{i}_{t}" for t in ts], ps) for k, ts, ps in pad_block]
    dead = honest + [(k, [f"d{t}" for t in ts], ps) for k, ts, ps in new_motif(rng, 200)]

    suite = [  # label, elements, truth bits, motifs + rules as declared, written form for raw compression
        ("one motif, 30 plain copies", plain, truth_within, 1 + 0.3),
        ("three motifs, 30 tuned copies", honest, truth_honest, 3 + 0.3),
        ("30 all different", all_diff, truth_diff, 30 + 0.3),
        ("GAME huge rule (30 cures' table)", huge, truth_diff, 1),
        ("GAME near copies, jitter 40%", near, truth_near, 1 + 0.3),
        ("GAME near copies, jitter 1% (<grid)", within, truth_within, 1 + 0.3),
        ("GAME one kind swapped per copy", tweak, truth_tweak, 3 + 0.3),
        ("GAME connected padding in each copy", padded, truth_honest + 100 * (kind_bits + 2 * math.log2(100) + 2 * param_bits), 3 + 0.3),
        ("GAME dead parts, unconnected", dead, truth_honest, 3 + 0.3),
    ]
    print(f"{'circuit':38s} {'parts':>6s} {'truth':>7s} {'DL':>7s} {'DL/tr':>6s} {'raw':>7s} {'raw/tr':>6s} {'count':>6s} {'bits/count':>10s}")
    rows = []
    for label, els, truth, count in suite:
        d, raw = dl(els), raw_bits(els)
        parts = len(els) if label[:9] != "GAME huge" else len(table)
        rows.append((d / truth, raw / truth, truth / count))
        print(f"{label:38s} {parts:6d} {truth:7.0f} {d:7d} {d / truth:6.2f} {raw:7d} {raw / truth:6.2f} {count:6.1f} {truth / count:10.0f}")
    r = np.array(rows)
    print(f"spread (max / min, over the suite): DL {r[:, 0].max() / r[:, 0].min():.2f}, raw {r[:, 1].max() / r[:, 1].min():.2f}, count {r[:, 2].max() / r[:, 2].min():.1f}")

    print("\nRenaming and reordering, 20 trials:")
    for label, els in (("three motifs, 30 tuned copies", honest), ("30 all different", all_diff)):
        ds = [dl(rename(els, np.random.default_rng(s))) for s in range(20)]
        rs = [raw_bits(rename(els, np.random.default_rng(s))) for s in range(20)]
        print(f"{label}: DL {min(ds)}-{max(ds)} ({(max(ds) - min(ds)) / np.mean(ds):.2%}), raw {min(rs)}-{max(rs)}, unrenamed raw {raw_bits(els)}; count unchanged")

    print("\nWhat a copy costs (DL of n copies of one motif, one tuned parameter each; marginal bits per copy):")
    prev = None
    for n in (1, 3, 10, 30, 100, 300):
        d = dl([e for i in range(n) for e in instantiate(one, i, rng, tune=int(rng.integers(100)))])
        print(f"n {n}: {d} bits" + (f", {(d - prev[1]) / (n - prev[0]):.1f} per added copy" if prev else ""))
        prev = (n, d)
    print("and n all-different cures:")
    prev = None
    for n in (1, 3, 10, 30, 100):
        d = dl([e for i in range(n) for e in instantiate(new_motif(rng), i, rng)])
        print(f"n {n}: {d} bits" + (f", {(d - prev[1]) / (n - prev[0]):.1f} per added cure" if prev else ""))
        prev = (n, d)
    print("\nThe compressor's own arithmetic: all-different cures against one cure's size. Should be 1 if a compressor adds nothing.")
    fresh = [[e for e in instantiate(new_motif(rng), i, rng)] for i in range(30)]
    flat = [e for c in fresh for e in c]
    for label, given in (("no corpus", False), ("given the frozen corpus", True)):
        alone = np.median([dl(c, given) for c in fresh])
        print(f"{label}: one cure alone {alone:.0f} bits; 30 all different {dl(flat, given)} bits, ratio to 30 x alone {dl(flat, given) / (30 * alone):.3f}")
    print("\nPadding against a cure-relative control: S = DL(circuit) / (copies x DL(one copy alone))")
    alone = dl(copy_tuned[0])
    pad_alone = dl(padded[:N_EL + 100])
    ref_cure = np.median([dl(c) for c in fresh])
    print(f"honest {dl(honest) / (COPIES * alone):.3f}; padded {dl(padded) / (COPIES * pad_alone):.3f}; "
          f"against the frozen reference of {ref_cure:.0f} bits: honest {dl(honest) / (COPIES * ref_cure):.3f}, padded {dl(padded) / (COPIES * ref_cure):.3f}; "
          f"huge rule against its own size {dl(huge) / dl(huge):.1f} / 30 = {1 / 30:.3f}, against the reference {dl(huge) / (30 * ref_cure):.3f}")


# ---------------------------------------------------------------- 5. how many worlds, how many lives

def s5():
    section("5. Power: N = 225 pool, M fresh worlds, proposed rule, worlds with graded effects (working Beta(8,2), not Beta(1,9)), 200 runs")
    print("% of runs saying YES / NO. se = per-world standard error of the gap closed = sigma_pair / sqrt(pairs). Truth labelled.")
    pops = [("own (no)", ("own", {})), ("zipf1 K=3000 (no)", ("types", dict(K=3000, zipf=1.0))), ("mix q=.3 (between)", ("general", dict(m=30, q=0.3))),
            ("mix q=.5 (not yes)", ("general", dict(m=30, q=0.5))), ("mix q=.7 (yes)", ("general", dict(m=30, q=0.7))),
            ("mix q=.85 (yes)", ("general", dict(m=30, q=0.85))), ("general m=30 (yes)", ("general", dict(m=30)))]
    Ms, ses = (25, 50, 75, 150, 300), (0.1, 0.2, 0.3, 0.4, 0.5)
    for name, spec in pops:
        res = batch({(M, se): dict(spec=spec, N=225, M=M, se=se, partial=True) for M in Ms for se in ses}, 200)
        print(name)
        for se in ses:
            print(f"   se {se}: " + "  ".join(f"M{M}: {sum(verdict(r) == 'YES' for r in res[(M, se)]) / 2:3.0f}/{sum(verdict(r).startswith('NO') for r in res[(M, se)]) / 2:3.0f}" for M in Ms)
                  + f"   median F_novel {med(res[(150, se)], 'F'):.2f}")

    section("5b. Does the bootstrap over worlds cover the circuit's true F_novel? mix q=.7, crisp effects, se 0.1, N 225, 200 runs")
    rng = np.random.default_rng(5)
    for M in (25, 75, 300):
        hit = 0
        for s in range(200):
            r = run(("general", dict(m=30, q=0.7)), 225, M, 0.1, 900_000 + s, keep=True)
            _, cures = draw(("general", dict(m=30, q=0.7)), rng, 20000)
            rank = {c: i for i, c in enumerate(r["order"])}
            tr = (first_cure(cures, rank) < BIG).mean()
            hit += r["F_lo"] <= tr <= r["F_hi"]
        print(f"M {M}: 95% interval held the truth in {hit / 2:.0f}% of runs")

    section("5c. Cost: worlds x pairs x 2 s / 8 cores, per circuit judged")
    print("Pairs needed for a se: (sigma_pair / se)^2. sigma_pair (gap units, per pair of lives) is unknown until stage 2.")
    print(f"{'sigma':>6s} {'se':>5s} {'pairs':>6s} | 75 worlds | 300 worlds | a curve of 30 circuits on 75 | the same on 150")
    for sg in (0.5, 1.0, 2.0, 4.0):
        for se in (0.2, 0.3):
            n = math.ceil((sg / se) ** 2)
            print(f"{sg:6.1f} {se:5.1f} {n:6d} | {75 * n * 0.25 / 3600:8.2f}h | {300 * n * 0.25 / 3600:9.2f}h | {30 * 75 * n * 0.25 / 3600:27.1f}h | {30 * 150 * n * 0.25 / 3600:6.1f}h")


if __name__ == "__main__":
    t0 = time.time()
    parts = {"1": s1, "2": s2, "3": s3, "4": s4, "5": s5}
    for k in (sys.argv[1:] or parts):
        parts[k]()
        print(f"[section {k} done at {time.time() - t0:.0f} s]", flush=True)

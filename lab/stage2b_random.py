"""stage2b_random.py: stage 2b, parts 3 and 5. About 100 random worlds from the frozen generator (lab/stage2b_gen.py, SHA in
lab/v/stage2b_gen.sha256), development world numbers only; lives of base, bank, told and the frozen reference (lab/v/stage2b_reference.md)
on seeds 65200-65259 x 2; first differences on the wires on 65300-65319 x 2 under base, bank and unwired. Development draws: not stage 3,
and no coverage is computed.

    run       the lives, saved in /home/pilgrim/nca-scratch-backup/stage2b/random_lives.pkl (and the wires' first differences)
    analyse   labels in bits (stage 2a's method, lab/stage2_label.py's functions), gap, x, r, nothing to judge, sigma and pairs for se .1

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage2b_random.py run|analyse"""
import os
import pickle
import sys
import time
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from stage2_lang import arms as S, lang
from stage2_lang.sim import Refused
import stage2b_gen as G

OUT = "/home/pilgrim/nca-scratch-backup/stage2b/"
SEEDS = range(65200, 65260)
FD_SEEDS = range(65300, 65320)
NWORLDS = 100
PLAIN = "(world)"


def worlds():
    return {f"g{n}": G.draw(n) for n in G.development(NWORLDS)}


def one(job):
    """(text, arm, seed, first) -> Lived with its cpu time, rows kept for the bank only; or the refusal."""
    text, arm, seed, first = job
    t0 = time.perf_counter()
    try:
        l = S.live(S.make(S.world_of(text), arm, seed, first))
    except Refused as e:
        return ("refused", str(e))
    l.cpu = time.perf_counter() - t0
    if arm != "bank":
        l.rows = None
    l.picks = None
    return l


def told_arm(text):
    return "vtoldw" if "told_wait" in S.world_of(text).fn else "vtold"


def wire(job):
    import stage2_label as L
    try:
        p, tt, rates = L.wire(job)
    except Refused as e:
        return None
    return p, tt, rates


def run():
    W = worlds()
    t00 = time.time()
    res, fd, plain_w = {}, {}, {}
    with ProcessPoolExecutor(7) as ex:
        for name, (text, desc) in [("plain", (PLAIN, []))] + list(W.items()):
            res[name] = {}
            for label, arm in (("base", "circuit"), ("bank", "bank"), ("told", told_arm(text)), ("ref", "ref")):
                res[name][label] = list(ex.map(one, [(text, arm, s, c) for s in SEEDS for c in S.COL], chunksize=4))
            import stage2_label as L
            fd[name] = {}
            for arm in ("circuit", "bank", "unwired"):
                w_ = list(ex.map(wire, [(text, arm, s, c) for s in FD_SEEDS for c in S.COL], chunksize=4))
                if name == "plain":
                    plain_w[arm] = w_
                fd[name][arm] = ([L.first_diff(a, b) if a is not None else -1 for a, b in zip(w_, plain_w[arm])], [a[2] if a is not None else None for a in w_])
            print(f"{name} {time.time() - t00:.0f} s", flush=True)
            if len(res) % 10 == 0:
                with open(OUT + "random_lives_partial.pkl", "wb") as f:
                    pickle.dump((res, fd), f)
    with open(OUT + "random_lives.pkl", "wb") as f:
        pickle.dump((res, fd), f)
    print(f"done {time.time() - t00:.0f} s", flush=True)


# ---------------------------------------------------------------- analysis
BOOT = 2000


def gs(L):
    from minimal.spec import COST, spent
    return np.array([sum(a - COST * b for a, b, _ in l) for l in L], dtype=float), np.array([spent(l) for l in L], dtype=float)


def boot_eff(L, I):
    g, s = gs(L)
    return g.sum() / s.sum(), g[I].sum(1) / s[I].sum(1)


def judge(R, I):
    """Point values and bootstrap draws (the same draws I for every arm) of base, bank, told, ref, floor, gap, x, r."""
    out = {}
    for k in ("base", "bank", "told", "ref"):
        out[k] = boot_eff(R[k], I)
    fl = (max(out["base"][0], 0), np.maximum(out["base"][1], 0))
    gap = (out["told"][0] - fl[0], out["told"][1] - fl[1])
    with np.errstate(divide="ignore", invalid="ignore"):
        x = ((out["bank"][0] - fl[0]) / gap[0], (out["bank"][1] - fl[1]) / gap[1])
        r = ((out["ref"][0] - fl[0]) / gap[0], (out["ref"][1] - fl[1]) / gap[1])
    out.update(floor=fl, gap=gap, x=x, r=r)
    return out


def ci(v):
    v = v[np.isfinite(v)]
    return np.percentile(v, [2.5, 97.5]) if len(v) else (np.nan, np.nan)


def analyse(path=OUT + "random_lives.pkl"):
    import stage2_label as L
    res, fd = pickle.load(open(path, "rb"))
    W = worlds()
    print(f"generator SHA-256 {open('/home/pilgrim/git/simple-learner/lab/v/stage2b_gen.sha256').read().split()[0][:16]}; reference "
          f"{open('/home/pilgrim/git/simple-learner/lab/v/stage2b_reference.sha256').read().split()[0][:16]}; corpus "
          f"{open('/home/pilgrim/git/simple-learner/lab/stage2_lang/corpus.txt.sha256').read().strip()[:16]}", flush=True)
    refused = {n: [l for R in res[n].values() for l in R if isinstance(l, tuple)] for n in res}
    print("worlds with any life refused by the engine:", {n: v[0] for n, v in refused.items() if v} or "none", flush=True)
    npairs = len(SEEDS)
    rng = np.random.default_rng(0)
    k = rng.integers(0, npairs, (BOOT, npairs))
    I = np.concatenate((2 * k, 2 * k + 1), axis=1)
    # labels, as stage 2a (D33): bank's scored tastes; first differences against plain under three policies
    st = {n: L.stats([l.rows for l in res[n]["bank"]]) for n in res}
    e_plain = st["plain"][:, 1].sum() / st["plain"][:, 3].sum()
    rows = {}
    print(f"\n== {len(W)} random worlds (development numbers {G.development(NWORLDS)[0]}..{G.development(NWORLDS)[-1]}), seeds {SEEDS.start}-{SEEDS.stop - 1} x 2. "
          "Development draws. Efficiency; floor = max(base, 0); gap = told - floor; x = bank's closure, r = the reference's; 95% over seed pairs."
          " judge: '-' nothing to judge (gap's interval reaches 0, or gap < .1); pass: x > max(.5 r, .25)", flush=True)
    hdr = f"{'world':6s} {'DL':>5s} {'cls':>3s} {'e':>6s} {'b/life':>6s} {'D':>6s} {'base':>6s} {'bank':>6s} {'told':>6s} {'ref':>6s} {'gap[95%]':>17s} {'x[95%]':>20s} {'r[95%]':>20s} judge  sig_b sig_k sig_d  n(eff) n(x)  s/life  what"
    print(hdr, flush=True)
    for n, R in res.items():
        J = judge(R, I)
        lab = L.summarise(st[n], e_plain)
        d = {}
        for arm in ("circuit", "bank", "unwired"):
            ds, rates = fd[n][arm]
            d[arm] = ([x * 0.01 for x in ds if x is not None], sum(x is None for x in ds) / max(1, len(ds)), L.rate_kl(rates, fd["plain"][arm][1]))
        none = min(d[a][1] for a in d)
        cls, why = L.classify(n, lab, none, d["circuit"][2], None)
        text = PLAIN if n == "plain" else W[n][0]
        bits = lang.bits(lang.World(text))
        gl, gh = ci(J["gap"][1])
        nothing = not (gl > 0 and J["gap"][0] >= 0.1)
        x, r = J["x"][0], J["r"][0]
        xl, xh = ci(J["x"][1])
        rl, rh = ci(J["r"][1])
        sg_b = float(np.std(J["base"][1]) * np.sqrt(npairs))
        sg_k = float(np.std(J["bank"][1]) * np.sqrt(npairs))
        sg_d = float(np.std(J["bank"][1] - J["base"][1]) * np.sqrt(npairs))
        sx = float(np.std(J["x"][1][np.isfinite(J["x"][1])]) * np.sqrt(npairs)) if not nothing else np.nan
        verdict = "-" if nothing else ("pass" if x > max(0.5 * r, 0.25) else "no")
        cpu = float(np.mean([l.cpu for k_ in ("base", "bank", "told", "ref") for l in R[k_]]))
        what = "; ".join(f"{a} {b} {c}" for a, b, c, _ in (W[n][1] if n != "plain" else [])) or "plain"
        e = lab["e"]
        print(f"{n:6s} {bits:5d} {cls[0]:>3s} {e if e is not None else float('nan'):6.3f} {lab['bl'] if lab['bl'] is not None else float('nan'):6.1f} {lab['D']:6.1f} "
              f"{J['base'][0]:+6.2f} {J['bank'][0]:+6.2f} {J['told'][0]:+6.2f} {J['ref'][0]:+6.2f} {J['gap'][0]:+5.2f}[{gl:+5.2f},{gh:+5.2f}] "
              + (f"{x:+6.2f}[{xl:+5.2f},{xh:+5.2f}] {r:+6.2f}[{rl:+5.2f},{rh:+5.2f}]" if not nothing else f"{'':20s} {'':20s}")
              + f" {verdict:5s} {sg_b:5.2f} {sg_k:5.2f} {sg_d:5.2f} {(sg_k / 0.1) ** 2:6.0f} {(sx / 0.1) ** 2 if not nothing else float('nan'):5.0f}  {cpu:.2f}  {what}", flush=True)
        rows[n] = dict(bits=bits, cls=cls, why=why, lab=lab, fd=d, J={k_: J[k_][0] for k_ in J}, gap_ci=(gl, gh), x_ci=(xl, xh), r_ci=(rl, rh),
                       nothing=nothing, verdict=verdict, sg=(sg_b, sg_k, sg_d), sx=sx, cpu=cpu, desc=(W[n][1] if n != "plain" else []))
    with open(OUT + "random_rows.pkl", "wb") as f:
        pickle.dump(rows, f)
    summary(rows)


def summary(rows):
    R = {n: v for n, v in rows.items() if n != "plain"}
    N = len(R)
    from collections import Counter
    cls = Counter(v["cls"] for v in R.values())
    gap = [n for n, v in R.items() if not v["nothing"]]
    closes = [n for n in gap if R[n]["r_ci"][0] > 0.25]
    passes = [n for n in gap if R[n]["verdict"] == "pass"]

    def wilson(k, n):
        if n == 0:
            return (np.nan, np.nan)
        p, z = k / n, 1.96
        c = (p + z * z / (2 * n)) / (1 + z * z / n)
        h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
        return c - h, c + h
    print(f"\n== summary, {N} random worlds (development draws; not stage 3's coverage)", flush=True)
    print(f"  labels: {dict(cls)}", flush=True)
    print(f"  something to judge (a gap): {len(gap)}/{N} = {len(gap) / N:.2f} [{wilson(len(gap), N)[0]:.2f},{wilson(len(gap), N)[1]:.2f}]", flush=True)
    print(f"  of those, the reference surely closes over .25 of the gap (r's lower bound > .25): {len(closes)}/{len(gap)}; of all {len(closes) / N:.2f} [{wilson(len(closes), N)[0]:.2f},{wilson(len(closes), N)[1]:.2f}]", flush=True)
    print(f"  the bank passes (x > max(.5 r, .25)), for the record: {len(passes)}/{len(gap)}", flush=True)
    print(f"  worlds with a gap: {gap}", flush=True)
    print(f"  the reference closes: {closes}", flush=True)
    by = Counter()
    for n, v in R.items():
        for link, c, course, _ in v["desc"]:
            by[link, "all"] += 1
            by[link, "gap"] += int(not v["nothing"])
    print("  share with a gap, by link of any statement: " + ", ".join(f"{l} {by[l, 'gap']}/{by[l, 'all']}" for l in sorted({k[0] for k in by})), flush=True)
    ks = sorted(set(len(v["desc"]) for v in R.values()))
    print("  by statements in the world: " + ", ".join(f"{k}: {sum(not v['nothing'] for v in R.values() if len(v['desc']) == k)}/{sum(len(v['desc']) == k for v in R.values())}" for k in ks), flush=True)
    sb = np.array([v["sg"][0] for v in R.values()])
    sk = np.array([v["sg"][1] for v in R.values()])
    sd = np.array([v["sg"][2] for v in R.values()])
    sx = np.array([v["sx"] for v in R.values() if np.isfinite(v["sx"])])
    cpu = np.array([v["cpu"] for v in R.values()])
    q = lambda a: f"median {np.median(a):.2f}, 10-90% {np.percentile(a, 10):.2f}-{np.percentile(a, 90):.2f}, max {a.max():.2f}"
    print("\n== part 5: real sigma (a seed pair's, from the bootstrap) and cost", flush=True)
    print(f"  sigma base: {q(sb)}", flush=True)
    print(f"  sigma bank: {q(sk)}", flush=True)
    print(f"  sigma bank - base: {q(sd)}", flush=True)
    print(f"  pairs for se .1 in efficiency (bank): {q((sk / 0.1) ** 2)}", flush=True)
    print(f"  pairs for se .1 in bank - base: {q((sd / 0.1) ** 2)}", flush=True)
    if len(sx):
        print(f"  sigma of x (worlds with a gap): {q(sx)}; pairs for se .1 in x: {q((sx / 0.1) ** 2)}", flush=True)
    print(f"  cpu seconds a life (mean of the four arms): {q(cpu)}", flush=True)


if __name__ == "__main__":
    {"run": run, "analyse": analyse}[sys.argv[1]]()

"""D78: allocation rules under an enforced total cap (lab/alloc_rules.py), scored by the frozen comparison's metric.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/alloc_compare.py stage1
    ... alloc_compare.py stage2 RULE SEED0     (frozen rule against E on fresh seeds, both families)
Stage 1 first runs the neutral check (rule none must reproduce the historical seq-17 lives).
"""
import glob
import hashlib
import json
import os
import pickle
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "lab"), str(ROOT)]
for flag in ("GRADED", "DVOTE", "SURP", "LMIX", "LB_JOINT", "LB_LETTER", "MUSCLE", "EXTRA", "SPLIT", "TOLDT"):
    assert os.environ.get(flag) in (None, "", "0"), flag
os.environ["LB_FINE"] = os.environ["LB_LIVE"] = "1"
import numpy as np

ARM, G = "net10kc60SFBLMR", 258
FAMILIES = {"seq": (17, 300.0, "grownet_pair300_seq_5-11-17_10_s142000_*.pkl", 4480),
            "time": (3, 3000.0, "grownet_pair3000_time_3-5-7_10_s142000_*.pkl", 2240)}
FAM = ("event", "clock", "integrator", "rhythm")


def family(kind):
    return "integrator" if kind.startswith("lb") else "rhythm" if kind.startswith("rt") else "clock" if kind.startswith("clock") else "event"


def world(fam):
    import ladders as L
    rung = FAMILIES[fam][0]
    return L.seq(rung) if fam == "seq" else L.timing(rung)


def one(job):
    import stage3_random as R
    import teach as T
    from stage2_lang import arms as S
    import alloc_rules as A
    fam, rule, P, seed, first = job
    R._init(.0025, False)
    if rule in ("circuit", "vtold"):                    # the references, as the frozen comparison ran them
        res = T.job((world(fam), rule, 0, seed, first, FAMILIES[fam][1]))
        return dict(fam=fam, rule=rule, P=0, seed=seed, first=first, result=list(res[:5]) + [None] + list(res[6:]))
    original, out = S.live, {}

    def live(lf, secs):
        assert lf.t == 0
        st = A.install(lf.brain, rule, G, seed)
        c0 = time.process_time()
        lived = original(lf, secs)
        b = lf.brain
        out.update(cpu_s=time.process_time() - c0, alloc={k: v for k, v in st.items()},
                   final_units=sum(len(n.units) for n in b.nets),
                   grown={f: sum(sum(x["sym"] is None for x in n.units.values()) for n in b.nets if family(n.kind) == f) for f in FAM},
                   heaviest=sorted(((float(getattr(n, "w", 1.0)), n.kind) for n in b.nets), reverse=True)[:3])
        return lived

    S.live = live
    try:
        res = T.job((world(fam), ARM, P, seed, first, FAMILIES[fam][1]))
    finally:
        S.live = original
    return dict(fam=fam, rule=rule, P=P, seed=seed, first=first, result=list(res[:5]) + [None] + list(res[6:]), **out)


def history(fam):
    rung = FAMILIES[fam][0]
    path = glob.glob(str(ROOT / "lab/v" / FAMILIES[fam][2]))
    assert len(path) == 1, path
    rows = pickle.loads(Path(path[0]).read_bytes())
    return {(j[1], j[2], j[3], j[4]): r for j, r in rows if j[0] == rung}, path[0]


def closure_samples(rows_by_life, ref, seeds):
    k = np.random.default_rng(0).integers(0, len(seeds), (2000, len(seeds)))
    idx = np.concatenate((2 * k, 2 * k + 1), axis=1)
    order = [(s, c) for s in seeds for c in ("red", "blue")]

    def eff(get):
        d = np.array([get(s, c)[:5] for s, c in order], dtype=float)
        return d[idx, 2].sum(1) / d[idx, 3].sum(1)
    base, told = eff(lambda s, c: ref["circuit", 0, s, c]), eff(lambda s, c: ref["vtold", 0, s, c])
    return {name: (eff(get) - base) / (told - base) for name, get in rows_by_life.items()}


def ci(x):
    lo, med, hi = np.quantile(x, [.025, .5, .975])
    return dict(median=float(med), ci95=[float(lo), float(hi)])


def provenance():
    return dict(revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                dirty=subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
                sha256={p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in
                        ("lab/alloc_compare.py", "lab/alloc_rules.py", "lab/grownet.py", "lab/teach.py", "lab/ladders.py",
                         "lab/stage2_lang/seconds.py", "lab/stage2_lang/sim.py")}, G=G, arm=ARM, env=dict(LB_FINE="1", LB_LIVE="1"))


def run(jobs, workers=8):
    with ProcessPoolExecutor(workers) as ex:
        return list(ex.map(one, jobs, chunksize=1))


def neutral():
    hist, _ = history("seq")
    jobs = [("seq", "none", P, 142000, c) for P in (560, 4480) for c in ("red", "blue")]
    for r in run(jobs, 4):
        h = hist[ARM, r["P"], r["seed"], r["first"]]
        same = [v for i, v in enumerate(h) if i not in (5, 7)] == [v for i, v in enumerate(r["result"]) if i not in (5, 7)] \
            and abs(h[7] - r["result"][7]) < 1e-12
        print("neutral", r["P"], r["first"], "reproduces record" if same else "DIFFERS", flush=True)
        assert same, "the hooks change behaviour"


def stage(name, plan, seeds, out):
    t0 = time.monotonic()
    report = dict(stage=name, seeds=[min(seeds), max(seeds)], plan=plan, provenance=provenance(), families={})
    for fam, rules in plan.items():
        jobs = [(fam, rule, 560, s, c) for rule in rules for s in seeds for c in ("red", "blue")]
        res = run(jobs)
        by = {(r["rule"], r["seed"], r["first"]): r for r in res}
        hist, hpath = history(fam) if name == "stage1" else (None, None)
        if name == "stage1":
            getters = {rule: (lambda s, c, rule=rule: by[rule, s, c]["result"]) for rule in rules}
            ref_P = FAMILIES[fam][3]
            getters["hist_P560"] = lambda s, c: hist[ARM, 560, s, c]
            getters[f"hist_P{ref_P}"] = lambda s, c, P=ref_P: hist[ARM, P, s, c]
            ref = hist
        else:
            getters = {rule: (lambda s, c, rule=rule: by[rule, s, c]["result"]) for rule in rules if rule not in ("circuit", "vtold")}
            ref = {(rule, 0, s, c): by[rule, s, c]["result"] for rule in ("circuit", "vtold") for s in seeds for c in ("red", "blue")}
        X = closure_samples(getters, ref, list(seeds))
        summ = {k: ci(v) for k, v in X.items()}
        for rule in X:
            if rule != "E":
                summ[f"{rule}-E"] = ci(X[rule] - X["E"])
        if name == "stage1":
            for rule in rules:
                summ[f"{rule}-hist_P{FAMILIES[fam][3]}"] = ci(X[rule] - X[f"hist_P{FAMILIES[fam][3]}"])
        print(f"\n== {name} {fam} rung {FAMILIES[fam][0]}, {FAMILIES[fam][1]:.0f} s, seeds {min(seeds)}-{max(seeds)}", flush=True)
        for k, v in summ.items():
            extra = ""
            if k in rules and k not in ("circuit", "vtold"):
                rr = [by[k, s, c] for s in seeds for c in ("red", "blue")]
                extra = (f"  units {np.mean([r['final_units'] for r in rr]):6.0f} peak {np.mean([r['alloc']['peak'] for r in rr]):6.0f}  grown " +
                         " ".join(f"{f} {np.mean([r['grown'][f] for r in rr]):.0f}" for f in FAM) +
                         f"  transfers {np.mean([r['alloc']['transfers'] for r in rr]):.0f} contests {np.mean([r['alloc']['contests'] for r in rr]):.0f}"
                         f" won {np.mean([r['alloc']['won'] for r in rr]):.0f} evictions {np.mean([r['alloc']['evictions'] for r in rr]):.0f}"
                         f"  cpu {np.mean([r['cpu_s'] for r in rr]):.0f} s")
            print(f"  {k:22s} {v['median']:+.2f} [{v['ci95'][0]:+.2f},{v['ci95'][1]:+.2f}]{extra}", flush=True)
        report["families"][fam] = dict(history=hpath, summary=summ, lives=res)
        Path(out).write_text(json.dumps(report, indent=1, default=str) + "\n")
    report["wall_seconds"] = time.monotonic() - t0
    Path(out).write_text(json.dumps(report, indent=1, default=str) + "\n")
    print("wall_seconds", report["wall_seconds"], flush=True)


def main():
    a = sys.argv[1:]
    if a[0] == "stage1":
        neutral()
        stage("stage1", {"seq": ["E", "M", "W", "U", "R"], "time": ["E", "M", "W", "U"]}, range(142000, 142010),
              ROOT / "lab/v/alloc_stage1.json")
    elif a[0] == "stage2":
        rule, s0 = a[1], int(a[2])
        stage("stage2", {f: ["circuit", "vtold", "E", rule] for f in FAMILIES}, range(s0, s0 + 10), ROOT / f"lab/v/alloc_stage2_{rule}.json")


if __name__ == "__main__":
    main()

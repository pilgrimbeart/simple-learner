"""D180 driver (work order section 10). From the repository root, maths threads 1:

  run.py check | bench | action | learn | confirm [--dry-run] | refine [--dry-run] | report

Each stage refuses to overwrite its outputs and refuses to start without the saved gate pass of the stage before.
A failed scientific gate writes a saved not-triggered record for downstream stages (exit 0), never a false completion.
Outputs: lab/v/catalogue_brain_20261120/ (compact ledgers *.jsonl.gz, gates, summaries); full traces in
lab/v/catalogue_brain_20261120_<stage>.pkl (git-ignored; absolute path and hash recorded).
"""
from __future__ import annotations

import gzip
import hashlib
import json
import math
import multiprocessing
import os
import pickle
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
OUT = ROOT / "lab/v/catalogue_brain_20261120"
WORKERS = 7
DEV = range(8, 40)
COLOURS = ("red", "blue")

for v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    assert os.environ.get(v) == "1", f"set {v}=1 (one maths thread per worker)"


def hashes():
    files = sorted(HERE.glob("*.py")) + [ROOT / p for p in ("mixed_feedback.py", "units.py", "chip.py", "creature.py",
                                                             "world.py", "brains/circuit.py")]
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def sim_hashes():
    """The files that determine a simulated life (reuse across stages requires these unchanged)."""
    return {k: v for k, v in hashes().items() if Path(k).name in ("brain.py", "lives.py", "design.py", "mixed_feedback.py",
                                                                   "units.py", "chip.py", "creature.py", "world.py",
                                                                   "circuit.py")}


def gate(name):
    p = OUT / f"gate_{name}.json"
    return json.loads(p.read_text()) if p.exists() else None


def save_gate(name, d):
    p = OUT / f"gate_{name}.json"
    if p.exists():
        raise SystemExit(f"{p} exists: refusing to overwrite")
    d = dict(d, code=hashes(), sim_code=sim_hashes(), time=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    p.write_text(json.dumps(d, indent=1, default=float) + "\n")
    print(json.dumps({k: v for k, v in d.items() if k != "code"}, indent=1, default=float))


def require(name, key):
    g = gate(name)
    if g is None:
        raise SystemExit(f"stage needs gate_{name}.json: run that stage first")
    return g.get(key, False), g


def version():
    g = gate("revision")
    return g["selected_version"] if g else 1


# --------------------------------------------------------------------------------------------- jobs
def J(stage, arm, seed, poison, P, learning, removed="none", ratio=1, noise="native", v=1):
    return dict(stage=stage, version=v, arm=arm, seed=seed, poison=poison, P=P, learning=learning, removed=removed,
                ratio=ratio, noise=noise)


def action_jobs(v):
    jobs = []
    for s in DEV:
        for c in COLOURS:
            jobs += [J("action", "informed", s, c, "informed", False, v=v), J("action", "neutral", s, c, "neutral", False, v=v),
                     J("action", "reversed", s, c, "reversed", False, v=v),
                     J("action", "no_explore", s, c, "informed", False, "no_explore", v=v),
                     J("action", "no_sensory", s, c, "informed", False, "no_sensory", v=v)]
        jobs += [J("action", "informed_allfood", s, None, "informed", False, v=v),
                 J("action", "neutral_allfood", s, None, "neutral", False, v=v)]
    return jobs


def learn_jobs(v):
    jobs = []
    for s in DEV:
        for c in COLOURS:
            jobs += [J("learn", "learned", s, c, None, True, v=v),
                     J("learn", "writers_removed", s, c, None, True, "no_writers", v=v)]
        jobs += [J("learn", "learned_allfood", s, None, None, True, v=v),
                 J("learn", "writers_removed_allfood", s, None, None, True, "no_writers", v=v)]
    return jobs


def confirm_jobs(seeds, ratio, v):
    jobs = []
    for s in seeds:
        for c in COLOURS:
            jobs += [J("confirm", "learned", s, c, None, True, ratio=ratio, noise="coupled", v=v),
                     J("confirm", "writers_removed", s, c, None, True, "no_writers", ratio=ratio, noise="coupled", v=v),
                     J("confirm", "informed", s, c, "informed", False, ratio=ratio, noise="coupled", v=v)]
        jobs += [J("confirm", "learned_allfood", s, None, None, True, ratio=ratio, noise="coupled", v=v),
                 J("confirm", "writers_removed_allfood", s, None, None, True, "no_writers", ratio=ratio, noise="coupled", v=v)]
    return jobs


def execute(name, jobs):
    """Run jobs in a 7-worker pool; compact rows to <name>_ledger.jsonl.gz, full rows (traces) to the pkl archive."""
    import lives
    ledger = OUT / f"{name}_ledger.jsonl.gz"
    archive = ROOT / f"lab/v/catalogue_brain_20261120_{name}.pkl"
    for p in (ledger, archive):
        if p.exists():
            raise SystemExit(f"{p} exists: refusing to overwrite")
    chk = subprocess.run(["git", "check-ignore", "-q", str(archive.relative_to(ROOT))], cwd=ROOT)
    assert chk.returncode == 0, "trace archive would not be git-ignored"
    (OUT / f"{name}_jobs.json").write_text(json.dumps(dict(jobs=jobs, n=len(jobs), keys=[lives.key(j) for j in jobs]),
                                                      indent=0) + "\n")
    t0 = time.time()
    rows = []
    with ProcessPoolExecutor(max_workers=WORKERS, mp_context=multiprocessing.get_context("spawn")) as pool, \
            gzip.open(ledger, "wt") as L, open(archive, "wb") as A:
        print(f"{name}: {len(jobs)} lives, pool pid(s):", flush=True)
        for i, r in enumerate(pool.map(lives.one, jobs, chunksize=1)):
            if i == 0:
                print("  workers", [p.pid for p in pool._processes.values()], flush=True)
            pickle.dump(r, A)
            c = lives.compact(r)
            L.write(json.dumps(c, default=float) + "\n")
            rows.append(c)
            if (i + 1) % 50 == 0 or i + 1 == len(jobs):
                el = time.time() - t0
                print(f"  {i + 1}/{len(jobs)}  {el:.0f} s  eta {el / (i + 1) * (len(jobs) - i - 1):.0f} s", flush=True)
    meta = dict(ledger=str(ledger), archive=str(archive), archive_sha256=sha(archive), ledger_sha256=sha(ledger),
                lives=len(rows), seconds=time.time() - t0)
    (OUT / f"{name}_meta.json").write_text(json.dumps(meta, indent=1) + "\n")
    return rows


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def load(name):
    p = OUT / f"{name}_ledger.jsonl.gz"
    if not p.exists():
        return None
    with gzip.open(p, "rt") as f:
        return [json.loads(x) for x in f]


def arm(rows, a):
    return [r for r in rows if r["arm"] == a]


# --------------------------------------------------------------------------------------------- stages
def stage_check():
    import checks
    import preflight
    res = checks.main()
    pre = preflight.main()
    import schematic_v1
    schematic_v1.main()
    save_gate("check", dict(valid=res["valid"], preflight=pre))


def stage_bench():
    ok, _ = require("check", "valid")
    if not ok:
        save_gate("bench_record", dict(triggered=False, reason="R1 invalid"))
        return
    import bench
    g = bench.main(OUT)
    save_gate("bench", dict(g, version=1))


def stage_action(authorised=False):
    """authorised: the user's decision of 2026-11-20 (after D181) to run R5 on v1 although bench B failed, since R5
    withholds taste and so never uses the writers. Requires bench A and C gates; outputs under the name action_auth,
    leaving the earlier not-triggered gate_action.json untouched."""
    v = version()
    gb = gate("bench") if v == 1 else gate("bench_v%d" % v)
    if gb is None:
        raise SystemExit("run bench first")
    name = "action_auth" if authorised else "action"
    if authorised:
        if not (gb["A"] and gb["C_side"] and gb["C_plastic"] and gb["C_no_clip"]):
            raise SystemExit("authorised R5 still needs bench A and C gates")
    elif not gb.get("R3R4_pass"):
        save_gate("action", dict(triggered=False, reason="R3/R4 progression gate failed", bench=gb))
        return
    import analyse as A
    rows = [dict(r, stage="action") for r in execute(name, action_jobs(v))]
    S = {a: A.summary(arm(rows, a)) for a in sorted({r["arm"] for r in rows})}
    inf = arm(rows, "informed")
    C = dict(informed_minus_neutral=A.paired(inf, arm(rows, "neutral")),
             informed_minus_reversed=A.paired(inf, arm(rows, "reversed")),
             informed_minus_no_explore=A.paired(inf, arm(rows, "no_explore")),
             informed_minus_no_sensory=A.paired(inf, arm(rows, "no_sensory")),
             allfood_informed_minus_neutral=A.paired(arm(rows, "informed_allfood"), arm(rows, "neutral_allfood"),
                                                     "food_rate_final"))
    g = dict(triggered=True, version=v,
             neutral_ok=C["informed_minus_neutral"][1] > 0.10, reversed_ok=C["informed_minus_reversed"][1] > 0.10,
             food_rate_ok=S["informed"]["food_rate_final"][1] >= 1.0,
             no_meal_ok=S["informed"]["no_meal_fraction"] <= 0.20)
    g["pass"] = bool(g["neutral_ok"] and g["reversed_ok"] and g["food_rate_ok"] and g["no_meal_ok"])
    (OUT / f"{name}_summary.json").write_text(json.dumps(dict(summaries=S, contrasts=C), indent=1, default=float) + "\n")
    save_gate(name, dict(g, contrasts=C, informed=S["informed"], authorised_by_user=authorised))


def stage_learn():
    ok, ga = require("action", "pass")
    if not ok:
        save_gate("learn", dict(triggered=False, reason="R5 informed-action gate failed or not triggered"))
        return
    import analyse as A
    v = ga["version"]
    rows = execute("learn", learn_jobs(v))
    act = load("action")
    reuse_ok = gate("action")["sim_code"] == sim_hashes()
    assert reuse_ok, "R5 outputs reused only if the simulation code is unchanged"
    ev = A.evidence(arm(rows, "learned"), arm(act, "neutral"))       # before any reward contrast
    (OUT / "learn_evidence.json").write_text(json.dumps(ev, indent=1, default=float) + "\n")
    print("EVIDENCE (before reward contrasts):", json.dumps(ev, indent=1, default=float)[:3000])
    L, W = arm(rows, "learned"), arm(rows, "writers_removed")
    S = {a: A.summary(arm(rows, a)) for a in sorted({r["arm"] for r in rows})}
    S["taste_withheld(R5 neutral)"] = A.summary(arm(act, "neutral"))
    S["informed(R5)"] = A.summary(arm(act, "informed"))
    S["informed_allfood(R5)"] = A.summary(arm(act, "informed_allfood"))
    C = dict(learned_minus_writers_removed=A.paired(L, W),
             allfood_learned_minus_writers_removed=A.paired(arm(rows, "learned_allfood"), arm(rows, "writers_removed_allfood"),
                                                            "food_rate_final"),
             stranding_learned_minus_writers_removed=A.paired(L, W, "stranded"),
             informed_minus_learned=A.paired(arm(act, "informed"), L),
             learned_minus_taste_withheld=A.paired(L, arm(act, "neutral")))
    jobL = A.job(S["learned"])
    g = dict(triggered=True, version=v, reuse_hashes_match=reuse_ok,
             primary_ok=C["learned_minus_writers_removed"][1] > 0.10,
             allfood_ok=C["allfood_learned_minus_writers_removed"][1] > -0.05,
             stranding_ok=C["stranding_learned_minus_writers_removed"][2] < 0.05, job=jobL)
    g["pass"] = bool(g["primary_ok"] and g["allfood_ok"] and g["stranding_ok"] and jobL["all"])
    sds = A.per_seed(L, "net")
    sdw = A.per_seed(W, "net")
    import numpy as np
    diffs = [sds[k] - sdw[k] for k in sds]
    g["dev_primary_sd"] = float(np.std(diffs, ddof=1))
    (OUT / "learn_summary.json").write_text(json.dumps(dict(summaries=S, contrasts=C), indent=1, default=float) + "\n")
    save_gate("learn", dict(g, contrasts=C))


def confirm_freeze(dry):
    ok, gl = require("learn", "pass")
    if not ok:
        return None, "R6 learning gate failed or not triggered"
    s = gl["dev_primary_sd"]
    N = max(128, 32 * math.ceil((1.96 * s / 0.05) ** 2 / 32))
    if N > 256:
        return None, f"N={N} > 256: deferred as incomplete precision/budget requirement"
    import seed_audit
    start, search = seed_audit.first_unused(N)
    seeds = list(range(start, start + N))
    return dict(N=N, sd=s, seeds=[seeds[0], seeds[-1]], search=search,
                jobs={r: len(confirm_jobs(seeds, r, gl["version"])) for r in (1, 2, 4)}), None


def stage_confirm(dry):
    plan, why = confirm_freeze(dry)
    if plan is None:
        if not dry:
            save_gate("confirm", dict(triggered=False, reason=why))
        print("not triggered:", why)
        return
    print(json.dumps(plan, indent=1))
    if dry:
        return
    p = OUT / "confirm_freeze.json"
    if p.exists():
        raise SystemExit(f"{p} exists: refusing to overwrite")
    seeds = list(range(plan["seeds"][0], plan["seeds"][1] + 1))
    v = gate("learn")["version"]
    plan["ledger"] = {str(r): confirm_jobs(seeds, r, v) for r in (1, 2, 4)}
    p.write_text(json.dumps(plan, indent=0) + "\n")
    execute("confirm_r1", plan["ledger"]["1"])
    save_gate("confirm", dict(triggered=True, N=plan["N"], done=True))


def stage_refine(dry):
    g = gate("confirm")
    if g is None or not g.get("triggered"):
        if not dry and g is not None:
            save_gate("refine", dict(triggered=False, reason="confirmation not triggered"))
        print("not triggered")
        return
    plan = json.loads((OUT / "confirm_freeze.json").read_text())
    if dry:
        print({r: len(plan["ledger"][r]) for r in ("2", "4")})
        return
    for r in ("2", "4"):
        execute(f"confirm_r{r}", plan["ledger"][r])
    save_gate("refine", dict(triggered=True, done=True))


def stage_report():
    import report
    report.main()


if __name__ == "__main__":
    st = sys.argv[1]
    dry = "--dry-run" in sys.argv
    if dry and st not in ("confirm", "refine"):
        import lives
        v = version()
        jobs = dict(action=action_jobs(v), learn=learn_jobs(v)).get(st, [])
        print(f"{st}: {len(jobs)} lives (dry run: nothing simulated)")
        sys.exit(0)
    dict(check=stage_check, bench=stage_bench, action=lambda: stage_action("--authorised" in sys.argv), learn=stage_learn,
         confirm=lambda: stage_confirm(dry), refine=lambda: stage_refine(dry), report=stage_report)[st]()

"""Action grid driver (work order 2026-11-20, section 4). From the repository root, maths threads 1:

  run.py check | bench | develop | analyse | confirm | report | all   [--dry-run] [--resume]

check: R0 manifest freeze, R1 identity checks/fixtures, realised physical table, preflight timing and budget estimate.
bench/develop/confirm: job ledgers (frozen key lists, refused overwrite; --resume runs only missing keys after verifying
the completed rows' simulation-code hash). Rows stream to <name>.part.jsonl, compressed to <name>_ledger.jsonl.gz on
completion; event/pulse records (and traces where required) to the git-ignored lab/v/action_grid_20261120_<name>.pkl.
analyse: R4/R5 tables and the mechanical selection (saved with its hash before any fresh result).
report: R6/R7 confirmation tables. Nothing here prompts or branches on a scientific result.
"""
from __future__ import annotations

import gzip
import hashlib
import json
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
OUT = ROOT / "lab/v/action_grid_20261120"
WORKERS = int(os.environ.get("AG_WORKERS", "7"))   # 4 after the 2026-11-21 OOM kill (routine, logged)
DEV_SEEDS = range(8, 40)
N_CONFIRM = 128
RATIOS = (1, 2, 4)
START = "2026-11-20T18:28:04Z"
DEADLINE = "2026-11-21T06:28:04Z"

for v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    assert os.environ.get(v) == "1", f"set {v}=1 (one maths thread per worker)"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


SIM_FILES = ["lab/action_grid_20261120/ag_engine.py", "lab/action_grid_20261120/ag_jobs.py",
             "lab/action_grid_20261120/variants.py", "lab/action_grid_20261120/PLAN.json",
             "lab/catalogue_brain_20261120/brain.py", "lab/catalogue_brain_20261120/design.py",
             "lab/catalogue_brain_20261120/analyse.py", "mixed_feedback.py", "units.py", "chip.py", "creature.py",
             "world.py", "brains/circuit.py", "minimal/spec.py"]


def sim_hash():
    h = hashlib.sha256()
    for f in SIM_FILES:
        h.update(f.encode() + sha(ROOT / f).encode())
    return h.hexdigest()[:16]


def log(msg):
    line = f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}] {msg}"
    print(line, flush=True)
    with open(OUT / "run.log", "a") as f:
        f.write(line + "\n")


def configs():
    import ag_engine as AE
    return AE.CONFIGS, AE.BASELINE


# --------------------------------------------------------------------------------------------- execution
def read_part(p):
    rows = []
    if p.exists():
        with open(p) as f:
            for line in f:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    log(f"{p.name}: dropped a truncated final line (crash during write)")
    return rows


def execute(name, tasks, fn, expected, resume, dry):
    """tasks: list of picklable task args; fn(task) -> list of (row, arch) or (row, arch). expected: frozen keys."""
    import ag_analysis as AA
    part, ledger = OUT / f"{name}.part.jsonl", OUT / f"{name}_ledger.jsonl.gz"
    archive = ROOT / f"lab/v/action_grid_20261120_{name}.pkl"
    jobs_file = OUT / f"{name}_jobs.json"
    if dry:
        print(f"{name}: {len(expected)} jobs in {len(tasks)} tasks (dry run: nothing simulated)")
        return None
    if ledger.exists():
        rows = load(name)
        miss = AA.validate(rows, expected)
        log(f"{name}: complete ledger exists ({len(rows)} rows, {len(miss)} missing); not rerun")
        return rows
    chk = subprocess.run(["git", "check-ignore", "-q", str(archive.relative_to(ROOT))], cwd=ROOT)
    assert chk.returncode == 0, "archive would not be git-ignored"
    if jobs_file.exists():
        frozen = json.loads(jobs_file.read_text())
        if frozen["keys"] != expected:
            raise SystemExit(f"{jobs_file}: frozen job keys differ from this invocation: incompatible resume")
    if part.exists() and not resume:
        raise SystemExit(f"{part} exists: refusing to overwrite (use --resume)")
    done = read_part(part)
    sh = sim_hash()
    bad = [r["key"] for r in done if r.get("sim") != sh]
    if bad:
        raise SystemExit(f"{len(bad)} completed rows have a different simulation-code hash: incompatible resume")
    AA.validate(done, expected)
    if not jobs_file.exists():
        jobs_file.write_text(json.dumps(dict(n=len(expected), keys=expected, sim=sh)) + "\n")
    have = {r["key"] for r in done if r.get("status") != "error"}
    if len(have) < len(done):                                   # failed attempts are rerun on resume; keep their log
        with open(OUT / f"{name}_failed_attempts.jsonl", "a") as f:
            for r in done:
                if r.get("status") == "error":
                    f.write(json.dumps(r, default=float) + "\n")
        done = [r for r in done if r.get("status") != "error"]
        with open(part, "w") as f:
            for r in done:
                f.write(json.dumps(r, default=float) + "\n")
    todo = [t for t in tasks if not set(task_keys(name, t)) <= have]
    log(f"{name}: {len(expected)} jobs, {len(have)} done, {len(todo)} tasks to run (sim {sh})")
    t0 = time.time()
    n_done = len(done)
    with ProcessPoolExecutor(max_workers=WORKERS, mp_context=multiprocessing.get_context("spawn")) as pool, \
            open(part, "a") as P, open(archive, "ab") as A:
        for i, res in enumerate(pool.map(fn, todo, chunksize=1)):
            if i == 0:
                log(f"  {name} parent pid {os.getpid()} workers {[p.pid for p in pool._processes.values()]}")
            pairs = res if isinstance(res, list) else [res]
            for row, arch in pairs:
                if row["key"] in have:
                    continue
                row["sim"] = sh
                if arch is not None:
                    pickle.dump(arch, A, protocol=5)
                P.write(json.dumps(row, default=float) + "\n")
                n_done += 1
            P.flush()
            A.flush()
            if (i + 1) % max(1, len(todo) // 40) == 0 or i + 1 == len(todo):
                el = time.time() - t0
                log(f"  {name}: {n_done}/{len(expected)}  {el:.0f} s  eta {el / (i + 1) * (len(todo) - i - 1):.0f} s")
    rows = read_part(part)
    miss = AA.validate(rows, expected)
    errs = [r for r in rows if r.get("status") == "error"]
    if miss or errs:
        log(f"{name}: INCOMPLETE: {len(miss)} missing, {len(errs)} errors; rerun with --resume")
        return rows
    with gzip.open(ledger, "wt") as L:
        for r in rows:
            L.write(json.dumps(r, default=float) + "\n")
    part.unlink()
    meta = dict(ledger=str(ledger), ledger_sha256=sha(ledger), archive=str(archive), archive_sha256=sha(archive),
                rows=len(rows), seconds=time.time() - t0, sim=sh)
    (OUT / f"{name}_meta.json").write_text(json.dumps(meta, indent=1) + "\n")
    log(f"{name}: complete, {len(rows)} rows; ledger {meta['ledger_sha256'][:12]} archive {meta['archive_sha256'][:12]}")
    return rows


def task_keys(name, t):
    import ag_jobs as J
    if name == "bench":
        return [J.key(j) for j in J.bench_jobs(t[0]) if j["seed"] == t[1]]
    return [J.key(t[0])]


def load(name):
    p = OUT / f"{name}_ledger.jsonl.gz"
    if not p.exists():
        return read_part(OUT / f"{name}.part.jsonl") or None
    with gzip.open(p, "rt") as f:
        return [json.loads(x) for x in f]


# --------------------------------------------------------------------------------------------- job lists
def bench_plan():
    import ag_jobs as J
    C, base = configs()
    order = [base] + sorted(c for c in C if c != base)
    tasks = [(c, s) for c in order for s in range(8)]
    keys = [J.key(j) for c in order for s in range(8) for j in J.bench_jobs(c) if j["seed"] == s]
    return tasks, keys


def dev_plan():
    import ag_jobs as J
    C, base = configs()
    order = [base] + sorted(c for c in C if c != base)
    jobs = [j for c in order for j in J.life_jobs("develop", c, DEV_SEEDS)]
    return [(j, j["config"] == base) for j in jobs], [J.key(j) for j in jobs]


def confirm_plan():
    import ag_jobs as J
    fz = json.loads((OUT / "confirm_freeze.json").read_text())
    seeds = range(fz["seeds"][0], fz["seeds"][1] + 1)
    jobs = [j for r in RATIOS for c in fz["configs"] for j in J.life_jobs("confirm", c, seeds, ratio=r, noise="coupled")]
    return [(j, True) for j in jobs], [J.key(j) for j in jobs]


# --------------------------------------------------------------------------------------------- stages
def stage_check(dry, resume):
    if dry:
        print("check: manifest freeze, R1 checks (~1 min), realised table 81 x 40 seeds, preflight (~2 min)")
        return
    import ag_checks
    import ag_jobs as J
    C, base = configs()
    if not (OUT / "manifest.json").exists():
        freeze_manifest()
    if not (OUT / "checks.json").exists():
        res = ag_checks.main(OUT / "checks.json")
        if not res["valid"]:
            log("R1 checks FAILED: dependent results invalid until fixed")
    if not (OUT / "realised.json").exists():
        realised_table(range(0, 40), OUT / "realised.json")
    if not (OUT / "preflight.json").exists():
        preflight()


def freeze_manifest():
    import ag_jobs as J
    import ag_analysis as AA
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout
    srcs = SIM_FILES + ["lab/action_grid_20261120/run.py", "lab/action_grid_20261120/ag_analysis.py",
                        "lab/action_grid_20261120/ag_checks.py", "lab/action_grid_20261120/ag_seeds.py",
                        "lab/WORK_ORDER_2026-11-20_action_grid.md", "lab/action_grid_20261120/PROTOCOL.md",
                        "lab/action_grid_20261120/PREDICTIONS.md", "requirements.txt"]
    dep = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True).stdout
    b_tasks, b_keys = bench_plan()
    d_tasks, d_keys = dev_plan()
    m = dict(head=head, dirty_status=dirty.splitlines(), source_sha256={f: sha(ROOT / f) for f in srcs},
             sim_hash=sim_hash(), pip_freeze_sha256=hashlib.sha256(dep.encode()).hexdigest(), python=sys.version,
             start=START, deadline=DEADLINE, workers=WORKERS, threads="OPENBLAS/OMP/MKL=1",
             units=dict(DT=J.DT, TICK=J.TICK, PULSE=J.PULSE, V_TYP=J.V_TYP), life_s=J.LIFE_S, bench_s=J.BENCH_S,
             bench_windows=J.BENCH_WINDOWS, dev_seeds=[8, 39], bench_seeds=[0, 7], confirm=dict(
                 N=N_CONFIRM, ratios=RATIOS, noise="coupled", seed_rule="first unused 128-seed prefix of 2027112000+1000k"),
             metrics="D180 analyse.life_metrics; final third [200/3,100) s; seed resampling; B=10000, RNG 182",
             ranking="descending informed final-third net, descending informed food rate, ascending ID; baseline "
                     "excluded; complete finite rows only",
             expected=dict(bench=len(b_keys), develop=len(d_keys), confirm=4 * N_CONFIRM * 12 * 3),
             job_key_hash=dict(bench=hashlib.sha256("\n".join(b_keys).encode()).hexdigest(),
                               develop=hashlib.sha256("\n".join(d_keys).encode()).hexdigest()))
    assert m["expected"] == dict(bench=31104, develop=31104, confirm=18432)
    (OUT / "manifest.json").write_text(json.dumps(m, indent=1, default=list) + "\n")
    log(f"manifest frozen: HEAD {head[:12]}, sim {m['sim_hash']}")


def realised_one(args):
    import ag_jobs as J
    from ag_engine import GridEngine
    c, seeds = args
    out = []
    for s in seeds:
        for rm in ("none", "no_explore", "no_sensory"):
            e = GridEngine(s, config=c, removed=rm, ticks=1)
            w = e.realised()
            out.append(dict(config=c, seed=s, removed=rm, sides=list(e.sides), **w))
    return out


def realised_table(seeds, path):
    C, _ = configs()
    seeds = list(seeds)
    with ProcessPoolExecutor(max_workers=WORKERS, mp_context=multiprocessing.get_context("spawn")) as pool:
        rows = [r for res in pool.map(realised_one, [(c, seeds) for c in sorted(C)]) for r in res]
    fails = [r for r in rows if r["failed"]]
    by = {}
    for r in rows:
        b = by.setdefault(r["config"], dict(n=0, failed=0, worst={}))
        b["n"] += 1
        b["failed"] += bool(r["failed"])
        for k in ("C_max", "R_max", "slew_max", "self_loop_max", "tau_max", "pulse_slew"):
            b["worst"][k] = max(b["worst"].get(k, 0), r[k])
        for k in ("I_min", "tau_min"):
            b["worst"][k] = min(b["worst"].get(k, 1e9), r[k])
    path.write_text(json.dumps(dict(rows=rows, by_config=by, n=len(rows), failed=len(fails),
                                    failed_rows=fails[:200]), indent=0) + "\n")
    log(f"realised physical table {path.name}: {len(rows)} engines, {len(fails)} with a failed limit")


def preflight():
    """Timing/check runs (separate keys, never selection data). Reward is not read."""
    import ag_jobs as J
    from ag_engine import BASELINE
    res = {}
    j = J.life_jobs("preflight", BASELINE, [8])[0]
    J.life_one(dict(j))                                           # compile
    for r in RATIOS:
        jj = dict(j, ratio=r, noise="coupled")
        import creature
        from ag_engine import GridBrain
        L = creature.Life(8, "red", False, brain=lambda s: GridBrain(s, ratio=r, noise="coupled", trace=True))
        L.brain.set_P(J.birth_P("informed", L))
        t = time.time()
        for _ in range(100):
            L.step()
        res[f"r{r}_coupled_1s"] = time.time() - t
    b = [x for x in J.bench_jobs(BASELINE) if x["seed"] == 0 and x["arm"] == "silent"][0]
    t = time.time()
    J.bench_one(dict(b, stage="preflight"))
    res["bench_silent_10s"] = time.time() - t
    t = time.time()
    J.life_one(dict(j), trace=True)
    res["native_100s_life_traced"] = time.time() - t
    t = time.time()
    J.life_one(dict(j), trace=False)
    res["native_100s_life"] = time.time() - t
    W = WORKERS
    # body-observation overhead is included (life_one observes); 1 s coupled lives extrapolated x100 plus the
    # native observation overhead share; conservative x1.25 allowance on every stage
    est = dict(bench_s=31104 * res["bench_silent_10s"] * 1.3 / W, develop_s=31104 * res["native_100s_life"] / W,
               confirm_s=4 * N_CONFIRM * 12 * sum(res[f"r{r}_coupled_1s"] * 100 * 1.15 for r in RATIOS) / W)
    est["total_s"] = sum(est.values())
    est["total_with_1.25x_s"] = 1.25 * est["total_s"]
    remaining = time.mktime(time.strptime(DEADLINE, "%Y-%m-%dT%H:%M:%SZ")) - time.mktime(time.gmtime())
    est["remaining_budget_s"] = remaining
    est["reserve_reporting_s"] = 3600 * 1.5
    est["fits"] = est["total_with_1.25x_s"] + est["reserve_reporting_s"] <= remaining
    out = dict(timing=res, estimate=est,
               note="bench x1.3 for the sustained schedule's pulses; confirm 1 s coupled timings x100 x1.15 for "
                    "observation; all x1.25 allowance. Reward not read.")
    (OUT / "preflight.json").write_text(json.dumps(out, indent=1) + "\n")
    log(f"preflight: {json.dumps(out)}")
    return out


def stage_bench(dry, resume):
    import ag_jobs as J
    tasks, keys = bench_plan()
    return execute("bench", tasks, J.bench_group, keys, resume, dry)


def stage_develop(dry, resume):
    import ag_jobs as J
    tasks, keys = dev_plan()
    return execute("develop", tasks, J.life_task, keys, resume, dry)


def stage_analyse(dry, resume):
    if dry:
        print("analyse: R2 bench tables, R4 reconciliation and costs, R5 81-row tables and selection")
        return
    import ag_report
    ag_report.analyse(OUT)


def stage_confirm(dry, resume):
    sel = OUT / "selection.json"
    if not sel.exists():
        if dry:
            print("confirm: 18432 lives (4 configs x 128 seeds x 12 lives x 3 ratios) after selection")
            return
        raise SystemExit("confirm needs selection.json (run analyse)")
    fz = OUT / "confirm_freeze.json"
    if not fz.exists():
        import ag_seeds
        S = json.loads(sel.read_text())
        if len(S["selected"]) != 3:
            log(f"confirm: only {len(S['selected'])} complete candidates; R5/R6 incomplete, no replacements")
            return
        if dry:
            print("confirm: would freeze", S["selected"])
            return
        audit = ag_seeds.first_unused(N_CONFIRM)
        C, base = configs()
        d = dict(configs=[base] + S["selected"], seeds=[audit["start"], audit["end"]], audit=audit,
                 selection_sha256=sha(sel), ratios=RATIOS, noise="coupled",
                 time=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        fz.write_text(json.dumps(d, indent=1, default=list) + "\n")
        log(f"confirm frozen: {d['configs']} seeds {d['seeds']}")
    import ag_jobs as J
    tasks, keys = confirm_plan()
    if not dry and not (OUT / "realised_confirm.json").exists():
        fzd = json.loads(fz.read_text())
        realised_confirm(fzd)
    return execute("confirm", tasks, J.life_task, keys, resume, dry)


def realised_confirm(fz):
    rows = []
    with ProcessPoolExecutor(max_workers=WORKERS, mp_context=multiprocessing.get_context("spawn")) as pool:
        for res in pool.map(realised_one, [(c, list(range(fz["seeds"][0], fz["seeds"][1] + 1))) for c in fz["configs"]]):
            rows += res
    fails = [r for r in rows if r["failed"]]
    (OUT / "realised_confirm.json").write_text(json.dumps(dict(rows=rows, failed=len(fails), failed_rows=fails),
                                                          indent=0) + "\n")
    log(f"realised confirm table: {len(rows)} engines, {len(fails)} failed")


def stage_report(dry, resume):
    if dry:
        print("report: R6/R7 confirmation tables, convergence, physical eligibility")
        return
    import ag_report
    ag_report.confirm_report(OUT)


STAGES = dict(check=stage_check, bench=stage_bench, develop=stage_develop, analyse=stage_analyse,
              confirm=stage_confirm, report=stage_report)

if __name__ == "__main__":
    st = sys.argv[1]
    dry, resume = "--dry-run" in sys.argv, "--resume" in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    if not dry:
        log(f"invoke {' '.join(sys.argv[1:])} pid {os.getpid()}")
    for s in (list(STAGES) if st == "all" else [st]):
        STAGES[s](dry, resume or st == "all")

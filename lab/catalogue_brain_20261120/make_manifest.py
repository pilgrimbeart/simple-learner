"""D180 R0: freeze manifest.json (refuses to overwrite)."""
import hashlib, json, subprocess, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
p = ROOT / "lab/v/catalogue_brain_20261120/manifest.json"
if p.exists():
    raise SystemExit(f"{p} exists: refusing to overwrite")
inputs = ["lab/WORK_ORDER_2026-11-20_catalogue_brain.md", "lab/catalogue_brain_20261120/DESIGN.md",
          "lab/catalogue_brain_20261120/design.py", "AGENTS.md", "mixed_feedback.py", "units.py", "chip.py",
          "creature.py", "world.py", "brains/circuit.py", "minimal/spice.py", "requirements.txt"]
code = sorted(str(q.relative_to(ROOT)) for q in HERE.glob("*.py")) + sorted(str(q.relative_to(ROOT)) for q in HERE.glob("*.md"))
h = lambda f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest()
git = lambda *a: subprocess.check_output(["git", *a], cwd=ROOT, text=True).strip()
import run, bench, numpy, numba
m = dict(frozen=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), HEAD=git("rev-parse", "HEAD"),
         dirty_inputs={f: dict(sha256=h(f), modified=bool(git("status", "--porcelain", f))) for f in inputs},
         code={f: h(f) for f in code},
         dependencies=dict(python=sys.version.split()[0], numpy=numpy.__version__, numba=numba.__version__,
                           requirements=(ROOT / "requirements.txt").read_text().split()),
         commands=["OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/catalogue_brain_20261120/run.py " + s
                   for s in ("check", "bench", "action", "learn", "confirm --dry-run", "confirm", "refine", "report")],
         units="SI; V_TYP=0.3 V, RAIL=0.9 V, DT=0.125 ms, TICK=10 ms, PULSE=2.5 ms; reward per 10 s",
         seeds=dict(component=list(range(8)), development=[8, 39], confirmation="2027010000.. after audit (seed_audit.py)",
                    circuit="world+1000003 streams", init="default_rng([seed,180,1])", wiring="default_rng([seed,180,2])",
                    bench_B_jitter="default_rng([seed,180,3,crc32(case)])", bench_C_times="default_rng([seed,180,4,ch])",
                    analysis="default_rng(180) per interval, 10000 resamples"),
         arms=dict(action=["informed", "neutral", "reversed", "no_explore", "no_sensory", "informed_allfood", "neutral_allfood"],
                   learn=["learned", "writers_removed", "learned_allfood", "writers_removed_allfood",
                          "(reused) taste_withheld=R5 neutral", "(reused) informed=R5 informed"],
                   confirm=["learned", "writers_removed", "informed", "learned_allfood", "writers_removed_allfood"]),
         removals={k: list(v) for k, v in __import__("brain").REMOVALS.items()},
         expected_rows=dict(bench_A=24 + 8 + 4, bench_B=8 * len(bench.cases_B()) + 4 * 12, bench_C=2 * 8 * 3 * 32 + 4 * 32,
                            action=len(run.action_jobs(1)), learn=len(run.learn_jobs(1)), confirm="8*N per step, 3 steps"),
         metric_code=dict(analyse=h("lab/catalogue_brain_20261120/analyse.py")),
         predictions=h("lab/catalogue_brain_20261120/PREDICTIONS.md"), protocol=h("lab/catalogue_brain_20261120/PROTOCOL.md"),
         arrays="realised component arrays for seeds 0-7, index-to-name maps and initial states: checks.json (physical); "
                "per life: arrays_hash in each ledger row; design.py gives node/edge order (index = position)",
         budget=dict(start="2026-11-20T15:50Z", cap_h=12, stages_h=dict(impl_preflight=2, bench=2, action=1, learn=1,
                                                                      validation=4, report=1, contingency=1)))
p.write_text(json.dumps(m, indent=1) + "\n")
print(json.dumps(m["expected_rows"]), m["HEAD"])

"""D178: freeze manifest.json (revision, dirty input hashes, commands, seeds, arms, parameters, metrics, analysis
version). Addenda are appended as manifest_addendum_<n>.json, never by rewriting this file."""
import hashlib, json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
FILES = ["brains/designed.py", "brains/circuit.py", "creature.py", "world.py", "mixed_feedback.py", "units.py", "chip.py"]
def sha(p): return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
def main(name="manifest.json", extra=None):
    rev = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
    m = dict(
        revision=rev,
        engine_files_dirty=[l for l in dirty if any(l.endswith(f) for f in FILES)],
        dirty_tracked=[l for l in dirty if not l.startswith("??")],
        hashes={f: sha(f) for f in FILES} | {str(p.relative_to(ROOT)): sha(p.relative_to(ROOT)) for p in sorted(HERE.glob("*.py"))},
        python=".venv/bin/python, OPENBLAS/OMP/MKL threads 1, 7 spawn workers",
        work_order="lab/WORK_ORDER_2026-11-20_robot_action.md",
        seeds="development seeds 0-31, each red then blue as poison (64 lives), 100 s; all-food one life per seed per poison label (64; red/blue labels give two worlds per seed as in D176)",
        substrates={"biology": "mixed_feedback SUBSTRATES['biology'] (historical replication)",
                    "silicon": "mixed_feedback SUBSTRATES['silicon'] via Circuit(substrate=...) only; VOLT 1 V, on_chip False: noise-only diagnostic, not an on-chip implementation"},
        circuit="brains/designed.py DesignedBrain unmodified, via lab adapter brain.make_brain; D176 repairs: P memory nodes, taste writers' thresholds +-0.8 V",
        arms={"learn": "taste-driven learning", "frozen": "Life(learning=False); knobs start 0.5",
              "informed": "Life(learning=False); food knob 1.0, poison knob 0.0 at birth (PRIVILEGED: wiring and valence)",
              "allfood": "both colours food, learning on"},
        metrics=dict(primary="(food-poison) per 10 s in the fixed final third of the 100 s life (ticks 6667-9999), all lives",
                     secondary="D176's: last third of time after moving began",
                     separate="food and poison counts and rates; stranding (no meal in life) Wilson 95%; knob order/strong state (>=0.8/<=0.2) end/ever/lost; path length; motor/sensor spike rates",
                     uncertainty="paired bootstrap over seeds (seed mean of red/blue lives), 4000 resamples, rng 178, 95% percentile",
                     job_limits="food rate lower bound >= 1/10 s; pooled food:poison >= 3; stranding Wilson upper <= 5%",
                     margins=dict(useful=+0.10, allfood_no_harm=-0.05, stranding_no_harm=+0.05)),
        stage1_branch="stop historical branch only if informed AND learning silicon pass all job limits AND learning silicon - learning biology lower bound > +0.10; else stage 2",
        commands=["python lab/robot_action_20261120/checks.py  (R1; also produces the biology stage-1 captures)",
                  "python lab/robot_action_20261120/capture.py <arm> silicon 0 31",
                  "python lab/robot_action_20261120/stage1.py  (summaries, contrasts, replay)"],
        large_outputs=str(Path.home() / "nca-scratch-backup/robot_action_20261120"),
        analysis_version="metrics.py as hashed",
    )
    if extra: m["addendum"] = extra
    out = ROOT / "lab/v/robot_action_20261120" / name
    assert not out.exists(), f"{out} exists: write an addendum instead"
    json.dump(m, open(out, "w"), indent=1)
    print("wrote", out)
if __name__ == "__main__":
    main(*(sys.argv[1:2] or ["manifest.json"]), extra=sys.argv[2] if len(sys.argv) > 2 else None)

"""Freeze the input manifest of the calibration-precision work order (D168) before any calculation.
Writes lab/v/calibration_precision_20261120/manifest.json once (refuses to overwrite). Template: D167's manifest.py."""
import hashlib,json,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'lab/v/calibration_precision_20261120'
INPUTS=['lab/WORK_ORDER_2026-11-20_calibration_precision.md','PROGRAMME.md','AGENTS.md','MIXED_FEEDBACK.md','PARTS.md',
 'units.py','chip.py','mixed_feedback.py','discrete/NOTEBOOK.md',
 'lab/calibration_next_20261120/t1b_weights.py','lab/calibration_next_20261120/t2_readout_error.py',
 'lab/order_long_calibration.py','lab/order_baseline_stream.py','lab/order_continuous_baseline.py','lab/order_local_calibration.py',
 'lab/order_balance_information.py','lab/order_bench.py','lab/population_trace_margin.py','lab/dynamic_parts_bench.py',
 'lab/overnight_20261119_support.py',
 'lab/v/calibration_next_20261120/index.json','lab/v/calibration_next_20261120/t2/rows.jsonl','lab/v/calibration_next_20261120/t2/summary.json',
 'lab/v/calibration_next_20261120/t1b/records.jsonl','lab/v/calibration_next_20261120/t1b/status.json',
 'lab/v/motifs/order_v2/confirm.jsonl','lab/v/order_long_calibration/streams.json','lab/v/order_long_calibration/draws.json',
 'lab/v/order_balance_information/branches.json','lab/v/order_balance_information/draws.json',
 'lab/v/order_continuous_baseline/observations.json','lab/v/order_calibration_precision/rows.json',
 'lab/v/overnight_20261119/failures_results/feasible_intervals.json',
 'lab/v/overnight_20261119/histories_results/settings.jsonl']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    rev=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    st=subprocess.run(['git','status','--porcelain','--untracked-files=all'],cwd=ROOT,capture_output=True,text=True).stdout.splitlines()
    dirty={}
    for line in st:
        p=ROOT/line[3:]
        if p.is_file() and p.stat().st_size<50_000_000:dirty[line[3:]]=sha(p)
    m=dict(created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),revision=rev,
        inputs={p:sha(ROOT/p) for p in INPUTS},
        dirty_files={k:v for k,v in dirty.items() if not k.startswith(('lab/calibration_precision_20261120','lab/v/calibration_precision_20261120'))},
        git_status_lines=len(st),note='discrete/NOTEBOOK.md hashed after the D168 Before-work record was appended, before any calculation')
    with (OUT/'manifest.json').open('x') as f:json.dump(m,f,indent=2)
    print(len(m['inputs']),'inputs;',len(m['dirty_files']),'dirty files hashed; revision',rev)
if __name__=='__main__':main()

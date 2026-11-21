"""Freeze the input manifest of the shared-readout work order (D170) before any calculation.
Writes lab/v/shared_readout_20261120/manifest.json once (refuses to overwrite). Later additions go to dated
manifest_addendum_*.json files written by `python manifest.py addendum NAME path...`, never by replacement.
Template: D168's manifest.py."""
import hashlib,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'lab/v/shared_readout_20261120'
INPUTS=['lab/WORK_ORDER_2026-11-20_shared_readout.md','PROGRAMME.md','AGENTS.md','README.md','MIXED_FEEDBACK.md','PARTS.md',
 'units.py','chip.py','mixed_feedback.py','discrete/NOTEBOOK.md',
 'lab/calibration_next_20261120/t1b_weights.py','lab/calibration_precision_20261120/d_quiet_reference.py',
 'lab/calibration_precision_20261120/b_error_arithmetic.py','lab/calibration_precision_20261120/e_noise_wall.py',
 'lab/order_long_calibration.py','lab/order_baseline_stream.py','lab/order_continuous_baseline.py',
 'lab/population_trace_margin.py','lab/dynamic_parts_bench.py','lab/overnight_20261119_support.py','lab/order_balance_information.py',
 'lab/v/calibration_precision_20261120/index.json','lab/v/calibration_precision_20261120/REPORT.md',
 'lab/v/calibration_precision_20261120/STATUS.md','lab/v/calibration_precision_20261120/b/error_map.md',
 'lab/v/calibration_precision_20261120/b/arithmetic.json','lab/v/calibration_precision_20261120/d/records.jsonl',
 'lab/v/calibration_precision_20261120/d/analysis.json','lab/v/calibration_precision_20261120/e/noise_wall.json',
 'lab/v/motifs/order_v2/confirm.jsonl','lab/v/order_long_calibration/streams.json','lab/v/order_long_calibration/draws.json',
 'lab/v/order_balance_information/branches.json']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    if len(sys.argv)>2 and sys.argv[1]=='addendum':
        name=sys.argv[2];m=dict(created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),files={p:sha(ROOT/p) for p in sys.argv[3:]})
        with (OUT/f'manifest_addendum_{name}.json').open('x') as f:json.dump(m,f,indent=2)
        print('addendum',name,len(m['files']),'files');return
    rev=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    st=subprocess.run(['git','status','--porcelain','--untracked-files=all'],cwd=ROOT,capture_output=True,text=True).stdout.splitlines()
    dirty={}
    for line in st:
        p=ROOT/line[3:]
        if p.is_file() and p.stat().st_size<50_000_000:dirty[line[3:]]=sha(p)
    m=dict(created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),revision=rev,
        inputs={p:sha(ROOT/p) for p in INPUTS},
        dirty_files={k:v for k,v in dirty.items() if not k.startswith(('lab/shared_readout_20261120','lab/v/shared_readout_20261120'))},
        git_status_lines=len(st),
        note='discrete/NOTEBOOK.md hashed after the D170 Before-work record was appended, before any calculation. '
             'Parameters, error-draw allocation and tracker/knob initialisation are frozen in CONTRACT.md and bounds.json '
             '(hashed in an addendum before the replay).')
    with (OUT/'manifest.json').open('x') as f:json.dump(m,f,indent=2)
    print(len(m['inputs']),'inputs;',len(m['dirty_files']),'dirty files hashed; revision',rev)
if __name__=='__main__':main()

"""D128 temporal failure classification and fixed-current trace decay prediction; no new simulations."""
import json,sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import DT,digest
out=Path(__file__).resolve().parents[1]/'lab/v/motifs/order_v1'
rows=[json.loads(l) for l in (out/'pilot.jsonl').read_text().splitlines()];rows=[r for r in rows if not r['control'] and r['dt']==DT/4]
failures=[]
for r in rows:
    if r['passed']:continue
    d=r['case']['delay'];ix=2 if d>0 else 3;cap=r['nodes'][2][ix];leak=r['nodes'][1][ix];tau=cap/leak
    def tail(tau):return tau*(-math.expm1(-.04/tau))*math.exp(-max(abs(d)-.04,0)/tau)
    ratio=tail(tau*1.5)/tail(tau)
    failures.append(dict(seed=r['seed'],case=r['case'],criteria=r['criteria'],actual_trace_tau_s=tau,
        order_V=r['metrics']['order_V'],predicted_tail_ratio=ratio,approx_order_after_V=r['metrics']['order_V']*ratio))
result=dict(failed_cases=len(failures),evaluated_cases=len(rows),failures=failures,
    all_failures_long_gap_weak_correct_sign=all(abs(r['case']['delay'])==.15 and r['order_V']*r['case']['delay']>0 for r in failures),
    source_sha256=digest(__file__),input_sha256=digest(out/'pilot.jsonl'),
    limitation='Rectangular constant-current approximation of first trace; input lag, threshold, offsets and downstream nonlinearities remain in the actual simulator. Prediction is not a pass label.')
(out/'diagnosis.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

"""Independent consistency checks and readable D135 report; no simulation reruns."""
import json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,digest
for name in ['trace_margin','phase_bias','pulse_recovery']:
    out=ROOT/'lab/v'/name;p=json.loads((out/'provenance.json').read_text());assert digest(out/'protocol.json')==p['protocol_sha256']
    for path,h in p['files'].items():assert digest(ROOT/path)==h,(name,path)
out=ROOT/'lab/v/trace_margin';req=json.loads((out/'requirements.json').read_text());s=json.loads((out/'summary.json').read_text());assert s['common_nominal_threshold_V']==max(r['nominal_required_V'] for r in req)
assert s['maximum_rest_at_bound_V']<=.003+1e-14
assert s['maximum_quadrature_change_V']<1e-6
lines=['# Quiet-trace sensitivity bound — D135','',f'A common nominal threshold of **{s["common_nominal_threshold_V"]:.4f} V** limits the predicted resting trace to 3 mV (1% gate opening) on the six previously failed draws. The old threshold was 0.15 V, with resting traces as high as {s["original_maximum_rest_V"]*1000:.1f} mV. Each observed threshold error is preserved in the calculation.','','The weakest tested input still leaves the following signal at that bound:','','| Measurement | Range across 12 trace branches (mV) |','|---|---:|']
labels={'peak_V':'Peak','onset_60ms_V':'60 ms after input onset','onset_150ms_V':'150 ms after input onset','offset_60ms_V':'60 ms after input offset','offset_150ms_V':'150 ms after input offset'}
for key,values in s['range_at_bound'].items():lines.append(f'| {labels[key]} | {values[0]*1000:.1f}–{values[1]*1000:.1f} |')
lines+=['',f'The original transfer-equation prediction matches the two saved first-confirmation trace branches with RMS errors of '+', '.join(f'{r["rmse_V"]*1000:.3f} mV' for r in s['saved_trace_validation'])+'. Halving quadrature spacing changes the predicted voltage by at most '+f'{s["maximum_quadrature_change_V"]*1e6:.3f} µV.','', 'This is an informed feasibility bound, not a selected repair. The 1% target is diagnostic; it does not replace the frozen order criteria. Equality leaves no stochastic margin, and a measurable trace need not be strong enough for the whole comparison circuit. Threshold and downstream balance require separate treatment. No general offset tolerance or fresh-seed reliability claim.','', 'Protocol, full tradeoff curve, source hashes and approximation checks are retained here. Rail fading and noise are omitted only in this transfer-equation analysis, checked against saved noisy traces. Sources: lab/trace_margin.py; readable report/audit: lab/catalogue_diagnostic_audit.py.']
(out/'report.md').write_text('\n'.join(lines)+'\n')
out=ROOT/'lab/v/phase_bias';rows=json.loads((out/'predictions.json').read_text());s=json.loads((out/'summary.json').read_text());assert len(rows)==480
rr=[r for r in rows if r['mode']=='original'];rmse=np.sqrt(np.mean([(r['mean_V']-r['observed_mean_V'])**2 for r in rr]));assert abs(rmse-s['validation_rmse_V'])<1e-15
assert all(r['mean_V']==0 for r in rows if r['mode']=='both_matched')
assert s['maximum_resolution_change_V']<1e-10
print('All three protocols and source hashes verified; trace bound, quadrature, phase prediction and matched symmetry checked.')

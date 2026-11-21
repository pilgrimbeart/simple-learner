"""Check D139 predictions against stored labels and original response margins."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
rows=json.loads((ROOT/'lab/v/population_trace_margin/rows.json').read_text())
raw=[json.loads(s) for s in (ROOT/'lab/v/motifs/order_v2/confirm.jsonl').read_text().splitlines()]
raw=[r for r in raw if r['dt']==min(x['dt'] for x in raw[:3])]
lookup={(r['seed'],r['case']['id']):r for r in raw}
original=[r for r in rows if r['mode']=='original']
assert len(original)==len(lookup)==1360
mismatch=[(r['seed'],r['case']['id']) for r in original if r['metric_adequate']!=lookup[r['seed'],r['case']['id']]['passed']]
print(json.dumps(dict(original_predicted_vs_recorded_pass_disagreements=mismatch),indent=2))
assert not mismatch
# Count near-threshold order predictions at the measured maximum original approximation error.
error=json.loads((ROOT/'lab/v/population_trace_margin/summary.json').read_text())['validation']['order_V']['maximum_error_V']
result={}
for mode in sorted({r['mode'] for r in rows}):
    margins=[]
    for r in rows:
        if r['mode']!=mode:continue
        c=r['case'];d=c['delay'];pair=c['a']>0 and c['b']>0
        margin=(1 if d>0 else -1)*r['order_V']-.03 if pair and 0<abs(d)<=.15 else (.06 if pair and d==0 else .03)-abs(r['order_V'])
        margins.append(margin)
    result[mode]=dict(order_cases_within_original_max_error_of_threshold=sum(abs(m)<=error for m in margins),
        failed_by_more_than_original_max_error=sum(m < -error for m in margins))
print(json.dumps(result,indent=2))

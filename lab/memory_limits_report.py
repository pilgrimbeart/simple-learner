"""D129 passive analysis and analytic RC/write-driver bias prediction."""
import json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,DT,digest,interval
from retained_write_report import svg_plot
from retained_write_preview import render
import chip
OUT=ROOT/'lab/v/memory_limits';rows=[json.loads(l) for l in (OUT/'rows.jsonl').read_text().splitlines()];protocol=json.loads((OUT/'protocol.json').read_text());assert len(rows)==384
assert len({(r['seed'],r['case']['id'],r['dt']) for r in rows})==384
prov=json.loads((OUT/'provenance.json').read_text());assert prov['protocol_sha256']==digest(OUT/'protocol.json')
for p,h in prov['files'].items():assert digest(ROOT/p)==h
fine=[r for r in rows if r['dt']==DT/4];bycase={};predictions=[]
for case in protocol['cases']:
    rr=[r for r in fine if r['case']['id']==case['id']];vals=[r['metrics']['write_delta_V'] for r in rr]
    bycase[case['id']]=dict(min_delta_V=min(vals),max_delta_V=max(vals),mean95=interval(vals),abs_below_1mV=sum(abs(v)<.001 for v in vals))
for r in fine:
    if r['case']['id']!='gate_only':continue
    n=np.array(r['nodes']);e=np.array(r['elements']);pulse=r['pulses'][0];duration=pulse[1];cur=pulse[3];tau=n[2,1]/n[1,1]
    t=np.linspace(0,5-pulse[0],200001);v=np.where(t<=duration,cur/n[1,1]*(1-np.exp(-t/tau)),cur/n[1,1]*(1-np.exp(-duration/tau))*np.exp(-(t-duration)/tau))
    gain,offset,slope=e[:3,1];raw=gain*np.tanh(-slope*offset)*np.clip(v/.3,0,1);current=np.sign(raw)*np.maximum(np.abs(raw)-chip.DEAD*abs(gain),0)
    expected=float(np.trapezoid(current,t)/n[2,2]);actual=r['metrics']['write_delta_V'];predictions.append(dict(seed=r['seed'],predicted_gate_only_delta_V=expected,observed_delta_V=actual,error_V=actual-expected,writer_offset_V=float(offset)))
ref={}
for case in protocol['cases']:
    for coarse,fine_dt in [(DT,DT/2),(DT/2,DT/4)]:
        aa={r['seed']:r['metrics']['write_delta_V'] for r in rows if r['case']['id']==case['id'] and r['dt']==coarse};bb={r['seed']:r['metrics']['write_delta_V'] for r in rows if r['case']['id']==case['id'] and r['dt']==fine_dt}
        ref[f'{case["id"]}:{coarse}']=interval([bb[s]-aa[s] for s in protocol['seeds']])
repeated=[r for r in fine if r['case']['kind']=='repeated'];result=dict(source_sha256=digest(__file__),input_sha256=digest(OUT/'rows.jsonl'),cases=bycase,analytic_gate_only_prediction=predictions,
    prediction_RMSE_V=float(np.sqrt(np.mean([r['error_V']**2 for r in predictions]))),step_differences_V=ref,
    repeated_saturation_success=sum(abs(r['metrics']['plateau_V'])>.89 for r in repeated),reverse_write_success=sum(-r['case']['sign']*r['metrics']['reverse_change_V']>.03 for r in repeated),repeated_denominator=len(repeated),
    limitations='Exploratory8draws; RC analytic expectation omits tiny sigmoid noise rectification and rail fade, not a noiseless alternate simulation. Memory saturation and idle hold follow the engine contract.')
(OUT/'analysis.json').write_text(json.dumps(result,indent=2)+'\n')
text=['# Retained-memory limits — D129','','The original gate protects memory when closed, but opening it without evidence can write a substantial false value. The missing control exposes transfer-offset leakage. This does not change the older frozen result.','',f'Gate-only writes below1mV: {bycase["gate_only"]["abs_below_1mV"]}/8. Evidence-only writes below1mV: {bycase["evidence_only"]["abs_below_1mV"]}/8.',f'Analytic gate-only RC/write-driver prediction RMSE: {result["prediction_RMSE_V"]:.6g} V.',f'Repeated-write saturation: {result["repeated_saturation_success"]}/16; opposite-write release: {result["reverse_write_success"]}/16.','', '| Condition | Minimum stored change,V | Maximum stored change,V |','|---|---:|---:|']
for case,v in bycase.items():text.append(f'| {case} | {v["min_delta_V"]:.6g} | {v["max_delta_V"]:.6g} |')
text+=['','Far-separated evidence produces essentially the gate-only bias. Subtracting that bias in analysis reveals the overlap contribution, but such observer subtraction is not a circuit repair. The next mechanism should reject absent evidence explicitly, using existing parts if possible.','',result['limitations'],'','All384rows retained in rows.jsonl. Protocol, original code hashes and exact component draws are retained. Source: lab/memory_limits.py and lab/memory_limits_report.py. D127 graph/parts are unchanged; per-run supply power and gross-charge activity remain in rows. Large traces are local at '+str(OUT)+'/*.npz; hashes in trace_manifest.json.']
(OUT/'report.md').write_text('\n'.join(text)+'\n');(OUT/'trace_manifest.json').write_text(json.dumps({str(p.resolve()):digest(p) for p in OUT.glob('*.npz')},indent=2)+'\n')
tr=np.load(OUT/'gate_only.npz')['trace'];svg=svg_plot([(tr[:,0],tr[:,2],'eligibility'),(tr[:,0],tr[:,3],'stored')],'Gate opens; evidence remains absent',(1.3,2.5),(-.05,.7));p=OUT/'gate_only.svg';p.write_text(svg);render(p)
tr1=np.load(OUT/'repeated_1.npz')['trace'];tr2=np.load(OUT/'repeated_-1.npz')['trace'];svg=svg_plot([(tr1[:,0],tr1[:,3],'positive repeats'),(tr2[:,0],tr2[:,3],'negative repeats')],'Memory bounds and opposite-write release',(0,26),(-1,1));p=OUT/'repeated.svg';p.write_text(svg);render(p)
print(json.dumps({k:v for k,v in result.items() if k not in ('cases','analytic_gate_only_prediction','step_differences_V')},indent=2));print('gate only below1mV',bycase['gate_only']['abs_below_1mV'],'/8')

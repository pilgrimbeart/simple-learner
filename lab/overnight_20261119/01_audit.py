"""Task A (overnight 2026-11-19): independent audit of D155-D164 inputs and the D162 oscillator confirmation.
Observer arithmetic on saved records only; no simulation, no old main().
"""
import hashlib,json,math,sys
from pathlib import Path
from statistics import NormalDist
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'lab'))
def fresh(name):
    base=ROOT/'lab/v/overnight_20261119'
    for n in [name,name+'_retry1',name+'_retry2']:
        if not (base/n).exists():(base/n).mkdir();return base/n
    raise RuntimeError('No retry directory left')
OUT=fresh('audit_results')
from dynamic_parts_bench import metrics  # listed measurement function, used only on saved traces
from units import MISMATCH,V_TYP,TAU_MAX
V=ROOT/'lab/v';TOL=1e-12
discrepancies=[];checks={}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def note(kind,detail):discrepancies.append(dict(kind=kind,detail=detail))
def jl(p):return [json.loads(l) for l in Path(p).read_text().splitlines()]
def boot_mean(values,seed=126,n=4000):
    a=np.asarray(values,dtype=float);idx=np.random.default_rng(seed).integers(0,len(a),(n,len(a)))
    m=a[idx].mean(axis=1);return [float(a.mean()),float(np.quantile(m,.025)),float(np.quantile(m,.975))]
def wilson(k,n,z=NormalDist().inv_cdf(.975)):
    p=k/n;den=1+z*z/n;mid=(p+z*z/(2*n))/den;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den;return [mid-half,mid+half]
def close(a,b,tol=TOL):return abs(a-b)<=tol

# 1. Manifest and provenance hashes
manifest=json.loads((ROOT/'lab/overnight_20261119_inputs.json').read_text());bad=[]
for name,info in manifest['files'].items():
    p=ROOT/name
    if not p.exists():bad.append(dict(file=name,problem='missing'));continue
    h=sha(p);n=p.stat().st_size
    if h!=info['sha256'] or n!=info['bytes']:bad.append(dict(file=name,problem='hash/bytes differ',expected=info['sha256'],got=h))
checks['manifest']=dict(files=len(manifest['files']),mismatches=bad)
for b in bad:note('manifest',b)
prov={}
for d in ['order_balance_information','order_local_calibration','order_continuous_baseline','order_baseline_stream','order_long_calibration','order_calibration_precision','adaptive_oscillator','adaptive_oscillator_confirm']:
    pdir=V/d;pp=pdir/'provenance.json'
    if not pp.exists():prov[d]=dict(status='provenance missing');note('provenance_missing',d);continue
    p=json.loads(pp.read_text());diff=[]
    for name,h in p['files'].items():
        cur=sha(ROOT/name) if (ROOT/name).exists() else None
        if cur!=h:diff.append(dict(file=name,recorded=h,current=cur))
    proto=pdir/'protocol.json';pmatch=(sha(proto)==p.get('protocol_sha256')) if proto.exists() else None
    prov[d]=dict(revision=p.get('revision'),files_checked=len(p['files']),file_mismatches=diff,protocol_sha256_matches=pmatch,dirty_recorded=bool(p.get('dirty')))
    for x in diff:note('provenance_file',dict(result=d,**x))
    if pmatch is not True:note('provenance_protocol',dict(result=d,matches=pmatch))
checks['provenance']=prov

# 2-5. Oscillator confirmation
C=V/'adaptive_oscillator_confirm';proto=json.loads((C/'protocol.json').read_text());rows=jl(C/'rows.jsonl')
seeds=proto['seeds'];arms=proto['arms'];steps=proto['steps_s']
keys={(r['seed'],r['arm'],r['dt']) for r in rows};want={(s,a,t) for s in seeds for a in arms for t in steps}
checks['oscillator_coverage']=dict(records=len(rows),unique=len(keys),declared=len(want),missing=len(want-keys),undeclared=len(keys-want))
if not(len(rows)==360 and keys==want):note('oscillator_coverage',checks['oscillator_coverage'])
R={(r['seed'],r['arm'],r['dt']):r for r in rows}
saved=json.loads((C/'summary.json').read_text())
passed={a:{s:all(R[s,a,t]['metrics']['passed'] for t in steps) for s in seeds} for a in arms}
osc={}
for a in arms:
    k=sum(passed[a].values());w=wilson(k,40)
    osc[a]=dict(passed=k,wilson95=w,saved_passed=saved[a]['passed'],saved_wilson95=saved[a]['wilson95'],failed=[s for s in seeds if not passed[a][s]])
    if k!=saved[a]['passed'] or not all(close(x,y) for x,y in zip(w,saved[a]['wilson95'])):note('oscillator_pass',dict(arm=a,mine=[k,w],saved=[saved[a]['passed'],saved[a]['wilson95']]))
paired={}
for other in ['original','writer_removed']:
    diff=[float(passed['adaptive'][s])-float(passed[other][s]) for s in seeds];iv=boot_mean(diff)
    paired[other]=dict(pass_difference=iv,includes_zero=bool(iv[1]<=0<=iv[2]),rescued=[s for s in seeds if passed['adaptive'][s] and not passed[other][s]],harmed=[s for s in seeds if passed[other][s] and not passed['adaptive'][s]],saved=saved['paired'][other]['pass_difference'])
    if not all(close(x,y) for x,y in zip(iv,saved['paired'][other]['pass_difference'])):note('oscillator_paired',dict(other=other,mine=iv,saved=saved['paired'][other]['pass_difference']))
osc['paired']=paired
# step halving
ref={};refbad=[]
for a in arms:
    for coarse,fine in [(steps[0],steps[1]),(steps[1],steps[2])]:
        for key in R[seeds[0],a,steps[0]]['metrics']['normalized']:
            iv=boot_mean([R[s,a,fine]['metrics']['normalized'][key]-R[s,a,coarse]['metrics']['normalized'][key] for s in seeds])
            inside=bool(iv[1]>-.05 and iv[2]<.05);sv=saved[a]['refinement'][f'{coarse}:{key}']
            ref[f'{a}:{coarse}:{key}']=dict(interval=iv,inside_margin=inside,saved=sv)
            if not all(close(x,y) for x,y in zip(iv,sv)):refbad.append(f'{a}:{coarse}:{key}')
            if not inside:note('oscillator_refinement_outside_margin',dict(arm=a,coarse=coarse,key=key,interval=iv))
    if all(v['inside_margin'] for k,v in ref.items() if k.startswith(a+':'))!=saved[a]['refinement_pass']:note('oscillator_refinement_flag',a)
for k in refbad:note('oscillator_refinement_mismatch',k)
osc['refinement']=dict(intervals=len(ref),all_inside=all(v['inside_margin'] for v in ref.values()),mismatches=refbad,detail=ref)
# saved traces
tm=json.loads((C/'trace_manifest.json').read_text());tr_checks=[];maxerr=0.
for path,h in sorted(tm.items()):
    p=Path(path);item=dict(path=path,exists=p.exists())
    if not p.exists():note('trace_missing',path);tr_checks.append(item);continue
    item['sha256_matches']=sha(p)==h
    if not item['sha256_matches']:note('trace_hash',path);tr_checks.append(item);continue
    seed=int(p.stem.split('_')[0]);arm=p.stem.split('_',1)[1];r=R[seed,arm,steps[2]]
    m=metrics('oscillator',[np.load(p)['trace']],[r['cost']]);err=max(abs(m['values'][k]-r['metrics']['values'][k]) for k in m['values'])
    item.update(seed=seed,arm=arm,passed_recomputed=m['passed'],passed_saved=r['metrics']['passed'],max_value_error=err);maxerr=max(maxerr,err)
    if m['passed']!=r['metrics']['passed'] or err>TOL:note('trace_metric',item)
    tr_checks.append(item)
osc['saved_traces']=dict(checked=sum('max_value_error' in t for t in tr_checks),listed=len(tm),of_records=360,finest_records=120,max_value_error=maxerr,detail=tr_checks)
# power and parts
fin=steps[2];power={a:boot_mean([R[s,a,fin]['cost']['power_W'] for s in seeds]) for a in arms}
added={o:boot_mean([R[s,'adaptive',fin]['cost']['power_W']-R[s,o,fin]['cost']['power_W'] for s in seeds]) for o in ['original','writer_removed']}
for a in arms:
    if not all(close(x,y,1e-20) for x,y in zip(power[a],saved[a]['power_W'])):note('power',dict(arm=a,mine=power[a],saved=saved[a]['power_W']))
for o in added:
    if not all(close(x,y,1e-20) for x,y in zip(added[o],saved['paired'][o]['power_difference_W'])):note('added_power',o)
activity={a:dict(gross_charge_C_mean=[float(np.mean([R[s,a,fin]['cost']['gross_charge_C'][i] for s in seeds])) for i in range(len(R[seeds[0],a,fin]['cost']['gross_charge_C']))],
    crossings_mean=[float(np.mean([R[s,a,fin]['cost']['crossings'][i] for s in seeds])) for i in range(len(R[seeds[0],a,fin]['cost']['crossings']))]) for a in arms}
parts=json.loads((V/'adaptive_oscillator/manifest.json').read_text())['parts'];totals={a:sum(parts[a].values()) for a in arms}
if totals!={'original':95,'adaptive':196,'writer_removed':147}:note('parts',totals)
osc.update(power_mean_W_finest=power,added_power_W=added,activity_finest=activity,parts=parts,part_totals=totals,
    memory_pump='excluded under the existing memory contract (writing voltage source and energy not counted); not reinterpreted as included',
    writer_removed_memory_held_all=all(R[s,'writer_removed',t]['memory']['held_exactly'] for s in seeds for t in steps))
checks['oscillator']=osc

# 6. order 1000s
L=V/'order_long_calibration';streams=json.loads((L/'streams.json').read_text());draws=json.loads((L/'draws.json').read_text())
old={r['seed']:r for r in json.loads((V/'order_baseline_stream/streams.json').read_text()) if r['spacing_s']==10.}
branches=json.loads((V/'order_balance_information/branches.json').read_text())
def bounds(c):
    pair=c['a']>0 and c['b']>0;d=c['delay']
    if pair and 0<abs(d)<=.15:return (.03,math.inf) if d>0 else (-math.inf,-.03)
    m=.06 if pair and d==0 else .03;return -m,m
bykey={}
for b in branches:bykey.setdefault(b['seed'],[]).append(b)
cov=dict(branch_records=len(branches),branch_unique=len({(b['seed'],b['case']['id']) for b in branches}),seeds=len(bykey),cases_per_seed=sorted({len(v) for v in bykey.values()}))
modes=['raw','0.15','1.0',str(TAU_MAX)]
dk={(r['seed'],r['mode']) for r in draws}
cov.update(histories=len(streams),unique_histories=len({s['seed'] for s in streams}),settings=len(draws),unique_settings=len(dk),modes=sorted({r['mode'] for r in draws}))
prefix_bad=[s['seed'] for s in streams if [e for e in s['events'] if e['first_s']<99.36]!=old[s['seed']]['events']]
rescore_bad=[];summ={m:dict(adequate_draws=0,adequate_cases=0,rescued=0,harmed=0) for m in modes}
SM={s['seed']:s for s in streams}
for r in draws:
    a,b=SM[r['seed']]['observations_Vs'][r['mode']];rd=-a/b;d=float(np.clip(rd,-1,1))
    if not close(rd,r['raw_d']) or not close(d,r['d']):rescore_bad.append(dict(seed=r['seed'],mode=r['mode'],problem='knob'))
    ok=[];base=[]
    for m in bykey[r['seed']]:
        lo,hi=bounds(m['case']);ok.append(lo<m['u_V']+d*m['v_V']<hi and m['coincidence_adequate']);base.append(lo<m['u_V']<hi and m['coincidence_adequate'])
    got=dict(passed=sum(ok),all_pass=all(ok),rescued=sum(x and not y for x,y in zip(ok,base)),harmed=sum(y and not x for x,y in zip(ok,base)))
    if any(got[k]!=r[k] for k in got):rescore_bad.append(dict(seed=r['seed'],mode=r['mode'],mine=got))
    s=summ[r['mode']];s['adequate_draws']+=got['all_pass'];s['adequate_cases']+=got['passed'];s['rescued']+=got['rescued'];s['harmed']+=got['harmed']
ssum=json.loads((L/'summary.json').read_text())['comparisons']
for m in modes:
    for k in summ[m]:
        if summ[m][k]!=ssum[m][k]:rescore_bad.append(dict(mode=m,key=k,mine=summ[m][k],saved=ssum[m][k]))
for x in rescore_bad:note('order_long_rescore',x)
if prefix_bad:note('order_long_prefix',prefix_bad)
if not(cov['branch_records']==cov['branch_unique']==1360 and cov['cases_per_seed']==[34] and cov['histories']==cov['unique_histories']==40 and cov['settings']==cov['unique_settings']==160):note('order_coverage',cov)
checks['order_1000s']=dict(coverage=cov,prefixes_identical=not prefix_bad,prefix_mismatches=prefix_bad,rescore_mismatches=rescore_bad,recomputed_summary=summ,
    failed_draws={m:sorted(r['seed'] for r in draws if r['mode']==m and not r['all_pass']) for m in modes})

# 7. D164 Gaussian probabilities
P=V/'order_calibration_precision';prows=json.loads((P/'rows.json').read_text());obs=json.loads((V/'order_continuous_baseline/observations.json').read_text())
cap={r['seed']:r for r in json.loads((V/'order_balance_information/draws.json').read_text())};nd=NormalDist();sigma=MISMATCH*V_TYP;pbad=[];maxdiff=0.
for r in prows:
    a=b=w=0.
    for o in obs:
        if o['seed']!=r['seed']:continue
        c=o['case'];near=c['a'] and c['b'] and 0<abs(c['delay'])<=.15;wt=(2*r['prior'] if c['delay']>0 else 2*(1-r['prior'])) if near else 1.
        aa,bb=o['observations_Vs'][f"{r['tau_s']}:random"];a+=wt*aa;b+=wt*bb;w+=wt*o['weight_s']
    cc=cap[r['seed']];feas=cc['feasible_order'] and cc['coincidence_all'];lo,hi=cc['feasible_interval'];el,eu=(a+b*lo)/w,(a+b*hi)/w
    for n in ['1','4','16']:
        s=sigma/math.sqrt(int(n));p=(nd.cdf(eu/s)-nd.cdf(el/s)) if feas else 0.
        maxdiff=max(maxdiff,abs(p-r['conditional_success'][n]))
        if abs(p-r['conditional_success'][n])>TOL:pbad.append(dict(seed=r['seed'],tau=r['tau_s'],prior=r['prior'],n=n,mine=p,saved=r['conditional_success'][n]))
    if not feas and any(r['conditional_success'][n]!=0. for n in ['1','4','16']):pbad.append(dict(seed=r['seed'],problem='infeasible draw given nonzero probability'))
for x in pbad:note('d164',x)
psum=json.loads((P/'summary.json').read_text());exp={k:{n:sum(r['conditional_success'][n] for r in prows if f"{r['tau_s']}:{r['prior']}"==k) for n in ['1','4','16']} for k in psum}
checks['d164']=dict(rows=len(prows),max_probability_difference=maxdiff,mismatches=pbad,infeasible_seeds=sorted(s for s,c in cap.items() if not(c['feasible_order'] and c['coincidence_all'])),expected_adequate=exp,
    assumption='Independent new Gaussian detector error sigma=MISMATCH*V_TYP; 4/16-path rows are hypothetical independent averages, not built or costed')

# hashes of everything read
read=[ROOT/'lab/overnight_20261119_inputs.json',C/'protocol.json',C/'rows.jsonl',C/'summary.json',C/'trace_manifest.json',V/'adaptive_oscillator/manifest.json',L/'streams.json',L/'draws.json',L/'summary.json',V/'order_baseline_stream/streams.json',V/'order_balance_information/branches.json',V/'order_balance_information/draws.json',P/'rows.json',P/'summary.json',V/'order_continuous_baseline/observations.json',ROOT/'lab/dynamic_parts_bench.py',ROOT/'units.py',Path(__file__).resolve()]
inputs={str(p.relative_to(ROOT)):sha(p) for p in read}
audit=dict(task='A',discrepancy_count=len(discrepancies),discrepancies=discrepancies,checks=checks,input_sha256=inputs)
(OUT/'audit.json').write_text(json.dumps(audit,indent=2)+'\n');(OUT/'input_hashes.json').write_text(json.dumps(inputs,indent=2)+'\n');(OUT/'discrepancies.json').write_text(json.dumps(discrepancies,indent=2)+'\n')
o=osc;lines=['# Task A — independent audit','',f'Discrepancies: **{len(discrepancies)}** (listed in `discrepancies.json`).','',
'## Inputs',f"- Manifest: {len(manifest['files'])} files, {len(bad)} mismatches.",*[f"- Provenance `{d}`: {v.get('files_checked','-')} files, {len(v.get('file_mismatches',[]))} current-hash differences, protocol hash matches: {v.get('protocol_sha256_matches')}" for d,v in prov.items()],'',
'## Oscillator confirmation (D162)',f"- Records {len(rows)}, unique keys {len(keys)} of {len(want)} declared (40 seeds x 3 arms x 3 steps).",
*[f"- {a}: {o[a]['passed']}/40 all-steps pass, Wilson95 [{o[a]['wilson95'][0]:.4f}, {o[a]['wilson95'][1]:.4f}]; failed {o[a]['failed']}" for a in arms],
*[f"- Paired pass difference adaptive minus {k}: {v['pass_difference'][0]:+.3f} [{v['pass_difference'][1]:+.3f}, {v['pass_difference'][2]:+.3f}] (seed bootstrap, 4000, RNG 126); includes zero: {v['includes_zero']}. Not evidence of population superiority or of equivalence." for k,v in paired.items()],
f"- Step halving: {len(ref)} intervals recomputed, all inside ±.05: {o['refinement']['all_inside']}; mismatches with saved: {len(refbad)}.",
f"- Saved finest traces: {o['saved_traces']['checked']} remeasured of {o['saved_traces']['listed']} listed (of 120 finest-step records; most traces were not saved). Max value error {maxerr:.3g}.",
*[f"- Mean supply power at finest step, {a}: {power[a][0]*1e9:.3f} nW [{power[a][1]*1e9:.3f}, {power[a][2]*1e9:.3f}]" for a in arms],
*[f"- Added power adaptive minus {k}: {v[0]*1e9:.3f} nW [{v[1]*1e9:.3f}, {v[2]*1e9:.3f}]" for k,v in added.items()],
f"- Core parts: {totals} (memory pump implementation and energy excluded, as before).",
f"- Writer-removed memory held exactly in all 120 records: {o['writer_removed_memory_held_all']}.",'',
'## Order references (D163, D164)',f"- Branch records {cov['branch_records']} (unique {cov['branch_unique']}), 34 cases per seed: {cov['cases_per_seed']==[34]}.",
f"- 1000 s histories {cov['histories']}, settings {cov['settings']} ({len(modes)} modes); 100 s prefixes identical: {not prefix_bad}.",
*[f"- {m}: {summ[m]['adequate_draws']}/40 draws, {summ[m]['adequate_cases']}/1360 cases, rescued {summ[m]['rescued']}, harmed {summ[m]['harmed']}; failed draws {checks['order_1000s']['failed_draws'][m] if len(checks['order_1000s']['failed_draws'][m])<6 else str(len(checks['order_1000s']['failed_draws'][m]))+' draws'}" for m in modes],
f"- Independent rescoring mismatches: {len(rescore_bad)}.",
f"- D164: {len(prows)} rows recomputed with statistics.NormalDist; max probability difference {maxdiff:.3g}; infeasible draws given probability 0: {checks['d164']['infeasible_seeds']}. Independence of a new detector's error is an assumption; 4/16-path rows are hypothetical.",'']
(OUT/'audit.md').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))

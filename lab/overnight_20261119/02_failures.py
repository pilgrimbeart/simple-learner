"""Task B (overnight 2026-11-19): which remaining order failure is 'no setting exists' and which is
'the available calculation selected a bad setting'. Stored branch responses and D163 settings only.
"""
import hashlib,json,math,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];V=ROOT/'lab/v'
def fresh(name):
    base=ROOT/'lab/v/overnight_20261119'
    for n in [name,name+'_retry1',name+'_retry2']:
        if not (base/n).exists():(base/n).mkdir();return base/n
    raise RuntimeError('No retry directory left')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def limits(c):
    pair=c['a']>0 and c['b']>0;d=c['delay']
    if pair and 0<abs(d)<=.15:return (.03,math.inf) if d>0 else (-math.inf,-.03)
    m=.06 if pair and d==0 else .03;return -m,m
def kind(c):
    pair=c['a']>0 and c['b']>0
    if not pair:return 'single'
    if c['delay']==0:return 'simultaneous'
    return 'near' if abs(c['delay'])<=.15 else 'far'
V_ZERO=1e-15

def interval(rows):
    """Allowed open set of d in [-1,1] for u+d*v strictly inside each case's limits."""
    lower=dict(value=-1.,case='knob_limit',coefficient_V=None,threshold_V=None,strict=False,u_V=None)
    upper=dict(value=1.,case='knob_limit',coefficient_V=None,threshold_V=None,strict=False,u_V=None)
    zero_v=[];contradictions=[]
    for r in rows:
        lo,hi=limits(r['case']);u,v=r['u_V'],r['v_V']
        if abs(v)<=V_ZERO:
            zero_v.append(r['case']['id'])
            if not lo<u<hi:contradictions.append(dict(case=r['case']['id'],reason='v~0 and output outside limits regardless of d'))
            continue
        # each finite limit gives one bound on d; direction depends on sign(v)
        for thr,side in [(lo,'low'),(hi,'high')]:
            if not math.isfinite(thr):continue
            bound=(thr-u)/v
            is_lower=(side=='low')==(v>0)
            item=dict(value=bound,case=r['case']['id'],kind=kind(r['case']),coefficient_V=v,threshold_V=thr,strict=True,u_V=u)
            if is_lower and (bound>lower['value'] or (bound==lower['value'] and not lower['strict'])):lower=item
            if not is_lower and (bound<upper['value'] or (bound==upper['value'] and not upper['strict'])):upper=item
    lo,hi=lower['value'],upper['value']
    nonempty=(lo<hi) or (lo==hi and not lower['strict'] and not upper['strict'])
    nonempty=nonempty and not contradictions
    return dict(lower=lower,upper=upper,nonempty=bool(nonempty),width=float(hi-lo),zero_v_cases=zero_v,contradictions=contradictions)

def main():
    OUT=fresh('failures_results')
    bpath=V/'order_balance_information/branches.json';branches=json.loads(bpath.read_text())
    cpath=V/'order_balance_information/draws.json';capacity={r['seed']:r for r in json.loads(cpath.read_text())}
    spath=V/'order_long_calibration/streams.json';streams={r['seed']:r for r in json.loads(spath.read_text())}
    dpath=V/'order_long_calibration/draws.json';settings=json.loads(dpath.read_text())
    by={}
    for b in branches:by.setdefault(b['seed'],[]).append(b)
    assert len(by)==40 and all(len(v)==34 and len({x['case']['id'] for x in v})==34 for v in by.values())
    feas=[];checks=dict(old_interval_mismatch=[],old_feasibility_mismatch=[])
    for seed in sorted(by):
        it=interval(by[seed]);coin=all(r['coincidence_adequate'] for r in by[seed])
        c=capacity[seed]
        if it['nonempty']!=c['feasible_order']:checks['old_feasibility_mismatch'].append(seed)
        if it['nonempty'] and max(abs(it['lower']['value']-c['feasible_interval'][0]),abs(it['upper']['value']-c['feasible_interval'][1]))>1e-12:checks['old_interval_mismatch'].append(seed)
        # margin of the satisfied side at the interval centre, for context
        feas.append(dict(seed=seed,order_feasible=it['nonempty'],coincidence_all=coin,any_setting_suffices=bool(it['nonempty'] and coin),
            interval=[it['lower']['value'],it['upper']['value']],width=it['width'],lower_bound=it['lower'],upper_bound=it['upper'],
            coincidence_failures=[r['case']['id'] for r in by[seed] if not r['coincidence_adequate']],zero_v_cases=it['zero_v_cases'],contradictions=it['contradictions']))
    F={f['seed']:f for f in feas}
    # failed conditions for every old long-history setting
    failed=[]
    for s in settings:
        d=s['d'];rows=[]
        for r in by[s['seed']]:
            lo,hi=limits(r['case']);y=r['u_V']+d*r['v_V'];ok=lo<y<hi
            if not ok or not r['coincidence_adequate']:
                dist=min(y-lo,hi-y)  # negative or zero: violated by this amount (V)
                rows.append(dict(case=r['case']['id'],kind=kind(r['case']),order_V=y,limits_V=[lo,hi],order_ok=ok,distance_to_threshold_V=dist,coincidence_ok=r['coincidence_adequate']))
        fi=F[s['seed']];lo,hi=fi['interval']
        outside=0. if lo<d<hi else (lo-d if d<=lo else d-hi)
        if bool(rows)==s['all_pass']:checks.setdefault('pass_flag_mismatch',[]).append([s['seed'],s['mode']])
        failed.append(dict(seed=s['seed'],mode=s['mode'],d=d,raw_d=s['raw_d'],all_pass=not rows,failed_conditions=rows,
            feasible_interval=fi['interval'],setting_feasible=fi['order_feasible'],distance_outside_interval=outside if fi['order_feasible'] else None))
    # detailed cases
    detail={}
    for seed,label in [(2026112215,'known capacity failure'),(2026112227,'single-anchor calibration failure')]:
        fi=F[seed];ev=streams[seed]['events'];third=[(i,e) for i,e in enumerate(ev) if e['first_s']>=2000/3]
        sim=[dict(index=i,first_s=e['first_s'],a_V=e['case']['a'],b_V=e['case']['b'],case=e['case']['id'],rank_in_final_third=j) for j,(i,e) in enumerate(third) if kind(e['case'])=='simultaneous']
        modes={f['mode']:dict(d=f['d'],raw_d=f['raw_d'],distance_outside_interval=f['distance_outside_interval'],failed=[(x['case'],x['distance_to_threshold_V']) for x in f['failed_conditions']]) for f in failed if f['seed']==seed}
        detail[str(seed)]=dict(label=label,order_feasible=fi['order_feasible'],interval=fi['interval'],lower_bound=fi['lower_bound'],upper_bound=fi['upper_bound'],
            events_total=len(ev),events_final_third=len(third),simultaneous_final_third=sim,
            simultaneous_whole_history=sum(kind(e['case'])=='simultaneous' for e in ev),settings=modes)
    # regression targets for 2215
    d15=detail['2026112215']
    req=dict(simultaneous_lower=None,long_gap_upper=None)
    for r in by[2026112215]:
        if r['case']['id']=='pair_0.5_0.35_0.0':req['simultaneous_lower']=(-.06-r['u_V'])/r['v_V'] if r['v_V']>0 else (.06-r['u_V'])/r['v_V']
        if r['case']['id'] in('pair_0.5_0.5_0.6','pair_0.5_0.5_-0.6'):
            lo,hi=limits(r['case']);b=[(lo-r['u_V'])/r['v_V'],(hi-r['u_V'])/r['v_V']];req.setdefault('long_gap_bounds',{})[r['case']['id']]=sorted(b)
    checks['d2215_simultaneous_lower']=dict(value=d15['lower_bound']['value'],case=d15['lower_bound']['case'],expected=-.1621863170,matches=abs(d15['lower_bound']['value']+.1621863170)<5e-11)
    checks['d2215_long_gap_upper']=dict(value=d15['upper_bound']['value'],case=d15['upper_bound']['case'],expected=-.1944916109,matches=abs(d15['upper_bound']['value']+.1944916109)<5e-11)
    checks['d2215_requirements_by_case']=req
    checks['feasible_count']=sum(f['any_setting_suffices'] for f in feas)
    for name,obj in [('feasible_intervals',feas),('failed_conditions',failed),('detail_cases',detail),('validation_checks',checks)]:(OUT/f'{name}.json').write_text(json.dumps(obj,indent=2)+'\n')
    inputs={str(p.relative_to(ROOT)):sha(p) for p in [bpath,cpath,spath,dpath,Path(__file__).resolve()]};(OUT/'input_hashes.json').write_text(json.dumps(inputs,indent=2)+'\n')
    modes=sorted({s['mode'] for s in settings},key=lambda m:(m!='raw',float(m) if m!='raw' else 0))
    L=['# Task B — what "the two remaining failures" means','',
       'Order output under balance d is u + d·v (positive readout gain ×(1+d), negative ×(1−d)), d in [−1, 1]. All original strict inequalities; coincidence adequacy is required separately and is unaffected by d. Stored branch responses (D155) and D163 settings only; no new trajectories.','',
       f"**{checks['feasible_count']}/40 component draws have some constant setting that meets all 34 conditions.** Old-interval mismatches: {checks['old_interval_mismatch']}; old-feasibility mismatches: {checks['old_feasibility_mismatch']}.",'',
       '## All 40 draws: allowed interval and its active bounds','','| seed | allowed d | width | lower bound set by | upper bound set by | coincidence ok | |','|---|---|---|---|---|---|---|']
    for f in feas:
        lb,ub=f['lower_bound'],f['upper_bound']
        L.append(f"| {f['seed']} | ({f['interval'][0]:+.4f}, {f['interval'][1]:+.4f}) | {f['width']:+.4f} | {lb['case']} (v={lb['coefficient_V'] if lb['coefficient_V'] is None else format(lb['coefficient_V'],'+.4f')}, limit {lb['threshold_V']}) | {ub['case']} (v={ub['coefficient_V'] if ub['coefficient_V'] is None else format(ub['coefficient_V'],'+.4f')}, limit {ub['threshold_V']}) | {f['coincidence_all']} | {'**no setting exists**' if not f['any_setting_suffices'] else ''} |")
    L+=['','Bounds from conditions are strict (open); the knob limits ±1 are closed. A negative width means the conditions contradict.','',
        '## The 160 old 1000 s settings: which fail, and by how much','','| mode | draws passing | failing draws (failed conditions; distance to threshold, V) |','|---|---|---|']
    for m in modes:
        ff=[f for f in failed if f['mode']==m];bad=[f for f in ff if not f['all_pass']]
        L.append(f"| {m} | {len(ff)-len(bad)}/40 | "+'; '.join(f"{f['seed']}: "+', '.join(f"{x['case']} {x['distance_to_threshold_V']:+.4f}" for x in f['failed_conditions']) for f in bad)+' |')
    for seed,dd in detail.items():
        L+=['',f"## {seed} — {dd['label']}",'',f"Allowed d: ({dd['interval'][0]:+.10f}, {dd['interval'][1]:+.10f}); nonempty: {dd['order_feasible']}.",
            f"Lower bound from `{dd['lower_bound']['case']}` (u={dd['lower_bound']['u_V']}, v={dd['lower_bound']['coefficient_V']}, limit {dd['lower_bound']['threshold_V']} V); upper bound from `{dd['upper_bound']['case']}` (u={dd['upper_bound']['u_V']}, v={dd['upper_bound']['coefficient_V']}, limit {dd['upper_bound']['threshold_V']} V).",
            f"Events: {dd['events_total']} in 1000 s, {dd['events_final_third']} in the final third; simultaneous in the whole history {dd['simultaneous_whole_history']}, in the final third {len(dd['simultaneous_final_third'])}: "+'; '.join(f"#{x['index']} at {x['first_s']:.2f} s, A {x['a_V']} V, B {x['b_V']} V" for x in dd['simultaneous_final_third'])+'.','',
            '| mode | d | distance outside allowed interval | failed conditions (distance to threshold, V) |','|---|---|---|---|']
        for m in modes:
            x=dd['settings'][m];L.append(f"| {m} | {x['d']:+.6f} | {'n/a (no interval)' if x['distance_outside_interval'] is None else format(x['distance_outside_interval'],'.6f')} | "+', '.join(f"{c} {v:+.4f}" for c,v in x['failed'])+' |')
    L+=['','## Answer','',
        f"- **2026112215: no setting exists.** Its simultaneous (.5, .35) V case requires d > {checks['d2215_simultaneous_lower']['value']:.10f} (regression target −.1621863170: {checks['d2215_simultaneous_lower']['matches']}); its long-gap (.5, .5) V case requires d < {checks['d2215_long_gap_upper']['value']:.10f} (target −.1944916109: {checks['d2215_long_gap_upper']['matches']}). More evidence cannot create a constant setting meeting contradictory inequalities.",
        f"- **2026112227: a setting exists, but the available calculation selected one outside it.** Allowed ({detail['2026112227']['interval'][0]:+.4f}, {detail['2026112227']['interval'][1]:+.4f}); the baseline references chose d ≈ {detail['2026112227']['settings']['0.15']['d']:+.4f}, {detail['2026112227']['settings']['0.15']['distance_outside_interval']:.4f} outside. Why it was selected is Task C's question; nothing here explains it.",
        '- The other raw-mode failures are listed above; they are not part of "the two remaining failures", which refers to the three ideal baseline references.']
    (OUT/'failure_report.md').write_text('\n'.join(L)+'\n');print('\n'.join(L[:8]));print(json.dumps(checks,indent=1)[:1500]);print('\n'.join(L[-4:]))
if __name__=='__main__':main()

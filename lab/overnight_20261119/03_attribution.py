"""Task C (overnight 2026-11-19): attribute D163's final-third calibration integrals to recorded events.
Replays the observer's analytic feedforward equations for the existing 40 histories (no noise engine,
no rail fading). Temporal accounting of fixed trajectories, not causal event removal.
"""
import copy,hashlib,json,math,sys,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'lab'));sys.path.insert(0,str(ROOT))
from overnight_20261119_support import partition_integrals,score_branches,setting
from order_long_calibration import make_long_stream
from order_baseline_stream import stream_trajectory
from order_continuous_baseline import lowpass,TAUS
from units import V_TYP,TAU_MAX
V=ROOT/'lab/v';BASE=V/'overnight_20261119'
DT=.0005;DUR=1000.;START=2000/3;MODES=['raw']+[str(t) for t in TAUS];TOL=1e-9
COMPUTE_VERSION='C1'  # bump if the per-seed calculation changes, so stale checkpoints are not reused
CKPT=BASE/'attribution_checkpoints'
def fresh(name):
    for n in [name,name+'_retry1',name+'_retry2']:
        if not (BASE/n).exists():(BASE/n).mkdir();return BASE/n
    raise RuntimeError('No retry directory left')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sha_text(s):return hashlib.sha256(s.encode()).hexdigest()
def kind(c):
    if not(c['a']>0 and c['b']>0):return 'single'
    return 'simultaneous' if c['delay']==0 else ('near' if abs(c['delay'])<=.15 else 'far')

def observations(row,dt,duration):
    """Observer signals of D163 on one history: t, w, and per mode the A and B integrands."""
    t,v=stream_trajectory(row,.15,dt,duration);p=copy.deepcopy(row);p['elements'][0][6]=0.
    _,pv=stream_trajectory(p,.15,dt,duration);u=v[7].copy();sens=2*pv[7]-u;w=np.clip(v[6]/V_TYP,0,1);maxv=float(np.max(np.abs(v)))
    del v,pv
    initial=np.random.default_rng([row['seed'],157]).uniform(-.075,.075)
    f={'raw':(w*u,w*sens)}
    for tau in TAUS:f[str(tau)]=(w*(u-lowpass(u,tau,dt,initial)),w*(sens-lowpass(sens,tau,dt,0.)))
    return t,w,f,maxv

def per_seed(seed,row,saved_stream):
    r,events=make_long_stream(row,10.,2)
    if events!=saved_stream['events']:raise RuntimeError(f'{seed}: regenerated event list differs from D163')
    t,w,f,maxv=observations(r,DT,DUR)
    i0=int(np.searchsorted(t,START,side='left'));t0=float(t[i0]);assert t0>=START and t[i0-1]<START and t[-1]==DUR
    mask=slice(i0,None);integ=lambda a:float(np.sum((a[mask][:-1]+a[mask][1:])*.5)*DT)
    full={m:[integ(f[m][0]),integ(f[m][1])] for m in MODES};Wfull=integ(w)
    regress={m:dict(A=abs(full[m][0]-saved_stream['observations_Vs'][m][0]),B=abs(full[m][1]-saved_stream['observations_Vs'][m][1])) for m in MODES}
    inside=[(i,e) for i,e in enumerate(events) if t0<e['first_s']<DUR]
    edges=np.array([t0]+[e['first_s'] for _,e in inside]+[DUR])
    W=partition_integrals(t,w,edges);parts={m:(partition_integrals(t,f[m][0],edges),partition_integrals(t,f[m][1],edges)) for m in MODES}
    before=[i for i,e in enumerate(events) if e['first_s']<=t0]
    intervals=[]
    for k in range(len(edges)-1):
        if k==0:
            ev=events[before[-1]] if before else None
            item=dict(label='carry_in',event_id=None,preceding_event_id=before[-1] if before else None,preceding_case=ev['case']['id'] if ev else None)
            item.update(kind='carry_in',case=None,a_V=None,b_V=None,delay_s=None)
        else:
            i,e=inside[k-1];c=e['case']
            item=dict(label=f'event_{i}',event_id=i,preceding_event_id=None,preceding_case=None,kind=kind(c),case=c['id'],a_V=c['a'],b_V=c['b'],delay_s=c['delay'])
        item.update(start_s=float(edges[k]),end_s=float(edges[k+1]),duration_s=float(edges[k+1]-edges[k]),W_s=float(W[k]),
            A_Vs={m:float(parts[m][0][k]) for m in MODES},B_Vs={m:float(parts[m][1][k]) for m in MODES})
        intervals.append(item)
    sums={m:[float(sum(x['A_Vs'][m] for x in intervals)),float(sum(x['B_Vs'][m] for x in intervals))] for m in MODES}
    partition_err={m:max(abs(sums[m][0]-full[m][0]),abs(sums[m][1]-full[m][1])) for m in MODES}
    return dict(seed=seed,compute_version=COMPUTE_VERSION,integration_start_s=t0,maximum_state_abs_V=maxv,full_window_Vs=full,W_full_s=Wfull,
        regression_error_Vs=regress,partition_error_Vs=partition_err,intervals=intervals,
        events_total=len(events),events_in_window=len(inside),simultaneous_in_window=sum(kind(e['case'])=='simultaneous' for _,e in inside))

def aggregate(name,ints,m):
    A=float(sum(x['A_Vs'][m] for x in ints));B=float(sum(x['B_Vs'][m] for x in ints))
    s=setting(A,B);return dict(aggregate=name,mode=m,A_Vs=A,B_Vs=B,B_sign=int(np.sign(B)),intervals=[x['label'] for x in ints],**s)

def score(s,rows,interval):
    if not s['identifiable']:return dict(status='unidentifiable')
    sc=score_branches(rows,s['d']);lo,hi=interval
    return dict(status='scored',passed=sum(x['passed'] for x in sc),all_pass=all(x['passed'] for x in sc),failed=[x['case_id'] for x in sc if not x['passed']],inside_feasible=bool(lo<s['d']<hi))

def main():
    OUT=fresh('attribution_results');CKPT.mkdir(exist_ok=True);start=time.monotonic()
    assert TAUS[-1]==TAU_MAX
    src=ROOT/'lab/v/motifs/order_v2/confirm.jsonl';raw=[json.loads(l) for l in src.read_text().splitlines()]
    dt=min(r['dt'] for r in raw);seedrows={r['seed']:r for r in raw if r['dt']==dt and not r['control']}
    spath=V/'order_long_calibration/streams.json';streams={r['seed']:r for r in json.loads(spath.read_text())}
    dpath=V/'order_long_calibration/draws.json';old={(r['seed'],r['mode']):r for r in json.loads(dpath.read_text())}
    bpath=V/'order_balance_information/branches.json';branches={}
    for b in json.loads(bpath.read_text()):branches.setdefault(b['seed'],[]).append(b)
    fpath=BASE/'failures_results/feasible_intervals.json';feas={r['seed']:r for r in json.loads(fpath.read_text())}
    capath=V/'order_balance_information/draws.json';cap={r['seed']:r for r in json.loads(capath.read_text())}
    lpath=V/'order_local_calibration/observations.json';local={(r['seed'],r['case']['id']):r for r in json.loads(lpath.read_text())}
    assert len(seedrows)==40 and sorted(seedrows)==sorted(streams)
    results={};ckpt_log=[]
    for seed in sorted(seedrows):
        path=CKPT/f'{seed}.json';hpath=CKPT/f'{seed}.sha256';res=None
        if path.exists() and hpath.exists() and sha(path)==hpath.read_text().strip():
            cand=json.loads(path.read_text())
            if cand.get('compute_version')==COMPUTE_VERSION:res=cand;ckpt_log.append(dict(seed=seed,reused=True))
        if res is None:
            res=per_seed(seed,seedrows[seed],streams[seed])
            path.write_text(json.dumps(res)+'\n');hpath.write_text(sha(path)+'\n');ckpt_log.append(dict(seed=seed,reused=False,sha256=sha(path)))
        results[seed]=res
        print('seed',seed,'elapsed',round(time.monotonic()-start,1),'max regression',max(max(v.values()) for v in res['regression_error_Vs'].values()),flush=True)
    # validation gate
    checks=dict(max_regression_error_Vs=max(max(v.values()) for r in results.values() for v in r['regression_error_Vs'].values()),
        max_partition_error_Vs=max(max(r['partition_error_Vs'].values()) for r in results.values()),knob_regression={},checkpoints=ckpt_log)
    knob_err=0.;bad=[]
    for seed,r in results.items():
        for m in MODES:
            s=setting(*r['full_window_Vs'][m]);o=old[seed,m]
            if s['identifiable']:knob_err=max(knob_err,abs(s['d']-o['d']),abs(s['raw_d']-o['raw_d']))
            else:bad.append([seed,m,'unidentifiable'])
    checks['max_knob_regression']=knob_err
    valid=checks['max_regression_error_Vs']<=TOL and checks['max_partition_error_Vs']<=TOL and knob_err<=TOL and not bad
    checks['valid']=bool(valid);checks['problems']=bad
    (OUT/'attribution_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    with (OUT/'event_contributions.jsonl').open('x') as fh:
        for seed,r in results.items():
            for x in r['intervals']:fh.write(json.dumps(dict(seed=seed,**x))+'\n')
    if not valid:
        print('VALIDATION FAILED',json.dumps({k:v for k,v in checks.items() if k!='checkpoints'}),flush=True);raise SystemExit(2)
    # aggregates
    aggs=[];fh=(OUT/'aggregate_settings.jsonl').open('x')
    for seed,r in results.items():
        ints=r['intervals'];sim=[x for x in ints if x['kind']=='simultaneous'];other=[x for x in ints if x['kind']!='simultaneous'];rows=branches[seed];iv=feas[seed]['interval']
        for m in MODES:
            items=[aggregate('all',ints,m),aggregate('simultaneous_only',sim,m),aggregate('other_only',other,m)]
            for x in sim:items.append(dict(aggregate('leave_out_'+x['label'],[y for y in ints if y is not x],m),left_out=x['label']))
            for x in sim:
                k=ints.index(x);items.append(dict(aggregate('prefix_to_end_of_'+x['label'],ints[:k+1],m),prefix_end_s=x['end_s']))
            items.append(dict(aggregate='fallback_d0',mode=m,identifiable=True,raw_d=0.,d=0.,clipped=False,A_Vs=None,B_Vs=None,B_sign=None,intervals=[],label='original d=0 comparator, not calibrated'))
            for it in items:
                it.update(seed=seed,feasible_interval=iv,order_feasible=feas[seed]['order_feasible'],**score(it,rows,iv));aggs.append(it);fh.write(json.dumps(it)+'\n')
    fh.close()
    A={(a['seed'],a['mode'],a['aggregate']):a for a in aggs}
    # contamination: anchor-only acceptable, all-intervals not
    moved=[dict(seed=s,mode=m,anchor_d=A[s,m,'simultaneous_only']['d'],all_d=A[s,m,'all']['d'],interval=feas[s]['interval']) for s in results for m in MODES
           if A[s,m,'simultaneous_only'].get('all_pass') and A[s,m,'all'].get('status')=='scored' and not A[s,m,'all']['all_pass']]
    rescued=[dict(seed=s,mode=m) for s in results for m in MODES if A[s,m,'simultaneous_only'].get('status')=='scored' and not A[s,m,'simultaneous_only']['all_pass'] and A[s,m,'all'].get('all_pass')]
    # anchor cases for 2227 and others
    anchor={}
    for seed in [2026112227,2026112215,2026112200]:
        r=results[seed];sims=[x for x in r['intervals'] if x['kind']=='simultaneous'];rows={b['case']['id']:b for b in branches[seed]}
        cases={}
        for x in sims:
            cid=x['case'];lo=local[seed,cid];br=rows[cid]
            iso=setting(*lo['observations_Vs']['baseline_reference']);isoraw=setting(*lo['observations_Vs']['raw'])
            zero=-br['u_V']/br['v_V']
            cases[x['label']]=dict(case=cid,start_s=x['start_s'],duration_s=x['duration_s'],in_history={m:dict(A_Vs=x['A_Vs'][m],B_Vs=x['B_Vs'][m],**setting(x['A_Vs'][m],x['B_Vs'][m])) for m in MODES},
                d156_isolated_baseline_reference=dict(A_Vs=lo['observations_Vs']['baseline_reference'][0],B_Vs=lo['observations_Vs']['baseline_reference'][1],**iso),
                d156_isolated_raw=dict(**isoraw),branch_zero_output_d=zero,
                scores=dict(isolated_baseline_reference=score(iso,branches[seed],feas[seed]['interval']),branch_zero_output=score(setting(-zero,1.),branches[seed],feas[seed]['interval'])))
        ctx=dict(feasible_interval=feas[seed]['interval'],order_feasible=feas[seed]['order_feasible'],d155_four_simultaneous_reference=cap[seed]['settings']['simultaneous'],
            anchor_only={m:{k:A[seed,m,'simultaneous_only'][k] for k in ['A_Vs','B_Vs','raw_d','d','status','passed','all_pass','inside_feasible'] if k in A[seed,m,'simultaneous_only']} for m in MODES},
            other_only={m:{k:A[seed,m,'other_only'][k] for k in ['A_Vs','B_Vs','raw_d','d','status','passed','all_pass','inside_feasible'] if k in A[seed,m,'other_only']} for m in MODES},
            all={m:{k:A[seed,m,'all'][k] for k in ['A_Vs','B_Vs','raw_d','d','passed','all_pass','inside_feasible']} for m in MODES},
            carry_in={m:dict(A_Vs=r['intervals'][0]['A_Vs'][m],B_Vs=r['intervals'][0]['B_Vs'][m]) for m in MODES},
            largest_A_contributions={m:sorted(({k:x[k] for k in ['label','kind','case','start_s']}|dict(A_Vs=x['A_Vs'][m],B_Vs=x['B_Vs'][m]) for x in r['intervals']),key=lambda y:-abs(y['A_Vs']))[:8] for m in ['0.15','raw']},
            anchors=cases)
        anchor[str(seed)]=ctx
    (OUT/'anchor_cases.json').write_text(json.dumps(anchor,indent=2)+'\n')
    # plot: cumulative inferred d over the measured third for 2227 (and 2200, fixed comparison)
    svg=plot(results,feas)
    (OUT/'cumulative_d_2227.svg').write_text(svg)
    # summary table per seed/mode
    table=[]
    for seed in sorted(results):
        for m in MODES:
            a,s,o=A[seed,m,'all'],A[seed,m,'simultaneous_only'],A[seed,m,'other_only']
            table.append(dict(seed=seed,mode=m,sim_events=results[seed]['simultaneous_in_window'],interval=feas[seed]['interval'],order_feasible=feas[seed]['order_feasible'],
                all=(a['d'],a.get('all_pass')),anchor_only=(s.get('d'),s.get('all_pass'),s['status']),other_only=(o.get('d'),o.get('all_pass'),o['status'])))
    inputs={str(p.relative_to(ROOT)):sha(p) for p in [src,spath,dpath,bpath,fpath,capath,lpath,ROOT/'lab/order_long_calibration.py',ROOT/'lab/order_baseline_stream.py',ROOT/'lab/order_continuous_baseline.py',ROOT/'lab/population_trace_margin.py',ROOT/'lab/overnight_20261119_support.py',Path(__file__).resolve()]}
    summary=dict(elapsed_s=time.monotonic()-start,checks={k:v for k,v in checks.items() if k!='checkpoints'},anchor_only_acceptable_moved_out_by_other_intervals=moved,anchor_only_failed_but_all_passed=rescued,
        counts={m:dict(all_pass=sum(bool(A[s,m,'all'].get('all_pass')) for s in results),anchor_only_pass=sum(bool(A[s,m,'simultaneous_only'].get('all_pass')) for s in results),
            anchor_only_unidentifiable=sum(A[s,m,'simultaneous_only']['status']=='unidentifiable' for s in results),other_only_pass=sum(bool(A[s,m,'other_only'].get('all_pass')) for s in results),
            fallback_d0_pass=sum(bool(A[s,m,'fallback_d0'].get('all_pass')) for s in results)) for m in MODES},table=table,input_sha256=inputs)
    (OUT/'attribution_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:summary[k] for k in ['elapsed_s','checks','counts','anchor_only_acceptable_moved_out_by_other_intervals','anchor_only_failed_but_all_passed']},indent=1),flush=True)
    print(json.dumps(anchor['2026112227'],indent=1)[:6000])

def plot(results,feas):
    """Cumulative inferred d (from start of measured third) at each interval end; 2227 with 2200 for comparison."""
    W,H,ml,mr,mt,mb=900,520,70,170,40,50
    def X(t):return ml+(t-650)/(1000-650)*(W-ml-mr)
    def Y(d):return mt+(0.6-d)/(1.4)*(H-mt-mb)   # d range [-0.8, 0.6]
    styles={'raw':('#E69F00','2,3'),'0.15':('#0072B2',''),'1.0':('#009E73','8,4'),str(TAU_MAX):('#CC79A7','1,1')}
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="sans-serif" font-size="12">','<rect width="100%" height="100%" fill="white"/>',
         '<text x="70" y="22" font-size="14">2026112227: balance inferred from the measured third so far, against the allowed interval (grey band)</text>']
    lo,hi=feas[2026112227]['interval']
    out.append(f'<rect x="{ml}" y="{Y(hi):.1f}" width="{W-ml-mr}" height="{Y(lo)-Y(hi):.1f}" fill="#dddddd"/>')
    out.append(f'<text x="{W-mr+5}" y="{(Y(hi)+Y(lo))/2:.1f}">allowed d</text>')
    for d in [-0.8,-0.6,-0.4,-0.2,0,0.2,0.4,0.6]:
        out.append(f'<line x1="{ml}" x2="{W-mr}" y1="{Y(d):.1f}" y2="{Y(d):.1f}" stroke="#eeeeee"/><text x="{ml-8}" y="{Y(d)+4:.1f}" text-anchor="end">{d:+.1f}</text>')
    for t in range(700,1001,50):out.append(f'<text x="{X(t):.1f}" y="{H-mb+18}" text-anchor="middle">{t}</text>')
    out.append(f'<text x="{(ml+W-mr)/2}" y="{H-10}" text-anchor="middle">time (s)</text><text x="16" y="{H/2}" transform="rotate(-90 16 {H/2})" text-anchor="middle">inferred balance d (clipped to ±1)</text>')
    r=results[2026112227]
    for x in r['intervals']:
        if x['kind']=='simultaneous':
            out.append(f'<line x1="{X(x["start_s"]):.1f}" x2="{X(x["start_s"]):.1f}" y1="{mt}" y2="{H-mb}" stroke="black" stroke-dasharray="4,2"/><text x="{X(x["start_s"])+4:.1f}" y="{mt+12}">anchor {x["case"]}</text>')
    for k,(m,(col,dash)) in enumerate(styles.items()):
        A=B=0.;pts=[]
        for x in r['intervals']:
            A+=x['A_Vs'][m];B+=x['B_Vs'][m]
            if abs(B)>1e-12:pts.append((x['end_s'],float(np.clip(-A/B,-1,1))))
        if pts:
            path=' '.join(f'{X(t):.1f},{Y(max(-0.8,min(0.6,d))):.1f}' for t,d in pts)
            out.append(f'<polyline points="{path}" fill="none" stroke="{col}" stroke-width="2" stroke-dasharray="{dash}"/>')
            out.append(f'<line x1="{W-mr+5}" x2="{W-mr+35}" y1="{mt+60+k*20}" y2="{mt+60+k*20}" stroke="{col}" stroke-width="2" stroke-dasharray="{dash}"/><text x="{W-mr+40}" y="{mt+64+k*20}">{"raw" if m=="raw" else "tau "+format(float(m),".3g")+" s"}</text>')
    out.append(f'<text x="{ml}" y="{H-mb+34}" font-size="11">Each point: cumulative −A/B up to the end of an interval. Dashed vertical: simultaneous events (anchors). Fixed analytic trajectory; not an online learner.</text>')
    out.append('</svg>');return '\n'.join(out)

if __name__=='__main__':main()

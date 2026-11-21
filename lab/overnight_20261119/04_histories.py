"""Task D (overnight 2026-11-19): the fixed development schedules of matrix.json.
10 reused, deliberately selected component draws x 8 new schedules = 80 histories of 1000 s at 10 s mean pair spacing.
Observer settings from a fixed analytic trajectory (no noise, no rail fading), scored on old isolated cases.
Not in-life learning, not a closed-loop life, not a physical reliability test.
"""
import copy,hashlib,importlib.util,json,sys,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'lab'));sys.path.insert(0,str(ROOT))
from overnight_20261119_support import score_branches,setting
from order_bench import cases
from dynamic_parts_bench import CAP
from order_continuous_baseline import TAUS
from units import TAU_MAX
spec=importlib.util.spec_from_file_location('task_c',HERE/'03_attribution.py');task_c=importlib.util.module_from_spec(spec);spec.loader.exec_module(task_c)
observations=task_c.observations  # identical observation functions to Task C
V=ROOT/'lab/v';BASE=V/'overnight_20261119';CKPT=BASE/'histories_checkpoints';COMPUTE_VERSION='D1'
MATRIX=HERE/'matrix.json';M=json.loads(MATRIX.read_text())
MODES=M['observation_modes'];WINDOWS=M['observation_windows'];DT=M['quadrature_s'];FINE=M['refinement_s'];DUR=M['duration_s']
def fresh(name):
    for n in [name,name+'_retry1',name+'_retry2']:
        if not (BASE/n).exists():(BASE/n).mkdir();return BASE/n
    raise RuntimeError('No retry directory left')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sha_obj(o):return hashlib.sha256(json.dumps(o,sort_keys=True).encode()).hexdigest()
def kind(c):
    if not(c['a']>0 and c['b']>0):return 'single'
    return 'simultaneous' if c['delay']==0 else ('near' if abs(c['delay'])<=.15 else 'far')

def schedule(row,seed,rep,entropy=None):
    """make_long_stream with the matrix's RNG; every other detail copied."""
    rng=np.random.default_rng(entropy if entropy is not None else [seed,165,1,rep]);spacing=M['mean_pair_spacing_s'];cc=cases();weights=[]
    for c in cc:
        near=c['a'] and c['b'] and 0<abs(c['delay'])<=.15
        weights.append((1.6 if c['delay']>0 else .4) if near else 1.)
    prob=np.array(weights)/sum(weights);events=[];pulses=[];at=rng.uniform(0,spacing)
    while at<M['latest_allowed_first_s_exclusive']:
        c=cc[rng.choice(len(cc),p=prob)];events.append(dict(first_s=float(at),case=c))
        for node,amp,t0 in [(0,c['a'],at+max(-c['delay'],0)),(1,c['b'],at+max(c['delay'],0))]:
            if amp:pulses.append([float(t0),M['pulse_duration_s'],node,CAP*amp/.01])
        at+=rng.uniform(*M['renewal_interval_multiplier'])*spacing
    r=copy.deepcopy(row);r['pulses']=pulses
    return r,events

def window_indices(t,dt,name):
    first=lambda x:int(np.searchsorted(t,x,side='left'))   # first sample >= x
    last=lambda x:int(np.searchsorted(t,x,side='right'))-1  # last sample <= x
    i100=int(round(100/dt));iend=int(round(DUR/dt));assert abs(t[i100]-100)<1e-9 and abs(t[iend]-DUR)<1e-9 and iend==len(t)-1
    return {'first_100s_last_third':(first(200/3),i100),'full_100s':(0,i100),'last_third_1000s':(first(2000/3),iend),'full_1000s':(0,iend),
        'prefix_666.6666666666666s':(0,last(2000/3)),'prefix_833.3333333333334s':(0,last(2500/3))}[name]

def history(row,seed,rep,dt,branches):
    r,events=schedule(row,seed,rep);t,w,f,maxv=observations(r,dt,DUR);out=[]
    for name in WINDOWS:
        i,j=window_indices(t,dt,name);ts,te=float(t[i]),float(t[j])
        integ=lambda a:float(np.sum((a[i:j+1][:-1]+a[i:j+1][1:])*.5)*dt)
        inwin=[e for e in events if ts<=e['first_s']<=te];sims=[e for e in inwin if kind(e['case'])=='simultaneous']
        Wint=integ(w)
        for m in MODES:
            A,B=integ(f[m][0]),integ(f[m][1]);s=setting(A,B)
            rec=dict(seed=seed,replicate=rep,dt=dt,window=name,mode=m,window_start_s=ts,window_end_s=te,first_index=i,last_index=j,A_Vs=A,B_Vs=B,W_s=Wint,B_sign=int(np.sign(B)),**s,
                events_in_window=len(inwin),simultaneous_in_window=len(sims),distinct_simultaneous_cases=len({e['case']['id'] for e in sims}),simultaneous_cases=sorted({e['case']['id'] for e in sims}))
            if s['identifiable']:
                sc=score_branches(branches,s['d']);rec.update(status='scored',passed=sum(x['passed'] for x in sc),all_pass=all(x['passed'] for x in sc),failed=[x['case_id'] for x in sc if not x['passed']],case_results=sc)
            else:rec.update(status='unidentifiable',passed=None,all_pass=None,failed=None,case_results=None)
            out.append(rec)
    return dict(seed=seed,replicate=rep,dt=dt,compute_version=COMPUTE_VERSION,events=events,schedule_sha256=sha_obj(events),pulses_sha256=sha_obj(r['pulses']),maximum_state_abs_V=maxv,records=out)

def main():
    OUT=fresh('histories_results');CKPT.mkdir(exist_ok=True);start=time.monotonic()
    assert float(M['baseline_taus_s'][-1])==TAU_MAX and [float(x) for x in M['baseline_taus_s']]==[float(x) for x in TAUS] and MODES==['raw']+[str(x) for x in TAUS]
    src=ROOT/'lab/v/motifs/order_v2/confirm.jsonl';raw=[json.loads(l) for l in src.read_text().splitlines()]
    dtmin=min(r['dt'] for r in raw);seedrows={r['seed']:r for r in raw if r['dt']==dtmin and not r['control']}
    bpath=V/'order_balance_information/branches.json';branches={}
    for b in json.loads(bpath.read_text()):branches.setdefault(b['seed'],[]).append(b)
    fpath=BASE/'failures_results/feasible_intervals.json';feas={r['seed']:r for r in json.loads(fpath.read_text())}
    seeds=M['existing_component_seeds'];reps=M['new_schedule_replicates'];assert len(seeds)*len(reps)==M['max_new_histories']==80
    # 0. the generator copy reproduces D163's schedules exactly when given D163's RNG
    old={r['seed']:r for r in json.loads((V/'order_long_calibration/streams.json').read_text())}
    for seed in seeds:
        r,ev=schedule(seedrows[seed],seed,None,entropy=[seed,158,2]);assert ev==old[seed]['events'],seed
    print('generator copy reproduces D163 schedules for all 10 seeds',flush=True)
    # 1. numerical validation on the two declared refinement histories
    coarse={};ref=[];mism=[]
    for seed,rep in M['refinement_histories']:
        a=history(seedrows[seed],seed,rep,DT,branches[seed]);b=history(seedrows[seed],seed,rep,FINE,branches[seed]);coarse[seed,rep]=a
        if a['schedule_sha256']!=b['schedule_sha256']:mism.append(dict(seed=seed,rep=rep,problem='schedule differs between steps'))
        for x,y in zip(a['records'],b['records']):
            assert (x['window'],x['mode'])==(y['window'],y['mode'])
            item=dict(seed=seed,replicate=rep,window=x['window'],mode=x['mode'],identifiable=[x['identifiable'],y['identifiable']],B_sign=[x['B_sign'],y['B_sign']],
                d=[x['d'],y['d']],d_change=None if not(x['identifiable'] and y['identifiable']) else abs(x['d']-y['d']),
                classifications_identical=(x['case_results'] is None and y['case_results'] is None) or (x['case_results'] is not None and y['case_results'] is not None and [c['passed'] for c in x['case_results']]==[c['passed'] for c in y['case_results']]),
                A_change_Vs=abs(x['A_Vs']-y['A_Vs']),B_change_Vs=abs(x['B_Vs']-y['B_Vs']),window_bounds=[[x['window_start_s'],x['window_end_s']],[y['window_start_s'],y['window_end_s']]])
            ok=item['identifiable'][0]==item['identifiable'][1] and item['B_sign'][0]==item['B_sign'][1] and item['classifications_identical'] and (item['d_change'] is None or item['d_change']<M['numerical_knob_tolerance'])
            item['ok']=bool(ok);ref.append(item)
            if not ok:mism.append(item)
        print('refinement',seed,rep,'elapsed',round(time.monotonic()-start,1),flush=True)
    refc=dict(passed=not mism,tolerance=M['numerical_knob_tolerance'],max_d_change=max((r['d_change'] for r in ref if r['d_change'] is not None),default=None),
        max_A_change_Vs=max(r['A_change_Vs'] for r in ref),max_B_change_Vs=max(r['B_change_Vs'] for r in ref),mismatches=mism,checks=ref)
    (OUT/'refinement_checks.json').write_text(json.dumps(refc,indent=2)+'\n')
    if mism:
        print('REFINEMENT FAILED: full batch blocked',len(mism),flush=True);raise SystemExit(3)
    # 2. full batch, checkpointed
    hist={};ckpt=[]
    for seed in seeds:
        for rep in reps:
            path=CKPT/f'{seed}_{rep}.json';hp=CKPT/f'{seed}_{rep}.sha256';h=None
            if path.exists() and hp.exists() and sha(path)==hp.read_text().strip():
                cand=json.loads(path.read_text())
                if cand.get('compute_version')==COMPUTE_VERSION and cand['dt']==DT:h=cand;ckpt.append(dict(key=[seed,rep],reused=True))
            if h is None:
                h=coarse.get((seed,rep)) or history(seedrows[seed],seed,rep,DT,branches[seed])
                path.write_text(json.dumps(h)+'\n');hp.write_text(sha(path)+'\n');ckpt.append(dict(key=[seed,rep],reused=False,sha256=sha(path)))
            hist[seed,rep]=h
            el=time.monotonic()-start;print('history',seed,rep,'elapsed',round(el,1),flush=True)
            if el>M['new_history_job_wall_limit_s']-60:raise RuntimeError('Approaching job limit; stopping with checkpoints kept')
    # 3. outputs
    recs=[r for h in hist.values() for r in h['records']];assert len(recs)==80*len(MODES)*len(WINDOWS)==1920
    with (OUT/'settings.jsonl').open('x') as fs,(OUT/'case_scores.jsonl').open('x') as fc:
        for r in recs:
            fs.write(json.dumps({k:v for k,v in r.items() if k!='case_results'})+'\n')
            fc.write(json.dumps(dict(seed=r['seed'],replicate=r['replicate'],window=r['window'],mode=r['mode'],d=r['d'],status=r['status'],cases=r['case_results']))+'\n')
    sched={f'{s}_{r}':dict(schedule_sha256=h['schedule_sha256'],pulses_sha256=h['pulses_sha256'],events=h['events']) for (s,r),h in hist.items()}
    (OUT/'schedules.json').write_text(json.dumps(sched)+'\n')
    def tally(rr):
        sc=[r for r in rr if r['status']=='scored']
        return dict(n=len(rr),scored=len(sc),unidentifiable=len(rr)-len(sc),all_pass=sum(r['all_pass'] for r in sc),clipped=sum(bool(r['clipped']) for r in sc),nonpositive_B=sum(r['B_Vs']<=0 for r in rr),
            inside_feasible=sum(bool(feas[r['seed']]['order_feasible'] and feas[r['seed']]['interval'][0]<r['d']<feas[r['seed']]['interval'][1]) for r in sc))
    summ=dict(by_mode_window={f'{m}|{w}':tally([r for r in recs if r['mode']==m and r['window']==w]) for m in MODES for w in WINDOWS},
        by_seed_mode_window={f'{s}|{m}|{w}':tally([r for r in recs if r['seed']==s and r['mode']==m and r['window']==w]) for s in seeds for m in MODES for w in WINDOWS},
        by_evidence={f'{m}|{w}|{k}':tally([r for r in recs if r['mode']==m and r['window']==w and min(r['simultaneous_in_window'],2)==k]) for m in MODES for w in WINDOWS for k in [0,1,2]},
        by_distinct_cases={f'{m}|{w}|{k}':tally([r for r in recs if r['mode']==m and r['window']==w and r['distinct_simultaneous_cases']==k]) for m in MODES for w in WINDOWS for k in range(5)},
        evidence_counts={w:dict(zero_simultaneous=sum(1 for h in hist.values() for r in h['records'] if r['window']==w and r['mode']=='raw' and r['simultaneous_in_window']==0),
            mean_simultaneous=float(np.mean([r['simultaneous_in_window'] for h in hist.values() for r in h['records'] if r['window']==w and r['mode']=='raw'])),
            mean_events=float(np.mean([r['events_in_window'] for h in hist.values() for r in h['records'] if r['window']==w and r['mode']=='raw']))) for w in WINDOWS},
        refinement=dict(passed=refc['passed'],max_d_change=refc['max_d_change']),elapsed_s=time.monotonic()-start,histories=len(hist),expected_histories=80,settings=len(recs),expected_settings=1920,
        maximum_state_abs_V=max(h['maximum_state_abs_V'] for h in hist.values()),checkpoints=ckpt,
        input_sha256={str(p.relative_to(ROOT)):sha(p) for p in [src,bpath,fpath,MATRIX,HERE/'03_attribution.py',ROOT/'lab/order_baseline_stream.py',ROOT/'lab/order_continuous_baseline.py',ROOT/'lab/order_bench.py',ROOT/'lab/overnight_20261119_support.py',Path(__file__).resolve()]})
    (OUT/'history_summary.json').write_text(json.dumps(summ,indent=2)+'\n')
    L=['# Task D — fixed development schedules','',f"Histories {len(hist)}/80, settings {len(recs)}/1920; elapsed {summ['elapsed_s']:.1f} s; refinement passed (max knob change {refc['max_d_change']:.3g}).",
       'Ten reused, deliberately selected component draws (the two failures and the lowest eight labels) × eight new schedules. Not a population sample; not fresh components; not new event families. Observer settings computed from a fixed trajectory and scored on isolated old cases; not closed-loop lives or online learning.','',
       '## Draws whose every old case passes (of 80 histories), by observation mode and window','','| window | '+' | '.join(MODES)+' |','|---|'+'---|'*len(MODES)]
    for w in WINDOWS:L.append(f'| {w} | '+' | '.join(f"{summ['by_mode_window'][f'{m}|{w}']['all_pass']}/80"+(f" ({summ['by_mode_window'][f'{m}|{w}']['unidentifiable']} unid.)" if summ['by_mode_window'][f'{m}|{w}']['unidentifiable'] else '') for m in MODES)+' |')
    L+=['','## By component seed (all-pass count of 8 schedules), tau 0.15 s','','| seed | '+' | '.join(WINDOWS)+' |','|---|'+'---|'*len(WINDOWS)]
    for s in seeds:L.append(f'| {s} | '+' | '.join(f"{summ['by_seed_mode_window'][f'{s}|0.15|{w}']['all_pass']}/8" for w in WINDOWS)+' |')
    L+=['','## By evidence (simultaneous events in the window: 0, 1, 2+), tau 0.15 s','','| window | 0 | 1 | 2+ |','|---|---|---|---|']
    for w in WINDOWS:L.append(f'| {w} | '+' | '.join(f"{summ['by_evidence'][f'0.15|{w}|{k}']['all_pass']}/{summ['by_evidence'][f'0.15|{w}|{k}']['n']}" for k in [0,1,2])+' |')
    L+=['','Every setting, failed case and denominator is in `settings.jsonl` / `case_scores.jsonl`; full tables by seed, mode, window and evidence in `history_summary.json`.']
    (OUT/'history_report.md').write_text('\n'.join(L)+'\n');print('\n'.join(L),flush=True)
if __name__=='__main__':main()

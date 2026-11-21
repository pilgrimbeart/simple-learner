"""D167 task 1, part B: two observer weights on the unchanged 40 D163 schedules.
Regenerates only D163's schedules (make_long_stream(row,10,2)); unchanged analytic trajectories at 0.5 ms,
original random baseline starts. Observer weights, each read only from the coincidence voltage:
  'w'  = clip(V_coincidence/V_TYP,0,1)   (original; final third checked against D163)
  'w2' = w*w                              (exploratory reference, not a selected mechanism)
Same A/B integrands before weighting (raw, three baseline taus). Windows: full 0-1000 s and the final third.
Event-category attribution (simultaneous, positive-near, negative-near, far, single, carry-in) uses analyst
labels for accounting only; no rule reads them. Then one informed intervention (2026112227 with all its
non-simultaneous pulses removed) and refinement of 2200/2227 at 0.25 ms. Rows streamed to JSONL.
Branch derivative (positive-path decomposition) and ideal baselines remain privileged reference operations.
"""
import copy,json,sys,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'lab'));sys.path.insert(0,str(ROOT))
from overnight_20261119_support import partition_integrals,score_branches,setting
from order_long_calibration import make_long_stream
from order_baseline_stream import stream_trajectory
from order_continuous_baseline import lowpass,TAUS
from dynamic_parts_bench import CAP
from units import V_TYP
V=ROOT/'lab/v';OUT=V/'calibration_next_20261120/t1b'
DT=.0005;FINE=.00025;DUR=1000.;START=2000/3;MODES=['raw']+[str(t) for t in TAUS];WEIGHTS=['w','w2'];BUDGET=900.
CATS=['simultaneous','positive_near','negative_near','far','single','carry_in']
def category(c):
    if not(c['a']>0 and c['b']>0):return 'single'
    if c['delay']==0:return 'simultaneous'
    if abs(c['delay'])<=.15:return 'positive_near' if c['delay']>0 else 'negative_near'
    return 'far'
def pulses_of(events):
    out=[]
    for e in events:
        c=e['case'];at=e['first_s']
        for node,amp,t0 in [(0,c['a'],at+max(-c['delay'],0)),(1,c['b'],at+max(c['delay'],0))]:
            if amp:out.append([float(t0),.04,node,CAP*amp/.01])
    return out

def signals(row,dt):
    """u, branch derivative, coincidence weight w, and baseline-subtracted integrands per mode (unweighted)."""
    t,v=stream_trajectory(row,.15,dt,DUR);p=copy.deepcopy(row);p['elements'][0][6]=0.
    _,pv=stream_trajectory(p,.15,dt,DUR);u=v[7].copy();der=2*pv[7]-u;w=np.clip(v[6]/V_TYP,0,1);maxv=float(np.max(np.abs(v)))
    del v,pv
    initial=np.random.default_rng([row['seed'],157]).uniform(-.075,.075)
    f={'raw':(u,der)}
    for tau in TAUS:f[str(tau)]=(u-lowpass(u,tau,dt,initial),der-lowpass(der,tau,dt,0.))
    return t,w,f,maxv

def history(row,events,dt,branches,label,partition=True):
    """Window totals (trapezoid as D163) and per-interval category contributions, both weights."""
    t,w,f,maxv=signals(row,dt);i0=int(np.searchsorted(t,START,side='left'));t0=float(t[i0]);assert t[-1]==DUR
    wins={'full_1000s':slice(0,None),'final_third_1000s':slice(i0,None)}
    trap=lambda a,s:float(np.sum((a[s][:-1]+a[s][1:])*.5)*dt)
    om={'w':w,'w2':w*w};recs=[]
    starts=[e['first_s'] for e in events if 0<e['first_s']<DUR]
    edges=np.array(sorted(set([0.,t0,DUR]+starts)))
    # label each partition interval with the event in force at its start (analyst accounting only)
    labels=[];evs=sorted(events,key=lambda e:e['first_s'])
    for k in range(len(edges)-1):
        a=edges[k];prev=[e for e in evs if e['first_s']<=a]
        labels.append(dict(start_s=float(a),end_s=float(edges[k+1]),case=prev[-1]['case']['id'] if prev else None,cat=category(prev[-1]['case']) if prev else 'carry_in',in_final_third=bool(a>=t0)))
    for name,o in om.items():
        Wp=partition_integrals(t,o,edges) if partition else None;W2p=partition_integrals(t,o*o,edges) if partition else None
        parts={m:(partition_integrals(t,o*f[m][0],edges),partition_integrals(t,o*f[m][1],edges)) if partition else None for m in MODES}
        for win,s in wins.items():
            Wt=trap(o,s);W2t=trap(o*o,s)
            sel=[k for k,l in enumerate(labels) if (win=='full_1000s' or l['in_final_third'])]
            for m in MODES:
                A=trap(o*f[m][0],s);B=trap(o*f[m][1],s);st=setting(A,B)
                rec=dict(history=label,seed=row['seed'],dt=dt,weight=name,window=win,mode=m,window_start_s=float(t[s][0]),A_Vs=A,B_Vs=B,W_s=Wt,W2_s=W2t,**st)
                if st['identifiable']:
                    sc=score_branches(branches,st['d']);rec.update(passed=sum(x['passed'] for x in sc),all_pass=all(x['passed'] for x in sc),case_pass=[x['passed'] for x in sc],case_ids=[x['case_id'] for x in sc])
                if partition:
                    cat={c:dict(A_Vs=0.,B_Vs=0.,W_s=0.,W2_s=0.,n=0) for c in CATS}
                    for k in sel:
                        c='carry_in' if (win=='final_third_1000s' and labels[k]['start_s']==t0) else labels[k]['cat']
                        cat[c]['A_Vs']+=float(parts[m][0][k]);cat[c]['B_Vs']+=float(parts[m][1][k]);cat[c]['W_s']+=float(Wp[k]);cat[c]['W2_s']+=float(W2p[k]);cat[c]['n']+=1
                    rec['categories']=cat;rec['partition_error_Vs']=max(abs(sum(v['A_Vs'] for v in cat.values())-A),abs(sum(v['B_Vs'] for v in cat.values())-B),abs(sum(v['W_s'] for v in cat.values())-Wt))
                recs.append(rec)
    extra=None
    if partition and row['seed']==2026112227:
        # per-interval anchor rows for the intervention comparison (2227 only, caller decides)
        extra=dict(edges=edges,labels=labels,t0=t0)
        extra['interval_values']={name:{m:(partition_integrals(t,om[name]*f[m][0],edges),partition_integrals(t,om[name]*f[m][1],edges)) for m in MODES}|{'W':partition_integrals(t,om[name],edges)} for name in om}
    return recs,maxv,extra

def main():
    OUT.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    src=V/'motifs/order_v2/confirm.jsonl';raw=[json.loads(l) for l in src.read_text().splitlines()]
    dtmin=min(r['dt'] for r in raw);seedrows={r['seed']:r for r in raw if r['dt']==dtmin and not r['control']}
    d163={r['seed']:r for r in json.loads((V/'order_long_calibration/streams.json').read_text())}
    d163draws={(r['seed'],r['mode']):r for r in json.loads((V/'order_long_calibration/draws.json').read_text())}
    branches={}
    for b in json.loads((V/'order_balance_information/branches.json').read_text()):branches.setdefault(b['seed'],[]).append(b)
    assert len(seedrows)==40
    fh=(OUT/'records.jsonl').open('x');check=dict(max_d163_A_B_error_Vs=0.,max_d163_knob_error=0.,max_partition_error_Vs=0.,schedules_identical=True,pulses_rebuilt=True)
    status=dict(completed_seeds=[],stopped=None)
    keep={}
    for seed in sorted(seedrows):
        r,events=make_long_stream(seedrows[seed],10.,2)
        if events!=d163[seed]['events']:check['schedules_identical']=False;raise RuntimeError(f'{seed} schedule differs')
        if pulses_of(events)!=r['pulses']:check['pulses_rebuilt']=False;raise RuntimeError(f'{seed} pulse rebuild differs')
        recs,maxv,extra=history(r,events,DT,branches[seed],f'{seed}')
        for x in recs:
            check['max_partition_error_Vs']=max(check['max_partition_error_Vs'],x['partition_error_Vs'])
            if x['weight']=='w' and x['window']=='final_third_1000s':
                oa,ob=d163[seed]['observations_Vs'][x['mode']];check['max_d163_A_B_error_Vs']=max(check['max_d163_A_B_error_Vs'],abs(x['A_Vs']-oa),abs(x['B_Vs']-ob))
                check['max_d163_knob_error']=max(check['max_d163_knob_error'],abs(x['d']-d163draws[seed,x['mode']]['d']))
            fh.write(json.dumps(x)+'\n')
        fh.flush()
        if seed==2026112227:keep['orig']=(events,extra)
        status['completed_seeds'].append(seed);el=time.monotonic()-start;print('seed',seed,'elapsed',round(el,1),'maxV',round(maxv,3),flush=True)
        if el>BUDGET-150:status['stopped']=f'budget guard after {seed}';break
    fh.close()
    (OUT/'checks.json').write_text(json.dumps(check,indent=2)+'\n')
    # informed intervention: 2227 with all non-simultaneous pulses removed; same initial state and remaining pulse times
    if status['stopped'] is None:
        seed=2026112227;events,extra=keep['orig'];r,_=make_long_stream(seedrows[seed],10.,2)
        kept=[e for e in events if category(e['case'])=='simultaneous'];ri=copy.deepcopy(r);ri['pulses']=pulses_of(kept)
        assert all(p in r['pulses'] for p in ri['pulses'])
        t,w,f,maxv=signals(ri,DT);om={'w':w,'w2':w*w};edges=extra['edges']
        rows=[]
        for k,l in enumerate(extra['labels']):
            if l['cat']!='simultaneous':continue
            for name in WEIGHTS:
                Wi=float(partition_integrals(t,om[name],edges)[k])
                for m in MODES:
                    Ai=float(partition_integrals(t,om[name]*f[m][0],edges)[k]);Bi=float(partition_integrals(t,om[name]*f[m][1],edges)[k])
                    Ao=float(extra['interval_values'][name][m][0][k]);Bo=float(extra['interval_values'][name][m][1][k]);Wo=float(extra['interval_values'][name]['W'][k])
                    rows.append(dict(seed=seed,interval_start_s=l['start_s'],interval_end_s=l['end_s'],case=l['case'],in_final_third=l['in_final_third'],weight=name,mode=m,
                        original=dict(A_Vs=Ao,B_Vs=Bo,W_s=Wo,**setting(Ao,Bo)),removed_nonsimultaneous=dict(A_Vs=Ai,B_Vs=Bi,W_s=Wi,**setting(Ai,Bi))))
        del t,w,f
        recs,_,_=history(ri,kept,DT,branches[seed],'2227_intervention',partition=False)
        (OUT/'intervention.json').write_text(json.dumps(dict(description='2026112227 with all non-simultaneous pulses removed; initial state and remaining pulse times preserved; informed reference, not a local selector',
            kept_events=len(kept),removed_events=len(events)-len(kept),anchor_intervals=rows,window_records=recs),indent=1)+'\n')
        print('intervention done',round(time.monotonic()-start,1),flush=True)
    # refinement at 0.25 ms
    ref=[]
    if status['stopped'] is None:
        coarse={}
        for line in (OUT/'records.jsonl').read_text().splitlines():
            x=json.loads(line)
            if x['seed'] in (2026112200,2026112227):coarse[x['seed'],x['weight'],x['window'],x['mode']]=x
        for seed in (2026112200,2026112227):
            if time.monotonic()-start>BUDGET-60:status['stopped']='budget guard before refinement';break
            r,events=make_long_stream(seedrows[seed],10.,2);recs,_,_=history(r,events,FINE,branches[seed],f'{seed}_fine',partition=False)
            for y in recs:
                x=coarse[seed,y['weight'],y['window'],y['mode']]
                ref.append(dict(seed=seed,weight=y['weight'],window=y['window'],mode=y['mode'],d=[x['d'],y['d']],d_change=abs(x['d']-y['d']),classifications_identical=x['case_pass']==y['case_pass'],
                    ok=bool(abs(x['d']-y['d'])<.001 and x['case_pass']==y['case_pass'])))
            print('refined',seed,round(time.monotonic()-start,1),flush=True)
    status['refinement']=dict(rows=len(ref),all_ok=bool(ref) and all(r['ok'] for r in ref),max_d_change=max((r['d_change'] for r in ref),default=None))
    (OUT/'refinement.json').write_text(json.dumps(ref,indent=1)+'\n')
    status['elapsed_s']=time.monotonic()-start;status['checks']=check
    (OUT/'status.json').write_text(json.dumps(status,indent=2)+'\n');print(json.dumps(status,indent=1))
if __name__=='__main__':main()

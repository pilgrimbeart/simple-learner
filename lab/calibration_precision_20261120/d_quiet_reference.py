"""D168 Task D (run part): quiet-period self-reference on the same observation.

Regenerates only the 40 D163 schedules with D167's unchanged signal functions (t1b_weights.signals, imported,
not edited): analytic trajectories at 0.5 ms, original random baseline starts, four modes (raw, three baselines).
For each observer weight o in {w, w*w} and quiet weight q = 1 - o (read only from the coincidence voltage;
no threshold, labels or future samples), windows full 0-1000 s and final third, accumulate
  W=int o, Q=int q, A=int o*r, B=int o*der, Aq=int q*r, Bq=int q*der   (trapezoid exactly as D167)
and the self-referenced observation A* = A - (W/Q) Aq, B* = B - (W/Q) Bq, setting d* = -A*/B* (clipped).
A shared readout error e adds e*W to A and e*Q to Aq, so cancels exactly in A*.
Gate: o-weighted A, B, W match D167's 640 records within 1e-12; refinement of 2026112200 and 2026112227 at
0.25 ms changes every knob (D167's and the self-referenced) by <.001 with identical classifications.
Only per-window totals are kept; no whole-life arrays are saved.
"""
import json,sys,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
for p in [ROOT,ROOT/'lab',ROOT/'lab/calibration_next_20261120']:sys.path.insert(0,str(p))
from t1b_weights import signals,MODES,DT,FINE,START,DUR
from order_long_calibration import make_long_stream
from overnight_20261119_support import score_branches,setting
V=ROOT/'lab/v';OUT=V/'calibration_precision_20261120/d';BUDGET=900.
def totals(row,dt):
    t,w,f,maxv=signals(row,dt);i0=int(np.searchsorted(t,START,side='left'));assert t[-1]==DUR
    trap=lambda a,s:float(np.sum((a[s][:-1]+a[s][1:])*.5)*dt)
    out={}
    for name,o in (('w',w),('w2',w*w)):
        q=1.-o
        for win,s in (('full_1000s',slice(0,None)),('final_third_1000s',slice(i0,None))):
            W,Q=trap(o,s),trap(q,s)
            for m in MODES:
                out[name,win,m]=dict(W_s=W,Q_s=Q,A_Vs=trap(o*f[m][0],s),B_Vs=trap(o*f[m][1],s),Aq_Vs=trap(q*f[m][0],s),Bq_Vs=trap(q*f[m][1],s))
    return out,maxv
def scored(x,branches):
    k=x['W_s']/x['Q_s'];As,Bs=x['A_Vs']-k*x['Aq_Vs'],x['B_Vs']-k*x['Bq_Vs']
    st=setting(As,Bs);x.update(A_star_Vs=As,B_star_Vs=Bs,ratio_W_Q=k,star=st)
    if st['identifiable']:
        sc=score_branches(branches,st['d']);x.update(star_passed=sum(y['passed'] for y in sc),star_all_pass=all(y['passed'] for y in sc),star_case_pass=[y['passed'] for y in sc])
    return x
def main():
    OUT.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    raw=[json.loads(l) for l in (V/'motifs/order_v2/confirm.jsonl').read_text().splitlines()]
    dtmin=min(r['dt'] for r in raw);seedrows={r['seed']:r for r in raw if r['dt']==dtmin and not r['control']};assert len(seedrows)==40
    d163={r['seed']:r for r in json.loads((V/'order_long_calibration/streams.json').read_text())}
    branches={}
    for b in json.loads((V/'order_balance_information/branches.json').read_text()):branches.setdefault(b['seed'],[]).append(b)
    d167={}
    for l in (V/'calibration_next_20261120/t1b/records.jsonl').read_text().splitlines():
        x=json.loads(l);d167[x['seed'],x['weight'],x['window'],x['mode']]=x
    check=dict(max_A_B_W_error=0.,schedules_identical=True);status=dict(completed=[],stopped=None)
    fh=(OUT/'records.jsonl').open('x')
    for seed in sorted(seedrows):
        r,events=make_long_stream(seedrows[seed],10.,2)
        if events!=d163[seed]['events']:check['schedules_identical']=False;raise RuntimeError(f'{seed} schedule differs')
        tot,maxv=totals(r,DT)
        for (name,win,m),x in tot.items():
            o=d167[seed,name,win,m]
            check['max_A_B_W_error']=max(check['max_A_B_W_error'],abs(x['A_Vs']-o['A_Vs']),abs(x['B_Vs']-o['B_Vs']),abs(x['W_s']-o['W_s']))
            x=scored(dict(seed=seed,dt=DT,weight=name,window=win,mode=m,**x),branches[seed])
            x.update(d167_d=o['d'],d167_all_pass=o['all_pass'],d167_passed=o['passed'],d167_case_pass=o['case_pass'])
            fh.write(json.dumps(x)+'\n')
        fh.flush();status['completed'].append(seed);el=time.monotonic()-start
        print('seed',seed,'elapsed',round(el,1),'maxV',round(maxv,3),'maxerr',check['max_A_B_W_error'],flush=True)
        if el>BUDGET-120:status['stopped']=f'budget guard after {seed}';break
    fh.close()
    ref=[]
    if status['stopped'] is None:
        coarse={}
        for l in (OUT/'records.jsonl').read_text().splitlines():
            x=json.loads(l)
            if x['seed'] in (2026112200,2026112227):coarse[x['seed'],x['weight'],x['window'],x['mode']]=x
        for seed in (2026112200,2026112227):
            if time.monotonic()-start>BUDGET-60:status['stopped']='budget guard before refinement';break
            r,_=make_long_stream(seedrows[seed],10.,2);tot,_=totals(r,FINE)
            for (name,win,m),y in tot.items():
                c=coarse[seed,name,win,m];y=scored(dict(**y),branches[seed])
                st0=setting(c['A_Vs'],c['B_Vs']);st1=setting(y['A_Vs'],y['B_Vs'])
                p0=[z['passed'] for z in score_branches(branches[seed],st0['d'])];p1=[z['passed'] for z in score_branches(branches[seed],st1['d'])]
                ref.append(dict(seed=seed,weight=name,window=win,mode=m,d=[st0['d'],st1['d']],d_star=[c['star']['d'],y['star']['d']],
                    d_change=abs(st0['d']-st1['d']),d_star_change=abs(c['star']['d']-y['star']['d']),
                    classifications_identical=bool(p0==p1 and c['star_case_pass']==y['star_case_pass'])))
            print('refined',seed,round(time.monotonic()-start,1),flush=True)
    status['refinement']=dict(rows=len(ref),max_d_change=max((x['d_change'] for x in ref),default=None),max_d_star_change=max((x['d_star_change'] for x in ref),default=None),
        all_ok=bool(ref) and all(x['d_change']<.001 and x['d_star_change']<.001 and x['classifications_identical'] for x in ref))
    check['gate_A_B_W']=bool(check['max_A_B_W_error']<1e-12)
    status.update(checks=check,elapsed_s=time.monotonic()-start,gate_passed=bool(check['gate_A_B_W'] and check['schedules_identical'] and status['refinement']['all_ok'] and status['stopped'] is None))
    (OUT/'refinement.json').write_text(json.dumps(ref,indent=1)+'\n');(OUT/'status.json').write_text(json.dumps(status,indent=2)+'\n')
    print(json.dumps(status,indent=1))
if __name__=='__main__':main()

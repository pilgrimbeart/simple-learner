"""D167 task 2: does retaining evidence survive one fixed readout error? Saved rows only, no trajectories.
For each of D165's 1920 settings (80 histories x 4 modes x 6 windows), the exact region of a persistent detector
error e (volts) with d(e)=clip((e*W-A)/B,-1,1) satisfying every original case (strict), and the conditional
success P = Gaussian mass of that region for e~N(0,(MISMATCH*V_TYP)^2). One e per detector/life, shared
across windows: paired comparisons use the same e (interval algebra, exact Gaussian integration).
Assumption kept from D164: e independent of existing component offsets. Infeasible draw 2215: P=0.
First reproduces D164's 240 rows exactly.
"""
import json,math,sys
from pathlib import Path
from statistics import NormalDist
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'lab'));sys.path.insert(0,str(ROOT))
from units import MISMATCH,V_TYP
from order_continuous_baseline import TAUS
from order_balance_information import bounds
V=ROOT/'lab/v';OUT=V/'calibration_next_20261120/t2';SIG=MISMATCH*V_TYP;N=NormalDist()
INF=float('inf')
def case_interval(rows):
    """Unclamped strict d-interval from the 34 branch inequalities (lo,hi), coincidence separately."""
    lo,hi=-INF,INF;empty=False
    for r in rows:
        a,b=bounds(r['case']);u,v=r['u_V'],r['v_V']
        if v==0:
            if not a<u<b:empty=True
            continue
        x,y=(a-u)/v,(b-u)/v;lo=max(lo,min(x,y));hi=min(hi,max(x,y))
    return lo,hi,(empty or not lo<hi)
def d_region(lo,hi):
    """Allowed values of g=(eW-A)/B before clipping, as (lower,upper,lower_closed,upper_closed) or None.
    d=clip(g,-1,1) must lie in the open (lo,hi)."""
    if hi<=-1 or lo>=1:return None           # no d in [-1,1] strictly inside
    gl,lc=(-INF,False) if lo<-1 else (lo,False)  # lo<-1 => d=-1 allowed, so all g<=-1 allowed
    gu,uc=(INF,False) if hi>1 else (hi,False)
    return gl,gu,lc,uc
def e_region(A,B,W,reg):
    """Map g-interval to e-interval: e=(B*g+A)/W. Returns (lo,hi) in volts, possibly infinite, or None; 'all' if W==0 and 0 allowed."""
    if reg is None:return None
    gl,gu,_,_=reg
    if W==0 or B==0:raise ValueError('degenerate W or B')
    f=lambda g:(B*g+A)/W if math.isfinite(g) else (math.copysign(INF,g*B*W))
    x,y=f(gl),f(gu);return (min(x,y),max(x,y))
def mass(iv):
    if iv is None:return 0.
    lo,hi=iv;return (N.cdf(hi/SIG) if math.isfinite(hi) else 1.)-(N.cdf(lo/SIG) if math.isfinite(lo) else 0.)
def inter(a,b):
    if a is None or b is None:return None
    lo,hi=max(a[0],b[0]),min(a[1],b[1]);return (lo,hi) if lo<hi else None
def reproduce_d164(caps,branches):
    rows=json.loads((V/'order_continuous_baseline/observations.json').read_text());old={(r['seed'],r['tau_s'],r['prior']):r for r in json.loads((V/'order_calibration_precision/rows.json').read_text())}
    err=0.;n=0
    for tau in TAUS:
        for prior in [.5,.8]:
            for seed,c in caps.items():
                rr=[r for r in rows if r['seed']==seed];a=b=w=0.
                for r in rr:
                    cc=r['case'];near=cc['a'] and cc['b'] and 0<abs(cc['delay'])<=.15;wt=(2*prior if cc['delay']>0 else 2*(1-prior)) if near else 1.
                    aa,bb=r['observations_Vs'][f'{tau}:random'];a+=wt*aa;b+=wt*bb;w+=wt*r['weight_s']
                lo,hi,empty=case_interval(branches[seed]);feasible=not empty and c['coincidence_all']
                iv=e_region(a,b,w,d_region(lo,hi)) if feasible else None;p=mass(iv);o=old[seed,tau,prior]
                err=max(err,abs(p-o['conditional_success']['1']));n+=1
                if feasible:err=max(err,abs(iv[0]-o['error_interval_V'][0]),abs(iv[1]-o['error_interval_V'][1]))
    return dict(rows=n,max_abs_error=err,valid=bool(n==240 and err<1e-12))
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    branches={}
    for b in json.loads((V/'order_balance_information/branches.json').read_text()):branches.setdefault(b['seed'],[]).append(b)
    caps={r['seed']:r for r in json.loads((V/'order_balance_information/draws.json').read_text())}
    feas={r['seed']:r for r in json.loads((V/'overnight_20261119/failures_results/feasible_intervals.json').read_text())}
    rep=reproduce_d164(caps,branches);print('D164 reproduction',rep,flush=True)
    if not rep['valid']:raise SystemExit('D164 not reproduced')
    S=[json.loads(l) for l in (V/'overnight_20261119/histories_results/settings.jsonl').read_text().splitlines()];assert len(S)==1920
    out=[];icheck=0.;zero_mismatch=[]
    for s in S:
        lo,hi,empty=case_interval(branches[s['seed']]);feasible=not empty and feas[s['seed']]['coincidence_all']
        if not empty:icheck=max(icheck,abs(max(lo,-1)-feas[s['seed']]['interval'][0]),abs(min(hi,1)-feas[s['seed']]['interval'][1]))
        assert s['identifiable'] and s['B_Vs']!=0 and s['W_s']>0  # 3 raw rows have B<0; e_region handles either sign
        iv=e_region(s['A_Vs'],s['B_Vs'],s['W_s'],d_region(lo,hi)) if feasible else None
        z=bool(iv is not None and iv[0]<0<iv[1])
        if z!=bool(s['all_pass']):zero_mismatch.append([s['seed'],s['replicate'],s['window'],s['mode']])
        out.append(dict(seed=s['seed'],replicate=s['replicate'],window=s['window'],mode=s['mode'],A_Vs=s['A_Vs'],B_Vs=s['B_Vs'],W_s=s['W_s'],d0=s['d'],
            feasible_draw=feasible,d_interval=[lo,hi] if not empty else None,error_region_V=list(iv) if iv else None,
            unbounded=bool(iv and not(math.isfinite(iv[0]) and math.isfinite(iv[1]))),zero_in_region=z,zero_error_all_pass=s['all_pass'],
            symmetric_tolerance_V=(min(-iv[0],iv[1]) if z else 0.),conditional_success=mass(iv)))
    with (OUT/'rows.jsonl').open('w') as f:
        for r in out:f.write(json.dumps(r)+'\n')
    key={(r['seed'],r['replicate'],r['window'],r['mode']):r for r in out}
    windows=sorted({r['window'] for r in out});modes=['raw']+[str(t) for t in TAUS];seeds=sorted({r['seed'] for r in out});reps=sorted({r['replicate'] for r in out})
    summary=dict(d164_reproduction=rep,interval_reproduction_max_error=icheck,zero_error_classification_mismatches=zero_mismatch,sigma_V=SIG,by_window_mode={},paired={})
    for w in windows:
        for m in modes:
            rr=[r for r in out if r['window']==w and r['mode']==m];tol=sorted(r['symmetric_tolerance_V'] for r in rr if r['zero_in_region'])
            summary['by_window_mode'][f'{w}|{m}']=dict(n=len(rr),zero_error_pass=sum(r['zero_in_region'] for r in rr),expected_successes=sum(r['conditional_success'] for r in rr),
                unbounded_regions=sum(r['unbounded'] for r in rr),median_symmetric_tolerance_mV=1000*float(np.median(tol)) if tol else None,min_positive_tolerance_mV=1000*tol[0] if tol else None)
    rng=np.random.default_rng(126);idx=rng.integers(0,len(seeds),size=(4000,len(seeds)))
    for m in modes:
        diffs={s:[] for s in seeds};items=[]
        for s in seeds:
            for k in reps:
                f,t=key[s,k,'full_1000s',m],key[s,k,'last_third_1000s',m]
                fi=tuple(f['error_region_V']) if f['error_region_V'] else None;ti=tuple(t['error_region_V']) if t['error_region_V'] else None
                both=mass(inter(fi,ti));pf,pt=f['conditional_success'],t['conditional_success']
                it=dict(seed=s,replicate=k,P_full=pf,P_third=pt,delta=pf-pt,P_both=both,P_full_only=pf-both,P_third_only=pt-both,zero_full=f['zero_in_region'],zero_third=t['zero_in_region'],
                    tol_full_mV=1000*f['symmetric_tolerance_V'],tol_third_mV=1000*t['symmetric_tolerance_V'],region_full_V=f['error_region_V'],region_third_V=t['error_region_V'])
                items.append(it);diffs[s].append(pf-pt)
        cm=np.array([np.mean(diffs[s]) for s in seeds]);boot=cm[idx].mean(axis=1)
        summary['paired'][m]=dict(histories=len(items),expected_full=sum(i['P_full'] for i in items),expected_third=sum(i['P_third'] for i in items),
            mean_delta=float(np.mean([i['delta'] for i in items])),cluster_bootstrap95=[float(np.quantile(boot,.025)),float(np.quantile(boot,.975))],
            expected_full_only=sum(i['P_full_only'] for i in items),expected_third_only=sum(i['P_third_only'] for i in items),
            zero_error_rescues=sum(i['zero_full'] and not i['zero_third'] for i in items),zero_error_harms=sum(i['zero_third'] and not i['zero_full'] for i in items),
            tolerance_losses=[dict(seed=i['seed'],replicate=i['replicate'],tol_third_mV=i['tol_third_mV'],tol_full_mV=i['tol_full_mV']) for i in items if i['tol_full_mV']<i['tol_third_mV']],
            per_component_mean_delta={str(s):float(v) for s,v in zip(seeds,cm)},items=items)
    (OUT/'summary.json').write_text(json.dumps(summary,indent=1)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='paired'},indent=1))
    for m in modes:print(m,{k:v for k,v in summary['paired'][m].items() if k not in('items','tolerance_losses','per_component_mean_delta')},'tolerance losses',len(summary['paired'][m]['tolerance_losses']))
if __name__=='__main__':main()

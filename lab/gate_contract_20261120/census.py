"""D172: census of the coincidence voltage (node 6) on the 40 D163 histories, for the steering-gate contract.

Unchanged generators (order_long_calibration.make_long_stream, order_baseline_stream.stream_trajectory), 1000 s at 0.5 ms,
as D170's replay. Event labels are used by this harness only, to attribute integrals and to define quiet time; no learner
sees them. For each effective threshold th in a grid (th = V_theta + g, the designed threshold plus one pair's offset):
  sigmoid gate (chip.py's gate pair):  w = 1/(1+exp(-NATIVE (V6 - th)))
  clipped gate (comparator):           w = clip((V6 - th)/V_TYP, 0, 1)
the integrals of w and of w*der (knob sensitivity, raw mode as D168's B) per event category, per anchor event, and the
histogram of quiet-time V6 (quiet: more than 2 s after the last event's start, and after the first 2 s of life).
Writes lab/v/gate_contract_20261120/census.npz and census.json (exclusive create).
"""
import copy,json,math,sys,time
from pathlib import Path
import numpy as np
from numba import njit
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
for p in [ROOT,ROOT/'lab',ROOT/'lab/calibration_next_20261120']:sys.path.insert(0,str(p))
import chip
from units import V_TYP
from order_long_calibration import make_long_stream
from order_baseline_stream import stream_trajectory
from t1b_weights import category
OUT=ROOT/'lab/v/gate_contract_20261120';DT=.0005;DUR=1000.;QUIET_AFTER=2.
CATS=['simultaneous','positive_near','negative_near','far','single']
TH=np.round(np.arange(-.15,.6001,.005),4)          # effective thresholds, V
HIST_EDGES=np.arange(-.2,.2001,.0001)               # quiet V6 histogram, 0.1 mV bins

@njit(cache=True)
def kernel(v6,der,lab,evi,th,nat,vtyp,dt,ncat,nev):
    nt=len(th);n=len(v6)
    Fs=np.zeros((ncat,nt));Bs=np.zeros((ncat,nt));Fc=np.zeros((ncat,nt));Bc=np.zeros((ncat,nt))
    Es=np.zeros((nev,nt));EBs=np.zeros((nev,nt));Ec=np.zeros((nev,nt));EBc=np.zeros((nev,nt));peak=np.full(nev,-9.)
    for k in range(n):
        c=lab[k]
        if c<0:continue
        e=evi[k];x=v6[k]
        if x>peak[e]:peak[e]=x
        for j in range(nt):
            s=1./(1.+math.exp(-nat*(x-th[j])));q=min(max((x-th[j])/vtyp,0.),1.)
            Fs[c,j]+=s*dt;Bs[c,j]+=s*der[k]*dt;Fc[c,j]+=q*dt;Bc[c,j]+=q*der[k]*dt
            Es[e,j]+=s*dt;EBs[e,j]+=s*der[k]*dt;Ec[e,j]+=q*dt;EBc[e,j]+=q*der[k]*dt
    return Fs,Bs,Fc,Bc,Es,EBs,Ec,EBc,peak

def main():
    start=time.monotonic();V=ROOT/'lab/v'
    raw=[json.loads(l) for l in (V/'motifs/order_v2/confirm.jsonl').read_text().splitlines()]
    dtmin=min(r['dt'] for r in raw);rows={r['seed']:r for r in raw if r['dt']==dtmin and not r['control']};assert len(rows)==40
    d163={r['seed']:r for r in json.loads((V/'order_long_calibration/streams.json').read_text())}
    out={};summ=[]
    for seed in sorted(rows):
        r,events=make_long_stream(rows[seed],10.,2);assert events==d163[seed]['events']
        t,v=stream_trajectory(r,.15,DT,DUR);p=copy.deepcopy(r);p['elements'][0][6]=0.
        _,pv=stream_trajectory(p,.15,DT,DUR);v6=v[6].copy();u=v[7].copy();der=2*pv[7]-u;del v,pv
        st=np.array([e['first_s'] for e in events]);cat=np.array([CATS.index(category(e['case'])) for e in events])
        k=np.searchsorted(st,t,side='right')-1           # event in force
        since=np.where(k>=0,t-st[np.maximum(k,0)],t)
        lab=np.where((k>=0)&(since<QUIET_AFTER),cat[np.maximum(k,0)],-1).astype(np.int64)
        quiet=(lab<0)&(t>=QUIET_AFTER)
        evi=np.maximum(k,0).astype(np.int64)
        Fs,Bs,Fc,Bc,Es,EBs,Ec,EBc,peak=kernel(v6,der,lab,evi,TH,chip.NATIVE,V_TYP,DT,len(CATS),len(events))
        hq,_=np.histogram(v6[quiet],HIST_EDGES)
        qv=v6[quiet];pre=[]
        for e in events:                                 # V6 just before each event (mean of the preceding 50 ms)
            i=int(round(e['first_s']/DT));pre.append(float(v6[max(i-100,0):i].mean()) if i>0 else float(v6[0]))
        out[seed]=dict(Fs=Fs,Bs=Bs,Fc=Fc,Bc=Bc,Es=Es,EBs=EBs,Ec=Ec,EBc=EBc,peak=peak,cat=cat,hq=hq,pre=np.array(pre),
            quiet_s=float(quiet.sum()*DT),qmin=float(qv.min()),qmax=float(qv.max()),qmean=float(qv.mean()),qsd=float(qv.std()),
            u_quiet_mean=float(u[quiet].mean()))
        summ.append(dict(seed=seed,quiet_s=out[seed]['quiet_s'],v6_quiet_mean_mV=qv.mean()*1e3,v6_quiet_sd_mV=qv.std()*1e3,v6_quiet_min_mV=qv.min()*1e3,
            v6_quiet_max_mV=qv.max()*1e3,v6_quiet_p999_mV=float(np.percentile(qv,99.9))*1e3,
            anchor_peaks_mV=[float(x*1e3) for x,c in zip(peak,cat) if c==0],
            peak_by_cat_max_mV={c:float(max([x for x,cc in zip(peak,cat) if cc==i],default=float('nan'))*1e3) for i,c in enumerate(CATS)}))
        print(seed,round(time.monotonic()-start,1),'quiet mean/max mV',round(qv.mean()*1e3,2),round(qv.max()*1e3,2),
              'anchor peaks mV',np.round(np.sort(peak[cat==0])*1e3,0)[:5],flush=True)
        if time.monotonic()-start>560:raise RuntimeError('budget')
    np.savez_compressed(OUT/'census.npz',TH=TH,HIST_EDGES=HIST_EDGES,cats=np.array(CATS),seeds=np.array(sorted(out)),
        **{f'{s}|{k}':v for s,d in out.items() for k,v in d.items() if isinstance(v,np.ndarray)})
    with (OUT/'census.json').open('x') as f:json.dump(dict(dt=DT,duration_s=DUR,quiet_after_s=QUIET_AFTER,per_draw=summ,
        scalars={str(s):{k:v for k,v in d.items() if not isinstance(v,np.ndarray)} for s,d in out.items()},elapsed_s=time.monotonic()-start),f,indent=1)
if __name__=='__main__':main()

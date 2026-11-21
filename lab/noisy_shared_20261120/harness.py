"""D173: frozen noisy confirmation of shared-path calibration with physical steering gates (notebook D173 protocol).

python lab/noisy_shared_20261120/harness.py run      all condition sets, pool of 6 (one maths thread each)
python lab/noisy_shared_20261120/harness.py refine   four fresh main draws at 0.25 and 0.125 ms (sequential)
Labels (event categories, cases, feasible ranges) are used by the harness only: to build schedules and controls, and to
score. The candidate sees v7, its own m and V_d, and V6 through its steering pairs.
"""
import copy,itertools,json,math,os,sys,time
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
for p in [ROOT,ROOT/'lab',ROOT/'lab/shared_readout_20261120',ROOT/'lab/calibration_next_20261120',HERE]:sys.path.insert(0,str(p))
import chip
from units import V_TYP,RAIL,K_B,T as TEMP,Q_SI,DT as UDT
from order_bench import build,cases
from dynamic_parts_bench import integrate,CAP
from population_trace_margin import predict
from overnight_20261119_support import old_case_limits
from checks import errors
from core2 import _run,SHARED,SEPARATE,CONST
OUT=ROOT/'lab/v/noisy_shared_20261120';DUR=1000.;START=2000/3;FINE=UDT   # noise drawn at 0.125 ms
FRESH=list(range(2026117300,2026117400));OLD=list(range(2026112200,2026112240))
P=json.loads((ROOT/'lab/v/shared_readout_20261120/bounds.json').read_text())['points']
ARMS={  # name: (point, law, V_theta, C_d scale, arm code)
 'shared_P2_g250':('P2_preamp','sigmoid',.25,.72,SHARED),'separate_P2_g250':('P2_preamp','sigmoid',.25,.72,SEPARATE),
 'shared_P1_g270':('P1_native','sigmoid',.27,.68,SHARED),'separate_P1_g270':('P1_native','sigmoid',.27,.68,SEPARATE),
 'shared_P1_ideal':('P1_native','clip0',0.,1.,SHARED)}

def category(c):
    if not(c['a']>0 and c['b']>0):return 'single'
    if c['delay']==0:return 'simultaneous'
    if abs(c['delay'])<=.15:return 'positive_near' if c['delay']>0 else 'negative_near'
    return 'far'

def schedule(row,idx,spacing=10.,skew=.8,amp=1.):
    """order_long_calibration.make_long_stream generalised (identical at idx=2, spacing 10, skew .8, amp 1)."""
    rng=np.random.default_rng([row['seed'],158,idx]);cc=cases();weights=[]
    for c in cc:
        near=c['a'] and c['b'] and 0<abs(c['delay'])<=.15
        weights.append((2*skew if c['delay']>0 else 2*(1-skew)) if near else 1.)
    prob=np.array(weights)/sum(weights);events=[];at=rng.uniform(0,spacing)
    while at<999.36:
        c=cc[rng.choice(len(cc),p=prob)];events.append(dict(first_s=float(at),case=c));at+=rng.uniform(.8,1.2)*spacing
    return events

def pulses_of(events,amp=1.):
    out=[]
    for e in events:
        c=e['case'];at=e['first_s']
        for node,a,t0 in [(0,c['a'],at+max(-c['delay'],0)),(1,c['b'],at+max(c['delay'],0))]:
            if a:out.append([float(t0),.04,node,CAP*a*amp/.01])
    return out

def component_row(seed):
    c=build(seed);return dict(seed=seed,nodes=c.node_arr.tolist(),elements=c.el_arr.tolist(),links=c.link.tolist())

def branches(row,amp=1.,gamma=0.):
    """34 isolated-case metrics as order_balance_information (predict at 0.05 ms): u, v at drift gain (1+gamma)."""
    out=[];jit=np.random.default_rng([row['seed'],128,5]).uniform(.001,.009);first=1+jit
    for case in cases():
        ta=first+max(-case['delay'],0);tb=first+max(case['delay'],0);pl=[]
        for i,(at,a) in enumerate([(ta,case['a']),(tb,case['b'])]):
            if a:pl.append([at,.04,i,CAP*a*amp/.01])
        r=dict(row,pulses=pl,case=case);orig=predict(r,.15,.00005);pos=copy.deepcopy(r);pos['elements'][0][6]=0.
        p=predict(pos,.15,.00005)['order_V'];n=orig['order_V']-p;p=(1+gamma)*p
        out.append(dict(case=case,u_V=p+n,v_V=p-n,coincidence_adequate=orig['coincidence_adequate']))
    return out

def feasible(br):
    lo,hi=-1.,1.
    for b in br:
        if not b['coincidence_adequate']:return None
        a,c=old_case_limits(b['case']);u,v=b['u_V'],b['v_V']
        if v==0:
            if not(a<u<c):return None
            continue
        x1,x2=(a-u)/v,(c-u)/v;lo,hi=max(lo,min(x1,x2)),min(hi,max(x1,x2))
    return (lo,hi) if lo<hi else None

def all_pass(br,d):
    return [bool(b['coincidence_adequate'] and (lambda l:l[0]<b['u_V']+d*b['v_V']<l[1])(old_case_limits(b['case']))) for b in br]

def noise(seed,tag,dt,steps):
    """standard normals per step for 8 engine nodes and 2 candidate states, drawn at FINE and summed (refinement-consistent)."""
    ratio=int(round(dt/FINE));rng=np.random.default_rng([seed,173,tag]);z=np.empty((steps,10));chunk=max(1,2_000_000//ratio)
    for a in range(0,steps,chunk):
        b=min(steps,a+chunk);z[a:b]=rng.standard_normal(((b-a)*ratio,10)).reshape(b-a,ratio,10).sum(axis=1)/math.sqrt(ratio)
    return z

def instream(t,v6,v7,events,dt):
    """per event: (passed, in final third) by the bench's frozen criteria on the actual traces."""
    res=[]
    for e in events:
        c=e['case'];f=e['first_s'];last=f+abs(c['delay'])
        if f<2. or last+.2>DUR:continue
        ib=slice(int(round((f-.25)/dt)),int(round((f-.05)/dt)));io=slice(int(round((last+.02)/dt)),int(round((last+.10)/dt)));ic=slice(int(round(f/dt)),int(round((last+.2)/dt)))
        order=float(v7[io].mean()-v7[ib].mean());coinc=float(v6[ic].max()-v6[ib].mean())
        pair=c['a']>0 and c['b']>0;dl=c['delay']
        gc=coinc>.15 if pair and dl==0 else coinc<.03 if (not pair or abs(dl)>=.15) else True
        lo,hi=old_case_limits(c);go=lo<order<hi
        res.append((bool(gc and go),bool(f>=START),bool(go),category(c),order))
    return res

def life(task):
    seed,cond,dt=task['seed'],task['cond'],task['dt'];t0=time.monotonic()
    row=component_row(seed);amp=task.get('amp',1.);gend=task.get('gamma',0.)
    events=schedule(row,task['idx'],task.get('spacing',10.),task.get('skew',.8))
    if task.get('keep'):events=[e for e in events if category(e['case']) in task['keep']]
    if task.get('keep')==[]:events=[]
    c=build(seed);steps=round(DUR/dt);z=noise(seed,task['noise_tag'],dt,steps)
    pl=np.array(pulses_of(events,amp)) if events else np.zeros((0,4))
    tr,power,charge,hits=integrate(c.V,c.Vx,c.armed,c.spikes,c.vmax,c.node_arr,c.el_arr,c.link,c.q,c.rest,c.cfg,np.ascontiguousarray(z[:,:8]),dt,1,pl,np.zeros(5))
    t=tr[:,0];v=tr[:,1:].T;del tr
    n=np.array(row['nodes']);el=np.array(row['elements']);L=np.array(row['links'])
    I=[]
    for j in (5,6):
        to,src,gate=L[:,j];assert to==7;x=el[2,j]*(v[src]-el[1,j]);f=1/(1+np.exp(-x)) if el[4,j]>.5 else np.tanh(x)
        if gate>=0:f=f*np.clip(v[gate]/V_TYP,0,1)
        I.append(el[0,j]*f)
    g7,C7=n[1,7],n[2,7];a7=math.exp(-dt*g7/C7);I5b=(I[0][:-1]+I[0][1:])/2;I6b=(I[1][:-1]+I[1][1:])/2
    gam=gend*t[:-1]/DUR;v6=v[6];v7e=v[7].copy();del v
    # informed reference (privileged, offline): D168's whole-life shared estimator, clipped engine weight, raw mode
    wc=np.clip(v6/V_TYP,0,1)
    pp=_filt(I5b*(1+gam),a7,g7);nn=_filt(I6b,a7,g7);der=pp-nn;u=v7e+_filt(gam*I5b,a7,g7)
    trap=lambda a:float(np.sum((a[:-1]+a[1:])*.5)*dt)
    W=trap(wc);Q=DUR-W;A=trap(wc*u);B=trap(wc*der);Aq=trap((1-wc)*u);Bq=trap((1-wc)*der)
    As,Bs=A-W/Q*Aq,B-W/Q*Bq;d_inf=float(np.clip(-As/Bs,-1,1)) if abs(Bs)>1e-15 else 0.
    del pp,nn,u
    er=errors(seed);brs=branches(row,amp,gend);fe=feasible(brs);recs=[]
    zc=np.ascontiguousarray(z[:,8:10]);del z
    def score(name,v7,d,m,acc,extra):
        dfin=float(d[-1]);ap=all_pass(brs,dfin);ins=instream(t,v6,v7,events,dt)
        ft=[x[0] for x in ins if x[1]];le=[x[0] for x in ins if not x[1]]
        infe=np.zeros(len(d),bool) if fe is None else (d>fe[0])&(d<fe[1]);out=np.nonzero(~infe)[0]
        settle=None if (fe is None or not infe[-1]) else float(t[out[-1]+1] if len(out) else 0.)
        r=dict(seed=seed,cond=cond,dt=dt,arm=name,d_final=dfin,d_min=float(d.min()),d_max=float(d.max()),isolated_all_pass=all(ap),isolated_passed=sum(ap),
            feasible=fe,in_feasible_final=bool(fe is not None and fe[0]<dfin<fe[1]),settle_s=settle,time_in_feasible_last_third=float(infe[int(START/dt):].mean()),
            instream_final=dict(n=len(ft),passed=int(sum(ft))),instream_learning=dict(n=len(le),passed=int(sum(le))),
            instream_order_by_cat={cat:float(np.mean([x[4] for x in ins if x[3]==cat and x[1]])) if any(x[3]==cat and x[1] for x in ins) else None for cat in ('positive_near','negative_near','simultaneous')},
            eps_vs_informed_mV=float(-(As+dfin*Bs)/W*1e3) if W>0 else None,d_informed=d_inf,events=len(events),rail_hits=int(hits),power_engine_W=float(power))
        if acc is not None:r.update(write_charge_C=float(acc[0]),write_time_s=float(acc[1]),quiet_write_charge_C=float(acc[2]),write_charge_last_third_C=float(acc[4]),
            max_abs_m=float(np.max(np.abs(m))),quiet_track_rms_mV=float(math.sqrt(acc[7]/acc[5])*1e3) if acc[5] else None)
        r.update(extra);return r
    kT=K_B*TEMP
    for name,(pt,law,Vt,cds,code) in ARMS.items():
        p=P[pt]
        if law=='sigmoid':w1=1/(1+np.exp(-chip.NATIVE*(v6[:-1]-Vt-er['g1'])));w2=1/(1+np.exp(-chip.NATIVE*(v6[:-1]-Vt-er['g2'])))
        else:w1=wc[:-1].copy();w2=w1
        v7,d,m,acc=_run(v7e,I5b,I6b,gam,w1,w2,a7,g7,dt,code,p['slope_per_V'],p['I0_A'],p['k_q'],p['k_w'],p['g_m_S'],p['V_bias_V'],p['C_m_F'],p['C_d_F']*cds,chip.DEAD,
            er['e'],er['e_q'] if code==SEPARATE else er['e'],er['alpha'],er['beta'],V_TYP,RAIL,0.,kT,Q_SI,zc,START)
        recs.append(score(name,v7,d,m,acc,{}));del v7,d,m,w1,w2
    for name,dc in (('fixed',0.),('informed',d_inf)):
        p=P['P1_native'];v7,d,m,acc=_run(v7e,I5b,I6b,gam,wc[:-1],wc[:-1],a7,g7,dt,CONST,p['slope_per_V'],p['I0_A'],p['k_q'],p['k_w'],p['g_m_S'],0.,p['C_m_F'],p['C_d_F'],chip.DEAD,
            0.,0.,0.,0.,V_TYP,RAIL,dc,kT,Q_SI,zc,START)
        recs.append(score(name,v7,d,m,None,{}))
    for r in recs:r['elapsed_s']=time.monotonic()-t0
    return recs

from numba import njit
@njit(cache=True)
def _filt(I,a7,g7):
    x=np.zeros(len(I)+1)
    for k in range(len(I)):x[k+1]=a7*x[k]+(1-a7)/g7*I[k]
    return x

def tasks():
    T=[]
    for s in FRESH:T.append(dict(seed=s,cond='main',idx=73,dt=.0005,noise_tag=0))
    for s in FRESH[:30]:
        T.append(dict(seed=s,cond='balanced_skew',idx=73,skew=.5,dt=.0005,noise_tag=1))
        T.append(dict(seed=s,cond='sparse',idx=73,spacing=20.,dt=.0005,noise_tag=2))
        T.append(dict(seed=s,cond='weak_inputs',idx=73,amp=.8,dt=.0005,noise_tag=3))
        T.append(dict(seed=s,cond='drift',idx=73,gamma=.1,dt=.0005,noise_tag=4))
    for s in FRESH[:10]:
        T.append(dict(seed=s,cond='no_input',idx=73,keep=[],dt=.0005,noise_tag=0))
        T.append(dict(seed=s,cond='no_anchor',idx=73,keep=['positive_near','negative_near','far','single'],dt=.0005,noise_tag=0))
        T.append(dict(seed=s,cond='ordered_only',idx=73,keep=['positive_near','negative_near'],dt=.0005,noise_tag=0))
    for s in OLD:T.append(dict(seed=s,cond='old_diagnostic',idx=2,dt=.0005,noise_tag=0))
    return T

def main():
    mode=sys.argv[1];start=time.monotonic()
    if mode=='run':
        from multiprocessing import Pool
        T=tasks();fh=(OUT/'records.jsonl').open('x');done=0
        with Pool(6) as pool:
            for recs in pool.imap_unordered(life,T):
                for r in recs:fh.write(json.dumps(r)+'\n')
                fh.flush();done+=1
                if done%10==0:print('done',done,'of',len(T),round(time.monotonic()-start,1),flush=True)
                if time.monotonic()-start>5000:print('BUDGET GUARD',flush=True);pool.terminate();break
        fh.close()
    elif mode=='refine':
        fh=(OUT/'refine.jsonl').open('x')
        for s in FRESH[:4]:
            for dt in (.00025,.000125):
                for r in life(dict(seed=s,cond='main',idx=73,dt=dt,noise_tag=0)):fh.write(json.dumps(r)+'\n')
                fh.flush();print('refined',s,dt,round(time.monotonic()-start,1),flush=True)
        fh.close()
    elif mode=='one':
        recs=life(dict(seed=int(sys.argv[2]),cond='probe',idx=int(sys.argv[3]),dt=.0005,noise_tag=9))
        for r in recs:print(r['arm'],r['d_final'],r['isolated_all_pass'],r['instream_final'],r['eps_vs_informed_mV'],round(r['elapsed_s'],1))
    print('elapsed',round(time.monotonic()-start,1))
if __name__=='__main__':main()

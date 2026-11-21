"""D170 task 3: cheap discriminating checks of the candidate (core.py) before any history replay, and the static
error budget on synthetic anchors. Synthetic inputs only (no D163 trajectory). Writes
lab/v/shared_readout_20261120/checks/checks.json and budget_rows.jsonl once.

Synthetic anchor (harness only): every 5 s, coincidence weight w = sin^2(pi t/0.12) on 0..0.12 s; the positive-path
current into node 7 a sin^2 bump on 0..0.10 s of amplitude g7*P, the negative path -g7*N on 0.02..0.16 s (different
shapes, so the balanced output is biphasic and curvature/erosion can show). Resting currents put node 7 at the draw's
own resting level u_rest (D168 arithmetic.json) independent of d. Node 7 leak/capacitance: the first D163 draw's.
Errors: the frozen allocation rng([seed,170,1]) (CONTRACT §4). Ideal limits (linear tanh, leak-free tracker, no dead
band) are labelled nonphysical references.
"""
import json,math,sys,time
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(HERE));sys.path.insert(0,str(ROOT))
import chip
from units import V_TYP,RAIL,R_MAX
from core import run,currents,SHARED,SEPARATE,FIXED
OUT=ROOT/'lab/v/shared_readout_20261120/checks'
DT=.0005;P_AMP,N_AMP=.10,.08;PERIOD=5.;DUR=300.

def errors(seed):
    z=np.random.default_rng([seed,170,1]).standard_normal(6)
    return dict(e=.1*V_TYP*z[0],e_q=.1*V_TYP*z[1],alpha=.1*z[2],beta=.1*z[3],g1=.1*V_TYP*z[4],g2=.1*V_TYP*z[5])

def bump(t,a,b):
    x=np.clip((t-a)/(b-a),0,1);return np.where((t>a)&(t<b),np.sin(np.pi*x)**2,0.)

def synthetic(g7,u_rest,dur=DUR,P=P_AMP,N=N_AMP,period=PERIOD,anchors=True):
    t=np.arange(round(dur/DT)+1)*DT;ph=np.mod(t,period)
    on=anchors and 1.
    w=on*bump(ph,1.,1.12) if anchors else np.zeros_like(t)
    I5=g7*u_rest/2+on*g7*P*bump(ph,1.,1.10) if anchors else np.full_like(t,g7*u_rest/2)
    I6=g7*u_rest/2-on*g7*N*bump(ph,1.02,1.16) if anchors else np.full_like(t,g7*u_rest/2)
    return t,w,I5,I6

def tbar(x):return (x[:-1]+x[1:])/2

def point(p,**kw):
    q=dict(p);q['dead']=chip.DEAD;q.update(kw);return q

def linear(p):   # ideal linear reference: tanh slope /1000, current x1000 (same loop gains and rates), no dead band
    return point(p,slope_per_V=p['slope_per_V']*1e-3,I0_A=p['I0_A']*1e3,dead=0.)

def main():
    OUT.mkdir(parents=True,exist_ok=False);t0=time.monotonic()
    B=json.loads((ROOT/'lab/v/shared_readout_20261120/bounds.json').read_text());PTS=B['points']
    arith=json.loads((ROOT/'lab/v/calibration_precision_20261120/b/arithmetic.json').read_text())
    rows=[json.loads(l) for l in (ROOT/'lab/v/motifs/order_v2/confirm.jsonl').read_text().splitlines()]
    n7=np.array(rows[0]['nodes']);g7,C7=n7[1,7],n7[2,7];a7=math.exp(-DT*g7/C7)
    res=dict(node7=dict(g7_S=g7,C7_F=C7),checks={})
    zero=dict(e=0.,e_q=0.,alpha=0.,beta=0.)
    def sim(arm,p,err,w1,w2,I5,I6,u0,**k):
        return run(tbar(I5),tbar(I6),w1[:-1],w2[:-1],a7,g7,u0,DT,arm,p,err,V_TYP,RAIL,2*DUR/3,**k)

    # 1. constant input: tracker fixed point against the analytic finite-leak solution
    c=[]
    for name,p0 in PTS.items():
        p=point(p0)
        for u0,e,beta in ((.08,.03,.1),(-.05,-.02,-.1),(.0,.0,.0)):
            n=round(3./DT);I=np.full(n+1,g7*u0/2);w=np.zeros(n+1)
            v7,d,m,a=run(I[:-1],I[:-1],w[:-1],w[:-1],a7,g7,u0,DT,SHARED,p,dict(e=e,e_q=e,alpha=0.,beta=beta),V_TYP,RAIL,2.)
            f=lambda mm:p['k_q']*p['I0_A']*(math.tanh(p['slope_per_V']*(u0-mm-e))+beta/2)-p['g_m_S']*(mm-p['V_bias_V'])
            lo,hi=-RAIL,RAIL
            for _ in range(200):
                mid=(lo+hi)/2
                if f(mid)>0:lo=mid
                else:hi=mid
            c.append(dict(point=name,u_V=u0,e_V=e,beta=beta,m_sim=float(m[-1]),m_analytic=lo,error_V=abs(float(m[-1])-lo),knob_moved=float(abs(d[-1]))))
    res['checks']['constant_input']=dict(rows=c,passed=bool(all(r['error_V']<1e-6 and r['knob_moved']==0 for r in c)))

    # 2. shared-offset cancellation in the ideal linear, leak-free limit; expected failure for separate offsets
    seed=2026112200;ur=arith['per_draw'][0]['u_rest_V'];t,w,I5,I6=synthetic(g7,ur)
    canc=[]
    for name,p0 in PTS.items():
        p=point(linear(p0),g_m_S=1e-30,dead=0.)   # correction 1: point() had re-applied the dead band at the x1000 linear scale
        dd={}
        for arm in (SHARED,SEPARATE):
            for e,eq in ((0.,0.),(.03,.03),(-.03,-.03),(.03,-.03)):
                v7,d,m,a=sim(arm,p,dict(e=e,e_q=eq,alpha=0.,beta=0.),w,w,I5,I6,ur);dd[arm,e,eq]=float(d[-1])
        canc.append(dict(point=name,shared={f'{e},{eq}':dd[SHARED,e,eq] for (arm,e,eq) in dd if arm==SHARED},
            separate={f'{e},{eq}':dd[SEPARATE,e,eq] for (arm,e,eq) in dd if arm==SEPARATE},
            shared_max_change=max(abs(dd[SHARED,e,eq]-dd[SHARED,0.,0.]) for (arm,e,eq) in dd if arm==SHARED),
            separate_unequal_change=abs(dd[SEPARATE,.03,-.03]-dd[SEPARATE,0.,0.]),
            separate_equal_change=max(abs(dd[SEPARATE,.03,.03]-dd[SEPARATE,0.,0.]),abs(dd[SEPARATE,-.03,-.03]-dd[SEPARATE,0.,0.]))))
    res['checks']['ideal_cancellation']=dict(label='nonphysical reference: linear tanh, leak-free tracker, no dead band',rows=canc,
        passed=bool(all(r['shared_max_change']<1e-4 and r['separate_equal_change']<1e-4 and r['separate_unequal_change']>1e-3 for r in canc)))

    # 3. feedback sign, bounded states, current conservation
    sg=[]
    for name,p0 in PTS.items():
        p=point(p0);fx=sim(FIXED,p,zero,w,w,I5,I6,ur)
        der_fx=None
        v7,d,m,a=sim(SHARED,p,zero,w,w,I5,I6,ur)
        # offline linear optimum on this synthetic stream (harness only): affine in constant d
        q=point(p0);p5=sim(FIXED,q,zero,w,w,I5,np.full_like(I6,g7*ur/2),ur)[0]
        p6=sim(FIXED,q,zero,w,w,np.full_like(I5,g7*ur/2),I6,ur)[0]
        u0=fx[0];der=(p5-ur)-(p6-ur)
        A=float(np.sum(w*(u0-ur))*DT);Bv=float(np.sum(w*der)*DT);dstar=-A/Bv
        k_end=[int(round((1.2+i*PERIOD)/DT)) for i in range(int(DUR/PERIOD))]
        gaps=[abs(d[k]-dstar) for k in k_end]
        sg.append(dict(point=name,A_Vs=A,B_Vs=Bv,d_star_linear=dstar,d_final=float(d[-1]),gap_start=abs(0-dstar),gap_end=gaps[-1],
            gap_after_anchors=[float(x) for x in gaps[:8]],moved_toward=bool(gaps[-1]<abs(dstar))))
    rng=np.random.default_rng(170);n=round(60/DT)
    wr=np.clip(rng.standard_normal(n+1).cumsum()*.01,0,1);Ir=g7*rng.standard_normal(n+1).cumsum()*.002
    bounded=[]
    for name,p0 in PTS.items():
        for arm in (SHARED,SEPARATE):
            v7,d,m,a=run(tbar(Ir),tbar(-Ir*.7),wr[:-1],wr[:-1],a7,g7,0.,DT,arm,point(p0),errors(seed),V_TYP,RAIL,40.)
            bounded.append(dict(point=name,arm=arm,finite=bool(np.all(np.isfinite(v7))&np.all(np.isfinite(m))),
                max_abs_m=float(np.max(abs(m))),max_abs_d=float(np.max(abs(d))),max_abs_Vd=a['max_abs_Vd'],within=bool(np.max(abs(m))<=RAIL and np.max(abs(d))<=1 and a['max_abs_Vd']<=RAIL)))
    cons=0.
    for _ in range(2000):
        u,mm,w1,w2=rng.uniform(-.3,.3),rng.uniform(-.3,.3),rng.uniform(0,1),rng.uniform(0,1)
        Ik,Im=currents(SHARED,u,mm,w1,w2,13.,1e-10,1.,1.,.01,.0,0.,0.);cons=max(cons,abs(Ik+Im-1e-10*math.tanh(13.*(u-mm-.01))))
    res['checks']['feedback_sign']=dict(rows=sg,passed=bool(all(r['moved_toward'] for r in sg)))
    res['checks']['bounded_states']=dict(rows=bounded,passed=bool(all(r['finite'] and r['within'] for r in bounded)))
    res['checks']['current_conservation']=dict(max_error_A=cons,passed=bool(cons<1e-22))

    # 4. prefix causality: change inputs after 150 s; states before must be identical
    K=round(150/DT);w_b=w.copy();w_b[K+1:]=1-w_b[K+1:];I5b=I5.copy();I5b[K+1:]*=-3
    cz=[]
    for name,p0 in PTS.items():
        for arm in (SHARED,SEPARATE):
            x=sim(arm,point(p0),errors(seed),w,w,I5,I6,ur);y=sim(arm,point(p0),errors(seed),w_b,w_b,I5b,I6,ur)
            cz.append(dict(point=name,arm=arm,prefix_identical=bool(np.array_equal(x[1][:K+1],y[1][:K+1]) and np.array_equal(x[2][:K+1],y[2][:K+1]) and np.array_equal(x[0][:K+1],y[0][:K+1])),
                future_differs=bool(not np.array_equal(x[1],y[1]))))
    res['checks']['prefix_causality']=dict(rows=cz,passed=bool(all(r['prefix_identical'] and r['future_differs'] for r in cz)))

    # 5. identical read-path errors: shared and separate coincide
    ide=[]
    for name,p0 in PTS.items():
        er=errors(seed);er['e_q']=er['e']
        x=sim(SHARED,point(p0),er,w,w,I5,I6,ur);y=sim(SEPARATE,point(p0),er,w,w,I5,I6,ur)
        ide.append(dict(point=name,max_d_diff=float(np.max(abs(x[1]-y[1]))),max_m_diff=float(np.max(abs(x[2]-y[2])))))
    res['checks']['identical_errors_coincide']=dict(rows=ide,passed=bool(all(r['max_d_diff']<1e-12 and r['max_m_diff']<1e-12 for r in ide)))

    # 6. lost gain: known positive and negative order inputs, knob frozen (huge C_d), reading integrated over one anchor;
    #    against the ideal hold (tracker frozen at rest: huge C_m)
    lg=[]
    for name,p0 in PTS.items():
        for X in (.02,-.02,.05,-.05):
            tt,ww,_,_=synthetic(g7,0.,dur=3.,period=3.);I5x=g7*X*bump(np.mod(tt,3.),1.,1.10)
            def q(Cm):
                pp=point(p0,C_d_F=1e3,C_m_F=Cm);v7,d,m,a=sim(SHARED,pp,zero,ww,ww,I5x,np.zeros_like(I5x),0.)
                # writer current integral recomputed from states (harness), dead band included
                x=pp['k_w']*pp['I0_A']*ww*np.tanh(pp['slope_per_V']*(v7-m));y=np.sign(x)*np.maximum(abs(x)-chip.DEAD*pp['k_w']*pp['I0_A'],0)
                return float(np.sum(y)*DT),float(np.max(abs(m)))
            Qc,mc=q(p0['C_m_F']);Qi,mi=q(1e3)
            lg.append(dict(point=name,order_input_V=X,reading_causal_C=Qc,reading_ideal_hold_C=Qi,retained_fraction=Qc/Qi,tracker_excursion_V=mc,sign_kept=bool(np.sign(Qc)==np.sign(X))))
    res['checks']['known_order_inputs_lost_gain']=dict(rows=lg,passed=bool(all(r['sign_kept'] for r in lg)),
        note='retained_fraction < 1 is anchor erosion by the fast tracker; reported, not thresholded')

    # 7. static budget on synthetic anchors, 40 draws' u_rest and frozen errors, terms separately then combined
    fh=(OUT/'budget_rows.jsonl').open('x');summ={}
    conds=[('ideal_erosion_only',dict(lin=True,leak=False,dead=False,mirror=False,gate=False)),
           ('leak',dict(lin=True,leak=True,dead=False,mirror=False,gate=False)),
           ('mirror',dict(lin=False,leak=False,dead=False,mirror=True,gate=False)),   # correction 1: output-stage terms are input-referred by 1/s, so tanh at the real slope (compare with curvature)
           ('dead_band',dict(lin=False,leak=False,dead=True,mirror=False,gate=False,tanh_only_for_dead=True)),
           ('curvature',dict(lin=False,leak=False,dead=False,mirror=False,gate=False)),
           ('gate_sensitivity',dict(lin=False,leak=False,dead=False,mirror=False,gate=True)),   # correction 1: as mirror
           ('combined_nominal_gates',dict(lin=False,leak=True,dead=True,mirror=True,gate=False)),
           ('combined_with_gate_sensitivity',dict(lin=False,leak=True,dead=True,mirror=True,gate=True))]
    for name,p0 in PTS.items():
        for dr in arith['per_draw']:
            sd=dr['seed'];ur=dr['u_rest_V'];er=errors(sd);t,w,I5,I6=synthetic(g7,ur)
            fx=sim(FIXED,point(p0),zero,w,w,I5,I6,ur)[0]
            p5=sim(FIXED,point(p0),zero,w,w,I5,np.full_like(I6,g7*ur/2),ur)[0];p6=sim(FIXED,point(p0),zero,w,w,np.full_like(I5,g7*ur/2),I6,ur)[0]
            der=p5-p6;A=float(np.sum(w*(fx-ur))*DT);Bv=float(np.sum(w*der)*DT);W=float(np.sum(w)*DT);dstar=-A/Bv
            for cn,cf in conds:
                pp=point(p0)
                if cf['lin']:pp=linear(p0)
                if not cf['leak']:pp['g_m_S']=1e-30
                pp['dead']=chip.DEAD if cf['dead'] else 0.
                w1=np.clip(w-(er['g1']/V_TYP if cf['gate'] else 0.),0,1);w2=np.clip(w-(er['g2']/V_TYP if cf['gate'] else 0.),0,1)
                for arm in (SHARED,SEPARATE):
                    e2=dict(e=er['e'],e_q=er['e_q'] if arm==SEPARATE else er['e'],alpha=er['alpha'] if cf['mirror'] else 0.,beta=er['beta'] if cf['mirror'] else 0.)
                    v7,d,m,a=sim(arm,pp,e2,w1,w2,I5,I6,ur)
                    df=float(d[-1]);eps=-(A+df*Bv)/W     # equivalent constant readout error at the final knob (V)
                    r=dict(point=name,seed=sd,condition=cn,arm='shared' if arm==SHARED else 'separate',d_star=dstar,d_final=df,eps_mV=eps*1e3,
                           clipped=bool(abs(df)>=1),max_abs_Vd=a['max_abs_Vd'],quiet_write_charge_C=a['quiet_write_charge_C'])
                    fh.write(json.dumps(r)+'\n');summ.setdefault((name,cn,r['arm']),[]).append(r)
            if time.monotonic()-t0>110:break
    fh.close()
    S=[]
    for (name,cn,arm),rs in summ.items():
        e=np.array([r['eps_mV'] for r in rs])
        S.append(dict(point=name,condition=cn,arm=arm,n=len(rs),mean_mV=float(e.mean()),sd_mV=float(e.std(ddof=1)),rms_mV=float(np.sqrt(np.mean(e*e))),
            max_abs_mV=float(np.max(abs(e))),clipped=sum(r['clipped'] for r in rs),within_10mV=int(np.sum(abs(e)<10)),within_15mV=int(np.sum(abs(e)<15))))
    res['static_budget']=dict(note='equivalent constant readout error at the final knob on 300 s of synthetic anchors (60 anchors), against the harness linear optimum of that stream; '
        'ideal_erosion_only is the nonphysical linear leak-free reference; dead_band uses tanh with the band; gate_sensitivity uses the assumed 30 mV gate offsets',rows=S)
    res['passed_all']=bool(all(v['passed'] for v in res['checks'].values()));res['elapsed_s']=time.monotonic()-t0
    (OUT/'checks.json').write_text(json.dumps(res,indent=1)+'\n')
    print(json.dumps({k:v['passed'] for k,v in res['checks'].items()},indent=1))
    for s in S:print(s['point'],s['condition'],s['arm'],'n',s['n'],'mean %.2f sd %.2f rms %.2f max %.2f clip %d in10 %d'%(s['mean_mV'],s['sd_mV'],s['rms_mV'],s['max_abs_mV'],s['clipped'],s['within_10mV']))
    print('elapsed',round(res['elapsed_s'],1))
if __name__=='__main__':main()

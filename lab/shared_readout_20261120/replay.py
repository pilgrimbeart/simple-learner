"""D170 task 4: conditional causal replay on the 40 D163 schedules — exploratory mathematical reference only.

Regenerates the schedules with unchanged generators (order_long_calibration.make_long_stream, order_baseline_stream.
stream_trajectory), exactly as D167/D168 (t1b_weights.signals' raw-mode lines are reproduced here because the upstream
node voltages it discards are needed for node 7's branch currents). Streams each trajectory through all arms, then
discards it. Arms per parameter point (bounds.json): shared reading, separate reading paths; plus the fixed knob d = 0
(removal) and D168's whole-history shared reference (privileged, offline, read from its records). Nominal gates only:
the gate-mismatch sensitivity failed its static bound (checks.json) and is not replayed.

Gates before interpretation: schedules identical to D163; raw-mode A/B/W within 1e-12 of D168's records; node 7
propagated causally at fixed knob equals the unchanged trajectory within 1e-12 V; refinement of 2026112200/2026112227 at
0.25 and 0.125 ms. Then three diagnostic input controls on those two seeds (no input, ordered only, simultaneous only).
"""
import copy,json,math,sys,time
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
for p in [ROOT,ROOT/'lab',ROOT/'lab/calibration_next_20261120',HERE]:sys.path.insert(0,str(p))
import chip
from units import V_TYP,RAIL
from order_long_calibration import make_long_stream
from order_baseline_stream import stream_trajectory
from overnight_20261119_support import score_branches,setting,old_case_limits
from t1b_weights import pulses_of,category,START,DUR
from core import run,SHARED,SEPARATE,FIXED
from checks import errors
V=ROOT/'lab/v';OUT=V/'shared_readout_20261120/replay';DT=.0005;BUDGET=1750.;SEEDS_FINE=(2026112200,2026112227)
ARMS={'shared':SHARED,'separate':SEPARATE}

def feasible(branches):
    """Exact d interval in [-1,1] on which all 34 old cases pass (empty -> None)."""
    lo,hi=-1.,1.
    for b in branches:
        if not b['coincidence_adequate']:return None
        a,c=old_case_limits(b['case']);u,v=b['u_V'],b['v_V']
        if v==0:
            if not(a<u<c):return None
            continue
        x1,x2=(a-u)/v,(c-u)/v;l,h=min(x1,x2),max(x1,x2);lo,hi=max(lo,l),min(hi,h)
    return (lo,hi) if lo<hi else None

def branch_currents(row,v):
    n=np.array(row['nodes']);e=np.array(row['elements']);links=np.array(row['links']);e[1,:2]+=.15-.15
    js=[j for j in range(e.shape[1]) if links[0,j]==7];assert js==[5,6],js
    out=[]
    for j in js:
        to,src,gate=links[:,j];x=e[2,j]*(v[src]-e[1,j]);f=1/(1+np.exp(-x)) if e[4,j]>.5 else np.tanh(x)
        if gate>=0:f=f*np.clip(v[gate]/V_TYP,0,1)
        out.append(e[0,j]*f)
    g7,C7=n[1,7],n[2,7]
    return out[0],out[1],g7,C7

def one(row,events,branches,dt,d168,params,label,save_hist=None):
    t,v=stream_trajectory(row,.15,dt,DUR);p=copy.deepcopy(row);p['elements'][0][6]=0.
    _,pv=stream_trajectory(p,.15,dt,DUR);u=v[7].copy();der=2*pv[7]-u;w=np.clip(v[6]/V_TYP,0,1)
    del pv
    I5,I6,g7,C7=branch_currents(row,v);v70=float(v[7][0]);del v
    i0=int(np.searchsorted(t,START,side='left'));trap=lambda a,s:float(np.sum((a[s][:-1]+a[s][1:])*.5)*dt)
    wins={'full_1000s':slice(0,None),'final_third_1000s':slice(i0,None)}
    rep={win:dict(A_Vs=trap(w*u,s),B_Vs=trap(w*der,s),W_s=trap(w,s)) for win,s in wins.items()}
    a7=math.exp(-dt*g7/C7);I5b=(I5[:-1]+I5[1:])/2;I6b=(I6[:-1]+I6[1:])/2;del I5,I6
    wk=w[:-1].copy()
    fx_v7,fx_d,_,_=run(I5b,I6b,wk,wk,a7,g7,v70,dt,FIXED,dict(params['P1_native'],dead=chip.DEAD),dict(e=0.,e_q=0.,alpha=0.,beta=0.),V_TYP,RAIL,START)
    repro_v7=float(np.max(np.abs(fx_v7-u)))
    fe=feasible(branches);er=errors(row['seed']);ev_t=np.array([x['first_s'] for x in events]);ev_k=np.clip(np.round(ev_t/dt).astype(int),0,len(t)-1)
    case_index={b['case']['id']:k for k,b in enumerate(branches)}
    pos=[b for b in branches if b['case']['a']>0 and b['case']['b']>0 and 0<b['case']['delay']<=.15]
    neg=[b for b in branches if b['case']['a']>0 and b['case']['b']>0 and -.15<=b['case']['delay']<0]
    recs=[];hist={}
    def metrics(arm,point,v7,d,m,acc):
        dfin=float(d[-1]);sc=score_branches(branches,dfin);inf=lambda x:fe is not None and fe[0]<x<fe[1]
        infe=np.zeros(len(d),bool) if fe is None else (d>fe[0])&(d<fe[1])
        out=np.nonzero(~infe)[0];delay=None if (fe is None or not infe[-1]) else float(t[out[-1]+1] if len(out) else 0.)
        r=dict(seed=row['seed'],history=label,dt=dt,point=point,arm=arm,errors=er,d_final=dfin,d_at_final_third_start=float(d[i0]),
            d_mean_final_third=float(np.mean(d[i0:])),passed=sum(x['passed'] for x in sc),all_pass=all(x['passed'] for x in sc),case_pass=[x['passed'] for x in sc],
            feasible=fe,in_feasible_final=bool(inf(dfin)),time_in_feasible_full=float(np.mean(infe)),time_in_feasible_last_third=float(np.mean(infe[i0:])),
            calibration_delay_s=delay,max_abs_m=float(np.max(np.abs(m))),m_final=float(m[-1]),acc=acc,
            pos_near_mean_V=float(np.mean([b['u_V']+dfin*b['v_V'] for b in pos])),neg_near_mean_V=float(np.mean([b['u_V']+dfin*b['v_V'] for b in neg])),
            pos_near_min_V=float(np.min([b['u_V']+dfin*b['v_V'] for b in pos])),neg_near_max_V=float(np.max([b['u_V']+dfin*b['v_V'] for b in neg])))
        # residual readout error against D168's offline shared reference (raw mode, weight w), both windows
        for win in ('full_1000s','final_third_1000s'):
            x=d168.get((win,'raw'))
            if x:r[f'eps_vs_offline_{win}_mV']=-(x['A_star_Vs']+dfin*x['B_star_Vs'])/x['W_s']*1e3
        # quiet tracking error of the tracker's own reading
        if acc['quiet_n']:
            for pre,key in (('quiet','full'),('lt_quiet','last_third')):
                nq=acc[pre+'_n'];mu=acc[pre+'_sum']/nq;rms=math.sqrt(acc[pre+'_sumsq']/nq)
                r[f'tracking_{key}_mV']=dict(mean=mu*1e3,rms=rms*1e3,sd=math.sqrt(max(rms*rms-mu*mu,0))*1e3,max=acc[pre+'_max']*1e3)
        # isolated-case score of each event's own case at the knob in force at its start (the in-stream response is unscorable)
        ok=[];okl=[]
        for k,(x,kk) in enumerate(zip(events,ev_k)):
            b=branches[case_index[x['case']['id']]];lo,hi=old_case_limits(b['case']);y=b['u_V']+d[kk]*b['v_V'];pa=bool(lo<y<hi and b['coincidence_adequate'])
            ok.append(pa)
            if x['first_s']>=START:okl.append(pa)
        r['event_isolated_pass_share']=dict(full=float(np.mean(ok)),last_third=float(np.mean(okl)) if okl else None,events=len(ok))
        return r
    for point,pp in params.items():
        q=dict(pp,dead=chip.DEAD)
        for arm,code in ARMS.items():
            v7,d,m,acc=run(I5b,I6b,wk,wk,a7,g7,v70,dt,code,q,dict(e=er['e'],e_q=er['e_q'] if code==SEPARATE else er['e'],alpha=er['alpha'],beta=er['beta']),V_TYP,RAIL,START)
            r=metrics(arm,point,v7,d,m,acc)
            aff=u+d*der;dev=np.abs(v7-aff);r['affine_deviation_V']=dict(max=float(dev.max()),max_where_w_gt_0p01=float(dev[w>.01].max()) if np.any(w>.01) else 0.,
                rms_where_w_gt_0p01=float(np.sqrt(np.mean(dev[w>.01]**2))) if np.any(w>.01) else 0.)
            r['d_at_events']=[float(d[k]) for k in ev_k]
            recs.append(r)
            if save_hist is not None:
                step=round(1./dt);hist[f'{point}|{arm}|d']=d[::step].astype(np.float32);hist[f'{point}|{arm}|m']=m[::step].astype(np.float32)
            del v7,d,m,aff,dev
    r=metrics('fixed','none',fx_v7,fx_d,np.zeros_like(fx_d),dict(quiet_n=0,quiet_sum=0,quiet_sumsq=0,quiet_max=0,lt_quiet_n=0,lt_quiet_sum=0,lt_quiet_sumsq=0,lt_quiet_max=0,
        write_charge_C=0.,write_time_s=0.,quiet_write_charge_C=0.,max_abs_Vd=0.,write_charge_last_third_C=0.));recs.append(r)
    for win in ('full_1000s','final_third_1000s'):
        x=d168.get((win,'raw'))
        if x:recs.append(dict(seed=row['seed'],history=label,dt=dt,point='none',arm=f'offline_{win}',d_final=x['star']['d'],passed=x['star_passed'],all_pass=x['star_all_pass'],
            case_pass=x['star_case_pass'],feasible=fe,in_feasible_final=bool(fe is not None and fe[0]<x['star']['d']<fe[1]),eps_vs_offline_full_1000s_mV=None))
    if save_hist is not None:save_hist[row['seed']]=hist
    return recs,rep,repro_v7

def main():
    OUT.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    B=json.loads((V/'shared_readout_20261120/bounds.json').read_text());params=B['points']
    raw=[json.loads(l) for l in (V/'motifs/order_v2/confirm.jsonl').read_text().splitlines()]
    dtmin=min(r['dt'] for r in raw);seedrows={r['seed']:r for r in raw if r['dt']==dtmin and not r['control']};assert len(seedrows)==40
    d163={r['seed']:r for r in json.loads((V/'order_long_calibration/streams.json').read_text())}
    branches={}
    for b in json.loads((V/'order_balance_information/branches.json').read_text()):branches.setdefault(b['seed'],[]).append(b)
    d168={}
    for l in (V/'calibration_precision_20261120/d/records.jsonl').read_text().splitlines():
        x=json.loads(l)
        if x['weight']=='w':d168.setdefault(x['seed'],{})[x['window'],x['mode']]=x
    check=dict(schedules_identical=True,pulses_rebuilt=True,max_A_B_W_error=0.,max_node7_repro_error_V=0.)
    status=dict(completed=[],stopped=None);fh=(OUT/'records.jsonl').open('x');hists={}
    for seed in sorted(seedrows):
        r,events=make_long_stream(seedrows[seed],10.,2)
        if events!=d163[seed]['events']:check['schedules_identical']=False;raise RuntimeError(f'{seed} schedule differs')
        if pulses_of(events)!=r['pulses']:check['pulses_rebuilt']=False;raise RuntimeError(f'{seed} pulse rebuild differs')
        recs,rep,rv=one(r,events,branches[seed],DT,d168[seed],params,str(seed),save_hist=hists)
        for win,x in rep.items():
            o=d168[seed][win,'raw'];check['max_A_B_W_error']=max(check['max_A_B_W_error'],abs(x['A_Vs']-o['A_Vs']),abs(x['B_Vs']-o['B_Vs']),abs(x['W_s']-o['W_s']))
        check['max_node7_repro_error_V']=max(check['max_node7_repro_error_V'],rv)
        for x in recs:fh.write(json.dumps(x)+'\n')
        fh.flush();status['completed'].append(seed);el=time.monotonic()-start
        print('seed',seed,'elapsed',round(el,1),'ABW err',check['max_A_B_W_error'],'node7',rv,flush=True)
        if el>BUDGET-400:status['stopped']=f'budget guard after {seed}';break
    fh.close();np.savez_compressed(OUT/'histories_1s.npz',**{f'{s}|{k}':v for s,h in hists.items() for k,v in h.items()})
    check['gate_A_B_W']=bool(check['max_A_B_W_error']<=1e-12);check['gate_node7']=bool(check['max_node7_repro_error_V']<=1e-12)
    # refinement
    ref=[]
    if status['stopped'] is None:
        coarse={}
        for l in (OUT/'records.jsonl').read_text().splitlines():
            x=json.loads(l)
            if x['seed'] in SEEDS_FINE:coarse[x['seed'],x['point'],x['arm']]=x
        for seed in SEEDS_FINE:
            prev={k[1:]:v for k,v in coarse.items() if k[0]==seed}
            for dt in (.00025,.000125):
                if time.monotonic()-start>BUDGET-120:status['stopped']=f'budget guard before refinement {seed} {dt}';break
                r,events=make_long_stream(seedrows[seed],10.,2);recs,_,rv=one(r,events,branches[seed],dt,d168[seed],params,f'{seed}_dt{dt}')
                cur={(x['point'],x['arm']):x for x in recs}
                for k,x in cur.items():
                    y=prev[k];row=dict(seed=seed,point=k[0],arm=k[1],dt=[y['dt'],dt],d_final=[y['d_final'],x['d_final']],d_change=abs(x['d_final']-y['d_final']),
                        classes_identical=bool(x['case_pass']==y['case_pass']))
                    if 'eps_vs_offline_full_1000s_mV' in x and x['eps_vs_offline_full_1000s_mV'] is not None:
                        row['eps_change_mV']=max(abs(x['eps_vs_offline_full_1000s_mV']-y['eps_vs_offline_full_1000s_mV']),abs(x['eps_vs_offline_final_third_1000s_mV']-y['eps_vs_offline_final_third_1000s_mV']))
                    row['ok']=bool(row['d_change']<.001 and row['classes_identical'] and row.get('eps_change_mV',0)<1.)
                    ref.append(row)
                prev=cur;check['max_node7_repro_error_V_fine']=max(check.get('max_node7_repro_error_V_fine',0.),rv)
                print('refined',seed,dt,round(time.monotonic()-start,1),flush=True)
    (OUT/'refinement.json').write_text(json.dumps(ref,indent=1)+'\n')
    status['refinement']=dict(rows=len(ref),all_ok=bool(ref) and all(x['ok'] for x in ref),max_d_change=max((x['d_change'] for x in ref),default=None),
        max_eps_change_mV=max((x.get('eps_change_mV',0) for x in ref),default=None))
    # diagnostic input controls (labels build the inputs in the harness only)
    ctl=[]
    if status['stopped'] is None:
        for seed in SEEDS_FINE:
            r0,events=make_long_stream(seedrows[seed],10.,2)
            for name,keep in (('no_input',[]),('ordered_only',[e for e in events if category(e['case'])!='simultaneous']),('simultaneous_only',[e for e in events if category(e['case'])=='simultaneous'])):
                if time.monotonic()-start>BUDGET-30:status['stopped']=f'budget guard before control {seed} {name}';break
                r=copy.deepcopy(r0);r['pulses']=pulses_of(keep);assert all(p in r0['pulses'] for p in r['pulses'])
                recs,_,_=one(r,keep,branches[seed],DT,d168[seed],params,f'{seed}_{name}')
                for x in recs:
                    x['control']=name;x['events_kept']=len(keep)
                    x.pop('d_at_events',None);ctl.append(x)
                print('control',seed,name,round(time.monotonic()-start,1),flush=True)
    (OUT/'controls.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in ctl))
    status.update(checks=check,elapsed_s=time.monotonic()-start,gate_passed=bool(check['schedules_identical'] and check['gate_A_B_W'] and check['gate_node7'] and status['refinement']['all_ok'] and status['stopped'] is None))
    (OUT/'status.json').write_text(json.dumps(status,indent=2)+'\n');print(json.dumps(status,indent=1))
if __name__=='__main__':main()

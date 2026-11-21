"""D172: rest-closure versus useful-sensitivity bounds for the steering-gate contract, from census.npz only (no trajectory).

Monte Carlo over gate offsets g1, g2 ~ N(0, (30 mV)^2), mirror imbalances alpha, beta ~ N(0, 0.1^2) (correlation rho), the
reading pair's offset e ~ N(0, (30 mV)^2), for each designed threshold V_theta. Linearised knob writer current per unit
k_w I0 (CONTRACT.md §2 of D170): shared i = (1+a/2) w1 (1+T)/2 - (1-a/2) w2 (1-T)/2; separate i = w1 (T_w + a/2).
Rest: V6 at its quiet level (+ 0, 3 mV, or the per-draw worst upstream leakage, which judges safety), T from the tracker's null; a write fires if |i| > DEAD.
Anchors: knob sensitivity sum(w*der) relative to the engine's clipped gate at threshold 0 (D170's nominal).
Gate-edge bias of the knob's zero: eps_g = -(F1 - F2)/(s (F1 + F2)), F_i the life's event integral of w_i (rest is inside
the dead band), against the D170 budget: sqrt(10^2 - 6.9^2) = 7.2 mV.
Writes lab/v/gate_contract_20261120/bound.json (exclusive create).
"""
import json,math,sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT))
import chip
from units import V_TYP,MISMATCH,R_MAX,TAU_MAX
OUT=ROOT/'lab/v/gate_contract_20261120'
P=json.loads((ROOT/'lab/v/shared_readout_20261120/bounds.json').read_text())['points']
M=4000;SIG_G=MISMATCH*V_TYP;DESIGN=np.round(np.arange(0.,.3501,.005),4);REST_OFFSETS=(0.,.003,'upstream')
BUDGET_EDGE_mV=math.sqrt(10**2-6.9**2)

def sig(x):return 1/(1+np.exp(-chip.NATIVE*x))

def main():
    z=np.load(OUT/'census.npz');TH=z['TH'];seeds=[int(s) for s in z['seeds']];cats=list(z['cats'])
    C=json.loads((OUT/'census.json').read_text())['scalars']
    interp=lambda arr,x:np.interp(x,TH,arr)       # arr over the TH grid; x clipped to the grid by np.interp
    rng=np.random.default_rng([172,1])
    # worst resting V6 if the coincidence element's upstream gate were fully open at rest: its sigmoid's tail into node 6's leak
    raw=[json.loads(l) for l in (ROOT/'lab/v/motifs/order_v2/confirm.jsonl').read_text().splitlines()]
    dtmin=min(r['dt'] for r in raw);rows={r['seed']:r for r in raw if r['dt']==dtmin and not r['control']};up={}
    for sd,rw in rows.items():
        n=np.array(rw['nodes']);el=np.array(rw['elements']);j=[j for j in range(el.shape[1]) if rw['links'][0][j]==6][0]
        up[sd]=float(el[0,j]/(1+np.exp(-el[2,j]*(0-el[1,j])))/n[1,6])
    res=dict(design_thresholds_V=DESIGN.tolist(),M=M,sigma_g_V=SIG_G,budget_edge_mV=BUDGET_EDGE_mV,points={})
    for pname,p in P.items():
        s=p['slope_per_V'];G=p['loop_gain_G'];kwI0=p['k_w']*p['I0_A'];Cd=p['C_d_F']
        rate_per_unit=kwI0/(Cd*V_TYP)               # d per second per unit of (|i| - DEAD)
        rows=[]
        for rho in (0.,.5):
            g=rng.standard_normal((len(seeds),M,2))*SIG_G;e=rng.standard_normal((len(seeds),M))*SIG_G;eq=rng.standard_normal((len(seeds),M))*SIG_G
            a0=rng.standard_normal((len(seeds),M));b0=rho*a0+math.sqrt(1-rho*rho)*rng.standard_normal((len(seeds),M))
            al,be=MISMATCH*a0,MISMATCH*b0
            for law in ('sigmoid','clip'):
                F=lambda arr,th: interp(arr,th)
                for Vt in DESIGN:
                    r=dict(point=pname,rho=rho,law=law,V_theta=float(Vt))
                    # --- rest
                    for off in REST_OFFSETS:
                        writes=np.zeros((len(seeds),M),bool);writes_sep=writes.copy();drift=np.zeros((len(seeds),M));drift_sep=drift.copy()
                        for k,sd in enumerate(seeds):
                            sc=C[str(sd)];x=sc['qmax']+(up[sd] if off=='upstream' else off)                    # worst quiet sample
                            th1=Vt+g[k,:,0];th2=Vt+g[k,:,1]
                            if law=='sigmoid':w1,w2=sig(x-th1),sig(x-th2)
                            else:w1,w2=np.clip((x-th1)/V_TYP,0,1),np.clip((x-th2)/V_TYP,0,1)
                            # tracker null at rest (shared): (1+b/2)(1-w1)(1+T) = (1-b/2)(1-w2)(1-T), plus its leak residual
                            A=(1+be[k]/2)*(1-w1);B=(1-be[k]/2)*(1-w2);T=(B-A)/(A+B)+s*(sc['u_quiet_mean']-e[k])/G
                            i=(1+al[k]/2)*w1*(1+T)/2-(1-al[k]/2)*w2*(1-T)/2
                            over=np.maximum(np.abs(i)-chip.DEAD,0);writes[k]=over>0;drift[k]=over*rate_per_unit*sc['quiet_s']
                            Tw=np.tanh(s*(eq[k]-e[k]))+0*T                     # separate: its tracker nulls its own pair
                            i2=w1*(Tw+al[k]/2);over2=np.maximum(np.abs(i2)-chip.DEAD,0);writes_sep[k]=over2>0;drift_sep[k]=over2*rate_per_unit*sc['quiet_s']
                        tag='rest_offset_upstream_worst' if off=='upstream' else f'rest_offset_{off*1e3:g}mV'
                        r[tag]=dict(p_write_shared=float(writes.mean()),p_drift_gt_0p02_shared=float((drift>.02).mean()),
                            p_write_separate=float(writes_sep.mean()),p_drift_gt_0p02_separate=float((drift_sep>.02).mean()))
                    # --- anchors and selectivity at nominal offsets
                    key='Es' if law=='sigmoid' else 'Ec';bkey='EBs' if law=='sigmoid' else 'EBc'
                    ratios_w=[];ratios_b=[];peaks=[];draw_b=[];share_anchor=[];share_near=[];share_anchor_nom=[]
                    for sd in seeds:
                        cat=z[f'{sd}|cat'];pk=z[f'{sd}|peak'];Ew=z[f'{sd}|{key}'];EB=z[f'{sd}|{bkey}'];E0=z[f'{sd}|Ec'];EB0=z[f'{sd}|EBc']
                        j0=int(np.argmin(np.abs(TH-0.)))
                        for ev in np.nonzero(cat==0)[0]:
                            nom=E0[ev,j0];ratios_w.append(F(Ew[ev],Vt)/nom if nom>0 else np.nan);peaks.append(pk[ev])
                            nb=EB0[ev,j0];ratios_b.append(F(EB[ev],Vt)/nb if abs(nb)>1e-12 else np.nan)
                        anc=cat==0;bt=sum(F(EB[ev],Vt) for ev in np.nonzero(anc)[0]);bn=sum(EB0[ev,j0] for ev in np.nonzero(anc)[0])
                        draw_b.append(bt/bn if abs(bn)>1e-12 else np.nan)
                        tot=sum(F(Ew[ev],Vt) for ev in range(len(cat)));near=sum(F(Ew[ev],Vt) for ev in np.nonzero((cat==1)|(cat==2))[0])
                        share_anchor.append(sum(F(Ew[ev],Vt) for ev in np.nonzero(anc)[0])/tot if tot>0 else np.nan);share_near.append(near/tot if tot>0 else np.nan)
                        tot0=E0[:,j0].sum();share_anchor_nom.append(E0[anc,j0].sum()/tot0)
                    peaks=np.array(peaks);rw=np.array(ratios_w);rb=np.array(ratios_b)
                    p5=np.percentile(peaks,5);weak=np.argsort(np.abs(peaks-p5))[:5]
                    r['anchors']=dict(n=len(peaks),peak_p5_mV=float(p5*1e3),weakest_ratio_w=float(np.nanmedian(rw[weak])),weakest_ratio_b=float(np.nanmedian(rb[weak])),
                        share_anchors_ratio_w_ge_0p5=float(np.nanmean(rw>=.5)),median_draw_ratio_b=float(np.nanmedian(draw_b)),min_draw_ratio_b=float(np.nanmin(draw_b)),
                        anchor_share_of_W_median=float(np.nanmedian(share_anchor)),near_share_of_W_median=float(np.nanmedian(share_near)),anchor_share_nominal_clip_median=float(np.median(share_anchor_nom)))
                    # --- gate-edge bias over the life's events (shared arm), with mirror term for the total
                    eps=np.zeros((len(seeds),M))
                    for k,sd in enumerate(seeds):
                        Ew=z[f'{sd}|{key}'].sum(axis=0)                       # total event integral of w over the TH grid
                        F1=np.interp(Vt+g[k,:,0],TH,Ew);F2=np.interp(Vt+g[k,:,1],TH,Ew)
                        eps[k]=np.where(F1+F2>0,-(F1-F2)/(s*np.maximum(F1+F2,1e-30)),0.)
                    mirror=(be-al)/(2*s)
                    r['edge_bias_mV']=dict(sd=float(eps.std()*1e3),p95_abs=float(np.percentile(np.abs(eps),95)*1e3),
                        total_with_mirror_rms=float(np.sqrt(np.mean((eps+mirror)**2))*1e3))
                    off3=r['rest_offset_upstream_worst'];an=r['anchors']
                    r['safe']=bool(off3['p_write_shared']<=.01 and off3['p_drift_gt_0p02_shared']<=.01)
                    r['useful']=bool(an['weakest_ratio_w']>=.5 and an['median_draw_ratio_b']>=.5 and r['edge_bias_mV']['sd']<=BUDGET_EDGE_mV)
                    rows.append(r)
        res['points'][pname]=rows
        for law in ('sigmoid','clip'):
            for rho in (0.,.5):
                ok=[x['V_theta'] for x in rows if x['law']==law and x['rho']==rho and x['safe'] and x['useful']]
                safe=[x['V_theta'] for x in rows if x['law']==law and x['rho']==rho and x['safe']]
                use=[x['V_theta'] for x in rows if x['law']==law and x['rho']==rho and x['useful']]
                print(pname,law,'rho',rho,'safe from',min(safe,default=None),'useful',(min(use,default=None),max(use,default=None)),'overlap',(min(ok,default=None),max(ok,default=None)),flush=True)
                res.setdefault('ranges',{})[f'{pname}|{law}|rho{rho}']=dict(safe=[min(safe,default=None),max(safe,default=None)],useful=[min(use,default=None),max(use,default=None)],
                    overlap=[min(ok,default=None),max(ok,default=None)],n_overlap=len(ok))
    with (OUT/'bound.json').open('x') as f:json.dump(res,f,indent=1)
if __name__=='__main__':main()

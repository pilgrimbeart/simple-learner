"""D168 Task A: how precise must the order calibration's readout be? Saved rows only, no trajectories.

For every saved setting, the exact region of one fixed readout error e (volts) under which
d(e)=clip((e*W-A)/B,-1,1) satisfies all 34 original cases (strict), computed by D167's unchanged
functions (lab/calibration_next_20261120/t2_readout_error.py: case_interval, d_region, e_region).
Expected adequate count for e~N(0,sigma^2) by exact Gaussian integration, over the frozen grid
sigma in {0,1,2,3,5,7.5,10,15,20,30} mV, for every window, mode and weight.
  set 'D165_histories': D167 task 2's 1920 rows (80 histories x 6 windows x 4 modes, weight w).
  set 'D163_schedules': D167 task 1's 640 records (40 draws x 2 weights x 2 windows x 4 modes);
                        for the w*w observer W is the integral of w^2, stored as W_s on its 'w2' rows.
Required precision: the largest grid sigma whose expected count reaches 90% / 95% of the zero-error count
(a requirement, not an achievement). A finer scan (0.05 mV steps) is reported as a supplement only.
Gates: the 30 mV points reproduce D167 exactly; D164's 240 rows reproduce; draw 2215 has probability 0.
"""
import json,math,sys,time
from pathlib import Path
from statistics import NormalDist
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'lab/calibration_next_20261120'));sys.path.insert(0,str(ROOT/'lab'));sys.path.insert(0,str(ROOT))
from t2_readout_error import case_interval,d_region,e_region,reproduce_d164
V=ROOT/'lab/v';OUT=V/'calibration_precision_20261120/a';N=NormalDist()
GRID_MV=[0,1,2,3,5,7.5,10,15,20,30];FINE_MV=[round(.05*k,2) for k in range(0,1201)]
INFEASIBLE=2026112215
def mass(iv,sig):
    """Gaussian mass of the open interval iv for e~N(0,sig^2); sig=0 is the indicator of 0 in iv."""
    if iv is None:return 0.
    lo,hi=iv
    if sig==0:return 1. if lo<0<hi else 0.
    return (N.cdf(hi/sig) if math.isfinite(hi) else 1.)-(N.cdf(lo/sig) if math.isfinite(lo) else 0.)
def required(curve,zero,frac):
    ok=[s for s,c in curve if c>=frac*zero-1e-12]
    return max(ok) if ok else None
def main():
    t0=time.monotonic();OUT.mkdir(parents=True,exist_ok=False)
    branches={}
    for b in json.loads((V/'order_balance_information/branches.json').read_text()):branches.setdefault(b['seed'],[]).append(b)
    caps={r['seed']:r for r in json.loads((V/'order_balance_information/draws.json').read_text())}
    feas={r['seed']:r for r in json.loads((V/'overnight_20261119/failures_results/feasible_intervals.json').read_text())}
    gate=dict(d164=reproduce_d164(caps,branches))
    def region(seed,A,B,W):
        lo,hi,empty=case_interval(branches[seed]);feasible=not empty and feas[seed]['coincidence_all']
        if B==0 or W<=0:raise ValueError('degenerate B or W')
        return feasible,(e_region(A,B,W,d_region(lo,hi)) if feasible else None)
    rows=[]
    t2=[json.loads(l) for l in (V/'calibration_next_20261120/t2/rows.jsonl').read_text().splitlines()];assert len(t2)==1920
    max30=0.;regerr=0.
    for r in t2:
        f,iv=region(r['seed'],r['A_Vs'],r['B_Vs'],r['W_s'])
        old=tuple(r['error_region_V']) if r['error_region_V'] else None
        if (iv is None)!=(old is None):raise SystemExit('region existence differs from D167')
        if iv:regerr=max(regerr,abs(iv[0]-old[0]) if math.isfinite(old[0]) else 0.,abs(iv[1]-old[1]) if math.isfinite(old[1]) else 0.)
        p30=mass(iv,.03);max30=max(max30,abs(p30-r['conditional_success']))
        rows.append(dict(set='D165_histories',seed=r['seed'],replicate=r['replicate'],weight='w',window=r['window'],mode=r['mode'],A_Vs=r['A_Vs'],B_Vs=r['B_Vs'],W_s=r['W_s'],
            feasible_draw=f,error_region_V=list(iv) if iv else None,P={str(s):mass(iv,s/1000) for s in GRID_MV}))
    t1=[json.loads(l) for l in (V/'calibration_next_20261120/t1b/records.jsonl').read_text().splitlines()];assert len(t1)==640
    zero_vs_saved=[]
    for r in t1:
        assert r['identifiable']
        f,iv=region(r['seed'],r['A_Vs'],r['B_Vs'],r['W_s'])
        z=bool(iv is not None and iv[0]<0<iv[1])
        if z!=bool(r['all_pass']):zero_vs_saved.append([r['seed'],r['weight'],r['window'],r['mode']])
        rows.append(dict(set='D163_schedules',seed=r['seed'],replicate=0,weight=r['weight'],window=r['window'],mode=r['mode'],A_Vs=r['A_Vs'],B_Vs=r['B_Vs'],W_s=r['W_s'],
            feasible_draw=f,error_region_V=list(iv) if iv else None,P={str(s):mass(iv,s/1000) for s in GRID_MV}))
    # gate: 30 mV group sums against D167's summary
    s167=json.loads((V/'calibration_next_20261120/t2/summary.json').read_text())['by_window_mode'];sumerr=0.
    for k,v in s167.items():
        w,m=k.split('|');sumerr=max(sumerr,abs(sum(x['P']['30'] for x in rows if x['set']=='D165_histories' and x['window']==w and x['mode']==m)-v['expected_successes']))
    p2215=max(max(x['P'].values()) for x in rows if x['seed']==INFEASIBLE)
    gate.update(max_row_error_30mV=max30,max_group_error_30mV=sumerr,max_region_error_V=regerr,zero_error_vs_saved_all_pass_mismatches=zero_vs_saved,
        draw_2215_max_probability=p2215,valid=bool(gate['d164']['valid'] and max30==0. and sumerr<1e-9 and regerr==0. and not zero_vs_saved and p2215==0.))
    print('gate',json.dumps(gate),flush=True)
    if not gate['valid']:
        (OUT/'gate_failed.json').write_text(json.dumps(gate,indent=1)+'\n');raise SystemExit('reproduction gate failed; not interpreted')
    with (OUT/'rows.jsonl').open('x') as fh:
        for x in rows:fh.write(json.dumps(x)+'\n')
    table=[]
    groups=sorted({(x['set'],x['weight'],x['window'],x['mode']) for x in rows})
    for g in groups:
        rr=[x for x in rows if (x['set'],x['weight'],x['window'],x['mode'])==g]
        curve=[(s,sum(x['P'][str(s)] for x in rr)) for s in GRID_MV];zero=curve[0][1]
        regions=[tuple(x['error_region_V']) if x['error_region_V'] else None for x in rr]
        fine=[(s,sum(mass(iv,s/1000) for iv in regions)) for s in FINE_MV]
        table.append(dict(set=g[0],weight=g[1],window=g[2],mode=g[3],n=len(rr),zero_error=zero,expected={str(s):c for s,c in curve},
            fraction_of_zero_error={str(s):(c/zero if zero else None) for s,c in curve},
            required_sigma_mV_90=required(curve,zero,.90),required_sigma_mV_95=required(curve,zero,.95),
            fine_scan_sigma_mV_90=required(fine,zero,.90),fine_scan_sigma_mV_95=required(fine,zero,.95)))
    summary=dict(grid_mV=GRID_MV,gate=gate,table=table,elapsed_s=time.monotonic()-t0)
    (OUT/'summary.json').write_text(json.dumps(summary,indent=1)+'\n')
    for t in table:print(t['set'],t['weight'],t['window'],t['mode'],'n',t['n'],'zero',t['zero_error'],'@30',round(t['expected']['30'],2),'req90',t['required_sigma_mV_90'],'req95',t['required_sigma_mV_95'],'fine90/95',t['fine_scan_sigma_mV_90'],t['fine_scan_sigma_mV_95'])
    print('elapsed',round(time.monotonic()-t0,2))
if __name__=='__main__':main()

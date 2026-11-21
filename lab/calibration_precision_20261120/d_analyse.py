"""D168 Task D (analysis part): saved d/records.jsonl only.

1. Settings at zero shared error (shared e cancels exactly): self-referenced d* scored on all 34 old cases for all
   40 draws (2215 kept), with paired draw- and case-level rescues/harms against D167's setting on the same record.
2. The term that remains, -(W/Q) Aq (the quiet-time residual, i.e. the baseline's own error), against A.
3. Independent error between the two accumulations: with two physically separate readings, A* gains W*(e_w - e_q);
   e_eff = e_w - e_q enters exactly as e did in Task A, so its region is D167's function applied to (A*, B*, W).
   Exact Gaussian expected adequate counts at the Task A grid and at the Task B sigmas (passed on the command line,
   in mV, as name=value), next to D167's single-error counts at the same sigma.
"""
import json,math,sys
from pathlib import Path
from statistics import NormalDist
ROOT=Path(__file__).resolve().parents[2]
for p in [ROOT,ROOT/'lab',ROOT/'lab/calibration_next_20261120']:sys.path.insert(0,str(p))
from t2_readout_error import case_interval,d_region,e_region
V=ROOT/'lab/v';D=V/'calibration_precision_20261120/d';N=NormalDist()
GRID=[0,1,2,3,5,7.5,10,15,20,30]
def mass(iv,sig):
    if iv is None:return 0.
    lo,hi=iv
    if sig==0:return 1. if lo<0<hi else 0.
    return (N.cdf(hi/sig) if math.isfinite(hi) else 1.)-(N.cdf(lo/sig) if math.isfinite(lo) else 0.)
def main():
    extra={k:float(v) for k,v in (a.split('=') for a in sys.argv[1:])}
    st=json.loads((D/'status.json').read_text())
    if not st['gate_passed']:raise SystemExit('Task D gate failed: not interpreted')
    R=[json.loads(l) for l in (D/'records.jsonl').read_text().splitlines()];assert len(R)==640
    branches={}
    for b in json.loads((V/'order_balance_information/branches.json').read_text()):branches.setdefault(b['seed'],[]).append(b)
    feas={r['seed']:r for r in json.loads((V/'overnight_20261119/failures_results/feasible_intervals.json').read_text())}
    def region(seed,A,B,W):
        lo,hi,empty=case_interval(branches[seed]);f=not empty and feas[seed]['coincidence_all']
        return e_region(A,B,W,d_region(lo,hi)) if f else None
    sig=dict({f'grid_{g}mV':g for g in GRID},**extra);groups={}
    rows=[]
    for x in R:
        assert x['star']['identifiable']
        ivs=region(x['seed'],x['A_star_Vs'],x['B_star_Vs'],x['W_s']);ivo=region(x['seed'],x['A_Vs'],x['B_Vs'],x['W_s'])
        row=dict(seed=x['seed'],weight=x['weight'],window=x['window'],mode=x['mode'],d167_d=x['d167_d'],d_star=x['star']['d'],clipped=x['star']['clipped'],
            d167_all_pass=x['d167_all_pass'],star_all_pass=x['star_all_pass'],d167_passed=x['d167_passed'],star_passed=x['star_passed'],
            case_rescues=sum(b and not a for a,b in zip(x['d167_case_pass'],x['star_case_pass'])),case_harms=sum(a and not b for a,b in zip(x['d167_case_pass'],x['star_case_pass'])),
            quiet_term_Vs=x['ratio_W_Q']*x['Aq_Vs'],A_Vs=x['A_Vs'],quiet_term_over_A=(x['ratio_W_Q']*x['Aq_Vs']/x['A_Vs'] if x['A_Vs'] else None),
            quiet_term_per_W_mV=1000*x['ratio_W_Q']*x['Aq_Vs']/x['W_s'],ratio_W_Q=x['ratio_W_Q'],
            region_star_V=list(ivs) if ivs else None,region_d167_V=list(ivo) if ivo else None,
            P_star={k:mass(ivs,v/1000) for k,v in sig.items()},P_d167={k:mass(ivo,v/1000) for k,v in sig.items()})
        rows.append(row);groups.setdefault((x['weight'],x['window'],x['mode']),[]).append(row)
    with (D/'analysis_rows.jsonl').open('w') as f:
        for r in rows:f.write(json.dumps(r)+'\n')
    table=[]
    for (w,win,m),rr in sorted(groups.items()):
        assert len(rr)==40
        qa=sorted(abs(r['quiet_term_per_W_mV']) for r in rr)
        table.append(dict(weight=w,window=win,mode=m,draws=40,
            d167_adequate=sum(r['d167_all_pass'] for r in rr),star_adequate=sum(r['star_all_pass'] for r in rr),
            d167_cases=sum(r['d167_passed'] for r in rr),star_cases=sum(r['star_passed'] for r in rr),
            draw_rescues=[r['seed'] for r in rr if r['star_all_pass'] and not r['d167_all_pass']],draw_harms=[r['seed'] for r in rr if r['d167_all_pass'] and not r['star_all_pass']],
            case_rescues=sum(r['case_rescues'] for r in rr),case_harms=sum(r['case_harms'] for r in rr),clipped=sum(r['clipped'] for r in rr),
            quiet_term_per_W_mV_median_abs=qa[20],quiet_term_per_W_mV_max_abs=qa[-1],
            expected_star={k:sum(r['P_star'][k] for r in rr) for k in sig},expected_d167={k:sum(r['P_d167'][k] for r in rr) for k in sig}))
    out=dict(sigmas_mV=sig,table=table,note='star: self-referenced; P_star at sigma = independent error e_w-e_q of that SD; P_d167 = D167 single error of that SD')
    (D/'analysis.json').write_text(json.dumps(out,indent=1)+'\n')
    for t in table:
        print(t['weight'],t['window'],t['mode'],'adequate d167/star',t['d167_adequate'],t['star_adequate'],'cases',t['d167_cases'],t['star_cases'],'rescue/harm draws',t['draw_rescues'],t['draw_harms'],
              'cases +',t['case_rescues'],'-',t['case_harms'],'quiet/W med|max mV',round(t['quiet_term_per_W_mV_median_abs'],2),round(t['quiet_term_per_W_mV_max_abs'],2))
        print('   ',{k:(round(t['expected_star'][k],2),round(t['expected_d167'][k],2)) for k in sig if not k.startswith('grid_') or k in('grid_10mV','grid_30mV')})
if __name__=='__main__':main()

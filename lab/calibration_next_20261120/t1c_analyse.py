"""D167 task 1, part C: analyse t1b's rows (no new trajectories). Writes t1b/analysis.json and prints a summary."""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];V=ROOT/'lab/v/calibration_next_20261120';T=V/'t1b'
CATS=['simultaneous','positive_near','negative_near','far','single','carry_in'];IDENT=1e-12
def main():
    R=[json.loads(l) for l in (T/'records.jsonl').read_text().splitlines()];st=json.loads((T/'status.json').read_text())
    key={(r['seed'],r['weight'],r['window'],r['mode']):r for r in R}
    seeds=sorted({r['seed'] for r in R});modes=sorted({r['mode'] for r in R},key=lambda m:(m!='raw',float(m) if m!='raw' else 0));wins=['full_1000s','final_third_1000s']
    out=dict(records=len(R),expected_records=640,seeds=len(seeds),status=st,groups={},paired={},concentration={})
    for wt in ['w','w2']:
        for win in wins:
            for m in modes:
                rr=[key[s,wt,win,m] for s in seeds]
                sim_share=[r['categories']['simultaneous']['B_Vs']/r['B_Vs'] for r in rr if abs(r['B_Vs'])>IDENT]
                pull=[-(r['A_Vs']-r['categories']['simultaneous']['A_Vs'])/r['B_Vs'] for r in rr if abs(r['B_Vs'])>IDENT]
                out['groups'][f'{wt}|{win}|{m}']=dict(all_pass=sum(bool(r.get('all_pass')) for r in rr),cases_passed=sum(r.get('passed',0) for r in rr),of_draws=len(rr),of_cases=34*len(rr),
                    unidentifiable=sum(not r['identifiable'] for r in rr),clipped=sum(bool(r['clipped']) for r in rr),nonpositive_B=sum(r['B_Vs']<=0 for r in rr),
                    failing_seeds=[r['seed'] for r in rr if not r.get('all_pass')],
                    sim_B_share_median=float(np.median(sim_share)),sim_B_share_range=[min(sim_share),max(sim_share)],
                    nonsim_pull_median=float(np.median(pull)),nonsim_pull_range=[min(pull),max(pull)],
                    mean_W_s=float(np.mean([r['W_s'] for r in rr])),mean_W2_s=float(np.mean([r['W2_s'] for r in rr])),
                    mean_B_share={c:float(np.mean([r['categories'][c]['B_Vs']/r['B_Vs'] for r in rr])) for c in CATS},
                    mean_W_share={c:float(np.mean([r['categories'][c]['W_s']/r['W_s'] for r in rr])) for c in CATS},
                    mean_pull={c:float(np.mean([-r['categories'][c]['A_Vs']/r['B_Vs'] for r in rr])) for c in CATS})
            for m in modes:
                a=[key[s,'w',win,m] for s in seeds];b=[key[s,'w2',win,m] for s in seeds]
                resc=[x['seed'] for x,y in zip(a,b) if y.get('all_pass') and not x.get('all_pass')];harm=[x['seed'] for x,y in zip(a,b) if x.get('all_pass') and not y.get('all_pass')]
                cr=sum(sum(q and not p for p,q in zip(x['case_pass'],y['case_pass'])) for x,y in zip(a,b));ch=sum(sum(p and not q for p,q in zip(x['case_pass'],y['case_pass'])) for x,y in zip(a,b))
                out['paired'][f'{win}|{m}']=dict(draws_rescued_by_w2=resc,draws_harmed_by_w2=harm,cases_rescued=cr,cases_harmed=ch,
                    d_w_2227=key[2026112227,'w',win,m]['d'],d_w2_2227=key[2026112227,'w2',win,m]['d'],
                    weight_retained_W2_over_W=float(np.median([y['W_s']/x['W_s'] for x,y in zip(a,b)])),
                    B_retained_median=float(np.median([y['B_Vs']/x['B_Vs'] for x,y in zip(a,b)])))
    # concentration of weight per event category: simultaneous share of integrated weight under w vs w2
    for win in wins:
        r0=[key[s,'w',win,'raw'] for s in seeds];r1=[key[s,'w2',win,'raw'] for s in seeds]
        out['concentration'][win]=dict(sim_share_of_W_w=float(np.median([r['categories']['simultaneous']['W_s']/r['W_s'] for r in r0])),
            sim_share_of_W_w2=float(np.median([r['categories']['simultaneous']['W_s']/r['W_s'] for r in r1])),
            posnear_share_of_W_w=float(np.median([r['categories']['positive_near']['W_s']/r['W_s'] for r in r0])),
            posnear_share_of_W_w2=float(np.median([r['categories']['positive_near']['W_s']/r['W_s'] for r in r1])))
    # 2227 per category, both weights, final third, tau .15
    out['seed_2227']={f'{wt}|{win}|{m}':dict(d=key[2026112227,wt,win,m]['d'],all_pass=key[2026112227,wt,win,m].get('all_pass'),passed=key[2026112227,wt,win,m].get('passed'),
        categories={c:dict(A=v['A_Vs'],B=v['B_Vs'],W=v['W_s'],n=v['n'],alone_d=(-v['A_Vs']/v['B_Vs'] if abs(v['B_Vs'])>IDENT else None)) for c,v in key[2026112227,wt,win,m]['categories'].items()})
        for wt in ['w','w2'] for win in wins for m in modes}
    iv=T/'intervention.json'
    if iv.exists():
        I=json.loads(iv.read_text());rows=I['anchor_intervals']
        out['intervention']=dict(kept=I['kept_events'],removed=I['removed_events'],
            anchor_rows=[dict(start=r['interval_start_s'],case=r['case'],final_third=r['in_final_third'],weight=r['weight'],mode=r['mode'],
                A_orig=r['original']['A_Vs'],A_removed=r['removed_nonsimultaneous']['A_Vs'],B_orig=r['original']['B_Vs'],B_removed=r['removed_nonsimultaneous']['B_Vs'],
                W_orig=r['original']['W_s'],W_removed=r['removed_nonsimultaneous']['W_s'],d_orig=r['original']['d'],d_removed=r['removed_nonsimultaneous']['d']) for r in rows],
            window_settings={f"{r['weight']}|{r['window']}|{r['mode']}":dict(d=r['d'],all_pass=r.get('all_pass'),passed=r.get('passed')) for r in I['window_records']})
        a=out['intervention']['anchor_rows']
        out['intervention']['max_rel_change_A']={f'{wt}|{m}':max(abs(x['A_removed']-x['A_orig'])/abs(x['A_orig']) for x in a if x['weight']==wt and x['mode']==m) for wt in ['w','w2'] for m in modes}
        out['intervention']['max_abs_change_d']={f'{wt}|{m}':max(abs(x['d_removed']-x['d_orig']) for x in a if x['weight']==wt and x['mode']==m) for wt in ['w','w2'] for m in modes}
    rf=T/'refinement.json'
    if rf.exists():
        ref=json.loads(rf.read_text());out['refinement']=dict(rows=len(ref),all_ok=bool(ref) and all(r['ok'] for r in ref),max_d_change=max((r['d_change'] for r in ref),default=None),failures=[r for r in ref if not r['ok']])
    (T/'analysis.json').write_text(json.dumps(out,indent=1)+'\n')
    for k,v in out['groups'].items():print(k,{x:v[x] for x in ['all_pass','cases_passed','failing_seeds','sim_B_share_median','nonsim_pull_median','mean_W_s','clipped']})
    for k,v in out['paired'].items():print(k,v)
    print(json.dumps(out['concentration'],indent=1));print(json.dumps(out.get('refinement'),indent=1))
    if 'intervention' in out:print(json.dumps({k:out['intervention'][k] for k in ['max_rel_change_A','max_abs_change_d','window_settings']},indent=1))
if __name__=='__main__':main()

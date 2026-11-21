"""D167 task 1, part A (saved rows only, no trajectories).
1. Reproduce D165's 40-history event-contribution sums (against D163's saved final-third integrals) and
   2026112227's anchor-only / all-event settings (against D165's aggregate rows).
2. Contamination accounting: for every component and the four observation modes, A, B, W contributed by
   simultaneous, positive-near, negative-near, far and single events, carry-in separate. Arithmetic
   attribution on fixed trajectories, not deletion of events. Ratios only for identifiable denominators.
"""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'lab'))
from overnight_20261119_support import setting,score_branches
V=ROOT/'lab/v';OUT=V/'calibration_next_20261120/t1a'
CATS=['simultaneous','positive_near','negative_near','far','single','carry_in']
IDENT=1e-12
def category(x):
    if x['kind']=='near':return 'positive_near' if x['delay_s']>0 else 'negative_near'
    return x['kind']
def decompose(parts,modes):
    """parts: {cat:{'A':{m:..},'B':{m:..},'W':..}}. Returns per-mode decomposition d_all = sum_k (B_k/B) d_k."""
    out={}
    for m in modes:
        A=sum(parts[c]['A'][m] for c in CATS);B=sum(parts[c]['B'][m] for c in CATS)
        cat={}
        for c in CATS:
            a,b=parts[c]['A'][m],parts[c]['B'][m]
            cat[c]=dict(A_Vs=a,B_Vs=b,B_share=(b/B if abs(B)>IDENT else None),alone_raw_d=(-a/b if abs(b)>IDENT else None),
                pull_on_raw_d=(-a/B if abs(B)>IDENT else None))   # signed contribution of this category to raw d = -A/B
        nonsim_A=sum(parts[c]['A'][m] for c in CATS if c!='simultaneous');nonsim_B=sum(parts[c]['B'][m] for c in CATS if c!='simultaneous')
        out[m]=dict(A_Vs=A,B_Vs=B,raw_d=(-A/B if abs(B)>IDENT else None),categories=cat,
            nonsimultaneous=dict(A_Vs=nonsim_A,B_Vs=nonsim_B,B_share=(nonsim_B/B if abs(B)>IDENT else None),pull_on_raw_d=(-nonsim_A/B if abs(B)>IDENT else None)),
            cancellation=dict(sum_abs_category_A_Vs=sum(abs(parts[c]['A'][m]) for c in CATS),abs_total_A_Vs=abs(A)))
    return out
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    ev=[json.loads(l) for l in (V/'overnight_20261119/attribution_results/event_contributions.jsonl').read_text().splitlines()]
    agg={(a['seed'],a['mode'],a['aggregate']):a for a in map(json.loads,(V/'overnight_20261119/attribution_results/aggregate_settings.jsonl').read_text().splitlines())}
    d163={r['seed']:r for r in json.loads((V/'order_long_calibration/streams.json').read_text())}
    d163draws={(r['seed'],r['mode']):r for r in json.loads((V/'order_long_calibration/draws.json').read_text())}
    branches={}
    for b in json.loads((V/'order_balance_information/branches.json').read_text()):branches.setdefault(b['seed'],[]).append(b)
    feas={r['seed']:r for r in json.loads((V/'overnight_20261119/failures_results/feasible_intervals.json').read_text())}
    modes=list(next(iter(ev))['A_Vs'].keys());seeds=sorted({x['seed'] for x in ev});assert len(seeds)==40 and len(modes)==4
    checks=dict(max_sum_error_Vs=0.,max_knob_error=0.,max_2227_error=0.,intervals=len(ev))
    rows=[]
    for s in seeds:
        xs=[x for x in ev if x['seed']==s]
        for m in modes:
            A=sum(x['A_Vs'][m] for x in xs);B=sum(x['B_Vs'][m] for x in xs);oa,ob=d163[s]['observations_Vs'][m]
            checks['max_sum_error_Vs']=max(checks['max_sum_error_Vs'],abs(A-oa),abs(B-ob))
            checks['max_knob_error']=max(checks['max_knob_error'],abs(setting(A,B)['d']-d163draws[s,m]['d']))
        parts={c:dict(A={m:0. for m in modes},B={m:0. for m in modes},W=0.,n=0,duration_s=0.) for c in CATS}
        for x in xs:
            c=category(x);parts[c]['W']+=x['W_s'];parts[c]['n']+=1;parts[c]['duration_s']+=x['duration_s']
            for m in modes:parts[c]['A'][m]+=x['A_Vs'][m];parts[c]['B'][m]+=x['B_Vs'][m]
        dec=decompose(parts,modes);Wt=sum(parts[c]['W'] for c in CATS)
        rows.append(dict(seed=s,window='final_third_1000s',weight='w',feasible_interval=feas[s]['interval'],order_feasible=feas[s]['order_feasible'],
            W_s=Wt,categories={c:dict(n_intervals=parts[c]['n'],duration_s=parts[c]['duration_s'],W_s=parts[c]['W'],W_share=parts[c]['W']/Wt if Wt>0 else None) for c in CATS},modes=dec))
    # 2227: anchor-only and all-event settings
    r27={}
    for m in modes:
        xs=[x for x in ev if x['seed']==2026112227]
        for name,sel in [('all',xs),('simultaneous_only',[x for x in xs if x['kind']=='simultaneous'])]:
            A=sum(x['A_Vs'][m] for x in sel);B=sum(x['B_Vs'][m] for x in sel);st=setting(A,B);o=agg[2026112227,m,name]
            checks['max_2227_error']=max(checks['max_2227_error'],abs(st['d']-o['d']),abs(A-o['A_Vs']),abs(B-o['B_Vs']))
            sc=score_branches(branches[2026112227],st['d'])
            r27[f'{m}|{name}']=dict(A_Vs=A,B_Vs=B,d=st['d'],passed=sum(x['passed'] for x in sc),all_pass=all(x['passed'] for x in sc),saved_d=o['d'],saved_all_pass=o['all_pass'])
    checks['valid']=checks['max_sum_error_Vs']<1e-12 and checks['max_knob_error']<1e-9 and checks['max_2227_error']<1e-12
    # summaries across seeds
    summ={}
    for m in modes:
        ok=[r for r in rows if r['modes'][m]['B_Vs']>IDENT]
        summ[m]=dict(identifiable=len(ok),of=len(rows),
            nonsim_B_share_range=[min(r['modes'][m]['nonsimultaneous']['B_share'] for r in ok),max(r['modes'][m]['nonsimultaneous']['B_share'] for r in ok)],
            nonsim_pull_range=[min(r['modes'][m]['nonsimultaneous']['pull_on_raw_d'] for r in ok),max(r['modes'][m]['nonsimultaneous']['pull_on_raw_d'] for r in ok)],
            mean_pull_by_category={c:sum(r['modes'][m]['categories'][c]['pull_on_raw_d'] for r in ok)/len(ok) for c in CATS},
            mean_B_share_by_category={c:sum(r['modes'][m]['categories'][c]['B_share'] for r in ok)/len(ok) for c in CATS},
            positive_near_alone_d_range=[min(v for v in (r['modes'][m]['categories']['positive_near']['alone_raw_d'] for r in ok) if v is not None),max(v for v in (r['modes'][m]['categories']['positive_near']['alone_raw_d'] for r in ok) if v is not None)])
    out=dict(checks=checks,seed_2227=r27,summary=summ)
    (OUT/'contamination_rows.json').write_text(json.dumps(rows,indent=1)+'\n');(OUT/'summary.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=1))
    if not checks['valid']:raise SystemExit('Reproduction failed')
if __name__=='__main__':main()

"""Task E (overnight 2026-11-19): information and precision summary from Tasks C and D (small arithmetic).
Descriptive counts on a selected set; no bit count, no new learner.
"""
import hashlib,json,math,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];V=ROOT/'lab/v';BASE=V/'overnight_20261119'
def fresh(name):
    for n in [name,name+'_retry1',name+'_retry2']:
        if not (BASE/n).exists():(BASE/n).mkdir();return BASE/n
    raise RuntimeError('No retry directory left')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def latest(name):
    c=[BASE/n for n in [name+'_retry2',name+'_retry1',name] if (BASE/n).exists()];return c[0] if c else None
P_SIM=4/34

def main():
    OUT=fresh('information_results');res={};notes=[]
    C=latest('attribution_results');D=latest('histories_results')
    cvalid=C is not None and json.loads((C/'attribution_checks.json').read_text()).get('valid') and (C/'aggregate_settings.jsonl').exists()
    dvalid=D is not None and (D/'settings.jsonl').exists()
    res['inputs']=dict(task_c=str(C) if C else None,task_c_valid=bool(cvalid),task_d=str(D) if D else None,task_d_complete=bool(dvalid))
    feas={r['seed']:r for r in json.loads((BASE/'failures_results/feasible_intervals.json').read_text())}
    res['infeasible_draws']={str(s):dict(interval=f['interval'],note='no constant setting meets all 34 conditions; more evidence cannot create one') for s,f in feas.items() if not f['any_setting_suffices']}
    # ---- Task C: existing 40 histories, final third
    if cvalid:
        agg=[json.loads(l) for l in (C/'aggregate_settings.jsonl').read_text().splitlines()];A={(a['seed'],a['mode'],a['aggregate']):a for a in agg}
        seeds=sorted({a['seed'] for a in agg});modes=sorted({a['mode'] for a in agg},key=lambda m:(m!='raw',m))
        nsim={s:sum(1 for a in agg if a['seed']==s and a['mode']=='raw' and a['aggregate'].startswith('leave_out_')) for s in seeds}
        res['C']={m:dict(histories=len(seeds),no_anchor=sum(nsim[s]==0 for s in seeds),
            anchor_present_all_window_fail=sorted(s for s in seeds if nsim[s]>0 and not A[s,m,'all'].get('all_pass')),
            anchor_present_anchor_only_fail=sorted(s for s in seeds if nsim[s]>0 and A[s,m,'simultaneous_only'].get('status')=='scored' and not A[s,m,'simultaneous_only']['all_pass']),
            anchor_only_pass=sum(bool(A[s,m,'simultaneous_only'].get('all_pass')) for s in seeds),all_window_pass=sum(bool(A[s,m,'all'].get('all_pass')) for s in seeds),
            other_only_pass=sum(bool(A[s,m,'other_only'].get('all_pass')) for s in seeds)) for m in modes}
    else:notes.append('Task C outputs unavailable or invalid; its attribution is not used.')
    # ---- Task D: 80 new histories
    if dvalid:
        S=[json.loads(l) for l in (D/'settings.jsonl').read_text().splitlines()]
        windows=list(dict.fromkeys(r['window'] for r in S));modes=list(dict.fromkeys(r['mode'] for r in S));seeds=sorted({r['seed'] for r in S})
        K={(r['seed'],r['replicate'],r['mode'],r['window']):r for r in S};hist=sorted({(r['seed'],r['replicate']) for r in S})
        ok=lambda r:bool(r['status']=='scored' and r['all_pass'])
        res['D_completed']=dict(histories=len(hist),settings=len(S),expected_histories=80,expected_settings=1920)
        # 1. anchors
        q1={}
        for w in windows:
            for m in modes:
                rr=[K[h+(m,w)] for h in hist]
                q1[f'{m}|{w}']=dict(no_anchor=sum(r['simultaneous_in_window']==0 for r in rr),no_anchor_pass=sum(ok(r) for r in rr if r['simultaneous_in_window']==0),
                    one_anchor=sum(r['simultaneous_in_window']==1 for r in rr),one_anchor_fail=sum(not ok(r) for r in rr if r['simultaneous_in_window']==1),
                    multi_anchor_one_case=sum(r['simultaneous_in_window']>=2 and r['distinct_simultaneous_cases']==1 for r in rr),
                    multi_anchor_one_case_pass=sum(ok(r) for r in rr if r['simultaneous_in_window']>=2 and r['distinct_simultaneous_cases']==1),
                    multi_case=sum(r['distinct_simultaneous_cases']>=2 for r in rr),multi_case_pass=sum(ok(r) for r in rr if r['distinct_simultaneous_cases']>=2),
                    unidentifiable=sum(r['status']!='scored' for r in rr),all_pass=sum(ok(r) for r in rr),
                    failures_on_infeasible_draw=sum(not ok(r) for r in rr if not feas[r['seed']]['any_setting_suffices']))
        res['D_anchors']=q1
        # 2. keeping earlier observations: paired against the frozen reference windows
        pairs=[('last_third_1000s','full_1000s'),('last_third_1000s','prefix_666.6666666666666s'),('last_third_1000s','prefix_833.3333333333334s'),('first_100s_last_third','full_100s'),('first_100s_last_third','last_third_1000s')]
        q2={};rng_seed=126
        for ref,alt in pairs:
            for m in modes:
                a=[ok(K[h+(m,ref)]) for h in hist];b=[ok(K[h+(m,alt)]) for h in hist]
                dd=[]
                for h in hist:
                    x,y=K[h+(m,ref)],K[h+(m,alt)]
                    if x['status']=='scored' and y['status']=='scored':dd.append(abs(y['d']-x['d']))
                per_seed=np.array([[float(ok(K[(s,r,m,alt)]))-float(ok(K[(s,r,m,ref)])) for r in range(8)] for s in seeds])
                idx=np.random.default_rng(rng_seed).integers(0,len(seeds),(4000,len(seeds)));boot=per_seed[idx].mean(axis=(1,2))
                q2[f'{m}|{ref}->{alt}']=dict(reference_pass=sum(a),alternative_pass=sum(b),rescued=sum(y and not x for x,y in zip(a,b)),harmed=sum(x and not y for x,y in zip(a,b)),
                    mean_change_in_pass_fraction=float(per_seed.mean()),cluster_bootstrap95=[float(np.quantile(boot,.025)),float(np.quantile(boot,.975))],
                    interval_note='descriptive, over 10 selected component seeds with all 8 schedules kept together; not confirmation; an interval containing zero is not equivalence',
                    median_abs_d_change=float(np.median(dd)) if dd else None)
        res['D_retention']=q2
        # 3. opportunities vs generator
        q3={}
        for w in windows:
            rr=[K[h+('raw',w)] for h in hist];N=[r['events_in_window'] for r in rr]
            q3[w]=dict(window_seconds=[min(r['window_start_s'] for r in rr),max(r['window_end_s'] for r in rr)],mean_event_starts=float(np.mean(N)),
                observed_no_anchor=sum(r['simultaneous_in_window']==0 for r in rr),expected_no_anchor=float(sum((1-P_SIM)**n for n in N)),
                mean_simultaneous=float(np.mean([r['simultaneous_in_window'] for r in rr])),expected_mean_simultaneous=float(np.mean(N)*P_SIM))
        res['D_opportunities']=q3
    else:notes.append('Task D outputs unavailable; the new schedule experiment is not reported as completed.')
    # opportunities in C (existing 40 histories)
    if cvalid:
        ev=[json.loads(l) for l in (C/'event_contributions.jsonl').read_text().splitlines()];Nc={}
        for e in ev:
            if e['kind']!='carry_in':Nc[e['seed']]=Nc.get(e['seed'],0)+1
        res['C_opportunities']=dict(window='first 0.5 ms sample at or after 666.667 s to 1000 s',mean_event_starts=float(np.mean(list(Nc.values()))),observed_no_anchor=res['C']['raw']['no_anchor'],expected_no_anchor=float(sum((1-P_SIM)**n for n in Nc.values())))
    res['generator']=dict(p_simultaneous=P_SIM,n_for_95pct_one_anchor=math.ceil(math.log(.05)/math.log(1-P_SIM)),note='(1-4/34)^N is the generator probability of no simultaneous event among N starts; not a probability that a circuit learns or passes')
    # 4. D164 fixed-detector limit
    psum=json.loads((V/'order_calibration_precision/summary.json').read_text())
    res['D164']=dict(summary=psum,explanation='A fixed manufacturing offset e in the detector adds e*W to the integral A on every reading; d=(e*W-A)/B. Longer observation grows W, A and B together, so the bias -e*W/B converges to a constant, not to zero. Averaging only reduces error that is independent between readings; one detector read repeatedly supplies the same e every time. The 4- and 16-path rows assume independent paths that are neither built nor costed.')
    res['notes']=notes
    res['input_sha256']={str(p.relative_to(ROOT)):sha(p) for p in [BASE/'failures_results/feasible_intervals.json',V/'order_calibration_precision/summary.json',Path(__file__).resolve()]+([C/'aggregate_settings.jsonl',C/'event_contributions.jsonl'] if cvalid else [])+([D/'settings.jsonl'] if dvalid else [])}
    (OUT/'information_summary.json').write_text(json.dumps(res,indent=2)+'\n')
    # report
    L=['# Task E — information and precision summary','','Descriptive counts on deliberately selected, reused component draws. No bit count: no unknown, prior, likelihood and evidence process has been specified tonight.','']
    for n in notes:L.append(f'**Note:** {n}')
    L+=['## Draw with no possible setting','',*[f"- {s}: allowed interval ({v['interval'][0]:+.4f}, {v['interval'][1]:+.4f}) is empty. It fails in every table below whatever the evidence." for s,v in res['infeasible_draws'].items()],'']
    if cvalid:
        L+=['## Existing 40 histories (D163 schedules), final third','','| mode | no anchor | anchor present but all-window setting fails | anchor-only setting passes | all-window passes | other-intervals-only passes |','|---|---|---|---|---|---|']
        for m,v in res['C'].items():L.append(f"| {m} | {v['no_anchor']}/40 | {v['anchor_present_all_window_fail']} | {v['anchor_only_pass']}/40 | {v['all_window_pass']}/40 | {v['other_only_pass']}/40 |")
        co=res['C_opportunities'];L+=['',f"Opportunities: mean {co['mean_event_starts']:.1f} event starts in the window ({co['window']}); observed no-anchor histories {co['observed_no_anchor']}, generator expectation {co['expected_no_anchor']:.2f}.",'']
    if dvalid:
        L+=['## 80 new development histories (10 selected components × 8 schedules)','',f"Completed {res['D_completed']['histories']}/80 histories, {res['D_completed']['settings']}/1920 settings.",'',
            '### 1. Anchors: absent, single, repeated case, several cases (tau 0.15 s; all modes in JSON)','','| window | no anchor (pass) | one anchor (fail) | ≥2 anchors, one case (pass) | ≥2 cases (pass) | all pass | failures on 2215 |','|---|---|---|---|---|---|---|']
        for w in windows:
            v=res['D_anchors'][f'0.15|{w}'];L.append(f"| {w} | {v['no_anchor']} ({v['no_anchor_pass']}) | {v['one_anchor']} ({v['one_anchor_fail']}) | {v['multi_anchor_one_case']} ({v['multi_anchor_one_case_pass']}) | {v['multi_case']} ({v['multi_case_pass']}) | {v['all_pass']}/80 | {v['failures_on_infeasible_draw']}/8 |")
        L+=['','### 2. Keeping earlier observations (paired on the same 80 histories)','','Both the frozen reference window and the alternative are shown; the frozen result is not replaced.','','| mode | reference → alternative | ref pass | alt pass | rescued | harmed | mean change [95% cluster bootstrap, descriptive] |','|---|---|---|---|---|---|---|']
        for k,v in res['D_retention'].items():
            m,pr=k.split('|');L.append(f"| {m} | {pr} | {v['reference_pass']}/80 | {v['alternative_pass']}/80 | {v['rescued']} | {v['harmed']} | {v['mean_change_in_pass_fraction']:+.3f} [{v['cluster_bootstrap95'][0]:+.3f}, {v['cluster_bootstrap95'][1]:+.3f}] |")
        L+=['','### 3. Opportunities against the generator','','| window | span (s) | mean event starts | no-anchor observed | no-anchor expected (1−4/34)^N | mean anchors observed / expected |','|---|---|---|---|---|---|']
        for w,v in res['D_opportunities'].items():L.append(f"| {w} | {v['window_seconds'][0]:.1f}–{v['window_seconds'][1]:.1f} | {v['mean_event_starts']:.1f} | {v['observed_no_anchor']}/80 | {v['expected_no_anchor']:.2f} | {v['mean_simultaneous']:.2f} / {v['expected_mean_simultaneous']:.2f} |")
    g=res['generator'];L+=['',f"Generator: P(simultaneous) = 4/34; {g['n_for_95pct_one_anchor']} event starts give ≥95% chance of at least one. {g['note']}.",'',
        '## 4. Fixed detector error (D164, reproduced in Task A)','']
    for k in ['0.15:0.5','0.15:0.8']:
        v=psum[k];L.append(f"- tau .15 s, prior {k.split(':')[1]}: zero-error adequate {v['zero_error_adequate']}/40; expected adequate with a new 30 mV-SD detector {v['conditional_expected_adequate_draws']['1']:.2f}; hypothetical 4 / 16 independent paths {v['conditional_expected_adequate_draws']['4']:.2f} / {v['conditional_expected_adequate_draws']['16']:.2f}; narrowest positive symmetric tolerance {v['positive_symmetric_margin_range_V'][0]*1e3:.2f} mV.")
    L+=['',res['D164']['explanation'],'','## Observation, inference, limitations','- Observations: the tables above, on fixed analytic trajectories without circuit noise or rail fading, scored on isolated old cases.',
        '- Inference is limited to what an observer computing −A/B from these windows would select; a physical calibration state, its update rule and its own offsets are not implemented.',
        '- Ten components were deliberately selected (two known failures, lowest eight labels); schedules are new but event families are reused. Counts are descriptive, not population estimates.']
    (OUT/'information_report.md').write_text('\n'.join(L)+'\n');print('\n'.join(L))
if __name__=='__main__':main()

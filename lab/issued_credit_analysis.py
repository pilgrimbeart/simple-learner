"""D82 descriptive checks and counter summaries; no new simulations or selection.

The primary metric and bootstrap live in issued_credit_compare.py. This companion
reports the individual development lives, forecast-timing confound and software
cost proxies so that a change in average reward cannot hide the mechanism.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'lab/v/issued_credit_analysis'


def main():
    p = ROOT/'lab/v/issued_credit_compare.json'
    d = json.loads(p.read_text())
    assert 'failure' not in d, d.get('failure')
    rows = d['lives']
    assert len(rows) == 92
    assert all(x['exact'] for x in d['neutral_checks'])
    assert all(x['behaviour_exact'] for x in d['allfood_checks'])
    source_checks = {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
                     for p,h in d['provenance']['source_sha256'].items()}
    assert all(source_checks.values()), source_checks
    input_checks = {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in d['provenance']['input_sha256'].items()}
    assert all(input_checks.values()), input_checks
    previous = json.loads((ROOT/'lab/v/scoring_feedback.json').read_text())['lives']
    d81_checks=[]
    for row in rows:
        if row['world']=='seq' and row['mode']=='selector' and row['seed']==177000:
            old=next(r for r in previous if r['corrected'] and (r['rule'],r['first'])==(row['rule'],row['first']))
            exact=row['fingerprint']==old['fingerprint'] and row['result']==old['result']
            assert exact
            d81_checks.append(dict(rule=row['rule'],first=row['first'],exact=exact))
    historical = json.loads((ROOT/'lab/v/alloc_confirm.json').read_text())
    seq = [r for r in rows if r['world']=='seq' and r['mode']!='neutral']
    for r in historical['families']['seq']['lives']:
        if r['rule'] in ('none','W'):
            seq.append(dict(r,mode='legacy'))
    idx = {(r['rule'],r['mode'],r['seed'],r['first']):r for r in seq}
    counters = {}
    for world,mode in (('seq','neutral'),('seq','issued'),('allfood','issued')):
        for rule in ('none','W'):
            selected = [r for r in rows if (r['world'],r['mode'],r['rule'])==(world,mode,rule)]
            keys = sorted({k for r in selected for k in r['credit']['counters']})
            sums = {k:sum(r['credit']['counters'].get(k,0) for r in selected) for k in keys}
            counters[f'{world}/{rule}/{mode}'] = dict(lives=len(selected),sum=sums,
                max_reconstruction_error=max(r['credit']['max_reconstruction_error'] for r in selected),
                max_issued_entry_probability_difference=max(r['credit']['max_issued_entry_probability_difference'] for r in selected),
                cache_scalar_slots_per_life=sorted({r['credit']['persistent_cache_scalar_slots'] for r in selected}),
                cache_scalar_writes_per_simulated_second=sums['forecast_scalar_fields_written']/(300*len(selected)))
            if mode=='issued':
                correct=sums.get('delivered_correct_forecasts',0)+sums.get('correct_but_undeliverable_credit',0)
                awake=sums.get('issued_guessed_calls',0)
                counters[f'{world}/{rule}/{mode}']['credit_denominators']=dict(awake_accepted_stream_forecasts=awake,correct_stream_forecasts=correct,
                    incorrect_stream_forecasts=awake-correct,undeliverable_correct_fraction=sums.get('correct_but_undeliverable_credit',0)/correct if correct else None)
            assert sums['accepted_tastes']==sums['completed_accepted_updates']
            assert sums.get('tastes_without_prior_forecast',0)==0
            assert max(r['credit']['max_reconstruction_error'] for r in selected)<=1e-12
    lives = []
    for rule in ('none','W'):
        for seed in d['config']['seeds']:
            for colour in ('red','blue'):
                group = {m:idx[rule,m,seed,colour] for m in ('legacy','selector','issued')}
                lives.append(dict(rule=rule,seed=seed,first=colour,
                    whole_gain={m:r['result'][0] for m,r in group.items()},
                    last_third_gain={m:r['result'][2] for m,r in group.items()},
                    last_third_efficiency={m:r['result'][2]/r['result'][3] for m,r in group.items()},
                    final_units={m:r['final_units'] for m,r in group.items()},
                    issued_matches_selector_result=group['issued']['result']==group['selector']['result'],
                    issued_matches_selector_fingerprint=group['issued']['fingerprint']==group['selector']['fingerprint']))
    signs = {}
    for rule in ('none','W'):
        rr = [r for r in lives if r['rule']==rule]
        for a,b in (('selector','legacy'),('issued','legacy'),('issued','selector')):
            delta = [r['last_third_efficiency'][a]-r['last_third_efficiency'][b] for r in rr]
            signs[f'{rule}: {a} minus {b}'] = dict(positive=sum(x>0 for x in delta),
                zero=sum(x==0 for x in delta),negative=sum(x<0 for x in delta),lives=len(rr))
    resource_activity={}
    for rule in ('none','W'):
        for mode in ('legacy','selector','issued'):
            rr=[idx[rule,mode,seed,c] for seed in d['config']['seeds'] for c in ('red','blue')]
            resource_activity[f'{rule}/{mode}']=dict(lives=len(rr),
                mean_count_recycled=sum(r.get('count_recycled',r['result'][6][3]) for r in rr)/len(rr),
                mean_duplicates=sum(r.get('duplicates',r['result'][6][4]) for r in rr)/len(rr),
                mean_contests=sum(r['alloc']['contests'] for r in rr)/len(rr),
                mean_won_contests=sum(r['alloc']['won'] for r in rr)/len(rr),
                mean_peak_categorical_units=sum(r['alloc']['peak'] for r in rr)/len(rr))
    out = dict(analysis_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),input_checks=input_checks,d81_reproduction_checks=d81_checks,resource_activity=resource_activity,input_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),source_checks=source_checks,
        simulation_wall_s=d['wall_s'],counters=counters,individual_lives=lives,descriptive_signs=signs,
        primary_analysis=d['analysis'],
        limits='Existing development families/seeds; no equivalence or physical-cost claim. Signs are descriptive, not an independence test.')
    BASE.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('individual_lives','source_checks')},indent=2))


if __name__=='__main__':
    main()

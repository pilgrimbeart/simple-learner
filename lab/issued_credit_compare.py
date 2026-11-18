"""D82: existing ten-pair development comparison of three credit contracts.

Historical code and records stay unchanged. Run only after issued_credit.py review:
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python
lab/issued_credit_compare.py > lab/v/issued_credit_compare.log 2>&1
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'lab'),str(ROOT)]
import numpy as np
import alloc_compare as C
from active_mixture_audit import fingerprint
from scoring_feedback import SelectorCredit

SEEDS = list(range(177000,177010))
BASE = ROOT/'lab/v/issued_credit_compare'


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,default=str).encode()).hexdigest()


def one(job):
    world, rule, mode, seed, first = job
    from stage2_lang import arms as S
    import issued_credit as I
    P = 4480 if rule == 'none' else 560
    C.G = 258 if rule == 'none' else 1000
    original_live, original_world = S.live, C.world
    out = {}

    def live(lf, seconds):
        observer = None
        if mode in ('neutral','issued'):
            observer = I.install(lf,enabled=mode=='issued')
        elif mode == 'selector':
            observer = SelectorCredit(lf,True)
        elif mode != 'legacy':
            raise ValueError(mode)
        result = original_live(lf,seconds)
        b = lf.brain
        out.update(fingerprint=fingerprint(lf)[0],
                   behaviour=digest(dict(meals=lf.meals,scored=lf.scored,firings=lf.firings)),
                   accepted=getattr(b,'ntaste',0),births=sum(n.births for n in b.nets),
                   count_recycled=sum(n.fades for n in b.nets),duplicates=sum(n.dups for n in b.nets))
        if mode in ('neutral','issued'):
            out['credit'] = observer.summary() if hasattr(observer,'summary') else dict(observer.counters)
        elif mode == 'selector':
            out['credit'] = dict(affected_tastes=sum(bool(t['changed_scores']) for t in observer.tastes),
                                 same_update_max_error=observer.same_update_max_error)
        return result
    S.live = live
    if world == 'allfood':
        from stage2_lang.worlds import W
        C.world = lambda fam: W['allfood']['text']
    try:
        result = C.one(('seq',rule,P,seed,first))
    finally:
        S.live, C.world = original_live, original_world
    return dict(**result,world=world,mode=mode,**out)


def analyse(lives,history):
    by={(r['rule'],r['mode'],r['seed'],r['first']):r for r in lives if r['world']=='seq' and r['mode']!='neutral'}
    refs={}
    for r in history:
        if r['rule'] in ('circuit','vtold'):
            refs[r['rule'],0,r['seed'],r['first']]=r['result']
        else:
            by[r['rule'],'legacy',r['seed'],r['first']]=r
    getters={(rule,mode):(lambda s,c,rule=rule,mode=mode:by[rule,mode,s,c]['result'])
             for rule in ('none','W') for mode in ('legacy','selector','issued')}
    samples=C.closure_samples(getters,refs,SEEDS)
    values={f'{r}/{m}':C.ci(v) for (r,m),v in samples.items()}
    differences={}
    for rule in ('none','W'):
        for a,b in (('selector','legacy'),('issued','legacy'),('issued','selector')):
            differences[f'{rule}: {a} minus {b}']=C.ci(samples[rule,a]-samples[rule,b])
    for mode in ('legacy','selector','issued'):
        differences[f'{mode}: W minus original']=C.ci(samples['W',mode]-samples['none',mode])
    resources={}
    for rule,mode in getters:
        rows=[by[rule,mode,s,c] for s in SEEDS for c in ('red','blue')]
        resources[f'{rule}/{mode}']=dict(lives=len(rows),final_units_mean=float(np.mean([r['final_units'] for r in rows])),
            whole_gain_mean=float(np.mean([r['result'][0] for r in rows])),
            last_third_gain_mean=float(np.mean([r['result'][2] for r in rows])),
            births_mean=float(np.mean([r.get('births',r['result'][6][2]) for r in rows])),
            grown_mean={f:float(np.mean([r['grown'][f] for r in rows])) for f in C.FAM})
    return dict(closure=values,differences=differences,resources=resources,
                metric='Final-third efficiency gap, paired bootstrap of 10 seed pairs, 2000 samples, RNG 0; development only')


def main():
    start=time.monotonic()
    historical=json.loads((ROOT/'lab/v/alloc_confirm.json').read_text())
    source_paths=('lab/issued_credit_compare.py','lab/issued_credit.py','lab/issued_credit_checks.py',
        'lab/scoring_feedback.py','lab/scoring_order_replay.py','lab/active_mixture_audit.py',
        'lab/alloc_compare.py','lab/alloc_rules.py','lab/grownet.py','lab/teach.py','lab/ladders.py',
        'lab/stage2_lang/seconds.py','lab/stage2_lang/sim.py','discrete/model.py','world.py','units.py')
    # Historical comparison must really be the same unchanged production implementation.
    provenance_checks={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
        for p,h in historical['provenance']['sha256'].items()}
    assert all(provenance_checks.values()),provenance_checks
    out=dict(config=dict(seeds=SEEDS,seconds=300.,dt=.0025,rung=17,arm=C.ARM,workers=4,allfood_seed=142000),
        provenance=dict(revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            dirty=subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True),
            source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in source_paths},
            input_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
                ('lab/v/alloc_confirm.json','lab/v/active_mixture_audit.json','lab/v/scoring_feedback.json')},
            command='OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/issued_credit_compare.py',
            environment={k:os.environ.get(k) for k in ('LB_FINE','LB_LIVE','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')}),
        provenance_checks=provenance_checks,neutral_checks=[],allfood_checks=[],lives=[])
    try:
        old=json.loads((ROOT/'lab/v/active_mixture_audit.json').read_text())['lives']
        d81=json.loads((ROOT/'lab/v/scoring_feedback.json').read_text())['lives']
        with ProcessPoolExecutor(4) as pool:
            controls=[('seq',r,'neutral',177000,c) for r in ('none','W') for c in ('red','blue')]
            for row in pool.map(one,controls):
                out['lives'].append(row)
                h=next(x for x in old if (x['rule'],x['first'])==(row['rule'],row['first']))
                same=row['fingerprint']==h['fingerprint'] and json.loads(json.dumps(row['result']))==h['result']
                out['neutral_checks'].append(dict(rule=row['rule'],first=row['first'],exact=same))
                assert same,out['neutral_checks'][-1]
                print('NEUTRAL PASS',row['rule'],row['first'],flush=True)
            jobs=[('allfood',r,m,142000,c) for r in ('none','W') for m in ('legacy','issued') for c in ('red','blue')]
            for row in pool.map(one,jobs):
                out['lives'].append(row)
                print('ALLFOOD',row['rule'],row['mode'],row['first'],row['result'][:5],flush=True)
            for rule in ('none','W'):
                for colour in ('red','blue'):
                    rows={r['mode']:r for r in out['lives'] if (r['world'],r['rule'],r['first'])==('allfood',rule,colour)}
                    same=rows['legacy']['behaviour']==rows['issued']['behaviour']
                    out['allfood_checks'].append(dict(rule=rule,first=colour,behaviour_exact=same,
                        allocated_units=[rows[m]['final_units'] for m in ('legacy','issued')],
                        births=[rows[m]['births'] for m in ('legacy','issued')]))
                    assert same,out['allfood_checks'][-1]
            jobs=[('seq',r,m,s,c) for r in ('none','W') for m in ('selector','issued') for s in SEEDS for c in ('red','blue')]
            for row in pool.map(one,jobs):
                out['lives'].append(row)
                if row['mode']=='selector' and row['seed']==177000:
                    h=next(x for x in d81 if x['corrected'] and (x['rule'],x['first'])==(row['rule'],row['first']))
                    assert row['fingerprint']==h['fingerprint'] and json.loads(json.dumps(row['result']))==h['result'], 'D81 reproduction'
                print('LIFE',row['rule'],row['mode'],row['seed'],row['first'],
                      'gains',row['result'][0],row['result'][2],'units',row['final_units'],flush=True)
        out['analysis']=analyse(out['lives'],historical['families']['seq']['lives'])
        print(json.dumps(out['analysis'],indent=2),flush=True)
    except Exception as e:
        out['failure']=repr(e)
        raise
    finally:
        out['wall_s']=time.monotonic()-start
        BASE.with_suffix('.json').write_text(json.dumps(out,indent=2,default=str)+'\n')
        print('wall_s',out['wall_s'],flush=True)


if __name__=='__main__':
    main()

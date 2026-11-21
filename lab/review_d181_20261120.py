"""Independent saved-ledger arithmetic audit; no simulation or design selection."""
import gzip, hashlib, json
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
D = ROOT / 'lab/v/catalogue_brain_20261120'
rows = [json.loads(x) for x in gzip.open(D/'action_auth_ledger.jsonl.gz', 'rt')]
jobs = json.loads((D/'action_auth_jobs.json').read_text())['jobs']
key = lambda r: tuple(r[k] for k in ('stage','version','arm','seed','poison','ratio'))
assert len(set(map(key, rows))) == len(rows) == 384
assert set(map(key, rows)) == set(map(key, jobs))
def boot(x):
    x = np.array(x, float)
    bs = x[np.random.default_rng(180).integers(0,len(x),(10000,len(x)))].mean(1)
    return [float(x.mean()), *map(float,np.percentile(bs,[2.5,97.5]))]
def values(arm, metric):
    by = {}
    for r in rows:
        if r['arm'] != arm: continue
        food = sum(c != r['poison'] for t,c in r['meals'] if t*.01 >= 200/3)
        poison = sum(c == r['poison'] for t,c in r['meals'] if t*.01 >= 200/3)
        assert food == r['m']['food_final'] and poison == r['m']['poison_final']
        val = {'food':food*.3, 'net':(food-poison)*.3, 'meals':(food+poison)*.3}[metric]
        by.setdefault(r['seed'],[]).append(val)
    return np.array([np.mean(v) for _,v in sorted(by.items())])
res = {'scope':'Saved meal-ledger arithmetic and hashes; no simulation, live demo or convergence check.', 'rows':len(rows)}
res['arms'] = {a:{m:boot(values(a,m)) for m in ('food','net','meals')} for a in sorted({r['arm'] for r in rows})}
res['contrasts'] = {a:boot(values('informed','net')-values(a,'net')) for a in ('neutral','reversed','no_explore','no_sensory')}
meta=json.loads((D/'action_auth_meta.json').read_text())
res['artifact_hashes']={k:hashlib.sha256(Path(meta[k]).read_bytes()).hexdigest()==meta[k+'_sha256'] for k in ('ledger','archive')}
manifest=json.loads((D/'manifest.json').read_text())
res['frozen_code_hashes']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in manifest['code'].items()}
res['frozen_input_hashes']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==v['sha256'] for p,v in manifest['dirty_inputs'].items()}
res['informed_clipped_lives']=sum(r['clip_steps']>0 for r in rows if r['arm']=='informed')
res['informed_final_food_poison']=[sum(r['m'][k] for r in rows if r['arm']=='informed') for k in ('food_final','poison_final')]
path=ROOT/'lab/v/review_d181_20261120.json'
path.write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps(res,indent=2))

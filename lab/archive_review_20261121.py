"""Independent saved-data review; no simulations or imports of experiment analysis.
Run: OPENBLAS_NUM_THREADS=1 .venv/bin/python lab/archive_review_20261121.py
"""
import collections
import gzip
import hashlib
import json
import subprocess
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'lab/v/action_grid_20261120'
OUT = ROOT / 'lab/v/archive_review_20261121.json'
def digest(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()
def read(p): return json.loads(p.read_text())
def boot(x, q=(2.5,97.5)):
    x=np.asarray(x); rng=np.random.default_rng(182)
    means=x[rng.integers(len(x),size=(10000,len(x)))].mean(axis=1)
    return [float(x.mean()), *np.percentile(means,q).tolist()]
manifest=read(P/'manifest.json'); freeze=read(P/'confirm_freeze.json'); saved=read(P/'confirm_tables.json')
result={'review_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'source_hash_matches':{p:digest(ROOT/p)==h for p,h in manifest['source_sha256'].items()},
        'ledger_hash_matches':{},'counts':{},'primary':{},'convergence':{},'levels':{},'clipping':{},'no_harm':{}}
groups=collections.defaultdict(list); dev=collections.defaultdict(list)
for stage, expected in [('bench',31104),('develop',31104),('confirm',18432)]:
    path=P/f'{stage}_ledger.jsonl.gz'; meta=read(P/f'{stage}_meta.json')
    result['ledger_hash_matches'][stage]=digest(path)==meta['ledger_sha256']
    keys=set(); statuses=collections.Counter(); count=0
    with gzip.open(path,'rt') as f:
        for line in f:
            r=json.loads(line); count+=1; assert r['key'] not in keys; keys.add(r['key']); statuses[r['status']]+=1
            if stage=='bench': continue
            # integer meal counts avoid floating-point ranking tie errors
            meals=[c for tick,c in r['meals'] if 200/3 <= tick*.01 < 100]
            food=sum(c!=r['poison'] for c in meals); bad=len(meals)-food
            vals=[.3*(food-bad),.3*food,.3*(food-3*bad),int(not r['meals'])]
            if stage=='develop': dev[r['config']].append((r['status'],r['arm'],food-bad,food))
            else:
                assert r['seed'] in range(freeze['seeds'][0],freeze['seeds'][1]+1)
                groups[r['config'],r['ratio'],r['arm'],r['seed']].append(vals)
                result['clipping'][r['config']]=result['clipping'].get(r['config'],0)+int(r['clip_steps']>0)
    assert count==expected
    result['counts'][stage]={'rows':count,'unique':len(keys),'status':dict(statuses)}
base,*candidates=freeze['configs']; seeds=range(freeze['seeds'][0],freeze['seeds'][1]+1)
def values(c,r,arm):
    lists=[groups[c,r,arm,s] for s in seeds]
    assert all(len(x)==(1 if 'allfood' in arm else 2) for x in lists)
    return np.array([np.mean(x,axis=0) for x in lists])
rank=[]
for c,rows in dev.items():
    if c!=base and len(rows)==384 and all(x[0]=='ok' for x in rows):
        inf=[x for x in rows if x[1]=='informed']; rank.append((c,sum(x[2] for x in inf),sum(x[3] for x in inf)))
rank.sort(key=lambda x:(-x[1],-x[2],x[0]))
selection=read(P/'selection.json'); result['selection_matches']= [x[0] for x in rank[:3]]==selection['selected']
result['exact_rank_disagreements']=[{'rank':i+1,'exact':x[0],'saved':y} for i,(x,y) in enumerate(zip(rank,selection['ranked'])) if x[0]!=y]
for c in [base,*candidates]:
    for r in (1,2,4):
        v=values(c,r,'informed'); anystrand=sum(max(x[3] for x in groups[c,r,'informed',s]) for s in seeds)
        result['levels'][f'{c}|{r}']={'food':boot(v[:,1]),'food_minus_3poison':boot(v[:,2]),'stranded_seed_count':anystrand}
for c in candidates:
    ds={}
    for r in (1,2,4):
        ds[r]=values(c,r,'informed')[:,0]-values(base,r,'informed')[:,0]
        ci=boot(ds[r],(100*.008333333,100*.991666667))
        ref=saved['primary'][c]['by_ratio'][str(r)]
        result['primary'][f'{c}|{r}']={'ci98_333':ci,'ci95':boot(ds[r]),'saved':ref}
        assert np.allclose(boot(ds[r]),ref['ci95'],atol=1e-12)
    result['no_harm'][c]={str(r):{'allfood_food':boot(values(c,r,'informed_allfood')[:,1]-values(base,r,'informed_allfood')[:,1]), 'stranding':boot(values(c,r,'informed')[:,3]-values(base,r,'informed')[:,3])} for r in (1,2,4)}
    result['convergence'][c]={f'{a}-{b}':boot(ds[a]-ds[b]) for a,b in [(2,1),(4,2)]}
result['script_sha256']=digest(Path(__file__))
OUT.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['primary','levels','source_hash_matches']},indent=2))
print('Changed manifest sources:',[p for p,ok in result['source_hash_matches'].items() if not ok])
print('Wrote',OUT)

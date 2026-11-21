"""Read-only D178 review: reproduce paired reward from committed-format CSV ledgers; no simulations."""
import csv, hashlib, json, subprocess
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'lab/v/robot_action_20261120'
def rows(name):
    with (OUT / 'ledger' / (name + '.csv')).open() as f:
        return list(csv.DictReader(f))
def compare(a, b):
    A, B = rows(a), rows(b)
    def grouped(rs):
        d = {}
        for r in rs:
            d.setdefault(int(r['seed']), []).append((int(r['food_final_third'])-int(r['poison_final_third']))*0.3)
        return {k: np.mean(v) for k,v in d.items()}
    x,y=grouped(A),grouped(B)
    assert x.keys()==y.keys()
    delta=np.array([x[k]-y[k] for k in sorted(x)])
    rng=np.random.default_rng(178)
    bs=delta[rng.integers(0,len(delta),(4000,len(delta)))].mean(1)
    return dict(delta=[float(delta.mean()), *map(float,np.percentile(bs,[2.5,97.5]))],
                stranded=[sum(int(r['stranded']) for r in rs) for rs in (A,B)],
                food_poison=[[sum(int(r[k]) for r in rs) for k in ('food_final_third','poison_final_third')] for rs in (A,B)])
m=json.loads((OUT/'manifest.json').read_text())
result={'revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'hash_checks':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in m['hashes'].items()},
        'bias_vs_baseline':compare('informed_silicon_s0-31_bias-motor-1.3e-09','informed_silicon_s0-31'),
        'learn_vs_frozen':compare('learn_silicon_s0-31','frozen_silicon_s0-31'),
        'allfood_bias_vs_baseline':compare('allfood_silicon_s0-31_bias-motor-1.3e-09','allfood_silicon_s0-31'),
        'scope':'CSV arithmetic and paired seed bootstrap only; no full capture replay or rail measurement replication'}
path=ROOT/'lab/v/review_d178_20261120.json'
path.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))

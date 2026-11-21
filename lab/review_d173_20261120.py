"""Read-only arithmetic/provenance review of D173; no simulation. Prints JSON."""
import hashlib,json
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1]
p=R/'lab/v/noisy_shared_20261120'
rows=[json.loads(l) for l in (p/'records.jsonl').read_text().splitlines()]
keys=[(r['cond'],r['seed'],r['arm']) for r in rows]
assert len(set(keys))==len(keys)
m=json.loads((p/'manifest.json').read_text())
hashes={f:hashlib.sha256((R/f).read_bytes()).hexdigest()==h for f,h in m['hashes'].items()}
a='shared_P2_g250';b='fixed'
by={}
for r in rows:
 if r['cond']=='main':by.setdefault(r['seed'],{})[r['arm']]=r
assert len(by)==100 and all(len(x)==7 for x in by.values())
share=lambda r:r['instream_final']['passed']/r['instream_final']['n']
x=np.array([share(by[s][a])-share(by[s][b]) for s in sorted(by)])
y=np.array([int(by[s][a]['isolated_all_pass'])-int(by[s][b]['isolated_all_pass']) for s in sorted(by)])
i=np.random.default_rng(173).integers(0,100,(10000,100))
fresh=sorted(by)[:4]
out=dict(records=len(rows),unique=True,hash_matches=hashes,main_mean=float(x.mean()),main_ci=np.quantile(x[i].mean(1),[.025,.975]).tolist(),all_pass_delta=int(y.sum()),all_pass_ci=np.quantile(y[i].mean(1),[.025,.975]).tolist(),share_harms=int((x<0).sum()),refinement_draws=[dict(seed=s,effect=share(by[s][a])-share(by[s][b]),isolated_rescue=int(by[s][a]['isolated_all_pass'])-int(by[s][b]['isolated_all_pass'])) for s in fresh],input_sha256={str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [p/'records.jsonl',p/'refine.jsonl',p/'manifest.json']})
print(json.dumps(out,indent=2))

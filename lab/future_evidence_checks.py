"""D84 deterministic history and semantic checks; no simulated life."""
import itertools
import json
from pathlib import Path
import numpy as np
import alloc_compare
import grownet as GN
from future_evidence import definition, write_history, signature, activates, native_expression_fires


def main():
    n=GN.Net('fixture',30,np.random.default_rng(42),prune=False)
    ab=n._add(0,1,2,0.)
    ba=n._add(1,0,2,0.)
    left=n._add(ab,0,3,0.)
    right=n._add(0,ba,3,0.)
    defs={k:definition(x) for k,x in n.units.items()}
    words={}
    for k in defs: signature(defs,k,words)
    assert words[left]==words[right]==(0,1,0)
    evaluations=0
    for values in itertools.product((None,0,1),repeat=5):
        n.hist={i:s for i,s in enumerate(values) if s is not None}
        for i in range(-1,6):
            for k in defs:
                assert n.fires(k,i,{})==activates(words[k],n.hist,i)==native_expression_fires(defs,k,n.hist,i,{})
                evaluations+=1
    n.hist={0:0,GN.HIST:1};shadow=dict(n.hist)
    for i,s,keep in ((GN.HIST,0,True),(GN.HIST,0,False),(GN.HIST+1,1,False),(GN.HIST+1,0,True)):
        old=dict(shadow);changed=write_history(shadow,i,s,keep,GN.HIST)
        n.write(i,s,keep)
        assert shadow==n.hist and changed==(old!=shadow)
    n._remove(ab)
    assert left not in n.units and right in n.units
    assert signature(defs,left,{})==(0,1,0)
    out=dict(passed=True,native_semantic_evaluations=evaluations,checks=['association equivalence','missing history','keep short circuit and truncation','deleted ancestor definitions retained'],simulated_steps=0)
    Path('lab/v/future_evidence_checks.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()

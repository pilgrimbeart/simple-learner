"""D86 fixed confidence control of saved D79 issued mixtures; no simulation."""
import hashlib
import json
import math
from pathlib import Path
import pickle
import time
import numpy as np

RAW=Path('lab/v/active_mixture_audit.pkl')
BASE=Path('lab/v/mixture_confidence')


def score(ps,ys):
    assert len(ps)==len(ys)
    return dict(n=len(ps),log_bits=sum(-math.log2(p if y else 1-p) for p,y in zip(ps,ys)),
        brier_sum=sum((p-y)**2 for p,y in zip(ps,ys)),
        expected_errors=sum(.5 if p==.5 else int((p>.5)!=bool(y)) for p,y in zip(ps,ys)))


def main():
    started=time.monotonic();data=pickle.loads(RAW.read_bytes())
    assert 'failure' not in data and data['config']['seconds']==300.
    lives=[l for l in data['lives'] if l['observe']];assert len(lives)==4
    out=dict(lives=[],checks={},provenance=dict(raw_path=str(RAW.resolve()),raw_sha256=hashlib.sha256(RAW.read_bytes()).hexdigest(),
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),source_provenance=data['provenance'],
        command='timeout 60s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/mixture_confidence.py'),
        limitations=['Four historical uncorrected-credit D79 lives, one reused seed pair, not the D84 corrected life.',
                    'Fixed diagnostic shrinkage, no fitted knob or changed action, learning, allocation or reward.',
                    'Dependent observations; no independent-taste interval or generalisation claim.'])
    maxerr=0.;forecasts=0;labels=0
    for life in lives:
        other=next(l for l in data['lives'] if not l['observe'] and (l['rule'],l['first'])==(life['rule'],life['first']))
        assert life['fingerprint']==other['fingerprint'] and life['result']==other['result']
        ps=life['predictions']
        for p in ps:
            active=np.isfinite(p['q'])
            reconstructed=float(np.dot(p['w'][active],p['q'][active])/p['w'][active].sum())
            err=abs(reconstructed-p['p1']);maxerr=max(maxerr,err);assert err<=1e-12
            forecasts+=1
        accepted=[t for t in life['tastes'] if t['accepted']]
        assert all(t['issued'] is not None and t['letter'] in (0,1) for t in accepted)
        assert all(ps[t['issued']]['t']<=t['t']+1e-10 for t in accepted)
        row=dict(rule=life['rule'],P=life['P'],first=life['first'],seed=life['seed'],fingerprint=life['fingerprint'],windows={})
        for name,lo in (('full',0.),('last_third',200.)):
            tastes=[t for t in accepted if lo<=t['t']<300.]
            probabilities=[ps[t['issued']]['p1'] for t in tastes];ys=[t['letter'] for t in tastes]
            shrunk=[.25+.5*p for p in probabilities]
            assert all((p>.5)==(q>.5) and (p==.5)==(q==.5) for p,q in zip(probabilities,shrunk))
            native,shrink,uniform=score(probabilities,ys),score(shrunk,ys),score([.5]*len(ys),ys)
            assert native['expected_errors']==shrink['expected_errors']
            row['windows'][name]=dict(native=native,halfway=shrink,uniform=uniform,
                halfway_saves_bits=native['log_bits']-shrink['log_bits'],
                halfway_reduces_brier=native['brier_sum']-shrink['brier_sum'])
        labels+=len(accepted);out['lives'].append(row)
    out['checks']=dict(forecasts_reconstructed=forecasts,max_error=maxerr,accepted_labels=labels,
        observed_unobserved_identity=True,all_issued_links_present=True,all_hard_choices_preserved=True)
    out['wall_s']=time.monotonic()-started
    BASE.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':main()

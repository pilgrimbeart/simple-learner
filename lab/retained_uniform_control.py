"""D85 post-result exploratory uniform control from saved per-candidate losses only."""
import hashlib
import json
import math
from pathlib import Path
import pickle
import time
from future_evidence_analysis import distribution

BASE=Path('lab/v/retained_uniform_control')
RAW=Path('lab/v/retained_prediction.pkl')


def mixture_loss(a,b):
    lo,hi=sorted((a,b))
    return lo+1-math.log2(1+2**(-(hi-lo)))


def summarize(rows,key='full'):
    pairs=[(r,r[key]) for r in rows if r[key]['n']]
    def better(a,b):return a < b-1e-10
    return dict(units=len(rows),active=len(pairs),
        retained_beats_uniform=sum(better(s['retained_bits'],s['n']) for r,s in pairs),
        retained_beats_both=sum(better(s['retained_bits'],s['n']) and better(s['retained_bits'],s['baseline_bits']) for r,s in pairs),
        baseline_beats_uniform=sum(better(s['baseline_bits'],s['n']) for r,s in pairs),
        uniform_beats_both=sum(better(s['n'],min(s['baseline_bits'],s['retained_bits'])) for r,s in pairs),
        retained_mix_beats_uniform_mix=sum(better(s['mixture_bits'],mixture_loss(s['baseline_bits'],s['n'])) for r,s in pairs),
        retained_vs_uniform_bits=distribution([s['n']-s['retained_bits'] for r,s in pairs]),
        retained_mix_vs_uniform_mix_bits=distribution([mixture_loss(s['baseline_bits'],s['n'])-s['mixture_bits'] for r,s in pairs]),
        overlapping_sums=dict(uniform_bits=sum(s['n'] for r,s in pairs),
            retained_bits=sum(s['retained_bits'] for r,s in pairs),baseline_bits=sum(s['baseline_bits'] for r,s in pairs),
            retained_mix_bits=sum(s['mixture_bits'] for r,s in pairs),
            uniform_mix_bits=sum(mixture_loss(s['baseline_bits'],s['n']) for r,s in pairs)))


def main():
    start=time.monotonic()
    # Direct sequence likelihoods independently verify log-domain expression.
    for a,b in ((0.,0.),(3.,7.),(1000.,2000.)):
        assert abs(mixture_loss(a,b)-mixture_loss(b,a))<1e-12
        assert mixture_loss(a,b)<=min(a,b)+1
    pbase=[.8,.2,.7];labels=[1,0,0];w=.5;loss=0.
    for p,y in zip(pbase,labels):
        like=p if y else 1-p
        mix=(1-w)*like+w*.5
        loss-=math.log2(mix);w=w*.5/mix
    a=-sum(math.log2(p if y else 1-p) for p,y in zip(pbase,labels))
    assert abs(loss-mixture_loss(a,len(labels)))<1e-12
    data=pickle.loads(RAW.read_bytes());assert not data['summary']['failures']
    rows=data['rows']
    for r in rows:
        for key in ('full','horizon'):
            s=r[key]
            assert abs(s['mixture_bits']-mixture_loss(s['baseline_bits'],s['retained_bits']))<1e-9
    out=dict(full=summarize(rows),horizon_100s=summarize([r for r in rows if r['eligible_100s']],'horizon'),
        by_family={f:summarize([r for r in rows if r['family']==f]) for f in ('event','clock','integrator','rhythm')},
        by_churn={str(c):summarize([r for r in rows if r['same_taste_birth']==c]) for c in (False,True)},
        provenance=dict(raw_sha256=hashlib.sha256(RAW.read_bytes()).hexdigest(),raw_path=str(RAW.resolve()),
            source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            command='timeout 60s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/retained_uniform_control.py'),
        checks=dict(equal_prior_mixture_identity=True,all_saved_mixture_losses_match=True),
        limitations=['Post-result exploratory control; no independent sample or new simulation.',
            'A candidate-specific uniform mixture still uses the candidate activation domain, supplied by its retained definition.',
            'Uniform-mixture cumulative loss is exact; hard-choice counts cannot be recovered from totals.',
            'Overlapping sums are not whole-brain information or a measured calibration decomposition.'],wall_s=time.monotonic()-start)
    BASE.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':main()

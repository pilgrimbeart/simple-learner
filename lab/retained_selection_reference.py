"""D87 supplementary causal deletion-order prior; exact full-sequence likelihood mixture."""
import hashlib
import json
import math
from pathlib import Path
import pickle

RAW=Path('lab/v/retained_mixture_analysis.pkl')
BASE=Path('lab/v/retained_selection_reference')


def ratio(gains):
    n=len(gains)
    return .5+.5/(n+1)+math.fsum(2**g/(2*j*(j+1)) for j,g in enumerate(gains,1))


def main():
    for n in (0,1,10,5369):assert abs(ratio([0.]*n)-1)<1e-12
    assert ratio([1.])==1.25
    assert ratio([-1000.]*100)>.5
    data=pickle.loads(RAW.read_bytes());rows=data['rows'];assert not data['summary']['failures']
    assert [r['death_seq'] for r in rows]==sorted(r['death_seq'] for r in rows)
    gains=[r['full']['retained_saving_bits'] for r in rows]
    actual=ratio(gains);saving=math.log2(actual)
    labels=data['unique_tastes'];native=-math.fsum(math.log2(r['p1'] if r['label'] else 1-r['p1']) for r in labels)
    out=dict(candidates=len(rows),accepted_labels=len(labels),native_log_bits=native,
        selection_reference_log_bits=native-saving,saving_bits=saving,likelihood_ratio=actual,
        default_prior=.5,unborn_prior=.5/(len(rows)+1),largest_candidate_gain=max(gains),
        candidate_prior_formula='1/(2*j*(j+1)), j is one-tally deletion order starting at 1',
        best_gain_minus_prior_cost=max(g-math.log2(2*j*(j+1)) for j,g in enumerate(gains,1)),
        checks=dict(zero_gain_identity=True,one_candidate_identity=True,half_native_bound=saving>=-1),
        provenance=dict(raw_path=str(RAW.resolve()),raw_sha256=hashlib.sha256(RAW.read_bytes()).hexdigest(),
            source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            command='timeout 60s .venv/bin/python lab/retained_selection_reference.py'),
        limitations=['Post-result exploratory supplied deletion-order prior; no alternative priors searched.',
            'Counts each accepted taste once via sequence likelihoods, not a sum of overlapping gains.',
            'Unlimited offline retention; no causal return, locality or resource claim.'])
    BASE.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))


if __name__=='__main__':main()

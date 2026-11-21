"""Counterexamples to D133's local-sensitivity criterion: it is not calibration."""
import copy
from phase_bench import assess,cases

def rows(values):
    return [dict(case=c,mean_V=values[c['phase_index']],cost=dict(rail_hits=0)) for c in cases()]

def main():
    good=rows([.03,.015,0,-.015,-.03,0])
    assert assess(good,False)[0]
    assert not assess(rows([0]*6),False)[0]
    assert assess(rows([0]*6),True)[0]
    assert not assess(rows([-.03,-.015,0,.015,.03,0]),False)[0]
    shifted=copy.deepcopy(good)
    for r in shifted:r['mean_V']+=.2
    assert assess(shifted,False)[0] # Intended: sensitivity passes despite a useless zero crossing.
    bad=copy.deepcopy(good);bad[0]['cost']['rail_hits']=1
    assert not assess(bad,False)[0]
    try:assess(good[:-1],False)
    except AssertionError:pass
    else:raise AssertionError('Incomplete condition set accepted')
    print('7 phase-metric checks passed; explicit offset counterexample preserves claim boundary.')
if __name__=='__main__':main()

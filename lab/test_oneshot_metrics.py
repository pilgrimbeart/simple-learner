"""Manufactured counterexamples for absolute event scoring, not simulator tests."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from oneshot_bench import measure

t=np.arange(0,3,.001)
def trace(pulses,baseline=0.):
    y=np.full(len(t),baseline)
    for at,width,amp in pulses:y[(t>=at)&(t<at+width)]=amp
    return np.column_stack([t,y])
assert measure(trace([(1.01,.05,.6),(2.01,.05,.6)]),[1,2])['passed']
assert not measure(trace([(1.01,.05,.6),(2.01,.05,.6)],.2),[1,2])['passed'], 'quiet baseline must not be subtracted away'
assert not measure(trace([(1.01,1.2,.6)]),[1,2])['passed'], 'sustained input is not a one-shot'
assert not measure(trace([(1.01,.05,.6),(1.2,.05,.6),(2.01,.05,.6)]),[1,2])['passed']
assert not measure(trace([(1.01,.05,.3),(2.01,.05,.3)]),[1,2])['passed']
print('5 manufactured absolute-pulse checks passed')

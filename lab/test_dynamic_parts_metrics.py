"""Manufactured signals check D126 analysis, without running or changing the circuit engine."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import numpy as np
from dynamic_parts_bench import amp, metrics, oscillation, wilson

# Decay fitting must recover a physical time constant, not number of samples.
for spacing in [.001,.0005]:
    t=np.arange(0,2,spacing); end=.214
    x=np.where(t>=end,.25*np.exp(-(t-end)/.05),0.)
    tr=np.column_stack([t,x]); c=dict(shift=.004,rail_hits=0)
    m=metrics('trace',[tr],[c])
    assert m['passed'] and abs(m['values']['tau_s']-.05)<1e-10

# Oscillation measurement ignores a static offset and recovers the period.
t=np.arange(0,100,.001)
x=.15+.2*np.sin(2*np.pi*7*t)
f,cv,a,n=oscillation(t,x,10,45)
assert abs(f-7)<1e-5 and cv<1e-4 and a>.35
assert amp(t,np.full_like(t,.07),10,45)==0

# A fixed voltage is not a rhythm, even though it is nonzero.
flat=np.column_stack([t,np.full_like(t,.07)])
assert not metrics('oscillator',[flat],[dict(shift=.004,rail_hits=0)])['passed']
# A bit that flips to the wrong sign during retention must fail.
x=np.where(t<50,.55,-.55); x[(t>10)&(t<12)]=-.55
assert not metrics('memory',[np.column_stack([t,x])],[dict(shift=.004,rail_hits=0)])['passed']
# The declared sample size supports, but does not force, a 90% reliability claim.
assert wilson(40,40)[0]>.9 and wilson(39,40)[0]<.9
print('5 manufactured-signal checks passed')

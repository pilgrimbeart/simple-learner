"""D73 analytical inventory: reference priors, control differences and reward/noise checks."""
from pathlib import Path
import sys
import json
import math
sys.path[:0]=[str(Path(__file__).resolve().parent),str(Path(__file__).resolve().parents[1])]
import numpy as np
import table
from bits_bank import V7
from drift_filter import Filter

seed=137000
a=table.numbers(seed,{"P":2240})
b={**table.numbers(seed,V7), "bankk":0, "open":0}  # VTold.__init__ overrides
print("Candidate Circuit versus reference VTold parameter differences, seed",seed)
for k in sorted(set(a)|set(b)):
    if a.get(k)!=b.get(k):
        print(k,"candidate",a.get(k),"reference",b.get(k))
f=Filter()
print("Filter: uniform prior over",len(f.hs),"(mean dwell, error) pairs; state prior [0.5,0.5]")
print("mean dwell seconds",np.unique(f.hs).tolist())
print("false-taste probabilities",np.unique(f.qs).tolist())
print("Reference also receives actual eaten colour and sensor wiring via arms.make.tell; no latent state.")
print("VTold disables colour-bank selection/opening, but inherits adaptive pausing and jitter from universal_v.V/universal.U.")
print("The candidate uses story1.Circuit movement; their closed-loop action kernels are not identical.")
print("H2(e) and maximum expected scored gain per meal, with poison penalty 2:")
for e in (.05,.12,.20,.28,.35,.42):
    h=-e*math.log2(e)-(1-e)*math.log2(1-e)
    print(json.dumps(dict(e=e,channel_bits=1-h,best_meal_gain=1-3*e,worst_meal_gain=3*e-2,
                          bits_per_s_at_0_68525_meals=0.68525*(1-h))))
print("For hidden food probability p, P(positive worth)=e+(1-2e)*p.")
print("If forced to choose one of two equally costly colours, choose p>1/2.")
print("If abstention is available, positive expected meal gain requires e+(1-2e)*p>2/3.")
print("At e>=1/3 no p<=1 yields strictly positive expected scored meal gain.")
print("This concerns the existing food-minus-two-poison numerator, not a new survival objective.")

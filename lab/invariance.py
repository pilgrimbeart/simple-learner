"""Is the conversion to 1.2 V behaviour-preserving? HR_31p_pol converted as stored (the body's pulses unchanged, the
pulsed nodes made smaller), against a fully scaled one (pulses x s too, every node's currents x s), per substrate."""
import copy, json, sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import units
import minimal.spec as S
from minimal.designs import rescale
spec0 = json.load(open("/home/pilgrim/git/simple-learner/minimal/results/HR_31p_pol.json"))["spec"]
s = units.V_TYP
mode = sys.argv[1]
if mode == "full":
    import brains.circuit as bc, minimal.fastlife as fl
    fl.STIMULUS, fl.TASTE = bc.STIMULUS * s, bc.TASTE * s
    bc.STIMULUS, bc.TASTE = fl.STIMULUS, fl.TASTE
    sp = copy.deepcopy(spec0)
    for n in sp["nodes"]:
        n[1] *= s
        for j in (4, 5, 6):
            if n[j] is not None: n[j] *= s
    for e in sp["elements"]:
        e[3] *= s; e[4] *= s; e[5] /= s
    sp["volt"] = s
else:
    sp = rescale(spec0)
# score in-process (the pool would re-import fastlife unpatched)
from minimal.spec import one
lives = [one((sp, seed, p, 100.0, True, sb)) for sb in S.JUDGED for seed in range(100, 132) for p in ("red", "blue")]
for sb, v in S.summary(lives)["by_substrate"].items():
    print(mode, sb, f"food {v['food']:.2f} poison {v['poison']:.2f} gain {v['gain']:.2f} eff {v['efficiency']:.2f} stranded {v['stranded']:.0%} power {v['power']*1e9:.1f} nW", flush=True)

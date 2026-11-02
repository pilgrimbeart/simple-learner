"""predict.py: the fast model's prediction for circuit B (cmos.pol, blocksB.KW, vbf 1.1) from its 32-seed bench
(spreadB2/), on the seeds ngspice will live (50000-50031 x 2), written down before the SPICE run."""
import sys, json, glob, pickle, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from concurrent.futures import ProcessPoolExecutor
import cmodel4
from minimal.spec import summary
from discrete.poison import show
D = "/home/pilgrim/git/simple-learner/lab/"
R = [json.loads(open(f).read()) for f in glob.glob(D + "spreadB2/*.json")]
med = lambda k, skip=(): float(np.median([r[k] for r in R if int(r["seed"]) not in skip]))
sdl = lambda k, skip=(): float(np.std(np.log([r[k] for r in R if int(r["seed"]) not in skip])))
sd = lambda k: float(np.std([r[k] for r in R]))
VH, VL, HI = med("V_H"), med("V_L"), 0.8                 # doubt in volts, anchored so that the threshold is HI
P = dict(hold=med("hold"), bored=med("bored"), scan=med("scan"), drive=med("drive"), run=med("run"),
         step=med("step"), fstep=med("fstep", (23,)), drift=med("drift"), hi=HI, conf=VH - HI, top=1.8 - VH + HI,
         flip_reset=1, flip_to=VL - VH + HI, init=VL - VH + HI, lo=-99.0, leak=0.0, cleak=0.0, food_reset=0, vary=1)
cmodel4.SPREAD = dict(hold=sdl("hold"), bored=sdl("bored"), scan=sdl("scan"), drive=sdl("drive"), run=sdl("run"),
                      step=sdl("step"), fstep=sdl("fstep", (23,)), drift=sdl("drift"))
cmodel4.SHIFT = dict(hi=sd("V_H"), flip_to=sd("V_L"))
print("numbers", {k: round(v, 4) for k, v in P.items()})
print("spreads", {k: round(v, 3) for k, v in cmodel4.SPREAD.items()}, {k: round(v, 4) for k, v in cmodel4.SHIFT.items()})
with ProcessPoolExecutor(4) as ex:
    L = cmodel4.lives(P, range(50000, 50032), ex=ex)
    pickle.dump(L, open(D + "v/predB.lives", "wb"))
    print("PREDICTION on 50000-50031 x 2:", show("model of circuit B", summary(L)))
    W = cmodel4.lives(P, range(60000, 60256), ex=ex)
    print("the model on 256 x 2 other seeds (the mean to expect):", show("model of circuit B", summary(W)))
json.dump(P, open(D + "v/predB.json", "w"))

"""trace_life.py SEED POISON: circuit B lived in ngspice, recording each tick's mode (dn, run, q at the tick's end),
firings and sightings, to $S/v/trace_SEED_POISON.json."""
import sys, json, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import cmos
from discrete.life import live
D = "/home/pilgrim/git/simple-learner/lab/"
KW = dict(mirror=1, gain=4, cdq=1.38e-11, counter=1, wbt=0.6, wfast=2, ch=1.6e-11, cb=4.5e-11, runfast=1, vbf=1.1)
import os
KW.update({k: float(v) for k, v in (a.split("=") for a in os.environ.get("POLX", "").split() if a)})
TAG = os.environ.get("TAG", "")
seed, poison = int(sys.argv[1]), sys.argv[2]
seconds = float(sys.argv[3]) if len(sys.argv) > 3 else 100.0
n = cmos.pol(np.random.default_rng(seed + 5_000_011), **KW)
r = live(n, seed, seconds, 1.8, poison=poison, probe=("dn", "run", "q", "dq"), record=True)
json.dump({k: r[k] for k in ("meals", "fired", "seen", "trace", "moving", "firings")},
          open(D + f"v/trace{TAG}_{seed}_{poison}.json", "w"))
print("done", seed, poison, len(r["meals"]))

"""Time one CMOS policy life: timepol.py SECONDS ACCURACY-variant"""
import sys, time
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import cmos  # noqa: F401
from discrete import life
from discrete.poison import _one
secs, variant = float(sys.argv[1]), sys.argv[2]
if variant == "loose":
    life.CHIP_ACCURACY = ".options trtol=7 reltol=1e-3 abstol=1e-12 gmin=1e-15"
t = time.time()
r = _one(("pol", dict(vbpw=1.27, cq=2.5e-12, wbt=0.6, wfast=2), 0, secs, "red"))
print(variant, secs, "s life:", round(time.time() - t, 1), "s computing", r[2] if len(r) > 2 else r)

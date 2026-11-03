"""story1_run2.py: the run the user saw, traced (seed 50206, red as poison): for each run over 60 s, its heading and spin,
the sideways drift per lap of the 60 mm world, how many blocks stayed in the eye's range, and what ended it."""
import math, sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import numpy as np
from creature import Life
from story1 import Gated, M
from units import TICK

seconds = float(sys.argv[1]) if len(sys.argv) > 1 else 30000.0
p, spread = M.from_bench()
q = dict(M.drawn(p, spread, 50206), use=0, trust=1)
lf = Life(50206, "red", brain=lambda s: Gated(s, q))
b = lf.brain
print("drawn: scan", q["scan"], "run", q["run"], "bored", q["bored"], "hold", q["hold"], "poison eye", lf.sensor["red"], flush=True)
start = None
while lf.t < int(seconds / TICK):
    n = len(lf.meals)
    lf.step()
    running = b.t - b.last_drive >= b.p["hold"] and b.t - b.last_food > b.p["bored"]
    if running and start is None:
        start, hs, ss, m0, fl0, fir0 = b.t, [lf.body.heading], [abs(lf.body.spin)], n, len(b.flips), len(lf.firings)
    elif running:
        if lf.t % 10 == 0:
            hs.append(lf.body.heading); ss.append(abs(lf.body.spin))
    elif start is not None:
        d = b.t - start
        if d > 60:
            h = np.array(hs)
            late = h[len(h) // 2:]
            sp = np.linalg.norm(lf.body.speed)
            print(f"run {start:.0f}-{b.t:.0f} s ({d:.0f} s): meals {len(lf.meals) - m0}, flips {len(b.flips) - fl0}; heading {math.degrees(h[0]) % 360:.3f} deg, moved over the run {math.degrees(h.max() - h.min()):.4f} deg; second half {math.degrees(late.max() - late.min()):.6f} deg; "
                  f"largest spin late {max(ss[len(ss) // 2:]):.2e} rad/s; ended by food pulse: {b.last_food == b.t}; pos {lf.body.pos * 1000} mm", flush=True)
            if len(late) > 2:
                hd = late[-1] % (math.pi / 2)
                off = min(hd, math.pi / 2 - hd)
                print(f"   off the world's axis {math.degrees(off):.4f} deg: sideways {60 * math.tan(off):.4f} mm a lap", flush=True)
        start = None
if start is not None:
    print(f"run from {start:.0f} s still going at {b.t:.0f} s; heading {math.degrees(lf.body.heading) % 360:.4f} deg, spin {lf.body.spin:.2e}, meals in it {len(lf.meals) - m0}", flush=True)
print("meals", len(lf.meals), "flips", len(b.flips))

import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner"); sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np, periodbal as PB
from discrete import model as M
p, spread = M.from_bench()
C = dict(cal_every=32.0, cal_len=8.0, stall=0.05, stall_need=3000.0, gate=8.0)
for body, seed in ((1, 50001), (1, 50027), (0, 50001), (0, 50005)):
    l = PB.life(("learn", dict(p, body=body, **C), spread, seed, 2000.0, "red"))
    tr = [(round(t), round(x, 2)) for t, x, n in l.trace if t < 400][::2]
    print(f"body{body} seed {seed}: sweeps {l.sweeps}, balance {l.x:+.2f} vs needed {l.right:+.2f}, food {sum(m>0 for m in [v for _,v in getattr(l,'meals',[])]) if hasattr(l,'meals') else ''}")
    print("   trace (t, balance) every 40 s to 400 s:", tr)

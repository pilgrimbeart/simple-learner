"""drift.py vbf [seed]: doubt's drift at rest after one poison, and the step sizes."""
import sys, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import cmos
from discrete.life import bench
vbf = float(sys.argv[1]); seed = int(sys.argv[2]) if len(sys.argv) > 2 else None
kw = dict(mirror=1, gain=4, cdq=1.38e-11, counter=1, wbt=0.6, wfast=2, ch=1.6e-11, cb=4.5e-11, runfast=1, vbf=vbf, **{k: float(v) for k, v in (a.split("=") for a in sys.argv[3:])})
n = cmos.pol(None if seed is None else np.random.default_rng(seed + 5_000_011), **kw)
t, V, p = bench(n, 6.0, ["dq"], pulses=[("poison", 1.0), ("food", 4.0)], supply=1.8, step=5e-4)
d = V["dq"]; at = lambda x: float(d[np.searchsorted(t, x)])
print(f"vbf {vbf} seed {seed}: poison step {at(1.05) - at(0.95):+.3f} V, food step {at(4.05) - at(3.95):+.3f} V, "
      f"drift {(at(3.9) - at(1.1)) / 2.8 * 1e3:+.1f} mV/s at {at(1.1):.2f} V, power {p * 1e9:.2f} nW", flush=True)

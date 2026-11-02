"""What a circuit does in a life: firings by thruster, while something is seen and not."""
import sys, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from discrete.circuits import CIRCUITS
from discrete.life import live
name = sys.argv[1]; seed = int(sys.argv[2])
params = {k: float(v) for k, v in (a.split("=") for a in sys.argv[3:])}
b, sup = CIRCUITS[name]
r = live(b(np.random.default_rng(seed + 5_000_011), **params), seed, 30.0, sup, probe=("h",) if "h" in str(b(None, **params).lines) else (), record=True)
seen = np.array(r["seen"]) > 0
T = len(seen)
L = np.zeros(T); R = np.zeros(T)
for t, f in r["fired"]:
    (L if f == "left" else R)[t] += 1
for lab, m in (("seen", seen), ("not seen", ~seen)):
    n = m.sum()
    print(f"{lab:9s}: {n/T:4.0%} of ticks; per s: left {L[m].sum()/n*100:5.1f} right {R[m].sum()/n*100:5.1f}  "
          f"ticks with both {((L>0)&(R>0)&m).sum()/n:4.0%}, one only {(((L>0)^(R>0))&m).sum()/n:4.0%}")
print("food", len(r["meals"]), "firings", r["firings"], "power nW", round(r["power"]*1e9))
# a stretch: 60 ticks from the first sighting
i = int(np.argmax(seen[100:])) + 100
print("from tick", i, ":", "".join(("S" if seen[k] else ".") for k in range(i, i + 60)))
print("            left :", "".join(str(int(min(L[k], 9))) for k in range(i, i + 60)))
print("            right:", "".join(str(int(min(R[k], 9))) for k in range(i, i + 60)))

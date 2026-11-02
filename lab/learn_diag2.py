import sys; sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from units import TICK

def one(job):
    from creature import Life
    from discrete.policies import Policy
    kind, p, seed, poison = job
    box = {}
    def mk(s):
        box["p"] = Policy(s, kind, **p); return box["p"]
    lf = Life(seed, poison, brain=mk)
    P = box["p"]
    food_sensor = 1 - lf.sensor[poison]
    c = Counter()
    orig = P.taste
    def taste(value, at):
        state = "roam" if P.t < P.roam_until else ("approach" if P.t - P.last < p["hold"] + 2 * TICK else "scan")
        right = P.on[food_sensor] and not P.on[1 - food_sensor]; c[("blame", value > 0, int(max(range(2), key=lambda i: P.trace[i]) == food_sensor), round(max(P.trace), 0))] += 1
        c[("food" if value > 0 else "poison", state, "right" if right else "wrong")] += 1
        orig(value, at)
    P.taste = taste
    wrong_time = 0
    while lf.t < int(100 / TICK):
        lf.step()
        wrong_time += not (P.on[food_sensor] and not P.on[1 - food_sensor])
    c["wrong_time_s"] = wrong_time * TICK
    return c

p = dict(scan=32, k=8, hold=0.1, learn="toggle", n=2, avoid=2, blame="held", bored=2.0, roam=1.0, roam_rate=80)
if len(sys.argv) > 1: p.update(eval(sys.argv[1]))
with ProcessPoolExecutor(3) as ex:
    tot = Counter()
    for c in ex.map(one, [("reflex_hold", p, s, col) for s in range(7000, 7012) for col in ("red", "blue")]):
        tot.update(c)
for k, v in sorted(tot.items(), key=str):
    print(k, round(v / 24, 2))

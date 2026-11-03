"""story2_stage3.py: unequal thrusters, manual interventions (STORIES.md, 2; lab/story2.py's bodies: each thruster 0.5-2).
   python lab/story2_stage3.py trace    # is the lopsided error curve the scan's speed? the same curve with the scan unscaled
   python lab/story2_stage3.py fixed    # Immunise: random settings of the fixed brain searched on these bodies
   python lab/story2_stage3.py learners # Judge and Sense: D19's jitter against each drive; D20's sweeps, by size of bank
All told the colour, the run's 1 s limit, drive in step; lives of 2,000 s for learners."""
import json, sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from creature import Life
from discrete import model as M
from discrete.bodies import THRUSTERS, draw, vary
from minimal.spec import SPAN, Lived, thirds, summary, efficiency
from story1 import RunLimit
from story2 import factors, paired, line
from units import TICK
import periodbal as PB
import drivebal as DB

SWEEPS = dict(cal_every=32.0, cal_len=8.0, stall=0.05, stall_need=3000.0, gate=8.0, gate_rate=1.0, cal_first=0.0, cal_fast=12.0)


class Plain(RunLimit, M.Model):
    unscaled = False

    def step(self):
        if self.unscaled:
            self.p["scan"] = self.scan0 / self.p["g0"]
        return super().step()


class Sweeps(RunLimit, PB.PeriodBal):
    pass


class Jitter(RunLimit, DB.DriveBal):
    pass


def life(job):
    arm, kw, a, users, e, seed, seconds, poison = job
    p, spread = M.from_bench()
    q = dict(M.drawn(p, spread, seed), run_max=1.0, sync=1, V_H=99.0)
    for k, v in kw.items():
        if k.endswith("_x"):
            q[k[:-2]] = q[k[:-2]] * v
        else:
            q[k] = v
    cls = {"plain": Plain, "unscaled": Plain, "jitter": Jitter}.get(arm) or globals()["Sweeps"]
    lf = Life(seed, poison, brain=lambda s: cls(s, q))
    b = lf.brain
    b.food = 1 - lf.sensor[poison]
    if a is not None or users:
        f = factors(seed, a, users)
        vary(lf, f)
        thr = {m: t for t, m in lf.motor.items()}
        right = float(np.log(f[thr[1]] / f[thr[0]]))
    else:
        right = 0.0
    if arm == "unscaled":
        b.unscaled, b.scan0 = True, q["scan"]
        x = right + e
        b.p["g0"], b.p["g1"] = float(np.exp(x / 2)), float(np.exp(-x / 2))
    ticks = int(round(seconds / TICK))
    while lf.t < ticks:
        lf.step()
    l = Lived(thirds(lf.meals, lf.moving, ticks, poison))
    l.power, l.firings, l.substrate = 3.7e-9, SPAN * len(lf.firings) / seconds, "silicon"
    l.right = right
    l.x = getattr(b, "x", None)
    l.sweeps = getattr(b, "sweeps", 0)
    return l


def run(arm, seeds, kw=None, a=None, users=True, e=0.0, seconds=100.0):
    jobs = [(arm, kw or {}, a, users, e, s, seconds, c) for s in seeds for c in ("red", "blue")]
    with ProcessPoolExecutor(8) as ex:
        return list(ex.map(life, jobs, chunksize=4))


if __name__ == "__main__":
    cmd = sys.argv[1]
    S = range(51000, 51064)
    if cmd == "trace":
        ref = run("unscaled", S, a=1.25, users=False)
        print(f"unscaled scan, x1.25: error 0: {efficiency(ref):.2f}", flush=True)
        for e in (-0.4, -0.2, -0.1, -0.05, 0.05, 0.1, 0.2, 0.4):
            L = run("unscaled", S, a=1.25, users=False, e=e)
            d, i = paired(L, ref)
            print(f"  error {e:+.2f}: {efficiency(L):.2f}, against none {d:+.2f} [{i[0]:+.2f}, {i[1]:+.2f}]", flush=True)
    elif cmd == "fixed":
        rng = np.random.default_rng(1)
        res = []
        for i in range(60):
            kw = {k + "_x": float(3 ** rng.uniform(-1, 1)) for k in ("hold", "bored", "scan", "drive", "run")}
            kw["run_max"] = float(rng.choice([0.5, 1, 2, 5]))
            s = summary(run("plain", range(0, 32), kw))
            res.append((s["efficiency"], s["stranded"], kw))
        res.sort(key=lambda r: -r[0])
        for r in res[:4]:
            print(f"  training {r[0]:.2f} stranded {r[1]:.0%} {json.dumps({k: round(v, 2) for k, v in r[2].items()})}", flush=True)
        base = run("plain", S)
        for r in res[:3]:
            L = run("plain", S, r[2])
            d, i = paired(L, base)
            line(f"held out, {json.dumps({k: round(v, 2) for k, v in r[2].items()})}", L)
            print(f"   against the baseline {d:+.2f} [{i[0]:+.2f}, {i[1]:+.2f}]", flush=True)
    elif cmd == "learners":
        T = range(51000, 51032)
        base = run("plain", T, seconds=2000.0)
        line("baseline", base)
        opt = None
        J = run("jitter", T, dict(learn=1, eta=0.03, sd=0.3, N=1000.0), seconds=2000.0)
        line("D19, jitter judged per drive", J)
        for K in (0, 192, 96, 64, 48, 32, 24, 16):
            kw = dict(SWEEPS)
            if K:
                kw |= dict(bank=float(K), local=1.0, binary=1.0, cap=3.0)
            L = run("sweeps", T, kw, seconds=2000.0)
            x = np.array([l.x for l in L]); r = np.array([l.right for l in L])
            line(f"sweeps, {'exact histogram' if not K else f'{K} counters'}", L)
            print(f"   balance within 0.1 {np.mean(abs(x - r) < 0.1):.0%}, within 0.2 {np.mean(abs(x - r) < 0.2):.0%}; sweeps {np.median([l.sweeps for l in L]):.0f}", flush=True)

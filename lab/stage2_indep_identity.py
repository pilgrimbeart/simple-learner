"""stage2_indep_identity.py: independent check 1 (PROGRAMME.md, gate 2 to 3): with no world rule, the engine
(lab/stage2_lang/sim.WLife) against the real creature.Life, tick by tick, the two lives stepped in lockstep in one
process. Brains built from the existing code only (discrete/model.py; lab/table.py's Circuit and numbers;
lab/universal_v.py's V with lab/v/universal_v7.json). Every brain call is logged by a proxy (stimulate's sensor and
moment, step's motors, taste's value and moment) and every body state compared exactly after every tick.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage2_indep_identity.py [SEEDS]"""
import json
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np

V7 = json.load(open("/home/pilgrim/git/simple-learner/lab/v/universal_v7.json"))


def brain_maker(kind):
    from discrete import model as M
    import table as T
    import universal_v as UV
    if kind == "model":
        p, spread = M.from_bench()
        return lambda s: M.Model(s, M.drawn(p, spread, s))
    if kind == "circuit":
        return lambda s: T.Circuit(s, T.numbers(s, {}))
    if kind == "bank":
        return lambda s: UV.V(s, T.numbers(s, dict(V7)))
    raise ValueError(kind)


class Proxy:
    """Forwards the three-call interface, logging every call. Nothing else is exposed: any other attribute the
    engine asked for would raise (and be reported)."""

    def __init__(self, inner):
        object.__setattr__(self, "_b", inner)
        object.__setattr__(self, "log", [])
        object.__setattr__(self, "n", 0)
        object.__setattr__(self, "other", [])

    def stimulate(self, sensor, at):
        self.log.append(("s", self.n, int(sensor), float(at)))
        self._b.stimulate(sensor, at)

    def taste(self, value, at):
        self.log.append(("t", self.n, float(value), float(at)))
        self._b.taste(value, at)

    def step(self):
        m = self._b.step()
        self.log.append(("m", self.n, tuple(m) if m else ()))
        object.__setattr__(self, "n", self.n + 1)
        return m

    def __getattr__(self, k):
        self.other.append(("get", k))
        return getattr(self._b, k)

    def __setattr__(self, k, v):
        self.other.append(("set", k))
        setattr(self._b, k, v)


def state_life(lf):
    b = lf.body
    return np.concatenate([b.pos, [b.heading, b.spin], b.speed, b.xy.ravel()])


def one(job):
    kind, seed, first, seconds, text = job
    from creature import Life
    from stage2_lang.sim import WLife
    from stage2_lang import lang
    mk = brain_maker(kind)
    world = lang.World(text)
    A = Life(seed, first, brain=lambda s: Proxy(mk(s)))
    B = WLife(seed, first, lambda s: Proxy(mk(s)), world)
    ticks = int(round(seconds / 0.01))
    bad = None
    ia = 0
    for k in range(ticks):
        A.step()
        B.step()
        sa, sb = state_life(A), state_life(B)
        if not np.array_equal(sa, sb):
            bad = ("state", k, float(np.max(np.abs(sa - sb))))
            break
        la, lb = A.brain.log, B.brain.log
        if la[ia:] != lb[ia:]:
            j = next(i for i in range(ia, max(len(la), len(lb))) if i >= len(la) or i >= len(lb) or la[i] != lb[i])
            bad = ("calls", k, la[j] if j < len(la) else None, lb[j] if j < len(lb) else None)
            break
        ia = len(la)
    meals_ok = A.meals == B.meals
    fir_ok = A.firings == B.firings and A.moving == B.moving
    wires_ok = [A.sensor[c] for c in ("red", "blue")] == B.wire_s and [A.motor[t] for t in ("left", "right")] == B.wire_m
    rng_ok = A.rng.bit_generator.state == B.rng.bit_generator.state
    log = A.brain.log
    n = dict(pulses=sum(1 for x in log if x[0] == "s"), tastes=sum(1 for x in log if x[0] == "t"),
             firings=len(A.firings), meals=len(A.meals))
    return dict(kind=kind, seed=seed, first=first, bad=bad, meals_ok=meals_ok, fir_ok=fir_ok, wires_ok=wires_ok,
                rng_ok=rng_ok, other=sorted(set(A.brain.other) | set(B.brain.other)), **n)


def run(jobs, label, workers=7, ex=None):
    if ex is not None:
        R = list(ex.map(one, jobs, chunksize=2))
    else:
        with ProcessPoolExecutor(workers) as ex:
            R = list(ex.map(one, jobs, chunksize=2))
    out = {}
    for kind in sorted(set(r["kind"] for r in R)):
        rs = [r for r in R if r["kind"] == kind]
        ok = [r for r in rs if r["bad"] is None and r["meals_ok"] and r["fir_ok"] and r["wires_ok"] and r["rng_ok"]]
        print(f"{label} {kind}: {len(ok)} of {len(rs)} lives identical tick by tick; calls compared: pulses "
              f"{sum(r['pulses'] for r in rs)}, tastes {sum(r['tastes'] for r in rs)}, firings {sum(r['firings'] for r in rs)}, "
              f"meals {sum(r['meals'] for r in rs)}; lives with no meal {sum(r['meals'] == 0 for r in rs)}; "
              f"attributes the engine touched beyond the interface: {sorted(set(x for r in rs for x in r['other']))}", flush=True)
        for r in rs:
            if r not in ok:
                print("   DIFFERS", r, flush=True)
        out[kind] = (len(ok), len(rs))
    return out


if __name__ == "__main__":
    lo, hi = (int(x) for x in (sys.argv[1] if len(sys.argv) > 1 else "64000:64050").split(":"))
    assert 64000 <= lo < hi <= 65000
    jobs = [(k, s, c, 100.0, "(world)") for k in ("model", "circuit", "bank") for s in range(lo, hi) for c in ("red", "blue")]
    run(jobs, "no rule, 100 s")
    # the instrument must see small differences: each of these must differ in (nearly) every life
    for text in ("(world (const DRAG 50.000001))", "(world (on pulse (if (chance 0.001) (drop))))",
                 "(world (on taste (if (chance 0.01) (set value (- value)))))"):
        run([("circuit", s, c, 100.0, text) for s in range(lo, lo + 10) for c in ("red", "blue")], f"mutant {text}")

"""minbodies.py: the minimal line's leaders in the real creature.Life (silicon), held out (50000-50031 x 2), on
standard bodies and on bodies with each thruster 0.5-2 (bodies.THRUSTERS)."""
import sys, os
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import multiprocessing


def one(job):
    name, seed, poison, body = job
    from creature import Life
    from minimal.spec import SPAN, Lived, make, thirds, load
    from units import TICK
    spec = load(f"minimal/results/{name}.json")
    lf = Life(seed, poison, brain=make(spec, "silicon"))
    if body:
        from discrete.bodies import THRUSTERS, draw, vary
        vary(lf, draw(seed, THRUSTERS))
    ticks = int(round(100.0 / TICK))
    while lf.t < ticks:
        lf.step()
    l = Lived(thirds(lf.meals, lf.moving, ticks, poison))
    l.power = lf.brain.circuit.power()
    l.firings = SPAN * len(lf.firings) / 100.0
    return l


if __name__ == "__main__":
    import pickle
    from minimal.spec import summary
    from discrete.poison import show
    D = "/home/pilgrim/git/simple-learner/lab/m2/"
    with ProcessPoolExecutor(4, mp_context=multiprocessing.get_context("spawn")) as ex:
        for name in ("HR_31p_pol_pruned", "HR_32p_c"):
            for body in (0, 1):
                L = list(ex.map(one, [(name, s, c, body) for s in range(50000, 50032) for c in ("red", "blue")]))
                pickle.dump(L, open(D + f"min_{name}_{body}.lives", "wb"))
                print(show(f"{name} {'varied bodies' if body else 'standard bodies'}", summary(L)), flush=True)

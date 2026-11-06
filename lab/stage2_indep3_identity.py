"""stage2_indep3_identity.py: third independent check, 5. With seconds mode off, the engine against creature.Life, by my predecessor's
instrument (lab/stage2_indep_identity.py: the two lives in lockstep, every brain call logged by a proxy, the body's state compared
exactly after every tick), its `one` repeated here only to pass seconds=False (WLife's default is now seconds mode) and to run with
the instruments on and off. Fresh seeds 69900-69949; planted mutants on 69950-69954.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage2_indep3_identity.py"""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from stage2_indep_identity import Proxy, brain_maker, state_life


def one(job):
    kind, seed, first, seconds, text, inst = job
    from creature import Life
    from stage2_lang.sim import WLife
    from stage2_lang import lang
    WLife.instruments = inst
    mk = brain_maker(kind)
    world = lang.World(text)
    A = Life(seed, first, brain=lambda s: Proxy(mk(s)))
    B = WLife(seed, first, lambda s: Proxy(mk(s)), world, seconds=False)
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
    ok = (bad is None and A.meals == B.meals and A.firings == B.firings and A.moving == B.moving
          and [A.sensor[c] for c in ("red", "blue")] == B.wire_s and [A.motor[t] for t in ("left", "right")] == B.wire_m
          and A.rng.bit_generator.state == B.rng.bit_generator.state)
    log = A.brain.log
    return dict(kind=kind, inst=inst, text=text, ok=ok, bad=bad, pulses=sum(1 for x in log if x[0] == "s"),
                tastes=sum(1 for x in log if x[0] == "t"), firings=len(A.firings), meals=len(A.meals),
                other=sorted(set(A.brain.other) | set(B.brain.other)))


if __name__ == "__main__":
    jobs = [(k, s, c, 100.0, "(world)", inst) for inst in (True, False) for k in ("model", "circuit", "bank")
            for s in range(69900, 69950) for c in ("red", "blue")]
    mutants = ("(world (const DRAG 50.000001))", "(world (on pulse (if (chance 0.001) (drop))))",
               "(world (on meal (if (chance 0.01) (set worth (- worth)))))")
    jobs += [("circuit", s, c, 100.0, m, True) for m in mutants for s in range(69950, 69955) for c in ("red", "blue")]
    with ProcessPoolExecutor(7) as ex:
        R = list(ex.map(one, jobs, chunksize=2))
    for text in ("(world)",) + mutants:
        for inst in (True, False):
            for kind in ("model", "circuit", "bank"):
                rs = [r for r in R if r["text"] == text and r["inst"] == inst and r["kind"] == kind]
                if not rs:
                    continue
                n_ok = sum(r["ok"] for r in rs)
                print(f"{text:55s} instruments {'on ' if inst else 'off'} {kind:7s}: {n_ok} of {len(rs)} identical tick by tick; pulses "
                      f"{sum(r['pulses'] for r in rs)} tastes {sum(r['tastes'] for r in rs)} firings {sum(r['firings'] for r in rs)} meals "
                      f"{sum(r['meals'] for r in rs)}; touched beyond the interface {sorted(set(x for r in rs for x in r['other']))}", flush=True)
                if text == "(world)":
                    for r in rs:
                        if not r["ok"]:
                            print("    DIFFERS", r["bad"], flush=True)

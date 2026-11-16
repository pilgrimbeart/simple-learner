"""change_times.py: record, from timing lives, the moments the brain noticed the food colour change (its revealed changes), with the
world's slot length and phase, so a rhythm tracker can be designed and scored offline against the truth (2026-11-15, D68).
    .venv/bin/python lab/change_times.py RUNGS SEED0 N SECS OUT.pkl"""
import pickle
import sys
from concurrent.futures import ProcessPoolExecutor

sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import ladders as L
import stage3_random as R
import teach as T
from stage2_lang import arms as S


def live(lf, seconds=100.0):
    ticks = int(round(seconds / lf.dt))
    b = lf.brain
    ch, last = [], None
    while lf.t < ticks:
        lf.step()
        c = getattr(b, "lastchange", None)
        if c is not None and c != last:
            ch.append(c)
            last = c
    truth = [(t * lf.dt) for t, _ in lf.meals]
    raise StopIteration(dict(changes=ch, tau=lf.v_tau, ph=getattr(lf, "v_ph", None), meals=truth, secs=seconds))


def one(j):
    S.live = live
    try:
        T.job(j[:-1])
    except StopIteration as e:
        return dict(e.value, rung=j[-1], seed=j[3])


if __name__ == "__main__":
    rungs = [int(x) for x in sys.argv[1].split(",")]
    s0, k, secs, out = int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
    jobs = [(L.LADDERS["time"]["world"](n), "net10kc60S", 2240, s, "red", secs) for n in rungs for s in range(s0, s0 + k)]
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        res = list(ex.map(one, [j + (n,) for j, n in zip(jobs, [n for n in rungs for _ in range(k)])]))
    pickle.dump(res, open(out, "wb"))
    for r in res:
        print(f"rung {r['rung']} seed {r['seed']}: slot {r['tau']:.3f} s, phase {r['ph']}, {len(r['changes'])} noticed changes")

"""osc_trace.py: do the phase oscillators lock to the world's slot? (2026-11-15, T11.) Timing lives with PHASES=2; at the end, each
oscillator's slot length against the world's (a multiple or fraction counts), and the most trusted streams.
    PHASES=2 .venv/bin/python lab/osc_trace.py RUNG SEED0 N [SECS]"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import ladders as L
import stage3_random as R
import teach as T
from stage2_lang import arms as S


def live(lf, seconds=100.0):
    ticks = int(round(seconds / lf.dt))
    while lf.t < ticks:
        lf.step()
    b = lf.brain
    tau = getattr(lf, "v_tau", None)
    osc = [round(o["S"], 3) for o in getattr(b, "posc", [])]
    w = sorted(((getattr(N, "w", 1.0), N.kind) for N in b.nets), reverse=True)[:3]
    raise StopIteration((tau, osc, [k for _, k in w]))


def one(j):
    S.live = live
    try:
        T.job(j)
    except StopIteration as e:
        return e.value


if __name__ == "__main__":
    n, s0, k = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    secs = float(sys.argv[4]) if len(sys.argv) > 4 else 3000.0
    jobs = [(L.LADDERS["time"]["world"](n), "net10kc60S", 2240, s, "red", secs) for s in range(s0, s0 + k)]
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        for j, r in zip(jobs, ex.map(one, jobs)):
            tau, osc, top = r
            near = min(osc, key=lambda x: abs(x / tau - round(x / tau)) if x > tau else abs(tau / x - round(tau / x)))
            print(f"seed {j[3]}: slot {tau:.3f} s; oscillators {osc}; nearest ratio {near / tau:.3f}; trusted {top}")

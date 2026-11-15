"""phase_trace.py: how well does each phase oscillator's place (its bin modulo 5n, n the word's length) tell the world's colour, over a
life's last third? (2026-11-15, after T15.) Purity 1: the place fixes the colour; about .5 to .6: no information. PHASES=2 lives.
    PHASES=2 PLL_AVG=1 PDRIFT=.001 .venv/bin/python lab/phase_trace.py RUNG SEED0 N [SECS]"""
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor

sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import ladders as L
import stage3_random as R
import teach as T
from stage2_lang import arms as S

N_ = {}


def live(lf, seconds=100.0):
    ticks = int(round(seconds / lf.dt))
    b, n = lf.brain, N_["n"]
    seen = defaultdict(lambda: defaultdict(Counter))
    while lf.t < ticks:
        lf.step()
        if lf.t * lf.dt > 2 * seconds / 3 and lf.t % 40 == 0 and hasattr(b, "posc"):
            for i, o in enumerate(b.posc):
                seen[i][o["k"] % (5 * n)][lf.told_now] += 1
    tau = lf.v_tau
    th = lf.thirds(ticks)
    gain = th[2][0] - 2 * th[2][1]
    top = sorted(((getattr(N, "w", 1.0), N.kind) for N in b.nets), reverse=True)[:3]
    out = []
    for i, o in enumerate(b.posc):
        tot = sum(max(v.values()) for v in seen[i].values())
        out.append((round(o["S"] / tau, 4), round(tot / sum(sum(v.values()) for v in seen[i].values()), 2)))
    raise StopIteration((tau, out, gain, [k for _, k in top]))


def one(j):
    S.live = live
    N_["n"] = j[-1]
    try:
        T.job(j[:-1])
    except StopIteration as e:
        return e.value


if __name__ == "__main__":
    n, s0, k = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    secs = float(sys.argv[4]) if len(sys.argv) > 4 else 3000.0
    jobs = [(L.LADDERS["time"]["world"](n), "net10kc60S", 2240, s, "red", secs, n) for s in range(s0, s0 + k)]
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        for j, (tau, out, gain, top) in zip(jobs, ex.map(one, jobs)):
            print(f"seed {j[3]}: slot {tau:.2f} s; best purity {max(p for _, p in out):.2f}; last third gain {gain}; trusted {top}; "
                  f"(oscillator slot / world's, purity): {out}")

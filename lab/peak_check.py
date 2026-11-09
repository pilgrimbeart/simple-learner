"""peak_check.py: is the balance's sharp peak (lab/v/balance_speed_curve.log: a .15 offset costs 28% of a drive's food pulses; a fixed .02
wobble costs .12 a second, lab/v/rprop_cost.log) real, or plain's knife-edge of two exactly equal thrusters, or the step? The balance held
at the right value plus offsets d, the drive's food pulses and the life's gain, 300 s lives:
  double   one thruster twice the other; held at s (.69 + d), where s is the sign that suits the life (both tried, the better kept)
  plain    at 1.25 ms and at .625 ms
Seeds 81980-81999 x red/blue (fresh). Main session, 2026-11-08.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/peak_check.py [far]
far: the double world held from 0 to .84, to size the evidence a drive gives far from right (lab/v/peak_far.log)."""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import stage3_random as R
import adaptive as A
import balance_speed as B

SEEDS = range(81980, 82000)
OFF = (0.0, 0.02, 0.05, 0.15)
X = float(np.log(2.0))


def job(j):
    from minimal.spec import COST
    from stage2_lang import arms as S
    text, x, seed, first = j
    lf = A.make(S.world_of(text), seed, first, {"xheld": x}, cls=B.Held)
    l = S.live(lf, 300.0)
    return float(np.mean(lf.brain.ys)) if lf.brain.ys else 0.0, sum(a - COST * b for a, b, _ in l) / 300.0


def run(ex, text, xs):
    return {x: list(ex.map(job, [(text, x, s, c) for s in SEEDS for c in R.COL])) for x in xs}


FAR = (-0.69, -0.54, -0.39, -0.24, -0.09, 0.0, 0.15)     # far: offsets from the right value .69 (x from 0 to .84)


def far(ex):
    """How much a drive tells far from right: the drive's food pulses and their spread at each offset, so the slope against the spread
    gives the drives an ideal learner needs at each distance. Both signs held; each life's right sign from all its lives."""
    xs = sorted({s * (X + d) for s in (1, -1) for d in FAR})
    r = {x: list(ex.map(job_far, [(B.DOUBLE, x, s, c) for s in SEEDS for c in R.COL])) for x in xs}
    pos = sum(np.array([y[1] for y in r[k]]) for k in xs if k > 0)
    neg = sum(np.array([y[1] for y in r[k]]) for k in xs if k < 0)
    sgn = np.where(pos >= neg, 1, -1)
    print(f"double, held at s(.69 + d), {len(sgn)} lives of 300 s; right sign + in {np.mean(sgn > 0):.0%}")
    for d in FAR:
        ys = [r[min(r, key=lambda k: abs(k - s * (X + d)))][i] for i, s in enumerate(sgn)]
        y = np.concatenate([np.array(v[2], float) for v in ys])
        print(f"  d {d:+.2f} (x {X + d:.2f})   drives {len(y)}   pulses a drive {y.mean():.3f} +- {y.std() / np.sqrt(len(y)):.3f}"
              f"   spread {y.std():.2f}   gain {np.mean([v[1] for v in ys]):.3f}", flush=True)


def job_far(j):
    from minimal.spec import COST
    from stage2_lang import arms as S
    text, x, seed, first = j
    lf = A.make(S.world_of(text), seed, first, {"xheld": x}, cls=B.Held)
    l = S.live(lf, 300.0)
    return 0.0, sum(a - COST * b for a, b, _ in l) / 300.0, list(lf.brain.ys)


if __name__ == "__main__" and sys.argv[1:] == ["far"]:
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.00125, False)) as ex:
        far(ex)
elif __name__ == "__main__":
    for dt, worlds in ((0.00125, ("double", "plain")), (0.000625, ("plain",))):
        with ProcessPoolExecutor(7, initializer=R._init, initargs=(dt, False)) as ex:
            for w in worlds:
                if w == "double":
                    xs = sorted({s * X + d for s in (1, -1) for d in OFF + tuple(-o for o in OFF[1:])})
                    r = run(ex, B.DOUBLE, xs)
                    pos = sum(np.array([y[1] for y in r[k]]) for k in xs if k > 0)
                    neg = sum(np.array([y[1] for y in r[k]]) for k in xs if k < 0)
                    sgn = np.where(pos >= neg, 1, -1)       # each life's right sign, from all its lives of each sign (no offset favoured)
                    print(f"double, step {dt * 1000:g} ms, held at s(.69 + d), {len(pos)} lives; right sign + in {np.mean(sgn > 0):.0%}")
                    for d in sorted(set(OFF + tuple(-o for o in OFF[1:]))):
                        ys = [r[min(r, key=lambda k: abs(k - s * (X + d)))][i] for i, s in enumerate(sgn)]
                        print(f"  d {d:+.2f}   pulses a drive {np.mean([y[0] for y in ys]):.3f}   gain {np.mean([y[1] for y in ys]):.3f}", flush=True)
                else:
                    xs = sorted(set(OFF + tuple(-o for o in OFF[1:])))
                    r = run(ex, R.PLAIN, xs)
                    print(f"plain, step {dt * 1000:g} ms, held at d, {len(r[0.0])} lives")
                    for d in xs:
                        print(f"  d {d:+.2f}   pulses a drive {np.mean([y[0] for y in r[d]]):.3f}   gain {np.mean([y[1] for y in r[d]]):.3f}", flush=True)

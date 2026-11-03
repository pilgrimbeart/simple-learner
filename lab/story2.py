"""story2.py: the second story's experiment (STORIES.md): X = my two thrusters are unequal. The flaw is introduced on
purpose; the standard body keeps them identical. Stages 1 and 2 only: the baseline, and the optimum target.

Every arm: B's movements, told the colour (so this is about one X), the run's 1 s limit, a drive's two oscillators
started in step (D20: else any balance costs at every drive's start). A body's imbalance a: one thruster sqrt(a)
times as strong, the other sqrt(a) times weaker, which by a coin, so strength overall doesn't change.

    balance(e): each motor's rate set for a straight drive, x = log(motor 0's rate / motor 1's) = its right value + e
    python lab/story2.py curve        # the gap against the size of the flaw
    python lab/story2.py error        # the score against the error in the balance: how precisely must it be known?
    python lab/story2.py users        # the user's bodies (each thruster 0.5-2), lives of 100 s and 2,000 s"""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from creature import Life
from discrete import model as M
from discrete.bodies import THRUSTERS, draw, vary
from minimal.spec import SPAN, Lived, thirds, summary, efficiency, gain, interval
from discrete.poison import show
from story1 import RunLimit
from units import TICK


class Brain(RunLimit, M.Model):
    pass


def factors(seed, a, users):
    if users:
        return draw(seed, THRUSTERS)
    r = np.random.default_rng(seed + 5_500_007)
    s = 1 if r.random() < 0.5 else -1
    return {"left": a ** (s / 2), "right": a ** (-s / 2)}


def life(job):
    arm, a, users, e, seed, seconds, poison = job
    p, spread = M.from_bench()
    q = dict(M.drawn(p, spread, seed), run_max=1.0, sync=1, V_H=99.0)
    lf = Life(seed, poison, brain=lambda s: Brain(s, q))
    b = lf.brain
    b.food = 1 - lf.sensor[poison]
    f = factors(seed, a, users)
    vary(lf, f)
    thr = {m: t for t, m in lf.motor.items()}
    k0, k1 = f[thr[0]], f[thr[1]]
    right = np.log(k1 / k0)
    if arm == "balanced":
        x = right + e
        b.p["g0"], b.p["g1"] = float(np.exp(x / 2)), float(np.exp(-x / 2))
    elif arm == "restored":                             # every firing as the standard body's: nothing left to learn
        b.p["g0"], b.p["g1"] = 1 / k0, 1 / k1
    ticks = int(round(seconds / TICK))
    while lf.t < ticks:
        lf.step()
    l = Lived(thirds(lf.meals, lf.moving, ticks, poison))
    l.power, l.firings, l.substrate = 3.7e-9, SPAN * len(lf.firings) / seconds, "silicon"
    l.right = float(right)
    return l


def run(arm, seeds, a=1.0, users=False, e=0.0, seconds=100.0):
    jobs = [(arm, a, users, e, s, seconds, c) for s in seeds for c in ("red", "blue")]
    with ProcessPoolExecutor(8) as ex:
        return list(ex.map(life, jobs, chunksize=4))


def paired(A, B, f=efficiency, boot=2000):
    rng = np.random.default_rng(0)
    n = len(A) // 2
    d = []
    for _ in range(boot):
        k = rng.integers(0, n, n)
        d.append(f([l for i in k for l in (A[2 * i], A[2 * i + 1])]) - f([l for i in k for l in (B[2 * i], B[2 * i + 1])]))
    return f(A) - f(B), interval(d)


def line(name, L):
    s = summary(L)
    c = s["ci"]["efficiency"]
    print(f"{name}: efficiency {s['efficiency']:.2f} [{c[0]:.2f}, {c[1]:.2f}]  gain {s['gain']:.2f}  food {s['food']:.2f}  poison {s['poison']:.2f}  "
          f"stranded {s['stranded']:.0%}  firings {s['firings']:.0f}", flush=True)
    return s


if __name__ == "__main__":
    cmd = sys.argv[1]
    S = range(51000, 51064)
    if cmd == "curve":
        for a in (1.0, 1.01, 1.03, 1.1, 1.25, 1.5, 2.0, 4.0):
            base, opt = run("baseline", S, a), run("balanced", S, a)
            line(f"a {a}: baseline", base)
            line(f"a {a}: balanced", opt)
            d, i = paired(opt, base)
            print(f"   gap {d:+.2f} [{i[0]:+.2f}, {i[1]:+.2f}]", flush=True)
    elif cmd == "error":
        for a in (1.25, 2.0):
            ref = run("balanced", S, a)
            for e in (-0.8, -0.4, -0.2, -0.1, -0.05, 0.05, 0.1, 0.2, 0.4, 0.8):
                L = run("balanced", S, a, e=e)
                d, i = paired(L, ref)
                print(f"a {a} error {e:+.2f}: {efficiency(L):.2f}, against none {d:+.2f} [{i[0]:+.2f}, {i[1]:+.2f}]", flush=True)
            line(f"a {a} error 0", ref)
    elif cmd == "users":
        for secs in (100.0, 2000.0):
            T = S if secs == 100 else range(51000, 51032)
            base, opt, res = (run(x, T, users=True, seconds=secs) for x in ("baseline", "balanced", "restored"))
            line(f"{secs:.0f} s: baseline", base)
            line(f"{secs:.0f} s: balanced", opt)
            line(f"{secs:.0f} s: restored", res)
            d, i = paired(opt, base)
            print(f"   gap {d:+.2f} [{i[0]:+.2f}, {i[1]:+.2f}]; balance's spread {np.std([l.right for l in base]):.2f} (log), median size {np.median(np.abs([l.right for l in base])):.2f}", flush=True)

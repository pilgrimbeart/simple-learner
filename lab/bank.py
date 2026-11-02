"""bank.py: a revolution's period by a bank of resonating oscillators (QUESTIONS.md, step 3: rhythm by mode locking;
Large's neural resonance), on long steady one-motor spins, where locking has the cycles it needs (D23). Each spin:
60 s at B's scan rate on a lopsided body (period_probe.py's). Estimators of each motor's period from the first S s,
judged by the balance log(T0 / T1) against the right one.

    python bank.py collect            # v/bank_spins.pkl
    python bank.py test k=v ...       # N oscillators, log-spaced 0.3-4 s; alpha < 0 resonators, > 0 limit cycles
"""
import math, pickle, sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from units import TICK
V = "/home/pilgrim/git/simple-learner/lab/v"


class Scan:                                             # (period_probe.py's; it runs its demo on import)
    def __init__(self, m, rate):
        self.m, self.rate, self.phase, self.t, self.pulses = m, rate, 0.0, 0.0, []
    def stimulate(self, sensor, at): self.pulses.append(self.t + at)
    def taste(self, value, at): pass
    def step(self):
        self.t += TICK
        self.phase += self.rate * TICK
        k = int(self.phase); self.phase -= k
        return [self.m] * k


def fundamental(d, lo=0.3, hi=4.0, w=0.04, n=6, top=0.9):
    """(period_probe.py's comb on the intervals' histogram.)"""
    d = np.asarray(d)
    dens = lambda x: np.mean(np.abs(d - x) < w)
    base = lambda x: np.mean(np.abs(d - x) < 0.5) * (2 * w / 1.0) + 1e-9
    Ts = np.arange(lo, hi, 0.01)
    sc = np.array([np.mean([dens(k * T) / base(k * T) for k in range(1, n + 1)]) for T in Ts])
    return float(Ts[np.flatnonzero(sc >= top * sc.max())[0]])


def spin(job):
    from creature import Life
    from discrete import model as M
    from discrete.bodies import THRUSTERS, draw, vary
    seed, m = job
    p, _ = M.from_bench()
    b = Scan(m, p["scan"])
    lf = Life(seed, None, brain=lambda s: b)
    f = draw(seed, THRUSTERS); vary(lf, f)
    thr = {mm: t for t, mm in lf.motor.items()}
    for _ in range(int(60 / TICK)):
        lf.step()
    return seed, m, f[thr[m]], np.array(b.pulses)


def passes(x, merge=0.05):
    ev = []
    for v in x:
        if not ev or v - ev[-1] >= merge:
            ev.append(v)
    return np.array(ev)


def bank(ev, S, p):
    """The bank's amplitudes after S s: dz/dt = z (alpha + i w + beta |z|^2), each pass kicking every z by c."""
    N = int(p.get("N", 24))
    T = np.exp(np.linspace(np.log(p.get("lo", 0.1)), np.log(4.0), N))
    w = 2 * np.pi / T
    a, beta, c = p.get("alpha", -0.3), p.get("beta", 0.0), p.get("c", 0.3)
    z = np.zeros(N, complex)
    ev = ev[ev < S]
    j, t = 0, 0.0
    A = np.zeros(N)
    while t < S:
        z = z * np.exp((a + 1j * w) * TICK)             # rotation exact (Euler grew it), damping a per s for all
        if beta:
            z = z / np.sqrt(np.maximum(1 - 2 * beta * np.abs(z) ** 2 * TICK, 1e-9))   # beta |z|^2 z, exactly
        while j < len(ev) and ev[j] < t + TICK:
            z = z + c
            j += 1
        t += TICK
        if t > S - 5:
            A += np.abs(z)
    return T, A


def estimate(T, A, n=6, top=0.84, lo=0.3):
    """Subharmonic summation on the bank: each candidate period's multiples, weighted top^(k-1)."""
    logT = np.log(T)
    sc = np.zeros(len(T))
    for i in range(len(T)):
        for k in range(1, n + 1):
            x = logT[i] - math.log(k)                   # a period's harmonics lie at T / k
            if x < logT[0]:
                break
            sc[i] += top ** (k - 1) * np.interp(x, logT, A)
    sc[T < lo] = -np.inf                                # (the fundamental itself is at least lo)
    i = int(np.argmax(sc))
    if 0 < i < len(T) - 1:                               # (a parabola through the peak)
        y0, y1, y2 = sc[i - 1], sc[i], sc[i + 1]
        if not np.isfinite(y0):
            return float(T[i])
        d = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2) if (y0 - 2 * y1 + y2) != 0 else 0.0
        return float(np.exp(logT[i] + d * (logT[1] - logT[0])))
    return float(T[i])


if __name__ == "__main__":
    cmd = sys.argv[1]
    kv = {k: float(v) for k, v in (a.split("=") for a in sys.argv[2:] if "=" in a)}
    if cmd == "collect":
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(7) as ex:
            R = list(ex.map(spin, [(s, m) for s in range(32) for m in (0, 1)]))
        pickle.dump(R, open(f"{V}/bank_spins.pkl", "wb"))
        print(len(R), "spins")
    else:
        R = pickle.load(open(f"{V}/bank_spins.pkl", "rb"))
        by = {}
        for seed, m, k, x in R:
            by.setdefault(seed, {})[m] = (k, x)
        for S in (10, 20, 40, 60):
            xb, xh, right = [], [], []
            for seed, d in by.items():
                Tb, Th = [], []
                for m in (0, 1):
                    k, x = d[m]
                    ev = passes(x[(x > 2) & (x < S)] - 2)
                    Tb.append(estimate(*bank(ev, S - 2, kv)))
                    dd = (ev[None, :] - ev[:, None]).ravel(); dd = dd[(dd > 0.15) & (dd < 17)]
                    Th.append(fundamental(dd) if len(dd) else 1.0)
                right.append(math.log(d[1][0] / d[0][0]))
                xb.append(math.log(Tb[0] / Tb[1])); xh.append(math.log(Th[0] / Th[1]))
            xb, xh, right = map(np.array, (xb, xh, right))
            print(f"{kv} first {S} s: bank within 0.1 {np.mean(abs(xb - right) < 0.1):.0%} (median |error| "
                  f"{np.median(abs(xb - right)):.2f}); histogram within 0.1 {np.mean(abs(xh - right) < 0.1):.0%} "
                  f"({np.median(abs(xh - right)):.2f})", flush=True)

"""sepbench.py [k=v ...]: sepb's circuit on a bench (no body): its blocks' numbers, as blocks.bench_b measures cmos_b."""
import sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from sepb import spec
from minimal.spec import make
from units import TICK


def bench(s, names, events, seconds, seed=0, substrate="silicon"):
    """events: [(t, kind)] kind 0/1 an eye's pulse, 'food'/'poison' a taste; -> times, voltages (ticks x nodes),
    each motor's spikes per tick."""
    b = make(s, substrate)(seed)
    ev = sorted(events)
    T, V, M = [], [], []
    k = 0
    for i in range(int(round(seconds / TICK))):
        t0 = i * TICK
        while k < len(ev) and ev[k][0] < t0 + TICK:
            t, kind = ev[k]
            if kind in (0, 1):
                b.stimulate(kind, t - t0)
            else:
                b.taste(1 if kind == "food" else -1, t - t0)
            k += 1
        fired = b.step()
        T.append(t0 + TICK); V.append(b.circuit.V.copy()); M.append((fired.count(0), fired.count(1)))
    return np.array(T), np.array(V), np.array(M)


def numbers(s, names, seed=0, substrate="silicon"):
    ix = {n: i for i, n in enumerate(names)}
    food = 0 if s["nodes"][ix["q"]][6] > 0 else 1
    ev = [(4.0 + 0.02 * k, food) for k in range(10)]
    ev += [(20.0, "poison"), (20.5, "poison"), (21.5, "food"), (23.0, "poison"), (23.4, "poison"), (23.8, "poison")]
    t, V, M = bench(s, names, ev, 26.0, seed, substrate)
    v = lambda n: V[:, ix[n]]
    at = lambda n, x: float(v(n)[np.searchsorted(t, x)])
    out = {}
    drv = (t > 4.0) & (v("HD") > 0)
    out["hold"] = float(t[drv][-1] - 4.18) if drv.any() else 0.0
    run = (t > 4.3) & (v("BT") < s_v(s, "v_bored"))
    out["bored"] = float(t[run][0] - 4.18) if run.any() else None
    rate = lambda m, a, b: M[(t > a) & (t <= b), m].sum() / (b - a)
    out["scan"] = rate(0, 4.5, 4.18 + out["bored"] - 0.2) if out["bored"] else None
    out["drive"] = rate(1, 4.0, 4.18)
    rs = t[run][0] if run.any() else 19.0
    out["run"] = rate(1, rs + 0.1, 19.9) if rs < 19 else None
    out["step"] = at("DQ", 20.1) - at("DQ", 19.95)
    out["fstep"] = at("DQ", 21.45) - at("DQ", 21.6)
    out["drift"] = (at("DQ", 20.1) - at("DQ", 20.45)) / 0.35
    out["q before, after"] = (round(at("q", 22.9), 2), round(at("q", 25.9), 2))
    out["DQ after flip"] = round(at("DQ", 25.9), 3)
    out["DQ max"] = round(float(v("DQ")[(t > 22.9)].max()), 3)
    return {k: (round(x, 4) if isinstance(x, float) else x) for k, x in out.items()}, (t, V, M)


S_V = {"v_bored": -0.30}


def s_v(s, k):
    return S_V.get(k)


if __name__ == "__main__":
    kw = {k: float(x) for k, x in (a.split("=") for a in sys.argv[1:])}
    s, names = spec(**kw)
    S_V["v_bored"] = kw.get("v_bored", -0.30)
    print(numbers(s, names)[0])

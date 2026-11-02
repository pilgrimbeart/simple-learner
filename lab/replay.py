"""Open loop: a life lived by the simulator (silicon, as built for its seed), every pulse the body gave recorded, then
replayed into the transistor netlist (minimal/spice.py) in ngspice, and into the simulator again step by step; every
node's voltage and the motors' spikes compared."""
import json, os, sys, time
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from creature import Life
from minimal import spice
from minimal.spec import make
from mixed_feedback import DT, SPIKE
from units import TICK

HERE = os.path.dirname(os.path.abspath(__file__))


def live(spec, seed, poison, seconds):
    """The life, closed loop: every pulse (node, current, start, length), and the meals."""
    lf = Life(seed, poison, brain=make(spec, "silicon"))
    c = lf.brain.circuit
    pulses = []
    orig = c.pulse

    def pulse(node, current, at, length):
        c._ready()
        pulses.append((node, current, c.steps * DT + at, length))
        orig(node, current, at, length)
    c.pulse = pulse
    while lf.t < int(round(seconds / TICK)):
        lf.step()
    return pulses, lf


def fine(spec, seed, pulses, seconds):
    """The same life again, open loop, step by step: the simulator's every node at every step (the same noise: one
    stream, drawn in the same order)."""
    c = make(spec, "silicon")(seed).circuit
    c._ready()
    per = int(round(TICK / DT))
    ticks = int(round(seconds / TICK))
    out = np.empty((ticks * per, len(c.names)))
    ps = sorted(pulses, key=lambda p: p[2])
    k = 0
    for tick in range(ticks):
        t0 = tick * TICK
        while k < len(ps) and ps[k][2] < t0 + TICK - 1e-12:
            node, cur, at, length = ps[k]
            c.pulse(node, cur, at - t0, length)
            k += 1
        for s in range(per):
            c.run(DT)
            out[tick * per + s] = c.V
    return out


def spike_times(v, dt):
    """When v rose through SPIKE having fallen below RESET (as the simulator counts)."""
    armed, out = True, []
    for k, x in enumerate(v):
        if armed and x > SPIKE:
            out.append(k * dt)
            armed = False
        elif x < -0.3:
            armed = True
    return np.array(out)


if __name__ == "__main__":
    name, seed, seconds = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
    from minimal.spec import load
    spec = load(f"/home/pilgrim/git/simple-learner/minimal/results/{name}.json")
    pulses, lf = live(spec, seed, sys.argv[4] if len(sys.argv) > 4 else "red", seconds)
    print(f"lived {seconds:g} s: {len(pulses)} pulses; meals (s, colour): "
          + ", ".join(f"{t * TICK:.1f} {c}" for t, c in lf.meals), flush=True)
    sim = fine(spec, seed, pulses, seconds)
    trims = spice.trim(spec, seed)
    text, parts = spice.netlist(spec, seed, trims, pulses=pulses, seconds=seconds, probe="probe.txt",
                                title=f"{name} seed {seed}, replaying a life")
    work = os.path.join(HERE, f"replay_{name}_{seed}")
    os.makedirs(work, exist_ok=True)
    print(f"netlist: {parts}", flush=True)
    t0 = time.time()
    spice.run(text, work)
    print(f"ngspice: {time.time() - t0:.0f} s", flush=True)
    d = np.loadtxt(os.path.join(work, "probe.txt"), skiprows=1)
    t, sp = d[:, 0], d[:, 1:]
    n = min(len(sim), len(sp) - 1)
    sp, sim, t = sp[1:n + 1], sim[:n], t[1:n + 1]       # (SPICE's row k + 1 is the end of the simulator's step k)
    c, names = spice.build(spec, seed)
    np.savez(os.path.join(work, "compare.npz"), t=t, spice=sp, sim=sim, names=np.array(c.names),
             meals=np.array([(m[0] * TICK, m[1] == "red") for m in lf.meals]).reshape(-1, 2))
    for i, nm in enumerate(c.names):
        diff = np.abs(sp[:, i] - sim[:, i])
        print(f"{nm:3s} simulator {sim[:, i].min():+.2f}..{sim[:, i].max():+.2f} V, SPICE {sp[:, i].min():+.2f}.."
              f"{sp[:, i].max():+.2f}; |difference| median {np.median(diff) * 1e3:.0f} mV, 90% "
              f"{np.percentile(diff, 90) * 1e3:.0f} mV; at the end {sim[-1, i]:+.3f} against {sp[-1, i]:+.3f}")
    for k, m in zip(("M0", "M1"), spec["motors"]):
        a, b = spike_times(sim[:, m], DT), spike_times(sp[:, m], DT)
        near = [np.min(np.abs(b - x)) for x in a] if len(b) else []
        print(f"motor {k} ({c.names[m]}): spikes simulator {len(a)}, SPICE {len(b)}; a simulator spike's nearest SPICE"
              f" spike: median {np.median(near) * 1e3:.1f} ms, within 2 ms {np.mean(np.array(near) < 2e-3):.0%}")

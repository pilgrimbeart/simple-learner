"""Robot-action investigation (D178), R5 and R7: identical-input replay outside the body. A captured closed-loop
life's saved input stream (body pulses (s, sensor) and tastes (s, value), absolute seconds) is fed to a fresh adapter
brain of the same seed (same component draws, same noise stream) in either substrate; nothing reaches a body.
Spikes are read at RES (1 ms) resolution by running the circuit in 1 ms chunks (the same integration and noise
sequence as 10 ms runs: checked by `check`). Not a reward comparison.
omit: a set of pulse indices withheld (paired omission, the offline harness only; the brain never sees labels).
"""
import os, pickle, sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
RES = 0.001


def replay(r, substrate, omit=(), bias=None, seconds=100.0):
    import brain as B
    from units import TICK
    Brain = B.make_brain(substrate, True, True, bias if bias is not None else r.get("bias"), log=False)
    b = Brain(r["seed"])
    if r["arm"] == "informed":
        food = "blue" if r["poison"] == "red" else "red"
        b.circuit.start[b.P[r["sensor"][food]]] = r["F"]
        b.circuit.start[b.P[r["sensor"][r["poison"]]]] = r["Q"]
    c = b.circuit
    ev = [(t, "s", int(k), i) for i, (t, k) in enumerate(r["pulses"]) if i not in omit]
    ev += [(t, "t", v, -1) for t, v in r["tastes"]]
    ev.sort(key=lambda e: e[0])
    sub = int(round(TICK / RES))
    n = int(round(seconds / RES))
    nodes = list(b.sensors) + list(b.motors)
    spk = np.zeros((n, 4), np.int8)
    P = np.zeros((int(round(seconds / TICK)), 2), np.float32)
    j = 0
    for step in range(n):
        t0 = step * RES
        while j < len(ev) and ev[j][0] < t0 + RES:
            t, kind, v, _ = ev[j]
            at = t - t0
            if kind == "s":
                b.stimulate(v, at)          # brains.circuit.CircuitBrain.stimulate: the body's own pulse
            else:
                b.taste(v, at)
            j += 1
        s = c.run(RES)
        spk[step] = s[nodes]
        if step % sub == sub - 1:
            P[step // sub] = c.V[b.P[0]], c.V[b.P[1]]
    return spk, P


def per_tick(spk, sub=10):
    return spk.reshape(-1, sub, 4).sum(1)


def check(r):
    """The replay of a life in its own substrate reproduces its closed-loop spikes tick for tick."""
    spk, _ = replay(r, r["substrate"])
    return bool(np.array_equal(per_tick(spk), r["rows"][:, 4:8].astype(np.int64)))

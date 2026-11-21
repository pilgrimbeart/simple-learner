"""Robot-action investigation (D178; lab/WORK_ORDER_2026-11-20_robot_action.md): a lab adapter of the historical
designed circuit (brains/designed.py, unmodified) with D176's repairs, a supported substrate choice and passive logging.

  substrate  "biology" or "silicon", passed to mixed_feedback.Circuit's own `substrate` argument (its supported
             selection). Everything else is the historical contract: VOLT = 1 V, on_chip=False, PULSES, seed + 1000003,
             streams=False (one noise stream; the same standard-normal draws in both substrates, scaled differently).
             This is a noise-only diagnostic, NOT an on-chip implementation.
  mem, thr   D176's repairs: each P a memory node; the two taste writers' thresholds +-THR V (THR = 0.8).
  bias       None, or (group, I) with group in {"sensor", "motor"}: the stage-2 single knob family, that group's neuron
             bias current (mixed_feedback.Circuit.neuron's `bias`, an existing parameter), in A. Applied at build.
Logging is passive (nothing read back into the circuit): per tick E0, E1, P0, P1 and the spikes of S0, S1, M0, M1;
every body pulse (s, sensor) and taste (s, value) in absolute seconds.
"""
from __future__ import annotations

import sys
from collections import deque
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

THR = 0.8


def make_brain(substrate="biology", mem=True, thr=True, bias=None, log=True):
    from brains.designed import DesignedBrain
    from brains.circuit import TRACE, VOLT
    from mixed_feedback import Circuit
    from units import R_TYP, TICK

    class Adapted(DesignedBrain):
        def __init__(self, seed):                       # brains.circuit.CircuitBrain.__init__, with substrate passed
            self.seed = seed
            c = self.circuit = Circuit(seed=seed + 1_000_003, streams=self.STREAMS, volt=VOLT, on_chip=False,
                                       substrate=substrate)
            neuron = c.neuron
            if bias is not None:
                group, I = bias
                prefix = "S" if group == "sensor" else "M"

                def biased(name, *a, **k):
                    if name.startswith(prefix):
                        k = dict(k, bias=I)
                    return neuron(name, *a, **k)
                c.neuron = biased
            self.sensors = [c.neuron(f"S{k}") for k in (0, 1)]
            self.motors = [c.neuron(f"M{k}") for k in (0, 1)]
            c.neuron = neuron
            self.taste_node = c.node("taste", R=0.5 * R_TYP)
            self.build(c)
            self.last_inject = np.zeros(len(c.names))
            self.history = deque(maxlen=TRACE)
            self.log = None
            self.tick, self.pulses, self.tastes, self.rows = 0, [], [], []

        def build(self, c):
            node, element = c.node, c.element
            if mem:
                c.node = lambda name, *a, **k: node(name, *a, **dict(k, memory=name.startswith("P")))
            if thr:
                def el(to, frm, gain, offset, *a, **k):
                    if c.names[to].startswith("P") and frm == self.taste_node:
                        offset = THR if offset > 0 else -THR
                    return element(to, frm, gain, offset, *a, **k)
                c.element = el
            super().build(c)
            c.node, c.element = node, element

        def stimulate(self, sensor, at):
            if log:
                self.pulses.append((self.tick * TICK + at, int(sensor)))
            super().stimulate(sensor, at)

        def taste(self, value, at):
            if log:
                self.tastes.append((self.tick * TICK + at, float(value)))
            super().taste(value, at)

        def _tick(self):
            spikes = super()._tick()
            if log:
                V = self.circuit.V
                self.rows.append((V[self.E[0]], V[self.E[1]], V[self.P[0]], V[self.P[1]],
                                  spikes[self.sensors[0]], spikes[self.sensors[1]], spikes[self.motors[0]],
                                  spikes[self.motors[1]]))
            self.tick += 1
            return spikes

    return Adapted


def wiring(brain):
    """The realised internal wiring, read from the built graph (never inferred from firing): for each sensor k, the
    motor its fixed SIDE synapse drives and the motor its gated (plastic) synapse drives, and the gating knob."""
    c = brain.circuit
    out = []
    for k, s in enumerate(brain.sensors):
        side = [to for (_, (to, frm, gate)) in c.elements if frm == s and to in brain.motors and gate < 0]
        plastic = [(to, gate) for (_, (to, frm, gate)) in c.elements if frm == s and to in brain.motors and gate >= 0]
        assert len(side) == 1 and len(plastic) == 1
        out.append(dict(sensor=k, side_motor=brain.motors.index(side[0]), plastic_motor=brain.motors.index(plastic[0][0]),
                        knob=c.names[plastic[0][1]]))
    return out


def draws_hash(brain):
    """A hash of the realised component draws (the mismatched node and element arrays and the links; not the
    substrate's resting-noise levels, which differ by substrate by design)."""
    import hashlib
    c = brain.circuit
    c._ready()
    h = hashlib.sha256()
    for a in (c.node_arr, c.el_arr, c.link):
        h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest()[:16]

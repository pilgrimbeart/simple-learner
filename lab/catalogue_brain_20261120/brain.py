"""D180 catalogue-native brain: a lab adapter of the exact v1 graph (design.py) onto the unchanged engine.

Engine: mixed_feedback.Circuit builds the arrays (its own mismatch law, streams=True, silicon, V_TYP, on_chip) and the
per-node noise streams; integration is mixed_feedback._step, unchanged, called from a numba loop (_loop) that also
records observation-only quantities (pre-clip value, per-step extrema, motor event steps). At ratio 1 with "native"
noise, _loop reproduces Circuit.run bit for bit (checks.py). Refinement (ratio r = 2, 4): circuit step DT/r inside the
unchanged body TICK; noise "coupled": each coarse DT step's standard normal is the sum of FINE (=4) independent fine
normals / 2, the fine normals drawn from each node's own stream, so DT, DT/2, DT/4 share one Brownian path.

Removal controls: the FULL graph is built and its arrays drawn first, then removed edges' columns are dropped (their
current and power vanish; every surviving part keeps its original draw); static power is recomputed by chip.still.

The brain sees only stimulate(sensor, at), taste(value, at), step(). Informed controls are set by the harness
(set_P) after Life exposes wiring and before the first step.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import numpy as np
from numba import njit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import chip                                                   # noqa: E402
from mixed_feedback import Circuit, _pulse, _step, SPIKE      # noqa: E402
from units import DT, PULSE, TICK, V_TYP                      # noqa: E402
from brains.circuit import PULSES                             # noqa: E402
from design import graph                                      # noqa: E402

FINE = 4                     # coupled noise: fine normals per DT step (supports ratios 1, 2, 4)
CHUNK = 100                  # ticks of noise drawn at once (chunk-size invariance is checked)

REMOVALS = {                 # named controls: edges removed after the full graph's draws
    "none": (),
    "no_explore": ("explore_motor_0", "explore_motor_1"),
    "no_sensory": ("side_0", "side_1", "plastic_0", "plastic_1"),
    "no_writers": ("write_positive_0", "write_negative_0", "write_positive_1", "write_negative_1"),
    "no_bias_writer": ("explore_adjust_0", "explore_adjust_1"),
}


@njit(cache=True)
def _loop(V, Vx, armed, spikes, vmax, drive, node, el, link, z, q, rest, dt, steps, cfg,
          vmin_o, vmax_o, clip_o, preclip_o, slew_o, ev_step, ev_node, ev_n, motors, t0, ra_step, ra_node, ra_n):
    """steps calls of the unchanged _step. Observation only: per-node extrema, steps clipped at a rail (pre-clip value
    beyond lo/hi), the most extreme pre-clip value, the largest deterministic |dV|/C, and each motor event's step."""
    n = V.shape[0]
    dV, gross = np.empty(n), np.empty(n)
    power = 0.0
    cap, lo, hi = node[2], node[3], node[4]
    for k in range(steps):
        Vold = V.copy()
        before = spikes.copy()
        was = armed.copy()
        power += _step(V, Vx, armed, spikes, vmax, drive[k], node, el, link, z[k], q, rest, dt, dV, gross, cfg)
        for i in range(n):
            var = (q * gross[i] + rest[i]) * dt
            pre = Vold[i] + (dt * dV[i] + np.sqrt(var) * z[k, i]) / cap[i]
            if pre > hi[i] or pre < lo[i]:
                clip_o[i] += 1
                if abs(pre) > abs(preclip_o[i]):
                    preclip_o[i] = pre
            if V[i] < vmin_o[i]:
                vmin_o[i] = V[i]
            if V[i] > vmax_o[i]:
                vmax_o[i] = V[i]
            s = abs(dV[i]) / cap[i]
            if s > slew_o[i]:
                slew_o[i] = s
        for j in range(motors.shape[0]):
            m = motors[j]
            if spikes[m] > before[m] and ev_n[0] < ev_step.shape[0]:
                ev_step[ev_n[0]] = t0 + k
                ev_node[ev_n[0]] = j
                ev_n[0] += 1
            if armed[m] and not was[m] and ra_n[0] < ra_step.shape[0]:
                ra_step[ra_n[0]] = t0 + k
                ra_node[ra_n[0]] = j
                ra_n[0] += 1
    return power


class Engine:
    """The v1 graph on the unchanged engine. seed: the world seed. sides: wiring (default from the wiring RNG)."""

    def __init__(self, seed, sides=None, removed="none", ratio=1, noise="native", P0=None, record=True,
                 scale=None, spec=None):
        """P0: bench-only birth values of (P0, P1); sides: wiring fixture override."""
        assert ratio in (1, 2, 4) and noise in ("native", "coupled")
        assert noise == "coupled" or ratio == 1
        self.seed, self.ratio, self.noise = seed, ratio, noise
        if sides is None:
            sides = tuple(int(x) for x in np.random.default_rng([seed, 180, 2]).integers(0, 2, 2))
        self.sides = tuple(sides)
        g = spec(self.sides) if spec is not None else graph(self.sides)
        self.g = g
        self.ix = {nd["name"]: i for i, nd in enumerate(g["nodes"])}
        init = np.random.default_rng([seed, 180, 1])
        starts = []
        for nd in g["nodes"]:
            if nd["initial"] == "random":
                starts.append(float(init.uniform(-V_TYP / 4, V_TYP / 4)))
            elif nd["initial"] == "neutral":
                starts.append(V_TYP / 2)
            else:
                starts.append(-1.5 * V_TYP)
        if P0 is not None:                                         # bench-only birth assignment (harness)
            for k in (0, 1):
                starts[self.ix[f"P{k}"]] = float(P0[k])
        c = self.c = Circuit(seed=seed + 1_000_003, streams=True, substrate=g["substrate"], volt=g["volt"],
                             on_chip=g["on_chip"])
        for nd, s in zip(g["nodes"], starts):
            c.node(nd["name"], bias=nd["bias"], R=nd["R"], C=nd["C"], lo=nd["lo"], hi=nd["hi"], start=s,
                   memory=nd["memory"])
        self.enames = [e["name"] for e in g["edges"]]
        for e in g["edges"]:
            c.element(self.ix[e["to"]], self.ix[e["source"]], e["gain"], e["offset"], tau=e["tau"], slope=e["slope"],
                      sigmoid=e["sigmoid"], gate=-1 if e["gate"] is None else self.ix[e["gate"]])
        c._ready()                                                 # full graph's draws; all starts explicit
        rm = REMOVALS[removed] if isinstance(removed, str) else tuple(removed)
        assert all(r in self.enames for r in rm)
        self.removed = rm
        keep = np.array([j for j, nm in enumerate(self.enames) if nm not in rm], dtype=np.int64)
        self.keep = keep
        self.el = np.ascontiguousarray(c.el_arr[:, keep])
        if scale is not None:                                      # gain variants: nominal scaled, same draws
            for nm, f in scale.items():
                j = list(keep).index(self.enames.index(nm))
                self.el[0, j] *= f
        self.link = np.ascontiguousarray(c.link[:, keep])
        self.node = c.node_arr
        self.cfg = c.cfg.copy()
        self.cfg[1] = chip.still(self.node, self.el, self.link, 2 * self.cfg[2])
        self.q, self.rest = c.q, c.rest
        self.V = c.V.copy()
        self.Vx = self.V[self.link[1]].copy()
        n = len(self.V)
        self.armed = np.ones(n, dtype=np.bool_)
        self.spikes = np.zeros(n, dtype=np.int64)
        self.vmax = np.full(n, -np.inf)
        self.dt = DT / ratio
        self.tick_steps = int(round(TICK / self.dt))
        self.drive = np.zeros((self.tick_steps * 2, n))
        self.rngs = c.node_rng                                    # per-node noise streams [seed+1000003, i]
        self.zbuf, self.zpos = None, 0
        self.t_step = 0                                           # fine steps elapsed
        self.power_sum = 0.0
        self.vmin_o, self.vmax_o = np.full(n, np.inf), np.full(n, -np.inf)
        self.clip_o, self.preclip_o, self.slew_o = np.zeros(n, np.int64), np.zeros(n), np.zeros(n)
        self.ev_step, self.ev_node, self.ev_n = np.zeros(200000, np.int64), np.zeros(200000, np.int64), np.zeros(1, np.int64)
        self.ra_step, self.ra_node, self.ra_n = np.zeros(200000, np.int64), np.zeros(200000, np.int64), np.zeros(1, np.int64)
        self.motors = np.array([self.ix["M0"], self.ix["M1"]], dtype=np.int64)
        self.record = record

    # --- noise -------------------------------------------------------------------------------------------------
    def _refill(self, ticks):
        n = len(self.V)
        coarse = int(round(TICK / DT)) * ticks
        if self.noise == "native":
            z = np.empty((coarse, n))
            for i, g in enumerate(self.rngs):
                z[:, i] = g.standard_normal(coarse)
        else:
            fine = np.empty((coarse * FINE, n))
            for i, g in enumerate(self.rngs):
                fine[:, i] = g.standard_normal(coarse * FINE)
            per = FINE // self.ratio                                # fine normals per step at this ratio
            z = fine.reshape(coarse * self.ratio, per, n).sum(1) / np.sqrt(per)
        self.zbuf, self.zpos = z, 0

    def _z(self, steps):
        parts = []
        while steps > 0:
            if self.zbuf is None or self.zpos == len(self.zbuf):
                self._refill(CHUNK)
            k = min(steps, len(self.zbuf) - self.zpos)
            parts.append(self.zbuf[self.zpos:self.zpos + k])
            self.zpos += k
            steps -= k
        return parts[0] if len(parts) == 1 else np.concatenate(parts)

    # --- inputs ------------------------------------------------------------------------------------------------
    def pulse(self, node, current, at, length=PULSE):
        need = int(np.ceil((at + length) / self.dt)) + 1
        if need > len(self.drive):
            self.drive = np.concatenate([self.drive, np.zeros((need - len(self.drive), len(self.V)))])
        _pulse(self.drive, node, current, at, length, self.dt)

    def unit(self):
        return self.c.unit()

    def run_tick(self):
        steps = self.tick_steps
        z = np.ascontiguousarray(self._z(steps))
        if len(self.drive) < steps:
            self.drive = np.concatenate([self.drive, np.zeros((steps - len(self.drive), len(self.V)))])
        drive = np.ascontiguousarray(self.drive[:steps])
        self.drive = np.concatenate([self.drive[steps:], np.zeros((steps, len(self.V)))])
        self.spikes[:] = 0
        self.vmax[:] = -np.inf
        self.power_sum += _loop(self.V, self.Vx, self.armed, self.spikes, self.vmax, drive, self.node, self.el,
                                self.link, z, self.q, self.rest, self.dt, steps, self.cfg, self.vmin_o, self.vmax_o,
                                self.clip_o, self.preclip_o, self.slew_o, self.ev_step, self.ev_node, self.ev_n,
                                self.motors, self.t_step, self.ra_step, self.ra_node, self.ra_n) * (self.dt / DT)
        self.t_step += steps
        return self.spikes.copy()

    # --- state ---------------------------------------------------------------------------------------------------
    def snapshot(self):
        return dict(V=self.V.copy(), Vx=self.Vx.copy(), armed=self.armed.copy(), drive=self.drive.copy(),
                    rng=[g.bit_generator.state for g in self.rngs],
                    zbuf=None if self.zbuf is None else self.zbuf.copy(), zpos=self.zpos, t_step=self.t_step,
                    power_sum=self.power_sum, vmin=self.vmin_o.copy(), vmax=self.vmax_o.copy(),
                    clip=self.clip_o.copy(), preclip=self.preclip_o.copy(), slew=self.slew_o.copy(),
                    ev=(self.ev_step.copy(), self.ev_node.copy(), self.ev_n.copy()),
                    ra=(self.ra_step.copy(), self.ra_node.copy(), self.ra_n.copy()))

    def restore(self, s):
        self.V, self.Vx, self.armed, self.drive = s["V"].copy(), s["Vx"].copy(), s["armed"].copy(), s["drive"].copy()
        for g, st in zip(self.rngs, s["rng"]):
            g.bit_generator.state = st
        self.zbuf = None if s["zbuf"] is None else s["zbuf"].copy()
        self.zpos, self.t_step, self.power_sum = s["zpos"], s["t_step"], s["power_sum"]
        self.vmin_o, self.vmax_o, self.clip_o = s["vmin"].copy(), s["vmax"].copy(), s["clip"].copy()
        self.preclip_o, self.slew_o = s["preclip"].copy(), s["slew"].copy()
        self.ev_step, self.ev_node, self.ev_n = (a.copy() for a in s["ev"])
        self.ra_step, self.ra_node, self.ra_n = (a.copy() for a in s["ra"])

    def reset_obs(self):
        """Bench forks: restart the observation-only accumulators (no effect on dynamics)."""
        n = len(self.V)
        self.vmin_o, self.vmax_o = np.full(n, np.inf), np.full(n, -np.inf)
        self.clip_o, self.preclip_o, self.slew_o = np.zeros(n, np.int64), np.zeros(n), np.zeros(n)
        self.ev_n[0] = 0
        self.ra_n[0] = 0

    def rearms(self):
        k = int(self.ra_n[0])
        return self.ra_step[:k] * self.dt, self.ra_node[:k].copy()

    def events(self):
        """Motor events as (time s, motor index)."""
        k = int(self.ev_n[0])
        return self.ev_step[:k] * self.dt, self.ev_node[:k].copy()

    def power(self):
        return self.power_sum / max(self.t_step / self.ratio, 1)

    def arrays_hash(self):
        h = hashlib.sha256()
        for a in (self.node, self.el, self.link, self.keep, np.array(self.V)):
            h.update(np.ascontiguousarray(a).tobytes())
        return h.hexdigest()[:16]


class CatalogueBrain:
    """Life's brain: only stimulate, taste and step reach the circuit. log: passive per-tick record."""

    def __init__(self, seed, removed="none", ratio=1, noise="native", log=True, spec=None, scale=None):
        self.e = Engine(seed, removed=removed, ratio=ratio, noise=noise, spec=spec, scale=scale)
        ix = self.e.ix
        self.S, self.T, self.M = [ix["S0"], ix["S1"]], ix["T"], [ix["M0"], ix["M1"]]
        self.P, self.E = [ix["P0"], ix["P1"]], [ix["E0"], ix["E1"]]
        self.tick, self.log = 0, log
        self.pulses, self.tastes, self.rows = [], [], []
        self.rec_nodes = [ix[n] for n in ("E0", "E1", "P0", "P1", "B0", "B1", "X0", "X1", "M0", "M1")]

    def set_P(self, values):                       # privileged harness, before any step
        assert self.tick == 0
        for k in (0, 1):
            self.e.V[self.P[k]] = float(values[k])
        self.e.Vx[:] = self.e.V[self.e.link[1]]

    def stimulate(self, sensor, at):
        if self.log:
            self.pulses.append((self.tick * TICK + at, int(sensor)))
        self.e.pulse(self.S[sensor], PULSES * self.e.unit(), at, PULSE)

    def taste(self, value, at):
        if self.log:
            self.tastes.append((self.tick * TICK + at, float(value)))
        self.e.pulse(self.T, PULSES * self.e.unit() * value, at, PULSE)

    def step(self):
        sp = self.e.run_tick()
        if self.log:
            self.rows.append(self.e.V[self.rec_nodes].copy())
        self.tick += 1
        return [m for m, nd in enumerate(self.M) for _ in range(sp[nd])]

    def drive(self, sensor):                       # watching only (creature.watch prints it)
        return float(np.clip(self.e.V[self.P[sensor]] / V_TYP, 0, 1))


def factory(**kw):
    return lambda seed: CatalogueBrain(seed, **kw)

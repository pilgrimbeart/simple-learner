"""Action grid (work order 2026-11-20, sections 3-5): the D180 v1 brain with one of the 81 fixed variants, on the
unchanged engine, with a passive observer.

GridEngine subclasses D180's Engine (brain.py, read-only): the FULL variant graph is built and its mismatch drawn
before removals; node/edge order and RNG streams are D180's. run_tick calls _loop_obs, which calls the unchanged
mixed_feedback._step exactly as D180's _loop does and only READS afterwards. Extra observation (all from substep
states): per-tick substep counts of each motor above zero and not armed; per-edge gate factor sum and steps with an
open gate (the engine's gate definition clip(V_gate/volt, 0, 1)); per-node source events (rising through SPIKE).

GridBrain sees only stimulate/taste/step (Life's interface). Informed P is written by the harness at tick 0.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
from numba import njit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAT = ROOT / "lab/catalogue_brain_20261120"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(CAT))

from mixed_feedback import _step                               # noqa: E402
from units import DT, PULSE, TICK, V_TYP                       # noqa: E402
from brains.circuit import PULSES                              # noqa: E402
import brain as D180                                            # noqa: E402  (catalogue_brain_20261120/brain.py)

_spec = importlib.util.spec_from_file_location("action_grid_variants", HERE / "variants.py")
variants = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(variants)

CONFIGS = {c["id"]: c for c in variants.configurations()}
BASELINE = variants.BASELINE
REMOVALS = D180.REMOVALS


@njit(cache=True)
def _loop_obs(V, Vx, armed, spikes, vmax, drive, node, el, link, z, q, rest, dt, steps, cfg,
              vmin_o, vmax_o, clip_o, preclip_o, slew_o, ev_step, ev_node, ev_n, motors, t0, ra_step, ra_node, ra_n,
              tick, high_t, unarm_t, gsum, gopen, nspk, finite):
    """D180 _loop (identical _step calls) plus passive reads. high_t/unarm_t[tick, j]: substeps of motor j above zero /
    not armed; gsum/gopen[e]: gate factor summed / steps with gate factor > 0 (gated edges); nspk: node events."""
    n = V.shape[0]
    m = link.shape[1]
    dV, gross = np.empty(n), np.empty(n)
    power = 0.0
    cap, lo, hi = node[2], node[3], node[4]
    volt = cfg[0]
    for k in range(steps):
        Vold = V.copy()
        before = spikes.copy()
        was = armed.copy()
        power += _step(V, Vx, armed, spikes, vmax, drive[k], node, el, link, z[k], q, rest, dt, dV, gross, cfg)
        for i in range(n):
            var = (q * gross[i] + rest[i]) * dt
            pre = Vold[i] + (dt * dV[i] + np.sqrt(var) * z[k, i]) / cap[i]
            if not np.isfinite(pre):
                finite[0] = False
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
            nspk[i] += spikes[i] - before[i]
        for e in range(m):
            gi = link[2, e]
            if gi >= 0:
                g = min(max(V[gi] / volt, 0.0), 1.0)
                gsum[e] += g
                if g > 0.0:
                    gopen[e] += 1
        for j in range(motors.shape[0]):
            mm = motors[j]
            if V[mm] > 0.0:
                high_t[tick, j] += 1
            if not armed[mm]:
                unarm_t[tick, j] += 1
            if spikes[mm] > before[mm] and ev_n[0] < ev_step.shape[0]:
                ev_step[ev_n[0]] = t0 + k
                ev_node[ev_n[0]] = j
                ev_n[0] += 1
            if armed[mm] and not was[mm] and ra_n[0] < ra_step.shape[0]:
                ra_step[ra_n[0]] = t0 + k
                ra_node[ra_n[0]] = j
                ra_n[0] += 1
    return power


class GridEngine(D180.Engine):
    """D180 Engine on variant `config` (an id in PLAN.json). ticks: capacity of the per-tick observer arrays."""

    def __init__(self, seed, config=BASELINE, ticks=10000, **kw):
        cfg = CONFIGS[config]
        self.config = config
        super().__init__(seed, spec=lambda sides: variants.graph(cfg, sides), **kw)
        n, m = len(self.V), self.el.shape[1]
        self.cap_ticks = ticks
        self.high_t = np.zeros((ticks, 2), np.int64)
        self.unarm_t = np.zeros((ticks, 2), np.int64)
        self.gsum, self.gopen = np.zeros(m), np.zeros(m, np.int64)
        self.nspk = np.zeros(n, np.int64)
        self.finite = np.ones(1, np.bool_)
        self.tick = 0

    def run_tick(self):
        steps = self.tick_steps
        z = np.ascontiguousarray(self._z(steps))
        if len(self.drive) < steps:
            self.drive = np.concatenate([self.drive, np.zeros((steps - len(self.drive), len(self.V)))])
        drive = np.ascontiguousarray(self.drive[:steps])
        self.drive = np.concatenate([self.drive[steps:], np.zeros((steps, len(self.V)))])
        self.spikes[:] = 0
        self.vmax[:] = -np.inf
        if self.tick >= self.cap_ticks:
            raise RuntimeError("observer tick capacity exceeded")
        self.power_sum += _loop_obs(self.V, self.Vx, self.armed, self.spikes, self.vmax, drive, self.node, self.el,
                                    self.link, z, self.q, self.rest, self.dt, steps, self.cfg, self.vmin_o, self.vmax_o,
                                    self.clip_o, self.preclip_o, self.slew_o, self.ev_step, self.ev_node, self.ev_n,
                                    self.motors, self.t_step, self.ra_step, self.ra_node, self.ra_n,
                                    self.tick, self.high_t, self.unarm_t, self.gsum, self.gopen, self.nspk,
                                    self.finite) * (self.dt / DT)
        self.t_step += steps
        self.tick += 1
        return self.spikes.copy()

    def overflow(self):
        return bool(self.ev_n[0] >= len(self.ev_step) or self.ra_n[0] >= len(self.ra_step))

    def edge_names(self):
        return [self.enames[j] for j in self.keep]

    def realised(self):
        """Realised (mismatched) physical limits of the arrays this job runs, as D180 checks.physical computes them."""
        from units import C_MAX, I_MIN, R_MAX, SLEW, TAU_LEAK, TAU_LOOP, TAU_MAX
        node, el, link = self.node, self.el, self.link
        bias, leak, cap = node[0], node[1], node[2]
        R = 1 / leak[leak > 0]
        tau = R * cap[leak > 0]
        cur = np.r_[np.abs(el[0]), np.abs(bias[bias != 0])]
        sl = np.abs(el[0]) / cap[link[0]]
        selfl = link[0] == link[1]
        loop = float((np.abs(el[0] * el[2]) / cap[link[0]])[selfl].max()) if selfl.any() else 0.0
        pulse_slew = PULSES * self.unit() / cap[[self.ix["S0"], self.ix["S1"], self.ix["T"]]].min()
        w = dict(C_max=float(cap.max()), R_max=float(R.max()), I_min=float(cur.min()), slew_max=float(sl.max()),
                 self_loop_max=loop, tau_min=float(tau.min()), tau_max=float(tau.max()), pulse_slew=float(pulse_slew))
        ok = dict(C=w["C_max"] <= C_MAX, R=w["R_max"] <= R_MAX, I=w["I_min"] >= I_MIN, slew=w["slew_max"] <= SLEW,
                  loop=loop <= 1 / TAU_LOOP, tau=w["tau_min"] >= TAU_LEAK and w["tau_max"] <= TAU_MAX,
                  pulse=w["pulse_slew"] <= SLEW)
        w["failed"] = sorted(k for k, v in ok.items() if not v)
        return w


class GridBrain:
    """Life's brain: only stimulate, taste and step reach the circuit. trace: the D180 ten-node per-tick record."""

    def __init__(self, seed, config=BASELINE, removed="none", ratio=1, noise="native", trace=False, ticks=10000):
        self.e = GridEngine(seed, config=config, removed=removed, ratio=ratio, noise=noise, ticks=ticks)
        ix = self.e.ix
        self.S, self.T, self.M = [ix["S0"], ix["S1"]], ix["T"], [ix["M0"], ix["M1"]]
        self.P = [ix["P0"], ix["P1"]]
        self.tick = 0
        self.pulses, self.tastes = [], []
        self.trace = trace
        self.rec_nodes = [ix[n] for n in ("E0", "E1", "P0", "P1", "B0", "B1", "X0", "X1", "M0", "M1")]
        self.rows = np.zeros((ticks, 10), np.float32) if trace else None
        self.P_rows = np.zeros((ticks, 2), np.float32)          # P0, P1 per tick (drift / false writes), always

    def set_P(self, values):                       # privileged harness, before any step
        assert self.tick == 0
        for k in (0, 1):
            self.e.V[self.P[k]] = float(values[k])
        self.e.Vx[:] = self.e.V[self.e.link[1]]

    def stimulate(self, sensor, at):
        self.pulses.append((self.tick * TICK + at, int(sensor)))         # observer record (physical onset)
        self.e.pulse(self.S[sensor], PULSES * self.e.unit(), at, PULSE)

    def taste(self, value, at):
        self.tastes.append((self.tick * TICK + at, float(value)))
        self.e.pulse(self.T, PULSES * self.e.unit() * value, at, PULSE)

    def step(self):
        sp = self.e.run_tick()
        if self.trace:
            self.rows[self.tick] = self.e.V[self.rec_nodes]
        self.P_rows[self.tick] = self.e.V[self.P]
        self.tick += 1
        return [m for m, nd in enumerate(self.M) for _ in range(sp[nd])]

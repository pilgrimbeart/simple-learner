"""fast.py: the brains' once-a-tick step compiled (main session, 2026-11-06), for speed alone: lives identical to seconds.py's.

`fast_cls(cls)` replaces seconds.py's SecondsModel in a base-circuit or bank class (table.Circuit, bits_bank.Recorder) by FastModel, whose
step is one numba function doing what the chain of Python steps did, in the same order and with the same arithmetic:
  bank:     universal_v.V.step (tau_E 0 only) -> universal.U.step -> story1.RunLimit.step -> story1.Watched.step -> drivebal.DriveBal.step
            -> seconds.SecondsModel.step, with seconds._matched_step's filtering (a pause returns no beats)
  circuit:  story1.RunLimit.step -> story1.Watched.step -> seconds.SecondsModel.step
Between steps the state the chain reads and writes lives in two arrays (S, the state; Q, the numbers, fixed at birth), and is the truth;
the Python attributes of the same names are brought up to date before a taste (whose Python code is unchanged) and written back after
it; stimulate (each pulse) writes its pulse straight into the arrays, and `t` is kept current after every step. What is checked:
lab/speed_fingerprint.py, every life identical to the uncompiled engine's."""
from __future__ import annotations

import math

import numpy as np
from numba import njit

from stage2_lang import seconds as SEC

# the state: float slots (None as NaN)
SF = ("t", "dq", "phase", "phase1", "last_drive", "last_food", "run_from", "x", "e", "b", "start", "Tr", "F", "P", "rate", "ate_at",
      "est", "sd", "g0", "g1", "sd0", "last0", "last1", "trace_t", "food", "was_on", "seen0", "seen1", "was_driving", "pulses", "drives",
      "pausing", "open", "znext")
IX = {k: i for i, k in enumerate(SF)}
INTS = {"food", "seen0", "seen1", "pulses", "drives"}
BOOLS = {"was_on", "was_driving", "pausing", "open"}
OPT = {"run_from", "b"}
# the numbers, fixed at birth (as each layer reads them, with its default)
QK = ("lone", "hold", "bored", "drift", "drive", "run", "scan", "paired", "sync", "run_max", "anti", "N", "out", "rel", "eta", "tau_bD",
      "prior", "tau_bU", "tau_v", "tau_g", "tau_hold", "tau_p", "win", "jit", "gate", "theta_p", "off", "pausek", "hasU", "hasDB")
QX = {k: i for i, k in enumerate(QK)}
EVMAX = 4096


def _numbers(b, hasU, hasDB):
    p = b.p
    g = p.get
    v = dict(lone=p["lone"], hold=p["hold"], bored=p["bored"], drift=p["drift"], drive=p["drive"], run=p["run"], scan=p["scan"],
             paired=float(bool(g("paired"))), sync=float(bool(g("sync"))), run_max=p["run_max"], anti=float(bool(g("anti"))),
             N=g("N", 1e12), out=g("out", 0), rel=float(bool(g("rel"))), eta=g("eta", 0.01), tau_bD=g("tau_b", 20.0),
             prior=g("prior", 0.0), tau_bU=g("tau_b", 1000.0), tau_v=g("tau_v", 40.0), tau_g=g("tau_g", 30.0),
             tau_hold=g("tau_hold", 300.0), tau_p=g("tau_p", 30.0), win=g("win", 200.0), jit=float(bool(g("jit", 1))),
             gate=g("gate", 15.0), theta_p=g("theta_p", 3.0), off=g("off", 1.0), pausek=float(bool(g("pausek", 1))),
             hasU=float(hasU), hasDB=float(hasDB))
    return np.array([float(v[k]) for k in QK])


@njit(cache=True)
def _sort_ev(et, es, n):
    """Insertion sort of (time, sensor) pairs, as Python sorts tuples."""
    for i in range(1, n):
        a, s = et[i], es[i]
        j = i - 1
        while j >= 0 and (et[j] > a or (et[j] == a and es[j] > s)):
            et[j + 1], es[j + 1] = et[j], es[j]
            j -= 1
        et[j + 1], es[j + 1] = a, s


@njit(cache=True)
def _crossings(phase, w, a, span, out, n0):
    """seconds._crossings into out[n0:]: moments in (a, a + span] when phase + w (t - a) passes a whole number. Returns the new count."""
    if w <= 0:
        return n0
    n = int(math.floor(phase + w * span))
    k = n0
    for j in range(1, n + 1):
        out[k] = a + (j - phase) / w
        k += 1
    return k


@njit(cache=True)
def _beat(S, Q, r, on, a, b, t0, bm, bt, nb, tmp):
    """seconds.SecondsModel._beat: beats (motor bm, moment within the tick bt) from a to b at rate r. Returns the new count."""
    g0, g1 = S[18], S[19]
    span = b - a
    if span <= 0:
        return nb
    if Q[7] != 0.0 and g1 != g0 and on:
        hi = max(g0, g1)
        w = r * hi
        n = _crossings(S[2], w, a, span, tmp, 0)
        for j in range(n):
            tau = tmp[j]
            S[3] += min(g0, g1) / hi
            if S[3] >= 1:
                S[3] -= 1
                bm[nb], bt[nb] = 0, tau - t0
                bm[nb + 1], bt[nb + 1] = 1, tau - t0
                nb += 2
            else:
                bm[nb], bt[nb] = (0 if g0 > g1 else 1), tau - t0
                nb += 1
        S[2] = (S[2] + w * span) % 1.0
        return nb
    w = r * g0
    n = _crossings(S[2], w, a, span, tmp, 0)
    S[2] = (S[2] + w * span) % 1.0
    if not on:
        for j in range(n):
            bm[nb], bt[nb] = 0, tmp[j] - t0
            nb += 1
        return nb
    if g1 == g0:
        for j in range(n):
            bm[nb], bt[nb] = 0, tmp[j] - t0
            bm[nb + 1], bt[nb + 1] = 1, tmp[j] - t0
            nb += 2
        return nb
    w1 = r * g1
    n1 = _crossings(S[3], w1, a, span, tmp, n)
    S[3] = (S[3] + w1 * span) % 1.0
    for j in range(n):
        bm[nb], bt[nb] = 0, tmp[j] - t0
        nb += 1
    for j in range(n, n1):
        bm[nb], bt[nb] = 1, tmp[j] - t0
        nb += 1
    return nb


@njit(cache=True)
def _seconds_step(S, Q, et, es, nev, dt, bm, bt, tmp, ot, os_):
    """seconds.SecondsModel.step (its _events first). Returns the count of beats."""
    t0 = S[0]
    t1 = t0 + dt
    # _events: the pulses as the layers above left `seen`
    _sort_ev(et, es, nev)
    w0, w1 = int(S[26]), int(S[27])
    h0 = 0
    for j in range(nev):
        if es[j] == 0:
            h0 += 1
    h1 = nev - h0
    n = 0
    if w0 == h0 and w1 == h1:
        for j in range(nev):
            ot[n], os_[n] = et[j], es[j]
            n += 1
    elif w0 + w1 == 0:
        n = 0
    elif w0 + w1 == nev and (w0 == 0 or w1 == 0):
        k = 0 if w0 else 1
        for j in range(nev):
            ot[n], os_[n] = et[j], k
            n += 1
    else:
        for s in range(2):
            want = w0 if s == 0 else w1
            have = h0 if s == 0 else h1
            skip = have - want if want <= have else 0
            c = 0
            for j in range(nev):
                if es[j] == s:
                    if c >= skip:
                        ot[n], os_[n] = et[j], es[j]
                        n += 1
                    c += 1
        _sort_ev(ot, os_, n)
    S[26], S[27] = 0.0, 0.0
    lone_frac, hold, bored = Q[0], Q[1], Q[2]
    S[1] = max(0.0, S[1] - Q[3] * dt)
    l0, l1 = np.nan, np.nan
    nb = 0
    i = 0
    cur = t0
    while True:
        while i < n and ot[i] <= cur + 1e-15:
            tau, s = ot[i], os_[i]
            tau = max(tau, t0)
            if s == int(S[24]):
                S[4] = tau
                S[5] = tau
            else:
                S[4] = -1e9
            if s == 0:
                l0 = tau
            else:
                l1 = tau
            i += 1
        driving = cur - S[4] < hold
        running = (not driving) and cur - S[5] > bored
        on = driving or running
        if on and not S[25]:
            if lone_frac and driving and S[2] < lone_frac:
                bm[nb], bt[nb] = 1, cur - t0
                nb += 1
            if Q[8] != 0.0:
                S[3] = S[2]
        S[25] = 1.0 if on else 0.0
        nxt = t1
        if i < n:
            nxt = min(nxt, max(ot[i], cur))
        if driving:
            nxt = min(nxt, S[4] + hold)
        elif not running:
            nxt = min(nxt, S[5] + bored + 1e-12)
        b = max(cur, nxt)
        if b <= cur and b < t1:
            b = min(t1, cur + 1e-9)
        r = Q[4] if driving else Q[5] if running else Q[6]
        nb = _beat(S, Q, r, on, cur, b, t0, bm, bt, nb, tmp)
        cur = b
        if cur >= t1 - 1e-15 and i >= n:
            break
    if not math.isnan(l0):
        S[21] = l0
    if not math.isnan(l1):
        S[22] = l1
    S[0] = t1
    return nb


@njit(cache=True)
def step(S, Q, E, I, F, nev, dt, flags):
    """The whole chain once. flags[0]: the pause switched on (U's on_at); flags[1]: DriveBal's trace point due. Returns the count of
    beats (0 if a pause filtered them)."""
    et, ot = E[0], E[1]
    es, os_, bm = I[0], I[1], I[2]
    bt, tmp = F[0], F[1]
    flags[0], flags[1], flags[2] = 0, 0, 0
    t = S[0]
    paused_out = False
    if Q[28] != 0.0:                                    # universal.U.step
        prior = Q[16]
        S[11] += (prior - S[11]) * dt / (Q[17] if S[11] > prior else Q[18])
        S[12] *= 1 - dt / Q[19]
        S[13] *= 1 - dt / (Q[20] if S[31] else Q[21])
        w = Q[22]
        S[14] *= 1 - dt / w
        if Q[23] != 0.0:
            S[17] = S[20] if S[14] * 32.0 / w < Q[24] else 0.0
        on = S[13] >= Q[25] or (S[31] and S[13] > Q[26])
        if on and not S[31]:
            flags[0] = 1
        S[31] = 1.0 if (on and Q[27] != 0.0) else 0.0
        if S[32]:
            s = S[26] + S[27]
            S[26], S[27] = 0.0, 0.0
            S[26 + int(S[24])] = s
        if S[31] and t - S[15] < S[16]:
            S[26], S[27] = 0.0, 0.0
            paused_out = True
    # story1.RunLimit.step
    hold, bored = Q[1], Q[2]
    running = t - S[4] >= hold and t - S[5] > bored
    if not running:
        S[6] = np.nan
    elif math.isnan(S[6]):
        S[6] = t
    elif t - S[6] > Q[9]:
        S[5], S[6] = t, np.nan
    # story1.Watched.step
    if S[26]:
        S[21] = t
    if S[27]:
        S[22] = t
    if Q[29] != 0.0:                                    # drivebal.DriveBal.step, around SecondsModel.step
        Fs = S[26 + int(S[24])]
        nb = _seconds_step(S, Q, et, es, nev, dt, bm, bt, tmp, ot, os_)
        tt = S[0]
        driving = tt - S[4] < hold
        if driving and not S[28]:
            if Q[10] != 0.0 and int(S[30]) % 2 == 1:
                S[8] = -S[8]
            else:
                sd = S[17] / np.sqrt(1 + S[30] / Q[11])
                S[8] = sd * S[33]                   # DriveBal's own stream's next normal, drawn ahead (flags[2]: draw another)
                flags[2] = 1
            S[29], S[10] = 0.0, tt
            v = S[7] + S[8]
            S[18], S[19] = np.exp(v / 2), np.exp(-v / 2)
        if driving:
            S[29] += Fs
        if S[28] and not driving:
            y = S[29] if Q[12] == 0 else tt - S[10]
            if math.isnan(S[9]):
                S[9] = y
            d = (y - S[9]) / max(S[9], 1.0) if Q[13] != 0.0 else y - S[9]
            S[7] = min(max(S[7] + Q[14] * d * S[8], -1.4), 1.4)
            S[9] += (y - S[9]) / Q[15]
            S[30] += 1
            S[18], S[19] = np.exp(S[7] / 2), np.exp(-S[7] / 2)
        S[28] = 1.0 if driving else 0.0
        if math.isnan(S[23]) or tt - S[23] >= 100.0:
            S[23] = tt
            flags[1] = 1
    else:
        nb = _seconds_step(S, Q, et, es, nev, dt, bm, bt, tmp, ot, os_)
    if paused_out:
        return 0
    return nb


class FastModel(SEC.SecondsModel):
    """SecondsModel whose step is compiled (fast.step); see the module's docstring."""

    _packed = False

    def stimulate(self, sensor, at):
        if not self._packed:
            return SEC.SecondsModel.stimulate(self, sensor, at)
        n = self._nev
        self._et[n], self._es[n] = self.t + at, sensor
        self._nev = n + 1
        self._S[26 + sensor] += 1

    def _pack(self):
        from universal import U
        from drivebal import DriveBal
        self._hasU, self._hasDB = isinstance(self, U), isinstance(self, DriveBal)
        if self._hasU and self.p.get("tau_E", 0.0):
            raise ValueError("fast: the bank's tau_E is not compiled")
        self._Q = _numbers(self, self._hasU, self._hasDB)
        self._S = np.zeros(len(SF))
        self._S[IX["trace_t"]] = np.nan
        self._E, self._I, self._F = np.zeros((2, EVMAX)), np.zeros((3, EVMAX), np.int64), np.zeros((2, EVMAX))
        self._et, self._es = self._E[0], self._I[0]
        self._bm, self._bt = self._I[2], self._F[0]
        self._dt = SEC._tick()
        self._flags = np.zeros(3, np.int64)
        self._nev = 0
        self._rng_db = getattr(self, "rng", None) if self._hasDB else np.random.default_rng(0)
        self._present = {k for k in SF if k in ("sd", "g0", "g1", "seen0", "seen1", "last0", "last1", "trace_t", "znext") or hasattr(self, k)}
        self._to_arrays()
        self._S[33] = self._rng_db.standard_normal() if self._hasDB else 0.0
        for t, s in self._ev:
            self._et[self._nev], self._es[self._nev] = t, s
            self._nev += 1
        self._ev = []
        self._packed = True

    def _to_arrays(self):
        S, p = self._S, self.p
        for k in SF:
            if k in ("sd", "g0", "g1"):
                v = p.get(k, 0.3 if k == "sd" else 1.0)
            elif k in ("seen0", "seen1"):
                v = self.seen[int(k[-1])]
            elif k in ("last0", "last1"):
                v = self.last[int(k[-1])]
            elif k == "znext":
                continue
            elif k == "trace_t":
                tr = getattr(self, "trace", None)
                v = tr[-1][0] if tr else np.nan
            else:
                v = getattr(self, k, 0.0)
            S[IX[k]] = np.nan if v is None else float(v)

    def _to_attrs(self):
        S, p = self._S, self.p
        for k in self._present:
            v = S[IX[k]]
            if k in ("sd", "g0", "g1"):
                if k in p or k != "sd" or self._hasDB:
                    p[k] = float(v)
            elif k in ("seen0", "seen1"):
                self.seen[int(k[-1])] = int(v)
            elif k in ("last0", "last1"):
                self.last[int(k[-1])] = float(v)
            elif k in ("trace_t", "znext"):
                pass
            elif k in OPT:
                setattr(self, k, None if math.isnan(v) else float(v))
            elif k in INTS:
                setattr(self, k, int(v))
            elif k in BOOLS:
                setattr(self, k, bool(v))
            elif hasattr(self, k):
                setattr(self, k, float(v))

    def fast_step(self):
        if not self._packed:
            self._pack()
        S = self._S
        t_before = S[0]
        nb = step(S, self._Q, self._E, self._I, self._F, self._nev, self._dt, self._flags)
        if self._flags[2]:
            S[33] = self._rng_db.standard_normal()
        self._nev = 0
        if self._flags[0]:
            self.on_at.append(t_before)
        if self._flags[1]:
            self.trace.append((S[0], S[7]))
        self.t = S[0]
        bm, bt = self._bm, self._bt
        self.beats = [(int(bm[j]), float(bt[j])) for j in range(nb)]
        return [m for m, _ in self.beats]


def _synced_taste(cls):
    base = cls.taste

    def taste(self, value, at):
        if not self._packed:
            return base(self, value, at)
        self._to_attrs()
        try:
            return base(self, value, at)
        finally:
            self._to_arrays()
    return taste


_CACHE = {}

# The Python this module copies, by hash of its source: if any of it changes, fast_cls refuses, so the copy can't go stale unseen.
# After changing one of these, change fast.step to match, re-run lab/speed_fingerprint.py check and lab/speed_crosscheck.py, then
# update the hash here.
COPIED = {
    "universal_v.V.step": "c06bc47a3a673214",
    "universal.U.step": "b6c5c17f8f92c37b",
    "story1.RunLimit.step": "63a982fa3835ba39",
    "story1.Watched.step": "1e7de582113d4606",
    "drivebal.DriveBal.step": "79534eec07dd871a",
    "drivebal.DriveBal._set": "6b227b451ef50e22",
    "seconds.SecondsModel.step": "3f7edb538ae612aa",
    "seconds.SecondsModel._events": "fb39c482fde43065",
    "seconds.SecondsModel._beat": "e19b3a0b693f47f1",
    "seconds._crossings": "7de391fae0664178",
    "seconds._matched_step": "edad5a21221da087",
    "seconds.SecondsModel.stimulate": "bed7297aed173ed5",       # FastModel.stimulate stands in for these two
    "discrete.model.Model.stimulate": "8513eb84f2154712",
}
_CHECKED = []


def _check_copied():
    import hashlib
    import importlib
    import inspect
    bad = []
    for k, h in COPIED.items():
        mod, *path = k.split(".")
        obj = importlib.import_module("stage2_lang.seconds" if mod == "seconds" else mod)
        if mod == "discrete":
            obj = importlib.import_module("discrete." + path.pop(0))
        for a in path:
            obj = getattr(obj, a)
        if hashlib.sha256(inspect.getsource(obj).encode()).hexdigest()[:16] != h:
            bad.append(k)
    if bad:
        raise RuntimeError(f"fast.py copies Python that has changed: {bad}; bring fast.step up to date (see COPIED)")
    _CHECKED.append(True)


def fast_cls(cls):
    """cls (a base-circuit or bank class built on discrete.model.Model) with its step compiled; as seconds.seconds_cls otherwise."""
    if cls in _CACHE:
        return _CACHE[cls]
    from discrete import model as M
    if not _CHECKED:
        _check_copied()
    allowed = {k.split(".", 1)[1] for k in COPIED} | {"Model.step"}
    for c in cls.__mro__:                               # no layer with a step of its own that fast.step doesn't copy
        if "step" in c.__dict__ and f"{c.__qualname__}.step" not in allowed:
            raise RuntimeError(f"fast.py doesn't compile {c.__module__}.{c.__qualname__}.step")
    S = type(cls.__name__ + "F", (cls, FastModel), {})
    S.taste = _synced_taste(type("T", (S,), {"taste": SEC._timed_taste(S)}))
    S.step = FastModel.fast_step
    assert issubclass(cls, M.Model)
    _CACHE[cls] = S
    return S

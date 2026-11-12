"""couple_local.py: understanding as coupling, made local (D52 next). Each motor is a unit with its own gain (its rate's log, x_m) and
its own counter: how tightly its own beats and the eyes go together (I(A^m_t; S_t+1) + I(S_t; A^m_t+1), A^m whether it beat in a 50 ms
bin, S which eyes pulsed). Each unit nudges its own gain by the classic local rule, weight perturbation (SPSA): every WIN s it tries
x_m + delta_m, delta_m a fresh +-D of its own (independent of the other unit's), and moves x_m by ETA times (its coupling less its
running mean) times the sign of delta_m. Nothing is shared but the body and the world. The units tune while nothing tastes (play) and
stop at the first real taste (work), keeping x_m.
local:drive: as local:turns, each unit counting only the bins while driving (it knows from its own drive input): what the
knob acts on, without motor 0's scanning.
local:turns: each unit its own wide search (golden section on its own log rate, judged by its own normalised coupling), started
at its own random moment (0 to 120 s), so units mostly take turns with no coordinator.
local:norm: each unit's coupling as a share of its own activity's entropy (bits explained per bit of its own beating), since raw
coupling in fixed bins rewarded slowing down (traced: a unit beating in nearly every bin carries little information).

Offline first (D51's saved bins): motor 1's own coupling peaks at the right balance in every body from 60 s, motor 0's in 40 to 55%
(it also does all the scanning).

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/couple_local.py [PAIRS] [s98000]"""
import math
import pickle
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
OCCAM = 1.1
import numpy as np

import couple_search as CS
import play4 as P4
import stage3_random as R

BIN, WIN = 0.05, 20.0
D = 0.15                                        # each unit's perturbation of its own log rate
ETA = 0.1                                       # its step per bit a second of coupling above its running mean
ETA_NORM = 1.0                                  # local:norm: its step per unit of normalised coupling (peaks stand about .1 above the median)
TAU = 5                                         # windows: the running mean's memory


def _mi(J):
    n = J.sum()
    if n == 0:
        return 0.0
    P = J / n
    px, py = P.sum(1), P.sum(0)
    nz = P > 0
    I = float((P[nz] * np.log2(P[nz] / np.outer(px, py)[nz])).sum())
    return I - ((nz.sum() - 1) - (np.count_nonzero(px) - 1) - (np.count_nonzero(py) - 1)) / (2 * n * math.log(2))


class UnitSearch:
    """One unit's own wide search over its own log rate: golden section over [-1.5, 1.5], each point judged by WIN s of the unit's
    own normalised coupling; it starts at its own random moment, so units mostly take turns without any coordinator."""

    def __init__(self, start):
        self.start, self.lo, self.hi = start, -1.5, 1.5
        self.c, self.d = self.hi - CS.PHI * (self.hi - self.lo), self.lo + CS.PHI * (self.hi - self.lo)
        self.fc = self.fd = None
        self.queue = ["c", "d"]
        self.done, self.x = False, 0.0

    def point(self, t):
        if self.done or t < self.start:
            return self.x
        return getattr(self, self.queue[0])

    def judge(self, f):
        which = self.queue.pop(0)
        setattr(self, "f" + which, f)
        if not self.queue:
            if self.fc >= self.fd:
                self.hi, self.d, self.fd = self.d, self.c, self.fc
                self.c = self.hi - CS.PHI * (self.hi - self.lo)
                self.queue = ["c"]
            else:
                self.lo, self.c, self.fc = self.c, self.d, self.fd
                self.d = self.lo + CS.PHI * (self.hi - self.lo)
                self.queue = ["d"]
            if self.hi - self.lo < 0.2:
                self.done, self.x = True, (self.lo + self.hi) / 2


class LocalCouple:
    def __init__(self, seed, p):
        from stage2_lang.seconds import seconds_cls
        import table as T
        self.rng = np.random.default_rng(seed + 44_000_017)
        self.dt = p["dt"]
        self.forager = seconds_cls(T.Circuit)(seed, T.numbers(seed, {"sync": 1}))
        self.clock, self.t = 0.0, 0.0
        self.beats = []
        self.x = np.zeros(2)                            # each unit's own log rate
        self.delta = self.rng.choice((-D, D), 2)
        self.mean = [None, None]
        self.J = [[np.zeros((2, 4)), np.zeros((4, 2))] for _ in (0, 1)]   # per unit: (own beat then eyes), (eyes then own beat)
        self.s_bin, self.a_bin, self.prev = 0, [0, 0], None
        self.next_bin, self.win_end = BIN, WIN
        self.working, self.est, self.log = False, None, []
        self.norm = p.get("norm", False) or p.get("turns", False)
        self.driveonly = p.get("driveonly", False)
        self.joint = p.get("joint", False)              # judge by the joint coupling (each unit sees its neighbour's beats: local here)
        self.J4 = [np.zeros((4, 4)), np.zeros((4, 4))]     # count only bins while driving: what the knob acts on, without the scan
        self.turns = [UnitSearch(float(self.rng.uniform(0, 120))) for _ in (0, 1)] if p.get("turns") else None
        self._apply()

    def _apply(self):
        if self.turns:
            x = self.x if self.working else np.array([u.point(self.clock) for u in self.turns])
            p = self.forager.p
            p["g0"], p["g1"] = math.exp(x[0]), math.exp(x[1])
            return
        x = self.x + (0 if self.working else self.delta)
        p = self.forager.p
        p["g0"], p["g1"] = math.exp(x[0]), math.exp(x[1])

    def stimulate(self, sensor, at):
        self.s_bin |= 1 << sensor
        self.forager.stimulate(sensor, at)

    def taste(self, value, at):
        if value != 0 and not self.working:             # the world has begun to matter: work, with what play found
            self.working = True
            self.est = float(self.x[0] - self.x[1])      # the balance, log(g0 / g1), as the other arms. knob
            self._apply()
        self.forager.taste(value, at)

    def _window(self):
        jc = None
        if self.joint:
            jc = (_mi(self.J4[0]) + _mi(self.J4[1])) / BIN
            self.J4[0][:], self.J4[1][:] = 0, 0
        for m in (0, 1):
            c = (_mi(self.J[m][0]) + _mi(self.J[m][1])) / BIN
            if jc is not None:
                self.J[m][0][:], self.J[m][1][:] = 0, 0
                c = jc
                if self.turns:
                    u = self.turns[m]
                    if not u.done and self.clock - WIN >= u.start - 1e-9:
                        u.judge(c)
                    self.x[m] = u.point(self.clock) if not u.done else u.x
                continue
            if self.norm:                               # as a share of its own activity's entropy (the uncertainty coefficient):
                pa = self.J[m][0].sum(1) / max(self.J[m][0].sum(), 1)       # so no rate is rewarded for its own sake
                h = float(-(pa[pa > 0] * np.log2(pa[pa > 0])).sum())
                c = c * BIN / h if h > 0.05 else 0.0
            self.J[m][0][:], self.J[m][1][:] = 0, 0
            if self.turns:
                u = self.turns[m]
                if not u.done and self.clock - WIN >= u.start - 1e-9:
                    u.judge(c)
                self.x[m] = u.point(self.clock) if not u.done else u.x
                continue
            if self.mean[m] is None:
                self.mean[m] = c
            else:
                self.x[m] += (ETA_NORM if self.norm else ETA) * (c - self.mean[m]) * np.sign(self.delta[m])
                self.mean[m] += (c - self.mean[m]) / TAU
            self.x[m] = float(np.clip(self.x[m], -1.5, 1.5))
        self.log.append((self.clock, tuple(self.x)))
        self.delta = self.rng.choice((-D, D), 2)
        self._apply()

    def step(self):
        out = self.forager.step()
        self.beats = list(getattr(self.forager, "beats", None) or [])
        for m, _ in self.beats:
            self.a_bin[m] = 1
        self.clock += self.dt
        self.t = self.clock
        if self.clock >= self.next_bin:
            cur = (self.s_bin, tuple(self.a_bin))
            f = self.forager
            driving = f.t - f.last_drive < f.p["hold"]  # (a motor unit knows it is driving from its own drive input)
            if self.prev is not None and not self.working and getattr(self, "joint", False):   # both units' beats and the eyes
                a_prev = self.prev[1][0] | (self.prev[1][1] << 1)
                self.J4[0][a_prev, cur[0]] += 1             # actions then senses
                self.J4[1][self.prev[0], cur[1][0] | (cur[1][1] << 1)] += 1   # senses then actions
            if self.prev is not None and not self.working and (driving or not self.driveonly):
                for m in (0, 1):
                    self.J[m][0][self.prev[1][m], cur[0]] += 1
                    self.J[m][1][self.prev[0], cur[1][m]] += 1
            self.prev, self.s_bin, self.a_bin = cur, 0, [0, 0]
            self.next_bin += BIN
        if not self.working and self.clock >= self.win_end:
            self._window()
            self.win_end = self.clock + WIN
        return out



class HalfCentre(LocalCouple):
    """Sepulchre's half-centre as turn-taking between the two motor units (the user, 2026-11-12). A unit whose drive is highest, when
    none is searching, takes a turn: a golden-section search on its own log rate, each point judged by WIN s of its own normalised
    coupling counted while driving, ending with an Occam check against its value before the turn (kept only if 10% better). While it
    searches, the other unit's rate is held (inhibition). At the turn's end its drive falls to 0 (fatigue: bored); if its rate moved by
    more than MOVED, the other unit's landscape has changed, so the other rebounds (drive 1). Play is over when no unit has drive left,
    or at the first taste. The bracket of a unit's later turns narrows (W0, then W1): it is refining."""
    W0, W1, TOL, MOVED = 1.5, 0.5, 0.15, 0.1
    active = None                                       # (until the first turn starts)

    def __init__(self, seed, p):
        super().__init__(seed, {**p, "norm": True, "driveonly": not p.get("joint")})
        self.turns = None
        self.drive = 1.0 + 0.01 * self.rng.random(2)    # both curious at birth; the tie broken by each unit's own noise
        self.n_turns = [0, 0]
        self.active, self.search = None, None
        self.history = []                               # (time, unit, x before, x after)
        self._start_turn()

    def _start_turn(self):
        m = int(np.argmax(self.drive))
        if self.drive[m] < 0.5:
            self.active = None                          # every unit bored: play is over (until a taste ends it anyway)
            self._apply()
            return
        w = self.W0 if self.n_turns[m] == 0 else self.W1
        lo, hi = max(-1.5, self.x[m] - w), min(1.5, self.x[m] + w)
        self.active = m
        self.search = dict(lo=lo, hi=hi, c=hi - CS.PHI * (hi - lo), d=lo + CS.PHI * (hi - lo), fc=None, fd=None,
                           queue=["c", "d"], x0=float(self.x[m]), final=None)
        self._apply()

    def _point(self):
        s = self.search
        if s["final"] is not None:
            return s["final"][0][1]
        return s[s["queue"][0]]

    def _apply(self):
        x = self.x.copy()
        if not self.working and self.active is not None:
            x[self.active] = self._point()
        p = self.forager.p
        p["g0"], p["g1"] = math.exp(x[0]), math.exp(x[1])

    def _window(self):
        m = self.active
        cs = []
        for u in (0, 1):
            c = (_mi(self.J[u][0]) + _mi(self.J[u][1])) / BIN
            pa = self.J[u][0].sum(1) / max(self.J[u][0].sum(), 1)
            h = float(-(pa[pa > 0] * np.log2(pa[pa > 0])).sum())
            cs.append(c * BIN / h if h > 0.05 else 0.0)
            self.J[u][0][:], self.J[u][1][:] = 0, 0
        if self.joint:                                  # both units' beats and the eyes, in 4 x 4 counts (D51)
            jc = (_mi(self.J4[0]) + _mi(self.J4[1])) / BIN
            self.J4[0][:], self.J4[1][:] = 0, 0
            cs = [jc, jc]
        if m is None:
            return
        self.evals = getattr(self, "evals", [])
        self.evals.append((round(self.clock), m, round(self._point(), 2), round(cs[m], 3), round(cs[1 - m], 3)))
        f, s = cs[m], self.search
        if s["final"] is not None:                      # the Occam check: before, then the answer
            name, val = s["final"].pop(0)
            s["ff"] = {**s.get("ff", {}), name: f}
            if not s["final"]:
                new = s["ans"] if s["ff"]["answer"] > OCCAM * s["ff"]["before"] else s["x0"]
                self._end_turn(m, new)
                return
            self._apply()
            return
        which = s["queue"].pop(0)
        s["f" + which] = f
        if not s["queue"]:
            if s["fc"] >= s["fd"]:
                s["hi"], s["d"], s["fd"] = s["d"], s["c"], s["fc"]
                s["c"] = s["hi"] - CS.PHI * (s["hi"] - s["lo"])
                s["queue"] = ["c"]
            else:
                s["lo"], s["c"], s["fc"] = s["c"], s["d"], s["fd"]
                s["d"] = s["lo"] + CS.PHI * (s["hi"] - s["lo"])
                s["queue"] = ["d"]
            if s["hi"] - s["lo"] < self.TOL:
                s["ans"] = (s["lo"] + s["hi"]) / 2
                s["final"] = [("before", s["x0"]), ("answer", s["ans"])]
        self._apply()

    def _end_turn(self, m, new):
        old = self.x[m]
        self.x[m] = float(new)
        self.history.append((self.clock, m, float(old), float(new)))
        self.n_turns[m] += 1
        self.drive[m] = 0.0                             # fatigue: bored
        if abs(new - old) > self.MOVED:                 # it moved: the other's landscape changed, so the other rebounds
            self.drive[1 - m] = 1.0
        self._start_turn()

    def taste(self, value, at):
        if value != 0 and not self.working:
            self.working = True
            self.est = float(self.x[0] - self.x[1])
            self._apply()
        self.forager.taste(value, at)

def job(j):
    from stage2_lang import arms as S
    from stage2_lang.sim import WLife
    arm, body, seed, first = j
    if not arm.startswith("local"):
        return CS.job(j)
    w = S.world_of(CS.world_text(body))
    if arm in ("local:half", "local:halfj"):
        lf = WLife(seed, first, (lambda s: HalfCentre(s, {"dt": WLife.dt, "joint": arm == "local:halfj"})), w, seconds=True)
    else:
        lf = WLife(seed, first, (lambda s: LocalCouple(s, {"dt": WLife.dt, "norm": arm == "local:norm", "turns": arm in ("local:turns", "local:drive", "local:turnsj"), "driveonly": arm == "local:drive", "joint": arm == "local:turnsj"})), w, seconds=True)
    right = 0.0
    if body in ("lopsided", "both"):
        k = {lf.wire_m[th]: g for th, g in ((0, lf.v_a), (1, lf.v_b))}
        right = math.log(k[1] / k[0])
    S.live(lf, P4.SECS)
    q, b = lf.v_q, lf.brain
    win = []
    for a, z in P4.WINDOWS:
        lo, hi = (q + a) / lf.dt, (q + z) / lf.dt
        good = sum(am for t, bad, am in lf.scored if lo <= t < hi and not bad)
        badm = sum(am for t, bad, am in lf.scored if lo <= t < hi and bad)
        win.append((good - 2.0 * badm) / (z - a) * 10)
    # the knob compared as the other arms': g0 / g1 = exp(right) for the told balance, so the balance is x0 - x1
    est = float(b.x[0] - b.x[1])
    hist = getattr(b, "history", [])
    done_at = hist[-1][0] if hist and getattr(b, "active", 0) is None else None
    return dict(arm=arm, body=body, seed=seed, win=win, right=right, est=est, onset=q, done_at=done_at, tempo=float(b.x.sum() / 2),
                history=hist, drag=float(getattr(lf, "v_d", 1.0)))


if __name__ == "__main__":
    a = sys.argv[1:]
    n = int(a[0]) if a and a[0].isdigit() else 20
    s0 = next((int(x[1:]) for x in a if x.startswith("s") and x[1:].isdigit()), 98000)
    out = f"/home/pilgrim/git/simple-learner/lab/v/couple_local_{n}_s{s0}{'_both' if 'both' in a else ''}.pkl"
    if "report" not in a:
        import ledger
        ledger.start()
        arms = tuple(x for x in a if x in ("forage", "told", "couple:occam", "local", "local:norm", "local:turns", "local:drive", "local:half", "local:halfj", "local:turnsj")) or ("forage", "couple:occam", "local")
        if "both" in a:                                 # thrusters and drag drawn: the balance and the tempo both matter
            jobs = [(arm, "both", s, c) for arm in arms for s in range(s0, s0 + n) for c in ("red", "blue")]
        else:
            jobs = [(arm, "lopsided", s, c) for arm in arms for s in range(s0, s0 + n) for c in ("red", "blue")]
            jobs += [(arm, "plain", s, c) for arm in arms for s in range(s0, s0 + n // 2) for c in ("red", "blue")]
        with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
            rows = list(ex.map(job, jobs, chunksize=2))
        pickle.dump(rows, open(out, "wb"))
    rows = pickle.load(open(out, "rb"))
    CS.ARMS = ("forage", "told", "couple:occam", "local", "local:norm", "local:turns", "local:drive", "local:half", "local:halfj", "local:turnsj")
    CS.report(rows)
    for arm in ("local", "local:norm", "local:turns", "local:drive", "local:half", "local:halfj", "local:turnsj"):
        tb = [(r["tempo"], math.log(r.get("drag", 1.0))) for r in rows if r["arm"] == arm and r["body"] == "both"]
        if tb:
            e = np.array([abs(t - d) for t, d in tb])
            print(f"{arm}: tempo against the drag (log rate against log drag, the told tempo): median error {np.median(e):.2f}, within .2 {np.mean(e <= .2):.0%}; correlation {np.corrcoef([t for t, _ in tb], [d for _, d in tb])[0, 1]:+.2f}")
        t = [r["tempo"] for r in rows if r["arm"] == arm]
        if t:
            print(f"{arm}: the units' mean log rate (tempo) at the end: median {np.median(t):+.2f}, quartiles {np.percentile(t, 25):+.2f}, {np.percentile(t, 75):+.2f}")

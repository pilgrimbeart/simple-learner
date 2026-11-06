"""stage2_indep3_seconds.py: third independent check, 3 (seconds mode). Traced lives (WLife trace=True, so _step_seconds and
seconds.py's brains), watched by my own wrappers (instance attributes on the life, its body and its instruments, and a tap on the
brain's class; each only records and calls through, draws nothing, writes nothing the life reads). Per tick, from the state after the
tick stage, I integrate the body exactly myself (drag an exponential, each firing applied at its moment) and compare:
  beats     every beat the brain states (motor, moment) fires its motor's thruster at that moment, and nothing else fires
  motion    the body's state before each firing and at the tick's end against my exact solution
  meals     each meal's moment against the first moment the mouth's true (curved, decaying) path comes within EAT of the block;
            blocks the true path reaches but the engine doesn't eat (missed) or eats though the true path never reaches (extra)
  tastes    each meal with worth != 0 gives exactly one taste, of worth's sign, at the meal's moment, inside the meal; no other taste
  deferrals each (after d ...) runs at its due moment (lateness), or never (lost)
Also imported by lab/stage2_indep3_attacks.py for its interface measure.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage2_indep3_seconds.py"""
import math
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np

SEEDS = range(69600, 69700)          # this script's share of 69600-69999


def set_tick(dt):
    """Every loaded module's TICK to dt (as the builder's stage2_checks.set_tick does; my own copy). A worker's process only."""
    import types
    import units
    from stage2_lang import arms, sim, fast, seconds, instruments  # noqa: F401  (load everything first)
    import table, universal, universal_v, story1, drivebal, bits_bank  # noqa: F401
    old = units.TICK
    if old == dt:
        return
    for m in list(sys.modules.values()):
        if isinstance(m, types.ModuleType) and getattr(m, "TICK", None) == old:
            m.TICK = dt
    sim.WLife.dt = dt


def _wrapd(d, w):
    return (d + w / 2) % w - w / 2


class Watch:
    """My instrument on one life. Call attach(lf) after arms.make; read .stats at the end."""

    def __init__(self, check_motion=True, samples=64):
        self.check_motion = check_motion
        self.samples = samples
        self.steps, self.tastes = [], []
        self.stats = dict(ticks=0, beats=0, beats_clipped=0, beat_mismatch=0, beats_drawn=0, firings=0, fire_err=0.0, end_err=0.0,
                          motion_bad_ticks=0, meals=0, meals_dropped=0, meal_dt_max=0.0, meal_dt_sum=0.0, meal_dt_n=0, extra=0, missed=0,
                          taste_bad=0, taste_ok=0, orphan_tastes=0, zero_worth=0, defer_sched=0, defer_run=0, defer_late_max=0.0,
                          defer_early_max=0.0, defer_backwards=0, dmeals=[], dtastes=[])
        self.inmeal = None

    # ---- hooks
    def tap(self, cls):
        W = self

        class Tapped(cls):
            def taste(self, value, at):
                W.tastes.append((W.lf.t, float(value), float(at) + W.lf.dt, W.inmeal))
                return super().taste(value, at)

            def step(self):
                out = super().step()
                W.steps.append((list(out or []), list(getattr(self, "beats", None) or [])))
                return out
        return Tapped

    def attach(self, lf):
        self.lf = lf
        W = self
        tr, body = lf.tr, lf.body
        orig_record, orig_fire, orig_meal, orig_end = tr.record, body.fire, lf._meal, lf.inst.tick_end
        orig_later, orig_run = lf.later, lf._run_later
        self.D = lf.DRAG
        self.pend = {}

        def record(Wl):
            orig_record(Wl)
            b = Wl.body
            W.start = np.array([b.pos[0], b.pos[1], b.heading, b.spin, b.speed[0], b.speed[1]])
            W.xy0, W.alive0 = b.xy.copy(), b.alive.copy()
            W.ev = []
            W.consts = (Wl.PUSH, Wl.TURN, Wl.DRAG, Wl.EAT, Wl.RADIUS, Wl.WORLD)
            W.ntaste0 = len(W.tastes)
            W.nstep0 = len(W.steps)
            W.reached = 0.0

        def fire(th, k):
            b = lf.body
            W.reached = max(W.reached, lf._at)
            W.ev.append(("fire", lf._at, int(th), float(k), np.array([b.pos[0], b.pos[1], b.heading, b.spin, b.speed[0], b.speed[1]])))
            return orig_fire(th, k)

        def meal(blk, at):
            b = lf.body
            bxy = b.xy[blk].copy()
            n0, ns = len(W.tastes), len(lf.scored)
            W.inmeal = (lf.t, at, blk)
            W.reached = max(W.reached, at)
            try:
                orig_meal(blk, at)
            finally:
                W.inmeal = None
            worth = None
            if len(lf.scored) > ns:
                _, bad, am = lf.scored[-1]
                worth = -am if bad else am
            W.ev.append(("meal", at, int(blk), bxy, worth, W.tastes[n0:], b.xy[blk].copy(), bool(b.alive[blk])))

        def later(d, fn):
            W.pend[id(fn)] = (lf.now + max(0.0, float(d)), lf.t)
            W.stats["defer_sched"] += 1
            return orig_later(d, fn)

        def run_later(fn, cmd):
            due, t_s = W.pend.pop(id(fn), (None, None))
            if due is not None:
                W.stats["defer_run"] += 1
                late = lf.now - due
                W.stats["defer_late_max"] = max(W.stats["defer_late_max"], late)
                W.stats["defer_early_max"] = max(W.stats["defer_early_max"], -late)
                if t_s == lf.t and lf._at is not None and lf._at < getattr(W, "reached", 0.0) - 1e-15:
                    W.stats["defer_backwards"] += 1
            return orig_run(fn, cmd)

        def tick_end():
            orig_end()
            W.analyse()

        tr.record = record
        body.fire = fire
        lf._meal = meal
        lf.inst.tick_end = tick_end
        lf.later = later
        lf._run_later = run_later
        return lf

    # ---- the exact solution
    def prop(self, s, tau):
        D = self.D
        if tau <= 0:
            return s.copy()
        e = math.exp(-D * tau)
        f = (1 - e) / D
        return np.array([s[0] + s[4] * f, s[1] + s[5] * f, s[2] + s[3] * f, s[3] * e, s[4] * e, s[5] * e])

    def err(self, a, b):
        w = self.consts[5]
        d = np.abs(a - b)
        d[0], d[1] = abs(_wrapd(a[0] - b[0], w)), abs(_wrapd(a[1] - b[1], w))
        sc = np.array([1e-3, 1e-3, 1.0, 1.0, 1e-3, 1e-3])     # relative to a mm, a radian, a mm/s
        return float(np.max(d / sc))

    def path(self, s, a, b, n):
        """Mouth positions at n moments from a to b, starting from state s at moment a."""
        R = self.consts[4]
        D = self.D
        tau = np.linspace(0.0, b - a, n)
        e = np.exp(-D * tau)
        f = (1 - e) / D
        x, y, h = s[0] + s[4] * f, s[1] + s[5] * f, s[2] + s[3] * f
        return a + tau, x + R * np.cos(h), y + R * np.sin(h), s[3] * e, s[4] * e, s[5] * e, h

    def first_touch(self, s, a, b, bxy):
        """(moment of first approach within EAT along the true path in [a, b], min distance / EAT)."""
        EAT, w = self.consts[3], self.consts[5]
        tt, mx, my, *_ = self.path(s, a, b, self.samples)
        d = np.hypot(_wrapd(mx - bxy[0], w), _wrapd(my - bxy[1], w))
        j = int(np.argmin(d))
        lo_hi = None
        inside = np.nonzero(d < EAT)[0]
        if len(inside):
            k = inside[0]
            if k == 0:
                return tt[0], d.min() / EAT
            lo, hi = tt[k - 1], tt[k]
            for _ in range(60):
                m = 0.5 * (lo + hi)
                _, px, py, *_ = self.path(s, a, m, 2)
                if math.hypot(_wrapd(px[-1] - bxy[0], w), _wrapd(py[-1] - bxy[1], w)) < EAT:
                    hi = m
                else:
                    lo = m
            return hi, d.min() / EAT
        # refine the minimum near the closest sample
        lo, hi = tt[max(j - 1, 0)], tt[min(j + 1, len(tt) - 1)]
        best = d[j]
        for _ in range(60):
            m1, m2 = lo + (hi - lo) / 3, hi - (hi - lo) / 3
            _, p1x, p1y, *_ = self.path(s, a, m1, 2)
            _, p2x, p2y, *_ = self.path(s, a, m2, 2)
            d1 = math.hypot(_wrapd(p1x[-1] - bxy[0], w), _wrapd(p1y[-1] - bxy[1], w))
            d2 = math.hypot(_wrapd(p2x[-1] - bxy[0], w), _wrapd(p2y[-1] - bxy[1], w))
            best = min(best, d1, d2)
            if d1 < d2:
                hi = m2
            else:
                lo = m1
        if best < EAT:
            return lo, best / EAT
        return None, best / EAT

    def analyse(self):
        lf, S = self.lf, self.stats
        dt = lf.dt
        S["ticks"] += 1
        PUSH, TURN, DRAG, EAT, R, Wd = self.consts
        # beats against firings
        exp = []
        for out, beats in self.steps[self.nstep0:]:
            if sorted(out) != sorted(m for m, _ in beats):
                S["beats_drawn"] += len(out)
                exp = None
                break
            for i, (m, at) in enumerate(beats):
                S["beats"] += 1
                if not (0.0 <= at < dt):
                    S["beats_clipped"] += 1
                c = min(max(at, 0.0), dt * (1 - 1e-12))
                for th in (0, 1):
                    if lf.wire_m[th] == m:
                        exp.append((c, i, th))
        fires = [(e[1], e[2]) for e in self.ev if e[0] == "fire"]
        S["firings"] += len(fires)
        if exp is not None:
            exp = [(c, th) for c, _, th in sorted(exp)]
            if exp != fires:
                S["beat_mismatch"] += 1
        # motion, meals
        s = self.start.copy()
        cur = 0.0
        xy, alive = self.xy0.copy(), self.alive0.copy()
        segs = []                                     # (a, b, state at a)
        bad = False
        for e in self.ev:
            if e[0] == "fire":
                at = e[1]
                s = self.prop(s, at - cur)
                er = self.err(s, e[4])
                S["fire_err"] = max(S["fire_err"], er)
                bad |= er > 1e-9
                segs.append((cur, at, s.copy()))
                cur = at
                k = e[3]
                s[4] += k * PUSH * math.cos(s[2])
                s[5] += k * PUSH * math.sin(s[2])
                s[3] += k * TURN if e[2] == 1 else -(k * TURN)
        segs.append((cur, dt, s.copy()))
        s_end = self.prop(s, dt - cur)
        b = lf.body
        end = np.array([b.pos[0], b.pos[1], b.heading, b.spin, b.speed[0], b.speed[1]])
        er = self.err(s_end, end)
        S["end_err"] = max(S["end_err"], er)
        bad |= er > 1e-9
        S["motion_bad_ticks"] += int(bad)
        eaten_in = {}
        for e in self.ev:
            if e[0] != "meal":
                continue
            _, at, blk, bxy, worth, ts, nxy, nalive = e
            if worth is None:
                S["meals_dropped"] += 1
                continue
            S["meals"] += 1
            # tastes
            if worth == 0:
                S["zero_worth"] += 1
                if ts:
                    S["taste_bad"] += 1
            else:
                v = 1.0 if worth > 0 else -1.0
                if len(ts) == 1 and ts[0][1] == v and abs(ts[0][2] - at) < 1e-12:
                    S["taste_ok"] += 1
                else:
                    S["taste_bad"] += 1
            if self.check_motion and not bad:
                cands = [g for g in segs if g[0] - 1e-15 <= at <= g[1] + 1e-15] or [segs[-1]]
                for seg in cands:                     # a moment on a boundary belongs to both segments
                    tau, mind = self.first_touch(seg[2], seg[0], seg[1], bxy)
                    if tau is not None:
                        break
                if tau is None:
                    S["extra"] += 1
                    S["extra_worst"] = max(S.get("extra_worst", 1.0), mind)
                else:
                    d = at - tau
                    S["meal_dt_max"] = max(S["meal_dt_max"], abs(d))
                    S["meal_dt_sum"] += abs(d)
                    S["meal_dt_n"] += 1
                eaten_in.setdefault(id(seg), set()).add(blk)
            xy[blk], alive[blk] = nxy, nalive
        nt = sum(1 for e in self.ev if e[0] == "meal" for _ in e[5])
        S["orphan_tastes"] += len(self.tastes) - self.ntaste0 - nt
        # missed: blocks the true path reaches in a forward segment, not eaten there (worlds without block rules only)
        if self.check_motion and not bad:
            for g in segs:
                a, z, sa = g
                if z - a <= 0:
                    continue
                tt, mx, my, w_, vx, vy, h = self.path(sa, a, z, self.samples)
                if vx[-1] * math.cos(h[-1]) + vy[-1] * math.sin(h[-1]) <= 0:
                    continue
                near = np.nonzero(alive & (np.hypot(_wrapd(xy[:, 0] - mx[0], Wd), _wrapd(xy[:, 1] - my[0], Wd)) < EAT + 2e-3))[0]
                for blk in near:
                    if blk in eaten_in.get(id(g), ()):
                        continue
                    if any(e[0] == "meal" and e[2] == blk and a - 1e-15 <= e[1] <= z + 1e-15 for e in self.ev):
                        continue
                    tau, mind = self.first_touch(sa, a, z, xy[blk])
                    if tau is not None and mind < 1 - 1e-6:
                        S["missed"] += 1
                        S["missed_worst"] = min(S.get("missed_worst", 1.0), mind)
        self.ev = []


def life(text, arm, seed, first, dt=0.01, seconds=100.0, check_motion=True, samples=64):
    from stage2_lang import arms, lang
    from stage2_lang.sim import WLife
    set_tick(dt)
    WLife.instruments = True
    Wt = Watch(check_motion, samples)
    lf = arms.make(lang.World(text), arm, seed, first, trace=True, tap=Wt.tap, seconds=True)
    Wt.attach(lf)
    ticks = int(round(seconds / lf.dt))
    while lf.t < ticks:
        lf.step()
    Wt.stats["defer_lost"] = sum(1 for due, ts in Wt.pend.values() if due < ticks * lf.dt - 1e-9)
    Wt.stats.pop("dmeals"), Wt.stats.pop("dtastes")
    return Wt.stats


def job(j):
    name, text, arm, seed, first, dt, cm = j
    try:
        return name, arm, dt, life(text, arm, seed, first, dt, check_motion=cm)
    except Exception as e:
        return name, arm, dt, dict(error=f"{type(e).__name__}: {e}")


WORLDS = {
    "plain": "(world)",
    "digest": None, "unreliable": None, "rarefeast": None, "decoys": None, "swap10": None, "alternate": None, "keylock": None,
    "after_meal": "(world (let n 0) (let m 0) (on meal (set n (+ n 1)) (after 0.0005 (set m (+ m 1)))))",
    "after_meal0": "(world (let m 0) (on meal (after 0 (set m (+ m 1)))))",
    "after_tick": "(world (let m 0) (on tick (if (chance (* 5 TICK)) (after 0.002 (set m (+ m 1))))))",
    "after_pulse": "(world (let m 0) (on pulse (if (chance 0.05) (after 0.001 (set m (+ m 1))))))",
}


if __name__ == "__main__":
    from stage2_lang import worlds as WW
    for k in WORLDS:
        if WORLDS[k] is None:
            WORLDS[k] = WW.W[k]["text"]
    jobs = []
    for dt, seeds in ((0.01, SEEDS[:10]), (0.00125, SEEDS[10:13])):
        for name, text in WORLDS.items():
            for arm in ("circuit", "bank"):
                for s in seeds:
                    for c in ("red", "blue"):
                        jobs.append((name, text, arm, s, c, dt, True))
    jobs.sort(key=lambda j: j[5])                     # the 10 ms ones first; each worker sets its own tick per job
    out = {}
    with ProcessPoolExecutor(7) as ex:
        for name, arm, dt, st in ex.map(job, jobs, chunksize=1):
            out.setdefault((name, arm, dt), []).append(st)
    keys = ["beats", "beats_clipped", "beats_drawn", "beat_mismatch", "firings", "motion_bad_ticks", "meals", "meals_dropped", "taste_ok",
            "taste_bad", "zero_worth", "orphan_tastes", "extra", "missed", "defer_sched", "defer_run", "defer_lost", "defer_backwards"]
    for (name, arm, dt), rs in out.items():
        errs = [r["error"] for r in rs if "error" in r]
        rs = [r for r in rs if "error" not in r]
        tot = {k: sum(r[k] for r in rs) for k in keys}
        mx = dict(fire_err=max((r["fire_err"] for r in rs), default=0), end_err=max((r["end_err"] for r in rs), default=0),
                  meal_dt_max=max((r["meal_dt_max"] for r in rs), default=0),
                  meal_dt_mean=sum(r["meal_dt_sum"] for r in rs) / max(1, sum(r["meal_dt_n"] for r in rs)),
                  extra_worst=max((r.get("extra_worst", 1) for r in rs), default=1), missed_worst=min((r.get("missed_worst", 1) for r in rs), default=1),
                  defer_late_max=max((r["defer_late_max"] for r in rs), default=0), defer_early_max=max((r["defer_early_max"] for r in rs), default=0))
        print(f"{name:12s} {arm:7s} dt {dt*1e3:5.2f} ms lives {len(rs)} errors {len(errs)} {errs[:1]}", flush=True)
        print("    " + " ".join(f"{k} {v}" for k, v in tot.items()), flush=True)
        print("    " + " ".join(f"{k} {v:.3g}" for k, v in mx.items()) + "   (motion errors in mm, rad, mm/s; moments in s)", flush=True)

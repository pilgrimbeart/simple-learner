"""stage1c_arms.py: stage 1c's arms, worlds and life loop (PROGRAMME.md). Reuses lab/bits_bank.py; lab/universal_v.py, discrete/model.py and the body are untouched. World changes are wrappers.

What each arm is ideal *among* (never "ideal" alone). All arms share one likelihood: a scored taste says colour y ("the colour followed was food" if good, the other if bad); a hypothesis predicting colour c gives
P(y = c) = 1-e, independently. Each hypothesis's prediction is a function of the past stream and the clock only, so the policy's factor cancels and the posterior is exact given the stream, whoever drives. It says nothing of what a driver chosen for information could gain, and independence of lies is a stated model, not a fact.

  fsmap, fsbma   fixed share over the seven (Herbster-Warmuth; with a known likelihood this is the exact forward filter of Adams-MacKay changepoint detection, the run length marginalised out, a change redrawing from the prior pi). Hazard h per scored taste, or lam per second (h = 1 - exp(-lam dt)). Ideal among: sequences of the seven with geometric change times, given (h, e, pi).
  mix            the exact Bayesian mixture of any of: the seven (fixed for the life); two-state hidden Markov models over which colour is food (exact forward filter, switch rate lam per second, one per rate); swaps with a period and phase (family `fam`), each with both starting colours. Ideal among exactly its family, given e and the group shares. Told nothing else.
  ctrr           the bank's counter with its parts varied (bits_bank.Ctr), recording E's range and trace.
  oracle         told every block's position, the wiring and the dynamics; moves with motors only; rate capped. A ceiling on meals, never a brain.
  ureye          table.Unwired with each taste's eye recency recorded (its behaviour is table.Unwired's exactly).

Worlds: late_<rule>_<T>: plain until T s, then alternate, pattern or a single permanent swap. nlate_<rule>_<T>: unreliable (one lie in five) throughout, same onset (an addition to the brief: a plain prefix leaves little to forget). swap7, swap20: other periods. coin: each meal poison by a fair coin."""
import json
import os
import pickle
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from creature import Life
from minimal.spec import SPAN, Lived, thirds, efficiency, spent, COST, NEED, THRUST, ENERGY
import bits_bank as B
import ladder as Lad
import table as T
import world as Wd
from units import TICK

COL = T.COL
OUT = os.path.expanduser("~/nca-scratch-backup/stage1c/")
os.makedirs(OUT, exist_ok=True)
WORKERS = 7
NAMES = ["1/3", "1/0", "2/2", "3/2", "4/2", "5/2", "6/2"]


# ---------------------------------------------------------------- worlds
class OneSwap(Lad.Rule):
    """The colours swap for good (T is applied by the wrapper)."""

    def poison(self, t):
        return COL[1 - COL.index(self.first)]


class Late(T.Flaw):
    """Plain until T_on, then the inner rule from a fresh start. lie: each meal's colour is flipped with this chance, as table.Unreliable (the same stream of draws)."""

    T_on, kind, lie, now = 1e9, "alternate", 0.0, 0.0

    def __init__(self, first):
        super().__init__(first)
        self.inner = dict(alternate=Lad.Alternate, pattern=Lad.Pattern, swap=OneSwap)[self.kind](first)

    def setup(self, lf, seed):
        if self.lie:
            self.r = np.random.default_rng(seed + 5_500_019)

    def rule(self, t):
        return self.first if t < self.T_on else self.inner.poison(t)

    def poison(self, t):
        p = self.rule(t)
        if self.lie and self.r.random() < self.lie and p is not None:
            return COL[1 - COL.index(p)]
        return p

    def told_poison(self, t):
        return self.rule(t)

    def ate(self, colour):
        if self.now >= self.T_on:
            self.inner.ate(colour)


def late(kind, Ton, lie=0.0):
    return type(f"Late_{kind}_{Ton}", (Late,), dict(kind=kind, T_on=float(Ton), lie=float(lie)))


LATE_T = (30, 50, 70)
for _k in ("alternate", "pattern", "swap"):
    for _t in LATE_T:
        T.WORLDS[f"late_{_k}_{_t}"] = late(_k, _t)
        T.WORLDS[f"nlate_{_k}_{_t}"] = late(_k, _t, 0.2)
T.WORLDS["late_never"] = late("alternate", 1e9)        # control: must be plain's lives exactly
T.WORLDS["nlate_never"] = late("alternate", 1e9, 0.2)  # control: must be unreliable's lives exactly
T.WORLDS["swap7"] = type("Swap7", (T.Swap,), dict(T=7.0))
T.WORLDS["swap20"] = type("Swap20", (T.Swap,), dict(T=20.0))


class Coin(T.Unreliable):
    E = 0.5


T.WORLDS["coin"] = Coin


# ---------------------------------------------------------------- fixed share over the seven
class FSCore:
    def __init__(self, seed, p):
        super().__init__(seed, p)
        n = len(self.bank)
        self.mxe = float(p.get("eps", 0.2))
        pr = float(p.get("pr", 0.5))
        self.pi = np.array([pr] + [(1 - pr) / (n - 1)] * (n - 1))
        self.w = self.pi.copy()
        self.fsh, self.lam = float(p.get("h", 0.0)), float(p.get("lam", 0.0))
        self.last_s = 0.0
        self.le = list(np.log2(self.w))

    def score(self, value):
        scored, truth, _ = self.about(value)
        if scored:
            dt = self.t - self.last_s
            self.last_s = self.t
            h = 1 - np.exp(-self.lam * dt) if self.lam else self.fsh
            w = (1 - h) * self.w + h * self.pi
            hit = np.array([self.pred(m) == truth for m in self.bank], dtype=float)
            w = w * (hit * (1 - self.mxe) + (1 - hit) * self.mxe)
            self.w = w / w.sum()
            self.le = list(np.log2(np.maximum(self.w, 1e-300)))


class FSMap(FSCore, B.Map):
    """Follows the most probable model."""


class FSBma(FSCore, B.Bma):
    """The posterior-weighted vote."""


# ---------------------------------------------------------------- the exact mixture: seven, HMMs, periods
def fam_grid(name):
    """(periods, phases as fractions of a period), from a name. Hypotheses: each (T, phase, starting colour)."""
    if name == "":
        return np.zeros(0), np.zeros(0)
    if name == "T10":
        return np.array([10.0]), np.array([0.0])
    if name == "T4":
        return np.array([5.0, 10.0, 20.0, 50.0]), np.array([0.0])
    if name == "T64":                                  # log-spaced, 2 to 100 s, 10 exactly among them
        k = np.arange(64)
        return 10.0 * (50.0 ** (1 / 63)) ** (k - int(round(63 * np.log(5) / np.log(50)))), np.array([0.0])
    if name == "T64P16":
        return fam_grid("T64")[0], np.arange(16) / 16
    if name == "T393P16":                              # 1% steps from 2 s: fine enough to hold a phase over a life; 10 not exactly among them
        return 2.0 * 1.01 ** np.arange(393), np.arange(16) / 16
    if name == "T393P64":                              # and phases fine enough to resolve a swap to 1/6 s
        return 2.0 * 1.01 ** np.arange(393), np.arange(64) / 64
    raise KeyError(name)


class Mix(B.Recorder):
    """The exact mixture. p: eps; s7, sh, sp the shares of the three groups (renormalised over those present); pr: the default's share within the seven; lams: list of HMM rates (per s); fam: a period family; every: ticks between re-reading the clock."""

    def __init__(self, seed, p):
        super().__init__(seed, dict(p, bankk=0))
        self.mxe = float(p.get("eps", 0.05))
        pr = float(p.get("pr", 0.5))
        self.lams = np.array(p.get("lams", []), dtype=float)
        Ts, ph = fam_grid(p.get("fam", ""))
        self.pT = np.repeat(Ts, len(ph) * 2)
        self.pP = np.tile(np.repeat(ph, 2), len(Ts)) * self.pT
        self.pZ = np.tile([0, 1], len(Ts) * len(ph))
        n = len(self.bank)
        s7 = float(p.get("s7", 0.0))
        sh = float(p.get("sh", 0.0)) if len(self.lams) else 0.0
        sp = float(p.get("sp", 0.0)) if len(self.pT) else 0.0
        tot = s7 + sh + sp
        self.w7 = s7 / tot * np.array([pr] + [(1 - pr) / (n - 1)] * (n - 1)) if s7 else np.zeros(0)
        self.wh = np.full(len(self.lams), sh / tot / max(len(self.lams), 1)) if sh else np.zeros(0)
        self.wp = np.full(len(self.pT), sp / tot / max(len(self.pT), 1)) if sp else np.zeros(0)
        self.hb = np.full(len(self.wh), 0.5)                # each HMM: P(colour 1 is food), filtered to last_u
        self.last_u = 0.0
        self.every = int(p.get("every", 5))
        self.nticks = 0
        self.timed = bool(len(self.wp))

    def choose(self):
        pass

    def cp(self, t):
        return (self.pZ + np.floor((t - self.pP) / self.pT).astype(np.int64)) % 2

    def propagate(self, t):
        dt = t - self.last_u
        self.last_u = t
        s = 0.5 * (1 - np.exp(-2 * self.lams * dt))
        self.hb = self.hb * (1 - s) + (1 - self.hb) * s

    def observe(self, y):
        """One scored taste: the colour it says was food. Exact Bayes on every group."""
        e, t = self.mxe, self.t
        if len(self.w7):
            hit = np.array([self.pred(m) == y for m in self.bank], dtype=float)
            self.w7 = self.w7 * (hit * (1 - e) + (1 - hit) * e)
        if len(self.wh):
            self.propagate(t)
            p1 = self.hb * (1 - e) + (1 - self.hb) * e        # the predictive of y = 1
            py = p1 if y == 1 else 1 - p1
            self.wh = self.wh * py
            like1, like0 = (1 - e, e) if y == 1 else (e, 1 - e)
            self.hb = self.hb * like1 / (self.hb * like1 + (1 - self.hb) * like0)
        if len(self.wp):
            self.wp = self.wp * np.where(self.cp(t) == y, 1 - e, e)
        tot = self.w7.sum() + self.wh.sum() + self.wp.sum()
        self.w7, self.wh, self.wp = self.w7 / tot, self.wh / tot, self.wp / tot

    def vote(self):
        v = 0.0
        if len(self.w7):
            v += sum(w * self.pred(m) for w, m in zip(self.w7, self.bank))
        if len(self.wh):
            s = 0.5 * (1 - np.exp(-2 * self.lams * (self.t - self.last_u)))
            v += float(self.wh @ (self.hb * (1 - s) + (1 - self.hb) * s))
        if len(self.wp):
            v += float(self.wp @ self.cp(self.t))
        return v

    def taste(self, value, at):
        scored, truth, _ = self.about(value)
        was_open = self.open
        if scored:
            self.observe(truth)
        super().taste(value, at)
        if was_open and not self.open:
            self.observe(self.food)                         # the first bad is a taste too; all the seven agree on it
        if not self.open:
            self.food = int(self.vote() > 0.5)

    def step(self):
        self.nticks += 1
        if self.timed and not self.open and self.nticks % self.every == 0:
            self.food = int(self.vote() > 0.5)
        return super().step()


def prior_bits(p, true_in="period"):
    """-log2 of the prior weight of the true hypothesis in a Mix setting: group share, and uniform within it (both starting colours counted, so 1 bit is always the colour)."""
    s7, sh, sp = p.get("s7", 0.0), p.get("sh", 0.0), p.get("sp", 0.0)
    Ts, ph = fam_grid(p.get("fam", ""))
    sh = sh if len(p.get("lams", [])) else 0.0
    sp = sp if len(Ts) else 0.0
    tot = s7 + sh + sp
    if true_in == "period":
        return -np.log2(sp / tot / (2 * len(Ts) * len(ph)))
    if true_in == "hmm":
        return -np.log2(sh / tot / len(p["lams"])) + 1            # + the starting colour
    return -np.log2(s7 / tot * (1 - p.get("pr", 0.5)) / 6) + 1


# ---------------------------------------------------------------- counters with their range recorded
class CtrR(B.Ctr):
    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.etrace = []

    def taste(self, value, at):
        super().taste(value, at)
        self.etrace.append((self.t, self.act) + tuple(m["E"] for m in self.bank[1:]))


class BankE(B.Recorder):
    """The bank as it is, with the same trace (its E are the bank's own)."""

    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.etrace = []

    def taste(self, value, at):
        super().taste(value, at)
        self.etrace.append((self.t, self.act) + tuple(m["E"] for m in self.bank[1:]))


# ---------------------------------------------------------------- eat-more brains, with what their wires say recorded
class EyeLog:
    """Each taste with how long since each eye last pulsed, and how many pulses each in the last 0.3 s: all the wires say about it. Watching only."""

    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.tlast = [-1e9, -1e9]
        self.urows = []
        self.spy = None

    def stimulate(self, sensor, at):
        self.tlast[sensor] = self.t + at
        super().stimulate(sensor, at)

    def taste(self, value, at):
        eaten, F, bad = self.spy() if self.spy else (-1, -1, 0)
        self.urows.append((self.t, value, self.t - self.tlast[0], self.t - self.tlast[1], eaten, F))
        super().taste(value, at)


class UREye(EyeLog, T.Unwired):
    rows = ()
    picks = ()
    on_at = ()


class BankEye(EyeLog, B.Recorder):
    pass


class VToldEye(EyeLog, B.VTold):
    pass


class Oracle:
    """Told every block's position, the wiring and the dynamics. Each tick it heads for the block that minimises distance + turn cost, firing a single thruster to turn and both to go, at most `rate` firings a second per thruster. colour: if set, it eats only blocks of that kind (the world's food, for a sanity check). Moves only through the motors."""

    def __init__(self, seed, p):
        self.p = p
        self.t = 0.0
        self.rate = float(p.get("rate", 100.0))
        self.acc = 0.0
        self.lf = None
        self.rows, self.picks, self.on_at = (), (), ()
        self.spy = None
        self.tastes = 0

    def stimulate(self, sensor, at):
        pass

    def taste(self, value, at):
        self.tastes += 1

    def drive(self, sensor):
        return 1.0

    def step(self):
        self.t += TICK
        self.acc = min(self.acc + self.rate * TICK, max(1.0, self.rate * TICK))
        n = int(self.acc)
        if n < 1:
            return []
        lf = self.lf
        b = lf.body
        q = np.exp(-Wd.DRAG * TICK)
        carry = TICK / (1 - q)                              # distance or angle still to come per unit speed
        # where it will coast to, if nothing more fired
        head = b.heading + b.spin * carry
        pos = b.pos + b.speed * carry
        mouth = pos + Wd.RADIUS * np.array([np.cos(head), np.sin(head)])
        d = b.wrap(b.xy - mouth)
        dist = np.hypot(d[:, 0], d[:, 1])
        ang = np.arctan2(d[:, 1], d[:, 0])
        err = (ang - head + np.pi) % (2 * np.pi) - np.pi
        k = int(np.argmin(dist + self.p.get("turnc", 1.0) * Wd.MILLI * np.abs(err) / (Wd.TURN * carry)))
        e = err[k]
        per = Wd.TURN * carry                               # the angle one firing turns it
        self.acc -= n
        if abs(e) > 0.6 * per:
            th = "right" if e > 0 else "left"               # the right thruster turns it left: heading up
            m = lf.motor[th]
            return [m] * min(n, max(1, int(abs(e) / per)))
        return [lf.motor["left"], lf.motor["right"]] * n


T.ARMS.update(fsmap=FSMap, fsbma=FSBma, mix=Mix, ctrr=CtrR, banke=BankE, ureye=UREye, bankeye=BankEye, vtoldeye=VToldEye, oracle=Oracle)


# ---------------------------------------------------------------- the life, as bits_bank.life (control: identical), keeping meals and firings
def life(job):
    w, arm, kw, seed, seconds, first = job
    q = T.numbers(seed, {**B.V7, **kw})
    R = T.WORLDS[w](first)
    lf = Life(seed, first, brain=lambda s: T.ARMS[arm](s, q))
    b = lf.brain
    if arm == "oracle":
        b.lf = lf
    R.setup(lf, seed)
    tell = arm in ("vtold", "vtoldeye")
    wrong = int(kw.get("wrong", 0))

    def rule_food(t):
        tp = R.told_poison(t)
        return lf.sensor[T.COL[1 - T.COL.index(tp)]] if tp else -1

    def spy():
        here = []
        for tk, c in reversed(lf.meals):
            if tk != lf.t:
                break
            here.append(c)
        t = lf.t * T.TICK
        eaten = lf.sensor[here[0]] if len(set(here)) == 1 else -1
        c = here[0] if here else None
        isbad = int(R.bad(c, t)) if c and hasattr(R, "bad") else int(c == lf.poison)
        return eaten, rule_food(t), isbad
    if hasattr(b, "spy"):
        b.spy = spy
    if hasattr(R, "taste"):
        inner = b.taste
        b.taste = lambda v, at: inner(R.taste(v), at)
    ticks = int(round(seconds / T.TICK))
    labelled = 0
    while lf.t < ticks:
        t = lf.t * T.TICK
        po = R.poison(t)
        lf.poison, R.now = po, t
        if tell:
            f = rule_food(t)
            if f >= 0:
                b.told_food = f ^ wrong
                b.food = b.told_food
        R.tick(lf, t)
        lf.step()
        while labelled < len(lf.meals):
            tk, c = lf.meals[labelled]
            badm = R.bad(c, t) if hasattr(R, "bad") else c == po
            lf.meals[labelled] = (tk, "red" if badm else "blue")
            R.ate(c)
            labelled += 1
    l = Lived(thirds(lf.meals, lf.moving, ticks, "red"))
    l.power, l.firings, l.substrate = 3.7e-9, SPAN * len(lf.firings) / seconds, "silicon"
    rows = getattr(b, "rows", ())
    l.rows = np.array(rows, dtype=np.float32) if len(rows) else np.zeros((0, len(B.COLS)), dtype=np.float32)
    l.picks = list(getattr(b, "picks", []))
    l.on = list(getattr(b, "on_at", []))
    l.seed, l.first, l.world = seed, first, w
    l.mt = np.array([m[0] for m in lf.meals], dtype=np.int32)
    l.mbad = np.array([m[1] == "red" for m in lf.meals], dtype=bool)
    l.ft = np.array([f[0] for f in lf.firings], dtype=np.int32)
    l.moving = lf.moving
    if hasattr(b, "etrace"):
        l.etrace = np.array(b.etrace, dtype=np.float32)
    if hasattr(b, "urows"):
        l.urows = np.array(b.urows, dtype=np.float32)
    if arm == "oracle":
        l.tastes = b.tastes
    l.sensor = dict(lf.sensor)
    return l


def _nice():
    os.nice(10)


def run(w, arm, seeds, kw=None, seconds=100.0, workers=WORKERS):
    jobs = [(w, arm, kw or {}, s, seconds, c) for s in seeds for c in COL]
    with ProcessPoolExecutor(workers, initializer=_nice) as ex:
        return list(ex.map(life, jobs, chunksize=4))


def run_plain(w, arm, seeds, kw=None, seconds=100.0, workers=WORKERS):
    jobs = [(w, arm, kw or {}, s, seconds, c) for s in seeds for c in COL]
    with ProcessPoolExecutor(workers, initializer=_nice) as ex:
        return list(ex.map(T.life, jobs, chunksize=4))


# ---------------------------------------------------------------- statistics: efficiency as Sigma gained / Sigma spent; bootstrap over seeds, a seed's two lives together
def gs(L):
    return np.array([sum(a - COST * b for a, b, _ in l) for l in L], dtype=float), np.array([spent(l) for l in L], dtype=float)


def resample(n, boot=2000, seed=0):
    r = np.random.default_rng(seed)
    k = r.integers(0, n // 2, (boot, n // 2))
    return np.concatenate((2 * k, 2 * k + 1), axis=1)


def eff_ci(L, boot=2000):
    g, s = gs(L)
    I = resample(len(g), boot)
    v = g[I].sum(1) / s[I].sum(1)
    return g.sum() / s.sum(), np.percentile(v, 2.5), np.percentile(v, 97.5)


def pdiff(A, Bb, boot=2000):
    """A - B, paired, with the 95% interval."""
    ga, sa = gs(A)
    gb, sb = gs(Bb)
    I = resample(len(ga), boot)
    v = ga[I].sum(1) / sa[I].sum(1) - gb[I].sum(1) / sb[I].sum(1)
    return ga.sum() / sa.sum() - gb.sum() / sb.sum(), np.percentile(v, 2.5), np.percentile(v, 97.5)


def fmt_d(d):
    return f"{d[0]:+.3f} [{d[1]:+.3f},{d[2]:+.3f}]{' SURE' if d[1] > 0 or d[2] < 0 else ''}"


def keep(L):
    """As bits_record.keep, so that bits_analyse reads it."""
    return [dict(rows=l.rows.astype(np.float32), picks=l.picks, on=l.on, seed=l.seed, first=l.first, names=NAMES, lived=list(l)) for l in L]


def identical(A, Bb):
    return all(tuple(x) == tuple(y) for p, q in zip(A, Bb) for x, y in zip(p, q))


# ---------------------------------------------------------------- controls
if __name__ == "__main__":
    S = range(60000, 60004)
    print("== controls: each new piece of code, on development seeds 60000-60003 x 2 (spent in 1b, used only as a code check)", flush=True)
    print("life() = bits_bank.life:", all(identical(run(w, "v_rec", S), B.run(w, "v_rec", S)) for w in ("plain", "digest", "alternate")), flush=True)
    print("late_never = plain, lives exactly:", identical(run("late_never", "v_rec", S), run("plain", "v_rec", S)), flush=True)
    print("nlate_never = unreliable, lives exactly:", identical(run("nlate_never", "v_rec", S), run("unreliable", "v_rec", S)), flush=True)
    print("ctrr pen 3 floor 0 = the bank, lives exactly:", all(identical(run(w, "ctrr", S, dict(pen=3.0, floor=0.0)), run(w, "v_rec", S)) for w in ("unreliable", "swap10")), flush=True)
    print("banke = the bank, lives exactly:", identical(run("alternate", "banke", S), run("alternate", "v_rec", S)), flush=True)
    print("fsbma h=0 = bma, same e, pr, lives exactly:", all(identical(run(w, "fsbma", S, dict(eps=0.2, pr=0.5, h=0.0)), run(w, "bma", S, dict(eps=0.2, pr=0.5))) for w in ("unreliable", "swap10")), flush=True)
    print("mix s7 only = bma, lives exactly:", all(identical(run(w, "mix", S, dict(eps=0.2, pr=0.5, s7=1.0)), run(w, "bma", S, dict(eps=0.2, pr=0.5))) for w in ("unreliable", "swap10", "alternate")), flush=True)
    print("ureye = table.Unwired, thirds exactly:", identical(run("plain", "ureye", S, {"open": 0}), run_plain("plain", "unwired", S)), flush=True)
    print("vtoldeye = vtold:", identical(run("plain", "vtoldeye", S), run("plain", "vtold", S)), flush=True)
    # the HMM filter: against brute-force enumeration of state paths on a short random stream
    import itertools
    rng = np.random.default_rng(1)

    class Stub(Mix):
        def __init__(self):
            self.mxe, self.lams, self.w7, self.wp = 0.1, np.array([0.3]), np.zeros(0), np.zeros(0)
            self.wh, self.hb, self.last_u, self.t = np.array([1.0]), np.array([0.5]), 0.0, 0.0
    st = Stub()
    ys, ts = rng.integers(0, 2, 8), np.cumsum(rng.exponential(1.5, 8))
    for y, tt in zip(ys, ts):
        st.t = tt
        st.observe(int(y))
    num, den = 0.0, 0.0
    for path in itertools.product((0, 1), repeat=8):
        for z0 in (0, 1):
            pr, prev, tp = 0.5, z0, 0.0
            for z, y, tt in zip(path, ys, ts):
                s = 0.5 * (1 - np.exp(-2 * 0.3 * (tt - tp)))
                pr *= (s if z != prev else 1 - s) * (0.9 if z == y else 0.1)
                prev, tp = z, tt
            den += pr
            num += pr * (path[-1] == 1)
    print(f"HMM filter P(colour 1) {st.hb[0]:.10f}; brute force over paths {num / den:.10f}", flush=True)
    # fixed share: against brute force over model paths
    e, h, pi = 0.2, 0.05, np.array([0.5] + [0.5 / 6] * 6)
    H = rng.integers(0, 2, (5, 7))
    w = pi.copy()
    for i in range(5):
        w = (1 - h) * w + h * pi
        w = w * np.where(H[i], 1 - e, e)
        w /= w.sum()
    P = np.zeros(7)
    for path in itertools.product(range(7), repeat=6):      # path[0] the birth state; each taste moves first
        pr = pi[path[0]]
        for i in range(5):
            pr *= (1 - h) * (path[i + 1] == path[i]) + h * pi[path[i + 1]]
            pr *= (1 - e) if H[i, path[i + 1]] else e
        P[path[-1]] += pr
    P /= P.sum()
    print(f"fixed share vs brute force over paths: max difference {np.abs(P - w).max():.2e}", flush=True)
    # the period family holds what it says
    for nm in ("T10", "T4", "T64", "T64P16", "T393P16", "T393P64"):
        Ts, ph = fam_grid(nm)
        print(f"family {nm}: {len(Ts)} periods {Ts.min():.3f}-{Ts.max():.3f}, nearest to 10: {Ts[np.argmin(np.abs(Ts - 10))]:.4f}, {len(ph)} phases, {np.log2(2 * len(Ts) * len(ph)):.2f} bits", flush=True)
    # eff_ci and pdiff agree with table.paired
    a, b = run("swap10", "v_rec", range(60000, 60040)), run("swap10", "bma", range(60000, 60040), dict(eps=0.2, pr=0.5))
    d, i = T.paired(a, b, boot=2000)
    print(f"pdiff {fmt_d(pdiff(a, b))} against table.paired {d:+.3f} [{i[0]:+.3f},{i[1]:+.3f}]; efficiency {efficiency(a):.4f} eff_ci {eff_ci(a)[0]:.4f}", flush=True)

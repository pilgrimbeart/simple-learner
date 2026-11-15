"""steer.py: the steering grown (PROGRAMME.md, Next: the steering grown, G1 and G2; the user: go for it, 2026-11-14). Main session.
Predictions: lab/v/grownet_predictions.md, G1 and after.

The starting circuit drives by hand: when the followed eye pulses it fires both thrusters in turn (straight on), when bored it runs
straight, otherwise it scans on one thruster. Here that drive is removed and grown:
  - Play (PLAY s from birth): at random moments one option is tried (OPTIONS: thruster 0, thruster 1, both, or none), a short burst at
    the circuit's drive rate; each trial is a step of a growing network's stream (lab/grownet.py: blocks over sequences, strict copies),
    its symbol the context (which eye pulsed in the last CTX s) then the option; graded readouts (D60) keep how each eye's pulse count
    changed over the trial's window against the window before. Two networks, one for each eye's change; and the sixteen pair detectors
    (context, option) present from birth, a starting repertoire, since in a short play the pairs rarely grew by themselves.
  - Reflexes: for each context, the option whose own unit surely raises (SURE standard errors, against none) the change of the eye
    that matters is wired: with the followed eye just seen, the one raising that eye; with nothing seen, the one raising either (a scan).
    Nothing written by hand: what a thruster does, whether straight-on approaches, which way to spin.
  - Then: each tick, if the followed eye pulsed within CTX s its reflex is fired at the drive rate, else the scan's at the scan rate;
    the choice of colour and every rate are the starting circuit's own.
Arms: circuit (the hand-built drive), grown, still (the drive removed and nothing grown).

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/steer.py [PAIRS] [WORLD: plain|seq5|seq11] [s130000]"""
import math
import pickle
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import ladders as L
import stage3_random as R

PLAY = 120.0                                    # s of play from birth (60 found the scans but no approach, 2026-11-14)
OPTIONS = ((0,), (1,), (0, 1), ())              # thruster 0, thruster 1, both, none
TRY = 1.0                                       # s: a trial's burst, and its window (0.3 too short to see straight-on approach, 2026-11-14)
CTX = 0.1                                       # s: "this eye pulsed just now"
SURE = 2.0
LIFELONG = __import__("os").environ.get("LIFELONG") == "1"   # the pairs keep learning through the life (2026-11-14)
EPS = float(__import__("os").environ.get("EPS", 0.1))
EXPL = __import__("os").environ.get("EXPL", "")   # "fade": exploration falling with each context's uses
EPS_ = 0.1                                       # ... and an option other than the best this often
_C = {}


TRACE = __import__("os").environ.get("TRACE") == "1"   # the eligibility trace (2026-11-14): a taste credited back to the choices before it
TAU_E = 3.0                                     # s: a choice's mark fades with this time constant
HOLDCTX = __import__("os").environ.get("HOLDCTX", "1") == "1"
DECIDE = 0.3                                    # s: a choice is held this long


def td_cls(base):
    """Temporal differences (SARSA; Rummery & Niranjan 1994, Sutton & Barto): each (context, option) pair holds a value Q; at each
    choice (every DECIDE s) the pair just ended moves towards the tastes since it began plus the discounted value of the pair now chosen:
    Q(prev) += ALPHA (r + GAMMA Q(now) - Q(prev)). Leaving a bad situation is credited through the value of where it leads, not blamed for
    what happened seconds before. Local: a pair needs only its own reward and its successor's value. Choice: the best Q, another at random
    EPS of the time (always in the first PLAY s); the same contexts and options as the trace."""

    class TD(base):
        def __init__(self, seed, p):
            super().__init__(seed, p)
            self.lastpulse = [-1e9, -1e9]
            self.Q = {}
            self.prev, self.r, self.cur, self.until, self.ph, self.rate = None, 0.0, 3, -1.0, 0.0, 0.0
            self.rho = 0.0
            self.srng = np.random.default_rng([int(seed), 99])

        def stimulate(self, sensor, at):
            if sensor in (0, 1):
                self.lastpulse[sensor] = self.t + at
            return super().stimulate(sensor, at)

        def _search(self):
            """Habit search (O24): after play the habit is the values' best per context; then, pair after pair of HE s epochs, one change
            (a context, another option) is tried in one epoch and the kept habit in the other (order random); each change keeps its
            differences in meals (tastes, +1 food, -1 poison) and is kept once its mean beats twice its standard error (at least 3
            pairs), dropped after 8 pairs or once surely worse."""
            if self.t < HSTART:
                return
            if self.H is None:
                nopt = len(OPTIONS)
                self.H = [max(range(nopt), key=lambda o: self.Q.get((c, o), 0.0)) for c in range(8)]
                self.Hcur, self.ht0 = list(self.H), self.t
                return
            if self.t - self.ht0 < HE:
                return
            if self.hph == 0:                           # a new pair: draw a change among those not yet dropped
                cands = [(c, o) for c in (0, 1, 2, 3, 4, 6) for o in range(len(OPTIONS)) if o != self.H[c]
                         and self.hst.get((c, o), [0])[0] >= 0]
                if not cands:                           # every change dropped: all may be tried again
                    self.hst = {}
                    cands = [(c, o) for c in (0, 1, 2, 3, 4, 6) for o in range(len(OPTIONS)) if o != self.H[c]]
                self.hcand = cands[int(self.srng.integers(len(cands)))] if cands else None
                self.horder = int(self.srng.integers(2))
                self.hph, self.hr = 1, 0.0
            elif self.hph == 1:
                self.hA, self.hr, self.hph = self.hr, 0.0, 2
            else:
                trial, kept = (self.hA, self.hr) if self.horder == 0 else (self.hr, self.hA)
                if self.hcand is not None:
                    st = self.hst.setdefault(self.hcand, [0, 0.0, 0.0])
                    d = trial - kept
                    st[0] += 1; st[1] += d; st[2] += d * d
                    n, m = st[0], st[1] / st[0]
                    se = math.sqrt(max(st[2] / n - m * m, 1e-9) / n) if n > 1 else 1e9
                    if n >= 3 and m > 2 * se:           # surely better: kept; the context's other trials start afresh
                        c, o = self.hcand
                        self.H[c] = o
                        self.hst = {k: v for k, v in self.hst.items() if k[0] != c}
                    elif n >= 8 or (n >= 3 and m < -2 * se):
                        st[0] = -1                      # dropped
                self.hph = 0
            trial_now = (self.hph == 1 and self.horder == 0) or (self.hph == 2 and self.horder == 1)
            self.Hcur = list(self.H)
            if trial_now and self.hcand is not None:
                c, o = self.hcand
                self.Hcur[c] = o
                if c in (1, 3):
                    self.Hcur[c + 4] = o
            self.ht0 = self.t

        def taste(self, value, at):
            if search:
                self.hr += 1.0 if value > 0 else -1.0
            self.r += 1.0 if value > 0 else -1.0
            return super().taste(value, at)

        def step(self):
            super().step()
            p = self.p
            if self.t >= self.until:
                f = self.food
                w = p["hold"]
                ctx = int(self.t - self.lastpulse[f] < w) + 2 * int(self.t - self.lastpulse[1 - f] < w)
                eps = 1.0 if self.t < PLAY else EPS
                o = int(self.srng.integers(len(OPTIONS))) if self.srng.random() < eps else max(range(len(OPTIONS)), key=lambda o: self.Q.get((ctx, o), 0.0))
                if self.prev is not None:
                    q = self.Q.get(self.prev, 0.0)
                    r = self.r
                    if AVGR:                            # average-reward TD (Schwartz 1993): each choice judged against the creature's own
                        r = self.r - self.rho           # running reward rate, so idling (nothing gained) falls below the usual
                        self.rho += BETA * (self.r - self.rho)
                    self.Q[self.prev] = q + ALPHA * (r + (1.0 if AVGR else GAMMA) * self.Q.get((ctx, o), 0.0) - q)
                self.prev, self.r = (ctx, o), 0.0
                self.cur, self.until = o, self.t + DECIDE
                self.rate = p["drive"] if ctx & 1 else p["scan"]
            self.ph += self.rate * 0.0025
            n = int(self.ph)
            self.ph -= n
            if self.t - getattr(self, "_logt", -1e9) > 10.0:
                self._logt = self.t
                self.log_reflex = {c: max(range(len(OPTIONS)), key=lambda o: self.Q.get((c, o), 0.0)) for c in range(4)}
            return list(OPTIONS[self.cur]) * n
    return TD


AVGR = __import__("os").environ.get("AVGR") == "1"   # average-reward TD (2026-11-14)
BETA = 0.01                                     # its running reward rate's step
ALPHA = 0.1                                     # TD: a value's step towards each new estimate
GAMMA = math.exp(-DECIDE / TAU_E)               # TD: a choice's discount, the trace's own time constant over a choice's length


def option_cls(base, cost=True, rates=False, fine=False, bored=False, timed=False, share=False, knobs=None, avg=False, lam=0.0, search=False):
    """rates: False, the circuit's pairing of rate with context; 2, each pattern at scan or drive rate (eight options); 3, at scan, drive
    or run rate (twelve)."""
    """Options held while their context lasts (the options framework, Sutton, Precup & Singh 1999; semi-Markov TD). The context
    (the followed eye, the other, each seen within the circuit's own hold) is watched every tick; when it changes, or at a taste, the
    episode ends and a new option is chosen for the new context, then held (a latch: set at the context's start, reset at its end). The
    episode just ended updates its pair: Q(prev) += ALPHA (R - RHO d + Q(next) - Q(prev)), R the taste that ended it (if one did), d its
    length in seconds, Q(next) the value of the option now chosen. cost: RHO the creature's own running reward per second (forgetting
    over RHO_T s), so an episode is charged for its length (idling forever costs more and more); without it RHO = 0. Choice: the best Q,
    another at random EPS of the time (always in the first PLAY s). Nothing written about which option suits which context.
    An option also ends at random (a termination probability, mean T_END s), so an episode in a context that never changes (standing still
    with nothing in view) still ends, is charged and is re-decided."""

    class Opt(base):
        def __init__(self, seed, p):
            super().__init__(seed, p)
            self.lastpulse = [-1e9, -1e9]
            self.Q, self.prev, self.cur, self.t0, self.r, self.ctx, self.ph = {}, None, 3, 0.0, 0.0, None, 0.0
            self.R, self.D = 0.0, 1e-6                  # running reward and time, forgetting over RHO_T s
            self.tasted = False
            self.srng = np.random.default_rng([int(seed), 101])
            self.episodes = 0
            self.cuses = {}
            self.recent = []
            self.N = {}
            self.elig = []
            self.H, self.Hcur, self.hph, self.ht0, self.hr, self.hst, self.hcand, self.horder = None, None, 0, 0.0, 0.0, {}, None, 0
            self.lastrun = -1e9                         # with knobs: when the last bored run ended (a run lasts at most runlen)
            if knobs:                                   # the rhythm's settings as knobs (log2 multipliers of the circuit's own values), each
                kr = np.random.default_rng([int(seed), 202])   # tuned by antithetic perturbation against the taste (lab/v D64)
                self.th = {k: (float(kr.uniform(-2, 2)) if knobs != "warm" else 0.0) for k in KNOBS}
                self.th0 = dict(self.th)
                self.xi = {k: 0.0 for k in KNOBS}
                self.kph, self.kt0, self.kr, self.kRA, self.gs = 0, 0.0, 0.0, 0.0, 1e-3
                self.base = {k: (p["run_max"] if k == "runlen" else p[k]) for k in KNOBS}

        def stimulate(self, sensor, at):
            if sensor in (0, 1):
                self.lastpulse[sensor] = self.t + at
                if fine:
                    self.recent.append((self.t + at, sensor))
            return super().stimulate(sensor, at)

        def kv(self, k):
            if not knobs:
                return self.p["run_max"] if k == "runlen" else self.p[k]
            return self.base[k] * 2.0 ** (self.th[k] + self.xi[k])

        def _knobs(self):
            """Antithetic perturbation (a pair of epochs, +xi then -xi, each KE s): every knob moves by ETA_K times its own perturbation's
            sign times the normalised difference of taste between the two epochs. Local: a knob knows its own perturbation and the taste."""
            if self.t - self.kt0 < KE or self.t < PLAY:
                return
            if self.kph == 0:                           # a new pair: draw each knob's perturbation, run +xi
                self.xi = {k: SIG_K * (1 if self.srng.random() < 0.5 else -1) for k in KNOBS}
                self.kph, self.kr = 1, 0.0
            elif self.kph == 1:                         # first half done: remember its taste, run -xi
                self.kRA, self.kr = self.kr, 0.0
                self.xi = {k: -v for k, v in self.xi.items()}
                self.kph = 2
            else:                                       # pair done: move
                g = (self.kRA - self.kr) / 2.0
                self.gs = 0.95 * self.gs + 0.05 * g * g
                z = g / math.sqrt(self.gs + 1e-9)
                for k in KNOBS:
                    self.th[k] = float(np.clip(self.th[k] - ETA_K * z * np.sign(self.xi[k]), -4, 4))   # xi now holds -xi
                self.xi = {k: 0.0 for k in KNOBS}
                self.kph = 0
            self.kt0 = self.t

        def _search(self):
            """Habit search (O24): after play the habit is the values' best per context; then, pair after pair of HE s epochs, one change
            (a context, another option) is tried in one epoch and the kept habit in the other (order random); each change keeps its
            differences in meals (tastes, +1 food, -1 poison) and is kept once its mean beats twice its standard error (at least 3
            pairs), dropped after 8 pairs or once surely worse."""
            if self.t < HSTART:
                return
            if self.H is None:
                nopt = len(OPTIONS)
                self.H = [max(range(nopt), key=lambda o: self.Q.get((c, o), 0.0)) for c in range(8)]
                self.Hcur, self.ht0 = list(self.H), self.t
                return
            if self.t - self.ht0 < HE:
                return
            if self.hph == 0:                           # a new pair: draw a change among those not yet dropped
                cands = [(c, o) for c in (0, 1, 2, 3, 4, 6) for o in range(len(OPTIONS)) if o != self.H[c]
                         and self.hst.get((c, o), [0])[0] >= 0]
                if not cands:                           # every change dropped: all may be tried again
                    self.hst = {}
                    cands = [(c, o) for c in (0, 1, 2, 3, 4, 6) for o in range(len(OPTIONS)) if o != self.H[c]]
                self.hcand = cands[int(self.srng.integers(len(cands)))] if cands else None
                self.horder = int(self.srng.integers(2))
                self.hph, self.hr = 1, 0.0
            elif self.hph == 1:
                self.hA, self.hr, self.hph = self.hr, 0.0, 2
            else:
                trial, kept = (self.hA, self.hr) if self.horder == 0 else (self.hr, self.hA)
                if self.hcand is not None:
                    st = self.hst.setdefault(self.hcand, [0, 0.0, 0.0])
                    d = trial - kept
                    st[0] += 1; st[1] += d; st[2] += d * d
                    n, m = st[0], st[1] / st[0]
                    se = math.sqrt(max(st[2] / n - m * m, 1e-9) / n) if n > 1 else 1e9
                    if n >= 3 and m > 2 * se:           # surely better: kept; the context's other trials start afresh
                        c, o = self.hcand
                        self.H[c] = o
                        self.hst = {k: v for k, v in self.hst.items() if k[0] != c}
                    elif n >= 8 or (n >= 3 and m < -2 * se):
                        st[0] = -1                      # dropped
                self.hph = 0
            trial_now = (self.hph == 1 and self.horder == 0) or (self.hph == 2 and self.horder == 1)
            self.Hcur = list(self.H)
            if trial_now and self.hcand is not None:
                c, o = self.hcand
                self.Hcur[c] = o
                if c in (1, 3):
                    self.Hcur[c + 4] = o
            self.ht0 = self.t

        def taste(self, value, at):
            if search:
                self.hr += 1.0 if value > 0 else -1.0
            self.r += 1.0 if value > 0 else -1.0
            if knobs:
                self.kr += 1.0 if value > 0 else -1.0
            self.tasted = True
            return super().taste(value, at)

        def _q(self, ctx, o):
            """A pair's value; with share, a fine context's value pulled towards its coarse parent's (the same context without time)
            until it has uses of its own: (n Q_fine + SHARE_K Q_coarse) / (n + SHARE_K)."""
            if not share:
                return self.Q.get((ctx, o), 0.0)
            n = self.N.get((ctx, o), 0)
            return (n * self.Q.get((ctx, o), 0.0) + SHARE_K * self.Q.get((("c", ctx % 4), o), 0.0)) / (n + SHARE_K)

        def _choose(self, ctx):
            if search and self.H is not None:           # habit search (O24): after play, the habit on trial or the kept one
                return self.Hcur[ctx]
            fp = getattr(self, "FP", None)              # a habit forced (lab/habits.py): one option per context, no learning, no play
            if fp:
                return fp[ctx] if ctx < len(fp) else fp[ctx % 4]
            if FORCE:                                   # a diagnosis: the circuit's own policy forced, no learning, no play
                if FORCE2 and ctx >= 4:                 # (FORCE=2, with bored: the circuit's run, straight at its run rate)
                    return 2
                return {0: 0, 1: 2, 2: 0, 3: 0}[ctx % 4]
            eps = 1.0 if self.t < PLAY else EPS
            if EXPL == "fade" and self.t >= PLAY:     # exploration fading with each context's experience
                n = sum(1 for k in self.Q if k[0] == ctx) and self.cuses.get(ctx, 0)
                eps = 1.0 / math.sqrt(1.0 + n / 10.0)
            self.cuses[ctx] = self.cuses.get(ctx, 0) + 1
            nopt = len(OPTIONS) * (int(rates) if rates else 1)   # rates: each pattern at one of the circuit's rates, chosen too
            if self.srng.random() < eps:
                return int(self.srng.integers(nopt))
            return max(range(nopt), key=lambda o: self._q(ctx, o))

        def step(self):
            super().step()
            p = self.p
            f, w = self.food, (OPTW if OPTW else p["hold"])   # (OPTW: how long a pulse keeps its colour "in view", a test)
            if fine:                                    # finer contexts: each eye's pulses within the hold, none, one or several (near/far)
                self.recent = [x for x in self.recent if x[0] > self.t - w]
                nf = min(2, sum(1 for _, e in self.recent if e == f))
                no = min(2, sum(1 for _, e in self.recent if e != f))
                ctx = nf + 3 * no
            else:
                ctx = int(self.t - self.lastpulse[f] < w) + 2 * int(self.t - self.lastpulse[1 - f] < w)
            if timed and not (ctx & 1):                 # contexts carrying time: since the followed colour was last seen, in steps of four
                since = self.t - self.lastpulse[f]      # (under 1 s, 1 to 4, 4 to 16, over 16)
                ctx += 4 * (0 if since < 1.0 else 1 if since < 4.0 else 2 if since < 16.0 else 3)
            if knobs:
                self._knobs()
            if search:
                self._search()
            if bored and self.t - max(self.lastpulse[f], self.last_food, self.lastrun) > self.kv("bored"):
                ctx += 4                                # bored: nothing of the followed colour for longer than the circuit's own timer
                if knobs and self.t - max(self.lastpulse[f], self.last_food, self.lastrun) > self.kv("bored") + self.kv("runlen"):
                    self.lastrun = self.t               # with knobs, a bored run lasts runlen, then the bored timer restarts
                    ctx -= 4
            ended = self.srng.random() < 0.0025 / T_END    # an option also ends at random (termination probability, mean T_END s)
            if ctx != self.ctx or self.tasted or ended:
                o = self._choose(ctx)
                if self.prev is not None:
                    d = self.t - self.t0
                    k = math.exp(-d / RHO_T)
                    self.R, self.D = self.R * k + self.r, self.D * k + d
                    rho = self.R / self.D if cost else 0.0
                    q = self.Q.get(self.prev, 0.0)
                    nxt = self._q(ctx, o)
                    if avg == "post":                   # a step shrinking with the pair's own uses after play: 1/(n + 10), from ALPHA down
                        if self.t >= PLAY:
                            self.N[self.prev] = self.N.get(self.prev, 0) + 1
                        al = max(1.0 / (self.N.get(self.prev, 0) + 1.0 / ALPHA), AFLOOR)
                    elif avg:                           # a value as an average of all its evidence: step 1/n (floor AFLOOR)
                        self.N[self.prev] = self.N.get(self.prev, 0) + 1
                        al = max(1.0 / self.N[self.prev], AFLOOR)
                    else:
                        al = ALPHA
                    delta = self.r - rho * d + nxt - q
                    self.Q[self.prev] = q + al * delta
                    if lam:                             # the error reaches back over earlier episodes, each by lam per episode since (SMDP TD(lam))
                        for pr, w in self.elig:
                            self.Q[pr] = self.Q.get(pr, 0.0) + al * w * delta
                        self.elig = [(pr, w * lam) for pr, w in [(self.prev, 1.0)] + self.elig if w * lam > 0.02][:30]
                    if share:                           # the coarse parent learns from every episode too
                        cp = (("c", self.prev[0] % 4), self.prev[1])
                        qc = self.Q.get(cp, 0.0)
                        self.Q[cp] = qc + ALPHA * (self.r - rho * d + nxt - qc)
                        self.N[self.prev] = self.N.get(self.prev, 0) + 1
                self.prev, self.cur, self.t0, self.r, self.ctx, self.tasted = (ctx, o), o, self.t, 0.0, ctx, False
                self.episodes += 1
            if rates:
                rate = p[("scan", "drive", "run")[self.cur // len(OPTIONS)]]
                pat = OPTIONS[self.cur % len(OPTIONS)]
            else:
                rate = self.kv("drive") if ((ctx % 3) > 0 if fine else (ctx & 1)) else self.kv("run") if ((bored or (timed and not NATRATE)) and ctx >= 4) else self.kv("scan")
                pat = OPTIONS[self.cur]
            self.ph += rate * 0.0025
            n = int(self.ph)
            self.ph -= n
            if self.t - getattr(self, "_logt", -1e9) > 10.0:
                self._logt = self.t
                nopt = len(OPTIONS) * (int(rates) if rates else 1)
                self.log_reflex = {c: max(range(nopt), key=lambda o: self.Q.get((c, o), 0.0)) for c in range(16 if timed else 8 if bored else 4)}
                if knobs:
                    self.log_reflex["knobs"] = (dict(self.th0), dict(self.th))
                if search and self.H is not None:
                    self.log_reflex.update({c: self.H[c] for c in range(8)})
                if self.t > 800.0:                      # flicker: how often the best option per context changed over the last third (10 s looks)
                    lr = getattr(self, "_lastlr", None)
                    if lr is not None:
                        self._flick = getattr(self, "_flick", 0) + sum(1 for c in lr if isinstance(c, int) and lr[c] != self.log_reflex[c])
                    self.log_reflex["flicker"] = getattr(self, "_flick", 0)
                self._lastlr = dict(self.log_reflex)
            return list(pat) * n
    return Opt


T_END = 2.0                                     # s: an option's mean length when its context doesn't change (random termination)
OPTW = float(__import__("os").environ.get("OPTW", 0.0))   # s: "in view" after a pulse (0: the circuit's hold)
FORCE = __import__("os").environ.get("FORCE") in ("1", "2")
FORCE2 = __import__("os").environ.get("FORCE") == "2"   # a diagnosis: options carry out the circuit's policy, unlearned
NATRATE = __import__("os").environ.get("NATRATE") == "1"   # time contexts keep the natural rate (scan), the confound of O17-O18 removed
KNOBS = ("scan", "drive", "run", "bored", "runlen")   # the rhythm's settings a learner may tune (D64)
KE = float(__import__("os").environ.get("KE", 20.0))  # s: an epoch of one perturbation
SIG_K = 0.5                                     # log2: a perturbation's size (a factor 1.41)
ETA_K = float(__import__("os").environ.get("ETA_K", 0.1))  # log2: a knob's step per pair, at a one-sigma difference
HE = float(__import__("os").environ.get("HE", 20.0))   # s: an epoch of habit search (O24)
HSTART = float(__import__("os").environ.get("HSTART", 400.0))   # s: habit search starts (the values' learning before it)
AFLOOR = float(__import__("os").environ.get("AFLOOR", 0.01))   # averaged values: the smallest step
SHARE_K = 10.0                                  # uses' worth of prior a fine context takes from its coarse parent
RHO_T = 100.0                                   # s: the running reward rate forgets over this


def trace_cls(base, multi=False, cue=False):
    """The steering by an eligibility trace (QUESTIONS.md: crediting a taste seconds after the actions that led to it). Every DECIDE s
    the brain picks an option for its context (whether the followed eye, and the other, pulsed in the last CTX s: relative to the colour
    followed, so a flip of colour needs no relearning). Each (context, option) pair is a unit with a fading mark: a choice adds 1 to its
    pair's mark, every mark fades with TAU_E; a taste (+1 food, -1 poison) is credited to every pair in proportion to its mark. A pair's
    value is the reward credited to it per use. Choice: the best value, untried options first, another at random EPS of the time (all
    of the time during the first PLAY s). Nothing written by hand about what a thruster does or when to go straight.
    multi (2026-11-14): marks at four time constants, drawn per life log-uniform 1 to 30 s; a taste credits every mark; a pair's value the
    mean over the four of its credit per use (so a choice can be credited by food found tens of seconds later).
    cue (2026-11-14): "the followed eye starts pulsing" (its first pulse after a silence of the circuit's hold) is an event with marks of
    its own, credited by tastes like a pair, so it learns how much food follows it; each time it happens, it pays that learned value to
    the pairs then marked (secondary reinforcement: the cue's worth learned, not set)."""

    class Traced(base):
        def __init__(self, seed, p):
            super().__init__(seed, p)
            self.lastpulse = [-1e9, -1e9]
            self.mark, self.got, self.uses = {}, {}, {}
            self.tm, self.cur, self.until, self.ph = 0.0, None, -1.0, 0.0
            self.srng = np.random.default_rng([int(seed), 95])
            trng = np.random.default_rng([int(seed), 97])
            self.taus = list(np.exp(trng.uniform(np.log(1.0), np.log(30.0), 4))) if multi else [TAU_E]
            self.cmark, self.cgot, self.cuses = [0.0] * len(self.taus), 0.0, 0
            self.silent_since = 0.0

        def stimulate(self, sensor, at):
            if sensor in (0, 1):
                if cue and sensor == self.food and self.t + at - self.lastpulse[sensor] > self.p["hold"]:
                    self._cue()
                self.lastpulse[sensor] = self.t + at
            return super().stimulate(sensor, at)

        def _fade(self):
            ws = [math.exp(-(self.t - self.tm) / tau) for tau in self.taus]
            for k in self.mark:
                self.mark[k] = [m * w for m, w in zip(self.mark[k], ws)]
            self.cmark = [m * w for m, w in zip(self.cmark, ws)]
            self.tm = self.t

        def _pay(self, r):
            for k, ms in self.mark.items():
                g = self.got.setdefault(k, [0.0] * len(self.taus))
                for i, m in enumerate(ms):
                    g[i] += r * m

        def _cue(self):
            """The cue happened: it is marked (to be credited by later tastes), and pays its learned worth to the pairs now marked."""
            self._fade()
            if self.cuses:
                self._pay(self.cgot / self.cuses)
            self.cmark = [m + 1.0 for m in self.cmark]
            self.cuses += 1

        def taste(self, value, at):
            self._fade()
            r = 1.0 if value > 0 else -1.0
            self._pay(r)
            if cue:
                self.cgot += r * sum(self.cmark) / len(self.cmark)
            return super().taste(value, at)

        def step(self):
            super().step()                      # the starting circuit: its colour, its timers (its beats discarded)
            p = self.p
            if self.t >= self.until:
                f = self.food
                w = p["hold"] if HOLDCTX else CTX       # (HOLDCTX: "just pulsed" lasts the starting circuit's own hold, not CTX)
                ctx = int(self.t - self.lastpulse[f] < w) + 2 * int(self.t - self.lastpulse[1 - f] < w)
                eps = 1.0 if self.t < PLAY else EPS
                def val(o):
                    n = self.uses.get((ctx, o), 0)
                    return 1e9 if n == 0 else sum(self.got.get((ctx, o), [0.0])) / len(self.taus) / n
                o = int(self.srng.integers(len(OPTIONS))) if self.srng.random() < eps else max(range(len(OPTIONS)), key=val)
                self._fade()
                self.mark[(ctx, o)] = [m + 1.0 for m in self.mark.get((ctx, o), [0.0] * len(self.taus))]
                self.uses[(ctx, o)] = self.uses.get((ctx, o), 0) + 1
                self.cur, self.until = o, self.t + DECIDE
                self.rate = p["drive"] if ctx & 1 else p["scan"]
            self.ph += self.rate * 0.0025
            n = int(self.ph)
            self.ph -= n
            if self.t - getattr(self, "_logt", -1e9) > 10.0:
                self._logt = self.t
                self.log_reflex = {c: max(range(len(OPTIONS)), key=lambda o: sum(self.got.get((c, o), [0.0])) / max(self.uses.get((c, o), 0), 1)) for c in range(4)}
            return list(OPTIONS[self.cur]) * n
    return Traced


def grown_cls(base):
    import grownet as GN

    class Grown(base):
        def __init__(self, seed, p):
            super().__init__(seed, p)
            self.lastpulse = [-1e9, -1e9]
            self.pulses = []
            self.nets = [GN.Net(f"eye{e}", 40, np.random.default_rng([int(seed), 91 + e]), alphabet=4 + len(OPTIONS), strict=True) for e in (0, 1)]
            self.gi, self.trial, self.reflex, self.srng = 0, None, None, np.random.default_rng([int(seed), 93])
            self.ph = 0.0
            self.pairs = {}

        def stimulate(self, sensor, at):
            if sensor in (0, 1):
                self.lastpulse[sensor] = self.t + at
                self.pulses.append((self.t + at, sensor))
            return super().stimulate(sensor, at)

        def _ctx(self):
            a, b = self.t - self.lastpulse[0] < CTX, self.t - self.lastpulse[1] < CTX
            return int(a) + 2 * int(b)          # 0 none, 1 eye 0, 2 eye 1, 3 both

        def _count(self, e, a, b):
            return sum(1 for t, s in self.pulses if s == e and a <= t < b)

        def _close(self):
            tr = self.trial
            # the pair detectors present from birth (every context with every option: 16 units, a starting repertoire of pairs, not
            # a reflex): each keeps the graded change of each eye after its pair
            v = self.pairs.setdefault((tr["ctx"], tr["opt"]), [[0, 0.0, 0.0], [0, 0.0, 0.0]])
            for e in (0, 1):
                x = self._count(e, tr["t0"], tr["t0"] + TRY) - self._count(e, tr["t0"] - TRY, tr["t0"])
                v[e][0] += 1
                v[e][1] += x
                v[e][2] += x * x
            sym = [tr["ctx"], 4 + tr["opt"]]
            for e, N in enumerate(self.nets):
                x = self._count(e, tr["t0"], tr["t0"] + TRY) - self._count(e, tr["t0"] - TRY, tr["t0"])
                for j, s in enumerate(sym):
                    N.write(self.gi + j, s)
                k, f = N.says(self.gi + 1)
                N.add_value(f, float(x))
                if x != 0:
                    N.learn(self.gi + 1, int(x > 0), self.t, k, f)
                N.tidy(self.gi + 1, self.t)
            self.gi += 2
            self.pulses = [x for x in self.pulses if x[0] > self.t - 2 * TRY]
            self.trial = None

        def _unit(self, N, ctx, opt):
            """The block for (context, option): the option's sense unit if no block joins them."""
            best = None
            for x in N.units.values():
                if x["sym"] is None and x.get("val") and N.units.get(x["v"], {}).get("sym") == 4 + opt and N.units.get(x["u"], {}).get("sym") == ctx:
                    best = x
            return best

        def _wire(self):
            """Each context's reflex: the option surely raising the eye that matters, against none in that context."""
            self.reflex = {}
            for ctx in range(4):
                for e in (0, 1):
                    N = self.nets[e]
                    none = self.pairs.get((ctx, len(OPTIONS) - 1))
                    z = {o: N.welch((self.pairs.get((ctx, o)) or [None, None])[e], none[e] if none else None) for o in range(len(OPTIONS) - 1)}
                    good = [o for o, v in z.items() if v >= SURE]
                    if good:
                        self.reflex[(ctx, e)] = OPTIONS[max(good, key=lambda o: z[o])]
            self.log_reflex = dict(self.reflex)

        def step(self):
            out = super().step()                # the starting circuit's own step: its colour, its timers (its beats discarded)
            p = self.p
            if self.t < PLAY:
                if self.trial is not None and self.t >= self.trial["t0"] + TRY:
                    self._close()
                if self.trial is None and self.srng.random() < TRY * 0.5 * 0.0025 / TRY * 40:
                    self.trial = dict(t0=self.t, ctx=self._ctx(), opt=int(self.srng.integers(len(OPTIONS))))
                if self.trial is not None:
                    self.ph += p["drive"] * 0.0025
                    n = int(self.ph)
                    self.ph -= n
                    return list(OPTIONS[self.trial["opt"]]) * n
                return []
            if self.reflex is None:
                self._wire()
            if LIFELONG:                                # the pairs keep learning through the life: each moment a trial, mostly the best
                f = self.food                           # option so far in its context, sometimes another (EPS); judged as in play
                if self.trial is not None and self.t >= self.trial["t0"] + TRY:
                    self._close()
                if self.trial is None:
                    ctx = self._ctx()
                    seen = self.t - self.lastpulse[f] < CTX
                    target = f if seen else None
                    def score(o):
                        v = self.pairs.get((ctx, o))
                        if not v:
                            return 1e9                  # untried: try it
                        if target is not None:
                            return v[target][1] / max(v[target][0], 1)
                        return (v[0][1] + v[1][1]) / max(v[0][0] + v[1][0], 1)
                    o = int(self.srng.integers(len(OPTIONS))) if self.srng.random() < EPS else max(range(len(OPTIONS)), key=score)
                    self.trial = dict(t0=self.t, ctx=ctx, opt=o, rate=p["drive"] if seen else p["scan"])
                self.ph += self.trial.get("rate", p["drive"]) * 0.0025
                n = int(self.ph)
                self.ph -= n
                return list(OPTIONS[self.trial["opt"]]) * n
            f = self.food
            seen = self.t - self.lastpulse[f] < CTX
            ctx = self._ctx()
            if seen:
                opt, rate = self.reflex.get((ctx, f)), p["drive"]
            else:
                opt = self.reflex.get((0, 0)) or self.reflex.get((0, 1))
                rate = p["scan"]
            if not opt:
                return []
            self.ph += rate * 0.0025
            n = int(self.ph)
            self.ph -= n
            return list(opt) * n
    return Grown


def job(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    from stage2_lang.sim import WLife
    from stage2_lang.seconds import seconds_cls
    import table as T
    arm, text, seed, first, secs = j
    if arm == "circuit":
        lf = S.make(S.world_of(text), "circuit", seed, first)
    elif arm == "circraw":                              # the hand-built drive without the muscle retune (as if the body changed after birth)
        lf = S.make(S.world_of(text), "circuit", seed, first, {"raw": 1})
    elif arm in ("net", "netopt"):                     # G3: the frozen growing network's choice of colour (net10kc60S), with the
        import grownet as GN                            # hand-built drive (net) or grown held options (netopt)
        P = int(__import__("os").environ.get("NETP", 2240))
        if arm not in _C:
            G = GN.net_cls(senses=True, split=True, clocks=60, reset="change", fade=False, ondemand=True, strict=True, wmaj="spec")
            _C[arm] = seconds_cls(option_cls(G) if arm == "netopt" else G)
        q = T.numbers(seed, {"P": P})
        q["P"] = P
        lf = WLife(seed, first, (lambda s: _C[arm](s, q)), S.world_of(text), seconds=True)
    else:
        if arm not in _C:
            base = T.Circuit
            if arm == "still":
                class Still(base):
                    def step(self):
                        super().step()
                        return []
                _C[arm] = seconds_cls(Still)
            elif arm in ("opt", "optN", "opt8", "opt12", "optF", "optB", "optT", "optTS"):
                _C[arm] = seconds_cls(option_cls(base, cost=arm != "optN", rates={"opt8": 2, "opt12": 3}.get(arm, False), fine=arm == "optF",
                                                 bored=arm == "optB", timed=arm in ("optT", "optTS"), share=arm == "optTS"))
            elif arm == "optH":                         # O24: habit search after play, over optBa's values
                _C[arm] = seconds_cls(option_cls(base, bored=True, avg="post", search=True))
            elif arm.startswith("optBl"):               # O23: optBa with the error reaching back over earlier episodes (optBl8: lam .8)
                _C[arm] = seconds_cls(option_cls(base, bored=True, avg="post", lam=int(arm[5:]) / 10.0))
            elif arm in ("optBn", "optn", "optBa"):     # values as averages of all their evidence (O20); a: counted after play (O22)
                _C[arm] = seconds_cls(option_cls(base, bored=arm != "optn", avg="post" if arm == "optBa" else True))
            elif arm in ("optK", "optKw", "optK0", "optKw0"):   # optB with the rhythm's knobs: tuned from a random start (K), from the
                kn = "warm" if "w" in arm else "rand"   # circuit's values (Kw); 0: the same start, never tuned
                C = option_cls(base, bored=True, knobs=kn)
                if arm.endswith("0"):
                    C = type("Fixed", (C,), {"_knobs": lambda self: None})
                _C[arm] = seconds_cls(C)
            elif arm.startswith("pol"):                 # "pol0200": a habit forced, options for contexts 0-3; "pol0200xx": with bored (4-7)
                digits = tuple(int(c) for c in arm[3:])
                C = option_cls(base, bored=len(digits) > 4)
                _C[arm] = seconds_cls(type("Pol", (C,), {"FP": digits}))
            elif arm == "td":
                _C[arm] = seconds_cls(td_cls(base))
            elif arm.startswith("traced"):
                _C[arm] = seconds_cls(trace_cls(base, multi="M" in arm[6:], cue="Q" in arm[6:]))
            else:
                _C[arm] = seconds_cls(grown_cls(base))
        q = T.numbers(seed, {})
        lf = WLife(seed, first, (lambda s: _C[arm](s, q)), S.world_of(text), seconds=True)
    l = S.live(lf, secs)
    g = [a - COST * b for a, b, _ in l]
    sp = spent(l)
    return dict(arm=arm, seed=seed, eff=(sum(g), sp, g[2], sp * l[2][2] / sum(t for _, _, t in l)),
                reflex=getattr(lf.brain, "log_reflex", None), food=getattr(lf.brain, "food", None))


if __name__ == "__main__":
    a = sys.argv[1:]
    n = int(a[0]) if a and a[0].isdigit() else 10
    wname = a[1] if len(a) > 1 else "plain"
    secs = float(__import__("os").environ.get("SECS", {"plain": 300.0, "seq5": 300.0, "seq11": 600.0, "combo3": 1200.0, "time2": 1200.0}[wname]))
    text = {"plain": L.PLAIN, "seq5": L.seq(5), "seq11": L.seq(11), "combo3": L.combo(3), "time2": L.timing(2)}[wname]
    s0 = next((int(x[1:]) for x in a if x.startswith("s") and x[1:].isdigit()), 130000)
    import os
    arms = tuple(os.environ.get("ARMS", "circuit,traced,still").split(","))
    out = f"/home/pilgrim/git/simple-learner/lab/v/steer{'_muscle' if __import__('os').environ.get('MUSCLE') == '1' else ''}_{wname}_{n}_s{s0}_{int(secs)}s_{'-'.join(arms)}{'_w' + __import__('os').environ['OPTW'] if __import__('os').environ.get('OPTW') else ''}{'_eps' + __import__('os').environ['EPS'] if __import__('os').environ.get('EPS') else ''}{'_' + __import__('os').environ['EXPL'] if __import__('os').environ.get('EXPL') else ''}{'_force' + __import__('os').environ['FORCE'] if __import__('os').environ.get('FORCE') else ''}{'_natrate' if __import__('os').environ.get('NATRATE') == '1' else ''}.pkl"
    if "report" not in a:
        import ledger
        ledger.start()
        with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
            rows = list(ex.map(job, [(arm, text, s, c, secs) for arm in arms for s in range(s0, s0 + n) for c in L.COL], chunksize=2))
        pickle.dump(rows, open(out, "wb"))
    rows = pickle.load(open(out, "rb"))
    I = R.boot(n)
    e = {arm: L.scored([r["eff"] for r in rows if r["arm"] == arm], secs, I) for arm in arms}
    print(f"== the steering grown: {wname}, {n} pairs, {secs:.0f} s, last third [95%]")
    for arm in arms:
        d = e[arm][1] - e["circuit"][1]
        line = f"  {arm:8s} {e[arm][0]:+.2f} [{np.percentile(e[arm][1], 2.5):+.2f},{np.percentile(e[arm][1], 97.5):+.2f}]"
        if arm != "circuit":
            line += f"  vs circuit {e[arm][0] - e['circuit'][0]:+.2f} [{np.percentile(d, 2.5):+.2f},{np.percentile(d, 97.5):+.2f}]"
        if arm.startswith("grown") or arm.startswith("traced") or arm in ("td", "opt", "optN", "opt8", "opt12", "optF", "optB", "optT", "optTS", "optBn", "optn", "optBa", "optH") or arm.startswith("optBl"):
            from collections import Counter
            line += " | best option by context (0 none, 1 followed eye, 2 other, 3 both): " + ", ".join(f"{k} x{v}" for k, v in Counter(str(r["reflex"]) for r in rows if r["arm"] == arm).most_common(3))
        print(line, flush=True)

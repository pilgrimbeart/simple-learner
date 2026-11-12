"""play3.py: play first, the challenge later: three generic links from what play learned to the balance knob (the user, 2026-11-10: try
all of them). The play is play2.py's (40 random rhythm units, turns by learning progress, ending by itself), on bodies with each
thruster drawn (a half to twice); then the starting brain forages, its balance knob set by the link. 900 s lives, judged on the last
third.

What play leaves, for every link (two statistics: `sight`, the default, and `recur`, as arm:recur):
  beats   (partners, partnerstaste, and partnersalt: taste picks among play's best and each motor's rival period, 30 s each) each motor's beats a revolution from every run in which it alone beat, D43's record clocked by
          its own beats, pooled over runs.
  burst   for each mix, one over the median length of a sighting (a block stays in view for a time that goes as one
          over how fast the mix turns), weighted by its sightings.
  sight   for each mix, new sightings a second (bursts of eye pulses), which rises with how fast it turns the view; needs no revolution.
  recur    each stretch of steady motor mix it played (a unit's on part or off part: rates r0, r1 a second) and
the eye pulses during it. For each mix, pooled over its stretches, the recurrence of the view in seconds: pairs of pulses within one
stretch, excess over chance at each lag, the period chosen by excess summed over all its multiples (D44's rule, here in seconds since
the mixes beat both motors); a mix counts if that excess is clear (STRONG). Its frequency f = 1 / period: how fast that mix turns the view.

The links (none is told anything about this body):
  steady    gaze stabilisation (an inherited goal: driving at something, the view should stay still). A forward model learned from every
            counted mix, f = |a r0 - b r1| (how fast a mix turns the view, either way), fitted by least squares; the drive's mix is set
            where the model predicts no turning: the knob's balance log(b / a).
  partners  partners equalise: only the mixes that beat one motor alone; each motor's effect a beat, a = f / r0 and b = f / r1
            (pooled); the knob makes the two motors' effect equal: log(b / a).
  taste     taste picks: after play, the forager tries each of five balances spanning the prior (-1 to 1) for SLOT s, twice round, and
            keeps the one that ate most (good meals less poisoned ones); play itself proposes nothing (taste's own power, in the same time).
  steadytaste  taste picks among the steady link's estimate and that +- .3.
Links added for P2: readout (taste tries nine signed combinations of the two motors' measures), readw (a
readout w0 b0 + w1 b1 + c learned across lives, as readw:beats:w=w0/w1/c).
Options, as arm:option: stall (units in a shuffled cycle; play over when the knob's estimate has stopped moving, its
last five within .05; a taste ends play too), mover (the same end; each turn to the unit whose last turn moved the estimate most),
certain (units in a shuffled cycle; bored when each motor's best period beats its rival by SURE; a taste
ends play too; a motor still in doubt hands its rival to taste, 30 s a candidate), certainmover (the same; each turn to the unit whose
last turn raised the certainty most), for400 (play exactly 400 s, no other end: P1), handoff (the certainty hand-off whoever chose the turns),
untaste (forage, but play another round whenever 30 s pass with no taste at all; the first taste
ends play: play whenever nothing better is on), practice (the steady model keeps learning after play from the forager's scans and runs,
refitted every 30 s), n10 (a bank of 10 units, the life's own draw from the 40), t10 (turns of 10 s).
Arms beside them: forage (the starting brain all life, no play), told (the knob set right: a yardstick's privilege), play (play, knob
untouched).

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 BELIEF=... PREDICT=... .venv/bin/python lab/play3.py [PAIRS] [arms]"""
import math
import pickle
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np

import bodyladder as BL
import play2 as P2
import stage3_random as R

SEEDS0 = 91000                                  # development seeds, fresh
SECS = 900.0
WORLD = BL.WORLDS["thr"][0]                     # each thruster's strength drawn, a half to twice
EDGES = np.geomspace(0.05, 10.0, 61)            # s: lag bins for a mix's recurrence
STRONG = 3.0                                    # excess (in chance's spread, summed over multiples) for a mix's period to count
SLOT = 30.0                                     # s: a taste trial of one balance
RSLOT = 20.0                                    # s: a taste trial of one readout (P2, route A: nine of them)
GRID = (-1.0, -0.5, 0.0, 0.5, 1.0)
SURE = 3.0                                      # certain: a motor's best period beats its rival by this (in chance's spread)
STALL, STALL_N = 0.05, 5                        # bore: play is over when the last STALL_N estimates span under STALL
QUIET = 30.0                                    # s: foraging this long with no taste at all brings another round of play (untaste)
WIN = 0.5                                       # s: practice windows (one mix each)
REFIT = 30.0                                    # s: the practising model refits this often


def recurrence(pulses, stretches):
    """(period s, strength) of the view's recurrence pooled over stretches [(t0, t1)], from pulse times (sorted)."""
    c, e = np.zeros(len(EDGES) - 1), np.zeros(len(EDGES) - 1)
    w = np.diff(EDGES)
    for t0, t1 in stretches:
        L = t1 - t0
        p = pulses[np.searchsorted(pulses, t0):np.searchsorted(pulses, t1)]
        n = len(p)
        if n < 2:
            continue
        d = (p[None, :] - p[:, None])[np.triu_indices(n, 1)]
        c += np.histogram(d, EDGES)[0]
        e += n * n / L * w * np.maximum(1 - EDGES[:-1] / L, 0)    # pairs i < j at a lag, by chance: n^2 (L - lag) w / L^2
    x = (c - e) / np.sqrt(e + 1)
    lag = np.sqrt(EDGES[1:] * EDGES[:-1])
    cands = np.geomspace(0.15, 8.0, 150)
    s = []
    for T in cands:
        m = np.arange(1, int(lag[-1] // T) + 1) * T
        s.append(np.interp(m, lag, x).sum() / math.sqrt(len(m)))
    i = int(np.argmax(s))
    return cands[i], s[i]


def fit_steady(mixes):
    """mixes: [(r0, r1, f, weight)]. Fit f = |a r0 - b r1| (a, b > 0) by weighted least squares: for each ratio b / a on a grid the
    best scale is closed-form. Returns log(b / a), or None."""
    if len(mixes) < 2:
        return None
    r0, r1, f, wt = (np.array(v, float) for v in zip(*mixes))
    best = None
    for lr in np.linspace(-2.5, 2.5, 501):
        g = np.abs(r0 - math.exp(lr) * r1)
        den = (wt * g * g).sum()
        if den <= 0:
            continue
        a = (wt * g * f).sum() / den
        err = (wt * (a * g - f) ** 2).sum()
        if best is None or err < best[0]:
            best = (err, lr)
    return best[1]


def partners(mixes):
    a = [(f / r0, wt) for r0, r1, f, wt in mixes if r0 > 0 and r1 == 0]
    b = [(f / r1, wt) for r0, r1, f, wt in mixes if r1 > 0 and r0 == 0]
    if not a or not b:
        return None
    av = sum(x * w for x, w in a) / sum(w for _, w in a)
    bv = sum(x * w for x, w in b) / sum(w for _, w in b)
    return math.log(bv / av)


def sightings(pulses, stretches, gap=0.15):
    """New sightings a second over the stretches: bursts of pulses, a burst ending at a gap over `gap` s. Turning sweeps the view
    across blocks, so this rises with how fast a mix turns, and needs no whole revolution within a stretch."""
    n, L = 0, 0.0
    for t0, t1 in stretches:
        p = pulses[np.searchsorted(pulses, t0):np.searchsorted(pulses, t1)]
        n += (1 + int(np.sum(np.diff(p) > gap))) if len(p) else 0
        L += t1 - t0
    return n / L, L


def bursts(pulses, stretches, gap=0.15):
    """(1 / median length of a sighting, sightings): a block stays in view for a time that goes as one over how fast the mix turns the
    view; each sighting is its own measurement, so short stretches serve. None with fewer than 3 sightings of two pulses or more."""
    d = []
    for t0, t1 in stretches:
        p = pulses[np.searchsorted(pulses, t0):np.searchsorted(pulses, t1)]
        if len(p) < 2:
            continue
        cut = np.where(np.diff(p) > gap)[0]
        for a, z in zip(np.r_[0, cut + 1], np.r_[cut, len(p) - 1]):
            if a < z:
                d.append(p[z] - p[a])
    return (1.0 / float(np.median(d)), float(len(d))) if len(d) >= 3 else None


def beat_runs(beat_log, pulses, minrun=24, K=128):
    """For each motor, every run of beats in which it alone beat (at least minrun beats) as a record clocked by its own beats (D43:
    a cell a beat, did an eye pulse since its last beat?), coincidences at each look-back against chance, summed over runs; the
    fundamental by excess summed over all its multiples (D44). Rate changes within a run don't matter: the beats are the ruler.
    Returns each motor's log beats a revolution, or None."""
    import dance0 as D0
    out = []
    for m in (0, 1):
        tot = np.zeros(K)
        run, have = [], False
        def flush(run):
            nonlocal have
            if len(run) >= minrun:
                c = (np.diff(np.searchsorted(pulses, np.array(run))) > 0).astype(float)
                q = c.mean()
                for k in range(1, min(K, len(c) - 1) + 1):
                    e = (len(c) - k) * q * q
                    tot[k - 1] += ((c[k:] * c[:-k]).sum() - e) / math.sqrt(e + 1)
                have = True
        for t, mm in beat_log:
            if mm == m:
                run.append(t)
            else:
                flush(run)
                run = []
        flush(run)
        out.append(_top2(tot, np.arange(1.0, K + 1)) if have else None)
    return out


def _top2(v, x, lo=4.0, hi=90.0):
    """D44's fundamental (excess summed over all multiples over their number's square root), and its best rival: the highest-scoring
    period not within a quarter of it. Logs of beats a revolution: (best, rival)."""
    c = np.geomspace(lo, hi, 200)
    sc = np.array([np.interp(np.arange(1, int(x[-1] // T) + 1) * T, x, v).sum() / math.sqrt(int(x[-1] // T)) for T in c])
    i = int(np.argmax(sc))
    peak = np.r_[False, (sc[1:-1] > sc[:-2]) & (sc[1:-1] >= sc[2:]), False]     # rivals are other peaks, not the best's own shoulder
    far = peak & (np.abs(np.log(c / c[i])) > math.log(1.25))
    if not far.any():
        far = np.abs(np.log(c / c[i])) > math.log(1.25)
    j = int(np.argmax(np.where(far, sc, -np.inf)))
    return math.log(c[i]), math.log(c[j]), float(sc[i] - sc[j])      # and the margin: how clearly the best beats its rival


def _lin(X, y, w):
    """Weighted least squares y = X beta; (beta, error)."""
    sw = np.sqrt(w)
    beta = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)[0]
    return beta, float((w * (X @ beta - y) ** 2).sum())


def fit_steady_c(mixes):
    """Sightings a second = c + s |r0 - (b / a) r1| (c: sightings from moving forward), weighted by time played; the ratio on a grid,
    c and s by least squares (s > 0). Returns log(b / a), or None."""
    if len(mixes) < 4:
        return None
    r0, r1, y, w = (np.array(v, float) for v in zip(*mixes))
    best = None
    for lr in np.linspace(-2.5, 2.5, 501):
        X = np.column_stack([np.ones_like(r0), np.abs(r0 - math.exp(lr) * r1)])
        beta, err = _lin(X, y, w)
        if beta[1] > 0 and (best is None or err < best[0]):
            best = (err, lr)
    return None if best is None else best[1]


def partners_c(mixes):
    """One motor alone: sightings a second = c + a r0, or c + b r1, c shared; log(b / a), or None."""
    m = [(r0, r1, y, w) for r0, r1, y, w in mixes if (r0 == 0) != (r1 == 0)]
    if sum(1 for x in m if x[1] == 0) < 2 or sum(1 for x in m if x[0] == 0) < 2:
        return None
    r0, r1, y, w = (np.array(v, float) for v in zip(*m))
    beta, _ = _lin(np.column_stack([np.ones_like(r0), r0, r1]), y, w)
    return math.log(beta[2] / beta[1]) if beta[1] > 0 and beta[2] > 0 else None


class Play3(P2.PlayBrain):
    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.link, self.stat = p["link"], p.get("stat", "sight")
        n = p.get("n", len(P2.UNITS))                   # a bank of n units: the life's own draw from the 40
        rng = np.random.default_rng(seed + 77_000_011)
        self.allowed = set(int(u) for u in rng.permutation(len(P2.UNITS))[:n])
        self.order = [u for u in self.order if u in self.allowed]
        self.stretch = None                             # (unit, r0, r1, t0)
        self.stretches = {}                             # (unit, r0, r1) -> [(t0, t1)]
        self.est = None
        self.trials, self.trial_end, self.tally = None, None, {}
        self.practice = p.get("practice", False)
        self.untaste = p.get("untaste", False)          # forage, but play another round whenever QUIET s pass with no taste
        self.stop_play, self.tasted, self.forage_since = False, False, None
        self.bore = p.get("bore")
        self.playfor = p.get("playfor")                 # P1: play exactly this long, then forage
        self.handoff = p.get("handoff", False)          # the certainty hand-off at play's end, whoever chose the turns
        self.end_lN, self.play_beats = None, None
        self.w = p.get("w", (1.0, -1.0, 0.0))                      # None (learning progress), "stall" or "mover"
        self.hist, self.moved, self._last_fed, self.last_play = [], {}, False, {}
        self.cycle_rng = np.random.default_rng(seed + 88_000_013)
        self.win, self.prac, self.next_fit = None, {}, None

    def progress(self, u):
        return super().progress(u) if u in self.allowed else (-1e9, 1e-9)

    def _close(self):
        if self.stretch is not None:
            u, r0, r1, t0 = self.stretch
            if self.clock > t0:
                self.stretches.setdefault((u, r0, r1), []).append((t0, self.clock))
            self.stretch = None

    def set_balance(self, right):
        p = self.forager.p
        p["g0"], p["g1"] = math.exp(right / 2), math.exp(-right / 2)

    def finish_play(self):
        self._close()
        pulses = np.sort(np.array([t for t, _ in self.pulses], float))
        mixes = []
        for (u, r0, r1), st in self.stretches.items():
            if r0 == 0 and r1 == 0:
                continue
            if self.stat == "recur":
                T, s = recurrence(pulses, st)
                if s >= STRONG:
                    mixes.append((r0, r1, 1.0 / T, s))
            elif self.stat == "burst":
                bb = bursts(pulses, st)
                if bb is not None:
                    mixes.append((r0, r1) + bb)
            else:
                mixes.append((r0, r1) + sightings(pulses, st))
        self.mixes = mixes
        if self.stat == "beats" and (self.bore in ("certain", "certainmover") or self.handoff):
            lN = beat_runs(sorted(self.beat_log), pulses)
            self.end_lN, self.play_beats = lN, len(self.beat_log)
            if None in lN:
                return
            opts = [[b] if mg >= SURE else [b, r] for b, r, mg in lN]     # a motor in doubt hands its rival to taste
            cands = [a0 - a1 for a0 in opts[0] for a1 in opts[1]]
            self.est = cands[0]
            self.set_balance(cands[0])
            if len(cands) > 1:
                self.trials, self.trial_end = cands, None
            return
        if self.stat == "beats" and self.link == "readw":
            lN = beat_runs(sorted(self.beat_log), pulses)       # P2, route B: a readout learned across lives (evolution's), frozen
            self.end_lN = lN
            if None in lN:
                return
            w0, w1, c = self.w
            self.est = w0 * lN[0][0] + w1 * lN[1][0] + c
            self.set_balance(self.est)
            return
        if self.stat == "beats" and self.link == "readout":
            lN = beat_runs(sorted(self.beat_log), pulses)       # P2, route A: taste discovers how to use play's records
            self.end_lN = lN
            if None in lN:
                return
            b0, b1 = lN[0][0], lN[1][0]
            self.readouts = [(x, y) for x in (-1, 0, 1) for y in (-1, 0, 1)]      # every signed combination of the two measures
            self.trials = [x * b0 + y * b1 for x, y in self.readouts]
            self.slot = RSLOT
            self.est = self.trials[0]
            self.set_balance(self.trials[0])
            self.trial_end = None
            return
        if self.stat == "beats" and self.link == "partnersalt":
            lN = beat_runs(sorted(self.beat_log), pulses)
            if None in lN:
                return
            (a0, r0_, _), (a1, r1_, _) = lN
            self.trials = [a0 - a1, r0_ - a1, a0 - r1_]          # play's best, and each motor's rival: taste picks
            self.est = self.trials[0]
            self.set_balance(self.trials[0])
            self.trial_end = None
            return
        if self.stat == "beats" and self.link in ("partners", "partnerstaste"):
            lN = beat_runs(sorted(self.beat_log), pulses)
            self.end_lN = lN
            est = lN[0][0] - lN[1][0] if None not in lN else None     # k goes as 1 / beats a revolution; equal effect: log(k1 / k0)
            self.est = est
            if est is not None and self.link == "partners":
                self.set_balance(est)
            if self.link == "partnerstaste":
                c = est if est is not None else 0.0
                self.trials = [c - 0.3, c, c + 0.3] * 2
                self.set_balance(self.trials[0])
                self.trial_end = None
            return
        fits = {"recur": {"steady": fit_steady, "steadytaste": fit_steady, "partners": partners},
                "sight": {"steady": fit_steady_c, "steadytaste": fit_steady_c, "partners": partners_c},
                "burst": {"steady": fit_steady_c, "steadytaste": fit_steady_c, "partners": partners_c}}[self.stat]
        est = fits.get(self.link, lambda m: None)(mixes)
        self.est = est
        if self.link in ("steady", "partners") and est is not None:
            self.set_balance(est)
        if self.link == "taste":
            self.trials = list(GRID) * 2
        if self.link == "steadytaste":
            c = est if est is not None else 0.0
            self.trials = [c - 0.3, c, c + 0.3] * 2
        if self.trials:
            self.set_balance(self.trials[0])
            self.trial_end = None                       # a trial's clock starts at the first taste (nothing to judge before)

    def _fed(self, minrun=24):
        """Whether the turn just ended held a run of at least minrun beats of one motor alone."""
        beats = [m for t, m in self.beat_log[self._turn_beats:]] if hasattr(self, "_turn_beats") else []
        self._turn_beats = len(self.beat_log)
        run, last = 0, None
        for m in beats:
            run = run + 1 if m == last else 1
            last = m
            if run >= minrun:
                return True
        return False

    def margins(self):
        """Each motor's margin (best period over its rival), or None until both motors have a record."""
        pulses = np.sort(np.array([t for t, _ in self.pulses], float))
        lN = beat_runs(sorted(self.beat_log), pulses)
        self._lN = lN
        return None if None in lN else (lN[0][2], lN[1][2])

    def estimate(self):
        pulses = np.sort(np.array([t for t, _ in self.pulses], float))
        lN = beat_runs(sorted(self.beat_log), pulses)
        return None if None in lN else lN[0][0] - lN[1][0]

    def choose(self):
        if self.playfor and self.clock >= self.playfor:  # P1: every arm plays exactly playfor s
            if self.cur is not None:
                for pr in self.pred[self.cur]:
                    pr.turn_over()
            return None
        if not self.bore:
            u = super().choose()
            if u is None and self.playfor:              # learning progress has nothing to say: the least recently played unit
                u = min(self.allowed, key=lambda v: self.last_play.get(v, -1.0))
                self.mark = [len(pr.loss) for pr in self.pred[u]]
            if u is not None:
                self.last_play[u] = self.clock
            return u
        if self.cur is not None:                        # file the turn just ended, and how far it moved the estimate
            for pr in self.pred[self.cur]:
                pr.turn_over()
            fed = self._last_fed = self._fed()        # did this turn add a run to either motor's record?
            if fed and self.bore in ("certain", "certainmover"):
                m = self.margins()
                now = min(m) if m is not None else -np.inf
                prev = self.hist[-1] if self.hist else -np.inf
                self.moved[self.cur] = np.inf if not np.isfinite(prev) and np.isfinite(now) else max(0.0, now - prev) if np.isfinite(now) else 0.0
                self.hist.append(now)
            elif fed:
                e = self.estimate()
                prev = self.hist[-1] if self.hist else None
                self.moved[self.cur] = np.inf if (e is not None and prev is None) else (0.0 if e is None else abs(e - prev))
                if e is not None:
                    self.hist.append(e)             # only evidence counts: a turn that added nothing says nothing of stalling
                self.lp_log.append((self.clock, e))
            else:
                self.moved[self.cur] = 0.0
        if self.playfor:
            pass                                        # P1: no early end
        elif self.bore in ("certain", "certainmover"):
            m = self.margins()
            if m is not None and min(m) >= SURE:
                return None                             # bored: play's best guesses clearly beat their rivals
        else:
            h = self.hist[-STALL_N:]
            if len(h) == STALL_N and max(h) - min(h) < STALL:
                return None                             # bored: the estimate has stopped moving
        if self.order:
            u = self.order.pop(0)
        elif self.bore in ("stall", "certain"):        # every unit in turn, a fresh shuffle each cycle
            self.order = [v for v in self.cycle_rng.permutation(len(P2.UNITS)) if v in self.allowed]
            u = self.order.pop(0)
        else:                                           # mover: the unit whose last turn moved the estimate (or the certainty) most
            u = max(self.allowed, key=lambda v: (self.moved.get(v, np.inf), -self.last_play.get(v, -1.0)))   # ties: the least recent
        self.last_play[u] = self.clock
        self.mark = [len(pr.loss) for pr in self.pred[u]]
        return u

    def taste(self, value, at):
        if value != 0:
            self.tasted = True
            if self.playing and self.bore:
                self.stop_play = True
            if self.playing and self.untaste:
                self.stop_play = True                   # the world has begun to matter
        super().taste(value, at)
        if not self.playing and self.trials and self.trial_end is None and value != 0:
            self.trial_end = self.clock + getattr(self, "slot", SLOT)
        if not self.playing and self.trials:
            k = self.trials[0]
            self.tally[k] = self.tally.get(k, 0.0) + (1.0 if value > 0 else -2.0 if value < 0 else 0.0)

    def _practise(self):
        """After play: each WIN s window in which the forager scanned or ran throughout (open loop; chasing a block holds the view
        still by itself, and would only confirm the knob) is a stretch of the mix its beats made; refit the steady model on play's and
        practice's mixes every REFIT s and set the knob."""
        f = self.forager
        mode = "drive" if f.t - f.last_drive < f.p["hold"] else ("run" if f.t - f.last_food > f.p["bored"] else "scan")
        if self.win is None:
            self.win = [self.clock, mode != "drive", len(self.beat_log)]
        elif mode == "drive":
            self.win[1] = False
        if self.clock - self.win[0] >= WIN:
            t0, ok, i0 = self.win
            if ok:
                b = [m for _, m in self.beat_log[i0:]]
                key = (round(b.count(0) / WIN / 2) * 2, round(b.count(1) / WIN / 2) * 2)
                if key != (0, 0):
                    self.prac.setdefault(key, []).append((t0, self.clock))
            self.win = None
        if self.clock >= self.next_fit:
            self.next_fit = self.clock + REFIT
            pulses = np.sort(np.array([t for t, _ in self.pulses], float))
            mixes = list(self.mixes) + [k + sightings(pulses, st) for k, st in self.prac.items()]
            est = fit_steady_c(mixes)
            if est is not None:
                self.est = est
                self.set_balance(est)

    def step(self):
        if self.playing and self.stop_play:
            self._close()
            self.playing, self.play_end = False, self.clock
            self.finish_play()
            self.next_fit = self.clock + REFIT
            self.forage_since = self.clock
        was = self.playing
        if self.playing and self.clock >= self.turn_end:
            self._close()
        out = super().step()
        if was and not self.playing:
            self.finish_play()
            self.next_fit = self.clock + REFIT
            self.forage_since = self.clock
        elif not self.playing and self.untaste and not self.tasted and self.clock - self.forage_since >= QUIET:
            self.playing, self.cur, self.turn_end = True, None, self.clock     # nothing tasted yet: another round of play
            self.order = [u for u in np.random.default_rng(int(self.clock * 1000)).permutation(len(P2.UNITS)) if u in self.allowed]
        elif not self.playing and self.practice:
            self._practise()
        elif self.playing:
            r = self.fns[self.cur](self.clock, self.phase[self.cur])
            key = (self.cur, round(r[0], 6), round(r[1], 6))
            if self.stretch is None or self.stretch[:3] != key:
                self._close()
                self.stretch = key + (self.clock,)
        elif self.trials and self.trial_end is not None and self.clock >= self.trial_end:
            self.trials.pop(0)
            if self.trials:
                self.set_balance(self.trials[0])
                self.trial_end = self.clock + getattr(self, "slot", SLOT)
            else:
                best = max(self.tally, key=self.tally.get)
                self.est = best
                self.set_balance(best)
        return out


def make(arm, seed, first):
    from stage2_lang import arms as S
    from stage2_lang.sim import WLife
    from stage2_lang.seconds import seconds_cls
    import table as T
    w = S.world_of(WORLD)
    if arm in ("forage", "told"):
        q = T.numbers(seed, {"sync": 1})
        lf = WLife(seed, first, (lambda s: seconds_cls(T.Circuit)(s, q)), w, seconds=True)
        if arm == "told":
            k = {lf.wire_m[th]: g for th, g in ((0, lf.v_a), (1, lf.v_b))}
            right = math.log(k[1] / k[0])
            from stage2_lang import sim
            if sim.WLife.muscle:                        # thrust isn't proportional to rate on the muscle-like body
                import sigmoid_body as SB
                right = SB.told_balance(k[0], k[1], lf.brain.p["drive"])
            lf.brain.p["g0"], lf.brain.p["g1"] = math.exp(right / 2), math.exp(-right / 2)
        return lf
    parts = arm.split(":")                              # e.g. steady:recur:n10:t10
    p = {"dt": WLife.dt, "link": parts[0], "stat": "sight"}
    for x in parts[1:]:
        if x in ("recur", "sight", "burst", "beats"):
            p["stat"] = x
        elif x[0] == "n":
            p["n"] = int(x[1:])
        elif x[0] == "t":
            p["turn"] = float(x[1:])
        elif x == "practice":
            p["practice"] = True
        elif x == "untaste":
            p["untaste"] = True
        elif x in ("stall", "mover", "certain", "certainmover"):
            p["bore"] = x
        elif x.startswith("w="):                        # readw's weights: w=w0/w1/c
            p["w"] = tuple(float(v) for v in x[2:].split("/"))
        elif x.startswith("for"):
            p["playfor"] = float(x[3:])
        elif x == "handoff":
            p["handoff"] = True
    return WLife(seed, first, (lambda s: Play3(s, p)), w, seconds=True)


def job(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    arm, seed, first = j
    lf = make(arm, seed, first)
    k = {lf.wire_m[th]: g for th, g in ((0, lf.v_a), (1, lf.v_b))}
    l = S.live(lf, SECS)
    g = [a - COST * b for a, b, _ in l]
    sp = spent(l)
    b = lf.brain
    return dict(arm=arm, seed=seed, g3=g[2], sp3=sp * l[2][2] / sum(t for _, _, t in l), right=__import__('sigmoid_body').right_knob(k[0], k[1], __import__('table').numbers(seed, {})['drive']),
                est=getattr(b, "est", None), play_end=getattr(b, "play_end", None), nmix=len(getattr(b, "mixes", []) or []))


def report(rows, arms):
    I = R.boot(len(rows) // (2 * len(arms)))
    eff = {}
    print(f"{'arm':12s} | last third [95%] | vs forage, paired [95%] | knob error: median |est - right|, share within .2 | mixes counted")
    for a in arms:
        rs = [r for r in rows if r["arm"] == a]
        g, sp = np.array([r["g3"] for r in rs]), np.array([r["sp3"] for r in rs])
        eff[a] = (g, sp)
        b = g[I].sum(1) / sp[I].sum(1)
        line = f"{a:12s} | {g.sum() / sp.sum():+.2f} [{np.percentile(b, 2.5):+.2f},{np.percentile(b, 97.5):+.2f}]"
        if a != "forage" and "forage" in eff:
            g0, s0 = eff["forage"]
            d = b - g0[I].sum(1) / s0[I].sum(1)
            line += f" | {g.sum() / sp.sum() - g0.sum() / s0.sum():+.2f} [{np.percentile(d, 2.5):+.2f},{np.percentile(d, 97.5):+.2f}]"
        else:
            line += " |"
        e = [abs(r["est"] - r["right"]) for r in rs if r["est"] is not None]
        if e:
            line += f" | {np.median(e):.2f}, {np.mean(np.array(e) < .2):.0%} (of {len(e)})"
        else:
            line += " |"
        nm = [r["nmix"] for r in rs if r["play_end"] is not None]
        if nm:
            line += f" | {np.median(nm):.0f}"
        print(line, flush=True)


ARMS = ("forage", "told", "play", "steady", "partners", "taste", "steadytaste")

if __name__ == "__main__":
    a = sys.argv[1:]
    n = int(a[0]) if a else 20
    arms = a[1].split(",") if len(a) > 1 and a[1] != "report" else ARMS
    out = f"/home/pilgrim/git/simple-learner/lab/v/play3_{n}.pkl"
    out = out.replace(".pkl", "_muscle.pkl") if __import__("os").environ.get("MUSCLE") == "1" else out   # (the new body's lives apart)
    if "report" in a:
        report(pickle.load(open(out, "rb")), arms)
        sys.exit()
    import ledger
    ledger.start()
    jobs = [(arm, s, c) for arm in arms for s in range(SEEDS0, SEEDS0 + n) for c in ("red", "blue")]
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        rows = list(ex.map(job, jobs, chunksize=2))
    pickle.dump(rows, open(out, "wb"))
    report(rows, arms)

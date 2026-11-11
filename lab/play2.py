"""play2.py: the playing brain, step A (PROGRAMME.md, The next phase; the user, 2026-11-10: play is an investment, so a life of play first,
the challenge later). A bank of rhythm units plays in turns, each turn going to the unit whose predictions are improving fastest
(learning progress: Oudeyer and Kaplan 2007); play ends by itself when no unit's predictions are improving beyond their noise; then the
starting brain forages. No knob is set yet: this step asks only what learning progress chooses, and how long play lasts.

The units: lab/play1.py's 40, drawn once at random (evolution's draw, the same in every life), each with its own phase each life. So
each unit's ruler (bits it tells about the balance and the stride, play1.log) is known, and what play chooses can be read against it.

Each unit's predictor (generic, D38's record clocked by its own beats, D43): for each motor it drives, a cell a beat (did an eye pulse
since that motor's last beat?), and for each look-back k up to 64, counts of the cell given the cell k beats back. It predicts each new
cell from the look-back that tells most so far, and pays the log loss (bits) of that prediction before learning from it. Its learning
progress, in bits a second of play: its mean loss a cell in its turn before last, less that in its last turn, times its cells a second;
its noise, the standard error of that difference, likewise scaled. The turn goes to the unit with the most progress; a unit not yet
played twice counts as most promising (curiosity). Untried units are tried first (each once, in a random order: the life's own draw). A turn lasts TURN s.
Play ends when every unit's progress is within NOISE standard errors of nothing, or never improving.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 BELIEF=... PREDICT=... .venv/bin/python lab/play2.py [BODIES]"""
import math
import pickle
import re
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np

import dance0 as D0
import play1 as P1
import stage3_random as R

SEEDS0 = 90000                                  # development seeds, fresh
SECS = 900.0                                    # a life: play as long as it lasts, then forage; judged on the last third
UNITS = [P1.draw_unit(i) for i in range(40)]
K = 64                                          # look-backs, in the unit's own beats
TURN = 3.0                                      # s: a turn of play
NOISE = 2.0                                     # standard errors: progress within this of nothing is no progress


class Predictor:
    """One motor's record, clocked by its beats while its unit plays."""

    def __init__(self):
        self.n = np.zeros((K, 2, 2))                    # n[k, past, now]
        self.hist = []
        self.loss = []

    def cell(self, c):
        h = self.hist
        if len(h) >= 1:
            past = np.array([h[-k] if k <= len(h) else -1 for k in range(1, K + 1)])
            ok = past >= 0
            # the look-back that tells most so far (mutual information of the counts)
            N = self.n + 0.5
            Pj = N / N.sum((1, 2), keepdims=True)
            mi = (Pj * np.log2(Pj / Pj.sum(2, keepdims=True) / Pj.sum(1, keepdims=True))).sum((1, 2))
            mi[~ok] = -1
            k = int(np.argmax(mi))
            p1 = N[k, past[k], 1] / N[k, past[k]].sum()
            self.loss.append(-math.log2(p1 if c else 1 - p1))
            for j in np.nonzero(ok)[0]:
                self.n[j, past[j], c] += 1
        h.append(c)

    def turn_over(self):
        self.hist = []                                  # turns aren't contiguous: look-backs never span two turns


class PlayBrain:
    """The bank plays, then hands over to the starting brain (D20's sync'd drive, lab/table.py's numbers)."""

    def __init__(self, seed, p):
        from stage2_lang.seconds import seconds_cls
        import table as T
        rng = np.random.default_rng(seed + 66_000_007)
        self.dt = p["dt"]
        self.turn = p.get("turn", TURN)
        self.forager = seconds_cls(T.Circuit)(seed, T.numbers(seed, {"sync": 1}))
        self.fns = [P1.unit_fn(u) for u in UNITS]
        self.phase = rng.random(len(UNITS))
        self.order = list(rng.permutation(len(UNITS)))  # untried units, in the life's own order
        self.pred = [[Predictor(), Predictor()] for _ in UNITS]
        self.turns = [[] for _ in UNITS]
        self.mark = [0, 0]
        self.cur, self.turn_end = None, 0.0
        self.osc = rng.random(2)
        self.clock, self.t = 0.0, 0.0
        self.playing, self.play_end = True, None
        self.played = np.zeros(len(UNITS))
        self.flag = [0, 0]
        self.pulses, self.beat_log, self.beats = [], [], []
        self.lp_log = []

    def stimulate(self, sensor, at):
        self.pulses.append((self.clock + at, sensor))
        if self.playing:
            self.flag = [1, 1]
        else:
            self.forager.stimulate(sensor, at)

    def taste(self, value, at):
        if not self.playing:
            self.forager.taste(value, at)

    def progress(self, u):
        """(learning progress, its standard error) of unit u in bits a second of play: its mean loss a cell in its turn before last, less
        that in its last turn, times its cells a second in the last turn. None until it has had two turns."""
        T = self.turns[u]
        if len(T) < 2:
            return None
        a, b = T[-2], T[-1]
        if len(a) < 3 or len(b) < 3:                    # too few beats to predict anything: nothing to gain here
            return (0.0, 1e-9)
        rate = len(b) / self.turn
        return ((a.mean() - b.mean()) * rate, math.sqrt(a.var() / len(a) + b.var() / len(b)) * rate + 1e-9)

    def choose(self):
        if self.cur is not None:                        # file the turn just ended
            got = []
            for i, pr in enumerate(self.pred[self.cur]):
                got += pr.loss[self.mark[i]:]
                pr.turn_over()
            self.turns[self.cur].append(np.array(got))
        if self.order:
            u = self.order.pop(0)
        else:
            g = [self.progress(u) for u in range(len(UNITS))]
            lp = np.array([np.inf if x is None else x[0] for x in g])
            self.lp_log.append((self.clock, float(lp.max())))
            if all(x is not None and x[0] < NOISE * x[1] for x in g):
                return None                             # no unit is improving beyond its noise: play is over
            u = int(np.argmax(lp))
        self.mark = [len(pr.loss) for pr in self.pred[u]]
        return u

    def step(self):
        if self.playing and self.clock >= self.turn_end:
            u = self.choose()
            if u is None:
                self.playing, self.play_end = False, self.clock
            else:
                self.cur, self.turn_end = u, self.clock + self.turn
        if not self.playing:
            out = self.forager.step()
            self.beats = list(getattr(self.forager, "beats", None) or [])
            for m, at in self.beats:
                self.beat_log.append((self.clock + at, m))
            self.clock += self.dt
            self.t = self.clock
            return out
        r = self.fns[self.cur](self.clock, self.phase[self.cur])
        out, self.beats = [], []
        for m in (0, 1):
            if r[m] <= 0:
                continue
            a = self.osc[m]
            b = a + r[m] * self.dt
            for k in range(int(math.floor(a)) + 1, int(math.floor(b)) + 1):
                at = (k - a) / r[m]
                out.append(m)
                self.beats.append((m, at))
                self.beat_log.append((self.clock + at, m))
                self.pred[self.cur][m].cell(self.flag[m])
                self.flag[m] = 0
            self.osc[m] = b - math.floor(b)
        self.played[self.cur] += self.dt
        self.clock += self.dt
        self.t = self.clock
        return out


def job(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    from stage2_lang.sim import WLife
    arm, seed, first = j
    w = S.world_of(D0.WORLD)
    if arm == "play":
        lf = WLife(seed, first, (lambda s: PlayBrain(s, {"dt": WLife.dt})), w, seconds=True)
    else:
        lf = S.make(w, "circuit", seed, first)
    l = S.live(lf, SECS)
    g = [a - COST * b for a, b, _ in l]
    sp = spent(l)
    b = lf.brain
    return dict(arm=arm, seed=seed, gain=sum(g), spent=sp, g3=g[2], sp3=sp * l[2][2] / sum(t for _, _, t in l),
                play_end=getattr(b, "play_end", None), played=getattr(b, "played", None), lp_log=getattr(b, "lp_log", None))


def rulers():
    """Each unit's ruler from play1.log: bits about the balance (or its size, the better) plus the stride."""
    out = {}
    for line in open("/home/pilgrim/git/simple-learner/lab/v/play1.log"):
        m = re.match(r"^u(\d+) .*\|\s*([\d.]+)\s+([\d.]+)\s*\|\s*([\d.]+), ([\d.]+), ([\d.]+) \|", line)
        if m:
            out[int(m[1])] = max(float(m[4]), float(m[5])) + float(m[6])
    return np.array([out[i] for i in range(len(UNITS))])


def report(rows):
    I = R.boot(len(rows) // 4)
    by = {a: [r for r in rows if r["arm"] == a] for a in ("forage", "play")}
    for a, rs in by.items():
        g, sp = np.array([r["g3"] for r in rs]), np.array([r["sp3"] for r in rs])
        b = g[I].sum(1) / sp[I].sum(1)
        print(f"{a:7s} last third: efficiency {g.sum() / sp.sum():+.2f} [{np.percentile(b, 2.5):+.2f},{np.percentile(b, 97.5):+.2f}]")
    rs = by["play"]
    ends = np.array([r["play_end"] if r["play_end"] is not None else np.inf for r in rs])
    print(f"play ended by itself in {np.isfinite(ends).mean():.0%} of lives; when: median {np.median(ends):.0f} s, "
          f"quartiles {np.percentile(ends, 25):.0f}, {np.percentile(ends, 75):.0f} s")
    rul = rulers()
    T = np.array([r["played"] for r in rs]).mean(0)
    beyond = np.array([r["played"] for r in rs]).sum(0) - TURN * len(rs)    # play beyond each unit's first trial
    rk = lambda v: np.argsort(np.argsort(v))
    print(f"play time beyond the first trial against the unit's ruler: rank correlation {np.corrcoef(rk(beyond), rk(rul))[0, 1]:+.2f}")
    print(f"ruler bits per second of play: as played {float((T * rul).sum() / T.sum()):.2f}; every unit alike {rul.mean():.2f}")
    top = np.argsort(-T)[:8]
    print("most played: " + ", ".join(f"u{u} {T[u]:.0f} s (ruler {rul[u]:.2f})" for u in top))


if __name__ == "__main__":
    a = sys.argv[1:]
    n = int(a[0]) if a else 20
    out = f"/home/pilgrim/git/simple-learner/lab/v/play2_{n}.pkl"
    if len(a) > 1 and a[1] == "report":
        report(pickle.load(open(out, "rb")))
        sys.exit()
    import ledger
    ledger.start()
    jobs = [(arm, s, c) for arm in ("forage", "play") for s in range(SEEDS0, SEEDS0 + n) for c in ("red", "blue")]
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        rows = list(ex.map(job, jobs))
    pickle.dump(rows, open(out, "wb"))
    report(rows)

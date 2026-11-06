"""bits_bank.py: stage 1b's lives (PROGRAMME.md): the bank of predictors (lab/universal_v.py, setting lab/v/universal_v7.json) with every taste recorded, and
the arms that replace its selection step. Nothing here feeds back except where an arm says so: recording only watches. lab/universal_v.py is untouched.

A row of the record, one per taste pulse: t, value, vouched, scored (the bank scored it: vouched, not in the open phase, not a soon taste while pausing), open, followed
(the sensor the bit said was food), eaten (the sensor whose colour was eaten, -1 if two colours at once), F (the sensor the world's rule says is food now, -1 if none), kind (followed
eye pulsed within 0.3 s, other eye likewise: 2 bits), gap, act (after), preds (each model's prediction before the taste, one bit each).

Arms:  v       the bank, as it is
       map     MAP over the seven models, fixed lie rate: follow argmax of k*[model is default] + hits. (LLR between models is (h_i - h_j) log2((1-e)/e), so a stated prior and e
               only set k = log2(prior odds)/log2((1-e)/e).)
       bma     the posterior-weighted vote of the seven, stated e and prior pr (the default's prior; the rest shared equally)
       fix     one model followed from birth (fix=index): the true ceiling of selection among seven: no selector with this stream can beat the best model in hindsight
       ctr     the bank's counter with its parts varied: ctr_up, pen, floor (0, or None for no floor), top; the decision as the bank's
       vtold   the bank's body and parts (eyes, jitter, pause), its colour told at every moment; wrong=1 told backwards. open=0. What selection and the models could at best become.

    .venv/bin/python lab/bits_bank.py check            # my life loop against table.life, lives identical
    .venv/bin/python lab/bits_bank.py record SEEDS OUT [k=v ...]"""
import json
import os
import pickle
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from creature import Life
from minimal.spec import SPAN, Lived, thirds, efficiency
import table as T
import universal as X
import universal_v as UV

V7 = json.load(open("/home/pilgrim/git/simple-learner/lab/v/universal_v7.json"))
WORLDS9 = ["plain", "swap10", "alternate", "pattern", "digest", "unreliable", "patchy", "weak", "noisy"]
WORKERS = 6                                             # leaves the machine usable
COLS = ("t", "value", "vouched", "scored", "open", "followed", "eaten", "F", "kind", "gap", "act", "preds", "bad")


class Recorder(UV.V):
    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.rows = []
        self.spy = None

    def about(self, value):
        """What the bank's own taste would do with this taste, before it does: (scored, truth)."""
        p = self.p
        gap = self.t - self.ate_at
        est = self.est
        if not self.open and self.vouched() and p.get("pausek", 1) and gap < max(p.get("win_p", 1.2), est * p.get("stair", 0.0) if self.pausing else 0.0):    # V moves est before it decides
            if value < 0:
                est = est * (1 + p.get("up", 0.1)) if self.pausing and p.get("stair", 0.0) else max(est, gap * p.get("margin_p", 1.2))
            elif self.pausing:
                est *= p.get("shrink", 0.98)
        scored = not self.open and self.vouched() and not (self.pausing and gap < (est if p.get("stair", 0.0) else p.get("win_p", 1.2)))
        return scored, (self.food if value > 0 else 1 - self.food), gap

    def taste(self, value, at):
        scored, _, gap = self.about(value)
        vouched, opened, followed = self.vouched(), self.open, self.food
        preds = sum(self.pred(m) << i for i, m in enumerate(self.bank))
        k = self.kind(value)
        eaten, F, bad = self.spy() if self.spy else (-1, -1, 0)
        super().taste(value, at)
        self.rows.append((self.t, value, vouched, scored, opened, followed, eaten, F, k[1] * 2 + k[2], gap, self.act, preds, bad))


class Map(Recorder):
    """The exact posterior's MAP, all else the bank's."""

    def __init__(self, seed, p):
        super().__init__(seed, dict(p, bankk=0))
        self.le = [float(p.get("k", 1.5))] + [0.0] * (len(self.bank) - 1)

    def score(self, value):
        scored, truth, _ = self.about(value)
        if scored:
            for i, m in enumerate(self.bank):
                self.le[i] += float(self.pred(m) == truth)

    def taste(self, value, at):
        self.score(value)
        super().taste(value, at)

    def choose(self):
        best = int(np.argmax(self.le))                  # ties to the lowest index: the default first
        if best != self.act:
            self.act = best
            self.picks.append((self.t, best))
            if self.bank[best]["n"] > 1:
                self.grew.append((self.t, self.bank[best]["n"]))


class Bma(Map):
    """The posterior-weighted vote: Bayes-optimal one-taste-ahead under the stated e and prior."""

    def __init__(self, seed, p):
        super().__init__(seed, p)
        e, pr, n = p.get("eps", 0.1), p.get("pr", 0.5), len(self.bank)
        self.L = np.log2((1 - e) / e)
        self.le = [np.log2(pr)] + [np.log2((1 - pr) / (n - 1))] * (n - 1)

    def score(self, value):
        scored, truth, _ = self.about(value)
        if scored:
            for i, m in enumerate(self.bank):
                self.le[i] += self.L * float(self.pred(m) == truth)

    def taste(self, value, at):
        super().taste(value, at)
        if not self.open:
            w = np.exp2(np.array(self.le) - max(self.le))
            vote = sum(wi * self.pred(m) for wi, m in zip(w, self.bank)) / w.sum()
            self.food = int(vote > 0.5)


class Fix(Recorder):
    """One model from birth: no selection at all, the evidence it would have needed free."""

    def __init__(self, seed, p):
        super().__init__(seed, dict(p, bankk=0))
        self.act = int(p.get("fix", 0))

    def choose(self):
        pass


class Ctr(Recorder):
    """The bank's counters with their parts varied, for what each part costs."""

    def __init__(self, seed, p):
        super().__init__(seed, dict(p, bankk=0))

    def taste(self, value, at):
        scored, truth, _ = self.about(value)
        if scored:
            p = self.p
            floor, top = p.get("floor", 0.0), p.get("Emax", 10.0)
            floor = -1e9 if floor is None else floor
            base_hit = self.pred(self.bank[0]) == truth
            for m in self.bank[1:]:
                hit = self.pred(m) == truth
                m["E"] = min(top, max(floor, m["E"] + (p.get("ctr_up", 1.0) if hit > base_hit else -p.get("pen", 3.0) if hit < base_hit else 0.0)))
        super().taste(value, at)


class VTold(Recorder):
    """The bank's parts, told the colour. Told from outside at every tick: an arm for a ceiling, never a brain."""

    told_food = None

    def __init__(self, seed, p):
        super().__init__(seed, dict(p, bankk=0, open=0))

    def choose(self):
        pass

    def taste(self, value, at):
        super().taste(value, at)
        if self.told_food is not None:
            self.food = self.told_food


T.ARMS.update(v_rec=Recorder, map=Map, bma=Bma, fix=Fix, ctr=Ctr, vtold=VTold)


def life(job):
    """table.life's loop (bits_bank.py check shows the lives identical), with each taste recorded."""
    w, arm, kw, seed, seconds, first = job
    q = T.numbers(seed, {**V7, **kw})
    R = T.WORLDS[w](first)
    lf = Life(seed, first, brain=lambda s: T.ARMS[arm](s, q))
    b = lf.brain
    R.setup(lf, seed)
    tell = arm == "vtold"
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
    l.rows = np.array(b.rows, dtype=float) if b.rows else np.zeros((0, len(COLS)))
    l.picks = list(b.picks)
    l.on = list(b.on_at)
    l.seed, l.first, l.world = seed, first, w
    l.names = [f"{m['n']}/{m['trust']}" for m in b.bank]
    return l


def _nice():
    os.nice(10)


def run(w, arm, seeds, kw=None, seconds=100.0, workers=WORKERS):
    jobs = [(w, arm, kw or {}, s, seconds, c) for s in seeds for c in T.COL]
    with ProcessPoolExecutor(workers, initializer=_nice) as ex:
        return list(ex.map(life, jobs, chunksize=2))


def run_plain(w, arm, seeds, kw=None, seconds=100.0, workers=WORKERS):
    """Any of table.py's arms, by table.life itself."""
    jobs = [(w, arm, kw or {}, s, seconds, c) for s in seeds for c in T.COL]
    with ProcessPoolExecutor(workers, initializer=_nice) as ex:
        return list(ex.map(T.life, jobs, chunksize=2))


if __name__ == "__main__":
    cmd, *rest = sys.argv[1:]
    if cmd == "check":
        import time
        T.ARMS["v"] = UV.V
        for w in ("plain", "digest", "unreliable", "alternate"):
            t0 = time.time()
            a = run(w, "v_rec", range(60000, 60003))
            t1 = time.time()
            b = run_plain(w, "v", range(60000, 60003), V7)
            same = all(tuple(x) == tuple(y) for p, q in zip(a, b) for x, y in zip(p, q))
            print(w, "identical" if same else "DIFFERENT", f"{efficiency(a):.3f} {efficiency(b):.3f}, {(t1 - t0) / len(a):.2f} s of pool per life", flush=True)
    elif cmd == "record":
        lo, hi = (int(x) for x in rest[0].split(":"))
        kw = X.parse(rest[2:])
        out = {}
        for w in WORLDS9:
            out[w] = run(w, "v_rec", range(lo, hi), kw)
            print(w, f"{efficiency(out[w]):.3f}", flush=True)
        with open(rest[1], "wb") as f:
            pickle.dump({w: [dict(rows=l.rows.astype(np.float32), picks=l.picks, on=l.on, seed=l.seed, first=l.first, names=l.names, lived=list(l)) for l in L] for w, L in out.items()}, f)

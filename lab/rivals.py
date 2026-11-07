"""rivals.py: stage R (PROGRAMME.md), the bank's rivals made from simple parts rather than written. Main session, 2026-11-07.

Every rival in universal_v.V is a context and a table: a signal taking one of k values (there, the count of good tastes mod n) and a learned bit
for each value (which colour is food then) with a tally of trust. Here the table is the same, and the context is assembled from parts a circuit
can hold, each in seconds, never ticks:
  Const          k = 1 (story 1's circuit, the default)
  Count(n, src)  counts src's events mod n, an event of its own each time it wraps (Count(2) is a toggle; a chain of toggles a binary counter)
  Osc(T, bins)   a free-running oscillator of period T, read in phase bins, with phase noise; an event each cycle
  Timer(tau, src) whether src's last event was within tau
  Prod(a, b)     a conjunction: both contexts at once (k = ka x kb), how hierarchies form
Event sources are the tastes a brain already has: "good" (a good taste) and "taste" (any taste the bank scores), or another part's events.
A rival is scored exactly as V's (evidence where it disagrees with the default), on every taste, without ever being acted on.

RV copies V.taste with the count g replaced by the parts (marked below); everything else is V's, so the compiled step applies unchanged.

    .venv/bin/python lab/rivals.py identity     R1: the written bank rebuilt from parts, lives identical"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import numpy as np
import universal_v as UV


# ---------------------------------------------------------------- parts
class Part:
    k = 1
    def __init__(self):
        self.listeners = []

    def emit(self, t):
        for f in self.listeners:
            f(t)

    def advance(self, t):           # bring time-driven parts up to time t (seconds)
        pass

    def index(self, t):
        return 0

    def parts(self):
        return [self]


class Const(Part):
    def desc(self):
        return "1"


class Source(Part):
    """An event the brain already has: 'good' or 'taste'."""
    def __init__(self, name):
        super().__init__()
        self.name = name

    def desc(self):
        return self.name


class Count(Part):
    def __init__(self, n, src):
        super().__init__()
        self.k, self.n, self.c, self.src = n, n, 0, src
        src.listeners.append(self.on)

    def on(self, t):
        self.c = (self.c + 1) % self.n
        if self.c == 0:
            self.emit(t)

    def advance(self, t):
        self.src.advance(t)

    def index(self, t):
        return self.c

    def parts(self):
        return self.src.parts() + [self]

    def desc(self):
        return f"count{self.n}({self.src.desc()})"


class Osc(Part):
    """Period T (s), read in `bins` phase bins; phase noise: the phase wanders with variance noise^2 per cycle."""
    def __init__(self, T, bins, rng, phase=None, noise=0.02):
        super().__init__()
        self.k, self.T, self.bins, self.noise, self.rng = bins, T, bins, noise, rng
        self.ph = rng.random() if phase is None else phase
        self.t = 0.0

    def advance(self, t):
        dt = t - self.t
        if dt <= 0:
            return
        d = dt / self.T
        if self.noise:
            d += self.noise * np.sqrt(d) * self.rng.standard_normal()
        new = self.ph + d
        for _ in range(int(np.floor(new)) - int(np.floor(self.ph))):
            self.emit(t)
        self.ph, self.t = new, t

    def index(self, t):
        self.advance(t)
        return int((self.ph % 1.0) * self.bins) % self.bins

    def desc(self):
        return f"osc({self.T:.3g}s/{self.bins})"


class Timer(Part):
    def __init__(self, tau, src):
        super().__init__()
        self.k, self.tau, self.last, self.src = 2, tau, -1e9, src
        src.listeners.append(self.on)

    def on(self, t):
        self.last = t

    def advance(self, t):
        self.src.advance(t)

    def index(self, t):
        return int(t - self.last < self.tau)

    def parts(self):
        return self.src.parts() + [self]

    def desc(self):
        return f"within{self.tau:.3g}s({self.src.desc()})"


class Prod(Part):
    def __init__(self, a, b):
        super().__init__()
        self.a, self.b, self.k = a, b, a.k * b.k

    def advance(self, t):
        self.a.advance(t)
        self.b.advance(t)

    def index(self, t):
        return self.a.index(t) * self.b.k + self.b.index(t)

    def parts(self):
        return self.a.parts() + self.b.parts() + [self]

    def desc(self):
        return f"({self.a.desc()} x {self.b.desc()})"


def written(src_good):
    """V7's bank (BANKS[19]: n 1, 2, 3, 4, 5, 6) as parts: 4 a chain of two toggles, 6 a toggle and a 3-counter together."""
    g = src_good
    t1 = Count(2, g)
    return {1: Const(), 2: Count(2, g), 3: Count(3, g), 4: Prod(Count(2, t1), t1), 5: Count(5, g), 6: Prod(Count(2, g), Count(3, g))}


# ---------------------------------------------------------------- R2: rivals drawn at birth (rule fixed in lab/v/stageR_predictions.md)
def _logu(r, a, b):
    return float(np.exp(r.uniform(np.log(a), np.log(b))))


def base_part(r, src):
    kind = int(r.integers(3))
    s = src["good"] if r.random() < 0.5 else src["taste"]
    if kind == 0:
        return Count(int(r.integers(2, 17)), s)
    if kind == 1:
        return Osc(_logu(r, 1.0, 200.0), 2 if r.random() < 0.5 else 4, r)
    return Timer(_logu(r, 0.25, 10.0), s)


def draw_rival(r, src):
    a = base_part(r, src)
    if r.random() < 0.3:
        if r.random() < 0.5:
            a = Count(int(r.integers(2, 5)), a)          # a counter of a part's own events: a hierarchy
        else:
            a = Prod(a, base_part(r, src))              # a conjunction
    return a, int(r.integers(0, 4))


def random_rivals(K):
    return lambda r, src: [draw_rival(r, src) for _ in range(K)]


def occam(K):
    """The bar to adopt a rival and its cap, rising with log2 K as the Occam factor requires (a +1 about 1.7 bits, D31); K = 6 is V7's."""
    inc = (np.log2(max(K, 1)) - np.log2(6)) / 1.7
    return dict(theta=2.0 + inc, Emax=10.0 + inc)


# ---------------------------------------------------------------- the bank with made contexts
class RV(UV.V):
    """V with each model's context made of parts. Rivals: p['rivals'], a function (rng, sources) -> [(context, trust)]; default the
    written bank rebuilt from parts."""
    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.src = {"good": Source("good"), "taste": Source("taste")}
        self.rrng = np.random.default_rng([int(seed), 7])          # the rivals' own draws: never the body's or the brain's stream
        make = p.get("rivals")
        if isinstance(make, tuple) and make[0] == "random":
            make = random_rivals(int(make[1]))
        if make is None:
            ctx = written(self.src["good"])
            rivals = [(ctx[m["n"]], m["trust"]) for m in self.bank[1:]]
        else:
            rivals = make(self.rrng, self.src)
        self.bank = [dict(ctx=Const(), n=1, trust=int(p.get("d", 1)))] + [dict(ctx=c, n=c.k, trust=t) for c, t in rivals]
        for m in self.bank:
            m.update(bits=[self.food] * m["n"], tally=[0] * m["n"], E=0.0)

    def ix(self, m):
        m["ctx"].advance(self.t)
        return m["ctx"].index(self.t)

    def pred(self, m):
        return m["bits"][self.ix(m)]

    def taste(self, value, at):
        p = self.p
        gap = self.t - self.ate_at
        self.ate_at = self.t
        if value > 0:
            self.rate += 1.0
        if self.open:
            if value < 0:
                self.open = False
                self.food = 1 - self.recent
                for m in self.bank:
                    m["bits"] = [self.food] * m["n"]
            return
        soon = gap < max(p.get("win_p", 1.2), self.est * p.get("stair", 0.0) if self.pausing else 0.0)
        if self.vouched():
            if p.get("pausek", 1):
                if soon:
                    if value < 0:
                        self.P = min(p.get("mtop", 4.0), self.P + 1.0)
                        if self.pausing and p.get("stair", 0.0):
                            self.est *= 1 + p.get("up", 0.1)
                        else:
                            self.est = max(self.est, gap * p.get("margin_p", 1.2))
                    else:
                        self.P = max(0.0, self.P - p.get("down", 1.0))
                        if self.pausing:
                            self.est *= p.get("shrink", 0.98)
                elif value < 0:
                    self.P = max(0.0, self.P - p.get("late", 1.0))
            if not (self.pausing and gap < (self.est if p.get("stair", 0.0) else p.get("win_p", 1.2))):
                truth = self.food if value > 0 else 1 - self.food
                cs = [self.ix(m) for m in self.bank]                    # parts: the context, not g % n
                base_hit = self.bank[0]["bits"][cs[0]] == truth
                for i, m in enumerate(self.bank):
                    c = cs[i]
                    hit = m["bits"][c] == truth
                    if i and p.get("bankk", 1):
                        m["E"] = float(np.clip(m["E"] + (1.0 if hit > base_hit else -p.get("pen", 1.0) if hit < base_hit else 0.0), 0.0, p.get("Emax", 6.0)))
                    if hit:
                        m["tally"][c] = max(-m["trust"], m["tally"][c] - 1)
                    else:
                        m["tally"][c] += 1
                        if m["tally"][c] >= 1:
                            m["bits"][c], m["tally"][c] = 1 - m["bits"][c], 0
                            if i == self.act:
                                self.flips.append(self.t)
                self.src["taste"].emit(self.t)                                      # parts: a scored taste
        if value > 0:
            self.g += 1
            self.src["good"].emit(self.t)                                           # parts: a good taste, where V counts g
        self.choose()
        self.food = self.pred(self.bank[self.act])


# ---------------------------------------------------------------- lives
def make(world, seed, first, kw=None, cls=RV):
    """A life for RV in a world, as stage2_lang.arms.make builds the bank's (seconds mode, compiled step)."""
    import table as T
    from stage2_lang import arms as S, fast
    from stage2_lang.sim import WLife
    q = T.numbers(seed, {**S.V7, **(kw or {})})
    C = fast.fast_cls(cls) if WLife.seconds else cls
    return WLife(seed, first, (lambda s: C(s, q)), world, seconds=WLife.seconds)


def _identity_job(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    text, which, seed, first = j
    w = S.world_of(text)
    lf = S.make(w, "bank", seed, first) if which == "bank" else make(w, seed, first)
    l = S.live(lf, 100.0)
    return [(a, b, t) for a, b, t in l], spent(l), l.picks


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "identity":
        import stage3_random as R
        from concurrent.futures import ProcessPoolExecutor
        W, _, _ = R.worlds()
        names = ["plain", "g144", "g245", "g227", "g352", "g384", "g261", "g397"]
        seeds = range(81200, 81210)
        with ProcessPoolExecutor(int(sys.argv[2]) if len(sys.argv) > 2 else 1, initializer=R._init, initargs=(0.00125, False)) as ex:
            same = tot = 0
            for n in names:
                text = R.PLAIN if n == "plain" else W[n][0]
                jobs = [(text, w, s, c) for s in seeds for c in R.COL for w in ("bank", "rv")]
                out = list(ex.map(_identity_job, jobs))
                k = sum(out[i] == out[i + 1] for i in range(0, len(out), 2))
                same, tot = same + k, tot + len(out) // 2
                print(f"{n:6s} identical {k}/{len(out) // 2}", flush=True)
            print(f"all: {same}/{tot}")

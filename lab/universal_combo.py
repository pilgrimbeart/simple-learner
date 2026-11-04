"""universal_combo.py: pairs of mismatches never tuned together, the real test of universality (STORIES.md; discrete/NOTEBOOK.md, D29). A body flaw's setup and tick
with a rule flaw's poison, meals and taste. Registered in table.WORLDS as "thrusters+swap10" etc."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import table as T


def combo(a, b):
    A, B = T.WORLDS[a], T.WORLDS[b]

    class C:
        told = False

        def __init__(self, first):
            self.a, self.b = A(first), B(first)

        def setup(self, lf, seed):
            self.a.setup(lf, seed)
            self.b.setup(lf, seed)

        def tick(self, lf, t):
            self.a.tick(lf, t)
            self.b.tick(lf, t)

        def poison(self, t):
            return self.b.poison(t)

        def told_poison(self, t):
            return self.b.told_poison(t)

        def ate(self, c):
            self.b.ate(c)

        def __setattr__(self, k, v):
            object.__setattr__(self, k, v)
            if k == "now":
                self.a.now = v
                self.b.now = v

    if hasattr(B, "taste"):
        C.taste = lambda self, v: self.b.taste(v)
    if hasattr(B, "bad"):
        C.bad = lambda self, c, t: self.b.bad(c, t)
    T.WORLDS[f"{a}+{b}"] = C


PAIRS = [("thrusters", "swap10"), ("thrusters", "alternate"), ("thrusters", "digest"), ("noisy", "swap10"), ("noisy", "alternate"), ("noisy", "digest"), ("ageing", "unreliable"), ("weak", "pattern"), ("noisy", "thrusters"), ("thrusters", "unreliable")]
for a, b in PAIRS:
    combo(a, b)
    if a in T.LONG:
        T.LONG[f"{a}+{b}"] = T.LONG[a]


def digest_with(b):
    """Digest's clock on another rule's colours: a meal too soon is bad whatever its colour, and the colours follow the other rule."""
    D, B = T.WORLDS["digest"], T.WORLDS[b]

    class C:
        told = False

        def __init__(self, first):
            self.d, self.b = D(first), B(first)

        def setup(self, lf, seed):
            self.b.setup(lf, seed)

        def tick(self, lf, t):
            self.b.tick(lf, t)

        def poison(self, t):
            return self.b.poison(t)

        def told_poison(self, t):
            return self.b.told_poison(t)

        def ate(self, c):
            self.d.ate(c)
            self.b.ate(c)

        def taste(self, v):
            return self.d.taste(v)

        def bad(self, c, t):
            return c == self.b.poison(t) or t - self.d.was < self.d.W

        def __setattr__(self, k, v):
            object.__setattr__(self, k, v)
            if k == "now":
                self.d.now = v
                self.b.now = v

    T.WORLDS[f"digest+{b}"] = C


RULEPAIRS = ["alternate", "pattern", "swap10", "unreliable"]
for b in RULEPAIRS:
    digest_with(b)
ALL = [f"{a}+{b}" for a, b in PAIRS] + [f"digest+{b}" for b in RULEPAIRS]


if __name__ == "__main__":
    import json
    import numpy as np
    import universal as X
    import universal_v
    from table_rows import VALID
    from minimal.spec import efficiency
    v = json.load(open(sys.argv[1]))
    u = json.load(open(sys.argv[2]))
    seeds = list(VALID)
    for w in ALL:
        secs = T.LONG.get(w, 100.0)
        B = T.run(w, "circuit", seeds, seconds=secs)
        U, V = T.run(w, "u", seeds, u, secs), T.run(w, "v", seeds, v, secs)
        d, i = T.paired(V, B)
        d2, i2 = T.paired(V, U)
        print(f"{w} {secs:.0f} s: base {efficiency(B):.2f}, U {efficiency(U):.2f}, bank {efficiency(V):.2f}; bank-base {d:+.2f} [{i[0]:+.2f}, {i[1]:+.2f}]; bank-U {d2:+.2f} [{i2[0]:+.2f}, {i2[1]:+.2f}]; grew {np.mean([bool(l.grew) for l in V]):.2f} paused {np.mean([bool(l.on) for l in V]):.2f} |x| {np.mean([abs(l.x or 0) for l in V]):.2f}", flush=True)

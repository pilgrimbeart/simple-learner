"""ladders.py: stage 0's ruler (PROGRAMME.md; README, How we'll know). Main session, 2026-11-09. Three ladders on today's senses, each a world per rung in the
language, and the arms that certify a rung. Predictions: lab/v/ladders_predictions.md, written before any life.

Every word and table below is drawn per life from the world's own stream, so no design can hold the answer.
  seq n     the n-bit lesson: which colour is food follows a secret repeating word of n, moved on by each good meal; a colour out of turn is bad and leaves
            the turn where it is. n prime with its first two letters different, so the word's period is exactly n: rung 1 is plain, 2 is alternation.
  time n    the same word in time: which colour is food is the word's letter for this slot of TAU s, whatever the creature does, the slots' length (log-uniform 5 to 20 s) and phase drawn per life. Rung 2 is a regular swap.
  combo k   a meal's meaning depends on the last k colours eaten, good or bad: a secret table of 2^k letters says which colour is food after each history. Its two
            entries differing only in the oldest colour are forced different, so the table really does depend on all k.
Arms: base (the starting brain, table.Circuit), told (the bank's parts told the colour at every moment: can it be done with this body?), designed (below: is it
learnable from taste?), bank (today's best brain).

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/ladders.py certify LADDER [PAIRS] [DT_MS] [SIZES]   # a ladder's rungs
    ... lab/ladders.py baseline LADDER | cross"""
import json
import sys
import time
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import stage3_random as R

TAU = 10.0                                      # the designed clock's default, on worlds with no slots of their own
PLAIN = "(world)"
COL = ("red", "blue")
SEEDS0 = 83000                                  # development seeds (PROGRAMME.md, Sealed), fresh


def seq(n):
    if n == 1:
        return PLAIN
    return (f"(world (meta (link L7) (q D) (cap Ladder) (group seq)) (let i (int {n})) (table w {n} 1 (int 2)) (on birth (put w 0 0) (put w 1 1))"
            f" (on tick (set poison (if (= (at w i) 0) P F)))"
            f" (on score (if (= colour (if (= (at w i) 0) F P)) (set i (mod (+ i 1) {n})))))")


def timing(n):
    if n == 1:
        return PLAIN
    return (f"(world (meta (link L7) (q T) (cap Ladder) (group time)) (let tau (exp (uniform (log 5) (log 20)))) (let ph (uniform 0 tau)) (table w {n} 1 (int 2)) (on birth (put w 0 0) (put w 1 1))"
            f" (on tick (set poison (if (= (at w (mod (floor (/ (+ t ph) tau)) {n})) 0) P F))))")


def combo(k):
    if k == 0:
        return PLAIN
    m = 2 ** k
    return (f"(world (meta (link L7) (q D) (cap Ladder) (group combo)) (let h (int {m})) (table f {m} 1 (int 2)) (on birth (put f 0 0) (put f {m // 2} 1))"
            f" (on tick (set poison (if (= (at f h) 0) P F)))"
            f" (on score (set h (mod (+ (* 2 h) (if (= colour F) 0 1)) {m}))))")


# (size, seconds for each life): the sizes the ladder climbs; a rung's life is as long as it needs (AGENTS.md)
LADDERS = {
    "seq": dict(world=seq, rungs=[(1, 100), (2, 100), (3, 100), (5, 100), (7, 100), (11, 300), (13, 300), (17, 300)]),
    "time": dict(world=timing, rungs=[(1, 100), (2, 300), (3, 450), (4, 600), (5, 750), (6, 900), (7, 1050), (11, 1650), (13, 1950)]),
    "combo": dict(world=combo, rungs=[(0, 100), (1, 100), (2, 300), (3, 300), (4, 300), (5, 1000), (6, 1000)]),
}


def context_count(ladder, size):
    return 2 ** size if ladder == "combo" else size


def designed_cls():
    """A brain designed by hand for a rung, told the rung's structure (which ladder, its size, TAU), never its letters or phase: a table of one letter a context, each
    with one step of trust, as ladder.Cycle. It proves a rung can be learned from taste; it never counts as the solution (README)."""
    import table as T

    class Designed(T.Circuit):
        def __init__(self, seed, p):
            super().__init__(seed, p)
            self.lad, self.size = p["lad"], int(p["size"])
            n = context_count(self.lad, self.size)
            if self.lad == "time":                              # its own clock: told the period, never the phase; 5 bins a slot, so no lock is needed
                import rivals as RV
                self.clock = RV.Osc(TAU * max(n, 1), 5 * max(n, 1), np.random.default_rng([int(seed), 11]))
                n = 5 * max(n, 1)
            self.n, self.bits, self.tally, self.g, self.h = n, [self.food] * n, [0] * n, 0, 0

        def ctx(self):
            if self.lad == "seq":
                return self.g % self.n
            if self.lad == "time":
                return self.clock.index(self.t)
            return self.h

        def taste(self, value, at):
            v = self.vouched()
            c = self.ctx()
            eaten = self.food if v else int(self.last[1] > self.last[0])    # by its own eyes: what it was following if vouched, else the last eye to pulse
            if v:
                if value > 0:
                    self.tally[c] = max(-1, self.tally[c] - 1)
                else:
                    self.tally[c] += 1
                    if self.tally[c] >= 1:
                        self.bits[c], self.tally[c] = 1 - self.bits[c], 0
                        self.flips.append(self.t)
            if value > 0:
                self.g += 1
            if self.size and self.lad == "combo":
                self.h = (2 * self.h + eaten) % self.n
            self.food = self.bits[self.ctx()]
    return Designed


_D = {}


def make(world, arm, seed, first, kw):
    from stage2_lang import arms as S, fast
    from stage2_lang.sim import WLife
    import table as T
    if arm != "designed":
        return S.make(world, arm, seed, first)
    if "c" not in _D:
        _D["c"] = designed_cls()
    q = T.numbers(seed, kw)
    q.update(kw)
    if kw["lad"] != "time":
        C = fast.fast_cls(_D["c"])
        return WLife(seed, first, (lambda s: C(s, q)), world, seconds=True)
    from stage2_lang.seconds import seconds_cls             # its clock changes the colour between tastes, so not the compiled step
    C = seconds_cls(_D["c"])
    lf = WLife(seed, first, (lambda s: C(s, q)), world, seconds=True)

    def tell(W):                                            # told the slot's length (a yardstick's privilege), never its phase; its own clock, read once a tick
        if hasattr(W, "v_tau"):
            W.brain.clock.T = W.v_tau * max(W.brain.size, 1)
        W.brain.food = W.brain.bits[W.brain.ctx()]
    lf.tell = tell
    return lf


def job(j):
    """(text, arm, kw, seed, first, seconds) -> whole life's gain and spending, last third's, meals, cpu."""
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    text, arm, kw, seed, first, secs = j
    t0 = time.perf_counter()
    l = S.live(make(S.world_of(text), arm, seed, first, kw), secs)
    g = [a - COST * b for a, b, _ in l]
    meals = sum(a + b for a, b, _ in l)
    sp = spent(l)
    return (sum(g), sp, g[2], sp * l[2][2] / sum(t for _, _, t in l), meals, time.perf_counter() - t0)


def scored(L, secs, I):
    """Efficiency: over the whole of a 100 s life, over the last third of a longer one (AGENTS.md), and its bootstrap."""
    a, b = (0, 1) if secs <= 100 else (2, 3)
    g, s = np.array([x[a] for x in L], float), np.array([x[b] for x in L], float)
    return g.sum() / s.sum(), g[I].sum(1) / s[I].sum(1)


def certify(name, pairs=20, dt=2.5, only_secs=None, workers=7, seed0=SEEDS0, sizes=None):
    lad = LADDERS[name]
    I = R.boot(pairs)
    seeds = range(seed0, seed0 + pairs)
    out = {}
    print(f"== {name}: {pairs} pairs, {dt} ms, seeds {seed0}+; bar: gap >= .25 surely, designed closes half surely", flush=True)
    print(" size   secs |   base   told    gap [95%]      | designed x [95%]    | bank x [95%]        | tastes/s  bits needed/tastes | cpu/life | certified", flush=True)
    with ProcessPoolExecutor(workers, initializer=R._init, initargs=(dt / 1000, False)) as ex:
        for size, secs in lad["rungs"]:
            if sizes and size not in sizes:
                continue
            secs = only_secs or secs
            text = lad["world"](size)
            res = {}
            for arm, kw in (("circuit", {}), ("vtold", {}), ("designed", dict(lad=name, size=size)), ("bank", {})):
                res[arm] = list(ex.map(job, [(text, arm, kw, s, c, float(secs)) for s in seeds for c in COL]))
            e = {a: scored(res[a], secs, I) for a in res}
            b, t = e["circuit"], e["vtold"]
            gap = t[1] - b[1]
            xs = {a: (e[a][1] - b[1]) / np.where(np.abs(gap) < 1e-9, np.nan, gap) for a in ("designed", "bank")}
            g0, gi = t[0] - b[0], R.ci(gap)
            xv = {a: ((e[a][0] - b[0]) / g0 if g0 else float("nan"), R.ci(xs[a])) for a in xs}
            tastes = np.mean([x[4] for x in res["designed"]]) / secs
            need = max(0, context_count(name, size) - (0 if name == "combo" else 2)) + np.log2(max(context_count(name, size), 1))
            cert = gi[0] >= 0.25 and xv["designed"][1][0] >= 0.5
            cpu = np.mean([x[5] for a in res for x in res[a]])
            print(f"{size:5d} {secs:6d} | {b[0]:6.2f} {t[0]:6.2f} {g0:6.2f} [{gi[0]:+.2f},{gi[1]:+.2f}] | "
                  f"{xv['designed'][0]:+.2f} [{xv['designed'][1][0]:+.2f},{xv['designed'][1][1]:+.2f}] | {xv['bank'][0]:+.2f} [{xv['bank'][1][0]:+.2f},{xv['bank'][1][1]:+.2f}] | "
                  f"{tastes:.2f}  {need:.1f}/{tastes * secs:.0f} | {cpu:.1f}s | {'yes' if cert else 'no'}", flush=True)
            out[str(size)] = dict(secs=secs, base=b[0], told=t[0], gap=g0, gap_ci=gi, designed=xv["designed"], bank=xv["bank"], tastes=tastes, need=need, cert=bool(cert))
    import os
    tag = "_muscle" if os.environ.get("MUSCLE") == "1" else ""             # (the new body's certification apart)
    json.dump(out, open(f"/home/pilgrim/git/simple-learner/lab/v/ladders_{name}_{pairs}p_{dt}ms{tag}.json", "w"), indent=1)


def baseline(name, pairs=20, dt=2.5, workers=7, seed0=SEEDS0):
    """Today's only raw material: K random rivals in the bank (lab/rivals.py, R2's rule and Occam bar). x against base and told, on the same lives."""
    import rivals as RV
    I = R.boot(pairs)
    seeds = range(seed0, seed0 + pairs)
    print(f"== baseline {name}: {pairs} pairs, {dt} ms: x [95%] at K random rivals; solved if surely above .5", flush=True)
    with ProcessPoolExecutor(workers, initializer=R._init, initargs=(dt / 1000, False)) as ex:
        for size, secs in LADDERS[name]["rungs"]:
            if size == (0 if name == "combo" else 1):
                continue
            text = LADDERS[name]["world"](size)
            base, told = [list(ex.map(job, [(text, a, {}, s, c, float(secs)) for s in seeds for c in COL])) for a in ("circuit", "vtold")]
            b, t = scored(base, secs, I), scored(told, secs, I)
            line = f"{size:5d} {secs:6d} | gap {t[0] - b[0]:5.2f} |"
            for K in (10, 100, 1000):
                L = list(ex.map(jobK, [(text, K, s, c, float(secs)) for s in seeds for c in COL]))
                e = scored(L, secs, I)
                lo, hi = R.ci((e[1] - b[1]) / (t[1] - b[1]))
                line += f" K{K} {(e[0] - b[0]) / (t[0] - b[0]):+.2f} [{lo:+.2f},{hi:+.2f}]{'*' if lo > .5 else ' '} |"
            print(line, flush=True)


def jobK(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    import rivals as RV
    text, K, seed, first, secs = j
    t0 = time.perf_counter()
    l = S.live(RV.make(S.world_of(text), seed, first, {"rivals": ("random", K), **RV.occam(K)}), secs)
    g = [a - COST * b for a, b, _ in l]
    sp = spent(l)
    return (sum(g), sp, g[2], sp * l[2][2] / sum(t for _, _, t in l), sum(a + b for a, b, _ in l), time.perf_counter() - t0)


def cross(pairs=40, dt=2.5, workers=7, seed0=SEEDS0):
    """Are the ladders different? Each designed brain at a middle size on the others' middle rungs: x against that rung's base and told."""
    mids = dict(seq=5, time=5, combo=3)
    I = R.boot(pairs)
    seeds = range(seed0, seed0 + pairs)
    print(f"== cross: {pairs} pairs, {dt} ms: x [95%] of each designed brain (row) on each ladder's middle rung (column)", flush=True)
    with ProcessPoolExecutor(workers, initializer=R._init, initargs=(dt / 1000, False)) as ex:
        ref = {}
        for w, n in mids.items():
            secs = dict(LADDERS[w]["rungs"])[n]
            text = LADDERS[w]["world"](n)
            ref[w] = (text, secs, *[scored(list(ex.map(job, [(text, a, {}, s, c, float(secs)) for s in seeds for c in COL])), secs, I) for a in ("circuit", "vtold")])
        for a, n in mids.items():
            line = f"{a:6s}{n:3d} |"
            for w in mids:
                text, secs, b, t = ref[w]
                e = scored(list(ex.map(job, [(text, "designed", dict(lad=a, size=n), s, c, float(secs)) for s in seeds for c in COL])), secs, I)
                lo, hi = R.ci((e[1] - b[1]) / (t[1] - b[1]))
                line += f" {w} {(e[0] - b[0]) / (t[0] - b[0]):+.2f} [{lo:+.2f},{hi:+.2f}] |"
            print(line, flush=True)


if __name__ == "__main__":
    import ledger
    ledger.start()
    a = sys.argv[1:]
    if a[0] == "certify":
        certify(a[1], int(a[2]) if len(a) > 2 else 20, float(a[3]) if len(a) > 3 else 2.5, sizes=[int(x) for x in a[4].split(",")] if len(a) > 4 else None)
    elif a[0] == "baseline":
        baseline(a[1])
    elif a[0] == "cross":
        cross()
    elif a[0] == "check":
        from stage2_lang import lang
        for n, l in LADDERS.items():
            for s, _ in l["rungs"]:
                w = lang.World(l["world"](s), f"{n}{s}")
                print(n, s, "ok", getattr(w, "stage5", lambda: None) if False else "")

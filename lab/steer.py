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
EPS = 0.1                                       # ... and an option other than the best this often
_C = {}


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
    else:
        if arm not in _C:
            base = T.Circuit
            if arm == "still":
                class Still(base):
                    def step(self):
                        super().step()
                        return []
                _C[arm] = seconds_cls(Still)
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
    secs = {"plain": 300.0, "seq5": 300.0, "seq11": 600.0}[wname]
    text = {"plain": L.PLAIN, "seq5": L.seq(5), "seq11": L.seq(11)}[wname]
    s0 = next((int(x[1:]) for x in a if x.startswith("s") and x[1:].isdigit()), 130000)
    arms = ("circuit", "grown", "still")
    out = f"/home/pilgrim/git/simple-learner/lab/v/steer_{wname}_{n}_s{s0}.pkl"
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
        if arm == "grown":
            from collections import Counter
            line += " | reflexes: " + ", ".join(f"{k}:{v}" for k, v in Counter(str(r["reflex"]) for r in rows if r["arm"] == "grown").most_common(3))
        print(line, flush=True)

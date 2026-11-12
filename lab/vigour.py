"""vigour.py: how fast to act, set by recent food (the user, 2026-11-12: hunger; vigour follows the reward rate, Niv, Daw, Joel and Dayan
2007). Coupling sets what makes behaviour coherent but prefers half the right speed (D54); here the tempo (every rate of the starting
brain scaled by e^s) is searched by recent food instead. Bodies with drag drawn (a half to twice; equal thrusters, so only the tempo
matters: bodyladder's dragd), food from birth, 900 s, efficiency in the last third.

Arms: fixed (the starting brain), told (the tempo told: bodyladder's toldbody), food (a golden-section search over s in [-1, 1], each
setting judged by the net food, good less twice poisoned, in WIN s: recent food), coupling (the same search judged by D51's coupling).

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/vigour.py [PAIRS] [s106000]"""
import math
import pickle
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np

import bodyladder as BL
import couple_search as CS
import ladders as L
import stage3_random as R

SECS = 900.0
WIN = 40.0
LO, HI, TOL = -1.0, 1.0, 0.2
WORLD = BL.WORLDS["dragd"][0]
RATES = ("scan", "drive", "run")


FAST, SLOW = 20.0, 200.0                        # s: hunger's two running averages of food (recent; long-run)
R0 = 0.6                                        # good meals a second: an inherited "normal" (the plain world's rate), for hungerabs
K_VIG = 1.0                                     # the tempo's log factor per unit of log(recent / long-run food)
REGROW = {"plain": "(world)", "regrow60": "(world (on meal (if (= colour F) (do (hide block) (after 60 (show block))))))",
          "regrow120": "(world (on meal (if (= colour F) (do (hide block) (after 120 (show block))))))"}


class Hunger:
    """The starting brain whose tempo follows hunger (the user, 2026-11-12; vigour, Niv et al. 2007): two leaky averages of good meals,
    recent (FAST s) and long-run (SLOW s); tempo e^s with s = K_VIG log(recent / long-run), within [-1, .5]: slower when food has been
    scarcer than usual (energy saved), faster when richer. slow: the same brain always at e^-.5 (a control: is it just slowness?)."""

    def __init__(self, seed, p):
        from stage2_lang.seconds import seconds_cls
        import table as T
        self.dt, self.kind = p["dt"], p["kind"]
        self.forager = seconds_cls(T.Circuit)(seed, T.numbers(seed, {"sync": 1}))
        self.base = {r: self.forager.p[r] for r in RATES}
        self.fast = self.slow = 0.0
        self.clock = self.t = 0.0
        self.beats, self.trace = [], []
        self._tempo(-0.5 if self.kind == "slow" else 0.0)

    def _tempo(self, sv):
        self.s = sv
        for r in RATES:
            self.forager.p[r] = self.base[r] * math.exp(sv)

    def stimulate(self, sensor, at):
        self.forager.stimulate(sensor, at)

    def taste(self, value, at):
        if value > 0:
            self.fast += 1.0 / FAST
            self.slow += 1.0 / SLOW
        self.forager.taste(value, at)

    def step(self):
        out = self.forager.step()
        self.beats = list(getattr(self.forager, "beats", None) or [])
        self.clock += self.dt
        self.t = self.clock
        self.fast *= math.exp(-self.dt / FAST)
        self.slow *= math.exp(-self.dt / SLOW)
        if self.kind == "hungerabs" and self.clock > FAST:
            wf = 1.0 - math.exp(-self.clock / FAST)
            self._tempo(min(0.5, max(-1.0, K_VIG * math.log((self.fast / wf + 1e-3) / R0))))
        if self.kind == "hunger" and self.clock > SLOW / 4:
            wf = 1.0 - math.exp(-self.clock / FAST)          # each average corrected for the share of its window seen so far
            ws = 1.0 - math.exp(-self.clock / SLOW)
            sv = K_VIG * math.log((self.fast / wf + 1e-3) / (self.slow / ws + 1e-3))
            self._tempo(min(0.5, max(-1.0, sv)))
        if int(self.clock / 10.0) != int((self.clock - self.dt) / 10.0):
            self.trace.append((round(self.clock), round(self.s, 2)))
        return out


class TempoSearch:
    """The starting brain with a tempo knob searched by recent food (judge="food") or by coupling (judge="coupling")."""

    def __init__(self, seed, p):
        from stage2_lang.seconds import seconds_cls
        import table as T
        self.judge, self.dt = p["judge"], p["dt"]
        self.forager = seconds_cls(T.Circuit)(seed, T.numbers(seed, {"sync": 1}))
        self.base = {r: self.forager.p[r] for r in RATES}
        self.clock = self.t = 0.0
        self.beats = []
        self.lo, self.hi = LO, HI
        self.c, self.d = HI - CS.PHI * (HI - LO), LO + CS.PHI * (HI - LO)
        self.fc = self.fd = None
        self.queue = ["c", "d"]
        self.done, self.est, self.log = False, None, []
        self.net = 0.0
        self.Jf, self.Jp, self.s_bin, self.a_bin, self.prev, self.next_bin = np.zeros((4, 4)), np.zeros((4, 4)), 0, 0, None, CS.BIN
        self.win_end = WIN
        self.set_tempo(self.c)

    def set_tempo(self, s):
        for r in RATES:
            self.forager.p[r] = self.base[r] * math.exp(s)

    def stimulate(self, sensor, at):
        self.s_bin |= 1 << sensor
        self.forager.stimulate(sensor, at)

    def taste(self, value, at):
        self.net += 1.0 if value > 0 else -2.0 if value < 0 else 0.0
        self.forager.taste(value, at)

    def _judge(self):
        if self.judge == "food":
            f = self.net
        else:
            f = (CS._mi(self.Jf) + CS._mi(self.Jp)) / CS.BIN
        self.net = 0.0
        self.Jf[:], self.Jp[:] = 0, 0
        which = self.queue.pop(0)
        setattr(self, "f" + which, f)
        self.log.append((round(self.clock), round(getattr(self, which), 2), round(f, 2)))
        if not self.queue:
            if self.fc >= self.fd:
                self.hi, self.d, self.fd = self.d, self.c, self.fc
                self.c = self.hi - CS.PHI * (self.hi - self.lo)
                self.queue = ["c"]
            else:
                self.lo, self.c, self.fc = self.c, self.d, self.fd
                self.d = self.lo + CS.PHI * (self.hi - self.lo)
                self.queue = ["d"]
            if self.hi - self.lo < TOL:
                self.done, self.est = True, (self.lo + self.hi) / 2
                self.set_tempo(self.est)
                return
        self.set_tempo(getattr(self, self.queue[0]))

    def step(self):
        out = self.forager.step()
        self.beats = list(getattr(self.forager, "beats", None) or [])
        for m, _ in self.beats:
            self.a_bin |= 1 << m
        self.clock += self.dt
        self.t = self.clock
        if self.clock >= self.next_bin:
            cur = (self.s_bin, self.a_bin)
            if self.prev is not None and not self.done:
                self.Jf[self.prev[1], cur[0]] += 1
                self.Jp[self.prev[0], cur[1]] += 1
            self.prev, self.s_bin, self.a_bin = cur, 0, 0
            self.next_bin += CS.BIN
        if not self.done and self.clock >= self.win_end:
            self._judge()
            self.win_end = self.clock + WIN
        return out


def make(arm, seed, first, world=None):
    from stage2_lang import arms as S
    from stage2_lang.sim import WLife
    if world is not None:                               # the regrowth worlds: fixed, slow, hunger
        if arm == "fixed":
            return S.make(S.world_of(REGROW[world]), "circuit", seed, first)
        return WLife(seed, first, (lambda s: Hunger(s, {"dt": WLife.dt, "kind": arm})), S.world_of(REGROW[world]), seconds=True)
    if arm in ("fixed", "told"):
        return BL.make(WORLD, "toldbody" if arm == "told" else "circuit", seed, first)
    return WLife(seed, first, (lambda s: TempoSearch(s, {"judge": arm, "dt": WLife.dt})), S.world_of(WORLD), seconds=True)


def job(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    arm, seed, first = j[:3]
    world = j[3] if len(j) > 3 else None
    lf = make(arm, seed, first, world)
    l = S.live(lf, SECS)
    g = [a - COST * c for a, c, _ in l]
    sp = spent(l)
    b = lf.brain
    return dict(arm=arm, seed=seed, eff=(0.0, 0.0, g[2], sp * l[2][2] / sum(t for _, _, t in l)),
                logd=math.log(getattr(lf, "v_d", 1.0)), est=getattr(b, "est", None), log=getattr(b, "log", []), world=world,
                trace=getattr(b, "trace", []))


def regrowth(n=10, s0=107000):
    """The user's world: food regrows only after a delay, so richness varies; tempo by hunger against fixed and always slower."""
    I = R.boot(n)
    print(f"== hunger sets the tempo, in worlds where eaten food regrows after a delay; {n} pairs, {SECS:.0f} s, last third [95%]")
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        for world in REGROW:
            res = {arm: list(ex.map(job, [(arm, s, c, world) for s in range(s0, s0 + n) for c in L.COL])) for arm in ("fixed", "slow", "hunger", "hungerabs")}
            base = L.scored([r["eff"] for r in res["fixed"]], SECS, I)
            line = f"  {world:9s} fixed {base[0]:+.2f}"
            for arm in ("slow", "hunger", "hungerabs"):
                e = L.scored([r["eff"] for r in res[arm]], SECS, I)
                d = e[1] - base[1]
                line += f" | {arm} {e[0]:+.2f} ({e[0] - base[0]:+.2f} [{np.percentile(d, 2.5):+.2f},{np.percentile(d, 97.5):+.2f}])"
            tr = [x[1] for r in res["hungerabs"] for x in r["trace"]]
            line += f" | hungerabs' tempo: median {np.median(tr):+.2f}, quartiles {np.percentile(tr, 25):+.2f}, {np.percentile(tr, 75):+.2f}"
            print(line, flush=True)


ARMS = ("fixed", "told", "food", "coupling")

if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "regrowth":
        import ledger
        ledger.start()
        regrowth(int(a[1]) if len(a) > 1 else 10, int(a[2][1:]) if len(a) > 2 else 107000)
        sys.exit()
    n = int(a[0]) if a and a[0].isdigit() else 10
    s0 = next((int(x[1:]) for x in a if x.startswith("s") and x[1:].isdigit()), 106000)
    out = f"/home/pilgrim/git/simple-learner/lab/v/vigour_{n}_s{s0}.pkl"
    if "report" not in a:
        import ledger
        ledger.start()
        with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
            rows = list(ex.map(job, [(arm, s, c) for arm in ARMS for s in range(s0, s0 + n) for c in L.COL], chunksize=2))
        pickle.dump(rows, open(out, "wb"))
    rows = pickle.load(open(out, "rb"))
    I = R.boot(n)
    base = L.scored([r["eff"] for r in rows if r["arm"] == "fixed"], SECS, I)
    print(f"== vigour: the tempo searched by recent food or by coupling, drag drawn; {n} pairs, {SECS:.0f} s, last third [95%]")
    for arm in ARMS:
        rs = [r for r in rows if r["arm"] == arm]
        e = L.scored([r["eff"] for r in rs], SECS, I)
        d = e[1] - base[1]
        line = f"  {arm:9s} {e[0]:+.2f} [{np.percentile(e[1], 2.5):+.2f},{np.percentile(e[1], 97.5):+.2f}]"
        if arm != "fixed":
            line += f"  vs fixed {e[0] - base[0]:+.2f} [{np.percentile(d, 2.5):+.2f},{np.percentile(d, 97.5):+.2f}]"
        est = [(r["est"], r["logd"]) for r in rs if r["est"] is not None]
        if est:
            x, y = np.array(est).T
            line += f" | tempo against log drag: median error {np.median(np.abs(x - y)):.2f}, correlation {np.corrcoef(x, y)[0, 1]:+.2f}, mean offset {np.mean(x - y):+.2f}"
        print(line, flush=True)

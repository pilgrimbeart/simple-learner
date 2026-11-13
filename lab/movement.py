"""movement.py: plan B on the body (the user, 2026-11-13): movements grown, not wired. Main session. Predictions: lab/v/newparts_predictions.md.

On the muscle-like body a lone pulse barely moves; pulses close together add. So which new thruster to use is not enough: how to pulse
it matters. Play (still, the base behaviour paused, as D55's) kicks one new motor, or none, in a burst of 1 to 4 pulses GAP apart, the
length drawn at random. Each pulse is a step of a growing network's stream (D59: blocks grow beneath contradictions over sequences of
kicks, strict copies); a trial begins with a rest symbol and ends with its letter, whether activity on the new eye moved towards line 3
(1) or line 2 (0). A movement is a unit: a kick, or a block (a sequence of kicks). Play ends when each new line has a movement surely
moving activity out of its half against the no-kick unit (two-proportion test, SURE), or after PLAY_N trials a motor; the surest
movement for each line is then played, kick by kick, whenever that line pulses while the creature drives (as D55's reflexes, with
lateral inhibition). Arm moveG; its yardstick toldarcsI fires one pulse a line pulse.

    MUSCLE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/movement.py [PAIRS] [s110000]"""
import math
import os
import pickle
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import uptake as U

_C = {}
GRADED = os.environ.get("GRADED") == "1"         # the growing network's graded readouts decide (2026-11-13)
LENGTHS = tuple(int(x) for x in os.environ.get("LENGTHS", "1,3,6,12").split(","))   # play's burst lengths (fewer values: the evidence less spread, 2026-11-13)
PLAY_CAP = 200.0                                # s of play at most after the new parts wake (the hand-built play took 110 to 250)
GAP = 0.02                                      # s between the pulses of a burst (within the muscle's 30 ms activation)
BURST = 12                                      # play's bursts: 1 to this many pulses (4 moved the muscle body too little to see, 2026-11-13)


def move_cls(base):
    A = U.arcs_cls(base)

    class Mover(A):
        def setup(self, mode, right=None):
            super().setup("learn3bIN", right)
            import grownet as GN
            self.mode = "move"
            self.gnet = GN.Net("mv", 60, np.random.default_rng(int(self.t * 1000) + 13), alphabet=len(U.MOTORS) + 2, strict=True)
            self.gi, self.trials, self.sched, self.mv, self.mv_last = 0, [], [], {}, {2: -1e9, 3: -1e9}
            self.play_over = False
            self.ntrials = {m: 0 for m in list(U.MOTORS) + [None]}
            self.mrng = np.random.default_rng(int(self.t * 1000) + 17)
            self.REST, self.NONE = len(U.MOTORS) + 1, len(U.MOTORS)

        def stimulate(self, sensor, at):
            if sensor < 2:
                return super().stimulate(sensor, at)
            if self.last_c == self.food:
                self.rl.append((self.t + at, sensor))
                self.rl = [x for x in self.rl if x[0] > self.t + at - U.INHIB_W]
            if self.woke is None:
                self.woke = self.t
            self.lines.append((self.t + at, sensor))
            self.last_line = self.t + at
            if self.play_over and self.mv.get(sensor) and self.last_c == self.food and self.t - self.last_drive < self.p["hold"]:
                if self.t - self.mv_last[sensor] >= U.REFRACT and self._free(sensor):
                    for j, m in enumerate(self.mv[sensor]):
                        self.sched.append((self.t + at + j * GAP, m))
                    self.mv_last[sensor] = self.t

        def _seq(self, k):
            x = self.gnet.units[k]
            if x["sym"] is not None:
                return [x["sym"]]
            return self._seq(x["u"]) + self._seq(x["v"])

        def _trial(self):
            """Start a trial when something is in view on the new lines and the last has settled: a burst of one motor, or none."""
            if self.trials and (self.trials[-1]["open"] or self.t < self.trials[-1]["last"] + U.PRE + U.SETTLE):
                return
            if self.t - self.last_line >= 0.1:
                if self.t - max(self.last_line, self.trials[-1]["last"] if self.trials else -1e9) > U.LOOK:
                    self.sched.append((self.t, 0))      # a look-around beat of the scanning motor
                    self.trials.append(dict(m=None, b=0, t0=self.t, last=self.t, open=False))
                return
            opts = list(U.MOTORS) + [None]
            m = opts[len(self.trials) % len(opts)]
            b = int(LENGTHS[int(self.mrng.integers(len(LENGTHS)))]) if m is not None else 1
            for j in range(b if m is not None else 0):
                self.sched.append((self.t + j * GAP, m))
            self.trials.append(dict(m=m, b=b, t0=self.t, last=self.t + (b - 1) * GAP, open=True))

        def _close(self):
            N = self.gnet
            for tr in self.trials:
                if not tr["open"] or self.t <= tr["last"] + U.PRE:
                    continue
                tr["open"] = False

                def bal(a, b):
                    return sum(1 for t, l in self.lines if a <= t < b and l == 3) - sum(1 for t, l in self.lines if a <= t < b and l == 2)
                x = bal(tr["last"], tr["last"] + U.PRE) - bal(tr["t0"] - U.PRE, tr["t0"])
                self.ntrials[tr["m"]] += 1
                N.write(self.gi, self.REST)
                N.tidy(self.gi, self.t)
                self.gi += 1
                syms = [self.NONE] if tr["m"] is None else [U.MOTORS.index(tr["m"])] * tr["b"]
                for j, sy in enumerate(syms):
                    N.write(self.gi, sy)
                    if j == len(syms) - 1:
                        k, f = N.says(self.gi)
                        if GRADED:
                            N.add_value(f, float(x))
                        if x != 0:
                            N.learn(self.gi, int(x > 0), self.t, k, f)
                            if k is not None:
                                N.credit(k, self.t)
                    N.tidy(self.gi, self.t)
                    self.gi += 1
            self.lines = [x for x in self.lines if x[0] > self.t - 2 * U.PRE - 0.5]
            self._decide()

        def _decide(self):
            N = self.gnet
            c = next(x["n"] for x in N.units.values() if x["sym"] == self.NONE)
            cv = next(x.get("val") for x in N.units.values() if x["sym"] == self.NONE)
            nc = c[0] + c[1]
            if self.t - self.woke > PLAY_CAP or all(self.ntrials[m] >= U.PLAY_N for m in U.MOTORS):
                nc = max(nc, U.PLAY_MIN)                # the cap ends play whatever the evidence (fixed 2026-11-13: it sat after this check)
            if nc < U.PLAY_MIN:
                return
            z = {}
            for k, x in N.units.items():
                if x["sym"] in (self.NONE, self.REST):
                    continue
                seq = self._seq(k)
                if self.REST in seq or self.NONE in seq or len(set(seq)) != 1:
                    continue                            # a movement: one motor's kicks, within one trial
                a = x["n"]
                na = a[0] + a[1]
                if na < U.PLAY_MIN // 2:
                    continue
                if GRADED:                              # how far activity moved, against no kick
                    z[k] = N.welch(x.get("val"), cv)
                    continue
                pa, pc = a[1] / na, c[1] / nc
                pp = (a[1] + c[1]) / (na + nc)
                z[k] = (pa - pc) / math.sqrt(max(pp * (1 - pp), 1e-6) * (1 / na + 1 / nc))
            for line, sign in ((2, 1), (3, -1)):         # each line wired as soon as it has a sure movement
                if line not in self.mv:
                    c2 = [k for k, v in z.items() if sign * v >= U.SURE]
                    if c2:
                        k = max(c2, key=lambda kk: sign * z[kk])
                        self.mv[line] = [U.MOTORS[s] for s in self._seq(k)]
            done = all(self.ntrials[m] >= U.PLAY_N for m in U.MOTORS) or self.t - self.woke > PLAY_CAP or len(self.mv) == 2
            if done:
                self.play_over = True
                self.cands = {2: [], 3: []}
                blocks = sum(1 for x in N.units.values() if x["sym"] is None)
                self.log.append((round(self.t), "play done", {l: self.mv.get(l) for l in (2, 3)}, blocks))

        def step(self):
            out = super().step()
            playing = self.woke is not None and not self.play_over
            if playing:
                self._close()
                if not self.play_over:
                    self._trial()
                out = []                                # still: the base behaviour paused while playing
            due = [m for t, m in self.sched if t <= self.t]
            self.sched = [(t, m) for t, m in self.sched if t > self.t]
            return list(out) + due
    return Mover


def job(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    from stage2_lang.sim import WLife
    from stage2_lang.seconds import seconds_cls
    import table as T
    arm, seed, first = j
    if arm != "moveG":
        r = U.job(j)
        return r
    if "mv" not in _C:
        _C["mv"] = move_cls(seconds_cls(T.Circuit))
    cls = _C["mv"]
    q = T.numbers(seed, {"sync": 1})
    lf = WLife(seed, first, (lambda s: cls(s, q)), S.world_of(U.WORLD_TEXT), seconds=True)
    lf.brain.setup("moveG")
    l = S.live(lf, U.SECS)
    g = [a - COST * b for a, b, _ in l]
    sp = spent(l)
    b = lf.brain
    play_done = next((e[0] for e in b.log if len(e) > 1 and e[1] == "play done"), None)
    mv = next((e[2] for e in b.log if len(e) > 1 and e[1] == "play done"), None)
    return dict(arm=arm, seed=seed, eff=(0.0, 0.0, g[2], sp * l[2][2] / sum(t for _, _, t in l)), grow=lf.grow_at, play_done=play_done,
                whole=(sum(g), sp), mv=mv, sides={lf.wire_m[th]: th % 2 for th in range(2, len(lf.wire_m))}, on=[])


if __name__ == "__main__":
    a = sys.argv[1:]
    n = int(a[0]) if a and a[0].isdigit() else 10
    s0 = next((int(x[1:]) for x in a if x.startswith("s") and x[1:].isdigit()), 110000)
    arms = ("base", "toldarcsI", "learn3bIN", "moveG")
    out = f"/home/pilgrim/git/simple-learner/lab/v/movement_{n}_s{s0}_{int(U.SECS)}s{'_muscle' if os.environ.get('MUSCLE') == '1' else ''}{'_graded' if GRADED else ''}{'_L' + os.environ['LENGTHS'].replace(',', '-') if os.environ.get('LENGTHS') else ''}.pkl"
    if "report" not in a:
        import ledger
        ledger.start()
        import stage3_random as R
        with ProcessPoolExecutor(7, initializer=U._init) as ex:
            rows = list(ex.map(job, [(arm, s, c) for arm in arms for s in range(s0, s0 + n) for c in U.L.COL], chunksize=2))
        pickle.dump(rows, open(out, "wb"))
    rows = pickle.load(open(out, "rb"))
    import stage3_random as R
    I = R.boot(n)
    e = {arm: U.L.scored([r["eff"] for r in rows if r["arm"] == arm], U.SECS, I) for arm in arms}
    print(f"== movements grown on the new parts: {n} pairs, {U.SECS:.0f} s, {'muscle' if os.environ.get('MUSCLE') == '1' else 'original'} body; last third [95%]")
    for arm in arms:
        d = e[arm][1] - e["base"][1]
        rs = [r for r in rows if r["arm"] == arm]
        wh = np.array([r["whole"] for r in rs])
        line = f"  {arm:10s} {e[arm][0]:+.2f} [{np.percentile(e[arm][1], 2.5):+.2f},{np.percentile(e[arm][1], 97.5):+.2f}]"
        if arm != "base":
            line += f"  vs base {e[arm][0] - e['base'][0]:+.2f} [{np.percentile(d, 2.5):+.2f},{np.percentile(d, 97.5):+.2f}]"
        if arm == "moveG":
            lens = [len(v) for r in rs if r["mv"] for v in r["mv"].values() if v]
            both = sum(1 for r in rs if r["mv"] and r["mv"].get(2) and r["mv"].get(3)) / len(rs)
            pd = [r["play_done"] - r["grow"] for r in rs if r["play_done"] is not None]
            line += f" | movements' length {np.mean(lens) if lens else 0:.1f} (mean); a movement for both lines {both:.0%}; play done {np.median(pd) if pd else float('nan'):.0f} s after growth"
        print(line, flush=True)

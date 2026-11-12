"""couple_search.py: understanding as coupling, as a mechanism (PROGRAMME.md, the guiding principle; D51). The starting brain forages
from birth; a small counter at its interface measures, over each WIN s, how tightly its senses and actions go together (D51's
coupling: which eyes pulsed and which motors beat, in 50 ms bins, I(A_t; S_t+1) + I(S_t; A_t+1) from 4 x 4 counts); and its balance knob
is searched by that alone, with no reward and no model of the body: a golden-section search over the knob's range (generic one-
dimensional optimisation), each setting judged by WIN s of its own coupling, until the bracket is under TOL (bored: certain).

World: play4's (a quiet spell, meals worth nothing, until 400 to 600 s; then food and poison), lopsided bodies; and the plain body (the
knob's right value 0) as the check that the search leaves a normal body alone. Scored from the challenge's onset as play4.

Arms: forage (knob 0), told, partners (play then our formula, D47), couple (this search), couple:fine (the bracket to .1, and
each setting judged 60 s once the bracket is under .5: judge longer when the choices are closer), couple:fit (the same, ending
at the top of a parabola through the judgements near the bracket: every judgement used), couple:occam (then the default, no
adjustment, judged against the answer, 60 s each; the answer kept only if its coupling is 10% higher: MacKay's Occam factor).

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 BELIEF=... PREDICT=... .venv/bin/python lab/couple_search.py [PAIRS] [s98000]"""
import math
import pickle
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np

import couple as C
import play3 as P3
import play4 as P4
import stage3_random as R

BIN = 0.05                                      # s: the counter's bins
WIN = 30.0                                      # s: coupling judged over this long at each setting
LO, HI = -1.6, 1.6                              # the knob's range (the brain's own settings)
TOL = 0.3                                       # done when the bracket is narrower than this
PHI = (math.sqrt(5) - 1) / 2
OCCAM = 1.1                                     # an adjustment is kept only if its coupling beats no adjustment's by this factor


def _mi(J):
    n = J.sum()
    if n == 0:
        return 0.0
    P = J / n
    px, py = P.sum(1), P.sum(0)
    nz = P > 0
    I = float((P[nz] * np.log2(P[nz] / np.outer(px, py)[nz])).sum())
    return I - ((nz.sum() - 1) - (np.count_nonzero(px) - 1) - (np.count_nonzero(py) - 1)) / (2 * n * math.log(2))


class CoupleBrain:
    """The starting brain, with a counter of its own sense-action coupling and a knob searched by it."""

    def __init__(self, seed, p):
        from stage2_lang.seconds import seconds_cls
        import table as T
        self.dt = p["dt"]
        self.tol = p.get("tol", TOL)
        self.occam = p.get("occam", False)             # end by judging the default (no adjustment) against the answer
        self.vertex = p.get("vertex", False)           # end at the top of a parabola fitted through the judgements, not the bracket's middle
        self.fine = p.get("fine", False)               # judge longer when the choices are closer: 2 WIN once the bracket is under .5
        self.forager = seconds_cls(T.Circuit)(seed, T.numbers(seed, {"sync": 1}))
        self.clock, self.t = 0.0, 0.0
        self.pulses, self.beat_log, self.beats = [], [], []
        self.s_bin, self.a_bin = 0, 0
        self.prev = None                                # last bin's (S, A)
        self.next_bin = BIN
        self.Jf, self.Jp = np.zeros((4, 4)), np.zeros((4, 4))
        self.lo, self.hi = LO, HI
        self.c, self.d = self.hi - PHI * (self.hi - self.lo), self.lo + PHI * (self.hi - self.lo)
        self.fc = self.fd = None
        self.queue = ["c", "d"]                         # which point is being judged now
        self.win_end = WIN
        self.done, self.est, self.log = False, None, []
        self.set_balance(self.c)

    def set_balance(self, b):
        p = self.forager.p
        p["g0"], p["g1"] = math.exp(b / 2), math.exp(-b / 2)

    def stimulate(self, sensor, at):
        self.pulses.append((self.clock + at, sensor))
        self.s_bin |= 1 << sensor
        self.forager.stimulate(sensor, at)

    def taste(self, value, at):
        self.forager.taste(value, at)

    def _judge(self):
        f = (_mi(self.Jf) + _mi(self.Jp)) / BIN
        self.Jf[:], self.Jp[:] = 0, 0
        if getattr(self, "final", None):                # the Occam check: default, then answer, 2 WIN each
            name, b = self.final.pop(0)
            self.final_f[name] = f
            self.log.append((self.clock, b, f))
            if self.final:
                self.set_balance(self.final[0][1])
            else:
                if self.final_f["answer"] <= OCCAM * self.final_f["default"]:
                    self.est = 0.0                      # the evidence doesn't clearly beat no adjustment
                self.done = True
                self.set_balance(self.est)
            return
        which = self.queue.pop(0)
        if which == "c":
            self.fc = f
        else:
            self.fd = f
        self.log.append((self.clock, getattr(self, which), f))
        if not self.queue:                              # both points judged: narrow the bracket (golden section)
            if self.fc >= self.fd:
                self.hi, self.d, self.fd = self.d, self.c, self.fc
                self.c = self.hi - PHI * (self.hi - self.lo)
                self.queue = ["c"]
            else:
                self.lo, self.c, self.fc = self.c, self.d, self.fd
                self.d = self.lo + PHI * (self.hi - self.lo)
                self.queue = ["d"]
            if self.hi - self.lo < self.tol:
                self.done, self.est = True, (self.lo + self.hi) / 2
                if self.vertex:                         # use every judgement: the top of a parabola through those near the bracket
                    pts = np.array([(b, f) for _, b, f in self.log if abs(b - self.est) <= 0.6])
                    if len(pts) >= 3 and np.ptp(pts[:, 0]) > 0.05:
                        a2, a1, _ = np.polyfit(pts[:, 0], pts[:, 1], 2)
                        if a2 < 0:
                            self.est = float(np.clip(-a1 / (2 * a2), self.est - 0.3, self.est + 0.3))
                if self.occam:                          # the default (no adjustment) keeps its prior mass: judge it against the answer
                    self.done = False
                    self.final = [("default", 0.0), ("answer", self.est)]
                    self.final_f = {}
                    self.set_balance(0.0)
                    return
                self.set_balance(self.est)
                return
        self.set_balance(getattr(self, self.queue[0]))

    def step(self):
        out = self.forager.step()
        self.beats = list(getattr(self.forager, "beats", None) or [])
        for m, at in self.beats:
            self.beat_log.append((self.clock + at, m))
            self.a_bin |= 1 << m
        self.clock += self.dt
        self.t = self.clock
        if self.clock >= self.next_bin:                 # a bin closes: count it against the last
            cur = (self.s_bin, self.a_bin)
            if self.prev is not None and not self.done:
                self.Jf[self.prev[1], cur[0]] += 1      # actions then senses
                self.Jp[self.prev[0], cur[1]] += 1      # senses then actions
            self.prev, self.s_bin, self.a_bin = cur, 0, 0
            self.next_bin += BIN
        if not self.done and self.clock >= self.win_end:
            self._judge()
            self.win_end = self.clock + (2 * WIN if self.fine and self.hi - self.lo < 0.5 else WIN)
        return out


import bodyladder as BL
D_ = "(pow 2 (uniform -1 1))"
BOTH = (f"(world {BL.M} (let a {D_}) (let b {D_}) (let d {D_}) (let q (uniform 400 600)) (on fire (set gain (if (= thruster 0) a b)))"
        " (on move (set vx (* vx (exp (* (- 1 d) DRAG TICK)))) (set vy (* vy (exp (* (- 1 d) DRAG TICK)))) (set spin (* spin (exp (* (- 1 d) DRAG TICK)))))"
        " (on meal (if (< t q) (set worth 0))))")     # thrusters and drag drawn, with play4's quiet spell: the balance and the tempo both matter


def world_text(body):
    return {"lopsided": P3.WORLD, "plain": C.PLAIN, "both": BOTH}[body]


def make(arm, body, seed, first):
    from stage2_lang import arms as S
    from stage2_lang.sim import WLife
    text = world_text(body)
    if body == "both" and arm == "told":                 # told the balance and the tempo (bodyladder's toldbody)
        return BL.make(text, "toldbody", seed, first)
    w = S.world_of(text)
    if arm.startswith("couple"):
        p = {"dt": WLife.dt}
        if arm in ("couple:fine", "couple:fit"):
            p |= {"tol": 0.1, "fine": True}
        if arm == "couple:fit":
            p |= {"vertex": True}
        if arm == "couple:occam":
            p |= {"tol": 0.1, "fine": True, "vertex": True, "occam": True}
        return WLife(seed, first, (lambda s: CoupleBrain(s, p)), w, seconds=True)
    old = P3.WORLD
    P3.WORLD = text
    try:
        return P3.make(arm, seed, first)
    finally:
        P3.WORLD = old


def job(j):
    from stage2_lang import arms as S
    arm, body, seed, first = j
    lf = make(arm, body, seed, first)
    right = 0.0
    if body in ("lopsided", "both"):
        k = {lf.wire_m[th]: g for th, g in ((0, lf.v_a), (1, lf.v_b))}
        right = __import__('sigmoid_body').right_knob(k[0], k[1], __import__('table').numbers(seed, {})['drive'])      # (the right knob for whichever body is on)
    S.live(lf, P4.SECS)
    q, b = lf.v_q, lf.brain
    win = []
    for a, z in P4.WINDOWS:
        lo, hi = (q + a) / lf.dt, (q + z) / lf.dt
        good = sum(am for t, bad, am in lf.scored if lo <= t < hi and not bad)
        badm = sum(am for t, bad, am in lf.scored if lo <= t < hi and bad)
        win.append((good - 2.0 * badm) / (z - a) * 10)
    done_at = b.log[-1][0] if getattr(b, "done", False) else None
    return dict(arm=arm, body=body, seed=seed, win=win, right=right, est=getattr(b, "est", None), onset=q, done_at=done_at)


ARMS = ("forage", "told", "partners:beats", "couple", "couple:fine", "couple:fit", "couple:occam")


def report(rows):
    for body in [b for b in ("lopsided", "plain", "both") if any(r["body"] == b for r in rows)]:
        rb = [r for r in rows if r["body"] == body]
        arms = [a for a in ARMS if any(r["arm"] == a for r in rb)]
        n = len([r for r in rb if r["arm"] == arms[0]]) // 2
        I = R.boot(n)
        base = np.array([r["win"] for r in rb if r["arm"] == "forage"])
        print(f"== {body}: {n} pairs; gain from onset, a 10 s, vs forage [95%] | knob: median error, within .2 | search done (median s; before onset)")
        for a in arms:
            rs = [r for r in rb if r["arm"] == a]
            W = np.array([r["win"] for r in rs])
            line = f"{a:15s}"
            for i in range(2):
                d = W[I, i].mean(1) - base[I, i].mean(1)
                line += f" | {W[:, i].mean():+.2f}, {W[:, i].mean() - base[:, i].mean():+.2f} [{np.percentile(d, 2.5):+.2f},{np.percentile(d, 97.5):+.2f}]"
            e = [abs(r["est"] - r["right"]) for r in rs if r["est"] is not None]
            if e:
                line += f" | {np.median(e):.2f}, {np.mean(np.array(e) <= .2):.0%}"
            dn = [(r["done_at"], r["onset"]) for r in rs if r.get("done_at")]
            if dn:
                line += f" | {np.median([x for x, _ in dn]):.0f} s; {np.mean([x < o for x, o in dn]):.0%}"
            print(line, flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    n = int(a[0]) if a and a[0].isdigit() else 20
    s0 = next((int(x[1:]) for x in a if x.startswith("s") and x[1:].isdigit()), 98000)
    out = f"/home/pilgrim/git/simple-learner/lab/v/couple_search_{n}_s{s0}.pkl"
    out = out.replace(".pkl", "_muscle.pkl") if __import__("os").environ.get("MUSCLE") == "1" else out   # (the new body's lives apart)
    if "report" in a:
        report(pickle.load(open(out, "rb")))
        sys.exit()
    import ledger
    ledger.start()
    arms = [x for x in a if x in ARMS] or list(ARMS)
    jobs = [(arm, "lopsided", s, c) for arm in arms for s in range(s0, s0 + n) for c in ("red", "blue")]
    jobs += [(arm, "plain", s, c) for arm in arms if arm in ("forage", "couple", "couple:fine", "couple:fit", "couple:occam") for s in range(s0, s0 + n // 2) for c in ("red", "blue")]
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        rows = list(ex.map(job, jobs, chunksize=2))
    pickle.dump(rows, open(out, "wb"))
    report(rows)

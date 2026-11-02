"""trick2.py: D16 again, with a denser credit (QUESTIONS.md, the plan, 3). D16's reservoir (trick.py: random sequence
detectors beside B, each adding a beat to its motor with a learned probability, a REINFORCE tag fading over tau_e)
learned to rescue lopsided bodies but no steering: credit came only through meals. Here a detector's tag may also be
credited every tick by the food eye's pulses against their running mean (sight=eta_s; D19: the food a drive saw
judges it better than meals do), the proxy evolution supplies, never a property of the body; taste=0 turns meals'
credit off. Long lives judged on their last `judge` s, and a learning curve (food, poison per `seg` s).

    python trick2.py ARM [SEEDS] [seconds=10000] [judge=s] [body=1] [k=v ...]
    ARM: plain (B) or trick; k: trick.py's, and sight (eta_s), tau_b (the running mean's time, 200 s), taste (1),
    weak (1: the motor-share of grown detectors on the weaker thruster's motor is reported)"""
import sys, pickle
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from discrete import model as M
from units import TICK
import trick as T


class Trick2(T.Trick):
    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.fbar = 0.0
        n = len(self.a)
        self.last_fire = np.full(n, -1e9)               # burst=G: one coin per burst of a detector's own firing
        self.coin = np.zeros(n, bool)                   # (a burst begins after G s without firing): tagged once
        self.exp = np.zeros(n, bool)                    # duty: this burst is exploring
        self.v = np.full(n, 1e-12)                      # zthr: each detector's sum of its squared credit steps
        self.bstart = np.full(n, -1e9)                  # bmax: a burst also ends after bmax s (its own timer)

    def taste(self, value, at):
        if self.p.get("taste", 1):
            w0 = self.w.copy()
            M.Model.taste(self, value, at)
            if self.p.get("learn", 1):                  # pv: a poison's value (D16: 2)
                self.w += self.p.get("eta", 0.05) * (1.0 if value > 0 else -self.p.get("pv", 2.0)) * self.tag
            self.v += (self.w - w0) ** 2
        else:
            M.Model.taste(self, value, at)

    def step(self):
        if self.p.get("burst"):
            return self._burst_step()
        F = self.seen[self.food]
        out = super().step()
        es = self.p.get("sight", 0.0)
        if es and self.p.get("learn", 1):
            r = float(F > 0)
            self.w += es * (r - self.fbar) * self.tag
            self.fbar += TICK / self.p.get("tau_b", 200.0) * (r - self.fbar)
        return out


    def _burst_step(self):
        p = self.p
        F, P = self.seen[self.food], self.seen[1 - self.food]
        out = T.M.Model.step(self)
        ev = np.array([F > 0, P > 0, 0 in out, 1 in out], float)
        self.i = (self.i + 1) % self.H
        self.hist[:, self.i] = ev
        idx = (self.i - self.lag[None, :] - np.arange(T.WIN)[:, None]) % self.H
        fire = (ev[self.b] > 0) & (self.hist[self.a[None, :], idx].sum(0) > 0)
        self.tag -= TICK / p.get("tau_e", 2.0) * self.tag
        lo, hi = p.get("pmin", 0.05), p.get("pmax", 0.95)
        if fire.any():
            f = np.flatnonzero(fire)
            new = f[(self.t - self.last_fire[f] > p["burst"]) | (self.t - self.bstart[f] > p.get("bmax", 2.0))]
            if len(new):
                self.bstart[new] = self.t               # a burst begins: its coin, tagged once
                pr = np.clip(p.get("p0", 0.05) + self.w[new], lo, hi)
                if p.get("duty"):                       # duty: explore (an even coin, tagged) in this share of
                    ex = self.r.random(len(new)) < p["duty"]    # bursts, else act at the learned odds, untagged
                    if p.get("zthr"):                   # zthr: exploit only on clear evidence of one's own
                        pr = np.where(self.w[new] / np.sqrt(self.v[new]) > p["zthr"], pr, 0.0)
                    self.coin[new] = self.r.random(len(new)) < np.where(ex, 0.5, pr)
                    self.tag[new] += np.where(ex, self.coin[new] - 0.5, 0.0)
                    self.exp[new] = ex
                else:
                    self.coin[new] = self.r.random(len(new)) < pr
                    self.tag[new] += np.where(self.coin[new], 1.0 - pr, -pr)
            self.last_fire[f] = self.t
            act = f[self.coin[f]]
            if p.get("learn", 1) and p.get("charge", 0):    # charge=1: each beat's cost (THRUST meals, at price lam)
                ch = act[self.exp[act]] if p.get("duty") else act   # (duty: only exploring bursts' beats)
                self.w[ch] -= p.get("eta", 0.05) * p.get("lam", 2.0) * T.THRUST    # charged at once to its detector
            out = out + [int(m) for m in self.act[act]]
            self.extra += len(act)
        es = p.get("sight", 0.0)
        if es and p.get("learn", 1):
            r = float(F > 0)
            dw = es * (r - self.fbar) * self.tag
            self.w += dw
            self.v += dw ** 2
            self.fbar += TICK / p.get("tau_b", 200.0) * (r - self.fbar)
        if p.get("tau_v"):                              # tau_v: the evidence's noise scale fades (else it grows
            self.v -= TICK / p["tau_v"] * self.v        # without end while w is bounded, and zthr shuts every gate)
        if p.get("learn", 1) and p.get("tau_w"):        # tau_w: forgetting, each w relaxing to 0 (its odds to p0)
            self.w -= TICK / p["tau_w"] * self.w
        if p.get("learn", 1) and p.get("duty"):         # duty: exploring needs no floor; w free, bounded
            np.clip(self.w, -1.0, 1.0, out=self.w)
        elif p.get("learn", 1):                         # w kept where the odds can still move
            np.clip(self.w, lo - p.get("p0", 0.05), hi - p.get("p0", 0.05), out=self.w)
        return out


def life(job):
    from creature import Life
    from minimal.spec import SPAN, Lived, thirds
    arm, p, spread, seed, seconds, poison = job
    q = {k: v for k, v in M.drawn(p, spread, seed).items() if k not in ("body", "judge", "seg")}
    lf = Life(seed, poison, brain=lambda s: (Trick2 if arm == "trick" else M.Model)(s, q))
    f = None
    if p.get("body", 1):
        from discrete.bodies import THRUSTERS, draw, vary
        f = draw(seed, THRUSTERS)
        vary(lf, f)
    if arm == "trick" and p.get("planted") and f is not None:
        thr = {m: t for t, m in lf.motor.items()}       # diagnostic, the experimenter's: detector 0 the right steer
        wk = int(f[thr[0]] > f[thr[1]])                 # (a weak-motor beat beside each drive beat), 1 its wrong twin
        b = lf.brain
        pairs = ((0, wk), (1, 1 - wk)) if p["planted"] > 0 else ((0, 1 - wk),)   # planted=-1: the wrong one alone
        for j, act in pairs:
            if j < len(b.a):
                b.a[j], b.b[j], b.lag[j], b.act[j] = 3, 3, 2, act
    ticks = int(round(seconds / TICK))
    while lf.t < ticks:
        lf.step()
    jt = int(round(p.get("judge", seconds) / TICK))
    t0 = ticks - jt                                     # judged: the last `judge` s
    meals = [(t - t0, c) for t, c in lf.meals if t >= t0]
    mv = None if lf.moving is None else max(0, lf.moving - t0)
    l = Lived(thirds(meals, mv, jt, poison))
    l.power, l.substrate = 3.7e-9, "silicon"
    l.firings = SPAN * sum(1 for t, _ in lf.firings if t >= t0) / (jt * TICK)
    seg = int(round(p.get("seg", 1000.0) / TICK))
    l.curve = [(sum(1 for t, c in lf.meals if a <= t < a + seg and c != poison),
                sum(1 for t, c in lf.meals if a <= t < a + seg and c == poison)) for a in range(0, ticks, seg)]
    l.extra = getattr(lf.brain, "extra", 0)
    if arm == "trick":
        b = lf.brain
        l.det = (b.a, b.b, b.lag, b.act, b.w.copy())
        if f is not None:
            thr = {m: t for t, m in lf.motor.items()}
            l.weak = int(f[thr[0]] > f[thr[1]])         # the motor whose thruster is weaker
            l.ratio = max(f[thr[0]], f[thr[1]]) / min(f[thr[0]], f[thr[1]])
    return l


def lives(arm, p, spread, seeds, seconds, workers=None):
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(workers) as ex:
        return list(ex.map(life, [(arm, p, spread, s, seconds, c) for s in seeds for c in ("red", "blue")]))


def grown(L, thresh=0.05):
    """Of detectors grown (w above thresh), the share beating the weaker thruster's motor; and how many per life."""
    tot = weak = 0
    for l in L:
        a, b, lag, act, w = l.det
        g = w > thresh
        tot += int(g.sum())
        weak += int((act[g] == l.weak).sum())
    return weak / max(tot, 1), tot / len(L)


if __name__ == "__main__":
    from minimal.spec import summary
    from discrete.poison import show
    arm = sys.argv[1]
    args = [a for a in sys.argv[2:] if "=" not in a]
    lo, hi = (int(x) for x in (args[0] if args else "50000:50032").split(":"))
    kw = {k: float(v) for k, v in (a.split("=") for a in sys.argv[2:] if "=" in a)}
    seconds = kw.pop("seconds", 10000.0)
    p, spread = M.from_bench()
    L = lives(arm, dict(p, **kw), spread, range(lo, hi), seconds)
    tag = f"t2_{arm}_{int(seconds)}" + "".join(f"_{k}{v:g}" for k, v in sorted(kw.items())) + f"_{lo}-{hi - lo}"
    extra = f"extra beats per 10 s {np.mean([l.extra for l in L]) * 10 / seconds:.1f}"
    if arm == "trick" and kw.get("body", 1):
        sh, n = grown(L)
        extra += f"  grown {n:.1f}/life, on the weak motor {sh:.0%}"
        if kw.get("planted", 0) > 0 and kw.get("n", 200) > 1:
            w0, w1 = np.array([l.det[4][0] for l in L]), np.array([l.det[4][1] for l in L])
            extra += (f"\n  planted: right w {np.median(w0):+.3f} (above wrong in {np.mean(w0 > w1):.0%}),"
                      f" wrong w {np.median(w1):+.3f}; right w by body ratio corr {np.corrcoef([l.ratio for l in L], w0)[0, 1]:+.2f}")
    c = np.array([l.curve for l in L]).sum(0)
    print(show(tag, summary(L)), extra, flush=True)
    print("  curve food:poison per seg", " ".join(f"{a / max(b, 1):.1f}" for a, b in c), flush=True)
    print("  food per seg per life", " ".join(f"{a / len(L):.0f}" for a, b in c), flush=True)
    pickle.dump(L, open(f"/home/pilgrim/git/simple-learner/"
                        f"lab/v/{tag}.lives", "wb"))

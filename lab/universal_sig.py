"""universal_sig.py: H1's premise (STORIES.md; discrete/NOTEBOOK.md, D29). Do the worlds leave different signatures in the base circuit's own events?
Per world: vouched bads and goods per 10 s, bads soon (< 1.2 s) as a share, flips per 10 s, the share of flips contradicted by the next vouched taste,
the goods before a flip, the bads in a 10 s leaky tally (its 95th percentile), meals per 32 s (5th percentile; the mean)."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from creature import Life
import table as T
from table import Circuit, TICK


class Sig(Circuit):
    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.vb = self.vg = self.soon = self.bounced = self.conf = 0
        self.watch, self.run_g, self.runs, self.at = False, 0, [], -1e9
        self.F, self.Fs, self.m, self.ms = 0.0, [], 0.0, []

    def taste(self, value, at):
        gap, self.at = self.t - self.at, self.t
        if value > 0:
            self.m += 1
        if self.vouched():
            if value < 0:
                self.vb += 1
                self.soon += gap < 1.2
                self.F += 1
            else:
                self.vg += 1
                self.run_g += 1
            if self.watch:
                self.bounced += value < 0
                self.conf += value > 0
                self.watch = False
        n = len(self.flips)
        super().taste(value, at)
        if len(self.flips) > n:
            self.watch = True
            self.runs.append(self.run_g)
            self.run_g = 0

    def step(self):
        self.F *= 1 - TICK / 10.0
        self.m *= 1 - TICK / 32.0
        if int(self.t / TICK) % 200 == 0:
            self.Fs.append(self.F)
            self.ms.append(self.m)
        return super().step()


T.ARMS["sig"] = Sig


def one(job):
    w, seed, first, secs = job
    q = T.numbers(seed, {})
    R = T.WORLDS[w](first)
    lf = Life(seed, first, brain=lambda s: Sig(s, q))
    b = lf.brain
    R.setup(lf, seed)
    if hasattr(R, "taste"):
        inner = b.taste
        b.taste = lambda v, at: inner(R.taste(v), at)
    done = 0
    while lf.t < int(secs / TICK):
        t = lf.t * TICK
        lf.poison, R.now = R.poison(t), t
        R.tick(lf, t)
        lf.step()
        while done < len(lf.meals):
            R.ate(lf.meals[done][1])
            done += 1
    b.__dict__.pop("taste", None)
    b.__dict__.pop("stimulate", None)
    return b


def row(w, secs=100.0):
    with ProcessPoolExecutor(8) as ex:
        B = list(ex.map(one, [(w, s, c, secs) for s in T.TRAIN for c in T.COL]))
    k = 10.0 / secs
    vb, vg = np.mean([b.vb for b in B]) * k, np.mean([b.vg for b in B]) * k
    fl = sum(len(b.flips) for b in B)
    runs = [r for b in B for r in b.runs]
    print(f"{w:10} vouched bad {vb:5.2f} good {vg:5.2f}  soon share {sum(b.soon for b in B) / max(sum(b.vb for b in B), 1):.2f}  flips {fl / len(B) * k:5.2f}  "
          f"contradicted {sum(b.bounced for b in B) / max(sum(b.bounced + b.conf for b in B), 1):.2f}  goods before a flip median {np.median(runs) if runs else 0:.0f}, 90% {np.percentile(runs, 90) if runs else 0:.0f}  "
          f"F 50%/95% {np.percentile([f for b in B for f in b.Fs], 50):.1f}/{np.percentile([f for b in B for f in b.Fs], 95):.1f}  meals/32 s 5%/mean {np.percentile([m for b in B for m in b.ms[10:]], 5):.0f}/{np.mean([m for b in B for m in b.ms[10:]]):.0f}", flush=True)


if __name__ == "__main__":
    for w in ("plain", "swap10", "alternate", "pattern", "digest", "unreliable", "patchy", "weak", "noisy"):
        row(w)
    for w in ("thrusters", "ageing"):
        row(w, 400.0)

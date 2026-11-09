"""stageR2_trace.py: why random rivals lose to the written bank at 100 s (lab/v/stageR2.log), main session, 2026-11-07.

While the creature follows a rival (act != 0), on each taste: was the rival's colour right (the taste good), and would the default's colour
have been right? If the followed rivals are right less often than the default would have been, they were adopted on evidence that didn't
predict their later worth. Also: how much of the life is spent following a rival, and the E it had when adopted. Seeds 80100-80119 (the run's
own first 20), K = 100 with the Occam bar, as R2 ran them; the written bank beside it. Uncompiled path, so the trace can see every taste.

    .venv/bin/python lab/stageR2_trace.py g227 g361 g170 g244 plain"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import numpy as np
import stage3_random as R
import rivals as RV


class Traced(RV.RV):
    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.log = []

    def taste(self, value, at):
        if value and not self.open and self.act:
            truth = self.food if value > 0 else 1 - self.food
            self.log.append((self.t, self.act, value > 0, self.pred(self.bank[0]) == truth))
        super().taste(value, at)


def one(job):
    from stage2_lang import arms as S
    from stage2_lang.sim import WLife
    text, kw, seed, first = job
    WLife.seconds = True
    q = __import__("table").numbers(seed, {**S.V7, **kw})
    lf = WLife(seed, first, (lambda s: Traced(s, q)), S.world_of(text), seconds=True)
    l = S.live(lf, 100.0)
    b = lf.brain
    return b.log, [(t, i, b.bank[i]["ctx"].desc()) for t, i in b.picks]


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    W, _, _ = R.worlds()
    for n in sys.argv[1:]:
        text = R.PLAIN if n == "plain" else W[n][0]
        for name, kw in (("written", {}), ("K100", {"rivals": ("random", 100), **RV.occam(100)})):
            jobs = [(text, kw, s, c) for s in range(80100, 80120) for c in R.COL]
            with ProcessPoolExecutor(2, initializer=R._init, initargs=(0.00125, False)) as ex:
                out = list(ex.map(one, jobs))
            L = [x for o in out for x in o[0]]
            n_pick = sum(1 for o in out for _, i, _ in o[1] if i)
            if not L:
                print(f"{n:5s} {name:8s} never follows a rival ({n_pick} adoptions)")
                continue
            a = np.array([x[2] for x in L], float)
            d = np.array([x[3] for x in L], float)
            first10 = [x for o in out for k, x in enumerate(o[0]) if k < 10]
            print(f"{n:5s} {name:8s} adoptions {n_pick} in {len(out)} lives; tastes while following {len(L)}: the rival right {a.mean():.2f}, "
                  f"the default would have been {d.mean():.2f}; in the first 10 after adoption {np.mean([x[2] for x in first10]):.2f} vs "
                  f"{np.mean([x[3] for x in first10]):.2f}", flush=True)

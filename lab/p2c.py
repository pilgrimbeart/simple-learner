"""p2c.py: P2, route C (the user, 2026-11-11: try all three routes, then abstract): play that feeds a model of mixed commands, and the
steady-view goal choosing the drive. No formula from a measurement to a motor gain.

The slow bank: 40 rhythm units drawn once (evolution's draw), each a square wave of period 8 to 60 s (log-uniform), duty .3 to .7, rate
5 to 30 beats a second, each part's weight on each motor 0 with chance a third, else uniform 0 to 1; turns of 20 s in a shuffled cycle;
400 s of play. So a mixed command holds for seconds, long enough for the view to come round.

Each mix played (a unit's part: rates r0, r1), its own record clocked by its own beats of either motor, each stretch separately, pooled:
how many of its beats until the view comes round (the comb's best and its margin, D44, D48). A mix that turns the view slowly has a
long period. The steady-view goal (inherited: when approaching, the view should stay still): the drive is the mix that turns the view
least. Each mix with both motors is a point: the knob it would be as the drive (its rate ratio, in the brain's own terms: knowledge of
its own settings, not the body's) against its measured turning a beat; the minimum of that curve is found by fitting a V (weighted L1),
generic optimisation of a one-dimensional function from noisy samples; taste tries the minimum and that +- .3, 30 s each, from the first
taste. (First version ranked mixes by margin: traced, mixed records give the right period with small margins, so it threw out good
evidence and kept noise.)

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/p2c.py [PAIRS] [s96000]"""
import math
import pickle
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np

import play2 as P2
import play3 as P3
import play4 as P4
import stage3_random as R

K = 128
MIN_PTS_BEATS = 80                              # a mix's record counts once it holds this many beats


def draw_slow(n):
    rng = np.random.default_rng(2_000_029 + n)
    w = lambda: 0.0 if rng.random() < 1 / 3 else float(rng.random())
    return (float(np.exp(rng.uniform(math.log(8.0), math.log(60.0)))), float(rng.uniform(0.3, 0.7)),
            float(np.exp(rng.uniform(math.log(5.0), math.log(30.0)))), (w(), w()), (w(), w()))


SLOW = [draw_slow(i) for i in range(len(P2.UNITS))]


def mix_record(beats, pulses, stretches):
    """(log period in beats, margin, beats) of a mix's own record over its stretches, or None if too few beats."""
    tot, nb = np.zeros(K), 0
    for t0, t1 in stretches:
        bt = beats[(beats >= t0) & (beats < t1)]
        if len(bt) < 12:
            continue
        nb += len(bt)
        c = (np.diff(np.searchsorted(pulses, bt)) > 0).astype(float)
        q = c.mean()
        for k in range(1, min(K, len(c) - 1) + 1):
            e = (len(c) - k) * q * q
            tot[k - 1] += ((c[k:] * c[:-k]).sum() - e) / math.sqrt(e + 1)
    if nb < 24:
        return None
    best, rival, margin = P3._top2(tot, np.arange(1.0, K + 1))
    return best, margin, nb


class SlowPlay(P3.Play3):
    def __init__(self, seed, p):
        super().__init__(seed, {**p, "bore": "certain", "playfor": 400.0, "turn": 20.0})
        self.fns = [_fn(u) for u in SLOW]
        self.link = p["link"]

    def finish_play(self):
        self._close()
        pulses = np.sort(np.array([t for t, _ in self.pulses], float))
        beats = np.array(sorted(t for t, _ in self.beat_log))
        if self.link == "partners":                     # our formula on the same play, for reference
            lN = P3.beat_runs(sorted(self.beat_log), pulses)
            self.end_lN = lN
            if None not in lN:
                self.est = lN[0][0] - lN[1][0]
                self.set_balance(self.est)
            return
        pts = []                                        # (knob this mix would be as the drive, turning a beat, weight)
        for (u, r0, r1), st in self.stretches.items():
            if r0 <= 0 or r1 <= 0:
                continue
            m = mix_record(beats, pulses, st)
            if m is None or m[2] < MIN_PTS_BEATS:
                continue
            best, margin, nb = m
            pts.append((-math.log(r1 / r0), math.exp(-best), nb))
        self.mixes = pts
        if len(pts) < 3:
            return
        x, y, w = (np.array(v, float) for v in zip(*pts))
        best = None                                     # the minimum of turning against the knob: a V fitted by weighted L1
        for x0 in np.linspace(-2.0, 2.0, 401):
            g = np.abs(x - x0)
            for c in np.linspace(0, y.min(), 5):
                sl = np.median((y - c)[g > 0.05] / g[g > 0.05]) if (g > 0.05).any() else 0.0
                err = float((w * np.abs(c + max(sl, 0.0) * g - y)).sum())
                if best is None or err < best[0]:
                    best = (err, x0)
        c0 = best[1]
        cands = [c0, c0 - 0.3, c0 + 0.3]
        self.est = c0
        self.set_balance(c0)
        self.trials, self.trial_end = cands, None


def _fn(u):
    import play1 as P1
    return P1.unit_fn(u)


def make(arm, seed, first):
    from stage2_lang import arms as S
    from stage2_lang.sim import WLife
    if arm == "forage":
        return P3.make("forage", seed, first)
    w = S.world_of(P3.WORLD)
    return WLife(seed, first, (lambda s: SlowPlay(s, {"dt": WLife.dt, "link": arm, "stat": "beats"})), w, seconds=True)


def job(j):
    from stage2_lang import arms as S
    arm, seed, first = j
    lf = make(arm, seed, first)
    k = {lf.wire_m[th]: g for th, g in ((0, lf.v_a), (1, lf.v_b))}
    S.live(lf, P4.SECS)
    q, b = lf.v_q, lf.brain
    win = []
    for a, z in P4.WINDOWS:
        lo, hi = (q + a) / lf.dt, (q + z) / lf.dt
        good = sum(am for t, bad, am in lf.scored if lo <= t < hi and not bad)
        badm = sum(am for t, bad, am in lf.scored if lo <= t < hi and bad)
        win.append((good - 2.0 * badm) / (z - a) * 10)
    return dict(arm=arm, seed=seed, win=win, right=math.log(k[1] / k[0]), est=getattr(b, "est", None),
                nmix=len(getattr(b, "mixes", []) or []), trials=getattr(b, "tally", {}))


ARMS = ("forage", "partners", "steady")


def report(rows):
    n = len(rows) // (2 * len(ARMS))
    I = R.boot(n)
    base = np.array([r["win"] for r in rows if r["arm"] == "forage"])
    print("arm      | gain from onset vs forage [95%]: 0-100 s; 100-300 s | knob error: median, within .2 | steady mixes counted")
    for a in ARMS:
        rs = [r for r in rows if r["arm"] == a]
        W = np.array([r["win"] for r in rs])
        line = f"{a:8s}"
        for i in range(2):
            d = W[I, i].mean(1) - base[I, i].mean(1)
            line += f" | {W[:, i].mean() - base[:, i].mean():+.2f} [{np.percentile(d, 2.5):+.2f},{np.percentile(d, 97.5):+.2f}]"
        e = [abs(r["est"] - r["right"]) for r in rs if r["est"] is not None]
        line += f" | {np.median(e):.2f}, {np.mean(np.array(e) < .2):.0%} (of {len(e)})" if e else " |"
        line += f" | {np.median([r['nmix'] for r in rs]):.0f}"
        print(line, flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    n = int(a[0]) if a and a[0].isdigit() else 20
    s0 = next((int(x[1:]) for x in a if x.startswith("s") and x[1:].isdigit()), 92000)
    out = f"/home/pilgrim/git/simple-learner/lab/v/p2c_{n}_s{s0}.pkl"
    if "report" in a:
        report(pickle.load(open(out, "rb")))
        sys.exit()
    import ledger
    ledger.start()
    jobs = [(arm, s, c) for arm in ARMS for s in range(s0, s0 + n) for c in ("red", "blue")]
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        rows = list(ex.map(job, jobs, chunksize=2))
    pickle.dump(rows, open(out, "wb"))
    report(rows)

"""kick_timing.py: is precise timing of the thrusters' kicks worth learning? (the user, 2026-11-11: each beat is a large kick, so precise
control of timing might be quite beneficial.) A yardstick question before any mechanism: the told brain (its thrusters' strengths known)
with two ways of making its drive straight.

  told       the balance knob: each motor its own rate (D20's drive, its oscillators started in step): unpaired kicks may bunch.
  toldtime   equal rates, both motors beating together by default; a scheduler keeps the heading's accumulated turn (in units of each
             thruster's kick, known: a yardstick's privilege) within half a kick of straight by dropping one motor's beat of a pair
             whenever the turn would pass that (error diffusion, as sigma-delta modulation or dithering).
Bodies: lopsided (each thruster a half to twice) and plain. play4's frame (a quiet spell, then the challenge), scored from onset.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/kick_timing.py [PAIRS]"""
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


def scheduled(cls):
    """Wraps the starting brain: when both motors beat within a tick (a drive's pair), keep the heading's accumulated turn within half
    a kick by dropping one beat of the pair when needed. turn[m]: the signed turn of motor m's kick (set from outside: told)."""
    class Sched(cls):
        turn = (1.0, -1.0)

        def step(self):
            out = super().step()
            beats = list(getattr(self, "beats", None) or [])
            if not hasattr(self, "acc"):
                self.acc = 0.0
            m0 = [b for b in beats if b[0] == 0]
            m1 = [b for b in beats if b[0] == 1]
            if m0 and m1:                               # a pair (or pairs) this tick: schedule each
                keep = []
                for b0, b1 in zip(m0, m1):
                    opts = [(abs(self.acc + self.turn[0] + self.turn[1]), 0, [b0, b1], self.turn[0] + self.turn[1]),
                            (abs(self.acc + self.turn[0]), 1, [b0], self.turn[0]),
                            (abs(self.acc + self.turn[1]), 1, [b1], self.turn[1])]
                    _, _, kb, dt = min(opts, key=lambda o: (o[0], o[1]))    # the heading closest to straight; both on a tie
                    keep += kb
                    self.acc += dt
                keep += m0[len(m1):] + m1[len(m0):]
                self.beats = sorted(keep, key=lambda b: b[1])
                return [m for m, _ in self.beats]
            if m0 or m1:
                self.acc = 0.0                          # a scan or a lone beat: the drive's heading starts afresh
                                                        # (a tick with no beat leaves the heading's account as it was)
            return out
    return Sched


def make(arm, body, seed, first):
    from stage2_lang import arms as S
    from stage2_lang.sim import WLife
    from stage2_lang.seconds import seconds_cls
    import table as T
    text = P3.WORLD if body == "lopsided" else C.PLAIN
    w = S.world_of(text)
    q = T.numbers(seed, {"sync": 1})
    cls = seconds_cls(T.Circuit)
    if arm == "toldtime":
        cls = scheduled(cls)
    lf = WLife(seed, first, (lambda s: cls(s, q)), w, seconds=True)
    if body == "lopsided":
        k = {lf.wire_m[th]: g for th, g in ((0, lf.v_a), (1, lf.v_b))}
        sign = {lf.wire_m[th]: (-1.0 if th == 0 else 1.0) for th in (0, 1)}    # the left thruster (0) turns it right
        if arm == "told":
            right = math.log(k[1] / k[0])
            lf.brain.p["g0"], lf.brain.p["g1"] = math.exp(right / 2), math.exp(-right / 2)
        if arm == "toldtime":
            lf.brain.turn = (sign[0] * k[0], sign[1] * k[1])
    elif arm == "toldtime":
        sign = {lf.wire_m[th]: (-1.0 if th == 0 else 1.0) for th in (0, 1)}
        lf.brain.turn = (sign[0], sign[1])
    return lf


def job(j):
    from stage2_lang import arms as S
    arm, body, seed, first = j
    lf = make(arm, body, seed, first)
    S.live(lf, P4.SECS)
    q = lf.v_q
    win = []
    for a, z in P4.WINDOWS:
        lo, hi = (q + a) / lf.dt, (q + z) / lf.dt
        good = sum(am for t, bad, am in lf.scored if lo <= t < hi and not bad)
        badm = sum(am for t, bad, am in lf.scored if lo <= t < hi and bad)
        win.append((good - 2.0 * badm) / (z - a) * 10)
    return dict(arm=arm, body=body, seed=seed, win=win)


if __name__ == "__main__":
    import ledger
    ledger.start()
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    jobs = [(arm, body, s, c) for body in ("lopsided", "plain") for arm in ("forage", "told", "toldtime")
            for s in range(98000, 98000 + n) for c in ("red", "blue")]
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        rows = list(ex.map(job, jobs, chunksize=2))
    pickle.dump(rows, open(f"/home/pilgrim/git/simple-learner/lab/v/kick_timing_{n}.pkl", "wb"))
    I = R.boot(n)
    for body in ("lopsided", "plain"):
        W = {a: np.array([r["win"] for r in rows if r["body"] == body and r["arm"] == a]) for a in ("forage", "told", "toldtime")}
        print(f"== {body}: gain from onset, a 10 s [95%]")
        for a in W:
            print(f"  {a:9s} " + " | ".join(f"{W[a][:, i].mean():+.2f} [{np.percentile(W[a][I, i].mean(1), 2.5):+.2f},{np.percentile(W[a][I, i].mean(1), 97.5):+.2f}]" for i in range(2)))
        for i in range(2):
            d = W["toldtime"][I, i].mean(1) - W["told"][I, i].mean(1)
            print(f"  toldtime - told, window {i}: {W['toldtime'][:, i].mean() - W['told'][:, i].mean():+.2f} [{np.percentile(d, 2.5):+.2f},{np.percentile(d, 97.5):+.2f}]")

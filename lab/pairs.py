"""pairs.py: the paired-blocks world (PROGRAMME.md, Blocks in pairs), first step: is there a rung here? Main session, 2026-11-10.
Predictions first: lab/v/pairs_predictions.md.

Each red block has a blue partner at GAP (centre to centre), in a direction drawn afresh; when either is eaten the eaten one reappears
somewhere new and its partner moves beside it, so there are always 18 pairs. Nothing else changes: body, eyes, taste, a block's worth.
Arms: circuit (the starting brain, which learns the colour) and vtold (told the colour: the same driving, immune to mislearning).

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/pairs.py [PAIRS] [GAPS in mm, e.g. 2,3,4,6,10]
    ... lab/pairs.py careful [PAIRS] [GAPS]            # the yardstick: a careful driver, told the colour"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import ladders as L
import stage3_random as R

SEEDS0 = 85000                                  # development seeds, fresh


def world(gap_mm):
    if not gap_mm:
        return L.PLAIN
    g = gap_mm / 1000
    return ("(world (meta (link L3) (q D) (cap Ladder) (group pairs)) (let a 0) (let px 0) (let py 0) (on birth (each b (respawn b)))"
            " (on respawn (until (and (> (dist nx ny) (+ (* 3 EAT) BODY)) (> (dist px py) (+ (* 3 EAT) BODY))) 100"
            f" (set nx (uniform 0 WORLD)) (set ny (uniform 0 WORLD)) (set a (uniform 0 TWOPI)) (set px (+ nx (* {g} (cos a)))) (set py (+ ny (* {g} (sin a)))))"
            " (bset (mod (+ block BLOCKS) (* 2 BLOCKS)) px py)))")


def careful_cls():
    """The yardstick: the starting brain with two changes to how it drives, by hand. (1) A poison pulse ends a drive only if the poison
    eye is at least `ratio` as busy as the food eye (each a leaky count, `win` s): a poison block the mouth would touch covers more than
    half the corridor, one merely beside the path less. (2) A good taste ends the drive (`stop`), since the partner may lie just behind."""
    import math
    import table as T

    class Careful(T.Circuit):
        def __init__(self, seed, p):
            super().__init__(seed, p)
            self.cf = self.cp = 0.0
            self.tl = 0.0

        def step(self):
            p = self.p
            k = math.exp(-max(self.t - self.tl, 0.0) / p.get("win", 0.1))
            self.tl = self.t
            self.cf = self.cf * k + self.seen[self.food]
            self.cp = self.cp * k + self.seen[1 - self.food]
            if self.seen[1 - self.food] and self.cp < p.get("ratio", 0.5) * self.cf:
                self.seen[1 - self.food] = 0            # beside the path: not heeded
            return super().step()

        def taste(self, value, at):
            super().taste(value, at)
            if value > 0 and self.p.get("stop", 1):
                self.last_drive = -1e9
    return Careful


def looker_cls():
    """The manoeuvre (D41): look before you leap. A poison pulse during a drive doesn't end it; the brain stands still for `look` s
    and counts both eyes. If the poison eye was under `ratio` as busy as the food eye (a partner beside the path or hidden behind the
    food covers less of the corridor than one in the way), it commits: drives on for up to `commit` s heeding no poison pulse, and a
    good taste ends the drive (the partner may lie just behind). Otherwise it declines: both eyes unheeded for `shy` s, so the scan
    turns it away."""
    import table as T

    class Looker(T.Circuit):
        def __init__(self, seed, p):
            super().__init__(seed, p)
            self.mode, self.until, self.nf, self.np_ = "", 0.0, 0, 0
            self.looks = self.commits = 0

        def step(self):
            p = self.p
            f, o = self.food, 1 - self.food
            still = False
            if self.mode == "look":
                self.nf += self.seen[f]
                self.np_ += self.seen[o]
                self.seen = [0, 0]
                still = True
                if self.t >= self.until:
                    if self.nf and self.np_ < p.get("ratio", 0.5) * self.nf:
                        self.mode, self.until = "commit", self.t + p.get("commit", 0.5)
                        self.last_drive = self.last_food = self.t
                        self.commits += 1
                    else:
                        self.mode, self.until = "shy", self.t + p.get("shy", 0.4)
            elif self.mode == "commit":
                self.seen[o] = 0
                if self.t >= self.until:
                    self.mode = ""
            elif self.mode == "shy":
                self.seen = [0, 0]
                if self.t >= self.until:
                    self.mode = ""
            elif self.seen[o] and self.t - self.last_drive < p["hold"]:      # poison seen while driving at food: stop and look
                self.mode, self.until, self.nf, self.np_ = "look", self.t + p.get("look", 0.3), self.seen[f], self.seen[o]
                self.seen = [0, 0]
                self.looks += 1
                still = True
            out = super().step()
            return [] if still else out

        def taste(self, value, at):
            super().taste(value, at)
            if value > 0 and self.mode == "commit":
                self.last_drive, self.mode = -1e9, ""
    return Looker


_C = {}


def job(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    text, arm, seed, first, secs = j
    if isinstance(arm, tuple):                          # ("careful", told, {numbers})
        from stage2_lang.sim import WLife
        from stage2_lang.seconds import seconds_cls
        import table as T
        if arm[0] not in _C:
            _C[arm[0]] = seconds_cls(careful_cls() if arm[0] == "careful" else looker_cls())
        q = T.numbers(seed, {})
        q.update(arm[2])
        lf = WLife(seed, first, (lambda sd: _C[arm[0]](sd, q)), S.world_of(text), seconds=True)
        if arm[1]:
            def tell(W):
                tp = W.told_now
                if tp is not None and tp >= 0:
                    W.brain.food = W.wire_s[1 - tp]
            lf.tell = tell
        l = S.live(lf, secs)
        g = [a - COST * b for a, b, _ in l]
        sp = spent(l)
        return (sum(g), sp, g[2], sp * l[2][2] / sum(t for _, _, t in l), sum(a for a, _, _ in l), sum(b for _, b, _ in l))
    l = S.live(S.make(S.world_of(text), arm, seed, first), secs)
    g = [a - COST * b for a, b, _ in l]
    sp = spent(l)
    return (sum(g), sp, g[2], sp * l[2][2] / sum(t for _, _, t in l), sum(a for a, _, _ in l), sum(b for _, b, _ in l))


def run(pairs=5, gaps=(0, 10, 6, 4, 3, 2), secs=100, dt=2.5, workers=7):
    I = R.boot(pairs)
    seeds = range(SEEDS0, SEEDS0 + pairs)
    print(f"== pairs: {pairs} pairs of lives, {secs} s, {dt} ms, seeds {SEEDS0}+; efficiency [95%], food and poison meals a life", flush=True)
    with ProcessPoolExecutor(workers, initializer=R._init, initargs=(dt / 1000, False)) as ex:
        for gap in gaps:
            line = f" gap {gap:4.1f} mm |" if gap else " plain       |"
            for arm in ("circuit", "vtold"):
                res = list(ex.map(job, [(world(gap), arm, s, c, float(secs)) for s in seeds for c in L.COL]))
                e = L.scored(res, secs, I)
                lo, hi = R.ci(e[1])
                line += f" {arm} {e[0]:+.2f} [{lo:+.2f},{hi:+.2f}] food {np.mean([x[4] for x in res]):5.1f} poison {np.mean([x[5] for x in res]):5.1f} |"
            print(line, flush=True)


def careful(pairs=5, gaps=(0, 2), secs=100, dt=2.5, workers=7, told=True):
    """The careful driver, told the colour (so only its driving is judged), over a few settings; beside the told arm on the same lives."""
    I = R.boot(pairs)
    seeds = range(SEEDS0, SEEDS0 + pairs)
    sets = [dict(ratio=r, stop=st) for st in (0, 1) for r in (0.0, 0.3, 0.6, 1.0)]     # ratio 0, stop 0 is the starting brain's driving
    print(f"== careful driver{', told the colour' if told else ', learning the colour'}: {pairs} pairs, {secs} s, seeds {SEEDS0}+; efficiency [95%], food, poison", flush=True)
    with ProcessPoolExecutor(workers, initializer=R._init, initargs=(dt / 1000, False)) as ex:
        for gap in gaps:
            print(f" gap {gap:4.1f} mm:" if gap else " plain:", flush=True)
            arms = [("vtold" if told else "circuit", "the told arm" if told else "the starting brain")] + [(("careful", told, q), f"ratio {q['ratio']:.1f} stop {q['stop']}") for q in sets]
            for arm, name in arms:
                res = list(ex.map(job, [(world(gap), arm, s, c, float(secs)) for s in seeds for c in L.COL]))
                e = L.scored(res, secs, I)
                lo, hi = R.ci(e[1])
                print(f"   {name:18s} {e[0]:+.2f} [{lo:+.2f},{hi:+.2f}] food {np.mean([x[4] for x in res]):5.1f} poison {np.mean([x[5] for x in res]):5.1f}", flush=True)


def looker(pairs=5, gaps=(0, 2), secs=100, dt=2.5, workers=7, sets=None):
    I = R.boot(pairs)
    seeds = range(SEEDS0, SEEDS0 + pairs)
    sets = sets or [dict(look=lk, ratio=r) for lk in (0.15, 0.3) for r in (0.4, 0.7)]
    print(f"== look before you leap, told the colour: {pairs} pairs, {secs} s, seeds {SEEDS0}+; efficiency [95%], food, poison", flush=True)
    with ProcessPoolExecutor(workers, initializer=R._init, initargs=(dt / 1000, False)) as ex:
        for gap in gaps:
            print(f" gap {gap:4.1f} mm:" if gap else " plain:", flush=True)
            for arm, name in [("vtold", "the told arm")] + [(("looker", True, q), " ".join(f"{k} {v}" for k, v in q.items())) for q in sets]:
                res = list(ex.map(job, [(world(gap), arm, s, c, float(secs)) for s in seeds for c in L.COL]))
                e = L.scored(res, secs, I)
                lo, hi = R.ci(e[1])
                print(f"   {name:22s} {e[0]:+.2f} [{lo:+.2f},{hi:+.2f}] food {np.mean([x[4] for x in res]):5.1f} poison {np.mean([x[5] for x in res]):5.1f}", flush=True)


if __name__ == "__main__":
    import ledger
    ledger.start()
    a = sys.argv[1:]
    if a and a[0] == "looker":
        looker(int(a[1]) if len(a) > 1 else 5, tuple(float(x) for x in a[2].split(",")) if len(a) > 2 else (0, 2))
        sys.exit()
    if a and a[0] in ("careful", "careful-learning"):
        careful(int(a[1]) if len(a) > 1 else 5, tuple(float(x) for x in a[2].split(",")) if len(a) > 2 else (0, 2), told=a[0] == "careful")
        sys.exit()
    run(int(a[0]) if a else 5, tuple(float(x) for x in a[1].split(",")) if len(a) > 1 else (0, 10, 6, 4, 3, 2))

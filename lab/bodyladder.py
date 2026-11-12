"""bodyladder.py: the lopsided body as the acting ladder (the user, 2026-11-10; D42). First: which of the body's numbers, drawn afresh
each life, cost the starting brain anything? Predictions first: lab/v/body_predictions.md.

Worlds (each number drawn log-uniform between a half and twice, at birth, from the world's own stream):
  thr    each thruster's strength, separately (the lopsided body: lab/stage2_lang/worlds.py, thrusters)
  str    both thrusters' strength, together
  eyes   both eyes' sensitivity, together          eye1   one eye's sensitivity
  drag   the body's drag, a half or twice (two fixed worlds, averaged: a constant can't be drawn in the language)
Arms: circuit (the starting brain), toldbody (the starting brain told its thrusters' balance: each motor's rate set for a straight
drive, as lab/table.py's Thrusters told), bank (which holds D19's balance learner).

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/bodyladder.py which [PAIRS] [SECONDS]"""
import math
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import ladders as L
import stage3_random as R

SEEDS0 = 86000                                  # development seeds, fresh
D = "(pow 2 (uniform -1 1))"
M = "(meta (link L1) (q H) (cap Ladder) (group body))"
WORLDS = {
    "plain": [L.PLAIN],
    "thr": [f"(world {M} (let a {D}) (let b {D}) (on fire (set gain (if (= thruster 0) a b))))"],
    "str": [f"(world {M} (let a {D}) (on fire (set gain a)))"],
    "eyes": [f"(world {M} (let e {D}) (on see (set seen (* seen e))))"],
    "eye1": [f"(world {M} (let e {D}) (let k (int 2)) (on see (if (= colour k) (set seen (* seen e)))))"],
    "drag": [f"(world {M} (const DRAG (* 0.5 DRAG)))", f"(world {M} (const DRAG (* 2 DRAG)))"],
    # drag drawn per life, written as an extra fading of speed and spin each tick (a constant can't be drawn): check `dragx` against `drag`
    "dragx": [f"(world {M} (let k (exp (* (- 1 {f}) DRAG TICK))) (on move (set vx (* vx k)) (set vy (* vy k)) (set spin (* spin k))))" for f in (0.5, 2)],
    "dragd": [f"(world {M} (let d {D}) (on move (set vx (* vx (exp (* (- 1 d) DRAG TICK)))) (set vy (* vy (exp (* (- 1 d) DRAG TICK)))) (set spin (* spin (exp (* (- 1 d) DRAG TICK))))))"],
    "both": [f"(world {M} (let a {D}) (let b {D}) (let d {D}) (on fire (set gain (if (= thruster 0) a b)))"
             " (on move (set vx (* vx (exp (* (- 1 d) DRAG TICK)))) (set vy (* vy (exp (* (- 1 d) DRAG TICK)))) (set spin (* spin (exp (* (- 1 d) DRAG TICK))))))"],
}


def make(text, arm, seed, first):
    from stage2_lang import arms as S
    w = S.world_of(text)
    if arm != "toldbody":
        return S.make(w, arm, seed, first)
    from stage2_lang.sim import WLife
    from stage2_lang.seconds import seconds_cls
    import table as T
    q = T.numbers(seed, {"sync": 1})
    lf = WLife(seed, first, (lambda s: seconds_cls(T.Circuit)(s, q)), w, seconds=True)
    p = lf.brain.p
    if hasattr(lf, "v_a") and hasattr(lf, "v_b"):       # told its thrusters (a yardstick's privilege): motor m drives the thruster wired to it
        k = {lf.wire_m[th]: g for th, g in ((0, lf.v_a), (1, lf.v_b))}
        right = math.log(k[1] / k[0])
        from stage2_lang import sim
        if sim.WLife.muscle:                            # thrust isn't proportional to rate on the muscle-like body
            import sigmoid_body as SB
            right = SB.told_balance(k[0], k[1], p["drive"])
        p["g0"], p["g1"] = math.exp(right / 2), math.exp(-right / 2)
    if hasattr(lf, "v_d"):                              # told its drag: every rate scaled by it (the tempo)
        from stage2_lang import sim
        for r in ("scan", "drive", "run"):
            if sim.WLife.muscle:                        # thrust isn't proportional to rate: the factor that scales thrust by the drag
                import sigmoid_body as SB
                p[r] *= SB.told_tempo(lf.v_d, p[r])
            else:
                p[r] *= lf.v_d
    return lf


def job(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    text, arm, seed, first, secs = j
    l = S.live(make(text, arm, seed, first), secs)
    g = [a - COST * b for a, b, _ in l]
    sp = spent(l)
    return (sum(g), sp, g[2], sp * l[2][2] / sum(t for _, _, t in l), sum(a for a, _, _ in l), sum(b for _, b, _ in l))


def which(pairs=5, secs=300, dt=2.5, workers=7, worlds=None, arms=("circuit", "toldbody", "bank")):
    I = R.boot(pairs)
    seeds = range(SEEDS0, SEEDS0 + pairs)
    print(f"== which of the body's numbers matter: {pairs} pairs, {secs} s (judged on the last third), {dt} ms, seeds {SEEDS0}+; efficiency [95%]", flush=True)
    with ProcessPoolExecutor(workers, initializer=R._init, initargs=(dt / 1000, False)) as ex:
        for name in worlds or WORLDS:
            line = f" {name:6s}|"
            for arm in arms:
                if arm == "toldbody" and name not in ("thr", "dragd", "both"):
                    continue
                res = [list(ex.map(job, [(t, arm, s, c, float(secs)) for s in seeds for c in L.COL])) for t in WORLDS[name]]
                e = [L.scored(r, secs, I) for r in res]
                m, b = np.mean([x[0] for x in e]), np.mean([x[1] for x in e], axis=0)
                lo, hi = R.ci(b)
                line += f" {arm} {m:+.2f} [{lo:+.2f},{hi:+.2f}] |"
            print(line, flush=True)


if __name__ == "__main__":
    import ledger
    ledger.start()
    a = sys.argv[1:]
    if a[0] == "which":
        which(int(a[1]) if len(a) > 1 else 5, int(a[2]) if len(a) > 2 else 300, worlds=a[3].split(",") if len(a) > 3 else None)

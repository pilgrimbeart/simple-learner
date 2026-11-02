"""timing.py: the bound on timing (BOUNDS.md, Time; discrete/NOTEBOOK.md, D22). In B's lives (told the colour), at each
food pulse: what the brain itself could know (its pulses' exact times, its own motors' beats), and the truth it would
want: the offset across the corridor of the block that pulsed, signed towards the side motor 0 turns to (B scans on
motor 0, so its sweep turns that way; a life could learn the sign, since its wiring is fixed). How well do features
of the timing predict the offset? Cross-validated by life (a learner never sees the lives it is judged on).

    python timing.py [seeds=64]
"""
import sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import world
from units import TICK

GAP = 0.15                                               # s: pulses closer than this are one burst


def life(job):
    from creature import Life
    from discrete import model as M
    seed, poison, probe = job
    lf = Life(seed, poison, brain=lambda s: None)
    food = lf.sensor[next(c for c in lf.sensor if c != poison)]
    fk = world.COLOURS.index(next(c for c in lf.sensor if c != poison))
    p, sd = M.from_bench()
    q = M.drawn(p, sd, seed)
    q["V_H"] = 99.0
    br = M.Model(seed, q)
    br.food = food
    lf.brain = br
    s0 = 1.0 if lf.motor["right"] == 0 else -1.0         # the right thruster turns it left (+ across)
    pulses, beats, rows = [], [[], []], []
    pr = {"end": -1e9, "phase": 0.0, "next": 0}           # probe=(rate, s): on a food pulse, single beats alternating
    orig_stim, orig_step = br.stimulate, br.step

    def stim(sensor, at):
        orig_stim(sensor, at)
        if sensor != food:
            return
        b = lf.body
        t = lf.t * TICK + at
        head, f = b.head(), b.forward()
        n_ = np.array([-f[1], f[0]])
        d = np.array([b.wrap(x - head) for x in b.xy])
        along, off = d @ f, d @ n_
        m = np.flatnonzero((b.kind == fk) & (along > 0) & (along < world.RANGE) & (np.abs(off) < world.EAT + world.BLOCK))
        prev = pulses[-1] if pulses else -1e9
        if probe and t > pr["end"] + 1.0:               # (not again within 1 s of the last probe's end)
            pr["end"] = t + probe[1]
        pulses.append(t)
        if not len(m):
            return
        i = int(m[np.argmin(along[m])])
        ps = np.array(pulses)
        start = t
        for x in ps[::-1][1:]:                           # the burst's first pulse
            if start - x < GAP:
                start = x
            else:
                break
        bt = [np.array(beats[0]), np.array(beats[1])]
        cnt = lambda k, w: float(((bt[k] > t - w) & (bt[k] <= t)).sum()) if len(bt[k]) else 0.0
        since = lambda k: float((bt[k] >= start).sum()) if len(bt[k]) else 0.0
        mode = 2.0 if t < pr["end"] else float(lf.t * TICK - br.last_drive < br.p["hold"])
        last = lambda k: min(t - bt[k][-1], 1.0) if len(bt[k]) else 1.0
        rows.append([float(((ps > start - 1e-12)).sum()), t - start, min(t - prev, 1.0),
                     float((ps > t - 0.2).sum()), float((ps > t - 0.05).sum()),
                     cnt(0, 0.05), cnt(1, 0.05), cnt(0, 0.2), cnt(1, 0.2), since(0), since(1), mode, last(0), last(1), float(last(0) < last(1)),
                     s0 * off[i], along[i], seed])

    def step():
        out = orig_step()
        t = lf.t * TICK
        if t < pr["end"]:                               # probing: B's own beats withheld, its state still kept
            pr["phase"] += probe[0] * TICK
            k = int(pr["phase"]); pr["phase"] -= k
            out = []
            for _ in range(k):
                out.append(pr["next"]); pr["next"] = 1 - pr["next"]
        for k in out:
            beats[k].append(t)
        return out
    br.stimulate, br.step = stim, step
    while lf.t < 10000:
        lf.step()
    return rows


NAMES = ["pulses in burst", "since burst began", "since last pulse", "pulses in 0.2 s", "pulses in 0.05 s",
         "m0 beats 0.05 s", "m1 beats 0.05 s", "m0 beats 0.2 s", "m1 beats 0.2 s", "m0 since burst", "m1 since burst",
         "driving"]

if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    from sklearn.ensemble import HistGradientBoostingRegressor, HistGradientBoostingClassifier
    from sklearn.model_selection import GroupKFold, cross_val_predict
    kv = dict(a.split("=") for a in sys.argv[1:] if "=" in a)
    ns = int(kv.get("seeds", 64))
    probe = tuple(float(x) for x in kv["probe"].split(",")) if "probe" in kv else None
    with ProcessPoolExecutor(7) as ex:
        R = np.array([r for L in ex.map(life, [(s, c, probe) for s in range(50000, 50000 + ns) for c in ("red", "blue")]) for r in L])
    np.save(f"/home/pilgrim/git/simple-learner/lab/v/timing_{ns}_{kv.get('probe', 'none')}.npy", R)
    X, off, along, g = R[:, :15], R[:, 15], R[:, 16], R[:, 17]
    print(f"{len(R)} food pulses with the block in view, {ns} seeds x 2")
    cv = GroupKFold(5)
    for name, mask in (("all", np.ones(len(R), bool)), ("scanning", X[:, 11] == 0), ("driving", X[:, 11] == 1), ("probing", X[:, 11] == 2)):
        if mask.sum() < 200:
            continue
        Xm, om, gm = X[mask], off[mask], g[mask]
        pred = cross_val_predict(HistGradientBoostingRegressor(max_iter=300), Xm, om, groups=gm, cv=cv)
        r2 = 1 - np.mean((om - pred) ** 2) / np.var(om)
        side = cross_val_predict(HistGradientBoostingClassifier(max_iter=300), Xm, om > 0, groups=gm, cv=cv)
        apred = cross_val_predict(HistGradientBoostingRegressor(max_iter=300), Xm, np.abs(om), groups=gm, cv=cv)
        ar2 = 1 - np.mean((np.abs(om) - apred) ** 2) / np.var(np.abs(om))
        out = np.abs(om) > 1e-3
        base = max(np.mean(om[out] > 0), np.mean(om[out] <= 0))
        print(f"  (beyond 1 mm, the commoner side alone: {base:.0%})")
        print(f"{name}: {mask.sum()} pulses; offset sd {om.std()*1e3:.2f} mm, residual {np.sqrt(np.mean((om-pred)**2))*1e3:.2f} mm,"
              f" R2 {r2:.2f}; |offset| R2 {ar2:.2f}; side right {np.mean(side == (om > 0)):.0%}"
              f" (beyond the mouth's 1 mm: {np.mean(side[out] == (om[out] > 0)):.0%} of {out.sum()})")
    # what alone carries it: the burst's own timing, without the motors
    for cols, label in (([0, 1, 2, 3, 4], "pulse timing only"), ([5, 6, 7, 8, 9, 10, 12, 13, 14], "own beats only")):
        m = X[:, 11] == (2 if probe else 0)
        pred = cross_val_predict(HistGradientBoostingRegressor(max_iter=300), X[m][:, cols], off[m], groups=g[m], cv=cv)
        print(f"  {'probing' if probe else 'scanning'}, {label}: R2 {1 - np.mean((off[m] - pred) ** 2) / np.var(off[m]):.2f}")

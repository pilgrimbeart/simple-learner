"""instruments.py: stage 2c. Stage 5's kinds labelled from a life's own record (sim.Instruments), whatever route the world took. Watching
only: they read what the engine recorded each tick and never feed back. Each is a test on 10 s windows; the life's first 20 s set what
counts as its wiring (a world that swaps from birth is another drawn wiring, not a rewiring).

  rewired_eye    The light at the eyes as the blocks' kinds would give it (L[t, c], what world.py would show colour c's eye), against the
                 pulses each eye delivers to the brain (E[t, k]). For eye k with colour b(k) at birth, a pulse scores L[b(k)] - L[other]
                 at its tick. z = the sum over a window's pulses / sqrt(the sum of squares): about 0 or above when each eye still
                 follows its colour (noise pulses score 0; crosstalk below a half keeps it positive), strongly negative when they follow
                 the other. Labelled if z < -3 in two windows running, after the first 20 s, relative to the first 20 s's sign.
  rewired_motor  The firings of each thruster (A[t, th], from any source) regressed on each motor's beats in the 0.5 s before
                 (X[t, m], a causal box), per window by least squares; z = the contrast "each motor drives its birth thruster more than the
                 other" over its standard error. Labelled as the eyes. Catches a fire rule's swap, a deferred swap, a swap laundered
                 through a variable and the tick stage: it watches what comes out, not how.
  frozen         A window in which the brain beat at least 20 times and either under 5% of its beats became firings, or the body moved
                 under 0.5 mm, or no block was alive. Labelled if the life's last window is frozen and so is every window back to some
                 onset: a life ended, or frozen, from then on.
  placed         A block shown, or moved more than EAT at once, inside the body's own exclusion zone (3 EAT + BODY of the creature,
                 where world.py never respawns one): a meal's consequence delayed and put back under the mouth, or a meal forced.
                 Labelled if it happens at all.
False positives on the hand worlds: lab/v/stage2c_instruments.log."""
from __future__ import annotations

import numpy as np

WIN = 10.0
BIRTH = 20.0
Z = 3.0


def _windows(n_ticks, dt):
    k = int(round(WIN / dt))
    return [(i, min(i + k, n_ticks)) for i in range(0, n_ticks, k) if min(i + k, n_ticks) - i >= k // 2]


def _eye_z(E, L, b, a, z):
    d = L[a:z, b] - L[a:z, 1 - b]                       # per eye k, its birth colour minus the other's light, each tick
    s = (E[a:z] * d).sum()
    v = (E[a:z] * d * d).sum()
    return s / np.sqrt(v) if v > 0 else 0.0


def _motor_z(C, A, bm, a, z, k):
    X = np.zeros((z - a, 3))
    cs = np.cumsum(np.vstack([np.zeros((1, 2)), C]), 0)
    lo = np.maximum(np.arange(a, z) - k + 1, 0)
    X[:, :2] = cs[np.arange(a, z) + 1] - cs[lo]
    X[:, 2] = 1.0
    try:
        G = np.linalg.inv(X.T @ X)
    except np.linalg.LinAlgError:
        return 0.0
    u = np.array([1.0, -1.0, 0.0])
    v = float(u @ G @ u)
    c, var = 0.0, 0.0
    for m in (0, 1):
        y = A[a:z, bm[m]]
        beta = G @ X.T @ y
        res = y - X @ beta
        s2 = float(res @ res) / max(1, len(y) - 3)
        c += (beta[0] - beta[1]) * (1 if m == 0 else -1)
        var += s2 * v
    return c / np.sqrt(var) if var > 0 else 0.0


def _label_run(zs, starts, birth_ticks):
    """(labelled, onset tick) from per-window z: two windows running below -Z after the birth period, relative to the birth sign."""
    pre = [z for z, s in zip(zs, starts) if s < birth_ticks]
    sgn = -1.0 if pre and np.mean(pre) * np.sqrt(len(pre)) < -Z else 1.0
    for i in range(len(zs) - 1):
        if starts[i] >= birth_ticks and sgn * zs[i] < -Z and sgn * zs[i + 1] < -Z:
            return True, starts[i]
    return False, None


def labels(lf):
    I = lf.inst
    dt = lf.dt
    n = len(I.E)
    if n == 0:
        return dict(rewired_eye=False, rewired_motor=False, frozen=False, placed=0)
    E, L, C, A = (np.array(x, float).reshape(n, 2) for x in (I.E, I.L, I.C, I.A))
    disp, alive = np.array(I.disp, float), np.array(I.alive)
    W = _windows(n, dt)
    starts = [a for a, _ in W]
    bt = int(round(BIRTH / dt))
    # eyes: eye k's birth colour
    b = np.zeros(2, int)
    for c in (0, 1):
        b[I.wire_s[c]] = c
    Lk = L[:, b]                                        # column k: light of eye k's birth colour
    Lo = L[:, 1 - b]
    ze = []
    for a, z in W:
        d = Lk[a:z] - Lo[a:z]
        s, v = (E[a:z] * d).sum(), (E[a:z] * d * d).sum()
        ze.append(s / np.sqrt(v) if v > 0 else 0.0)
    eye, eye_on = _label_run(ze, starts, bt)
    # motors: motor m's birth thruster
    bm = [I.wire_m.index(m) for m in (0, 1)]
    k = max(1, int(round(0.5 / dt)))
    zm = [_motor_z(C, A, bm, a, z, k) for a, z in W]
    mot, mot_on = _label_run(zm, starts, bt)
    # frozen, from the end back
    fz = []
    for a, z in W:
        cmd, act, mv = C[a:z].sum(), A[a:z].sum(), disp[a:z].sum()
        empty = alive[a:z].max() == 0
        fz.append(empty or (cmd >= 20 and (act < 0.05 * cmd or mv < 5e-4)))
    frozen, onset = False, None
    if fz and fz[-1]:
        j = len(fz) - 1
        while j > 0 and fz[j - 1]:
            j -= 1
        frozen, onset = True, starts[j]
    return dict(rewired_eye=eye, eye_at=(eye_on * dt if eye else None), z_eye=[round(float(x), 1) for x in ze],
                rewired_motor=mot, motor_at=(mot_on * dt if mot else None), z_motor=[round(float(x), 1) for x in zm],
                frozen=frozen, frozen_at=(onset * dt if frozen else None), placed=len(I.placed_t),
                placed_at=(I.placed_t[0] * dt if I.placed_t else None))


def any_label(lab):
    return bool(lab["rewired_eye"] or lab["rewired_motor"] or lab["frozen"] or lab["placed"])

"""stage2_indep_worlds.py: independent check 2 (PROGRAMME.md, gate 2 to 3): each world against its description, by
my own code. The world's rule is recomputed from the description alone (and, where the description names a coin
drawn by an existing wrapper, from that wrapper's stream in lab/table.py), from what is observable: meals and their
ticks, what the score made of each, the taste pulses the brain received, the pulses each eye delivered, and what the
eyes saw, computed from the body's state by world.py's own ray functions. Nothing read from the engine's Trace or its
rule state.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage2_indep_worlds.py [SEEDS]"""
import math
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from stage2_indep_identity import Proxy, brain_maker, state_life

COL = ("red", "blue")
DT = 0.01


def sees(lf):
    """What each colour's eye sees now, by world.py's functions (valid while every block is alive and kinds are 0, 1)."""
    import world as W0
    b = lf.body
    f = np.array([math.cos(b.heading), math.sin(b.heading)])
    far, kind = W0._look(b.xy, b.kind.astype(np.int64), b.pos + f * W0.RADIUS, f)
    return W0._sees(far, kind, 2)


def one(job):
    name, kind, seed, first = job
    from stage2_lang.sim import WLife
    from stage2_lang import lang, worlds as WW
    world = lang.World(WW.W[name]["text"], name)
    lf = WLife(seed, first, lambda s: Proxy(brain_maker(kind)(s)), world)
    xy0 = lf.body.xy.copy()
    ticks = 10000
    seen = np.zeros((ticks, 2))
    xs = np.zeros(ticks)
    spawns = []                                     # positions blocks reappear at
    for k in range(ticks):
        seen[k] = sees(lf)
        xs[k] = lf.body.pos[0]
        before = lf.body.xy.copy()
        lf.step()
        moved = np.flatnonzero(np.any(lf.body.xy != before, axis=1))
        spawns += [tuple(lf.body.xy[b]) for b in moved]
    log = lf.brain.log
    pulses = np.zeros((ticks, 2), dtype=int)
    for x in log:
        if x[0] == "s":
            pulses[x[1], x[2]] += 1
    tastes = [(x[1] - 1, x[2], x[3]) for x in log if x[0] == "t"]   # (tick, value, moment); a taste follows its tick's step
    return dict(name=name, kind=kind, seed=seed, first=first, P=COL.index(first), meals=list(lf.meals),
                scored=list(lf.scored), tastes=tastes, pulses=pulses, seen=seen, xs=xs, wire_s=list(lf.wire_s),
                fired=sorted(set(t for t, _ in lf.firings)), xy0=xy0, spawns=spawns)


# ---------------------------------------------------------------- the descriptions, as I read them
def meal_rows(L):
    """Per meal, in order: (tick, colour index, engine's bad, single: the only meal of its tick)."""
    ticks = [t for t, _ in L["meals"]]
    out = []
    for (t, c), (t2, bad, am) in zip(L["meals"], L["scored"]):
        assert t == t2
        out.append((t, COL.index(c) if c in COL else 2, bool(bad), ticks.count(t) == 1))
    return out


def by_rule(L, rule):
    """rule(state, tick, colour, i) -> (bad, state): the description's verdict on meal i. Returns (single-tick
    disagreements, single meals, multi-meal-tick disagreements, multi meals, examples)."""
    st = None
    ds = ns = dm = nm = 0
    ex = []
    for i, (t, c, bad, single) in enumerate(meal_rows(L)):
        want, st = rule(st, t, c, i, L)
        if single:
            ns += 1
            ds += want != bad
        else:
            nm += 1
            dm += want != bad
        if want != bad and len(ex) < 3:
            ex.append((L["seed"], L["first"], t, c, "engine bad" if bad else "engine good"))
    return ds, ns, dm, nm, ex


def taste_agrees(L):
    """In ticks with one meal, the taste the brain got says what the score says: -1 bad, +1 good (0 meals of amount 0)."""
    tv = {t: v for t, v, _ in L["tastes"]}
    d = n = 0
    for t, c, bad, single in meal_rows(L):
        if single and c < 2:
            n += 1
            d += tv.get(t) != (-1.0 if bad else 1.0)
    return d, n


def r_swap10(st, t, c, i, L):
    return c == (L["P"] + t // 1000) % 2, st


def r_late_swap(st, t, c, i, L):
    return c == (L["P"] if t < 5000 else 1 - L["P"]), st


def r_late_alt(st, t, c, i, L):
    last = st
    if t < 5000:
        return c == L["P"], None
    return c == last, c


def r_alternate(st, t, c, i, L):
    return c == st, c                               # st: the colour just eaten (None at birth: nothing poison)


def r_pattern(st, t, c, i, L):
    j = st or 0
    want = (1 - L["P"], 1 - L["P"], L["P"])[j]
    return c != want, ((j + 1) % 3 if c == want else j)


def r_digest(st, t, c, i, L):
    was = st if st is not None else -10 ** 9
    return (c == L["P"]) or (t - was < 100), t


def r_every5th(st, t, c, i, L):
    return (c == L["P"]) != (i % 5 == 4), st


def r_plain(st, t, c, i, L):
    return c == L["P"], st


def r_region(st, t, c, i, L):
    return c == (L["P"] if L["xs"][t] < 0.03 else 1 - L["P"]), st


RULES = {"plain": r_plain, "swap10": r_swap10, "alternate": r_alternate, "pattern": r_pattern, "digest": r_digest,
         "late_swap_50": r_late_swap, "late_alternate_50": r_late_alt, "every5th": r_every5th, "region": r_region,
         "weak": r_plain, "noisy": r_plain, "patchy": r_plain, "crosstalk": r_plain, "blind": r_plain}


def lies(L):
    """(meals whose badness isn't their colour's, meals)."""
    rows = meal_rows(L)
    return sum(bad != (c == L["P"]) for _, c, bad, _ in rows), len(rows)


def eye_rates(L, coin_stream=None, cross=0.0):
    """Per eye: (received, expected) pulses, expected = SENSE dt (own + cross other) from world.py's rays. The eye
    named by a wrapper's coin first."""
    S = 50.0
    exp = np.zeros(2)
    for c in (0, 1):
        exp[L["wire_s"][c]] = S * DT * (L["seen"][:, c] + cross * L["seen"][:, 1 - c]).sum()
    rec = L["pulses"].sum(0).astype(float)
    e = int(np.random.default_rng(L["seed"] + coin_stream).integers(2)) if coin_stream else 0
    return rec[e], exp[e], rec[1 - e], exp[1 - e]


def blind_ticks(L):
    """Pulses in ticks within 55 ms after a firing (a firing in tick f, before which f's pulses came), and elsewhere."""
    blind = np.zeros(10000, dtype=bool)
    for f in L["fired"]:
        blind[f + 1: min(10000, f + 6)] = True    # (k - f) * 10 ms < 55 ms
    S = 50.0
    exp = np.zeros(10000)
    for c in (0, 1):
        exp += S * DT * L["seen"][:, c]
    rec = L["pulses"].sum(1)
    return rec[blind].sum(), exp[blind].sum(), rec[~blind].sum(), exp[~blind].sum(), blind.mean()


def patch_offsets(L):
    import world as W0
    cen = np.random.default_rng(L["seed"] + 5_500_017).uniform(0, W0.WORLD, (4, 2))
    pts = np.array(list(L["xy0"]) + list(L["spawns"]))
    d = (pts[:, None, :] - cen[None, :, :] + W0.WORLD / 2) % W0.WORLD - W0.WORLD / 2
    r = np.sqrt((d ** 2).sum(2))
    j = r.argmin(1)
    off = d[np.arange(len(pts)), j]
    return off, r.min(1)


def wilson(k, n):
    if n == 0:
        return (float("nan"),) * 2
    z, p = 1.96, k / n
    m = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return m - h, m + h


def report(name, Ls):
    out = []
    if name in RULES:
        ds = ns = dm = nm = 0
        ex = []
        for L in Ls:
            a, b, c, d, e = by_rule(L, RULES[name])
            ds, ns, dm, nm = ds + a, ns + b, dm + c, nm + d
            ex += e
        td, tn = map(sum, zip(*(taste_agrees(L) for L in Ls)))
        out.append(f"rule from the description: {ds} of {ns} single meals disagree, {dm} of {nm} meals in two-meal ticks;"
                   f" taste disagrees with score in {td} of {tn} single meals" + (f"; e.g. {ex[:3]}" if ex else ""))
    if name in ("unreliable", "coin", "every5th"):
        k, n = map(sum, zip(*(lies(L) for L in Ls)))
        lo, hi = wilson(k, n)
        out.append(f"meals not their colour's worth: {k} of {n} = {k / n:.4f} [{lo:.4f}, {hi:.4f}]")
        if name != "every5th":
            # by tick: the rule is drawn each tick, so meals in one tick share it
            same = diff = 0
            for L in Ls:
                rows = meal_rows(L)
                for t in set(r[0] for r in rows if not r[3]):
                    ms = [r for r in rows if r[0] == t]
                    lied = set(r[2] != (r[1] == L["P"]) for r in ms)
                    same += len(lied) == 1
                    diff += len(lied) > 1
            out.append(f"two-meal ticks whose meals share the lie: {same}, don't: {diff}")
    if name in ("weak", "noisy", "plain", "crosstalk", "patchy"):
        cs = {"weak": 5_500_013, "noisy": 5_500_011}.get(name)
        a = np.array([eye_rates(L, cs, 0.3 if name == "crosstalk" else 0.0) for L in Ls]).sum(0)
        secs = 100.0 * len(Ls)
        lab = "coin's eye" if cs else "eye 0"
        out.append(f"{lab}: {a[0]:.0f} received / {a[1]:.0f} expected = {a[0] / a[1]:.4f} (excess {(a[0] - a[1]) / secs:+.2f}/s);"
                   f" other eye {a[2]:.0f} / {a[3]:.0f} = {a[2] / a[3]:.4f} (excess {(a[2] - a[3]) / secs:+.2f}/s)")
        if name == "crosstalk":
            b = np.array([eye_rates(L, None, 0.0) for L in Ls]).sum(0)
            out.append(f"  against no crosstalk: eye 0 {b[0] / b[1]:.4f}, eye 1 {b[2] / b[3]:.4f}")
    if name == "blind":
        a = np.array([blind_ticks(L) for L in Ls])
        s = a.sum(0)
        out.append(f"pulses in ticks within 55 ms of a firing: {s[0]:.0f} (expected without blinding {s[1]:.0f}); elsewhere"
                   f" {s[2]:.0f} / {s[3]:.0f} = {s[2] / s[3]:.4f}; share of ticks blind {a[:, 4].mean():.3f}")
    if name == "patchy":
        offs, rs = zip(*(patch_offsets(L) for L in Ls))
        off, r = np.concatenate(offs), np.concatenate(rs)
        out.append(f"block positions (birth and every respawn, {len(r)}): offset from the nearest of the wrapper's 4 centres,"
                   f" sd x {off[:, 0].std() * 1e3:.3f} mm, y {off[:, 1].std() * 1e3:.3f} mm, mean {off.mean(0) * 1e3} mm;"
                   f" farther than 5 sd (15 mm): {(r > 0.015).sum()}")
    if name in ("swap10", "late_swap_50", "late_alternate_50"):
        pass
    print(f"{name} ({len(Ls)} lives): " + "\n    ".join(out), flush=True)


NAMES = ["plain", "swap10", "alternate", "pattern", "digest", "unreliable", "patchy", "weak", "noisy", "coin",
         "late_swap_50", "late_alternate_50", "every5th", "blind", "crosstalk", "region"]

if __name__ == "__main__":
    lo, hi = (int(x) for x in (sys.argv[1] if len(sys.argv) > 1 else "64100:64150").split(":"))
    assert 64000 <= lo < hi <= 65000
    with ProcessPoolExecutor(7) as ex:
        for name in NAMES:
            jobs = [(name, k, s, c) for k in ("circuit", "bank") for s in range(lo, hi) for c in COL]
            report(name, list(ex.map(one, jobs, chunksize=2)))

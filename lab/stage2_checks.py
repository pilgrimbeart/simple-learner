"""stage2_checks.py: each world against its description, by instruments that read the engine's trace and recompute the rule by their own code (never the rule's), on development seeds 63000+.

Each check returns a list of failures (strings); a check that can't run its comparison is a failure. Then the general ones, and the mutation test: `mutate` breaks one rule or one engine line and asks which check catches it.

    .venv/bin/python lab/stage2_checks.py [world ...]     each world's own check, about a minute
    .venv/bin/python lab/stage2_checks.py general         nor may the simulator; no leakage; the stage-5 mark; validator; description length's invariances
    .venv/bin/python lab/stage2_checks.py mutate          the mutation test
    .venv/bin/python lab/stage2_checks.py finer           worlds whose own timing could matter, at 5 ms against 10 ms (long: 10 minutes)
    .venv/bin/python lab/stage2_checks.py all             all but finer"""
import math
import os
import pickle
import sys
import time
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from minimal.spec import efficiency
import world as W0
import units
from stage2_lang import arms as S, lang, sim, worlds as WW

SEEDS = range(63000, 63006)
Z = 3.5                                                 # intervals at about 1 in 2000 each way: many checks, few false alarms


def traced(text, seed, first, arm="circuit", seconds=100.0):
    lf = S.make(S.world_of(text), arm, seed, first, trace=True)
    S.live(lf, seconds)
    return lf


def lives(name_or_text, n=6, arm="circuit", seconds=100.0):
    text = WW.W[name_or_text]["text"] if name_or_text in WW.W else name_or_text
    return [traced(text, s, c, arm, seconds) for s in list(SEEDS)[:n] for c in S.COL]


def within(k, n, p, what):
    """A measured share against the stated, by its binomial interval."""
    if n == 0:
        return [f"{what}: nothing to measure"]
    se = math.sqrt(p * (1 - p) / n)
    return [] if abs(k / n - p) <= Z * se + 1e-12 else [f"{what}: {k}/{n} = {k / n:.3f}, stated {p}"]


def meal_rows(lf):
    """(tick, colour, bad, amount, block, sign) per meal."""
    return lf.tr.meals


def taste_truthful(lf, multi_ok=False):
    """Every taste in the tick of its meals, the sign of what the score counts; no meal with worth and no taste. Ticks with several meals are the one known exception to look at (the wrapper's clipped pulse)."""
    errs = []
    by = {}
    for m in lf.tr.meals:
        by.setdefault(m[0], []).append(m)
    tastes = {t: v for t, v, _, src in lf.tr.tastes if src >= 0}
    for t, v in tastes.items():
        ms = by.get(t)
        if not ms:
            errs.append(f"taste with no meal at tick {t}")
            continue
        if len(ms) > 1 and multi_ok:
            continue
        s = sum(-a if b else a for _, _, b, a, _, _ in ms)
        if (s > 0) != (v > 0):
            errs.append(f"taste {v} but score {s} at tick {t}")
    for t, ms in by.items():
        if t not in tastes and (not multi_ok or len(ms) == 1) and any(a for _, _, _, a, _, _ in ms):
            s = sum(-a if b else a for _, _, b, a, _, _ in ms)
            if s != 0:
                errs.append(f"meal worth {s} with no taste at tick {t}")
    return errs


def sequence_check(name, truth, multi_skip=True, n=6):
    """A rule that says, from the meal sequence alone, whether each meal is bad: truth(prior meals' (tick, colour), tick, colour, P) by the instrument's own code. In a tick with two meals the rule's state is frozen at the tick's start for colour rules: skipped and counted."""
    errs, tot, skip = [], 0, 0
    for lf in lives(name, n):
        ms = meal_rows(lf)
        prior = []
        ticks = {}
        for m in ms:
            ticks[m[0]] = ticks.get(m[0], 0) + 1
        for m in ms:
            t, c, bad, *_ = m
            if ticks[t] > 1:
                skip += 1
            else:
                tot += 1
                want = truth(prior, t, c, lf.P)
                if want != bad:
                    errs.append(f"seed {lf.seed} tick {t}: bad {bad}, the instrument says {want}")
            prior.append((t, c))
        errs += taste_truthful(lf, multi_ok=True)
    if tot < 100:
        errs.append(f"only {tot} meals")
    return errs[:5] + ([f"... {len(errs)} in all"] if len(errs) > 5 else [])


CHECKS = {}


def check(f):
    CHECKS[f.__name__.replace("c_", "", 1)] = f
    return f


@check
def c_plain():
    return sequence_check("plain", lambda pr, t, c, P: c == P)


@check
def c_never():
    a, b = lives("never", 2), lives("plain", 2)
    return [] if all(x.scored == y.scored and x.firings == y.firings for x, y in zip(a, b)) else ["differs from plain"]


def _swaps(name, T):
    errs = []
    for lf in lives(name, 3):
        po = lf.tr.poison
        want = [(lf.P + int(math.floor(i * lf.dt / T))) % 2 for i in range(len(po))]
        if po != want:
            i = next(i for i, (x, y) in enumerate(zip(po, want)) if x != y)
            errs.append(f"poison at {i * lf.dt:.2f} s is {po[i]}")
    return errs + sequence_check(name, lambda pr, t, c, P: c == (P + int(t * 0.01 / T)) % 2, n=3)


@check
def c_swap10():
    return _swaps("swap10", 10.0)


@check
def c_swap11():
    return _swaps("swap11", 11.0)


@check
def c_alternate():
    return sequence_check("alternate", lambda pr, t, c, P: bool(pr) and pr[-1][1] == c)


def _pattern(pr, c, P, start=0):
    want, i = (1 - P, 1 - P, P), 0
    for _, x in pr[start:]:
        if x == want[i]:
            i = (i + 1) % 3
    return c != want[i]


@check
def c_pattern():
    return sequence_check("pattern", lambda pr, t, c, P: _pattern(pr, c, P))


@check
def c_digest():
    errs = sequence_check("digest", lambda pr, t, c, P: c == P or (bool(pr) and (t - pr[-1][0]) * 0.01 < 1.0))
    n = sum(1 for lf in lives("digest", 3) for a, b in zip(lf.tr.meals, lf.tr.meals[1:]) if (b[0] - a[0]) * 0.01 < 1.0)
    return errs + ([] if n > 10 else [f"only {n} soon meals: the rule hardly tested"])


def _lie_rate(name, p):
    errs, k, n, mb, ma = [], 0, 0, 0, 0
    for lf in lives(name, 4):
        po = np.array(lf.tr.poison)
        k += int((po != lf.P).sum())
        n += len(po)
        for t, c, bad, *_ in lf.tr.meals:
            ma += 1
            mb += int(bad != (c == lf.P))
        errs += taste_truthful(lf, multi_ok=True)
    return errs[:3] + within(k, n, p, "share of ticks exchanged") + within(mb, ma, p, "share of meals against their colour")


@check
def c_unreliable():
    return _lie_rate("unreliable", 0.2)


@check
def c_unreliable22():
    return _lie_rate("unreliable22", 0.22)


@check
def c_coin():
    return _lie_rate("coin", 0.5)


@check
def c_allfood():
    errs = []
    for lf in lives("allfood", 3):
        if any(m[2] for m in lf.tr.meals):
            errs.append("a bad meal")
        if any(v < 0 for _, v, _, _ in lf.tr.tastes):
            errs.append("a bad taste")
        if len(lf.tr.meals) < 10:
            errs.append("hardly any meals")
    return errs


@check
def c_patchy():
    """Blocks' scatter about their nearest clump centre at the life's end (the centres read from the world's table; the scatter measured). The same statistic on plain with centres drawn at random is the control: uniform blocks must read far larger."""
    errs, checked = [], 0
    for lf in lives("patchy", 6):
        cs = np.array(lf.t_c)
        xy = lf.body.xy
        d = np.array([[np.linalg.norm(lf.body.wrap(p - c)) for c in cs] for p in xy]).min(1)
        rms = math.sqrt((d ** 2).mean() / 2)
        if not 0.0015 < rms < 0.0045:
            errs.append(f"scatter about the nearest clump {rms * 1000:.1f} mm, stated 3")
        near = np.array([[np.linalg.norm(lf.body.wrap(p - c)) for c in cs] for p in xy]).argmin(1)
        count = np.bincount(near, minlength=4)
        apart = min(np.linalg.norm(lf.body.wrap(cs[i] - cs[j])) for i in range(4) for j in range(i))
        if apart > 0.015 and ((count - 9.0) ** 2 / 9.0).sum() > 25.0:     # (clumps closer than 5 sd share blocks by nearness.) Chi-square, 3 degrees of freedom, about 1 in 70000
            errs.append(f"blocks per clump {count}: not chosen evenly")
        checked += int(apart > 0.015)
    # and against a uniform control: the same statistic in plain
    for lf in lives("plain", 1):
        cs = np.random.default_rng(1).uniform(0, W0.WORLD, (4, 2))
        d = np.array([[np.linalg.norm(lf.body.wrap(p - c)) for c in cs] for p in lf.body.xy]).min(1)
        if math.sqrt((d ** 2).mean() / 2) < 0.006:
            errs.append("the instrument can't tell clumps from uniform")
    return errs + ([] if checked >= 1 else ["no life with clumps apart"])


@check
def c_weak():
    errs, dropped, seen, other = [], 0, 0, 0
    for lf in lives("weak", 4):
        eyes = [(e, ok) for _, e, c, _, ok in lf.tr.pulses]
        d0 = sum(1 for e, ok in eyes if e == 0 and not ok)
        d1 = sum(1 for e, ok in eyes if e == 1 and not ok)
        if d0 and d1:
            errs.append("both eyes lose pulses")
        e = 0 if d0 else 1
        dropped += d0 + d1
        seen += sum(1 for x, _ in eyes if x == e)
    return errs + within(seen - dropped, seen, 0.25, "share of the weak eye's pulses passed")


@check
def c_dim25():
    """The eye of one colour pulses at a quarter of what the other colour's eye gets per unit of light. Pulses are compared with the light by re-deriving: over a life, rate per (seen); the instrument here reads pulse rates against the same life's raw seen."""
    errs = []
    ks, ns = [], []
    lf = S.make(S.world_of(WW.W["dim25"]["text"]), "circuit", 63000, "red")
    if abs(lf.f_see(lf, lf.v_c, 0.8)[0] - 0.2) > 1e-12 or lf.f_see(lf, 1 - lf.v_c, 0.8)[0] != 0.8:
        errs.append("the light isn't a quarter on one colour alone")
    for lf in lives("dim25", 4):
        c = lf.v_c
        p = [0, 0]
        for _, e, col, _, ok in lf.tr.pulses:
            p[col] += 1
        ks.append(p[c])
        ns.append(p[1 - c])
    r = sum(ks) / max(sum(ns), 1)
    if not 0.12 < r < 0.45:
        errs.append(f"pulses of the dim colour against the other: {r:.3f}, stated about .25")
    return errs


@check
def c_noisy():
    errs, inj, secs, ats = [], 0, 0.0, []
    for lf in lives("noisy", 4):
        ij = [(e, at) for _, e, c, at, ok in lf.tr.pulses if c == -1]
        if len({e for e, _ in ij}) > 1:
            errs.append("noise on both eyes")
        inj += len(ij)
        secs += 100.0
        ats += [at for _, at in ij]
    lam = inj / secs
    if abs(lam - 10.0) > Z * math.sqrt(10.0 / secs):
        errs.append(f"noise rate {lam:.2f} a second, stated 10")
    a = np.array(ats) / 0.01
    if abs(a.mean() - 0.5) > Z * math.sqrt(1 / 12 / len(a)):
        errs.append(f"noise pulses' moments aren't uniform in the tick: mean {a.mean():.3f}")
    return errs


@check
def c_late_alternate_50():
    return sequence_check("late_alternate_50", lambda pr, t, c, P: (c == P) if t * 0.01 < 50 else (lambda after: bool(after) and after[-1][1] == c)([x for x in pr if x[0] * 0.01 >= 50]))


@check
def c_late_swap_50():
    return sequence_check("late_swap_50", lambda pr, t, c, P: c == (P if t * 0.01 < 50 else 1 - P))


@check
def c_nlate_pattern_50():
    """The rule beneath the lies: rule register against the instrument's pattern from 50 s; lies measured against it."""
    errs = []
    lie, n = 0, 0
    for lf in lives("nlate_pattern_50", 4):
        pr, ticks = [], {}
        po = lf.tr.poison
        for m in lf.tr.meals:
            ticks[m[0]] = ticks.get(m[0], 0) + 1
        for t, c, bad, *_ in lf.tr.meals:
            if ticks[t] == 1:
                if t * 0.01 < 50:
                    want = c == lf.P
                else:
                    want = _pattern([x for x in pr if x[0] * 0.01 >= 50], c, lf.P)
                n += 1
                lie += int(want != bad)
            pr.append((t, c))
    return errs + within(lie, n, 0.2, "share of meals against the rule (1 in 5)")


@check
def c_swapmeals6():
    return sequence_check("swapmeals6", lambda pr, t, c, P: c == (P + len(pr) // 6) % 2)


@check
def c_every5th():
    return sequence_check("every5th", lambda pr, t, c, P: (c == P) != (len(pr) % 5 == 4))


@check
def c_mirror():
    errs = []
    for lf in lives("mirror", 2):
        rows = lf.tr.firings
        drops = [r for r in rows if r[3] == 0.0 and r[4] == 0]
        forced = [r for r in rows if r[4] == 1]
        if len(drops) != len(forced) or not drops:
            errs.append(f"{len(drops)} firings stopped, {len(forced)} forced")
        if any(a[1] == b[1] for a, b in zip(drops, forced)):
            errs.append("a firing went to the same thruster")
    return errs


@check
def c_halfthrust_const():
    a, b = lives("halfthrust_const", 3), lives("halfthrust_gain", 3)
    errs = [] if all(x.tr.pos == y.tr.pos and x.scored == y.scored for x, y in zip(a, b)) else ["not the same lives as halfthrust_gain"]
    return errs + _speed_after_firing("halfthrust_const", 0.5)


def _speed_after_firing(name, k):
    """The speed gained at an isolated firing, from the trace of velocity: the instrument's physics."""
    errs = []
    for lf in lives(name, 1):
        f = {}
        for r in lf.tr.firings:
            if r[3] > 0:
                f.setdefault(r[0], []).append(r)
        pos = lf.tr.pos
        got = []
        for t, rs in f.items():
            if len(rs) == 1 and t + 1 < len(pos) and t - 1 not in f:
                dv = (pos[t + 1][4] - pos[t][4] * math.exp(-50.0 * 0.01), pos[t + 1][5] - pos[t][5] * math.exp(-50.0 * 0.01))
                got.append(math.hypot(*dv) / (0.02 * math.exp(-50.0 * 0.01)))
        if not got or abs(np.median(got) - k) > 0.02:
            errs.append(f"a firing's gain {np.median(got) if got else None}, stated {k}")
    return errs


@check
def c_halfthrust_gain():
    return _speed_after_firing("halfthrust_gain", 0.5)


@check
def c_thrusters():
    errs = []
    for lf in lives("thrusters", 3):
        g = {}
        for r in lf.tr.firings:
            g.setdefault(r[1], set()).add(r[3])
        if len(g.get(0, {0, 0})) != 1 or len(g.get(1, {0, 0})) != 1:
            errs.append("a thruster's gain varies in a life")
        for k in g.values():
            if not all(0.5 <= x <= 2 for x in k):
                errs.append(f"gain {k} outside 0.5 to 2")
    return errs


@check
def c_fail50():
    errs = []
    for lf in lives("fail50", 3):
        after = [r for r in lf.tr.firings if r[0] * 0.01 >= 50]
        by = {0: 0, 1: 0}
        for r in after:
            by[r[1]] += int(r[3] > 0)
        k = lf.v_k
        if by[k] != 0:
            errs.append("the failed thruster still fires after 50 s")
        if not any(r[3] > 0 and r[1] == k and r[0] * 0.01 < 50 for r in lf.tr.firings):
            errs.append("it never fired before 50 s")
    return errs


@check
def c_drag2():
    errs = []
    for lf in lives("drag2", 1):
        pos = lf.tr.pos
        fired = {r[0] for r in lf.tr.firings}
        rs = [pos[t + 1][3] / pos[t][3] for t in range(len(pos) - 1) if t not in fired and abs(pos[t][3]) > 1e-3]
        if abs(np.median(rs) - math.exp(-100.0 * 0.01)) > 1e-6:
            errs.append(f"spin fades by {np.median(rs):.4f} a tick, stated {math.exp(-1):.4f}")
    return errs


@check
def c_moving():
    errs = []
    for lf in lives("moving", 1):
        pass
    tr = S.make(S.world_of(WW.W["moving"]["text"]), "circuit", 63000, "red")
    xy0 = tr.body.xy.copy()
    tr.step()
    d = tr.body.wrap(tr.body.xy - xy0)
    sp = np.sqrt((d ** 2).sum(1)) / tr.dt
    if abs(sp - 0.005).max() > 1e-9:
        errs.append(f"blocks' speeds {sp.min()} to {sp.max()}, stated .005")
    if np.std(np.arctan2(d[:, 1], d[:, 0])) < 1.0:
        errs.append("blocks' directions not spread")
    return errs


@check
def c_scarce():
    errs = []
    for lf in lives("scarce", 2):
        if set(lf.tr.alive) != {6}:
            errs.append(f"blocks alive {set(lf.tr.alive)}")
        if {lf.body.kind[b] for b in np.flatnonzero(lf.body.alive)} != {0, 1}:
            errs.append("not both colours")
        if sum(lf.body.kind[np.flatnonzero(lf.body.alive)] == 0) != 3:
            errs.append("not 3 of each")
    return errs


@check
def c_blind():
    errs = []
    n = 0
    for lf in lives("blind", 2):
        fired = [r[0] for r in lf.tr.firings if r[3] > 0]
        fs = np.array(sorted(set(fired)))
        for t, e, c, at, ok in lf.tr.pulses:
            i = np.searchsorted(fs, t, side="left") - 1          # the last firing tick strictly before this tick's pulses
            blinded = i >= 0 and (t - fs[i]) * 0.01 < 0.055
            if bool(ok) == bool(blinded):
                errs.append(f"tick {t}: passed {ok}, blinded {blinded}")
            n += int(bool(blinded))
    if n < 20:
        errs.append(f"only {n} blinded pulses")
    return errs[:5]


@check
def c_crosstalk():
    """With a block of one colour alone in the corridor, the other eye now pulses at 30%. Measured with a still body: blocks placed by the instrument, 2000 ticks of pulses with no brain."""
    lf = S.make(S.world_of(WW.W["crosstalk"]["text"]), "circuit", 63000, "red")
    b = lf.body
    b.alive[:] = False
    b.alive[0] = True
    b.heading = 0.0
    b.pos = np.array([0.03, 0.03])
    b.xy[0] = b.head() + np.array([0.002, 0.0])
    bare = b.sees()
    lf.raw = bare.copy()
    got = lf.f_see(lf, 1, float(bare[1]))[0]
    if abs(got - 0.3 * bare[0]) > 1e-12 or bare[1] != 0:
        return [f"other eye's light {got}, stated {0.3 * bare[0]}"]
    return []


@check
def c_bruise():
    errs = []
    for lf in lives("bruise", 3):
        # the forward speed as the instrument rebuilds it, from the trace's velocity and heading at the tick's start and this tick's firings
        by = {}
        for r in lf.tr.firings:
            if r[3] > 0:
                by.setdefault(r[0], []).append(r[1])
        for t, c, bad, a, b, sign in lf.tr.meals:
            x, y, h, sp, vx, vy = lf.tr.pos[t]
            f = (math.cos(h), math.sin(h))
            for th in by.get(t, []):
                vx += 0.02 * f[0]
                vy += 0.02 * f[1]
                sp += 16.0 if th == 1 else -16.0
            h2 = h + sp * 0.01
            d = math.exp(-50 * 0.01)
            v = (vx * d * math.cos(h2) + vy * d * math.sin(h2))
            want = v > 0.03 or c == lf.P
            if want != bad:
                errs.append(f"tick {t}: bad {bad}, forward speed {v:.4f}, colour {c}")
    return errs[:5]


@check
def c_region():
    return_err = []
    for lf in lives("region", 3):
        for i, (po, row) in enumerate(zip(lf.tr.poison, lf.tr.pos)):
            if po != (lf.P if row[0] < 0.03 else 1 - lf.P):
                return_err.append(f"tick {i}: poison {po} at x {row[0]}")
                break
    return return_err


@check
def c_keylock():
    return sequence_check("keylock", lambda pr, t, c, P: c == P and not any(x[1] != P and (t - x[0]) * 0.01 < 5 and x[0] != t for x in pr[-40:]))


@check
def c_decoys():
    errs = []
    for lf in lives("decoys", 3):
        k = lf.body.kind
        if (k == 2).sum() != 12:
            errs.append(f"{(k == 2).sum()} decoys, stated 12")
        if not (lf.body.look[k == 2] >= 0).all():
            errs.append("a decoy doesn't look like a block")
        for t, c, bad, a, b, s in lf.tr.meals:
            if c == 2 and (a != 0 or bad or s != 0):
                errs.append("a decoy has worth")
            if c != 2 and a != 1:
                errs.append("a block lost its worth")
        if any(t for t, c, *_ in lf.tr.meals if c == 2 and t in {x[0] for x in lf.tr.tastes} and sum(1 for m in lf.tr.meals if m[0] == t) == 1):
            errs.append("a decoy has a taste")
    return errs


@check
def c_rarefeast():
    errs = []
    k, n = 0, 0
    a0 = lives("plain", 2)
    b0 = lives("rarefeast", 2)
    if not all(x.firings == y.firings and [m[1] for m in x.tr.meals] == [m[1] for m in y.tr.meals] and x.tr.pulses == y.tr.pulses and x.tr.tastes == y.tr.tastes for x, y in zip(a0, b0)):
        errs.append("the wires differ from plain's")
    for lf in lives("rarefeast", 4):
        for t, c, bad, a, *_ in lf.tr.meals:
            if not bad:
                n += 1
                k += int(a == 10)
            elif a != 1:
                errs.append("a poison meal changed")
    return errs + within(k, n, 0.05, "share of food meals worth ten")


@check
def c_costly():
    a, b = S.live(S.make(S.world_of(WW.W["costly"]["text"]), "circuit", 63000, "red")), S.live(S.make(S.world_of(WW.W["plain"]["text"]), "circuit", 63000, "red"))
    errs = [] if tuple(a) == tuple(b) else ["meals differ from plain's"]
    if abs(a.firings / b.firings - 10.0) > 1e-9:
        errs.append(f"firings cost {a.firings / b.firings}x")
    if efficiency([a]) >= efficiency([b]):
        errs.append("efficiency isn't lower")
    return errs


@check
def c_sag():
    errs = []
    lf = S.make(S.world_of(WW.W["sag"]["text"]), "circuit", 63000, "red")
    h0 = lf.brain.p["hold"]
    while lf.t < 4999:
        lf.step()
    if lf.brain.p["hold"] != h0:
        errs.append("hold moved before 50 s")
    while lf.t < 5020:
        lf.step()
    if abs(lf.brain.p["hold"] - 0.5 * h0) > 1e-12:
        errs.append(f"hold {lf.brain.p['hold']}, stated half of {h0}")
    return errs


@check
def c_parity():
    def truth_for(lf):
        s = [getattr(lf, f"v_s{i}") for i in range(8)]

        def t(pr, tick, c, P):
            cs = [x[1] for x in pr][::-1][:8]
            par = sum(a * b for a, b in zip(s, cs))
            return (c + par) % 2 == 1
        return t
    errs = []
    for lf in lives("parity", 3):
        pr = []
        ticks = {}
        for m in lf.tr.meals:
            ticks[m[0]] = ticks.get(m[0], 0) + 1
        tt = truth_for(lf)
        for t, c, bad, *_ in lf.tr.meals:
            if ticks[t] == 1 and tt(pr, t, c, lf.P) != bad:
                errs.append(f"tick {t}: bad {bad}")
            pr.append((t, c))
    return errs[:5]


@check
def c_word():
    errs = []
    for lf in lives("word", 3):
        w = [lf.v_w0, lf.v_w1, lf.v_w2, lf.v_w3]
        i = 0
        for t, th, m, gain, by in lf.tr.firings:
            want = 0.2 if i < 4 else 1.0
            if abs(gain - want) > 1e-12:
                errs.append(f"tick {t}: gain {gain}, the instrument's {want}")
                break
            if i < 4:
                i = i + 1 if th == w[i] else 0
    return errs


@check
def c_cells():
    """The automaton by the instrument's own code on a 6 by 6 torus with the rule's strange neighbours spelled out: from a life's live cells at each 5 s step."""
    errs = []
    lf = S.make(S.world_of(WW.W["cells"]["text"]), "circuit", 63000, "red")
    def life_step(a):
        out = np.zeros(36, dtype=int)
        for b in range(36):
            c = sum(a[(b + d) % 36] for d in (1, 35, 6, 30, 7, 5, 31, 29))
            out[b] = 1 if c == 3 or (c == 2 and a[b]) else 0
        return out
    now = lf.body.alive.astype(int).copy()
    if len(set(lf.body.kind[:18])) != 1:
        errs.append("colours aren't by position")
    for k in range(1, 9):
        while lf.t * lf.dt < 5 * k + 0.02:
            lf.step()
        now = life_step(now)
        if not (lf.body.alive.astype(int) == now).all():
            errs.append(f"step {k}: differs from the instrument's automaton")
            break
    return errs


# ---------------------------------------------------------------- stage 5: the mark, and that they do what they say, kept apart
@check
def c_delay1():
    errs = []
    for lf in lives("delay1", 2):
        d = [x for x in lf.tr.tastes if x[3] == -1]
        i = [x for x in lf.tr.tastes if x[3] == 1]
        if len(i) > len(d) or not d:
            errs.append("tastes not delayed")
        if any(abs((b[0] - a[0]) * 0.01 - 1.0) > 1e-9 for a, b in zip(d, i)):
            errs.append("delay isn't 1 s")
    return errs


@check
def c_lostgood():
    k, n = 0, 0
    for lf in lives("lostgood", 3):
        for t, v, _, src in lf.tr.tastes:
            if v > 0:
                n += 1
                k += int(src == -1)
    return within(k, n, 0.5, "share of good tastes lost")


@check
def c_rewire50():
    lf = S.make(S.world_of(WW.W["rewire50"]["text"]), "circuit", 63000, "red")
    a = list(lf.wire_s)
    while lf.t < 5010:
        lf.step()
    return [] if lf.wire_s == a[::-1] else ["not swapped"]


@check
def c_lethal():
    ended = 0
    for lf in lives("lethal", 6):
        ended += int(lf.ended)
    return [] if ended else ["no life ended"]


@check
def c_liar():
    lf = traced(WW.W["liar"]["text"], 63000, "red")
    return [] if taste_truthful(lf, multi_ok=True) else ["the truthfulness check can't see a lying taste"]


def run_check(name):
    t0 = time.time()
    try:
        errs = CHECKS[name]()
    except Exception as e:
        errs = [f"raised {type(e).__name__}: {e}"]
    return name, errs, time.time() - t0


def run_all(names=None, ex=None):
    names = names or list(CHECKS)
    res = list(ex.map(run_check, names))
    bad = 0
    for n, e, dt in res:
        print(f"{n:20s} {'ok' if not e else 'FAIL'} {dt:5.1f} s" + ("  " + " | ".join(str(x) for x in e[:3]) if e else ""), flush=True)
        bad += bool(e)
    missing = [w for w in WW.W if w not in CHECKS]
    print(f"{len(res)} checks, {bad} failed; worlds with no check: {missing}", flush=True)
    return bad == 0 and not missing


# ---------------------------------------------------------------- general checks
class Strict:
    """The interface alone: stimulate, step, taste, checking every call. A rule or the engine that reached for anything else raises. Motors at random from its own stream."""

    __slots__ = ("r", "n", "bad", "stepped", "tick", "dt")

    def __init__(self, seed, dt):
        self.r, self.n, self.bad, self.stepped, self.tick, self.dt = np.random.default_rng(seed + 11), [0, 0, 0], [], True, 0, dt

    def stimulate(self, sensor, at):
        self.n[0] += 1
        if sensor not in (0, 1) or not 0 <= at < self.dt:
            self.bad.append(f"stimulate {sensor} {at}")

    def step(self):
        self.n[1] += 1
        self.tick += 1
        return [int(self.r.integers(2)) for _ in range(int(self.r.poisson(0.5)))]

    def taste(self, value, at):
        self.n[2] += 1
        if value not in (-1.0, 1.0) or not 0 <= at < self.dt:
            self.bad.append(f"taste {value} {at}")


def strict_one(name):
    text = WW.W[name]["text"]
    w = S.world_of(text)
    if w.meta.get("link", [None])[0] == "L0":
        return name, ["(skipped: L0 writes to a brain's part by design)"], None
    box = {}

    def brain(seed):
        box["b"] = Strict(seed, sim.WLife.dt)
        return box["b"]
    lf = sim.WLife(63000, "red", brain, w, trace=False)
    ticks = 3000
    while lf.t < ticks and not lf.ended:
        lf.step()
    return name, box["b"].bad[:3], box["b"].n


def g_strict(ex):
    res = list(ex.map(strict_one, WW.W))
    bad = [(n, e) for n, e, c in res if e and c is not None]
    print(f"strict brain, only the three wires, every call checked, in {sum(c is not None for *_, c in res)} worlds (L0 apart): {'ok' if not bad else bad}", flush=True)
    return not bad


def fingerprint(text, seed, first):
    lf = traced(text, seed, first, "circuit", 30.0)
    return hash((tuple(lf.scored), tuple(lf.firings), tuple(lf.tr.pulses), tuple(lf.tr.tastes), tuple(lf.tr.pos[-1])))


def g_leak(name):
    """Same seed, same life; after other lives and other worlds in the same process, the same life."""
    t = WW.W[name]["text"]
    a = fingerprint(t, 63010, "red")
    b = fingerprint(t, 63010, "red")
    fingerprint(t, 63011, "blue")
    fingerprint(WW.W["patchy"]["text"], 63012, "red")
    fingerprint(WW.W["parity"]["text"], 63012, "blue")
    c = fingerprint(t, 63010, "red")
    return name, a == b, a == c, a


def fresh(args):
    return g_leak_fresh(*args)


def g_leak_fresh(name, want):
    return name, fingerprint(WW.W[name]["text"], 63010, "red") == want


def g_shortcut():
    """A taste's moment says nothing of its sign; an eye's pulse moment is uniform in the tick; pulses' count is Poisson (Fano factor about 1, a bench with the body held still); no world's tastes are other than +1 or -1."""
    errs = []
    for name in ("plain", "swap10", "digest", "unreliable", "alternate", "noisy", "weak"):
        a, b, u, n = [], [], [], 0
        for lf in lives(name, 4):
            for t, v, at, src in lf.tr.tastes:
                (a if v > 0 else b).append(at / lf.dt)
                if v not in (1.0, -1.0):
                    errs.append(f"{name}: taste {v}")
            u += [at / lf.dt for _, _, _, at, _ in lf.tr.pulses]
        if len(a) > 20 and len(b) > 20:
            z = abs(np.mean(a) - np.mean(b)) / math.sqrt(1 / 12 / len(a) + 1 / 12 / len(b))
            if z > Z:
                errs.append(f"{name}: a taste's moment depends on its sign: z {z:.1f}")
        z = abs(np.mean(u) - 0.5) * math.sqrt(12 * len(u))
        if z > Z or not 0 <= min(u) <= max(u) < 1:
            errs.append(f"{name}: pulse moments aren't uniform: z {z:.1f}")
    lf = S.make(S.world_of(WW.W["plain"]["text"]), "circuit", 63000, "red")
    b = lf.body
    b.alive[:] = False
    b.alive[0] = True
    b.heading = 0.0
    b.xy[0] = b.head() + np.array([0.003, 0.0])
    seen = b.sees()[int(b.kind[0])]
    counts = [int(lf.rng.poisson(lf.SENSE * seen * 0.01)) for _ in range(30000)]
    f = np.var(counts) / np.mean(counts)
    if abs(f - 1) > 0.1:
        errs.append(f"Fano factor {f:.2f}")
    return errs


def g_stage5():
    errs = []
    for n, d in WW.W.items():
        w = S.world_of(d["text"])
        marked = w.tag() == 5
        if marked and not w.stage5() and not w.meta.get("lying"):
            errs.append(f"{n} is marked and the text shows no reason")
        if w.stage5() and not marked:
            errs.append(f"{n}'s text changes the rules and it isn't marked: {w.stage5()}")
    # truthful and immediate, in every unmarked world
    multi = 0
    for n, d in WW.W.items():
        w = S.world_of(d["text"])
        if w.tag() == 5:
            continue
        for lf in lives(n, 2):
            e = taste_truthful(lf, multi_ok=True)
            if e:
                errs.append(f"{n}: {e[0]}")
            ticks = {}
            for m in lf.tr.meals:
                ticks[m[0]] = ticks.get(m[0], 0) + 1
            multi += sum(v > 1 for v in ticks.values())
    print(f"   ticks with several meals, in those lives: {multi} (left out of the truthfulness test: the pulse is clipped)", flush=True)
    return errs


def g_refuses():
    from stage2_run import judged
    errs = []
    for n in ("delay1", "liar", "rewire50"):
        try:
            judged(n, "circuit", range(63000, 63001))
            errs.append(f"the runner ran {n} as a result")
        except ValueError:
            pass
    return errs


REJECT = ["(world (on tick (__import__ 1)))", "(world (on tick (set t 0)))", "(world (on tick (drop)))", "(world (let t 0))", "(world (on nowhere (set poison 0)))", "(world (on tick (set foo 1)))", "(world (on tick (set poison (open 1))))",
          "(world (const FOO 1))", "(world (on tick (set seen 1)))", "(world (on meal (after 1 (set sign 0))))", "(world (on tick (set poison (eval 1))))", "(world (on tick (at nosuch 1)))", "(world (on score (set poison))", "(world", "(world (on tick (repeat 1 (nonsense))))", "(world (on tick (if 1)))"]


def g_validator():
    errs = []
    for t in REJECT:
        try:
            lang.World(t)
            errs.append(f"accepted {t}")
        except (lang.LangError, IndexError):
            pass
        except Exception as e:
            errs.append(f"{t} raised {type(e).__name__}: {e}")
    return errs


def g_length():
    """Description length: what must leave it unchanged, and what must raise it."""
    errs = []
    L = lambda t: lang.bits(lang.World(t))
    base = "(world (let a 0) (on tick (set poison (if (< t 10) P a))) (on score (set a colour)))"
    same = {"renamed": base.replace("(let a", "(let zzz").replace("P a)", "P zzz)").replace("(set a", "(set zzz"),
            "comment and meta": "(world (meta (group x)) ; a comment\n (let a 0) (on tick (set poison (if (< t 10) P a))) (on score (set a colour)))",
            "stages reordered": "(world (on score (set a colour)) (let a 0) (on tick (set poison (if (< t 10) P a))))",
            "dead state": "(world (let a 0) (let junk 3) (let junk2 1) (on tick (set junk (+ junk 1)) (set junk2 junk) (set poison (if (< t 10) P a))) (on score (set a colour)))",
            "stream": "(world (stream 77) (let a 0) (on tick (set poison (if (< t 10) P a))) (on score (set a colour)))",
            "a number within the grid": base.replace("10", "10.01")}
    for k, t in same.items():
        if L(t) != L(base):
            errs.append(f"{k}: {L(t)} against {L(base)}")
    more = base.replace("(on score (set a colour))", "(on score (set a colour)) (on meal (if (> speed 0.03) (set sign -1))) (on pulse (if (= eye a) (drop)))")
    if not L(more) > L(base):
        errs.append("a longer world isn't longer")
    if L("(world)") != 0:
        errs.append("plain isn't 0 bits")
    live_rule = "(world (let a 0) (let k 3) (on tick (set a k) (set poison (if (< t 10) P a))) (on score (set k colour)))"
    if lang.canonical(lang.World(live_rule))[0].count("let") != 2:
        errs.append("the pruner removed live state")
    return errs


def run_general(ex):
    ok = True
    ok &= g_strict(ex)
    res = list(ex.map(g_leak, [n for n, d in WW.W.items()]))
    leak = [n for n, a, b, _ in res if not (a and b)]
    print(f"same seed same life; unaffected by earlier lives and worlds, in {len(res)} worlds: {'ok' if not leak else leak}", flush=True)
    ok &= not leak
    fr = list(ex.map(fresh, [(n, f) for n, _, _, f in res]))           # another process: hash() of floats and ints is stable across processes
    bad = [n for n, x in fr if not x]
    print(f"the same in another worker process, whatever ran there before: {'ok' if not bad else bad}", flush=True)
    ok &= not bad
    for name, f in (("shortcut", g_shortcut), ("stage5 mark and truthfulness", g_stage5), ("runner refuses stage 5", g_refuses), ("validator", g_validator), ("description length", g_length)):
        t0 = time.time()
        e = f()
        print(f"{name}: {'ok' if not e else e[:6]} ({time.time() - t0:.0f} s)", flush=True)
        ok &= not e
    return ok


# ---------------------------------------------------------------- the mutation test
def rep(name, old, new):
    return ("text", name, old, new)


MUT_WORLD = [
    ("swap10", rep("swap10", "(/ t 10)", "(/ t 10.5)")), ("swap10", rep("swap10", "(+ P ", "(+ F ")), ("swap11", rep("swap11", "(/ t 11)", "(/ t 10)")),
    ("alternate", rep("alternate", "(on score (set last colour))", "(on score (set last P))")), ("pattern", rep("pattern", "(= i 2) F P", "(= i 0) F P")), ("pattern", rep("pattern", "(mod (+ i 1) 3)", "(mod (+ i 1) 4)")),
    ("digest", rep("digest", "(or (= colour P) (< (- t was) 1))", "(or (= colour P) (< (- t was) 1.5))")), ("digest", rep("digest", "(on taste (if (< (- t was) 1) (set value -1)))", "")), ("digest", rep("digest", "(set was t)", "")),
    ("unreliable", rep("unreliable", "0.2", "0.25")), ("unreliable22", rep("unreliable22", "0.22", "0.2")), ("coin", rep("coin", "0.5", "0.45")),
    ("patchy", rep("patchy", "0.003", "0.006")), ("patchy", rep("patchy", "(table c 4 2", "(table c 1 2").__class__(("text", "patchy", "(int 4)", "(int 1)"))),
    ("weak", rep("weak", "0.25", "0.35")), ("weak", rep("weak", "(= eye e) ", "(>= eye 0) ")), ("dim25", rep("dim25", "0.25", "0.5")), ("dim25", rep("dim25", "(= colour c)", "(>= colour 0)")),
    ("noisy", rep("noisy", "(* 10 TICK)", "(* 12 TICK)")), ("noisy", rep("noisy", "(pulse e)", "(pulse (int 2))")),
    ("allfood", rep("allfood", "(set poison -1)", "(set poison (if (< t 10) P -1))")), ("never", rep("never", "1000", "90")),
    ("late_alternate_50", rep("late_alternate_50", "(< t 50)", "(< t 55)")), ("late_swap_50", rep("late_swap_50", "(< t 50)", "(< t 55)")), ("nlate_pattern_50", rep("nlate_pattern_50", "0.2", "0.3")),
    ("swapmeals6", rep("swapmeals6", "(/ n 6)", "(/ n 7)")), ("every5th", rep("every5th", "(mod n 5)", "(mod n 4)")), ("every5th", rep("every5th", "(= (mod n 5) 4)", "(chance 0.2)")),
    ("mirror", rep("mirror", "(drop) ", "")), ("halfthrust_const", rep("halfthrust_const", "(const TURN (* 0.5 TURN))", "")), ("halfthrust_gain", rep("halfthrust_gain", "0.5", "0.6")),
    ("thrusters", rep("thrusters", "(pow 2 (uniform -1 1))", "(pow 4 (uniform -1 1))")), ("fail50", rep("fail50", "(>= t 50)", "(>= t 500)")), ("drag2", rep("drag2", "(* 2 DRAG)", "(* 1.9 DRAG)")),
    ("moving", rep("moving", "0.005", "0.006")), ("scarce", rep("scarce", "3", "4")), ("blind", rep("blind", "0.055", "0.11")), ("blind", rep("blind", "(set last t)", "")), ("crosstalk", rep("crosstalk", "0.3", "0.2")),
    ("bruise", rep("bruise", "0.03", "0.04")), ("region", rep("region", "P F", "F P")), ("keylock", rep("keylock", "(- t key) 5", "(- t key) 8")), ("decoys", rep("decoys", "(set sign 0)", "")), ("decoys", rep("decoys", "(mod b 3)", "(mod b 4)")),
    ("rarefeast", rep("rarefeast", "0.05", "0.1")), ("rarefeast", rep("rarefeast", "(on score", "(on meal (if (chance 0.05) (set sign -1))) (on score")), ("costly", rep("costly", "THRUST 10", "THRUST 5")), ("sag", rep("sag", "(* 0.5 ", "(* 0.6 ")), ("sag", rep("sag", "(>= t 50)", "(>= t 40)")),
    ("parity", rep("parity", "(* s7 h7)", "(* s6 h7)")), ("word", rep("word", "(set i 0)", "(set i i)")), ("cells", rep("cells", "(= c 3)", "(= c 4)")), ("delay1", rep("delay1", "(after 1", "(after 2")), ("lostgood", rep("lostgood", "0.5", "0.6")),
]


def mut_world(args):
    check_, (_, name, old, new) = args
    t = WW.W[name]["text"]
    if old not in t:
        return check_, name, old, new, None
    WW.W[name]["text"] = t.replace(old, new)
    S._cache.clear()
    r = run_check(check_)
    WW.W[name]["text"] = t
    S._cache.clear()
    return check_, name, old, new, bool(r[1])


# engine mutations: each a patch made in a fresh process; `via` names what is run to catch it
def e_taste_stream():
    orig = sim.WLife.t_score

    def f(self, taste):
        r, self.rng = self.rng, self.r
        try:
            orig(self, taste)
        finally:
            self.rng = r
    sim.WLife.t_score = f


def e_rule_uses_body_stream():
    o = sim.WLife.__init__

    def f(self, seed, first, brain, world, stream=None, trace=False):
        o(self, seed, first, brain, world, stream, trace)
        self.r = self.rng
    sim.WLife.__init__ = f


def e_light_1e7():
    """A change in what an eye sees too small to change any draw in a short life: only the per-tick light in the fingerprint can catch it."""
    s = sim._sees
    sim._sees = lambda *a: s(*a) * 1.0000001


def e_no_cross_ray():
    """A block not hiding what's behind it (the first block a ray meets no longer the nearest)."""
    s = sim._look

    def f(xy, alive, h, fw, world, block, rng, eat, across):
        far, hit = s(xy, alive, h, fw, world, block, rng, eat, across)
        return far * 1.01, hit
    sim._look = f


def e_drag_early():
    o = sim.WLife.move

    def f(self):
        self.body.speed *= 0.999999
        return o(self)
    sim.WLife.move = f


def e_fire_order():
    o = sim.Body.fire

    def f(self, th, k):
        o(self, 1 - th, k)
    sim.Body.fire = f


def e_tell_on():
    o = S.make

    def f(world, arm, seed, first, kw=None, trace=False, tap=None):
        lf = o(world, arm, seed, first, kw, trace, tap)
        if arm == "bank":
            def tell(W):
                W.brain.food = W.rule_food(W) if W.rule_food(W) >= 0 else W.brain.food
            lf.tell = tell
        return lf
    S.make = f


def e_bad_end_of_tick():
    """Score reads the poison register after the meal's state has moved, not the taste's sign."""
    o = sim.WLife.t_score

    def f(self, taste):
        self.tick_meals = [(b, c, (-1.0 if c == 1 - self.poison else s)) for b, c, s in self.tick_meals]
        o(self, taste)
    sim.WLife.t_score = f


def e_state_leak():
    """A life's state survives into the next in the process: each world's variables start where the last life ended."""
    last = {}
    o = sim.WLife.__init__

    def f(self, seed, first, brain, world, stream=None, trace=False):
        o(self, seed, first, brain, world, stream, trace)
        prev = last.get(id(world))
        if prev is not None:
            for k, v in prev.__dict__.items():
                if k.startswith(("v_", "t_")):
                    setattr(self, k, v)
        last[id(world)] = self
    sim.WLife.__init__ = f


def e_at_leak():
    """The taste's moment carries its sign: the simulator offering a shortcut."""
    o = sim.WLife.t_score

    def f(self, taste):
        class G:
            def __init__(s, r):
                s.r = r

            def random(s):
                x = s.r.random()
                return x * 0.5 + (0.5 if taste > 0 else 0.0)
        r = self.rng
        self.rng = G(r)
        try:
            o(self, taste)
        finally:
            self.rng = r
    sim.WLife.t_score = f


def e_later_off_by_one():
    o = sim.WLife.later

    def f(self, d, fn):
        o(self, d + self.dt, fn)
    sim.WLife.later = f


def e_respawn_ignored():
    def f(self, b):
        self.body.xy[int(b)] = self.body.somewhere()
    sim.WLife.respawn_now = f


def e_prune_off():
    lang._prune.__globals__["_prune"] = lambda w: (set(w.vars) | set(w.tabs), w.rules)


def e_extra_wire():
    """A rule's state reaches the brain by a door besides the three wires."""
    o = sim.WLife.step

    def f(self):
        self.brain.hint = self.poison
        return o(self)
    sim.WLife.step = f


def e_pulse_tick_boundary():
    """Pulses all at the tick's start: lockstep."""
    o = sim.WLife.step
    b = None

    def f(self):
        if not getattr(self, "_wrapped", False):
            self._wrapped = True
            s = self.brain.stimulate
            self.brain.stimulate = lambda e, at: s(e, 0.0)
            tr = self.tr
            if tr is not None:
                class L(list):
                    def append(q, x):
                        list.append(q, (x[0], x[1], x[2], 0.0, x[4]))
                tr.pulses = L(tr.pulses)
        return o(self)
    sim.WLife.step = f


def _identity_quick():
    import stage2_repro as R
    fails = []
    for w in ("plain", "digest", "alternate", "patchy", "unreliable"):
        for arm in ("circuit", "bank"):
            for c in S.COL:
                a, b = R.ref((w, arm, 60000, c, 30.0)), R.lang_life((WW.W[w]["text"], arm, 60000, c, 30.0))
                ok, why = R.same(a, b)
                if not ok:
                    fails.append(f"{w} {arm} {c}: {why}")
    return fails


def _leak_quick():
    fails = []
    for n in ("alternate", "pattern", "digest", "keylock", "fail50"):
        _, a, b, _ = g_leak(n)
        if not (a and b):
            fails.append(n)
    return fails


MUT_ENGINE = [(e_taste_stream, "identity", _identity_quick), (e_rule_uses_body_stream, "identity", _identity_quick), (e_light_1e7, "identity", _identity_quick), (e_no_cross_ray, "identity", _identity_quick), (e_drag_early, "identity", _identity_quick), (e_fire_order, "identity", _identity_quick), (e_tell_on, "reproduction", _identity_quick),
              (e_bad_end_of_tick, "reproduction", _identity_quick), (e_state_leak, "no leak", _leak_quick), (e_at_leak, "shortcut", g_shortcut), (e_later_off_by_one, "delay1", lambda: run_check("delay1")[1]), (e_respawn_ignored, "reproduction", _identity_quick),
              (e_prune_off, "description length", g_length), (e_extra_wire, "strict brain", lambda: strict_one("plain")[1]), (e_pulse_tick_boundary, "shortcut", g_shortcut)]


def mut_engine(i):
    patch, via, test = MUT_ENGINE[i]
    patch()
    try:
        r = test()
    except Exception as e:
        r = [f"raised {type(e).__name__}: {e}"]
    return patch.__name__, via, r[:1]


def run_mutations():
    import multiprocessing as mp
    ctx = mp.get_context("fork")
    caught = missed = 0
    print("== world rules broken: each should fail its world's own check", flush=True)
    with ctx.Pool(7, maxtasksperchild=1) as p:
        for check_, name, old, new, r in p.imap(mut_world, MUT_WORLD):
            caught += r is True
            missed += r is False
            print(f"{'caught' if r else 'MISSED' if r is False else 'NOT APPLIED'}  {name}: {old} -> {new}", flush=True)
    print(f"world rules: caught {caught}, missed {missed}", flush=True)
    ecaught = 0
    print("== engine broken", flush=True)
    with ctx.Pool(7, maxtasksperchild=1) as p:
        for name, via, r in p.imap(mut_engine, range(len(MUT_ENGINE))):
            ecaught += bool(r)
            print(f"{'caught' if r else 'MISSED'}  {name}, by {via}" + (f": {str(r[0])[:110]}" if r else ""), flush=True)
    print(f"engine: caught {ecaught} of {len(MUT_ENGINE)}", flush=True)


# ---------------------------------------------------------------- finer step
def set_tick(dt):
    """Every module holding the tick (the body's, the brains') to dt: a worker's process only."""
    import types
    old = units.TICK
    for m in list(sys.modules.values()):
        if isinstance(m, types.ModuleType) and getattr(m, "TICK", None) == old:
            m.TICK = dt
    sim.WLife.dt = dt


def _fine(job):
    text, arm, seed, first, dt = job
    if sim.WLife.dt != dt:
        set_tick(dt)
    return S.live(S.make(S.world_of(text), arm, seed, first))


def run_finer(names=("plain", "swap10", "digest", "blind", "noisy", "bruise", "moving", "keylock"), seeds=range(63100, 63150)):
    from stage2_run import pdiff, ci_eff
    res = {}
    for dt in (0.01, 0.005):
        with ProcessPoolExecutor(7) as ex:
            for n in names:
                for arm in ("circuit", "bank"):
                    res[n, arm, dt] = list(ex.map(_fine, [(WW.W[n]["text"], arm, s, c, dt) for s in seeds for c in S.COL], chunksize=4))
                print(f"done {n} {dt}", flush=True)
    for n in names:
        for arm in ("circuit", "bank"):
            d, lo, hi = pdiff(res[n, arm, 0.005], res[n, arm, 0.01])
            print(f"{n:12s} {arm:8s} 10 ms {efficiency(res[n, arm, 0.01]):+.3f}  5 ms {efficiency(res[n, arm, 0.005]):+.3f}  difference {d:+.3f} [{lo:+.3f},{hi:+.3f}]  {'holds' if lo <= 0 <= hi else 'MOVES'}", flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1:] or ["worlds"]
    if cmd[0] == "worlds":
        with ProcessPoolExecutor(7) as ex:
            run_all(None, ex)
    elif cmd[0] == "general":
        with ProcessPoolExecutor(7) as ex:
            print("ALL OK" if run_general(ex) else "FAILURES", flush=True)
    elif cmd[0] == "mutate":
        run_mutations()
    elif cmd[0] == "finer":
        run_finer()
    elif cmd[0] == "all":
        with ProcessPoolExecutor(7) as ex:
            a = run_all(None, ex)
            b = run_general(ex)
        run_mutations()
        print("ALL OK" if a and b else "FAILURES", flush=True)
    elif cmd[0] in CHECKS:
        with ProcessPoolExecutor(7) as ex:
            run_all(cmd, ex)

"""stage2_repro.py: the identity and reproduction tests of stage 2a. The reference is the real creature.Life with the existing wrappers (lab/table.py, lab/stage1c_arms.py) in a copy of bits_bank.life's loop, itself checked against table.life and bits_bank.life. Compared tick by tick: position, heading, speed, spin, every block's position (a CRC of their bytes), every pulse and taste the brain receives with its moment, firings, meals as scored, the rows of the record, the body stream's final state.

    .venv/bin/python lab/stage2_repro.py [identity|nine|bonus|all] [nseeds]"""
import os
import sys
import time
import zlib
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from creature import Life
from minimal.spec import SPAN, Lived, thirds
import table as T
import bits_bank as B
import stage1c_arms as A                                 # adds late_*, nlate_*, coin to T.WORLDS
from units import TICK
from stage2_lang import arms as S, worlds as WW

SEEDS = range(60000, 60100)
ARMS = ("circuit", "bank", "vtold")


def tap(cls):
    class Tapped(cls):
        def __init__(self, seed, p):
            self._pl, self._tl = [], []
            super().__init__(seed, p)

        def stimulate(self, sensor, at):
            self._pl.append((round(self.t * 100), sensor, at))
            super().stimulate(sensor, at)

        def taste(self, value, at):
            self._tl.append((round(self.t * 100), value, at))
            super().taste(value, at)
    return Tapped


def crc(b):
    xy = b.xy[b.alive] if hasattr(b, "alive") else b.xy      # (a hidden block isn't in the world: scarce)
    seen = b.sees()
    seen = np.array(list(seen.values()), dtype=float) if isinstance(seen, dict) else seen      # what reaches the eyes, a pure function: a small error in it would change no draw in a short life
    return zlib.crc32(b.pos.tobytes() + np.float64(b.heading).tobytes() + b.speed.tobytes() + np.float64(b.spin).tobytes() + xy.tobytes() + seen.tobytes())


def ref(job):
    """The reference: real Life, existing wrappers. wrapper None: no wrapper at all, the unmodified Life."""
    wname, arm, seed, first, seconds = job
    q, cls = (T.numbers(seed, {}), T.Circuit) if arm == "circuit" else (T.numbers(seed, B.V7), B.VTold if arm == "vtold" else B.Recorder)
    cls = tap(cls)
    lf = Life(seed, first, brain=lambda s: cls(s, q))
    b = lf.brain
    ticks = int(round(seconds / TICK))
    fp = []
    if wname is None:
        if arm == "bank":                               # the record's watching columns, as the wrapper's loop fills them
            def spy0():
                here = [c for tk, c in lf.meals if tk == lf.t]
                return (lf.sensor[here[0]] if len(set(here)) == 1 else -1), lf.sensor[T.COL[1 - T.COL.index(first)]], 0
            b.spy = spy0
        while lf.t < ticks:
            lf.step()
            fp.append(crc(lf.body))
        l = Lived(thirds(lf.meals, lf.moving, ticks, first))
        meals = [(t, c == first) for t, c in lf.meals]
        rows = b.rows if hasattr(b, "rows") else []
        return dict(life=tuple(l), fp=fp, pulses=b._pl, tastes=b._tl, firings=lf.firings, meals=meals, rows=rows, rng=lf.rng.bit_generator.state["state"]["state"])
    R = T.WORLDS[wname](first)
    R.setup(lf, seed)

    def rule_food(t):
        tp = R.told_poison(t)
        return lf.sensor[T.COL[1 - T.COL.index(tp)]] if tp else -1

    def spy():
        here = []
        for tk, c in reversed(lf.meals):
            if tk != lf.t:
                break
            here.append(c)
        t = lf.t * T.TICK
        eaten = lf.sensor[here[0]] if len(set(here)) == 1 else -1
        return eaten, rule_food(t), 0
    if arm != "circuit":
        b.spy = spy
    if hasattr(R, "taste"):
        inner = b.taste
        b.taste = lambda v, at: inner(R.taste(v), at)
    labelled = 0
    while lf.t < ticks:
        t = lf.t * T.TICK
        po = R.poison(t)
        lf.poison, R.now = po, t
        if arm == "vtold":
            f = rule_food(t)
            if f >= 0:
                b.told_food = f
                b.food = f
        R.tick(lf, t)
        lf.step()
        fp.append(crc(lf.body))
        while labelled < len(lf.meals):
            tk, c = lf.meals[labelled]
            badm = R.bad(c, t) if hasattr(R, "bad") else c == po
            lf.meals[labelled] = (tk, "red" if badm else "blue")
            R.ate(c)
            labelled += 1
    l = Lived(thirds(lf.meals, lf.moving, ticks, "red"))
    meals = [(t, c == "red") for t, c in lf.meals]
    return dict(life=tuple(l), fp=fp, pulses=b._pl, tastes=b._tl, firings=lf.firings, meals=meals, rows=b.rows if hasattr(b, "rows") else [], rng=lf.rng.bit_generator.state["state"]["state"])


def lang_life(job):
    text, arm, seed, first, seconds = job
    lf = S.make(S.world_of(text), arm, seed, first, tap=tap)
    b = lf.brain
    ticks = int(round(seconds / TICK))
    fp = []
    while lf.t < ticks:
        lf.step()
        fp.append(crc(lf.body))
    return dict(life=tuple(lf.thirds(ticks)), fp=fp, pulses=b._pl, tastes=b._tl, firings=lf.firings, meals=[(t, bad) for t, bad, _ in lf.scored], rows=b.rows if hasattr(b, "rows") else [], rng=lf.rng.bit_generator.state["state"]["state"])


def same(a, b, rows_cols=None):
    """(True, "") or (False, where they first differ)."""
    if a["fp"] != b["fp"]:
        i = next(i for i, (x, y) in enumerate(zip(a["fp"], b["fp"])) if x != y)
        return False, f"body differs first at tick {i}"
    for k in ("pulses", "tastes", "firings", "meals"):
        if a[k] != b[k]:
            i = next((i for i, (x, y) in enumerate(zip(a[k], b[k])) if x != y), min(len(a[k]), len(b[k])))
            return False, f"{k} differ at {i}: {a[k][i:i + 1]} {b[k][i:i + 1]}"
    ra, rb = [r[:-1] for r in a["rows"]], [r[:-1] for r in b["rows"]]      # (the last column, bad, is watching only and differently labelled)
    if ra != rb:
        i = next((i for i, (x, y) in enumerate(zip(ra, rb)) if x != y), min(len(ra), len(rb)))
        return False, f"rows differ at {i}: {ra[i:i + 1]} {rb[i:i + 1]}"
    if a["life"] != b["life"]:
        return False, f"thirds differ {a['life']} {b['life']}"
    if a["rng"] != b["rng"]:
        return False, "body stream's final state differs"
    return True, ""


def job(args):
    wname, text, arm, seed, first, seconds = args
    a, b = ref((wname, arm, seed, first, seconds)), lang_life((text, arm, seed, first, seconds))
    ok, why = same(a, b)
    return wname, arm, seed, first, ok, why, len(a["fp"]), len(a["pulses"]), len(a["tastes"]), len(a["meals"])


def run(pairs, nseeds, arms=ARMS, seconds=100.0, label="", ex=None):
    jobs = [(rw, WW.W[lw]["text"], arm, s, c, seconds) for rw, lw in pairs for arm in arms for s in list(SEEDS)[:nseeds] for c in T.COL]
    t0 = time.time()
    res = list(ex.map(job, jobs, chunksize=2))
    bad = {}
    tot = {}
    for wname, arm, seed, first, ok, why, n, np_, nt, nm in res:
        d = tot.setdefault((wname, arm), [0, 0, 0, 0])
        d[0] += 1
        d[1] += int(ok)
        d[2] += nt
        d[3] += n
        if not ok:
            bad.setdefault((wname, arm), []).append((seed, first, why))
    for (wname, arm), d in tot.items():
        ex_ = bad.get((wname, arm))
        print(f"{label} {str(wname):18s} {arm:8s} {d[1]}/{d[0]} lives exact; {d[3]} ticks, {d[2]} tastes" + (f"  FIRST: {ex_[0]}" if ex_ else ""), flush=True)
    print(f"{label} {time.time() - t0:.0f} s", flush=True)
    return not bad


def real_vs_ref(ex, n=3):
    """The reference loop against the real functions, so that the reference isn't my own copy alone."""
    ok = True
    for w in ("plain", "digest", "unreliable", "patchy"):
        for seed in list(SEEDS)[:n]:
            for c in T.COL:
                a = T.life((w, "circuit", {}, seed, 100.0, c))
                r = ref((w, "circuit", seed, c, 100.0))
                b = B.life((w, "v_rec", {}, seed, 100.0, c))
                rb = ref((w, "bank", seed, c, 100.0))
                if tuple(a) != r["life"] or tuple(b) != rb["life"]:
                    ok = False
                    print("reference differs from the real life", w, seed, c, flush=True)
    print("reference loop = table.life and bits_bank.life:", "yes" if ok else "NO", flush=True)
    return ok


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    with ProcessPoolExecutor(7) as ex:
        ok = True
        if what in ("identity", "all"):
            ok &= run([(None, "plain")], n, arms=("circuit", "bank"), label="identity", ex=ex)
            ok &= run([("plain", "plain"), ("late_never", "never")], n, label="identity", ex=ex)
        if what in ("nine", "all"):
            ok &= run([(w, w) for w in B.WORLDS9], n, label="nine", ex=ex)
        if what in ("bonus", "all"):
            ok &= run([(w, w) for w in ("coin", "allfood", "scarce", "moving", "late_alternate_50", "late_swap_50", "nlate_pattern_50")], n, label="bonus", ex=ex)
            ok &= run([("thrusters", "thrusters")], n, arms=("circuit",), label="bonus", ex=ex)
        if what == "all":
            ok &= real_vs_ref(ex)
    print("ALL EXACT" if ok else "DIFFERENCES", flush=True)

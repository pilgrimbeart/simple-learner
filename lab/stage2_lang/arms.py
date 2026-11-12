"""arms.py: a life in a world, for an arm. The same arms and loop as lab/bits_bank.py's life (and lab/table.py's), over sim.WLife.

Arms: ref (stage 2b's frozen reference, lab/stage2b_reference.py); circuit (the base brain); bank (bits_bank.Recorder, the bank with its tastes recorded: lives identical to universal_v.V); fix (one model from birth); vtold (the bank's parts told the colour); vtoldw (and a told pause where the world states one); unwired (either eye drives, taste to nothing: a policy for wire signatures)."""
import json
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import numpy as np
from minimal.spec import SPAN, Lived
import table as T
import bits_bank as B
from stage2_lang.sim import WLife, COLOURS
from stage2_lang import lang

V7 = B.V7
COL = T.COL
_cache = {}


def world_of(text, name=None):
    if text not in _cache:
        _cache[text] = lang.World(text, name)
    return _cache[text]


FAST = True                                             # the brains' step compiled (fast.py): circuit and bank, seconds mode;
                                                        # lives identical (lab/speed_fingerprint.py, lab/speed_crosscheck.py)


def make(world, arm, seed, first, kw=None, trace=False, tap=None, seconds=None):
    """A life, not yet lived, for arm. tap: a class-maker that wraps the brain's class (watching only). seconds: the engine's mode
    (default sim.WLife.seconds); in seconds mode every brain is its seconds version (seconds.py), and the reference is RefS."""
    from stage2_lang.seconds import seconds_cls, ref_seconds
    secs = WLife.seconds if seconds is None else bool(seconds)
    kw = kw or {}
    if arm == "circuit":
        q, cls = T.numbers(seed, kw), T.Circuit
    elif arm == "unwired":
        q, cls = T.numbers(seed, kw), T.Unwired
    elif arm == "ref":                                  # stage 2b's frozen reference (lab/v/stage2b_reference.md); kw can't change it
        from stage2b_reference import Ref, FROZEN
        q, cls = T.numbers(seed, {**V7, **FROZEN}), (ref_seconds() if secs else Ref)
    else:
        q = T.numbers(seed, {**V7, **kw})
        cls = {"bank": B.Recorder, "fix": B.Fix, "vtold": B.VTold, "vtoldw": B.VTold}[arm]
    if secs:
        from stage2_lang import fast
        cls = fast.fast_cls(cls) if (FAST and arm in ("circuit", "bank") and not tap and not trace) else seconds_cls(cls)
    if tap:
        cls = tap(cls)
    lf = WLife(seed, first, (lambda s: cls(s, q)), world, trace=trace, seconds=secs)
    b = lf.brain

    def rule_food(W):
        tp = W.told_now                                 # computed once a tick, after the tick stage, outside any brain call (no draws)
        return W.wire_s[1 - tp] if tp is not None and tp >= 0 else -1
    lf.rule_food = rule_food
    if hasattr(b, "spy"):
        def spy():
            cs = [c for _, c, _ in lf.tick_meals]
            eaten = lf.wire_s[cs[0]] if cs and cs[0] < 2 and len(set(cs)) == 1 else -1
            return eaten, rule_food(lf), int(bool(cs and cs[0] == lf.poison))
        b.spy = spy
    if arm in ("vtold", "vtoldw"):
        wrong = int(kw.get("wrong", 0))
        wait = world.fn.get("told_wait") if arm == "vtoldw" else None

        def tell(W):
            f = rule_food(W)
            if f >= 0:
                b.told_food = f ^ wrong
                b.food = b.told_food
            if wait:
                b.P, b.est = 99.0, float(wait(W))
        lf.tell = tell
    return lf


def live(lf, seconds=100.0):
    ticks = int(round(seconds / lf.dt))
    while lf.t < ticks:
        lf.step()
    b = lf.brain
    l = Lived(lf.thirds(ticks))
    nf = lf.fire_weight if getattr(lf, "grow_at", None) is not None else len(lf.firings)   # (new parts: weighted by strength)
    l.power, l.firings, l.substrate = 3.7e-9, lf.THRUST0 * SPAN * nf / seconds, "silicon"
    l.rows = np.array(b.rows, dtype=float) if getattr(b, "rows", None) else np.zeros((0, len(B.COLS)))
    l.picks = list(getattr(b, "picks", ()))
    l.seed, l.first = lf.seed, lf.first
    from stage2_lang import instruments
    l.labels = instruments.labels(lf)
    return l


def one(job):
    """(world text, arm, kw, seed, first, seconds) -> Lived."""
    text, arm, kw, seed, first, seconds = job
    return live(make(world_of(text), arm, seed, first, kw), seconds)

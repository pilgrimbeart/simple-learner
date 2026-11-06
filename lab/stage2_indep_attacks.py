"""stage2_indep_attacks.py: independent check 3 (PROGRAMME.md, gate 2 to 3): sanity attacks on the engine.

  channels   every world of worlds.py, a few lives each, the brain behind a proxy that logs any attribute the engine
             reads or writes beyond stimulate, step and taste; and every taste value the brain receives
  moments    a taste's moment against its sign (KS), and a pulse's moment and call order in a world that injects pulses
  inert      worlds whose hooks exist but never act, lockstep against the plain engine and creature.Life
  stage5     which worlds the runner's guard refuses (lab/stage2_run.py: tag 5 or stage5()), marked and unmarked

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage2_indep_attacks.py"""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np


def _kp(d, n):
    """The Kolmogorov distribution's tail: p of a KS statistic d at effective size n (asymptotic)."""
    lam = (np.sqrt(n) + 0.12 + 0.11 / np.sqrt(n)) * d
    k = np.arange(1, 101)
    return float(min(1.0, max(0.0, 2 * np.sum((-1) ** (k - 1) * np.exp(-2 * k * k * lam * lam)))))


class _P:
    def __init__(self, p):
        self.pvalue = p


class stats:
    """No scipy in the venv: two-sample and uniform KS tests, asymptotic p."""

    @staticmethod
    def ks_2samp(a, b):
        a, b = np.sort(np.asarray(a)), np.sort(np.asarray(b))
        x = np.concatenate([a, b])
        d = np.max(np.abs(np.searchsorted(a, x, "right") / len(a) - np.searchsorted(b, x, "right") / len(b)))
        return _P(_kp(d, len(a) * len(b) / (len(a) + len(b))))

    @staticmethod
    def kstest(a, _):
        a = np.sort(np.asarray(a))
        n = len(a)
        i = np.arange(1, n + 1)
        d = max(np.max(i / n - a), np.max(a - (i - 1) / n))
        return _P(_kp(d, n))
from stage2_indep_identity import Proxy, brain_maker, state_life, run as identity_run

COL = ("red", "blue")


def life_log(job):
    text, kind, seed, first = job
    from stage2_lang.sim import WLife
    from stage2_lang import lang
    lf = WLife(seed, first, lambda s: Proxy(brain_maker(kind)(s)), lang.World(text))
    for _ in range(10000):
        if lf.ended:
            break
        lf.step()
    b = lf.brain
    return dict(log=b.log, other=sorted(set(b.other)), wire_s=list(lf.wire_s), meals=list(lf.meals), scored=list(lf.scored), seed=seed)


def channels(ex):
    from stage2_lang import worlds as WW
    print("== channels: what each world's engine touches on the brain beyond the interface, and the taste values it gets", flush=True)
    for name, d in WW.W.items():
        jobs = [(d["text"], k, s, c) for k in ("circuit", "bank") for s in range(64200, 64203) for c in COL]
        try:
            R = list(ex.map(life_log, jobs))
        except Exception as e:
            print(f"  {name}: raised {type(e).__name__}: {e}", flush=True)
            continue
        other = sorted(set(x for r in R for x in r["other"]))
        vals = sorted(set(x[2] for r in R for x in r["log"] if x[0] == "t"))
        sens = sorted(set(x[2] for r in R for x in r["log"] if x[0] == "s"))
        ats = [x[3] for r in R for x in r["log"] if x[0] in "st"]
        flag = "" if (not other and set(vals) <= {-1.0, 1.0} and set(sens) <= {0, 1} and all(0 <= a < 0.01 for a in ats)) else "  <-- beyond the interface"
        print(f"  {name}: other {other}; taste values {vals}; sensors {sens}; moments in [0, dt): {all(0 <= a < 0.01 for a in ats)}{flag}", flush=True)


def moments(ex):
    from stage2_lang import worlds as WW
    print("== moments", flush=True)
    for name in ("plain", "digest", "every5th", "unreliable", "pattern", "bruise", "keylock"):
        jobs = [(WW.W[name]["text"], k, s, c) for k in ("circuit", "bank") for s in range(64300, 64340) for c in COL]
        R = list(ex.map(life_log, jobs, chunksize=2))
        good = np.array([x[3] for r in R for x in r["log"] if x[0] == "t" and x[2] > 0]) / 0.01
        bad = np.array([x[3] for r in R for x in r["log"] if x[0] == "t" and x[2] < 0]) / 0.01
        ks = stats.ks_2samp(good, bad)
        u1, u2 = stats.kstest(good, "uniform"), stats.kstest(bad, "uniform")
        print(f"  {name}: tastes good {len(good)}, bad {len(bad)}; moment good vs bad KS p {ks.pvalue:.3f}; each against uniform p {u1.pvalue:.3f}, {u2.pvalue:.3f};"
              f" mean {good.mean():.4f} vs {bad.mean():.4f}", flush=True)
        if name == "plain":
            # where in the tick's calls the taste comes: always after the step (so its tick is the meal's)?
            pass
    # pulses: in noisy, the injected pulses come first in a tick. How much does call order give away?
    jobs = [(WW.W["noisy"]["text"], "circuit", s, c) for s in range(64300, 64340) for c in COL]
    R = list(ex.map(life_log, jobs, chunksize=2))
    tell = tot_e = 0
    at_e, at_o = [], []
    for r in R:
        e = int(np.random.default_rng(r["seed"] + 5_500_011).integers(2))
        ticks = {}
        for x in r["log"]:
            if x[0] == "s":
                ticks.setdefault(x[1], []).append(x[2])
                (at_e if x[2] == e else at_o).append(x[3] / 0.01)
        first_eye = r["wire_s"][0]                  # the body delivers colour 0's eye first, then colour 1's
        for t, seq in ticks.items():
            tot_e += seq.count(e)
            if e != first_eye:                      # an e-pulse before any other-eye pulse, in a tick that has one, is injected
                j = seq.index(1 - e) if (1 - e) in seq else None
                if j is not None:
                    tell += seq[:j].count(e)
    print(f"  noisy: pulse moments, noisy eye vs other, KS p {stats.ks_2samp(at_e, at_o).pvalue:.3f}; noisy-eye pulses {tot_e}, of which"
          f" {tell} ({tell / max(1, tot_e):.4f}) are given away as injected by coming before the other eye's in their tick", flush=True)
    # plain: does call order within a tick give away the colour? (it does in creature.Life too: colour 0's eye first)
    jobs = [("(world)", "circuit", s, c) for s in range(64300, 64340) for c in COL]
    R = list(ex.map(life_log, jobs, chunksize=2))
    mixed = order_says = 0
    for r in R:
        ticks = {}
        for x in r["log"]:
            if x[0] == "s":
                ticks.setdefault(x[1], []).append(x[2])
        for seq in ticks.values():
            if len(set(seq)) == 2:
                mixed += 1
                order_says += seq[0] == r["wire_s"][0]
    print(f"  plain: ticks with both eyes' pulses {mixed}; in {order_says} the first call is colour 0's eye (as creature.Life does)", flush=True)


def two_engines(job):
    """Lockstep: world text A against world text B, both in the engine; exact body state and brain calls."""
    ta, tb, kind, seed, first = job
    from stage2_lang.sim import WLife
    from stage2_lang import lang
    mk = brain_maker(kind)
    A = WLife(seed, first, lambda s: Proxy(mk(s)), lang.World(ta))
    B = WLife(seed, first, lambda s: Proxy(mk(s)), lang.World(tb))
    for k in range(10000):
        A.step()
        B.step()
        if not np.array_equal(state_life(A), state_life(B)) or A.brain.log != B.brain.log:
            return k
    return None if A.scored == B.scored and A.meals == B.meals else -1


INERT = ["(world (let last -1) (on tick (set poison (if (< t 1000) P last))) (on score (if (>= t 1000) (set last colour))))",
         "(world (on see (set seen seen)))", "(world (on see (set seen (* 1 seen))))",
         "(world (on pulse (if (> t 1000) (drop))))", "(world (on fire (set gain 1)))", "(world (on fire (set gain gain)))",
         "(world (on meal (set sign sign)))", "(world (on taste (set value value)))",
         "(world (on score (set bad bad) (set amount amount)))", "(world (on move (set x x) (set spin spin)))",
         "(world (let z 0) (on tick (set z (chance 0.5))))", "(world (let z (uniform 0 1)) (table q 36 2 (normal 0 1)) (on tick (set z (+ z (at q 3 1)))))",
         "(world (on tick (if (> t 1000) (set poison F))))", "(world (on tick (set poison P)))", "(world (const PUSH PUSH) (const EAT EAT))",
         "(world (on birth (each b (bset b (bx b) (by b)))))", "(world (stream 123) (on tick (set poison (if (and (chance 0.5) (> t 1000)) F P))))",
         "(world (on tick (if (> t 1000) (pulse 0))))", "(world (on tick (after 2000 (pulse 0))))",
         "(world (on pulse (if (and (> t 1000) (chance 0.5)) (drop))))"]


def inert(ex):
    print("== inert: hooks that never act, against creature.Life (identity instrument) and the plain engine", flush=True)
    for text in INERT:
        jobs = [(k, s, c, 100.0, text) for k in ("circuit", "bank") for s in range(64400, 64410) for c in COL]
        identity_run(jobs, f"  {text}", ex=ex)
    print("== exact equalities the worlds claim", flush=True)
    from stage2_lang import worlds as WW
    for a, b in (("halfthrust_const", "halfthrust_gain"), ("plain", "never"), ("plain", "mirror"), ("weak", "dim25")):
        R = list(ex.map(two_engines, [(WW.W[a]["text"], WW.W[b]["text"], k, s, c) for k in ("circuit", "bank") for s in range(64400, 64425) for c in COL]))
        print(f"  {a} vs {b}: {sum(r is None for r in R)} of {len(R)} lives identical; first differing ticks {sorted(r for r in R if r is not None)[:8]}", flush=True)


def guarded(w):
    return w.tag() == 5 or bool(w.stage5())       # lab/stage2_run.py's guard, line 17


STAGE5 = {"unmarked delay1": "(world (on taste (drop) (after 1 (taste value))))",
          "unmarked lostgood": "(world (on taste (if (and (> value 0) (chance 0.5)) (drop))))",
          "unmarked rewire50": "(world (let done 0) (on tick (if (and (>= t 50) (= done 0)) (do (set done 1) (wire-sensor 0 (sensor 1)) (wire-sensor 1 (- 1 (sensor 1)))))))",
          "unmarked lethal": "(world (on score (if (and bad (chance 0.05)) (end))))",
          "unmarked liar": "(world (on taste (set value (- value))))",
          "liar, lying meta only": "(world (meta (lying 1)) (on taste (set value (- value))))",
          "random liar": "(world (on taste (if (chance 0.3) (set value (- value)))))",
          "taste of 0": "(world (on taste (set value 0)))",
          "taste of .5": "(world (on taste (set value (* 0.5 value))))",
          "score against taste": "(world (on score (set bad (not bad))))",
          "brain written (bp)": "(world (on tick (if (>= t 50) (bp hold 0.001))))",
          "brain told food (bp)": "(world (on tick (bp food (sensor F))))",
          "taste from the score stage": "(world (on score (if (chance 0.1) (after 0.01 (pulse 0)))))",
          "meal dropped, block uneaten": "(world (on meal (if (chance 0.5) (drop))))",
          "colours swapped (truthful)": "(world (on meal (set sign (- sign))))",
          "world fires a thruster": "(world (on tick (if (chance 0.01) (thrust 0))))"}


def stage5(ex):
    print("== stage 5: refused by the runner's guard?", flush=True)
    from stage2_lang import worlds as WW, lang
    import stage2_run as R
    for name, d in WW.W.items():
        w = lang.World(d["text"], name)
        if w.tag() == 5 or w.stage5() or "STAGE 5" in d["desc"]:
            try:
                R.guard(name)
                print(f"  {name}: NOT refused by stage2_run.guard", flush=True)
            except ValueError as e:
                print(f"  {name}: refused ({e})", flush=True)
    for name, text in STAGE5.items():
        w = lang.World(text)
        res = life_log((text, "circuit", 64500, "red"))
        vals = sorted(set(x[2] for x in res["log"] if x[0] == "t"))
        print(f"  {name}: guard {'refuses' if guarded(w) else 'ACCEPTS'} ({w.stage5()}); a life runs: taste values {vals[:6]}; brain attrs {res['other']}", flush=True)


if __name__ == "__main__":
    parts = sys.argv[1:] or ["channels", "moments", "inert", "stage5"]
    with ProcessPoolExecutor(7) as ex:
        for p in parts:
            globals()[p](ex)

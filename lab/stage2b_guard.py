"""stage2b_guard.py: stage 2b, part 1 (a) and (b). The brain channel closed and the stage-5 guard by what a world can do.

  static    every world: the hand worlds, stage 5's, the retired, the checker's attacks (lab/stage2_indep_attacks.py, STAGE5) and mine.
            lang.World(text) refuses, or compiles it.
  dynamic   every world the static guard lets through: lives on seeds 65100-65119 x 2, base and bank, each run by the three ways a life
            can be run (arms.one, the runner stage2_run.judged's loop, sim.WLife stepped by hand); the share refused by the engine, and why.
  paths     a refused world can't be lived by any path: World(..., compile_only=True) gives a world sim.WLife won't take, and a World whose
            refusal is cleared by hand still can't do what it does (the engine refuses in the tick).

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage2b_guard.py > lab/v/stage2b_guard.log"""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from stage2_lang import lang, worlds as WW
from stage2_lang.sim import Refused

SEEDS = range(65100, 65120)
COL = ("red", "blue")

# the checker's attacks, verbatim (lab/stage2_indep_attacks.py, STAGE5)
CHECKER = {"unmarked delay1": "(world (on taste (drop) (after 1 (taste value))))",
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

# mine: each capability reached another way
MINE = {"brain read (bpget)": "(world (on tick (set poison (bpget food))))",
        "an each variable that names the brain": "(world (on tick (each W.brain.p (set poison P))))",
        "taste always good, literal": "(world (on taste (set value 1)))",
        "taste always bad, literal": "(world (on taste (set value -1)))",
        "sign .5, literal": "(world (on meal (set sign 0.5)))",
        "sign halved": "(world (on meal (set sign (* 0.5 sign))))",
        "sign doubled": "(world (on meal (set sign (* 2 sign))))",
        "amount -1, literal": "(world (on score (set amount -1)))",
        "amount negated": "(world (on score (set amount (- 0 amount))))",
        "food worth nothing, tasting good": "(world (on score (if (not bad) (set amount 0))))",
        "poison worth nothing, tasting bad": "(world (on score (if bad (set amount 0))))",
        "decoy that tastes": "(world (on birth (each b (if (= (mod b 3) 0) (bkind b 2)))))",
        "COST -2, literal": "(world (const COST -2))",
        "COST negated mid-life": "(world (on tick (if (>= t 50) (set COST (- 0 2)))))",
        "THRUST -1": "(world (const THRUST -1))",
        "an extra score": "(world (on score (score 5)))",
        "an end by chance": "(world (on tick (if (chance 0.001) (end))))",
        "a taste injected at birth": "(world (on birth (taste 1)))",
        "a motor rewiring": "(world (on tick (if (>= t 50) (wire-motor 0 (- 1 (motorof 0))))))",
        "a taste dropped when two meals": "(world (on taste (if (> (abs value) 2) (drop))))",
        "the score inverted at the meal": "(world (on score (set bad (= colour F))))",
        "lies about worth, taste truthful (unreliable)": WW.W["unreliable"]["text"],
        "steering reversed at 50 s (mimics a rewiring)": "(world (on fire (if (>= t 50) (do (drop) (thrust (- 1 thruster))))))",
        "eyes exchanged at 50 s (mimics a rewiring)": "(world (on see (if (>= t 50) (set seen (raw (- 1 colour))))))",
        "digest as stage 2a wrote it": "(world (let was -1000000000.0) (told-wait 1) (on taste (if (< (- t was) 1) (set value -1))) (on score (set bad (or (= colour P) (< (- t was) 1))) (set was t)))",
        "digest at the meal (stage 2b)": "(world (let was -1000000000.0) (told-wait 1) (on meal (if (< (- t was) 1) (set sign -1)) (set was t)))"}


def static():
    print("== static: lang.World(text) refuses, or compiles", flush=True)
    sets = [("hand", {n: d["text"] for n, d in WW.W.items()}), ("stage 5", {n: d["text"] for n, d in WW.STAGE5.items()}),
            ("retired", {n: d["text"] for n, d in WW.RETIRED.items()}), ("checker", CHECKER), ("mine", MINE)]
    ok = {}
    for label, texts in sets:
        for n, t in texts.items():
            try:
                lang.World(t, n)
                ok[(label, n)] = t
                print(f"  {label:8s} {n:46s} compiles", flush=True)
            except lang.Refused as e:
                print(f"  {label:8s} {n:46s} REFUSED: {'; '.join(lang.World(t, n, compile_only=True).refused)}", flush=True)
            except lang.LangError as e:
                print(f"  {label:8s} {n:46s} NOT A PROGRAM: {e}", flush=True)
    return ok


def by_arms(job):
    from stage2_lang import arms as S
    text, arm, seed, first = job
    try:
        S.one((text, arm, {}, seed, first, 100.0))
        return None
    except Refused as e:
        return str(e).split(":")[0]


def by_runner(job):
    """stage2_run.judged's loop for a world that isn't in worlds.py: the same S.one jobs (judged() adds only its guard by name)."""
    import stage2_run as R
    from stage2_lang import arms as S
    text, arm, seed, first = job
    try:
        [S.one(j) for j in [(text, arm, {}, seed, first, 100.0)]]
        return None
    except Refused as e:
        return str(e).split(":")[0]


def by_hand(job):
    """sim.WLife stepped by hand, with a bare brain: no arms, no runner."""
    from stage2_lang.sim import WLife
    import table as T
    text, arm, seed, first = job
    lf = WLife(seed, first, lambda s: T.Circuit(s, T.numbers(s, {})), lang.World(text))
    try:
        for _ in range(10000):
            lf.step()
        return None
    except Refused as e:
        return str(e).split(":")[0]


def dynamic(ok, ex):
    print(f"\n== dynamic: lives on {SEEDS.start}-{SEEDS.stop - 1} x 2, base and bank, by arms.one, the runner's loop and sim.WLife by hand;"
          " lives refused by the engine and why (first reason of each life)", flush=True)
    for (label, n), t in ok.items():
        out = []
        for fn in (by_arms, by_runner, by_hand):
            arms = ("circuit", "bank") if fn is not by_hand else ("circuit",)
            R = list(ex.map(fn, [(t, a, s, c) for a in arms for s in SEEDS for c in COL], chunksize=2))
            k = Counter(r for r in R if r)
            out.append(f"{sum(k.values())}/{len(R)}" + (f" {dict(k)}" if k else ""))
        print(f"  {label:8s} {n:46s} refused lives: arms {out[0]}; runner {out[1]}; by hand {out[2]}", flush=True)


def paths():
    print("\n== paths: no way round the guard", flush=True)
    from stage2_lang.sim import WLife
    import table as T
    for n, t in (("unmarked liar", CHECKER["unmarked liar"]), ("unmarked delay1", CHECKER["unmarked delay1"]), ("an end by chance", MINE["an end by chance"])):
        w = lang.World(t, n, compile_only=True)
        try:
            WLife(65100, "red", lambda s: T.Circuit(s, T.numbers(s, {})), w)
            print(f"  {n}: compile-only world LIVED", flush=True)
        except Refused as e:
            print(f"  {n}: compile-only world not lived ({e})", flush=True)
        w.fn, w.refused = lang.compile_world(w), []         # the refusal cleared by hand: what the engine does on its own
        lf = WLife(65100, "red", lambda s: T.Circuit(s, T.numbers(s, {})), w)
        try:
            for _ in range(10000):
                lf.step()
            print(f"  {n}, refusal cleared by hand: a whole life LIVED", flush=True)
        except Refused as e:
            print(f"  {n}, refusal cleared by hand: the engine refuses at tick {lf.t} ({e})", flush=True)


if __name__ == "__main__":
    ok = static()
    paths()
    with ProcessPoolExecutor(7) as ex:
        dynamic(ok, ex)

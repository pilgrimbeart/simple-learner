"""stage2_indep2_guard.py: the stage-2b guard and brain channel, attacked (PROGRAMME.md, gate 2 to 3).

  old       the 16 attacks of lab/stage2_indep_attacks.py: refused statically (lang.Refused), in a life (sim.Refused), or accepted
  brain     texts that try to reach the brain object; and a (told e) that draws, evaluated inside the bank's taste by arms.py's spy
  new       worlds built to do what stage 5 is for while staying honest in every tick, each measured from the lives by my own code
  runner    the accepted ones through the builder's runner (arms.one) too

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage2_indep2_guard.py"""
import math
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from stage2_indep_identity import Proxy, brain_maker, state_life
from stage2_indep_attacks import STAGE5 as OLD

COL = ("red", "blue")
HEAD = "(+ x (* RADIUS (cos heading))) (+ y (* RADIUS (sin heading)))"     # the mouth, after the move

NEW = {
    "rewire by see at 50 s": "(world (on see (if (>= t 50) (set seen (raw (- 1 colour))))))",
    "rewire by look at 50 s": "(world (let done 0) (on tick (if (and (>= t 50) (= done 0)) (do (set done 1) (each b (blook b (- 1 (look b))))))))",
    "rewire by fire at 50 s": "(world (on fire (if (>= t 50) (do (drop) (thrust (- 1 thruster))))))",
    "life ended at first poison (body frozen)": "(world (let dead 0) (on score (if bad (set dead 1))) (on fire (if (= dead 1) (drop))))",
    "poison taste 1 s late (block hidden, put under the mouth)":
        f"(world (table due N 1 0) (on meal (if (and (= colour P) (= (at due block) 0)) (do (drop) (hide block) (put due block 1)"
        f" (after 1 (show block) (bset block {HEAD}))))) (on score (put due block 0)))",
    "verdicts swapped in food+poison ticks (forced)":
        f"(world (let m 0) (let s 0) (on tick (set m 0) (set s 0)) (on move (if (chance 0.02) (do (bset 0 {HEAD}) (bset 18 {HEAD}))))"
        " (on meal (set m (+ m 1)) (set s (+ s sign))) (on score (if (and (= m 2) (= s 0)) (set bad (not bad)))))",
    "one meal bad under a +1 taste (three food, forced)":
        f"(world (let m 0) (let k 0) (on tick (set poison -1) (set m 0) (set k 0)) (on move (if (chance 0.02) (do (bset 0 {HEAD}) (bset 1 {HEAD}) (bset 2 {HEAD}))))"
        " (on meal (set m (+ m 1))) (on score (if (and (>= m 3) (= k 0)) (set bad 1)) (set k (+ k 1))))",
    "food worth 1e-6, tasting +1": "(world (on score (if (not bad) (set amount 0.000001))))",
    "poison worth 1000, tasting -1": "(world (on score (if bad (set amount 1000))))",
    "COST 1e-4 from 50 s": "(world (on tick (if (>= t 50) (set COST 0.0001))))",
    "COST -1 from 50 s, by expression": "(world (on tick (if (>= t 50) (set COST (- 0 1)))))",
    "taste inverted by literals": "(world (on taste (if (= value 1) (set value -1) (set value 1))))",
    "taste inverted by literals, score inverted too": "(world (on taste (if (= value 1) (set value -1) (set value 1))) (on score (set bad (not bad))))",
    "half the food tastes lost, worth kept": "(world (on meal (if (and (= colour F) (chance 0.5)) (set sign 0))) (on score (if (= colour F) (set amount 1))))",
    "a Python error on poison (1/0)": "(world (on score (if bad (set amount (/ 1 (- 1 1))))))",
    "a Python error on poison (log -1)": "(world (on score (if bad (set amount (log (- 0 1))))))",
    "food+food tick, one meal worth 0": f"(world (let k 0) (on tick (set poison -1) (set k 0)) (on move (if (chance 0.02) (do (bset 0 {HEAD}) (bset 1 {HEAD})))) (on score (if (= k 0) (set amount 0)) (set k (+ k 1))))",
}

BRAIN = ["(world (on tick (set poison W)))", "(world (let W 0) (on tick (set W 1)))", "(world (table brain 1 1 0) (on tick (put brain 0 0 1)))",
         "(world (on tick (set poison (W.brain.p))))", "(world (on tick (set poison (__import__ 1))))", "(world (each brain (set poison 0)))",
         "(world (on tick (each W (set poison 0))))", "(world (let math 0) (on tick (set math 1)))", "(world (on tick (set poison (bpget hold))))",
         "(world (on tick (bp hold 1)))", "(world (let x_W 0))", "(world (on tick (set poison (at brain 0))))", "(world (const brain 1))",
         "(world (on tick (set dt 0.02)))", "(world (on tick (set now 5)))", "(world (on tick (set rng 0)))", "(world (on tick (set TICK 0.02)))",
         "(world (on tick (set P F)))", "(world (on tick (set seen 1)))", "(world (on pulse (set eye 1)))", "(world (on fire (set motor 1)))"]


def life(job):
    """A life, run until done or refused, and what I measure of it."""
    text, kind, seed, first, runner = job
    from stage2_lang import lang, sim
    try:
        w = lang.World(text)
    except lang.Refused as e:
        return dict(static=str(e)[:160])
    except Exception as e:
        return dict(compile=f"{type(e).__name__}: {str(e)[:120]}")
    if runner:
        from stage2_lang import arms
        try:
            l = arms.one((text, "circuit" if kind == "circuit" else "bank", {}, seed, first, 100.0))
            return dict(runner_ok=True, food=sum(a for a, b, _ in l[:3]))
        except Exception as e:
            return dict(runner=f"{type(e).__name__}: {str(e)[:120]}")
    lf = sim.WLife(seed, first, lambda s: Proxy(brain_maker(kind)(s)), w)
    alive_was = lf.body.alive.copy()
    hides, unhide = {}, []
    out = dict(refused=None)
    try:
        for k in range(10000):
            lf.step()
            a = lf.body.alive
            for b in np.flatnonzero(alive_was & ~a):
                hides[int(b)] = k
            alive_was = a.copy()
    except sim.Refused as e:
        out["refused"] = (k, str(e)[:120])
    except Exception as e:
        out["error"] = (k, f"{type(e).__name__}: {str(e)[:100]}")
    P = COL.index(first)
    meals = lf.meals
    out["meals"] = len(meals)
    out["thirds"] = lf.thirds(10000) if out["refused"] is None and "error" not in out else None
    bad_t = [t for (t, b, am) in lf.scored if b]
    out["first_bad"] = bad_t[0] if bad_t else None
    out["after_first_bad"] = sum(1 for t, _ in meals if bad_t and t > bad_t[0])
    tv = {}
    for x in lf.brain.log:
        if x[0] == "t":
            tv[x[1] - 1] = x[2]
    # per tick: meals, the engine's verdicts, the taste delivered
    by = {}
    for (t, c), (t2, b, am) in zip(meals, lf.scored):
        by.setdefault(t, []).append((c, b, am))
    out["bad_under_good"] = sum(1 for t, ms in by.items() if tv.get(t) == 1.0 for c, b, am in ms if b)
    out["mixed_swapped"] = sum(1 for t, ms in by.items() if len(ms) == 2 and {c for c, _, _ in ms} == set(COL) and t not in tv
                               and any(b != (COL.index(c) == P) for c, b, _ in ms))
    out["mixed"] = sum(1 for t, ms in by.items() if len(ms) == 2 and {c for c, _, _ in ms} == set(COL))
    out["ticks3"] = sum(1 for ms in by.values() if len(ms) >= 3)
    out["poison_meals"] = sum(1 for t, b, am in lf.scored if b)
    out["amounts"] = (sum(am for t, b, am in lf.scored if not b), sum(am for t, b, am in lf.scored if b))
    out["tastes"] = (sum(v > 0 for v in tv.values()), sum(v < 0 for v in tv.values()))
    out["hides"] = len(hides)
    # pulses per eye before and after 50 s against what each colour's eye would get (stimulate counts only)
    pul = np.zeros((2, 2))
    for x in lf.brain.log:
        if x[0] == "s":
            pul[int(x[1] >= 5000), x[2]] += 1
    out["pulses"] = pul.tolist()
    out["wire_s"] = list(lf.wire_s)
    return out


def tally(name, R):
    if "static" in R[0]:
        return f"{name}: REFUSED statically ({R[0]['static']})"
    if "compile" in R[0]:
        return f"{name}: does not compile ({R[0]['compile']})"
    ref = [r for r in R if r["refused"]]
    err = [r for r in R if r.get("error")]
    s = f"{name}: {len(R) - len(ref) - len(err)} of {len(R)} lives accepted"
    if ref:
        s += f"; REFUSED in {len(ref)} (first at tick {min(r['refused'][0] for r in ref)}: {ref[0]['refused'][1]})"
    if err:
        s += f"; CRASHED in {len(err)} ({err[0]['error'][1]})"
    ok = [r for r in R if not r["refused"] and not r.get("error")]
    if ok:
        g = lambda k: sum(r[k] for r in ok)
        s += (f"; meals {g('meals')}, scored bad {g('poison_meals')}, tastes +{sum(r['tastes'][0] for r in ok)}/-{sum(r['tastes'][1] for r in ok)};"
              f" bad meals under a +1 taste {g('bad_under_good')}; food+poison ticks {g('mixed')}, verdicts against colour in them {g('mixed_swapped')};"
              f" 3-meal ticks {g('ticks3')}; amounts good {sum(r['amounts'][0] for r in ok):.4g}, bad {sum(r['amounts'][1] for r in ok):.4g};"
              f" meals after the first bad {g('after_first_bad')}; blocks hidden {g('hides')}")
    return s


def rewire_check(R):
    """After 50 s, each eye's share of pulses: does it follow the other colour? (pulses per eye, before / after)."""
    p = np.array([r["pulses"] for r in R if not r["refused"]]).sum(0)
    return f"pulses per eye before 50 s {p[0].astype(int).tolist()}, after {p[1].astype(int).tolist()}"


def told_draw(job):
    """The bank through arms.py (Recorder, spy) against universal_v.V in the same world, lockstep."""
    text, seed, first = job
    from stage2_lang import arms, lang, sim
    A = arms.make(arms.world_of(text), "bank", seed, first)
    B = sim.WLife(seed, first, brain_maker("bank"), lang.World(text))
    for k in range(10000):
        A.step()
        B.step()
        if not np.array_equal(state_life(A), state_life(B)):
            return k
    return None


if __name__ == "__main__":
    seeds = range(64600, 64620)
    with ProcessPoolExecutor(7) as ex:
        print("== the old attacks (lab/stage2_indep_attacks.py's STAGE5)", flush=True)
        for name, text in OLD.items():
            R = list(ex.map(life, [(text, "circuit", s, c, False) for s in seeds for c in COL]))
            print("  " + tally(name, R), flush=True)
        print("== reaching the brain", flush=True)
        for text in BRAIN:
            r = life((text, "circuit", 64600, "red", False))
            print(f"  {text}: " + (r.get("static") or r.get("compile") or f"compiles and lives; refused {r['refused']}"), flush=True)
        told = "(world (told (if (chance 0.5) P F)) (on tick (set poison (if (chance 0.2) F P))))"
        for t in (told, "(world (told P) (on tick (set poison (if (chance 0.2) F P))))"):
            R = list(ex.map(told_draw, [(t, s, c) for s in seeds for c in COL]))
            print(f"  bank via arms.py (spy) vs universal_v.V, {t}: {sum(r is None for r in R)} of {len(R)} identical; first differing ticks {sorted(r for r in R if r is not None)[:6]}", flush=True)
        print("== new attacks", flush=True)
        for name, text in NEW.items():
            R = list(ex.map(life, [(text, k, s, c, False) for k in ("circuit", "bank") for s in seeds for c in COL]))
            print("  " + tally(name, R), flush=True)
            if name.startswith("rewire"):
                print("     " + rewire_check(R), flush=True)
        print("== through the builder's runner (arms.one)", flush=True)
        for name, text in list(NEW.items()) + list(OLD.items()):
            R = list(ex.map(life, [(text, "circuit", s, c, True) for s in range(64600, 64604) for c in COL]))
            st = R[0].get("static") or R[0].get("compile")
            print(f"  {name}: " + (f"refused statically" if st else f"{sum(1 for r in R if r.get('runner_ok'))} of {len(R)} run; {[r.get('runner') for r in R if r.get('runner')][:1]}"), flush=True)

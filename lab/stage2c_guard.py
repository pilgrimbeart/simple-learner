"""stage2c_guard.py: stage 2c, parts 1 and 2. The interface by construction, and stage 5's kinds labelled by instruments.

  static     the checker's attacks (lab/stage2_indep2_guard.py's NEW, BRAIN; lab/stage2_indep_attacks.py's STAGE5), verbatim, and my
             translations of each into the stage-2c language where one exists: does it compile, is it refused?
  told       a (told e) that draws no longer compiles; with an honest told, the bank through arms (legacy mode) against universal_v.V,
             lockstep, in a world that draws at every meal: identical?
  lives      every world that compiles: lives on seeds 66690-66709 x 2, base and bank, in seconds mode, through arms.one (the runner's
             path); refused lives (and why), and each instrument's labels (lab/stage2_lang/instruments.py). The hand worlds give each
             instrument's false-positive rate.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage2c_guard.py > lab/v/stage2c_guard.log"""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from stage2_lang import lang, worlds as WW
import stage2_indep2_guard as C2
import stage2_indep_attacks as C1

SEEDS = range(66690, 66710)
COL = ("red", "blue")
HEAD = C2.HEAD

# my translations of the checker's attacks into the stage-2c language: each tries the same thing with the words left
MINE = {
    "life ended at first poison (body frozen), by worth": "(world (let dead 0) (on score (if (< worth 0) (set dead 1))) (on fire (if (= dead 1) (drop))))",
    "food worth 1e-6, literal": "(world (on meal (if (> worth 0) (set worth 0.000001))))",
    "food worth 1e-6, by expression": "(world (on meal (if (> worth 0) (set worth (* worth 0.000001)))))",
    "poison worth 1000, by expression": "(world (on meal (if (< worth 0) (set worth (* worth 1000)))))",
    "COST 1e-4 from 50 s": "(world (on tick (if (>= t 50) (set COST 0.0001))))",
    "a Python error on poison (1/0)": "(world (on meal (if (< worth 0) (set worth (/ 1 (- 1 1))))))",
    "a Python error on poison (log -1)": "(world (on meal (if (< worth 0) (set worth (log (- 0 1))))))",
    "a Python error in a deferral": "(world (on meal (after 0.5 (set poison (/ 1 (- 1 1))))))",
    "rewire by fire, deferred 1 ms": "(world (on fire (if (>= t 50) (do (drop) (after 0.001 (thrust (- 1 thruster)))))))",
    "rewire by fire, laundered through the tick stage": "(world (let want -1) (on fire (if (>= t 50) (do (drop) (set want (- 1 thruster))))) (on tick (if (>= want 0) (do (thrust want) (set want -1)))))",
    "rewire by see, both eyes' light exchanged from 50 s": "(world (on see (if (>= t 50) (set seen (raw (- 1 colour))))))",
    "body frozen by drag from 50 s": "(world (on tick (if (>= t 50) (set DRAG 100000))))",
    "every block hidden at 50 s": "(world (let done 0) (on tick (if (and (>= t 50) (= done 0)) (do (set done 1) (each b (hide b))))))",
    "a tick-stage lie, chance per tick": "(world (on tick (set poison (if (chance 0.2) F P))))",
    "a pulse every tick": "(world (on tick (pulse 0)))",
    "a pulse at a rate": "(world (on tick (repeat (poisson (* 5 TICK)) (pulse 0))))",
    "a count of ticks": "(world (let n 0) (on tick (set n (+ n 1)) (set poison (mod (floor (/ n 1000)) 2))))",
    "told that draws": "(world (told (if (chance 0.5) P F)) (on meal (if (chance 0.2) (set worth (- worth)))))",
    "worth swapped in two-meal ticks (honest now: each meal its own taste)": f"(world (on move (if (chance (* 2 TICK)) (do (bset 0 {HEAD}) (bset 18 {HEAD})))) (on meal (set worth (- worth))))",
}


def static():
    print("== static: the checker's attacks verbatim, then mine in the stage-2c language", flush=True)
    sets = [("checker 1", C1.STAGE5), ("checker 2", C2.NEW), ("checker 2 brain", {t: t for t in C2.BRAIN}), ("mine", MINE),
            ("hand", {n: d["text"] for n, d in WW.W.items()}), ("stage 5", {n: d["text"] for n, d in WW.STAGE5.items()})]
    ok = {}
    for label, texts in sets:
        for n, t in texts.items():
            try:
                lang.World(t, n)
                ok[(label, n)] = t
                print(f"  {label:15s} {n[:70]:70s} compiles", flush=True)
            except lang.Refused as e:
                print(f"  {label:15s} {n[:70]:70s} REFUSED: {'; '.join(lang.World(t, n, compile_only=True).refused)[:160]}", flush=True)
            except lang.LangError as e:
                print(f"  {label:15s} {n[:70]:70s} NOT A PROGRAM: {str(e)[:160]}", flush=True)
    return ok


def told_lockstep(job):
    from stage2_lang import arms, sim
    from stage2_indep_identity import brain_maker, state_life
    text, seed, first = job
    A = arms.make(arms.world_of(text), "bank", seed, first, seconds=False)
    B = sim.WLife(seed, first, brain_maker("bank"), lang.World(text), seconds=False)
    for k in range(10000):
        A.step()
        B.step()
        if not np.array_equal(state_life(A), state_life(B)):
            return k
    return None


def one(job):
    from stage2_lang import arms as S, instruments
    from stage2_lang.sim import Refused
    text, arm, seed, first = job
    try:
        l = S.one((text, arm, {}, seed, first, 100.0))
    except Refused as e:
        return ("refused", str(e)[:90])
    return l.labels


def lives(ok, ex):
    from stage2_lang import instruments
    print(f"\n== lives, seconds mode, seeds {SEEDS.start}-{SEEDS.stop - 1} x 2, base and bank (80 a world): refused lives, and lives labelled by each instrument", flush=True)
    fp = Counter()
    nh = 0
    for (label, n), t in ok.items():
        R = list(ex.map(one, [(t, a, s, c) for a in ("circuit", "bank") for s in SEEDS for c in COL], chunksize=2))
        ref = [r for r in R if isinstance(r, tuple)]
        L = [r for r in R if isinstance(r, dict)]
        k = {key: sum(bool(r[key]) for r in L) for key in ("rewired_eye", "rewired_motor", "frozen", "placed")}
        AT = dict(rewired_eye="eye_at", rewired_motor="motor_at", frozen="frozen_at", placed="placed_at")
        when = {key: (np.median([r[AT[key]] for r in L if r[key]]) if k[key] else None) for key in AT}
        mw = when["rewired_motor"]
        print(f"  {label:15s} {n[:60]:60s} refused {len(ref)}/{len(R)}" + (f" ({Counter(x[1].split(':')[0] for x in ref).most_common(1)[0][0]})" if ref else "")
              + f"; labelled: eye {k['rewired_eye']}, motor {k['rewired_motor']}, frozen {k['frozen']}, placed {k['placed']}"
              + (f"; median onset eye {when['rewired_eye']:.0f} s" if when["rewired_eye"] is not None else "") + (f", motor {mw:.0f} s" if mw is not None else "")
              + (f", frozen {when['frozen']:.0f} s" if when["frozen"] is not None else "") + (f", placed {when['placed']:.1f} s" if when["placed"] is not None else ""), flush=True)
        if label == "hand":
            nh += len(L)
            for key in k:
                fp[key, n] = k[key]
    print("\n== false positives on the hand worlds (lives labelled / lives)", flush=True)
    for key in ("rewired_eye", "rewired_motor", "frozen", "placed"):
        tot = sum(v for (kk, _), v in fp.items() if kk == key)
        who = {n: v for (kk, n), v in fp.items() if kk == key and v}
        print(f"  {key}: {tot}/{nh} = {tot / max(1, nh):.4f}; worlds: {who}", flush=True)


if __name__ == "__main__":
    ok = static()
    with ProcessPoolExecutor(7) as ex:
        print("\n== told: the bank via arms (spy reads the told rule) against universal_v.V, legacy mode, lockstep, 40 lives", flush=True)
        t = "(world (told P) (on meal (if (chance 0.2) (set worth (- worth)))))"
        R = list(ex.map(told_lockstep, [(t, s, c) for s in SEEDS for c in COL]))
        print(f"  {t}: {sum(r is None for r in R)} of {len(R)} identical; first differing ticks {sorted(r for r in R if r is not None)[:6]}", flush=True)
        lives(ok, ex)

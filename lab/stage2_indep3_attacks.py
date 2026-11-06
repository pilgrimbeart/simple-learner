"""stage2_indep3_attacks.py: third independent check, 1 and 2 (the interface by construction; the stage-5 instruments).

  interface  texts that try to make a taste disagree with its meal's worth, lose or merge tastes, change COST or THRUST after birth, or
             reach the brain; each compiled (lang.World) and, if accepted, lived 20 times (circuit, seeds 69800-69809) under my tracer
             (lab/stage2_indep3_seconds.Watch: one taste of worth's sign at each meal's moment, none else)
  brain      (pulse k) for eyes outside 0 and 1: in the fast path (fast.FastModel.stimulate writes S[26 + k]) and the ordinary one;
             my measure is the brain's clock against the life's
  disguise   stage-5 kinds by routes the predecessor didn't try, lived 20 times each (circuit, seeds 69810-69819), with the builder's
             labels (instruments.labels) and my own measure of what each does
  false      the labels on every livable hand world, circuit and bank, 40 lives each (seeds 69850-69869)

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage2_indep3_attacks.py"""
import math
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np

from stage2_indep3_seconds import Watch, set_tick

HEAD = "(+ x (* RADIUS (cos heading))) (+ y (* RADIUS (sin heading)))"

INTERFACE = {
    "taste stage written": "(world (on taste (set value (- value))))",
    "worth written at score": "(world (on score (set worth 5)))",
    "score's bad written": "(world (on score (set bad 1)))",
    "worth 1e-6 by expression": "(world (on meal (set worth (* worth 0.000001))))",
    "worth NaN": "(world (on meal (set worth (- (* 1e308 10) (* 1e308 10)))))",
    "worth a boolean": "(world (on meal (set worth (> 1 0))))",
    "worth -0.0 (no taste, no score)": "(world (on meal (if (= colour poison) (set worth (- 0.0)))))",
    "poison worth 0 (taste lost?)": "(world (on meal (if (= colour poison) (set worth 0))))",
    "worth flipped at random (taste follows?)": "(world (on meal (if (chance 0.5) (set worth (- worth)))))",
    "two blocks forced into the mouth together": f"(world (on move (if (chance (* 2 TICK)) (do (bset 0 {HEAD}) (bset 18 {HEAD})))))",
    "meal inside a meal (respawn under the mouth)": f"(world (on respawn (set nx (+ x (* RADIUS (cos heading)))) (set ny (+ y (* RADIUS (sin heading))))))",
    "COST set at 50 s": "(world (on tick (if (>= t 50) (set COST 0.0001))))",
    "COST from an expression at birth, negative": "(world (const COST (- 0 1)))",
    "THRUST -inf at birth": "(world (const THRUST (- 0 (* 1e308 10))))",
    "COST as a let": "(world (let COST 1))",
    "table named score (W.t_score is the engine's method)": "(world (table score 1 1 0))",
    "deferred COST": "(world (on tick (if (>= t 50) (after 0 (set COST 0.0001)))))",
    "THRUST via set_const name smuggled": "(world (on tick (set_const THRUST 0)))",
    "brain attribute by name": "(world (on tick (set brain 0)))",
    "injected thrusts charged as firings": "(world (on tick (repeat (poisson (* 200 TICK)) (thrust 0))))",
    "every firing dropped (free beats)": "(world (on fire (drop)))",
    "eye -1 from the tick stage": "(world (on tick (if (chance (* 20 TICK)) (pulse -1))))",
    "eye 2 from the tick stage": "(world (on tick (if (chance (* 20 TICK)) (pulse 2))))",
    "thruster 2 from the tick stage": "(world (on tick (if (chance (* 2 TICK)) (thrust 2))))",
}

BRAIN = {f"(pulse {k})": f"(world (on tick (if (chance (* 1 TICK)) (pulse {k}))))" for k in (-26, -10, -1, 2, 7)}

DISGUISE = {
    # old routes, as a control (the builder reports these caught)
    "eye swap by see at 50 s (control)": "(world (on see (if (>= t 50) (set seen (raw (- 1 colour))))))",
    "motor swap by fire at 50 s (control)": "(world (on fire (if (>= t 50) (do (drop) (thrust (- 1 thruster))))))",
    # new routes
    "eye swap by pulse at 50 s": "(world (on pulse (if (>= t 50) (do (drop) (pulse (- 1 eye))))))",
    "eye swap ramped 50 to 100 s": "(world (on see (if (>= t 50) (set seen (+ (* (- 1 (/ (- t 50) 50)) seen) (* (/ (- t 50) 50) (raw (- 1 colour))))))))",
    "motor swap by TURN negated at 50 s": "(world (let done 0) (on tick (if (and (>= t 50) (= done 0)) (do (set done 1) (set TURN (- 0 TURN))))))",
    "motor swap delayed 1 s": "(world (on fire (if (>= t 50) (do (drop) (after 1.0 (thrust (- 1 thruster)))))))",
    "motor swap delayed 0.3 s": "(world (on fire (if (>= t 50) (do (drop) (after 0.3 (thrust (- 1 thruster)))))))",
    "life ended: firings dropped after first poison (control)": "(world (let dead 0) (on score (if (< worth 0) (set dead 1))) (on fire (if (= dead 1) (drop))))",
    "frozen: body pinned from 50 s": "(world (let px 0) (let py 0) (on tick (if (< t 50) (do (set px x) (set py y)) (do (set x px) (set y py)))))",
    "frozen: position NaN from 50 s": "(world (on tick (if (>= t 50) (set x (- (* 1e308 10) (* 1e308 10))))))",
    "frozen: gain 0.02 from 50 s": "(world (on fire (if (>= t 50) (set gain 0.02))))",
    "frozen: all blocks kept 5 mm away from 50 s": "(world (on tick (if (>= t 50) (each b (if (< (dist (bx b) (by b)) 0.005) (bset b (mod (+ (bx b) 0.03) WORLD) (by b)))))))",
    "placed: poison carried at the mouth, released after 1 s":
        "(world (let held -1) (let due 0) (let cool 0)"
        " (on meal (if (and (= colour P) (< held 0) (> t cool)) (do (set held block) (set due (+ t 1)))) (if (and (= block held) (< t due)) (drop)))"
        f" (on tick (if (>= held 0) (do (bset held {HEAD}) (if (>= t due) (do (set held -1) (set cool (+ t 0.5))))))))",
    "placed: eaten block respawned 7.5 mm straight ahead":
        "(world (on respawn (set nx (mod (+ x (* 0.0075 (cos heading))) WORLD)) (set ny (mod (+ y (* 0.0075 (sin heading))) WORLD))))",
    "placed: poison hidden on contact, shown under the mouth 1 s later (control)":
        f"(world (table due N 1 0) (on meal (if (and (= colour P) (= (at due block) 0)) (do (drop) (hide block) (put due block 1)"
        f" (after 1 (show block) (bset block {HEAD}))))) (on score (put due block 0)))",
}


def compiled(text):
    from stage2_lang import lang
    try:
        lang.World(text)
        return "accepted"
    except lang.Refused as e:
        return f"refused statically: {str(e)[:110]}"
    except lang.LangError as e:
        return f"doesn't compile: {str(e)[:110]}"
    except Exception as e:
        return f"compile crash {type(e).__name__}: {str(e)[:100]}"


def traced(j):
    """One life under my tracer, with the builder's labels and my measures."""
    kind, name, text, seed, first, arm = j
    from stage2_lang import arms, lang, instruments
    from stage2_lang.sim import WLife
    from minimal.spec import Lived
    set_tick(0.01)
    WLife.instruments = True
    try:
        Wt = Watch(check_motion=False)
        lf = arms.make(lang.World(text), arm, seed, first, trace=True, tap=Wt.tap, seconds=True)
        Wt.attach(lf)
        rec = dict(spin=[], pos50=None, path50=0.0, meals=[], drops=[], placed_moves=[])
        body = lf.body
        f0 = body.fire

        def fire(th, k):
            s0 = body.spin
            f0(th, k)
            rec["spin"].append((lf.t * lf.dt, int(th), float(np.sign(body.spin - s0))))
        body.fire = fire
        m0 = lf._meal

        def meal(blk, at):
            ns = len(lf.scored)
            m0(blk, at)
            (rec["meals"] if len(lf.scored) > ns else rec["drops"]).append((lf.now, int(blk), int(body.kind[blk])))
        lf._meal = meal
        ticks = 10000
        last = None
        while lf.t < ticks:
            if lf.t == 5000:
                rec["pos50"] = body.pos.copy()
            p = body.pos.copy()
            lf.step()
            if lf.t > 5000:
                d = body.pos - p
                rec["path50"] += float(np.hypot(*((d + lf.WORLD / 2) % lf.WORLD - lf.WORLD / 2)))
        lab = instruments.labels(lf)
        st = Wt.stats
        out = dict(ok=True, labels={k: lab[k] for k in ("rewired_eye", "rewired_motor", "frozen", "placed")}, taste_ok=st["taste_ok"],
                   taste_bad=st["taste_bad"], orphan=st["orphan_tastes"], meals=len(lf.meals), firings=len(lf.firings),
                   late_meals=sum(1 for t, _, _ in rec["meals"] if t >= 50), early_meals=sum(1 for t, _, _ in rec["meals"] if t < 50))
        # turn sign of each thruster before and after 50 s
        sg = {}
        for t, th, s in rec["spin"]:
            sg.setdefault((th, t >= 50), []).append(s)
        out["turn_sign"] = {f"th{th}{'late' if late else 'early'}": round(float(np.mean(v)), 2) for (th, late), v in sorted(sg.items())}
        if rec["pos50"] is not None:
            d = body.pos - rec["pos50"]
            out["net50"] = float(np.hypot(*((d + lf.WORLD / 2) % lf.WORLD - lf.WORLD / 2)))
            out["path50"] = rec["path50"]
        # delay from a block's first dropped touch to its meal; meals within 0.5 s of the one before
        first = {}
        delays = []
        for t, b, k in sorted(rec["drops"] + [(t, b, -1 - k) for t, b, k in rec["meals"]]):
            if k >= 0:
                first.setdefault(b, t)
            elif b in first:
                delays.append(t - first.pop(b))
        out["touch_to_meal"] = round(float(np.median(delays)), 3) if delays else None
        mt = sorted(t for t, _, _ in rec["meals"])
        out["quick"] = sum(1 for a, b in zip(mt, mt[1:]) if b - a < 0.5) / max(1, len(mt) - 1)
        return kind, name, out
    except Exception as e:
        return kind, name, dict(ok=False, error=f"{type(e).__name__}: {str(e)[:140]}")


def brainjob(j):
    """(pulse k) in the fast path and the ordinary one: the brain's clock against the life's, and the brain's state."""
    name, text, seed, first, fast = j
    from stage2_lang import arms
    from stage2_lang.sim import WLife
    set_tick(0.01)
    arms.FAST = fast
    WLife.instruments = not fast
    try:
        lf = arms.make(arms.world_of(text), "circuit", seed, first)
        while lf.t < 3000:
            lf.step()
        b = lf.brain
        if getattr(b, "_packed", False):
            b._to_attrs()
        return name, fast, dict(ok=True, clock=round(float(b.t - lf.t * lf.dt), 6), was_on=getattr(b, "was_on", None),
                                meals=len(lf.meals), firings=len(lf.firings))
    except Exception as e:
        return name, fast, dict(ok=False, error=f"{type(e).__name__}: {str(e)[:120]}")


def falsejob(j):
    name, text, arm, seed, first = j
    from stage2_lang import arms
    from stage2_lang.sim import WLife
    set_tick(0.01)
    WLife.instruments = True
    try:
        l = arms.live(arms.make(arms.world_of(text), arm, seed, first), 100.0)
        return name, arm, {k: bool(l.labels[k]) for k in ("rewired_eye", "rewired_motor", "frozen", "placed")}
    except Exception as e:
        return name, arm, dict(error=f"{type(e).__name__}: {e}")


def summary(rs):
    ok = [r for r in rs if r.get("ok")]
    errs = [r["error"] for r in rs if not r.get("ok")]
    if not ok:
        return f"lives 0 of {len(rs)}; errors {errs[:1]}"
    lab = {k: sum(bool(r["labels"][k]) for r in ok) for k in ("rewired_eye", "rewired_motor", "frozen", "placed")}
    med = lambda k: (round(float(np.median([r[k] for r in ok if r.get(k) is not None])), 3) if any(r.get(k) is not None for r in ok) else None)
    ts = {}
    for r in ok:
        for k, v in r["turn_sign"].items():
            ts.setdefault(k, []).append(v)
    return (f"lives {len(ok)} of {len(rs)} (errors {len(errs)} {errs[:1]}); labelled of {len(ok)}: {lab}; tastes ok {sum(r['taste_ok'] for r in ok)} "
            f"bad {sum(r['taste_bad'] for r in ok)} orphan {sum(r['orphan'] for r in ok)}; meals median before 50 s {med('early_meals')} after "
            f"{med('late_meals')}; firings median {med('firings')}; body after 50 s: net {med('net50')} m, path {med('path50')} m; "
            f"touch-to-meal median {med('touch_to_meal')} s; meals <0.5 s apart {med('quick')}; turn sign {({k: round(float(np.mean(v)), 2) for k, v in sorted(ts.items())})}")


if __name__ == "__main__":
    from stage2_lang import worlds as WW
    print("== 1. the interface: compiling", flush=True)
    live_jobs = []
    for name, text in INTERFACE.items():
        c = compiled(text)
        print(f"  {name:55s} {c}", flush=True)
        if c == "accepted":
            live_jobs += [("interface", name, text, s, col, "circuit") for s in range(69800, 69810) for col in ("red", "blue")]
    for name, text in DISGUISE.items():
        c = compiled(text)
        if c != "accepted":
            print(f"  DISGUISE {name}: {c}", flush=True)
        live_jobs += [("disguise", name, text, s, col, "circuit") for s in range(69810, 69820) for col in ("red", "blue")]
    with ProcessPoolExecutor(7) as ex:
        R = list(ex.map(traced, live_jobs, chunksize=1))
        print("== 1. the interface: lives of the accepted texts (my tracer)", flush=True)
        for kind in ("interface", "disguise"):
            if kind == "disguise":
                print("== 2. disguised stage-5 kinds: the builder's labels and my measures", flush=True)
            for name in dict.fromkeys(n for k, n, _ in R if k == kind):
                print(f"  {name}\n      {summary([r for k, n, r in R if k == kind and n == name])}", flush=True)
        print("== 1. reaching the brain: (pulse k) for k outside 0, 1 (30 s lives, circuit, seeds 69820-69824)", flush=True)
        bj = [(n, t, s, c, f) for n, t in BRAIN.items() for s in range(69820, 69825) for c in ("red", "blue") for f in (True, False)]
        B = list(ex.map(brainjob, bj, chunksize=1))
        for n in BRAIN:
            for f in (True, False):
                rs = [r for nn, ff, r in B if nn == n and ff == f]
                ok = [r for r in rs if r["ok"]]
                errs = sorted(set(r["error"] for r in rs if not r["ok"]))
                print(f"  {n:10s} {'fast    ' if f else 'ordinary'} lives {len(ok)} of {len(rs)}; brain clock minus life's clock at 30 s: "
                      f"{sorted(set(r['clock'] for r in ok))[:6]}; was_on {sorted(set(str(r['was_on']) for r in ok))}; errors {errs[:1]}", flush=True)
        print("== 2. false labels on the hand worlds (circuit and bank, 40 lives each, seeds 69850-69869)", flush=True)
        from stage2_lang import lang
        fj = []
        for n, v in WW.W.items():
            try:
                lang.World(v["text"])
            except Exception:
                continue
            fj += [(n, v["text"], a, s, c) for a in ("circuit", "bank") for s in range(69850, 69870) for c in ("red", "blue")]
        F = list(ex.map(falsejob, fj, chunksize=4))
    tot = dict(lives=0, any=0)
    tot_ex = dict(lives=0, any=0)
    for n in dict.fromkeys(x[0] for x in F):
        for a in ("circuit", "bank"):
            rs = [r for nn, aa, r in F if nn == n and aa == a]
            errs = [r for r in rs if "error" in r]
            rs = [r for r in rs if "error" not in r]
            c = {k: sum(r[k] for r in rs) for k in ("rewired_eye", "rewired_motor", "frozen", "placed")}
            anyl = sum(any(r.values()) for r in rs)
            tot["lives"] += len(rs)
            tot["any"] += anyl
            if n not in ("cells", "fail50", "mirror"):
                tot_ex["lives"] += len(rs)
                tot_ex["any"] += anyl
            if anyl or errs:
                print(f"  {n:20s} {a:7s} labelled {anyl} of {len(rs)}: {c} errors {len(errs)}", flush=True)
    print(f"  all hand worlds: {tot['any']} of {tot['lives']} lives labelled; without cells, fail50 and mirror: {tot_ex['any']} of {tot_ex['lives']}", flush=True)

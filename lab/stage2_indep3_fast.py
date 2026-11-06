"""stage2_indep3_fast.py: third independent check, 4 (the speed-up). The fast path (arms.FAST True, sim.WLife.instruments False:
_step_fused or _step_fast with fast.py's compiled brain) against the ordinary seconds path (arms.FAST False, instruments on:
_step_seconds with seconds.py's brains), each life fingerprinted by my own code: meals, firings, scored meals, the thirds, the final
states of the three streams (body, world, engine), the body's final state, and the brain's state (the compiled brain's arrays
written back to its attributes first, after the life, when nothing reads them any more), its rows, picks, on_at and trace.

Worlds: every livable hand world (lab/stage2_lang/worlds.py) and mine, built to strain the fast path. Arms circuit and bank, at 10 ms
and 1.25 ms, seeds 69700-69799.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage2_indep3_fast.py"""
import hashlib
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor

from stage2_indep3_seconds import set_tick

MINE = {
    "x_pulse_neg": "(world (on tick (if (chance (* 20 TICK)) (pulse -1))))",
    "x_pulse_clock": "(world (on tick (if (chance (* 1 TICK)) (pulse -26))))",
    "x_sense_high": "(world (const SENSE 1200))",
    "x_bright": "(world (on birth (each b (bbright b 30))))",
    "x_thrust_spaced_tick": "(world (on tick (if (chance (* 2 TICK)) ( thrust 0))))",
    "x_thrust_spaced_meal": "(world (on meal ( thrust 1)))",
    "x_after_spaced_meal": "(world (let m 0) (on meal ( after 0.0005 (set m (+ m 1)))))",
    "x_after_meal": "(world (let m 0) (on meal (after 0.0005 (set m (+ m 1)))))",
    "x_after_tick": "(world (let m 0) (on tick (if (chance (* 5 TICK)) (after 0.002 (set m (+ m 1))))))",
    "x_meal_moves_body": "(world (on meal (set heading (+ heading 0.5)) (set vx (* 0.5 vx))))",
    "x_tick_physics": "(world (on tick (set DRAG (+ 50 (* 20 (sin t)))) (set PUSH (* 0.02 (+ 1 (* 0.5 (cos t)))))))",
    "x_respawn_ahead": "(world (on respawn (set nx (mod (+ x (* 0.0075 (cos heading))) WORLD)) (set ny (mod (+ y (* 0.0075 (sin heading))) WORLD))))",
    "x_score_hide": "(world (on score (if (< worth 0) (hide block))) (on tick (if (chance (* 0.2 TICK)) (each b (show b)))))",
}
BKEYS = ("t", "dq", "phase", "phase1", "last_drive", "last_food", "run_from", "x", "e", "b", "start", "Tr", "F", "P", "rate", "ate_at",
         "est", "food", "was_on", "seen", "last", "pulses", "drives", "pausing", "open", "was_driving", "nticks")


def fingerprint(lf, l):
    b = lf.brain
    if getattr(b, "_packed", False):
        b._to_attrs()
    bs = {k: repr(getattr(b, k, None)) for k in BKEYS}
    bs["p"] = repr({k: b.p.get(k) for k in ("g0", "g1", "sd")})
    for k in ("rows", "picks", "on_at", "trace"):
        bs[k] = hashlib.sha256(repr(getattr(b, k, None)).encode()).hexdigest()[:12]
    B = lf.body
    parts = dict(meals=repr(lf.meals), firings=repr(lf.firings), scored=repr(lf.scored), thirds=repr(lf.thirds(lf.t)),
                 rng=repr(lf.rng.bit_generator.state), r=repr(lf.r.bit_generator.state), trng=repr(lf.trng.bit_generator.state),
                 body=repr((B.pos.tolist(), B.heading, B.spin, B.speed.tolist(), B.xy.tolist(), B.alive.tolist())),
                 vars=repr(sorted((k, v) for k, v in vars(lf).items() if k.startswith("v_"))), brain=repr(sorted(bs.items())))
    return {k: hashlib.sha256(v.encode()).hexdigest()[:16] for k, v in parts.items()}, len(lf.meals), len(lf.firings)


def one(j):
    name, text, arm, seed, first, dt, fast = j
    from stage2_lang import arms
    from stage2_lang.sim import WLife
    set_tick(dt)
    arms.FAST = fast
    WLife.instruments = not fast
    try:
        lf = arms.make(arms.world_of(text), arm, seed, first)
        path = type(lf.brain).__mro__[1].__name__
        l = arms.live(lf, 100.0)
        fp, nm, nf = fingerprint(lf, l)
        step = getattr(lf.step, "__name__", "?")
        return j, dict(fp=fp, meals=nm, firings=nf, step=step, brain=type(lf.brain).__name__)
    except Exception as e:
        return j, dict(error=f"{type(e).__name__}: {str(e)[:120]}")


if __name__ == "__main__":
    from stage2_lang import worlds as WW
    from stage2_lang import lang
    worlds = {}
    for k, v in WW.W.items():
        try:
            lang.World(v["text"])
            worlds[k] = v["text"]
        except Exception as e:
            print(f"hand world {k} not livable: {e}", flush=True)
    worlds.update(MINE)
    jobs = []
    for dt, seeds in ((0.01, range(69700, 69708)), (0.00125, range(69708, 69711))):
        for name, text in worlds.items():
            for arm in ("circuit", "bank"):
                for s in seeds:
                    for c in ("red", "blue"):
                        for fast in (True, False):
                            jobs.append((name, text, arm, s, c, dt, fast))
    jobs.sort(key=lambda j: (-j[5], j[0]))
    res = {}
    with ProcessPoolExecutor(7) as ex:
        for j, r in ex.map(one, jobs, chunksize=2):
            res[j] = r
    print(f"{len(worlds)} worlds ({len(MINE)} mine), arms circuit and bank, 16 lives a world and arm at 10 ms, 6 at 1.25 ms", flush=True)
    tot = dict(same=0, differ=0, err_both=0, err_one=0)
    for dt in (0.01, 0.00125):
        for name in worlds:
            for arm in ("circuit", "bank"):
                same, diff, eb, eo, parts, steps, ex_ = 0, 0, 0, 0, set(), set(), []
                for (n, t, a, s, c, d, fast), r in res.items():
                    if (n, a, d) != (name, arm, dt) or not fast:
                        continue
                    o = res[(n, t, a, s, c, d, False)]
                    if "error" in r or "error" in o:
                        if "error" in r and "error" in o:
                            eb += 1
                        else:
                            eo += 1
                            ex_.append(("fast", r.get("error")) if "error" in r else ("ordinary", o.get("error")))
                        continue
                    steps.add(r["step"])
                    if r["fp"] == o["fp"]:
                        same += 1
                    else:
                        diff += 1
                        parts |= {k for k in r["fp"] if r["fp"][k] != o["fp"][k]}
                tot["same"] += same
                tot["differ"] += diff
                tot["err_both"] += eb
                tot["err_one"] += eo
                flag = "" if diff == 0 and eo == 0 else "   <-- DISCREPANCY"
                print(f"{dt*1e3:5.2f} ms {name:22s} {arm:7s} identical {same:2d} differ {diff:2d} (in {sorted(parts)}) error both {eb} "
                      f"error one path {eo} {ex_[:1]} fast step {sorted(steps)}{flag}", flush=True)
    print("total", tot, flush=True)

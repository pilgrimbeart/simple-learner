"""speed_fingerprint.py: the engine's lives before and after speeding it up must be identical (main session, 2026-11-06). For six
worlds, base and bank, both modes (seconds on and off), 10 ms and 2.5 ms, 6 lives each: a hash of every meal, firing, score and the
streams' final states. `record` writes lab/v/speed_fingerprint.json; `check` compares and times.

    OPENBLAS_NUM_THREADS=1 .venv/bin/python lab/speed_fingerprint.py record|check"""
import hashlib, json, sys, time
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor

OUT = "/home/pilgrim/git/simple-learner/lab/v/speed_fingerprint.json"
WORLDS = ("plain", "swap10", "alternate", "unreliable", "digest", "noisy")
JOBS = [(w, a, secs, dt, s, c) for w in WORLDS for a in ("circuit", "bank") for secs in (False, True) for dt in (0.01, 0.0025)
        for s in (61000, 61001, 61002) for c in ("red", "blue")]


def one(job):
    import stage2_checks as C
    from stage2_lang import arms as S, sim, worlds as WW
    w, arm, secs, dt, seed, first = job
    import os
    from stage2_lang import arms as A
    A.FAST = os.environ.get("FAST") == "1"             # FAST=1: the compiled brains; INST=0: no instruments (neither changes a life)
    sim.WLife.instruments = os.environ.get("INST", "1") == "1"
    if abs(sim.WLife.dt - dt) > 1e-15:
        C.set_tick(dt)
    sim.WLife.seconds = secs
    t = time.time()
    lf = S.make(S.world_of(WW.W[w]["text"]), arm, seed, first)
    S.live(lf)
    took = time.time() - t
    h = hashlib.sha256(repr((lf.meals, lf.firings, lf.scored, lf.rng.bit_generator.state, lf.r.bit_generator.state,
                             lf.trng.bit_generator.state)).encode()).hexdigest()
    return "|".join(map(str, job)), h, took


if __name__ == "__main__":
    t0 = time.time()
    res = []
    for dt in (0.01, 0.0025):                           # one pool per tick: a worker's modules are set to one tick only
        with ProcessPoolExecutor(7) as ex:
            res += list(ex.map(one, [j for j in JOBS if j[3] == dt]))
    wall = time.time() - t0
    cpu = {}
    for k, _, took in res:
        w, a, secs, dt = k.split("|")[:4]
        cpu.setdefault(f"{a} seconds={secs} {float(dt) * 1000:g} ms", []).append(took)
    timing = {k: sum(v) / len(v) for k, v in cpu.items()}
    if sys.argv[1] == "record":
        json.dump({"hash": {k: h for k, h, _ in res}, "timing": timing}, open(OUT, "w"), indent=0)
        print(f"recorded {len(res)} lives in {wall:.0f} s")
    else:
        base = json.load(open(OUT))
        bad = [k for k, h, _ in res if base["hash"][k] != h]
        print(f"{len(res) - len(bad)} of {len(res)} lives identical; wall {wall:.0f} s")
        print("  differing by mode:", {m: sum(1 for k in bad if k.split("|")[2] == m) for m in ("False", "True")})
        for k in bad[:10]:
            print("  DIFFERS", k)
        for k in sorted(timing):
            print(f"  {k:32s} {base['timing'][k]:.3f} -> {timing[k]:.3f} s a life ({base['timing'][k] / timing[k]:.1f}x)")

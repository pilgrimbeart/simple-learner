"""Robot-action investigation (D178), R1: identity, provenance and passive-logging checks.
 1. The adapter at substrate=biology reproduces D176's stored captures (learn/frozen/informed/allfood -mem-thr,
    ~/nca-scratch-backup/robot_shortfall_20261120/) bit for bit in meals, rows and pulses, for every life.
 2. Passive logging: unlogged vs logged adapter, same life: identical meals and thruster firings (3 lives x 20 s, per
    substrate); and the original DesignedBrain vs the adapter with mem=thr=False and logging: identical meals/firings.
 3. Realised wiring from the built graph; body wiring/world identities (Life.sensor, Life.motor) per seed, both
    substrates; component-draw hashes equal across substrates (substrate changes noise only, not draws).
python checks.py -> lab/v/robot_action_20261120/checks.json
"""
import json, os, pickle, sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
OUT = ROOT / "lab/v/robot_action_20261120"
OLD = Path.home() / "nca-scratch-backup/robot_shortfall_20261120"


def short_life(brain, seed, poison, ticks=2000, learning=True):
    from creature import Life
    life = Life(seed, poison, learning, brain)
    while life.t < ticks:
        life.step()
    return life


def main():
    import capture as C
    import brain as B
    out = {}
    # 1. identity with D176's stored -mem-thr captures (all 64 lives per arm)
    ident = {}
    for arm in ("learn", "frozen", "informed", "allfood"):
        old = pickle.load(open(OLD / f"{arm}-mem-thr_64x100s.pkl", "rb"))
        new = C.run(arm, "biology", 0, 31)
        same = [o["meals"] == n["meals"] and np.array_equal(o["rows"], n["rows"]) and
                np.array_equal(o["pulses"], n["pulses"]) and o["moving"] == n["moving"] for o, n in zip(old, new)]
        ident[arm] = dict(lives=len(same), identical=int(sum(same)))
    out["identity_vs_D176_mem_thr"] = ident
    # 2. passive logging
    pl = {}
    for sub in ("biology", "silicon"):
        ok = []
        for seed, poison in ((0, "red"), (5, "blue"), (11, "red")):
            a = short_life(B.make_brain(sub, True, True, None, log=False), seed, poison)
            b = short_life(B.make_brain(sub, True, True, None, log=True), seed, poison)
            ok.append(a.meals == b.meals and a.firings == b.firings and np.array_equal(a.body.pos, b.body.pos))
        pl[sub] = ok
    ok = []
    for seed, poison in ((0, "red"), (5, "blue"), (11, "red")):
        a = short_life("designed-circuit", seed, poison)
        b = short_life(B.make_brain("biology", False, False, None, log=True), seed, poison)
        ok.append(a.meals == b.meals and a.firings == b.firings)
    pl["original_vs_adapter_unrepaired"] = ok
    out["passive_logging"] = pl
    # 3. wiring and identities
    from creature import Life
    ids = []
    for seed in range(32):
        row = dict(seed=seed)
        for sub in ("biology", "silicon"):
            life = Life(seed, "red", True, B.make_brain(sub))
            row[sub] = dict(sensor=life.sensor, motor=life.motor, wiring=B.wiring(life.brain), draws=B.draws_hash(life.brain))
        row["same_across_substrates"] = (row["biology"]["sensor"] == row["silicon"]["sensor"] and
                                         row["biology"]["motor"] == row["silicon"]["motor"] and
                                         row["biology"]["wiring"] == row["silicon"]["wiring"] and
                                         row["biology"]["draws"] == row["silicon"]["draws"])
        ids.append(row)
    out["identities"] = ids
    out["identities_same_wiring_all"] = all(r["same_across_substrates"] for r in ids)
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(OUT / "checks.json", "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in out.items() if k != "identities"}, indent=1, default=str))
    print("wiring same across substrates:", out["identities_same_wiring_all"])


if __name__ == "__main__":
    for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[k] = "1"
    main()

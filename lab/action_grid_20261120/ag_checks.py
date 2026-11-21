"""Action grid R1: identity checks and named fixtures (work order section 5). Each check is a named boolean with its
evidence; `valid` is their conjunction. Writes OUT/checks.json (refuses to overwrite)."""
from __future__ import annotations

import hashlib
import inspect
import itertools
import json
import pickle
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import ag_engine as AE                                             # noqa: E402
import ag_jobs as J                                                # noqa: E402
from ag_engine import GridBrain, GridEngine, _loop_obs, variants   # noqa: E402
from units import DT, PULSE, RAIL, TICK, V_TYP                     # noqa: E402
from brains.circuit import PULSES                                  # noqa: E402

OUT = ROOT / "lab/v/action_grid_20261120"
D180_ARCHIVE = ROOT / "lab/v/catalogue_brain_20261120_action_auth.pkl"
D180_LEDGER = ROOT / "lab/v/catalogue_brain_20261120/action_auth_ledger.jsonl.gz"
EXTREMES = ("g2.0_t0.0025_q0.3_f1.5", "g0.5_t0.01_q0.15_f0.75", "g1.0_t0.005_q0.225_f1.0")


def state_of(life):
    e = life.brain.e
    return dict(meals=list(life.meals), firings=list(life.firings), V=e.V.copy(), Vx=e.Vx.copy(), armed=e.armed.copy(),
                node_rng=[g.bit_generator.state for g in e.rngs], world_rng=life.rng.bit_generator.state,
                zpos=e.zpos)


def same(a, b):
    return (a["meals"] == b["meals"] and a["firings"] == b["firings"] and np.array_equal(a["V"], b["V"])
            and np.array_equal(a["Vx"], b["Vx"]) and np.array_equal(a["armed"], b["armed"])
            and a["node_rng"] == b["node_rng"] and a["world_rng"] == b["world_rng"] and a["zpos"] == b["zpos"])


def observer_on_off(config, seed, poison, removed, ratio, noise, ticks, P="informed"):
    """Observer ON: GridBrain + body observation wrapper. OFF: D180's CatalogueBrain on the same variant graph."""
    from creature import Life
    import brain as D180
    cfg = AE.CONFIGS[config]
    off = Life(seed, poison, False, brain=lambda s: D180.CatalogueBrain(
        s, removed=removed, ratio=ratio, noise=noise, log=False, spec=lambda sides: variants.graph(cfg, sides)))
    on = Life(seed, poison, False, brain=lambda s: GridBrain(s, config=config, removed=removed, ratio=ratio,
                                                             noise=noise, trace=True, ticks=ticks))
    Pv = J.birth_P(P, off)
    off.brain.set_P(Pv)
    on.brain.set_P(J.birth_P(P, on))
    body, orig = on.body, on.body.sees
    seen = []
    on.body.sees = lambda: (lambda d: (seen.append(d), d)[1])(orig())
    for _ in range(ticks):
        off.step()
        on.step()
    return same(state_of(off), state_of(on)), len(seen) == ticks


def main(path=None):
    path = Path(path) if path else OUT / "checks.json"
    if path.exists():
        raise SystemExit(f"{path} exists: refusing to overwrite")
    t0 = time.time()
    C = {}
    import design as D
    # 1. baseline graph equality, all four wirings
    base = AE.CONFIGS[AE.BASELINE]
    C["baseline_graph_equals_D180_all_wirings"] = dict(
        ok=all(variants.graph(base, s) == D.graph(s) for s in itertools.product((0, 1), repeat=2)))
    # 1b. D180 baseline reproduction, seed 8, all 12 native lives, against the saved archive
    C["d180_baseline_seed8_reproduction"] = d180_reproduction()
    # 2. transforms affect exactly the named fields
    C["transforms_named_fields_only"] = transforms_check(D)
    # 3. observer on/off identity (meals, body firings, final state, node and world RNG states)
    res = []
    cases = [(AE.BASELINE, 8, "red", "none", 1, "native"), (AE.BASELINE, 9, None, "none", 1, "native"),
             (AE.BASELINE, 10, "blue", "no_explore", 1, "native"), (AE.BASELINE, 11, "red", "no_sensory", 1, "native"),
             (AE.BASELINE, 8, "red", "none", 2, "coupled"), (AE.BASELINE, 8, "blue", "none", 4, "coupled")]
    cases += [(c, 12, "red", "none", 1, "native") for c in EXTREMES] + [(EXTREMES[0], 13, "blue", "none", 4, "coupled")]
    for cs in cases:
        ok, wrapped = observer_on_off(*cs, ticks=2000)
        res.append(dict(case=list(cs), identical=ok, sees_wrapper_called_every_tick=wrapped))
    C["observer_on_off_identical"] = dict(ok=all(r["identical"] and r["sees_wrapper_called_every_tick"] for r in res),
                                          cases=res, seconds_each=20.0)
    # 4. adapter reproduces Circuit.pulse/run on identical pulses and noise (ratio 1), baseline and a variant
    C["adapter_equals_circuit_run"] = adapter_check()
    # 5. identical-arm reproduction (compact rows equal, wall time excluded)
    j = J.life_jobs("check", EXTREMES[0], [14])[0]
    r1, _ = J.life_one(j)
    r2, _ = J.life_one(j)
    strip = lambda r: json.dumps({k: v for k, v in r.items() if k != "wall_s"}, sort_keys=True, default=float)
    C["identical_arm_reproduction"] = dict(ok=strip(r1) == strip(r2), job=J.key(j))
    # 6. removal keeps surviving draws and noise streams
    rm_ok = True
    for cfg in (AE.BASELINE,) + EXTREMES:
        for rm in AE.REMOVALS:
            full = GridEngine(15, config=cfg)                     # fresh each time: _z below consumes its streams
            e = GridEngine(15, config=cfg, removed=rm)
            rm_ok &= bool(np.array_equal(e.el, full.c.el_arr[:, e.keep]) and np.array_equal(e.node, full.node)
                          and np.array_equal(e.V, full.V) and np.array_equal(e.rest, full.rest)
                          and all(a.bit_generator.state == b.bit_generator.state for a, b in zip(e.rngs, full.rngs))
                          and len(e.keep) == 22 - len(AE.REMOVALS[rm]))
            za, zb = e._z(400), full._z(400)
            rm_ok &= bool(np.array_equal(za, zb))
    C["removal_keeps_surviving_draws_and_noise"] = dict(ok=rm_ok, configs=[AE.BASELINE, *EXTREMES])
    # 7. event-buffer overflow detection
    e = GridEngine(16)
    e.ev_step, e.ev_node = np.zeros(3, np.int64), np.zeros(3, np.int64)
    for _ in range(300):
        e.run_tick()
    C["event_buffer_overflow_detected"] = dict(ok=e.overflow() and int(e.ev_n[0]) == 3,
                                               note="every job row records overflow; any True invalidates that job")
    # 8. metric fixtures (D180 conventions): zero meals, zero poison, final-third boundaries
    import analyse as A180
    z = A180.life_metrics(dict(meals=[], poison="red", moving=None, Pf=None))
    C["fixture_no_meal"] = dict(ok=z["stranded"] == 1 and z["never_moved"] == 1 and z["net"] == 0.0)
    nz = A180.life_metrics(dict(meals=[(7000, "blue")], poison="red", moving=5, Pf=None))
    C["fixture_zero_poison"] = dict(ok=nz["poison_final"] == 0 and abs(nz["net"] - 0.3) < 1e-9)
    m = A180.life_metrics(dict(meals=[(0, "blue"), (6666, "blue"), (6667, "blue"), (9999, "red")], poison="red",
                               moving=0, Pf=None))
    C["fixture_final_third_boundaries"] = dict(ok=m["food_final"] == 1 and m["poison_final"] == 1 and m["food_full"] == 3,
                                               note="tick 6666 (66.66 s) outside [200/3,100); 6667 inside")
    # 9. duplicate / missing ledger detection
    import ag_analysis as AA
    keys = [J.key(x) for x in J.life_jobs("x", AE.BASELINE, [1, 2])]
    rows = [dict(key=k, status="ok") for k in keys]
    dup = False
    try:
        AA.validate(rows + rows[:1], keys)
    except ValueError:
        dup = True
    miss = AA.validate(rows[1:], keys)
    extra = False
    try:
        AA.validate(rows + [dict(key="zzz", status="ok")], keys)
    except ValueError:
        extra = True
    C["fixture_duplicate_missing_extra_rows"] = dict(ok=dup and extra and miss == [keys[0]])
    # 10. held-positive output: one event, no re-arm while held; observer occupancy consistent
    C["fixture_held_positive_one_event"] = held_check()
    # 11. unarmed accounting: substep observer equals event/re-arm intervals; interval logic on synthetic input
    r, _ = J.life_one(J.life_jobs("check", AE.BASELINE, [8])[0])
    iv = J.unarmed_intervals(np.array([10, 50]), np.array([30, 70]), 100)
    iv2 = J.unarmed_intervals(np.array([10, 50]), np.array([30]), 100)
    C["unarmed_accounting"] = dict(ok=all(abs(r["motors"][m]["unarmed_s"] - r["motors"][m]["unarmed_from_intervals_s"]) < 1e-9
                                          for m in ("M0", "M1")) and iv == [(10, 30, False), (50, 70, False)]
                                   and iv2 == [(10, 30, False), (50, 100, True)], life=r["motors"])
    # 12. ranking tie-break
    C["fixture_ranking_tiebreak"] = AA.ranking_fixture()
    # 13. coupled noise: DT, DT/2, DT/4 share one Brownian path
    zs = {}
    for ratio in (1, 2, 4):
        e = GridEngine(9, config=EXTREMES[0], ratio=ratio, noise="coupled")
        zs[ratio] = e._z(e.tick_steps * 10).copy()
    ok = np.allclose(zs[2].reshape(-1, 2, zs[2].shape[1]).sum(1) / np.sqrt(2), zs[1], atol=1e-12) and \
        np.allclose(zs[4].reshape(-1, 2, zs[4].shape[1]).sum(1) / np.sqrt(2), zs[2], atol=1e-12)
    C["coupled_noise_summation"] = dict(ok=bool(ok), std=[float(zs[r].std()) for r in (1, 2, 4)])
    # 14. no hidden labels reach the brain: source scan and the calls Life makes
    src = inspect.getsource(GridBrain) + inspect.getsource(GridEngine) + inspect.getsource(AE._loop_obs)
    forbidden = [w for w in ("poison", "colour", "COLOURS", "sensor_map", "life.", "body", "sees") if w in src]
    from creature import Life
    calls = set()

    class Spy(GridBrain):
        def __getattribute__(self, name):
            if not name.startswith("_") and name in ("stimulate", "taste", "step", "drive"):
                calls.add(name)
            return object.__getattribute__(self, name)
    L = Life(8, "red", True, brain=lambda s: Spy(s))
    for _ in range(3000):
        L.step()
    C["no_hidden_labels_reach_brain"] = dict(ok=not forbidden and calls <= {"stimulate", "taste", "step"},
                                             forbidden_found=forbidden, calls=sorted(calls),
                                             note="taste is withheld in every grid life (learning=False); the spy life "
                                                  "has learning on only to show taste would be the only other call")
    valid = all(v["ok"] for v in C.values())
    out = dict(valid=bool(valid), checks=C, seconds=time.time() - t0,
               code={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.glob("*.py"))})
    path.write_text(json.dumps(out, indent=1, default=str) + "\n")
    for k, v in C.items():
        print(("PASS " if v["ok"] else "FAIL ") + k, flush=True)
    print("valid", valid, f"{time.time() - t0:.1f} s")
    return out


def transforms_check(D):
    """Every field difference from D180 v1 is one the named factor owns, with the declared factor."""
    bad = []
    for c in variants.configurations():
        a = 0.005 / c["motor_tau_s"]
        f, g = c["oscillator_speed"], c["sensory_gain"]
        for s in itertools.product((0, 1), repeat=2):
            G, B = variants.graph(c, s), D.graph(s)
            for n1, n0 in zip(G["nodes"], B["nodes"]):
                assert n1["name"] == n0["name"]
                for k in n0:
                    if n1[k] == n0[k]:
                        continue
                    nm = n0["name"]
                    exp = None
                    if nm in ("M0", "M1") and k == "R":
                        exp = n0[k] / a
                    elif nm in ("M0", "M1") and k == "bias":
                        exp = n0[k] * a
                    elif nm[0] in "XYB" and k == "R":
                        exp = n0[k] / f
                    elif nm[0] in "XYB" and k == "bias":
                        exp = n0[k] * f
                    if exp is None or abs(n1[k] - exp) > 1e-12 * abs(exp):
                        bad.append((c["id"], s, nm, k))
            for e1, e0 in zip(G["edges"], B["edges"]):
                assert e1["name"] == e0["name"]
                for k in e0:
                    if e1[k] == e0[k]:
                        continue
                    nm = e0["name"]
                    if k == "gain":
                        exp = e0[k]
                        if e0["to"] in ("M0", "M1"):
                            exp *= a
                        if nm.startswith(("side_", "plastic_")):
                            exp *= g
                        if e0["to"][0] in "XYB":
                            exp *= f
                        ok = abs(e1[k] - exp) <= 1e-12 * abs(exp)
                    elif k == "offset" and nm.startswith("explore_motor_"):
                        ok = e1[k] == c["exploration_threshold_V"]
                    else:
                        ok = False
                    if not ok:
                        bad.append((c["id"], s, nm, k))
    return dict(ok=not bad, violations=bad[:20], configs=81, wirings=4)


def adapter_check():
    from mixed_feedback import Circuit
    out = []
    for cfg in (AE.BASELINE, EXTREMES[0]):
        a, b = GridEngine(3, config=cfg), GridEngine(3, config=cfg)
        r = np.random.default_rng([3, 99])
        sch = []
        for t in range(300):
            for k in (0, 1):
                if r.random() < 0.3:
                    sch.append((t, a.ix[f"S{k}"], PULSES * 0.3e-9, float(r.random() * TICK)))
        Va, Vb = [], []
        for t in range(300):
            for tt, nd, cur, at in sch:
                if tt == t:
                    a.pulse(nd, cur, at)
                    b.c.pulse(nd, cur, at)
            a.run_tick()
            b.c.run(TICK)
            Va.append(a.V.copy())
            Vb.append(b.c.V.copy())
        out.append(dict(config=cfg, identical=bool(np.array_equal(np.array(Va), np.array(Vb)))))
    return dict(ok=all(o["identical"] for o in out), cases=out, ticks=300)


def held_check():
    from mixed_feedback import Circuit
    c = Circuit(seed=1, streams=True, substrate="silicon", volt=V_TYP, on_chip=True)
    c.node("held", bias=+0.6e-9, R=5e8, C=10e-12, lo=-RAIL, hi=RAIL, start=-0.45)
    c.element(0, 0, 1e-12, 0.0)
    c._ready()
    V, Vx = c.V.copy(), c.Vx.copy()
    armed, spikes, vmax = np.ones(1, np.bool_), np.zeros(1, np.int64), np.full(1, -np.inf)
    steps = int(round(TICK / DT))
    n_t = 100
    high, unarm = np.zeros((n_t, 1), np.int64), np.zeros((n_t, 1), np.int64)
    ev_s, ev_n_, ev_c = np.zeros(10, np.int64), np.zeros(10, np.int64), np.zeros(1, np.int64)
    ra_s, ra_n_, ra_c = np.zeros(10, np.int64), np.zeros(10, np.int64), np.zeros(1, np.int64)
    g = c.node_rng[0]
    for t in range(n_t):
        z = g.standard_normal((steps, 1))
        _loop_obs(V, Vx, armed, spikes, vmax, np.zeros((steps, 1)), c.node_arr, c.el_arr, c.link, z, c.q, c.rest, DT,
                  steps, c.cfg, np.full(1, np.inf), np.full(1, -np.inf), np.zeros(1, np.int64), np.zeros(1), np.zeros(1),
                  ev_s, ev_n_, ev_c, np.array([0]), t * steps, ra_s, ra_n_, ra_c, t, high, unarm, np.zeros(1),
                  np.zeros(1, np.int64), np.zeros(1, np.int64), np.ones(1, np.bool_))
    iv = J.unarmed_intervals(ev_s[:ev_c[0]], ra_s[:ra_c[0]], n_t * steps)
    # unarmed from the state after the event step to the end: n_t*steps - ev_step substeps
    ok = ev_c[0] == 1 and ra_c[0] == 0 and iv[0][2] and int(unarm.sum()) == n_t * steps - int(ev_s[0])
    return dict(ok=bool(ok), events=int(ev_c[0]), rearms=int(ra_c[0]), unarmed_substeps=int(unarm.sum()),
                event_step=int(ev_s[0]) if ev_c[0] else None, seconds=1.0)


def d180_reproduction():
    """Baseline native development seed 8 (all 12 lives) against the saved D180 archive: meals, firings, node events,
    P/E/X/M traces, arrays hash, wiring."""
    want = {}
    with open(D180_ARCHIVE, "rb") as f:
        while True:
            try:
                r = pickle.load(f)
            except EOFError:
                break
            if r["seed"] == 8:
                want[(r["arm"], r["poison"])] = r
    out = []
    for j in J.life_jobs("check", AE.BASELINE, [8]):
        r, a = J.life_one(j, trace=True)
        h = want[(j["arm"], j["poison"])]
        out.append(dict(arm=j["arm"], poison=j["poison"], meals=r["meals"] == [tuple(x) for x in h["meals"]] or
                        [list(x) for x in r["meals"]] == [list(x) for x in h["meals"]],
                        firings=r["firings"] == h["firings"], node_events=r["node_events"] == h["node_events"],
                        trace=bool(np.array_equal(a["trace"], h["trace"])), arrays_hash=r["arrays_hash"] == h["arrays_hash"],
                        wiring=r["sides"] == h["sides"] and r["sensor_map"] == h["sensor_map"]
                        and r["motor_map"] == h["motor_map"]))
    ok = all(all(v for k, v in o.items() if k not in ("arm", "poison")) for o in out)
    return dict(ok=ok, lives=out, archive=str(D180_ARCHIVE),
                note="historical ledger lacks motor-event sequences: event-time identity is not claimed from counts")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)

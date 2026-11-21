"""D180 R1/R2 checks: adapter identity, state/noise/interface tests, fixtures, static/physical limits and costs.

Writes lab/v/catalogue_brain_20261120/checks.json (refuses to overwrite). Every check is a named boolean with its
evidence; `valid` is the conjunction of the R1 identity checks that dependent inference needs.
"""
from __future__ import annotations

import hashlib
import inspect
import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

import brain as B                                                       # noqa: E402
from brain import CatalogueBrain, Engine, REMOVALS                      # noqa: E402
from design import graph, validate                                     # noqa: E402
from mixed_feedback import Circuit                                     # noqa: E402
from units import (C_MAX, DT, I_MIN, PULSE, R_MAX, RAIL, SLEW, STEP_MOVE, TAU_LEAK, TAU_LOOP, TAU_MAX, TICK,  # noqa
                   V_TYP)
from brains.circuit import PULSES                                      # noqa: E402

OUT = ROOT / "lab/v/catalogue_brain_20261120"


def traj(e, ticks, pulses=(), engine_path=True):
    """Run ticks; pulses: list of (tick, node, current, at). Returns per-tick V and spikes."""
    Vs, Ss = [], []
    by = {}
    for t, nd, cur, at in pulses:
        by.setdefault(t, []).append((nd, cur, at))
    for t in range(ticks):
        for nd, cur, at in by.get(t, ()):
            (e.pulse if engine_path else e.c.pulse)(nd, cur, at)
        sp = e.run_tick() if engine_path else e.c.run(TICK)
        Vs.append((e.V if engine_path else e.c.V).copy())
        Ss.append(sp)
    return np.array(Vs), np.array(Ss)


def sched(seed, ix, ticks):
    r = np.random.default_rng([seed, 99])
    out = []
    for t in range(ticks):
        for k in (0, 1):
            if r.random() < 0.3:
                out.append((t, ix[f"S{k}"], PULSES * 0.3e-9, float(r.random() * TICK)))
        if r.random() < 0.02:
            out.append((t, ix["T"], PULSES * 0.3e-9 * (1 if r.random() < .5 else -1), float(r.random() * TICK)))
    return out


def life_run(seed, ticks, **kw):
    from creature import Life
    L = Life(seed, "red", True, B.factory(**kw))
    for _ in range(ticks):
        L.step()
    return L


def main(path=None):
    path = Path(path) if path else OUT / "checks.json"
    if path.exists():
        raise SystemExit(f"{path} exists: refusing to overwrite")
    t0 = time.time()
    C = {}
    ix = Engine(0).ix
    # 1. adapter reproduces Circuit.pulse/run at DT on identical arrays and noise
    s = sched(3, ix, 300)
    a = Engine(3)
    b = Engine(3)
    Va, Sa = traj(a, 300, s, True)
    Vb, Sb = traj(b, 300, s, False)
    C["adapter_equals_circuit_run"] = dict(ok=bool(np.array_equal(Va, Vb) and np.array_equal(Sa, Sb)),
                                           max_abs=float(np.abs(Va - Vb).max()), ticks=300)
    # 2. identical-arm reproduction (closed loop, 10 s)
    L1, L2 = life_run(8, 1000), life_run(8, 1000)
    C["identical_arm_reproduction"] = dict(ok=bool(L1.meals == L2.meals and L1.firings == L2.firings and
                                                   np.array_equal(L1.brain.e.V, L2.brain.e.V)))
    # 3. logging on/off
    L3 = life_run(8, 1000, log=False)
    C["logging_on_off_identical"] = dict(ok=bool(L1.meals == L3.meals and L1.firings == L3.firings and
                                                 np.array_equal(L1.brain.e.V, L3.brain.e.V)))
    # 4. null stimuli versus explicitly empty queue
    a, b = Engine(4), Engine(4)
    nulls = [(t, ix["S0"], 0.0, 0.0037) for t in range(0, 200, 3)] + [(t, ix["T"], 0.0, 0.006) for t in range(0, 200, 7)]
    Va, Sa = traj(a, 200, nulls)
    Vb, Sb = traj(b, 200, [])
    C["null_stimuli_equal_empty_queue"] = dict(ok=bool(np.array_equal(Va, Vb) and np.array_equal(Sa, Sb)))
    # 5. chunk sizes identical at common output boundaries
    res = {}
    for ch in (1, 7, 100):
        B.CHUNK = ch
        e = Engine(5)
        res[ch] = traj(e, 210, sched(5, ix, 210))
        ec = Engine(5, ratio=2, noise="coupled")
        res[("c", ch)] = traj(ec, 210, sched(5, ix, 210))
    B.CHUNK = 100
    C["chunk_size_invariance"] = dict(ok=bool(all(np.array_equal(res[1][0], res[c][0]) and np.array_equal(res[1][1], res[c][1])
                                                  for c in (7, 100)) and
                                              all(np.array_equal(res[("c", 1)][0], res[("c", c)][0]) for c in (7, 100))),
                                      chunks=[1, 7, 100], noise=["native", "coupled r=2"])
    # 6. saved-state clone restores V, pending pulses, noise position, spike arming
    e = Engine(6)
    sch = sched(6, ix, 500)
    traj(e, 300, [p for p in sch if p[0] < 300])
    e.pulse(ix["S1"], PULSES * 0.3e-9, 0.0095)               # a pending pulse that runs on past the tick boundary
    snap = e.snapshot()
    later = [(t - 300, nd, c, at) for t, nd, c, at in sch if t >= 300]
    V1, S1 = traj(e, 200, later)
    e.restore(snap)
    V2, S2 = traj(e, 200, later)
    e2 = Engine(6)                                            # and an independent clone made from the same snapshot
    e2.restore(snap)
    V3, S3 = traj(e2, 200, later)
    C["snapshot_restore"] = dict(ok=bool(np.array_equal(V1, V2) and np.array_equal(S1, S2) and np.array_equal(V1, V3)),
                                 includes=["V", "Vx", "pending drive", "per-node RNG states", "noise buffer position",
                                           "armed", "observation accumulators"])
    # 7. paired intervention trajectories identical up to the intervention
    e = Engine(7)
    traj(e, 100, [])
    snap = e.snapshot()
    Vp, _ = traj(e, 50, [(20, ix["S0"], PULSES * 0.3e-9, 0.004)])
    e.restore(snap)
    Vo, _ = traj(e, 50, [])
    diff = np.flatnonzero(np.any(Vp != Vo, axis=1))
    C["paired_intervention_identical_before"] = dict(ok=bool(len(diff) and diff[0] == 20), first_diff_tick=int(diff[0]),
                                                     intervention_tick=20)
    # 8. coupled noise: DT, DT/2, DT/4 share one Brownian path; native vs coupled law
    zs = {}
    for r in (1, 2, 4):
        e = Engine(9, ratio=r, noise="coupled")
        zs[r] = e._z(e.tick_steps * 10).copy()
    ok = np.allclose(zs[2].reshape(-1, 2, zs[2].shape[1]).sum(1) / np.sqrt(2), zs[1], atol=1e-12) and \
        np.allclose(zs[4].reshape(-1, 2, zs[4].shape[1]).sum(1) / np.sqrt(2), zs[2], atol=1e-12)
    C["coupled_brownian_increments"] = dict(ok=bool(ok), std=[float(zs[r].std()) for r in (1, 2, 4)])
    # 9. wiring independent of graph variant; hidden labels not used
    w_ok = True
    for sd in range(20):
        sides = {rm: Engine(sd, removed=rm).sides for rm in REMOVALS}
        w_ok &= len(set(sides.values())) == 1
    from creature import Life
    for sd in range(5):
        maps = [(Life(sd, "red", True, B.factory(removed=rm)).sensor, Life(sd, "red", True, B.factory(removed=rm)).motor)
                for rm in REMOVALS]
        w_ok &= all(m == maps[0] for m in maps)
    src = inspect.getsource(B)
    forbidden = [w for w in ("poison", "colour", "COLOURS", "sensor_map", "life.") if w in src]
    C["wiring_independent_of_variant"] = dict(ok=bool(w_ok), seeds=20)
    C["no_hidden_labels_in_brain"] = dict(ok=not forbidden, forbidden_found=forbidden,
                                          note="brain.py receives only the seed; Life passes stimulate/taste/step")
    # 10. removal keeps original IDs and draws
    full = Engine(11)
    r_ok = True
    for rm in REMOVALS:
        e = Engine(11, removed=rm)
        r_ok &= np.array_equal(e.el, full.c.el_arr[:, e.keep]) and np.array_equal(e.node, full.node) and \
            np.array_equal(e.V, full.V) and len(e.keep) == 22 - len(REMOVALS[rm])
    C["removal_keeps_draws"] = dict(ok=bool(r_ok))
    # 11. engine fixture: an output held above zero for a full period gives one event, no re-arming
    c = Circuit(seed=1, streams=True, substrate="silicon", volt=V_TYP, on_chip=True)
    c.node("held", bias=+0.6e-9, R=5e8, C=10e-12, lo=-RAIL, hi=RAIL, start=-0.45)
    c.element(0, 0, 1e-12, 0.0)
    n = sum(int(c.run(TICK)[0]) for _ in range(100))
    C["fixture_held_output_one_event"] = dict(ok=n == 1, events=n, seconds=1.0)
    # 12. analysis fixtures
    C.update(fixtures())
    # physical/static
    phys = physical()
    C.update(phys["checks"])
    valid = all(v["ok"] for v in C.values())
    out = dict(valid=bool(valid), checks=C, physical=phys["detail"], costs=phys["costs"], seconds=time.time() - t0,
               code_hashes={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.glob("*.py"))},
               graph_hash=hashlib.sha256(json.dumps(graph(), sort_keys=True).encode()).hexdigest())
    path.write_text(json.dumps(out, indent=1, default=float) + "\n")
    for k, v in C.items():
        print(("PASS " if v["ok"] else "FAIL ") + k)
    print("valid", valid, f"{time.time() - t0:.1f} s")
    return out


def fixtures():
    from analyse import life_metrics, acquisition, validate_ledger, summary
    C = {}
    z = life_metrics(dict(meals=[], poison="red", moving=None, Pf=None))
    C["fixture_zero_movement_zero_meals"] = dict(ok=z["stranded"] == 1 and z["never_moved"] == 1 and z["net"] == 0.0
                                                 and z["food_rate_final"] == 0.0)
    m = life_metrics(dict(meals=[(0, "blue"), (6666, "blue"), (6667, "blue"), (9999, "red")], poison="red", moving=0, Pf=None))
    C["fixture_window_boundaries"] = dict(ok=m["food_final"] == 1 and m["poison_final"] == 1 and m["food_full"] == 3
                                          and m["food_first"] == 1 and m["food_second"] == 1 and m["stranded"] == 0,
                                          note="meal tick 6666 (66.66 s) is outside [200/3,100), 6667 inside, 0 counted")
    nz = life_metrics(dict(meals=[(7000, "blue")], poison="red", moving=5, Pf=None))
    C["fixture_zero_poison"] = dict(ok=nz["poison_final"] == 0 and abs(nz["job_linear"] - 0.3) < 1e-9)
    pf = np.r_[np.full(10, .15), np.full(10, .3), np.full(10, .15), np.full(10, .3)]
    pp = np.zeros(40)
    a = acquisition(pf, pp)
    C["fixture_loss_and_reacquisition"] = dict(ok=a["acq_entries"] == 2 and a["acq_exits"] == 1 and a["acq_reentries"] == 1
                                               and a["acq_final"] and abs(a["acq_first_s"] - 0.11) < 1e-9, detail=a)
    a0 = acquisition(np.full(5, .15), np.zeros(5))
    C["fixture_no_acquisition_missing_not_zero"] = dict(ok=a0["acq_first_s"] is None)
    rows = [dict(stage="x", version=1, arm="a", seed=s, poison=p, ratio=1) for s in (1, 2) for p in ("red", "blue")]
    from lives import key
    exp = [key(r) for r in rows]
    dup_caught = False
    try:
        validate_ledger(rows + rows[:1], exp)
    except ValueError:
        dup_caught = True
    missing = validate_ledger(rows[1:], exp)
    C["fixture_duplicate_and_missing_rows"] = dict(ok=dup_caught and missing == [exp[0]])
    return C


def spec_of(g, removed=()):
    ix = {n["name"]: i for i, n in enumerate(g["nodes"])}
    edges = [e for e in g["edges"] if e["name"] not in removed]
    return dict(nodes=[[n["name"], n["bias"], n["R"], n["C"], n["lo"], n["hi"], None, n["memory"]] for n in g["nodes"]],
                elements=[[ix[e["to"]], ix[e["source"]], -1 if e["gate"] is None else ix[e["gate"]], e["gain"],
                           e["offset"], e["slope"], e["tau"], e["sigmoid"]] for e in edges],
                sensors=[ix[n] for n in g["sensors"]], taste=ix[g["taste"]])


def physical(seeds=range(8)):
    import chip
    from minimal.spice import count
    checks, detail = {}, {}
    detail["nominal_validate_all_sides"] = [validate(graph(s)) for s in itertools.product((0, 1), repeat=2)]
    g = graph()
    expected_neg = {f"write_negative_{k}" for k in (0, 1)}
    signs = {e["name"]: (np.sign(e["gain"]), np.sign(e["slope"])) for e in g["edges"]}
    sign_ok = all((s[1] < 0) == (nm in expected_neg) for nm, s in signs.items())
    neg_gain = sorted(nm for nm, s in signs.items() if s[0] < 0)
    checks["signed_slopes_as_designed"] = dict(ok=bool(sign_ok), negative_slope=sorted(expected_neg),
                                               negative_gain=neg_gain)
    checks["no_interior_clamps"] = dict(ok=all(n["lo"] == -RAIL and n["hi"] == RAIL for n in g["nodes"]))
    checks["no_implicit_filters"] = dict(ok=all(e["tau"] == 0 for e in g["edges"]))
    realised, worst = [], dict(C=0, R=0, I_min=np.inf, slew=0, loop=0, tau_min=np.inf, tau_max=0)
    for sd in seeds:
        e = Engine(sd)
        node, el, link = e.node, e.el, e.link
        bias, leak, cap = node[0], node[1], node[2]
        worst["C"] = max(worst["C"], float(cap.max()))
        R = 1 / leak[leak > 0]
        worst["R"] = max(worst["R"], float(R.max()))
        tau = R * cap[leak > 0]
        worst["tau_min"], worst["tau_max"] = min(worst["tau_min"], float(tau.min())), max(worst["tau_max"], float(tau.max()))
        cur = np.r_[np.abs(el[0]), np.abs(bias[bias != 0])]
        worst["I_min"] = min(worst["I_min"], float(cur.min()))
        sl = np.abs(el[0]) / cap[link[0]]
        worst["slew"] = max(worst["slew"], float(sl.max()))
        selfl = link[0] == link[1]
        worst["loop"] = max(worst["loop"], float((np.abs(el[0] * el[2]) / cap[link[0]])[selfl].max()))
        pulse_slew = PULSES * e.unit() / cap[[e.ix["S0"], e.ix["S1"], e.ix["T"]]].min()
        realised.append(dict(seed=sd, sides=e.sides, arrays_hash=e.arrays_hash(), cap=cap.tolist(), leak=leak.tolist(),
                             bias=bias.tolist(), gain=el[0].tolist(), offset=el[1].tolist(), slope=el[2].tolist(),
                             init=e.V.tolist(), pulse_slew=float(pulse_slew)))
    detail["realised_component_arrays_seeds_0_7"] = realised
    detail["worst_realised"] = worst
    checks["realised_C_max"] = dict(ok=worst["C"] <= C_MAX, value=worst["C"], limit=C_MAX)
    checks["realised_R_max"] = dict(ok=worst["R"] <= R_MAX, value=worst["R"], limit=R_MAX)
    checks["realised_I_min"] = dict(ok=worst["I_min"] >= I_MIN, value=worst["I_min"], limit=I_MIN)
    checks["realised_element_slew"] = dict(ok=worst["slew"] <= SLEW, value=worst["slew"], limit=SLEW)
    checks["realised_self_loop"] = dict(ok=worst["loop"] <= 1 / TAU_LOOP, value=worst["loop"], limit=1 / TAU_LOOP)
    checks["realised_leak_tau"] = dict(ok=worst["tau_min"] >= TAU_LEAK and worst["tau_max"] <= TAU_MAX,
                                       min=worst["tau_min"], max=worst["tau_max"], limits=[TAU_LEAK, TAU_MAX])
    checks["realised_pulse_slew"] = dict(ok=max(r["pulse_slew"] for r in realised) <= SLEW,
                                         value=max(r["pulse_slew"] for r in realised), limit=SLEW)
    e = Engine(0)
    checks["supply_fading_on"] = dict(ok=bool(e.cfg[3] > 0 and e.cfg[4] > 0 and e.cfg[5] > 0),
                                      cfg=dict(volt=e.cfg[0], half=e.cfg[2], knee_p=e.cfg[3], knee_n=e.cfg[4], dead=e.cfg[5]))
    # aggregate slew and pre-clip at recorded states: two development seeds, 10 s closed loop
    agg = []
    for sd in (8, 9):
        L = life_run(sd, 1000)
        en = L.brain.e
        agg.append(dict(seed=sd, max_dV_over_C=float(en.slew_o.max()), node=en.c.names[int(np.argmax(en.slew_o))],
                        clip_steps={en.c.names[i]: int(en.clip_o[i]) for i in range(len(en.V)) if en.clip_o[i]},
                        preclip_extreme=float(en.preclip_o[np.argmax(np.abs(en.preclip_o))])))
    detail["aggregate_slew_recorded_10s"] = agg
    checks["aggregate_slew_recorded"] = dict(ok=all(a["max_dV_over_C"] * DT <= STEP_MOVE for a in agg),
                                             value=max(a["max_dV_over_C"] for a in agg), limit=SLEW,
                                             note="deterministic |dV|/C at every recorded step (noise excluded)")
    detail["clipping_note"] = ("Pre-clip rail excursions are tracked (observation only) per node; clipping in "
                               "closed-loop lives is reported per life, not hidden; it is not a check failure here.")
    # costs
    costs = {}
    for rm in REMOVALS:
        costs[rm] = dict(parts=count(spec_of(g, REMOVALS[rm])),
                         static_power_W=float(Engine(0, removed=rm).cfg[1]))
    costs["note"] = ("minimal.spice.count of chip.py blocks as designed (nominal, no SPICE run): includes the four "
                     "retained SONOS cells and their high-voltage write switches, the two charge-pump supplies "
                     "counted as sources, oscillator bias writers, gate pairs, steep-slope preamplifiers (slope "
                     "18/V_TYP = 60/V > native 26/V) and the motor output nodes. The body's pulse sources and the "
                     "motor readout boundary (Schmitt/thruster driver) are outside the brain. Memory high-voltage "
                     "supply energy: UNMEASURED (not zero).")
    return dict(checks=checks, detail=detail, costs=costs)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)

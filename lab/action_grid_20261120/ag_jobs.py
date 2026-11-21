"""Action grid jobs (work order sections 6-7): fixed benches (10 s, no body) and closed-loop lives (100 s, unchanged
creature.Life, taste withheld). One job -> one compact row (JSON-able) plus an archive record (numpy arrays).

Time conventions (D180's): a motor event or re-arm at fine step k is reported at k*dt; a pulse's onset is its physical
time. A motor is unarmed from its event step e (state after step e) until its re-arm step r (state after r armed):
duration (r - e)*dt; an interval still open at the end is censored at the run's end. Window [a, b) uses event times.
"""
from __future__ import annotations

import hashlib
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ag_engine as AE                                           # noqa: E402
from ag_engine import GridBrain, GridEngine                      # noqa: E402
from units import DT, PULSE, TICK, V_TYP                         # noqa: E402
from brains.circuit import PULSES                                # noqa: E402

LIFE_S = 100.0
LIFE_TICKS = int(round(LIFE_S / TICK))                          # derived from units.TICK and 100 s
BENCH_S = 10.0
BENCH_TICKS = int(round(BENCH_S / TICK))
BENCH_WINDOWS = ((0.0, 1.0), (1.0, 3.25), (3.25, 10.0))
P_BENCH = (0.0, 0.15, 0.30)
SCHEDULES = ("silent", "single", "train", "sustained")
BENCH_REMOVALS = ("none", "no_explore")
NEAR = 0.010                                                    # s: opposite-motor event window (work order 7.5)
PULSE_WIN = ((0.0, 0.05), (0.05, 0.25))                         # s after a sensory onset (work order 7)


def key(j):
    """(stage, configuration, arm/schedule, removal, seed, poison/P, channel, integration ratio, noise mode)."""
    return "|".join(str(x) for x in (j["stage"], j["config"], j["arm"], j["removed"], j["seed"],
                                       j.get("poison", j.get("P")), j.get("channel"), f"r{j['ratio']}", j["noise"]))


# ------------------------------------------------------------------------------------------------ shared measures
def unarmed_intervals(evs, ras, end_step):
    """evs, ras: sorted fine-step indices of one motor's events and re-arms. Returns [(start, stop, censored)]."""
    out, ri = [], 0
    for e in evs:
        while ri < len(ras) and ras[ri] <= e:
            ri += 1
        if out and e < out[-1][1]:                               # an event while unarmed is impossible in the engine
            raise AssertionError("event while unarmed")
        if ri < len(ras):
            out.append((int(e), int(ras[ri]), False))
            ri += 1
        else:
            out.append((int(e), int(end_step), True))
    return out


def motor_window(e, j, a, b, intervals, evt, rat):
    """Motor j's measures in window [a, b) s (substep occupancy from the observer's per-tick counts)."""
    ta, tb = int(round(a / TICK)), int(round(b / TICK))
    dt = e.dt
    ev = evt[(evt >= a - 1e-12) & (evt < b - 1e-12)]
    ra = rat[(rat >= a - 1e-12) & (rat < b - 1e-12)]
    sa, sb = int(round(a / dt)), int(round(b / dt))
    longest = 0
    for s0, s1, _ in intervals:
        ov = min(s1, sb) - max(s0, sa)
        longest = max(longest, ov)
    return dict(events=int(len(ev)), rearms=int(len(ra)), first_event_s=float(ev[0]) if len(ev) else None,
                high_s=float(e.high_t[ta:tb, j].sum() * dt), unarmed_s=float(e.unarm_t[ta:tb, j].sum() * dt),
                longest_unarmed_s=float(longest * dt))


def motor_records(e, end_step):
    k = int(e.ev_n[0])
    evs, evm = e.ev_step[:k], e.ev_node[:k]
    q = int(e.ra_n[0])
    ras, ram = e.ra_step[:q], e.ra_node[:q]
    per = []
    for j in (0, 1):
        ej, rj = np.sort(evs[evm == j]), np.sort(ras[ram == j])
        per.append(dict(ev=ej, ra=rj, iv=unarmed_intervals(ej, rj, end_step)))
    return per


def realised_ok(e):
    w = e.realised()
    return w, not w["failed"]


# ------------------------------------------------------------------------------------------------ benches
def bench_jobs(config):
    out = []
    for seed in range(8):
        for P in P_BENCH:
            for rm in BENCH_REMOVALS:
                for ch in (0, 1):
                    for sc in SCHEDULES:
                        out.append(dict(stage="bench", config=config, arm=sc, removed=rm, seed=seed, P=P, channel=ch,
                                        ratio=1, noise="native"))
    return out


def schedule_times(seed, channel, sc):
    j = float(np.random.default_rng([seed, 182, channel]).uniform(0, 0.009))
    n = dict(silent=0, single=1, train=10, sustained=100)[sc]
    return j, [1.0 + j + 0.02 * k for k in range(n)]


def bench_one(job):
    t0 = time.time()
    out = dict(job, key=key(job))
    e = GridEngine(job["seed"], config=job["config"], P0=(job["P"], job["P"]), removed=job["removed"],
                   ticks=BENCH_TICKS)
    w, ok = realised_ok(e)
    out.update(sides=list(e.sides), arrays_hash_birth=e.arrays_hash(), realised=w)
    # A realised-limit failure is a named invalid job: still simulated (diagnostic only), never scored as valid
    jit, times = schedule_times(job["seed"], job["channel"], job["arm"])
    out["jitter_s"], out["n_pulses"] = jit, len(times)
    node = e.ix[f"S{job['channel']}"]
    amp = PULSES * e.unit()
    pend = sorted(times)
    ix = e.ix
    seg = []                                          # per-window accumulators of the observer, reset at boundaries
    bounds = [int(round(b / TICK)) for _, b in BENCH_WINDOWS]
    Pstart = [float(e.V[ix["P0"]]), float(e.V[ix["P1"]])]
    pw0, Pw, last = e.power_sum, [Pstart], 0
    for t in range(BENCH_TICKS):
        start = t * TICK
        while pend and pend[0] < start + TICK - 1e-12:
            e.pulse(node, amp, pend.pop(0) - start)
        e.run_tick()
        if not e.finite[0]:
            out.update(status="nonfinite", reason=f"nonfinite pre-clip state in tick {t}")
            return out, None
        if t + 1 in bounds:
            seg.append(dict(vmin=e.vmin_o.copy(), vmax=e.vmax_o.copy(), clip=e.clip_o.copy(), preclip=e.preclip_o.copy(),
                            slew=e.slew_o.copy(), power=(e.power_sum - pw0) / (t + 1 - last) / e.tick_steps * e.ratio))
            pw0, last = e.power_sum, t + 1
            Pw.append([float(e.V[ix["P0"]]), float(e.V[ix["P1"]])])
            n = len(e.V)
            e.vmin_o, e.vmax_o = np.full(n, np.inf), np.full(n, -np.inf)
            e.clip_o, e.preclip_o, e.slew_o = np.zeros(n, np.int64), np.zeros(n), np.zeros(n)
    assert not pend
    out["overflow"] = e.overflow()
    end = e.t_step
    per = motor_records(e, end)
    names = e.c.names
    side = e.sides[job["channel"]]
    wins = []
    for wi, (a, b) in enumerate(BENCH_WINDOWS):
        s = seg[wi]
        M = {}
        for j in (0, 1):
            m = motor_window(e, j, a, b, per[j]["iv"], per[j]["ev"] * e.dt, per[j]["ra"] * e.dt)
            m["Vmin"], m["Vmax"] = float(s["vmin"][e.motors[j]]), float(s["vmax"][e.motors[j]])
            M[f"M{j}"] = m
        wins.append(dict(window=[a, b], motors=M,
                         clip_by_node={names[i]: int(s["clip"][i]) for i in range(len(names)) if s["clip"][i]},
                         preclip_extreme=float(s["preclip"][np.argmax(np.abs(s["preclip"]))]),
                         slew_max_Vps=float(s["slew"].max()), slew_node=names[int(np.argmax(s["slew"]))],
                         power_W=float(s["power"]),
                         P_start=Pw[wi], P_end=Pw[wi + 1]))
    out.update(status="ok" if ok else "invalid_realised", reason=None if ok else w["failed"], fixed_motor=int(side), other_motor=int(1 - side), windows=wins,
               P_birth=[job["P"], job["P"]], P_start=Pstart, P_end=Pw[-1],
               P_drift=float(max(abs(Pw[-1][k] - job["P"]) for k in (0, 1))),
               clip_total=int(sum(sum(w["clip_by_node"].values()) for w in wins)),
               power_W=float(e.power()), node_events={names[i]: int(e.nspk[i]) for i in range(len(names))},
               wall_s=time.time() - t0)
    if out["overflow"]:
        out["status"] = "invalid_overflow"
    arch = dict(key=out["key"], ev=[p["ev"].astype(np.int32) for p in per], ra=[p["ra"].astype(np.int32) for p in per],
                pulses=np.array(times))
    return out, arch


def bench_group(args):
    """One worker task: all 48 bench jobs of one (config, seed)."""
    config, seed = args
    rows, archs = [], []
    for j in bench_jobs(config):
        if j["seed"] != seed:
            continue
        try:
            r, a = bench_one(j)
        except Exception as ex:                                   # implementation failure: an explicit failed row
            r, a = dict(j, key=key(j), status="error", reason=repr(ex)), None
        rows.append(r)
        archs.append(a)
    return list(zip(rows, archs))


# ------------------------------------------------------------------------------------------------ lives
ARMS = (("informed", "informed", "none"), ("neutral", "neutral", "none"), ("reversed", "reversed", "none"),
        ("no_explore", "informed", "no_explore"), ("no_sensory", "informed", "no_sensory"))
ALLFOOD = (("informed_allfood", "informed", "none"), ("neutral_allfood", "neutral", "none"))
ARM_GROUPS = [a for a, _, _ in ARMS] + [a for a, _, _ in ALLFOOD]


def life_jobs(stage, config, seeds, ratio=1, noise="native"):
    out = []
    for s in seeds:
        for c in ("red", "blue"):
            for arm, P, rm in ARMS:
                out.append(dict(stage=stage, config=config, arm=arm, removed=rm, seed=s, poison=c, channel=None, P=P,
                                ratio=ratio, noise=noise))
        for arm, P, rm in ALLFOOD:
            out.append(dict(stage=stage, config=config, arm=arm, removed=rm, seed=s, poison=None, channel=None, P=P,
                            ratio=ratio, noise=noise))
    return out


def birth_P(mode, life):
    """D180 lives.birth_P, unchanged in substance (imported convention)."""
    if mode == "neutral":
        return (V_TYP / 2, V_TYP / 2)
    if life.poison is None:
        assert mode == "informed"
        return (V_TYP, V_TYP)
    food = "blue" if life.poison == "red" else "red"
    P = [0.0, 0.0]
    good, bad = (V_TYP, 0.0) if mode == "informed" else (0.0, V_TYP)
    P[life.sensor[food]], P[life.sensor[life.poison]] = good, bad
    return tuple(P)


def life_one(job, trace=False, observe_body=True):
    from creature import Life
    import analyse as A180                                         # D180 metrics (catalogue_brain_20261120/analyse.py)
    t0 = time.time()
    out = dict(job, key=key(job))
    life = Life(job["seed"], job["poison"], False,
                brain=lambda s: GridBrain(s, config=job["config"], removed=job["removed"], ratio=job["ratio"],
                                          noise=job["noise"], trace=trace, ticks=LIFE_TICKS))
    b, e = life.brain, life.brain.e
    w, ok = realised_ok(e)
    out.update(sides=list(e.sides), arrays_hash_birth=e.arrays_hash(), realised=w, sensor_map=dict(life.sensor),
               motor_map=dict(life.motor))
    P = birth_P(job["P"], life)
    b.set_P(P)
    body = life.body
    btr = np.zeros((LIFE_TICKS, 8))                                # pre-step x, y, heading, vx, vy, spin, red, blue
    if observe_body:
        orig = body.sees

        def sees():                                                # passive: Life.step calls this first, pre-step
            d = orig()
            t = life.t
            btr[t, 0:2] = body.pos
            btr[t, 2] = body.heading
            btr[t, 3:5] = body.speed
            btr[t, 5] = body.spin
            btr[t, 6], btr[t, 7] = d["red"], d["blue"]
            return d
        body.sees = sees
    for t in range(LIFE_TICKS):
        life.step()
        if not e.finite[0]:
            out.update(status="nonfinite", reason=f"nonfinite pre-clip state in tick {t}")
            return out, None
    names = e.c.names
    end = e.t_step
    per = motor_records(e, end)
    dt = e.dt
    out["overflow"] = e.overflow()
    out["arrays_hash"] = e.arrays_hash()                          # D180 convention: arrays plus FINAL state
    # 1. D180 per-life ledger quantities and metrics
    food = None if life.poison is None else ("blue" if life.poison == "red" else "red")
    fk = None if food is None else life.sensor[food]
    Pr = b.P_rows
    out.update(meals=[(int(t), c) for t, c in life.meals], moving=life.moving, firings=len(life.firings),
               power_W=float(e.power()), motor_events=int(e.nspk[b.M].sum()),
               node_events={names[i]: int(e.nspk[i]) for i in range(len(names))},
               body_pulses=[sum(1 for _, s in b.pulses if s == k) for k in (0, 1)], tastes=len(b.tastes),
               clip_steps=int(e.clip_o.sum()), clip_by_node={names[i]: int(e.clip_o[i]) for i in range(len(names))
                                                             if e.clip_o[i]},
               preclip_extreme=float(e.preclip_o[np.argmax(np.abs(e.preclip_o))]),
               vmin={names[i]: float(e.vmin_o[i]) for i in range(len(names))},
               vmax={names[i]: float(e.vmax_o[i]) for i in range(len(names))},
               slew_max_Vps=float(e.slew_o.max()), slew_node=names[int(np.argmax(e.slew_o))],
               P_birth=[float(x) for x in P], P_end=[float(Pr[-1, 0]), float(Pr[-1, 1])],
               P_min=[float(Pr[:, k].min()) for k in (0, 1)], P_max=[float(Pr[:, k].max()) for k in (0, 1)],
               P_drift=[float(Pr[-1, k] - P[k]) for k in (0, 1)], food_sensor=fk)
    Pcap = [float(e.node[2, b.P[k]]) for k in (0, 1)]
    dP = np.diff(np.concatenate([[out["P_birth"]], Pr.astype(float)]), axis=0)
    out["write_charge_abs_C"] = float(sum(Pcap[k] * np.abs(dP[:, k]).sum() for k in (0, 1)))
    m_in = dict(meals=out["meals"], poison=life.poison, moving=life.moving, Pf=None if fk is None else Pr[:, fk],
                Pp=None if fk is None else Pr[:, 1 - fk])
    out["m"] = A180.life_metrics(m_in)
    # edge source events (labelled proxies, not communication energy) and gate duty
    en = e.edge_names()
    steps = e.t_step
    edges = {}
    for jj, nm in enumerate(en):
        src = names[int(e.link[1, jj])]
        gi = int(e.link[2, jj])
        edges[nm] = dict(source=src, source_events=int(e.nspk[e.link[1, jj]]),
                         gate=None if gi < 0 else names[gi],
                         gate_mean=None if gi < 0 else float(e.gsum[jj] / steps),
                         gate_open_fraction=None if gi < 0 else float(e.gopen[jj] / steps))
    out["edges"] = edges
    from minimal.spec import FIRING
    out["motor_energy_J"] = float(len(life.firings) * FIRING)
    out["circuit_energy_J"] = float(e.power() * LIFE_S)
    # 3. per-motor occupancy and recovery
    M = {}
    for j in (0, 1):
        evt, rat = per[j]["ev"] * dt, per[j]["ra"] * dt
        whole = motor_window(e, j, 0.0, LIFE_S, per[j]["iv"], evt, rat)
        iv_s = sum(s1 - s0 for s0, s1, _ in per[j]["iv"]) * dt
        whole["unarmed_from_intervals_s"] = float(iv_s)
        whole["censored_open_interval"] = bool(per[j]["iv"] and per[j]["iv"][-1][2])
        M[f"M{j}"] = whole
    out["motors"] = M
    # 4. body observation (analyst-only; never fed back)
    if observe_body:
        vis = btr[:, 6:8]
        either = (vis > 0).any(1)
        d = btr[1:, 0:2] - btr[:-1, 0:2]
        d = (d + 0.03) % 0.06 - 0.03                                  # world.WORLD = 60 mm torus
        from world import WORLD
        assert abs(WORLD - 0.06) < 1e-12
        thirds = {}
        for nm, (a, bb) in dict(full=(0, LIFE_TICKS), final=(int(math.ceil(LIFE_TICKS * 2 / 3)), LIFE_TICKS)).items():
            sl = slice(a, bb)
            dd = d[a:bb - 1]
            thirds[nm] = dict(see_either_s=float(either[sl].sum() * TICK), see_neither_s=float((~either[sl]).sum() * TICK),
                              mean_vis_red=float(vis[sl, 0].mean()), mean_vis_blue=float(vis[sl, 1].mean()),
                              path_m=float(np.hypot(dd[:, 0], dd[:, 1]).sum()),
                              angle_rad=float(np.abs(np.diff(btr[sl, 2])).sum()))
        if fk is not None:
            for nm in thirds:
                sl = slice(0, LIFE_TICKS) if nm == "full" else slice(int(math.ceil(LIFE_TICKS * 2 / 3)), LIFE_TICKS)
                fcol = 6 + (0 if food == "red" else 1)
                thirds[nm]["mean_vis_food"] = float(btr[sl, fcol].mean())
                thirds[nm]["mean_vis_poison"] = float(btr[sl, 13 - fcol].mean())
        out["body"] = thirds
    # 5. bilateral coordination
    fire = np.zeros((LIFE_TICKS, 2), np.int64)
    for t, f in life.firings:
        fire[t, 0 if f == "left" else 1] += 1
    pairs = int(np.minimum(fire[:, 0], fire[:, 1]).sum())
    tot = int(fire.sum())
    near = 0
    ev0, ev1 = per[0]["ev"] * dt, per[1]["ev"] * dt
    for a_, b_ in ((ev0, ev1), (ev1, ev0)):
        if len(a_) and len(b_):
            i = np.searchsorted(b_, a_)
            lo = np.abs(a_ - b_[np.clip(i - 1, 0, len(b_) - 1)])
            hi = np.abs(b_[np.clip(i, 0, len(b_) - 1)] - a_)
            near += int((np.minimum(lo, hi) <= NEAR + 1e-12).sum())
    nev = len(ev0) + len(ev1)
    out["coordination"] = dict(simultaneous_pairs=pairs, body_events=tot,
                               paired_fraction=None if tot == 0 else 2 * pairs / tot,
                               circuit_events=nev, near_opposite_fraction=None if nev == 0 else near / nev,
                               note="near_opposite is nonexclusive (within 0.010 s)")
    # pulse-locked temporal association (not causal attribution)
    pul = np.array(b.pulses) if b.pulses else np.zeros((0, 2))
    roles = dict(fixed=[], other=[])
    for t_on, ch in pul:
        ch = int(ch)
        s_on = int(math.floor(t_on / dt + 1e-9))
        for role, j in (("fixed", e.sides[ch]), ("other", 1 - e.sides[ch])):
            un = any(s0 <= s_on - 1 < s1 for s0, s1, _ in per[j]["iv"]) if per[j]["iv"] else False
            ev = per[j]["ev"] * dt
            c = [int(((ev >= t_on + a - 1e-12) & (ev < t_on + bb - 1e-12)).sum()) for a, bb in PULSE_WIN]
            roles[role].append((un, c[0], c[1]))
    out["pulses"] = dict(n=int(len(pul)), **{
        role: None if not v else dict(unarmed_before=float(np.mean([x[0] for x in v])),
                                      events_0_50ms=float(np.mean([x[1] for x in v])),
                                      events_50_250ms=float(np.mean([x[2] for x in v])))
        for role, v in roles.items()})
    out["status"] = "ok" if ok else "invalid_realised"                 # invalid: diagnostic only, never valid
    if out["overflow"]:
        out["status"] = "invalid_overflow"
    out["reason"] = None if ok else w["failed"]
    out["wall_s"] = time.time() - t0
    arch = dict(key=out["key"], ev=[p["ev"].astype(np.int32) for p in per], ra=[p["ra"].astype(np.int32) for p in per],
                pulses=pul.astype(np.float64), firings=np.array([(t, 0 if f == "left" else 1) for t, f in life.firings],
                                                               np.int32).reshape(-1, 2))
    if trace:
        arch["trace"] = b.rows
        if job["stage"] != "confirm":                              # body traces: baseline development only
            arch["body"] = btr.astype(np.float32)
        out["trace_sha"] = hashlib.sha256(b.rows.tobytes()).hexdigest()[:16]
        out["Pf_hash"] = None if fk is None else hashlib.sha256(np.ascontiguousarray(b.rows[:, 2 + fk]).tobytes()).hexdigest()[:12]
    return out, arch


def life_task(args):
    job, trace = args
    try:
        return life_one(job, trace=trace)
    except Exception as ex:
        import traceback
        return dict(job, key=key(job), status="error", reason=repr(ex), tb=traceback.format_exc()), None

"""D180 R3/R4 component and assembled-response benches (work order section 3). No body: inputs are the body's own
pulse amplitude (PULSES x unit, PULSE long) into S/T; full silicon noise and mismatch; component seeds 0-7, wiring
from each seed's own wiring draw; all four side combinations on seed 0 as wiring fixtures.

  A  quiet/startup/retention, 100 s, no inputs: P (both) neutral, 0, V_TYP; plus oscillator bias-writer removal.
  B  writes: 1 s, one S pulse, then +-T after {0.005, 0.05, 0.2} s; controls no S, no T, both S; 10-pulse train.
  C  sensory authority: 10 s no-input prefix (P both 0, V_TYP/2, V_TYP); 16 trial times U[10,20] s per seed/channel;
     each trial forks present/omitted from an identical prefix snapshot; paired second pulse after
     {0.005, 0.02, 0.05, 0.2} s; repeated with explore_motor edges removed.

usage: bench.py OUTDIR [--version N]   (refuses to overwrite)
"""
from __future__ import annotations

import json
import sys
import zlib
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))

from brain import Engine                                    # noqa: E402
from units import PULSE, TICK, V_TYP                        # noqa: E402
from brains.circuit import PULSES                           # noqa: E402

SEEDS = range(8)
P_LEVELS = dict(zero=0.0, half=V_TYP / 2, typ=V_TYP)
DELAYS = (0.005, 0.05, 0.2)
PAIR = (0.005, 0.02, 0.05, 0.2)
SPEC = None


def eng(seed, **kw):
    return Engine(seed, spec=SPEC, **kw)


def amp(e):
    return PULSES * e.unit()


def run_until(e, t_end, pulses=()):
    """Run whole ticks from e's current time until t_end (s); pulses: absolute (time, node, current)."""
    pend = sorted(pulses)
    while e.t_step * e.dt < t_end - 1e-12:
        start = e.t_step * e.dt
        while pend and pend[0][0] < start + TICK - 1e-12:
            t, nd, cur = pend.pop(0)
            assert t >= start - 1e-12
            e.pulse(nd, cur, max(t - start, 0.0))
        e.run_tick()


# ---------------------------------------------------------------------------------------------------------- A
def bench_A(seed, P, removed="none", sides=None, seconds=100.0):
    e = eng(seed, P0=(P, P), removed=removed, sides=sides)
    ix = e.ix
    X = {k: [] for k in (0, 1)}
    M = {k: [] for k in (0, 1)}
    Bv = {k: [] for k in (0, 1)}
    Xspk = np.zeros(2, int)
    t10 = None
    for t in range(int(round(seconds / TICK))):
        sp = e.run_tick()
        for k in (0, 1):
            X[k].append(e.V[ix[f"X{k}"]]); M[k].append(e.V[ix[f"M{k}"]]); Bv[k].append(e.V[ix[f"B{k}"]])
            if t * TICK >= 10.0:
                Xspk[k] += sp[ix[f"X{k}"]]
    evt, evm = e.events()
    rt, rm = e.rearms()
    out = dict(seed=seed, P=P, removed=removed, sides=list(e.sides), arrays_hash=e.arrays_hash())
    for k in (0, 1):
        x, m, b = np.array(X[k]), np.array(M[k]), np.array(Bv[k])
        tail = x[1000:]
        ev_k = evt[evm == k]
        up = np.flatnonzero((x[:-1] <= 0) & (x[1:] > 0))
        out[f"osc{k}"] = dict(
            startup_s=float((up[0] + 1) * TICK) if len(up) else None,
            first_motor_event_s=float(ev_k[0]) if len(ev_k) else None,
            amplitude_V=float(tail.max() - tail.min()), X_min=float(tail.min()), X_max=float(tail.max()),
            frequency_Hz=float(Xspk[k] / (seconds - 10.0)),
            duty_readout=float((tail > V_TYP / 2).mean()), duty_motor_above0=float((m[1000:] > 0).mean()),
            B_start=float(b[0]), B_end=float(b[-1]), B_range=[float(b.min()), float(b.max())],
            motor_events_10_100=int(((ev_k >= 10.0) & (ev_k < seconds)).sum()),
            rearms_10_100=int(((rt[rm == k] >= 10.0)).sum()),
            unarmed_fraction=float((m[1000:] > -V_TYP).mean()))
    P_end = [float(e.V[ix["P0"]]), float(e.V[ix["P1"]])]
    out["P_end"], out["P_drift"] = P_end, float(max(abs(P_end[0] - P), abs(P_end[1] - P)))
    out["P_extremes"] = [float(min(e.vmin_o[ix["P0"]], e.vmin_o[ix["P1"]])), float(max(e.vmax_o[ix["P0"]], e.vmax_o[ix["P1"]]))]
    out["clip_steps"] = {e.c.names[i]: int(e.clip_o[i]) for i in range(len(e.V)) if e.clip_o[i]}
    out["power_W"] = e.power()
    return out


# ---------------------------------------------------------------------------------------------------------- B
def bench_B_case(seed, case, sides=None):
    """case: dict(kind, ch, sign, delay). Returns per-P changes."""
    e = eng(seed, sides=sides)
    ix = e.ix
    jit = float(np.random.default_rng([seed, 180, 3, zlib.crc32(json.dumps(case, sort_keys=True).encode())]).uniform(0, 0.009))
    t0 = 1.0 + jit
    a = amp(e)
    pulses = []
    kind = case["kind"]
    if kind in ("single", "noT"):
        pulses.append((t0, ix[f"S{case['ch']}"], a))
    elif kind == "bothS":
        pulses += [(t0, ix["S0"], a), (t0, ix["S1"], a)]
    elif kind == "train":
        pulses += [(t0 + 0.02 * i, ix[f"S{case['ch']}"], a) for i in range(10)]
    last = max(p[0] for p in pulses) if pulses else t0
    tT = last + case.get("delay", 0.005)
    if kind != "noT":
        pulses.append((tT, ix["T"], a * case["sign"]))
    run_until(e, t0 - TICK)                                    # up to just before the first input
    P_before = [float(e.V[ix["P0"]]), float(e.V[ix["P1"]])]
    e.reset_obs()
    run_until(e, tT + 1.0, pulses)
    P_after = [float(e.V[ix["P0"]]), float(e.V[ix["P1"]])]
    return dict(seed=seed, sides=list(e.sides), case=case, jitter_s=jit, P_before=P_before, P_after=P_after,
                dP=[P_after[k] - P_before[k] for k in (0, 1)],
                P_extremes=[float(min(e.vmin_o[ix["P0"]], e.vmin_o[ix["P1"]])), float(max(e.vmax_o[ix["P0"]], e.vmax_o[ix["P1"]]))],
                E_peak=[float(e.vmax_o[ix["E0"]]), float(e.vmax_o[ix["E1"]])], S_peak=[float(e.vmax_o[ix["S0"]]), float(e.vmax_o[ix["S1"]])],
                T_extreme=[float(e.vmin_o[ix["T"]]), float(e.vmax_o[ix["T"]])],
                clip_steps={e.c.names[i]: int(e.clip_o[i]) for i in range(len(e.V)) if e.clip_o[i]})


def cases_B():
    out = []
    for ch in (0, 1):
        for sign in (1, -1):
            for d in DELAYS:
                out.append(dict(kind="single", ch=ch, sign=sign, delay=d))
            out.append(dict(kind="train", ch=ch, sign=sign, delay=0.005))
        out.append(dict(kind="noT", ch=ch, sign=0))
    for sign in (1, -1):
        out.append(dict(kind="noS", ch=None, sign=sign, delay=0.005))
        out.append(dict(kind="bothS", ch=None, sign=sign, delay=0.005))
    return out


# ---------------------------------------------------------------------------------------------------------- C
def fork(e, snap, t_from, pulses, horizon):
    """Restore snap (at time t_from, a tick start), run with pulses until the last pulse + horizon. Events."""
    e.restore(snap)
    e.reset_obs()
    end = max([t_from] + [p[0] for p in pulses]) + horizon
    run_until(e, end, pulses)
    evt, evm = e.events()
    rt, rm = e.rearms()
    ix = e.ix
    return dict(evt=evt, evm=evm, rt=rt, rm=rm, Mmax=[float(e.vmax_o[ix["M0"]]), float(e.vmax_o[ix["M1"]])],
                Mmin=[float(e.vmin_o[ix["M0"]]), float(e.vmin_o[ix["M1"]])],
                clip=int(e.clip_o.sum()))


def count_in(r, motor, a, b):
    return int(((r["evt"] >= a - 1e-12) & (r["evt"] < b - 1e-12) & (r["evm"] == motor)).sum())


def response(pres, omit, t, motor):
    ex50 = count_in(pres, motor, t, t + 0.05) - count_in(omit, motor, t, t + 0.05)
    ex200 = count_in(pres, motor, t + 0.05, t + 0.25) - count_in(omit, motor, t + 0.05, t + 0.25)
    first = pres["evt"][(pres["evt"] >= t) & (pres["evm"] == motor)]
    lat = float(first[0] - t) if len(first) else None
    rearm = None
    if lat is not None:
        ra = pres["rt"][(pres["rt"] > first[0]) & (pres["rm"] == motor)]
        rearm = float(ra[0] - first[0]) if len(ra) else None
    return dict(excess_50ms=ex50, excess_next_200ms=ex200, first_latency_s=lat, rearm_latency_s=rearm,
                Mmax_present=pres["Mmax"][motor], Mmax_omitted=omit["Mmax"][motor])


def bench_C_seed(seed, Plevel, removed="none", sides=None):
    e = eng(seed, P0=(P_LEVELS[Plevel],) * 2, removed=removed, sides=sides)
    ix = e.ix
    a = amp(e)
    side = e.sides
    rows = []
    trials = []
    for ch in (0, 1):
        ts = np.random.default_rng([seed, 180, 4, ch]).uniform(10.0, 20.0, 16)
        trials += [(float(t), ch, i) for i, t in enumerate(ts)]
    trials.sort()
    snaps = {}
    for t, ch, i in trials:                                     # one shared no-input prefix, snapshots cached
        k = int(np.floor(t / TICK + 1e-9))
        if k not in snaps:
            run_until(e, k * TICK)
            snaps[k] = e.snapshot()
    for t, ch, i in trials:
        k = int(np.floor(t / TICK + 1e-9))
        t_from = k * TICK
        # analyst-observed phase at onset (end of the tick before: the snapshot's state)
        s = snaps[k]
        X = s["V"][ix[f"X{side[ch]}"]], s["V"][ix[f"X{1 - side[ch]}"]]
        Msnap = s["V"][ix[f"M{side[ch]}"]], s["V"][ix[f"M{1 - side[ch]}"]]
        arm = s["armed"][ix[f"M{side[ch]}"]], s["armed"][ix[f"M{1 - side[ch]}"]]
        horizon = 0.26
        omit = fork(e, s, t_from, [], t - t_from + horizon)
        pres = fork(e, s, t_from, [(t, ix[f"S{ch}"], a)], horizon)
        row = dict(seed=seed, P=Plevel, removed=removed, sides=list(side), ch=ch, trial=i, t=t,
                   phase=dict(side_readout_on=bool(X[0] > V_TYP / 2), other_readout_on=bool(X[1] > V_TYP / 2),
                              side_armed=bool(arm[0]), other_armed=bool(arm[1]), side_M=float(Msnap[0]),
                              other_M=float(Msnap[1])),
                   side=response(pres, omit, t, side[ch]), plastic=response(pres, omit, t, 1 - side[ch]),
                   clip=pres["clip"] + omit["clip"])
        pairs = {}
        for d in PAIR:                                         # second pulse from the common first-pulse history
            t2 = t + d
            k2 = int(np.floor(t2 / TICK + 1e-9))
            e.restore(s)
            run_until(e, k2 * TICK, [(t, ix[f"S{ch}"], a)] if k2 > k else [])
            s2 = e.snapshot()
            first = [(t, ix[f"S{ch}"], a)] if k2 == k else []
            o2 = fork(e, s2, k2 * TICK, first, t2 - k2 * TICK + horizon)
            p2 = fork(e, s2, k2 * TICK, first + [(t2, ix[f"S{ch}"], a)], horizon)
            pairs[str(d)] = dict(side=response(p2, o2, t2, side[ch]), plastic=response(p2, o2, t2, 1 - side[ch]),
                                 clip=p2["clip"] + o2["clip"])
        row["second"] = pairs
        rows.append(row)
    return rows


def mean_ci(x):
    from analyse import boot
    return boot(x)


def main(outdir, version=1):
    global SPEC
    outdir = Path(outdir)
    if version != 1:
        import importlib
        SPEC = importlib.import_module(f"design_v{version}").graph
    tag = "" if version == 1 else f"_v{version}"
    paths = {x: outdir / f"bench_{x}{tag}.json" for x in "ABC"}
    for p in paths.values():
        if p.exists():
            raise SystemExit(f"{p} exists: refusing to overwrite")
    t0 = time.time()
    # A
    A = [bench_A(s, P) for s in SEEDS for P in P_LEVELS.values()]
    A_rm = [bench_A(s, V_TYP / 2, removed="no_bias_writer") for s in SEEDS]
    A_fix = [bench_A(0, V_TYP / 2, sides=sd, seconds=20.0) for sd in ((0, 0), (0, 1), (1, 0), (1, 1))]
    gA = dict(P_drift_max=max(r["P_drift"] for r in A), P_drift_ok=all(r["P_drift"] <= 0.01 for r in A),
              no_clip=all(not r["clip_steps"] for r in A),
              motors_min_events=min(min(r["osc0"]["motor_events_10_100"], r["osc1"]["motor_events_10_100"])
                                    for r in A if r["P"] == V_TYP / 2),
              per_seed_motor_ok=all(min(r["osc0"]["motor_events_10_100"], r["osc1"]["motor_events_10_100"]) >= 10
                                    for r in A))
    gA["pass"] = bool(gA["P_drift_ok"] and gA["no_clip"] and gA["per_seed_motor_ok"])
    paths["A"].write_text(json.dumps(dict(gate=gA, runs=A, bias_writer_removed=A_rm, wiring_fixtures_seed0=A_fix,
                                          seconds=time.time() - t0), indent=1, default=float) + "\n")
    print("A", gA, f"{time.time() - t0:.0f} s", flush=True)
    # B
    t1 = time.time()
    Bres = [bench_B_case(s, c) for s in SEEDS for c in cases_B()]
    B_fix = [bench_B_case(0, c, sides=sd) for sd in ((0, 0), (0, 1), (1, 0), (1, 1))
             for c in cases_B() if c["kind"] == "single" and c["delay"] == 0.005]
    single = [r for r in Bres if r["case"]["kind"] == "single" and r["case"]["delay"] == 0.005]
    ok_dir = [r["case"]["sign"] * r["dP"][r["case"]["ch"]] for r in single]
    unexposed = [abs(r["dP"][1 - r["case"]["ch"]]) for r in single]
    ctrl = [max(abs(d) for d in r["dP"]) for r in Bres if r["case"]["kind"] in ("noS", "noT")]
    gB = dict(correct_change_min=min(ok_dir), correct_change_max=max(ok_dir),
              size_ok=all(0.001 <= x <= 0.15 for x in ok_dir), unexposed_max=max(unexposed),
              controls_max=max(ctrl), unexposed_ok=max(unexposed) <= 0.01, controls_ok=max(ctrl) <= 0.01,
              no_clip=all(not r["clip_steps"] for r in Bres), n_single=len(single))
    gB["pass"] = bool(gB["size_ok"] and gB["unexposed_ok"] and gB["controls_ok"] and gB["no_clip"])
    paths["B"].write_text(json.dumps(dict(gate=gB, runs=Bres, wiring_fixtures_seed0=B_fix,
                                          seconds=time.time() - t1), indent=1, default=float) + "\n")
    print("B", gB, f"{time.time() - t1:.0f} s", flush=True)
    # C
    t2 = time.time()
    Cres = [r for rm in ("none", "no_explore") for s in SEEDS for P in P_LEVELS for r in bench_C_seed(s, P, rm)]
    C_fix = [r for sd in ((0, 0), (0, 1), (1, 0), (1, 1)) for r in bench_C_seed(0, "typ", sides=sd)]
    full = [r for r in Cres if r["removed"] == "none"]

    def seed_mean(rows, f):
        d = {}
        for r in rows:
            d.setdefault(r["seed"], []).append(f(r))
        return [float(np.mean(v)) for _, v in sorted(d.items())]
    side_ex = seed_mean(full, lambda r: r["side"]["excess_50ms"])
    pl_typ = {(r["seed"], r["ch"], r["trial"]): r["plastic"]["excess_50ms"] for r in full if r["P"] == "typ"}
    pl_zero = {(r["seed"], r["ch"], r["trial"]): r["plastic"]["excess_50ms"] for r in full if r["P"] == "zero"}
    dif = {}
    for kk in pl_typ:
        dif.setdefault(kk[0], []).append(pl_typ[kk] - pl_zero[kk])
    pl_diff = [float(np.mean(v)) for _, v in sorted(dif.items())]
    summ = {}
    for rm in ("none", "no_explore"):
        for P in P_LEVELS:
            rr = [r for r in Cres if r["removed"] == rm and r["P"] == P]
            summ[f"{rm}|{P}"] = dict(
                side_excess_50ms=mean_ci(seed_mean(rr, lambda r: r["side"]["excess_50ms"])),
                plastic_excess_50ms=mean_ci(seed_mean(rr, lambda r: r["plastic"]["excess_50ms"])),
                side_excess_next200=mean_ci(seed_mean(rr, lambda r: r["side"]["excess_next_200ms"])),
                plastic_excess_next200=mean_ci(seed_mean(rr, lambda r: r["plastic"]["excess_next_200ms"])),
                side_first_latency_median=float(np.median([r["side"]["first_latency_s"] for r in rr
                                                           if r["side"]["first_latency_s"] is not None] or [np.nan])),
                side_no_event_after=int(sum(r["side"]["first_latency_s"] is None for r in rr)),
                side_rearm_latency_median=float(np.median([r["side"]["rearm_latency_s"] for r in rr
                                                           if r["side"]["rearm_latency_s"] is not None] or [np.nan])),
                n=len(rr), negative_side_excess=int(sum(r["side"]["excess_50ms"] < 0 for r in rr)),
                second={str(d): dict(side=mean_ci(seed_mean(rr, lambda r, d=d: r["second"][str(d)]["side"]["excess_50ms"])),
                                     plastic=mean_ci(seed_mean(rr, lambda r, d=d: r["second"][str(d)]["plastic"]["excess_50ms"])))
                        for d in PAIR},
                by_phase={ph: dict(n=int(sum(r["phase"]["side_readout_on"] == ph for r in rr)),
                                   side_excess=float(np.mean([r["side"]["excess_50ms"] for r in rr
                                                              if r["phase"]["side_readout_on"] == ph] or [np.nan])))
                          for ph in (False, True)},
                by_arming={ph: dict(n=int(sum(r["phase"]["side_armed"] == ph for r in rr)),
                                    side_excess=float(np.mean([r["side"]["excess_50ms"] for r in rr
                                                               if r["phase"]["side_armed"] == ph] or [np.nan])))
                           for ph in (False, True)})
    gC = dict(side_excess_50ms=mean_ci(side_ex), plastic_typ_minus_zero=mean_ci(pl_diff),
              no_clip=all(r["clip"] == 0 for r in full))
    gC["side_ok"] = gC["side_excess_50ms"][0] > 0.25
    gC["plastic_ok"] = gC["plastic_typ_minus_zero"][0] > 0.25
    gate = dict(A=gA["pass"], B=gB["pass"], C_side=gC["side_ok"], C_plastic=gC["plastic_ok"], C_no_clip=gC["no_clip"])
    gate["R3R4_pass"] = bool(all(gate.values()))
    paths["C"].write_text(json.dumps(dict(gate=gC, summary=summ, progression=gate, trials=Cres,
                                          wiring_fixtures_seed0=C_fix, seconds=time.time() - t2),
                                     indent=1, default=float) + "\n")
    print("C", gC, f"{time.time() - t2:.0f} s")
    print("PROGRESSION", gate)
    (outdir / f"bench_progression{tag}.json").write_text(json.dumps(gate, indent=1) + "\n")
    return gate


if __name__ == "__main__":
    v = int(sys.argv[sys.argv.index("--version") + 1]) if "--version" in sys.argv else 1
    main(sys.argv[1], v)

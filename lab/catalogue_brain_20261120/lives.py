"""D180 closed-loop lives: one job -> one compact ledger row (plus float32 P/E traces for the archive).

A job: dict(stage, version, arm, seed, poison, ratio, noise, removed, P (None | 'informed' | 'neutral' | 'reversed'),
learning). Informed/neutral/reversed P are written by this privileged harness after Life has drawn the wiring and
before the first step (CatalogueBrain.set_P asserts tick 0). The brain never reads colour or valence.
"""
from __future__ import annotations

import hashlib
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))

from units import V_TYP  # noqa: E402

TICKS = 10000


def birth_P(mode, life):
    if mode is None:
        return None
    if mode == "neutral":
        return (V_TYP / 2, V_TYP / 2)
    if life.poison is None:                                  # all food: "informed" means both P = V_TYP
        assert mode == "informed"
        return (V_TYP, V_TYP)
    food = "blue" if life.poison == "red" else "red"
    P = [0.0, 0.0]
    good, bad = (V_TYP, 0.0) if mode == "informed" else (0.0, V_TYP)
    P[life.sensor[food]], P[life.sensor[life.poison]] = good, bad
    return tuple(P)


def one(job):
    from creature import Life
    from brain import CatalogueBrain
    t0 = time.time()
    spec = None
    if job.get("version", 1) != 1:
        import importlib
        spec = importlib.import_module(f"design_v{job['version']}").graph
    life = Life(job["seed"], job["poison"], job["learning"],
                brain=lambda s: CatalogueBrain(s, removed=job["removed"], ratio=job["ratio"], noise=job["noise"],
                                               spec=spec))
    b = life.brain
    P = birth_P(job["P"], life)
    if P is not None:
        b.set_P(P)
    e = b.e
    nspk = np.zeros(len(e.V), np.int64)
    for _ in range(TICKS):
        life.step()
        nspk += e.spikes
    rows = np.array(b.rows, dtype=np.float32)               # E0 E1 P0 P1 B0 B1 X0 X1 M0 M1 per tick
    out = dict(job)
    food = None if life.poison is None else ("blue" if life.poison == "red" else "red")
    fk = None if food is None else life.sensor[food]
    out.update(meals=[(int(t), c) for t, c in life.meals], moving=life.moving, firings=len(life.firings),
               sensor_map=dict(life.sensor), motor_map=dict(life.motor), sides=list(e.sides),
               arrays_hash=e.arrays_hash(), wall_s=time.time() - t0,
               power_W=float(e.power()), motor_events=int(nspk[b.M].sum()),
               node_events={e.c.names[i]: int(nspk[i]) for i in range(len(nspk))},
               body_pulses=[sum(1 for _, s in b.pulses if s == k) for k in (0, 1)], tastes=len(b.tastes),
               clip_steps=int(e.clip_o.sum()), clip_by_node={e.c.names[i]: int(e.clip_o[i]) for i in range(len(nspk))
                                                             if e.clip_o[i]},
               preclip_extreme=float(e.preclip_o[np.argmax(np.abs(e.preclip_o))]),
               vmin={e.c.names[i]: float(e.vmin_o[i]) for i in range(len(nspk))},
               vmax={e.c.names[i]: float(e.vmax_o[i]) for i in range(len(nspk))},
               slew_max_Vps=float(e.slew_o.max()),
               P_birth=[float(x) for x in (P if P is not None else (V_TYP / 2, V_TYP / 2))],
               P_end=[float(rows[-1, 2]), float(rows[-1, 3])],
               gate_mean=[float(np.clip(rows[:, 2 + k] / V_TYP, 0, 1).mean()) for k in (0, 1)],
               elig_mean=[float(np.clip(rows[:, k] / V_TYP, 0, 1).mean()) for k in (0, 1)],
               food_sensor=fk)
    Pcap = [float(e.node[2, b.P[k]]) for k in (0, 1)]
    dP = np.diff(np.concatenate([[out["P_birth"]], rows[:, 2:4]]), axis=0)
    out["write_charge_C"] = [float(Pcap[k] * dP[:, k].sum()) for k in (0, 1)]
    out["write_charge_abs_C"] = float(sum(Pcap[k] * np.abs(dP[:, k]).sum() for k in (0, 1)))
    # E at each meal (end of the tick before), for evidence/credit accounting (observer labels only)
    # rows[t] is the state at the end of meal tick t, before its taste pulse (delivered within tick t+1); dP over
    # ticks t..t+3 brackets that taste's write (T decays in ~12 ms); overlapping meals are not separated.
    out["E_at_meal"] = [(int(t), c, float(rows[t, 0]), float(rows[t, 1]),
                         float(rows[min(t + 3, TICKS - 1), 2] - rows[t, 2]), float(rows[min(t + 3, TICKS - 1), 3] - rows[t, 3]))
                        for t, c in life.meals]
    if fk is not None:
        out["Pf"], out["Pp"] = rows[:, 2 + fk].copy(), rows[:, 3 - fk].copy()
    else:
        out["Pf"] = out["Pp"] = None
    from analyse import life_metrics
    out["m"] = life_metrics(out)
    out["trace"] = rows                                      # archived; dropped from the compact ledger
    return out


def key(job):
    return f"{job['stage']}|v{job.get('version', 1)}|{job['arm']}|{job['seed']}|{job['poison']}|r{job['ratio']}"


def compact(row):
    r = {k: v for k, v in row.items() if k not in ("trace", "Pf", "Pp")}
    r["Pf_hash"] = None if row.get("Pf") is None else hashlib.sha256(np.asarray(row["Pf"]).tobytes()).hexdigest()[:12]
    return r

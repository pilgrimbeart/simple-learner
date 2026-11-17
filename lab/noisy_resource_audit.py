"""D76: inspect actual constructor allocations, without stepping a robot life.

P is examined as implemented, not assumed to be total material. Production code is
not changed. Run once normally and once with --signed; each is an isolated process.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import pickle
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/"lab"), str(ROOT)]


def family(name):
    if name.startswith("lbld"):
        return "signed_integrator"
    if name.startswith("lb"):
        return "event_integrator"
    if name.startswith("rt"):
        return "rhythm_context"
    if name.startswith("clock"):
        return "clock_context"
    return "event_context"


def snapshot(brain):
    streams, fixed, quotas = Counter(), Counter(), Counter()
    detail = []
    for net in brain.nets:
        f = family(net.kind)
        symbols = sum(u["sym"] is not None for u in net.units.values())
        assert symbols == len(net.units), "constructor unexpectedly contains grown units"
        streams[f] += 1
        fixed[f] += symbols
        quotas[f] += net.P
        detail.append(dict(stream=net.kind, family=f, fixed_units=symbols, quota=net.P))
    return dict(streams=dict(streams), fixed_units=dict(fixed), quotas=dict(quotas),
                total_streams=len(brain.nets), total_fixed_units=sum(fixed.values()),
                total_quota=sum(quotas.values()),
                units_over_own_quota=sum(max(0, r["fixed_units"]-r["quota"]) for r in detail),
                immediate_unused_quota=sum(max(0, r["quota"]-r["fixed_units"]) for r in detail),
                fixed_plus_immediate_unused=sum(max(r["fixed_units"], r["quota"]) for r in detail),
                independent_clocks=len(brain.clk), per_stream=detail)


class ConstructorCaptured(Exception):
    pass


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--signed", action="store_true")
    a = ap.parse_args()
    for flag in ("GRADED", "DVOTE", "SURP", "LMIX", "LB_JOINT", "MUSCLE", "EXTRA", "SPLIT"):
        assert os.environ.get(flag) != "1", flag
    os.environ["LB_FINE"] = os.environ["LB_LIVE"] = "1"
    os.environ["LB_LETTER"] = "1" if a.signed else "0"
    start, cpu = time.monotonic(), time.process_time()
    import stage3_random as R
    R._init(.0025, False)
    import teach as T
    from stage2_lang import arms as S
    import grownet as G
    snapshots = []

    def capture(life, seconds):
        assert life.t == 0, "No life may run in this audit"
        raise ConstructorCaptured(snapshot(life.brain))

    S.live = capture
    for P in (560, 1120, 2240, 4480):
        try:
            T.job(("(world)", "net10kc60SFBLMR", P, 137000, "red", 1000.))
        except ConstructorCaptured as e:
            snapshots.append(dict(nominal_P=P, **e.args[0]))
        else:
            raise AssertionError("constructor observer not reached")
    # Independent closed-form count using the declared bank/clock alphabets.
    expected = 10*2 + 60*5 + 8*7*12 + 6*sum(5*m for m in range(2, 9)) + (7*15 if a.signed else 0)
    assert all(r["total_fixed_units"] == expected for r in snapshots)
    record = ROOT / ("lab/v/noisy_path_signed.pkl" if a.signed else "lab/v/noisy_path_scoring.pkl")
    data = pickle.loads(record.read_bytes())
    end = [dict(seed=r["seed"], first=r["first"], allocated=r["allocated"],
                outer_predictor_slots=len(r["names"])) for r in data["lives"]]
    assert all(r["outer_predictor_slots"] == snapshots[0]["total_streams"]+1 for r in end)
    result = dict(condition="signed" if a.signed else "frozen", constructor_world="(world)",
                  simulator_steps=0, dt_s=.0025, constructor_seed=137000, snapshots=snapshots,
                  integrator_design_slots=len(G.LB_LINES)*len(G.LB_T),
                  acquisition_complex_resonators=len(G.RT_GRID), eventual_trackers=G.RT_K,
                  existing_1000s_allocations=end, source_record_sha256=hashlib.sha256(record.read_bytes()).hexdigest(),
                  revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                  dirty=subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
                  hashes={p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
                          ("lab/noisy_resource_audit.py", "lab/grownet.py", "lab/teach.py", "lab/stage2_lang/seconds.py")},
                  wall_seconds=time.monotonic()-start, cpu_seconds=time.process_time()-cpu)
    out = ROOT / f"lab/v/noisy_resource_{result['condition']}.json"
    out.write_text(json.dumps(result, indent=2)+"\n")
    for row in snapshots:
        print({k: v for k, v in row.items() if k not in ("per_stream", "quotas")})
    print("existing end allocations", end)
    print("integrators", result["integrator_design_slots"], "acquisition resonators", len(G.RT_GRID),
          "eventual trackers", G.RT_K)
    print("PASS: no simulation steps; independent alphabet count and recorded outer selector count agree")
    print("wall_seconds", result["wall_seconds"], "cpu_seconds", result["cpu_seconds"])


if __name__ == "__main__":
    main()

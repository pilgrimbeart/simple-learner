"""D178: bench the adapter's sensor neurons outside the body, to fix observation windows in seconds from the circuit's
own response and recovery before any scoring (work order, stage 2). For each seed 0-31 and substrate: 2 s quiet (own
firing), then for each sensor 40 single body-size pulses (brains.circuit.CircuitBrain.stimulate) at random gaps of
0.3-0.6 s (latency of its first spike, response share), then paired pulses at gaps 5, 10, 20, 50, 100, 200 ms (10 each:
recovery, the second pulse's response share). Spike times at 1 ms. Also each motor's response to its sensor's spike.
python bench.py -> lab/v/robot_action_20261120/bench.json
"""
import json, os, sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
OUT = ROOT / "lab/v/robot_action_20261120"
RES = 0.001
GAPS = (0.005, 0.01, 0.02, 0.05, 0.1, 0.2)


def bench(job):
    seed, substrate, bias = job
    import brain as B
    b = B.make_brain(substrate, True, True, bias, log=False)(seed)
    c = b.circuit
    rng = np.random.default_rng([seed, 178])
    nodes = list(b.sensors) + list(b.motors)
    t = 0.0
    spikes = []                                    # (time, which 0..3)

    def run(sec, pulses=()):
        nonlocal t
        pulses = sorted(pulses)
        j = 0
        for _ in range(int(round(sec / RES))):
            while j < len(pulses) and pulses[j][0] < t + RES:
                b.stimulate(pulses[j][1], pulses[j][0] - t)
                j += 1
            s = c.run(RES)[nodes]
            for k in np.flatnonzero(s):
                spikes.append((t, int(k)))
            t += RES
    run(2.0)
    quiet = [sum(1 for _, k in spikes if k == q) / 2.0 for q in range(4)]
    singles = {0: [], 1: []}
    for k in (0, 1):
        for _ in range(40):
            at = t + 0.3 + 0.3 * rng.random()
            singles[k].append(at)
            run(at - t + 0.0)
            run(0.05, [(at, k)])
        run(0.3)
    paired = {}
    for k in (0, 1):
        for g in GAPS:
            for _ in range(10):
                at = t + 0.4 + 0.2 * rng.random()
                paired.setdefault((k, g), []).append(at)
                run(at - t)
                run(g + 0.05, [(at, k), (at + g, k)])
    sp = np.array(spikes) if spikes else np.zeros((0, 2))
    out = dict(seed=seed, substrate=substrate, quiet_rate=quiet, sensors=[])
    for k in (0, 1):
        own = sp[sp[:, 1] == k, 0] if len(sp) else np.zeros(0)
        lat = []
        for at in singles[k]:
            after = own[(own >= at) & (own < at + 0.05)]
            lat.append(float(after[0] - at) if len(after) else None)
        rec = {}
        for g in GAPS:
            hits = []
            for at in paired[(k, g)]:
                a2 = at + g
                first = own[(own >= at) & (own < a2)]
                second = own[(own >= a2) & (own < a2 + 0.02)]
                hits.append((len(first) > 0, len(second) > 0))
            rec[str(g)] = hits
        out["sensors"].append(dict(latency=lat, recovery=rec))
    return out


def main(substrates=("biology", "silicon")):
    import multiprocessing
    from concurrent.futures import ProcessPoolExecutor
    jobs = [(s, sub, None) for sub in substrates for s in range(32)]
    with ProcessPoolExecutor(7, mp_context=multiprocessing.get_context("spawn")) as pool:
        res = list(pool.map(bench, jobs))
    S = {}
    for sub in substrates:
        R = [r for r in res if r["substrate"] == sub]
        lat = [x for r in R for s in r["sensors"] for x in s["latency"] if x is not None]
        n = sum(len(s["latency"]) for r in R for s in r["sensors"])
        share = [np.mean([x is not None for x in s["latency"]]) for r in R for s in r["sensors"]]
        rec = {g: float(np.mean([h[1] for r in R for s in r["sensors"] for h in s["recovery"][str(g)] if h[0]]))
               for g in GAPS}
        S[sub] = dict(responses=len(lat), pulses=n, latency_ms_median=1000 * float(np.median(lat)) if lat else None,
                      latency_ms_p99=1000 * float(np.percentile(lat, 99)) if lat else None,
                      response_share_units_p10_p50_p90=[float(np.percentile(share, q)) for q in (10, 50, 90)],
                      quiet_rate_sensor_p10_p50_p90=[float(np.percentile([r["quiet_rate"][k] for r in R for k in (0, 1)], q)) for q in (10, 50, 90)],
                      quiet_rate_motor_p10_p50_p90=[float(np.percentile([r["quiet_rate"][k] for r in R for k in (2, 3)], q)) for q in (10, 50, 90)],
                      second_pulse_response_given_first=rec)
    json.dump(dict(summary=S, lives=res), open(OUT / "bench.json", "w"), indent=1)
    print(json.dumps(S, indent=1))


if __name__ == "__main__":
    for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[k] = "1"
    main()

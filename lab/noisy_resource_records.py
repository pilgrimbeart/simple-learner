"""D76: reconcile retained frozen performance with its original criterion; audit missing cost data.

Reads only the already-opened sequence, timing and combination comparison records.
No simulator runs, new fits, modified metric, or reconstructed physical costs.
"""
from pathlib import Path
import hashlib
import json
import pickle
import re
import time

import numpy as np

ROOT = Path(__file__).resolve().parent
ARM = "net10kc60SFBLMR"
PS = (560, 1120, 2240, 4480)


def main():
    start, cpu = time.monotonic(), time.process_time()
    k = np.random.default_rng(0).integers(0, 10, (2000, 10))
    indices = np.concatenate((2*k, 2*k+1), axis=1)
    results = {}
    for family, seconds in (("seq", 300.), ("time", 3000.), ("combo", 3000.)):
        paths = list((ROOT/"v").glob(f"grownet_pair*_{family}_*_s142000_*.pkl"))
        assert len(paths) == 1, paths
        path = paths[0]
        rows = pickle.loads(path.read_bytes())
        logs = (ROOT/f"v/frozen3_{family}.log").read_text()
        rungs = sorted({job[0] for job, _ in rows})
        analysed = []
        highest = {p: None for p in PS}
        for rung in rungs:
            eff = {}
            for arm, P in (("circuit", 0), ("vtold", 0), *((ARM, p) for p in PS)):
                subset = [(job, r) for job, r in rows if job[:3] == (rung, arm, P)]
                assert [(job[3], job[4]) for job, _ in subset] == [(s, c) for s in range(142000,142010) for c in ("red","blue")]
                data = np.array([r[:6] for _, r in subset])
                # Original metric: ratio of summed final-third gain to spending;
                # bootstrap seed PAIRS, then ratio of paired differences to told gap.
                eff[arm, P] = data[indices, 2].sum(1)/data[indices, 3].sum(1)
                assert all(len(r) == (8 if arm == ARM else 6) for _, r in subset)
            gap = eff["vtold", 0]-eff["circuit", 0]
            line = next(line for line in logs.splitlines() if re.search(rf"rung\s+{rung}:", line))
            for P in PS:
                x = (eff[ARM, P]-eff["circuit", 0])/gap
                lo, median, hi = np.quantile(x, [.025,.5,.975])
                display = f"{ARM}:{P} {median:+.2f} [{lo:+.2f},{hi:+.2f}]"
                assert display in line, display
                passed = bool(lo > .5)
                if passed:
                    highest[P] = rung
                analysed.append(dict(rung=rung, P=P, median=float(median), ci95=[float(lo),float(hi)],
                                     historical_pass=passed, nonpositive_gap_bootstraps=int((gap<=0).sum())))
        results[family] = dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            rows=len(rows), seconds_from_protocol=seconds, seeds=[142000,142009], pairs=10,
            highest_historical_pass=highest, comparisons=analysed,
            stored_cost_information="Spending proxy and execution time; best/max stream grown count and event counters in candidate diagnostic tuple",
            missing=["total final allocation", "peak allocation", "allocation time integral", "per-stream allocation history",
                     "fixed/reserved material accounting", "messages and wiring", "memory writes and decision latency",
                     "measured energy of the growing brain", "embedded original code hashes and environment flags"])
        print(family, "rows", len(rows), "highest historical passing rung", highest)
    print("PASS: every median and interval reproduces the kept printed logs at their original precision")
    print("Criterion preserved: lower paired-bootstrap 95% bound of final-third gap closure > .5")
    print("No total-allocation histories in these eight-field candidate records; growth/removal event counters do not count cascading removals")
    payload = dict(script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   bootstrap=dict(pairs=10, replicates=2000, seed=0), results=results,
                   wall_seconds=time.monotonic()-start, cpu_seconds=time.process_time()-cpu)
    (ROOT/"v/noisy_resource_records.json").write_text(json.dumps(payload, indent=2)+"\n")
    print("wall_seconds", payload["wall_seconds"], "cpu_seconds", payload["cpu_seconds"])


if __name__ == "__main__":
    main()

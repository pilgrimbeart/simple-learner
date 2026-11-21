"""D180 preflight: compile and time on two development seeds for 1 s of life at each circuit step (DT, DT/2, DT/4).
Reward is never read here (no meals are reported). Writes preflight.json (refuses to overwrite)."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))
OUT = HERE.parents[1] / "lab/v/catalogue_brain_20261120"


def main():
    from creature import Life
    from brain import factory
    p = OUT / "preflight.json"
    if p.exists():
        raise SystemExit(f"{p} exists: refusing to overwrite")
    Life(8, "red", True, factory()).step()                        # compile
    res = {}
    for ratio, noise in ((1, "native"), (1, "coupled"), (2, "coupled"), (4, "coupled")):
        times = []
        for seed in (8, 9):
            L = Life(seed, "red", True, factory(ratio=ratio, noise=noise))
            t = time.time()
            for _ in range(100):
                L.step()
            times.append(time.time() - t)
        res[f"r{ratio}_{noise}"] = dict(s_per_life_second=sum(times) / 2, est_s_per_100s_life=50 * sum(times))
    W = 7
    est = dict(
        action_384_lives_s=384 * res["r1_native"]["est_s_per_100s_life"] / W,
        learn_192_lives_s=192 * res["r1_native"]["est_s_per_100s_life"] / W,
        confirm_per_seed_s={r: 8 * res[f"r{r}_coupled"]["est_s_per_100s_life"] / W for r in (1, 2, 4)})
    est["confirm_plus_refine_N128_s"] = 128 * sum(est["confirm_per_seed_s"].values())
    est["confirm_plus_refine_N256_s"] = 256 * sum(est["confirm_per_seed_s"].values())
    out = dict(timing=res, estimates_7_workers=est, note="1 s lives x 2 development seeds; reward not read")
    p.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    main()

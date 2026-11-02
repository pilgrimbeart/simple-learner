"""Paired against HR_31p_pol on the league's held-out seeds, by the league's own measure (the worst substrate's,
resampled with the same seeds for every substrate): the difference in efficiency and gain with its 95% interval."""
import glob, json, os, sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from minimal.league import validated, SEEDS
from minimal.spec import boot_index, by_level, per_pair, worst_resampled, parts
S = os.path.dirname(os.path.abspath(__file__))
if __name__ == "__main__":
    ref = json.load(open("/home/pilgrim/git/simple-learner/minimal/results/HR_31p_pol.json"))["spec"]
    cands = {"HR_31p_pol_pruned": json.load(open("/home/pilgrim/git/simple-learner/minimal/results/HR_31p_pol_pruned.json"))["spec"]}
    for n in ("archive_31", "archive_33", "archive_34", "archive_36", "best_gain_34"):
        cands[n] = json.load(open(f"{S}/e30_{n}.json"))["spec"]
    for p in sorted(glob.glob(f"{S}/sym_*.json")):
        cands[os.path.basename(p)[:-5]] = json.load(open(p))["spec"]
    lv = lambda s: {k: per_pair(v) for k, v in by_level(validated(s)[0]).items()}
    R = lv(ref)
    idx = boot_index(len(SEEDS))
    r = worst_resampled(R, idx)
    for n, s in cands.items():
        L = lv(s)
        w = worst_resampled(L, idx)
        out = []
        for key in ("efficiency", "gain"):
            d = w[key] - r[key]
            lo, hi = np.percentile(d, (2.5, 97.5))
            out.append(f"{key} {np.mean(d):+.2f} [{lo:+.2f}, {hi:+.2f}]{' surely' if lo > 0 or hi < 0 else ' tied'}")
        print(f"{n:18s} {parts(s)['total']} parts: " + "; ".join(out), flush=True)

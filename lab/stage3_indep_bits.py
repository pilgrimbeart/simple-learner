"""stage3_indep_bits.py: the independent check of stage 3, the "in bits" figures. The rate KL (lab/stage2_label.py's rate_kl, whose
formula, Poisson KL l1 log2(l1/l0) - (l1 - l0)/ln 2 summed over four count features, was checked by hand) of each world's wires under
base against plain's, regrouped by the check's own final verdicts (lab/v/stage3_indep_check.log, [final]), and the same with the
producer's groups (D35) for comparison. Also what share of each world's KL comes from the tastes (food and poison counts) rather
than the eyes.

    .venv/bin/python lab/stage3_indep_bits.py > lab/v/stage3_indep_bits.log"""
import math
import pickle
import re
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import numpy as np

LOG = "/home/pilgrim/git/simple-learner/lab/v/stage3_indep_check.log"


def groups():
    txt = open(LOG).read().split("[final]")[1]
    g = {}
    for key, pat in (("sure pass", r"sure pass \d+ (\[.*?\])"), ("sure fail", r"sure fail \d+ (\[.*?\])"),
                     ("can't tell", r"can't tell \d+ (\[.*?\])")):
        g[key] = eval(re.search(pat, txt).group(1))
    return g


def main():
    import stage2_label as L
    import stage3_random as R
    W, redo, fresh = R.worlds()
    lab, main_ = R._load("label"), R._load("main")
    wires = pickle.load(open("/home/pilgrim/nca-scratch-backup/stage3/wires.pkl", "rb"))
    plain = [w[2] for w in wires["plain"]["circuit"] if w is not None]
    G = groups()
    redo_t, seen, judged = {W[n][0] for n in redo}, set(), []
    for n in fresh:
        t = W[n][0]
        if t in redo_t or t in seen:
            continue
        seen.add(t)
        if not R._out_of_results(lab[n]):
            judged.append(n)
    learn = set(sum(G.values(), []))
    G["nothing"] = [n for n in judged if n not in learn]

    def kl(n, cols=None):
        """Own implementation: Poisson KL in bits a life per feature (eyes sorted within a life; good and bad tastes), a feature
        counted only where the paired difference's bootstrap 95% interval excludes 0. cols='taste' returns the tastes' part."""
        r = np.array([w[2] for w in wires[n]["circuit"] if w is not None], float)
        p = np.array(plain, float)
        f = lambda x: np.column_stack((x[:, :2].max(1), x[:, :2].min(1), x[:, 2], x[:, 3]))
        a, b = f(r), f(p)
        npairs = len(a) // 2
        k = np.random.default_rng(99).integers(0, npairs, (2000, npairs))
        d = (a - b)[np.concatenate((2 * k, 2 * k + 1), 1)].mean(1)
        lo, hi = np.percentile(d, [2.5, 97.5], axis=0)
        tot = 0.0
        for j in (range(4) if cols is None else (2, 3)):
            l1, l0 = a[:, j].mean(), b[:, j].mean()
            if (lo[j] > 0 or hi[j] < 0) and l0 > 0 and l1 > 0:
                tot += l1 * math.log2(l1 / l0) - (l1 - l0) / math.log(2)
        return tot

    prod = [(n, L.rate_kl([w[2] for w in wires[n]["circuit"] if w is not None], plain)) for n in judged]
    print(f"own KL against the producer's rate_kl, largest absolute difference over judged worlds: "
          f"{max(abs(kl(n) - v) for n, v in prod):.2f} bits")
    none_ = [n for n in judged if n not in wires]
    print(f"judged fresh worlds without wires: {none_}; wires lives per world {set(len(wires[n]['circuit']) for n in judged if n in wires)}")
    for k, ns in G.items():
        v = np.array([kl(n) for n in ns if n in wires])
        vt = np.array([kl(n, "taste") for n in ns if n in wires])
        print(f"{k:10s} {len(ns):3d} worlds: rate KL bits a life median {np.median(v):6.1f} (10-90% {np.percentile(v, 10):.1f}-"
              f"{np.percentile(v, 90):.1f}); from the taste counts alone median {np.median(vt):6.1f}")
    print("each sure fail: total KL, taste-only KL")
    for n in G["sure fail"]:
        print(f"  {n:5s} {kl(n):7.1f} {kl(n, 'taste'):7.1f}   " + "; ".join(f"{a} {b} {c}" for a, b, c, _ in W[n][1]))


if __name__ == "__main__":
    main()

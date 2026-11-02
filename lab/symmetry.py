"""Is HR_31p_pol's S0/S1 asymmetry worth anything? (1) Its lives split by which sensor is food: each seed lives once
with food on S0 and once on S1 (the same wiring, red then blue as poison), so the difference is paired by seed.
(2) Symmetric variants scored on the same held-out seeds (100-163, all three substrates), paired against it."""
import copy, json, sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from minimal import spec as S

SEEDS = range(100, 164)
SRC = "/home/pilgrim/git/simple-learner/minimal/results/HR_31p_pol.json"


def side(s):
    """Indices: the sensors, the memory node, its two writes (gated by taste, from S0, S1), its two reads (gated by S0, S1)."""
    i0, i1 = s["sensors"]
    T = s["taste"]
    E = s["elements"]
    w = {e[1]: j for j, e in enumerate(E) if e[2] == T and e[1] in (i0, i1)}
    m = E[w[i0]][0]
    r = {e[2]: j for j, e in enumerate(E) if e[1] == m and e[2] in (i0, i1)}
    return i0, i1, (w[i0], w[i1]), (r[i0], r[i1])


def mirror_write(e):            # m -> -m: a write's sign flips; its input (a sensor) is unchanged
    e = copy.deepcopy(e)
    e[3] = -e[3]
    return e


def mirror_read(e):             # m -> -m: g tanh(s (m - o)) becomes g tanh(-s (m + o))
    e = copy.deepcopy(e)
    e[4], e[5] = -e[4], -e[5]
    return e


def variant(s, how):
    s = copy.deepcopy(s)
    i0, i1, (w0, w1), (r0, r1) = side(s)
    N, E = s["nodes"], s["elements"]
    def put(dst_node, src_node, dst_w, src_w, dst_r, src_r):
        N[dst_node][1:4] = copy.deepcopy(N[src_node][1:4])
        E[dst_w][3:] = mirror_write(E[src_w])[3:]
        E[dst_r][3:] = mirror_read(E[src_r])[3:]
    if how == "mirror":
        n0, n1, e = copy.deepcopy(N[i0]), copy.deepcopy(N[i1]), copy.deepcopy(E)
        N[i0][1:4], N[i1][1:4] = n1[1:4], n0[1:4]
        E[w0][3:], E[w1][3:] = mirror_write(e[w1])[3:], mirror_write(e[w0])[3:]
        E[r0][3:], E[r1][3:] = mirror_read(e[r1])[3:], mirror_read(e[r0])[3:]
    elif how == "both S0's":
        put(i1, i0, w1, w0, r1, r0)
    elif how == "both S1's":
        put(i0, i1, w0, w1, r0, r1)
    elif how == "average":
        # each sensor node: the geometric mean of R, C, the arithmetic mean of rest; each pair of elements: the
        # geometric mean of |gain| and |slope|, the arithmetic mean of |offset| on the mirrored side
        a, b = N[i0], N[i1]
        R, C, rest = np.sqrt(a[2] * b[2]), np.sqrt(a[3] * b[3]), (a[1] * a[2] + b[1] * b[2]) / 2
        for n in (a, b):
            n[1], n[2], n[3] = rest / R, R, C
        for j0, j1, mir in ((w0, w1, mirror_write), (r0, r1, mirror_read)):
            x, y = E[j0], mir(E[j1])                    # y: E[j1] as it would be on S0's side
            g = np.sign(x[3]) * np.sqrt(abs(x[3] * y[3]))
            o, sl = (x[4] + y[4]) / 2, np.sign(x[5]) * np.sqrt(abs(x[5] * y[5]))
            x[3], x[4], x[5] = g, o, sl
            E[j1][3:6] = mir([0, 0, 0, g, o, sl, x[6], x[7]])[3:6]
    return s


def pairs(lives, food0):
    """Per (substrate, seed): (the S0-food life, the S1-food life)."""
    out = []
    k = len(SEEDS) * 2
    for sb in range(len(S.JUDGED)):
        for i, seed in enumerate(SEEDS):
            red, blue = lives[sb * k + 2 * i], lives[sb * k + 2 * i + 1]
            # red poison: food is blue, on sensor_of[blue]
            out.append((red, blue) if food0[seed] else (blue, red))
    return out


def measures(l):
    sec = sum(t[2] for t in l)
    f, p = sum(t[0] for t in l), sum(t[1] for t in l)
    lf, lp = l[2][0], l[2][1]
    return {"food": S.SPAN * f / sec, "poison": S.SPAN * p / sec, "gain": S.SPAN * (f - S.COST * p) / sec,
            "stranded": float(lf == 0), "last food": lf, "last poison": lp}


def boot(d, n=4000, rng=np.random.default_rng(0)):
    d = np.asarray(d)
    m = rng.integers(0, len(d), (n, len(d)))
    b = d[m].mean(1)
    return d.mean(), np.percentile(b, 2.5), np.percentile(b, 97.5)


if __name__ == "__main__":
    from creature import Life, COLOURS
    base = json.load(open(SRC))["spec"]
    food0 = {}
    for seed in SEEDS:
        lf = Life(seed, "red", brain=lambda s: None)
        food0[seed] = lf.sensor["blue"] == 0            # in the red-poison life, is the food (blue) on sensor 0?
    names = ["original", "mirror", "both S0's", "both S1's", "average"]
    specs = [base] + [variant(base, h) for h in names[1:]]
    for n, s in zip(names, specs):
        v = S.violations(s)
        print(n, "illegal:" if v else "legal", v if v else "", flush=True)
    res = S.score(specs, seeds=SEEDS)
    print("\n(1) the original's lives split by which sensor is food (paired by seed and substrate; S0-food minus S1-food)")
    P = pairs(res[0], food0)
    for key in ("food", "poison", "gain", "stranded"):
        a = [measures(x)[key] for x, _ in P]
        b = [measures(y)[key] for _, y in P]
        m, lo, hi = boot(np.array(a) - np.array(b))
        print(f"  {key:9s} S0 food {np.mean(a):.3f}  S1 food {np.mean(b):.3f}  difference {m:+.3f} [{lo:+.3f}, {hi:+.3f}]")
    print("\n(2) the variants on the same seeds")
    base_net = None
    for n, s, lives in zip(names, specs, res):
        v = S.summary(lives)
        line = (f"  {n:10s} score {v['net']:+.2f} [{v['lo']:+.2f}, {v['hi']:+.2f}], eff {v['efficiency']:.2f}, gain"
                f" {v['gain']:.2f}, stranded {v['stranded']:.1%}, job {v['job']}")
        per = [measures(a)["gain"] + measures(b)["gain"] for a, b in pairs(lives, food0)]
        if base_net is None:
            base_net = per
        else:
            m, lo, hi = boot(np.array(per) / 2 - np.array(base_net) / 2)
            line += f"; gain vs original {m:+.2f} [{lo:+.2f}, {hi:+.2f}]"
        print(line, flush=True)
        if n != "original":
            json.dump({"design": f"HR_31p_pol {n}", "spec": s},
                      open(f"/home/pilgrim/git/simple-learner/lab/sym_{n.replace(' ', '_').replace(chr(39), '')}.json", "w"))

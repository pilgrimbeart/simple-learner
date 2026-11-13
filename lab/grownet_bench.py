"""grownet_bench.py: the growing network's nets on their own, fed a stream of tastes from a pattern lesson, no body (a bench for
debugging; never a result). Main session, 2026-11-12. The creature eats the colour the net predicts (a random one when it says nothing,
or with chance EPS); the pattern moves on at each good meal. Prints how often the prediction was right, by quarter of the stream.

    .venv/bin/python lab/grownet_bench.py [N] [STEPS] [kind: net|net2]"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import numpy as np
import grownet as GN

EPS = 0.1


def run(N=5, steps=2000, kind="net2", seed=1):
    rng = np.random.default_rng(seed)
    w = list(rng.integers(0, 2, N))
    w[0], w[1] = 0, 1
    nr = np.random.default_rng([seed, 77])
    if kind == "net2":
        net = GN.Net2("taste", 64, nr)
    else:
        net = GN.Net("good", 32, nr)
    idx, g, hits = 0, 0, []
    for i in range(steps):
        place = (g if kind == "net" else i) - 1
        k, f = net.says(place)
        guess = None if k is None else int(net.units[k]["n"][1] > net.units[k]["n"][0])
        eat = int(rng.integers(2)) if guess is None or rng.random() < EPS else guess
        letter = w[idx]
        good = eat == letter
        hits.append(guess == letter)
        net.learn(place, letter, float(i), k, f)
        if kind == "net2":
            net.write(i, (0 if good else 1, 2 + eat))
            net.tidy(i, float(i))
        else:
            net.write(g, letter)
            if good:
                net.tidy(g, float(i))
        if good:
            idx, g = (idx + 1) % N, g + 1
    q = np.array_split(np.array(hits), 4)
    return [round(x.mean(), 2) for x in q], sum(1 for x in net.units.values() if x["sym"] is None)


if __name__ == "__main__":
    a = sys.argv[1:]
    N, steps = int(a[0]) if a else 5, int(a[1]) if len(a) > 1 else 2000
    for kind in (a[2:] or ["net", "net2"]):
        print(kind, [run(N, steps, kind, s) for s in (1, 2, 3)])


def run_combo(k=5, steps=3000, P=128, seed=1, **kw):
    """The combination lesson on the bench: the food colour is a secret table of the last k colours eaten; the net reads the colour
    eaten at each taste (Net, two symbols), the creature eats what it says (a random colour when it says nothing, or with chance EPS)."""
    rng = np.random.default_rng(seed)
    m = 2 ** k
    f = list(rng.integers(0, 2, m))
    f[0], f[m // 2] = 0, 1
    net = GN.Net("eaten", P, np.random.default_rng([seed, 77]), **kw)
    h, hits = 0, []
    for i in range(steps):
        kk, fr = net.says(i - 1)
        guess = None if kk is None else int(net.units[kk]["n"][1] > net.units[kk]["n"][0])
        eat = int(rng.integers(2)) if guess is None or rng.random() < EPS else guess
        letter = f[h]
        hits.append(guess == letter)
        if kk is not None and guess == letter:
            net.credit(kk, float(i))
        net.learn(i - 1, letter, float(i), kk, fr)
        net.write(i, eat)
        net.tidy(i, float(i))
        h = (2 * h + eat) % m
    q = np.array_split(np.array(hits), 4)
    return [round(float(x.mean()), 2) for x in q], sum(1 for x in net.units.values() if x["sym"] is None), net.births, net.dups, net.fades

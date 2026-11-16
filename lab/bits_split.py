"""bits_split.py: where are the bits lost? (2026-11-15, D67.) For lives of a Bayes brain (arm letter B), at the end: the mixture's bits a
taste (its prequential code length), the default's, and each stream's bits saved over the default when it spoke, so the best stream in
hindsight is known (bits a taste over all tastes: default minus its saving).
    .venv/bin/python lab/bits_split.py LADDERJSON RUNG ARM SEED0 N"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor

sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import math
import stage3_random as R
import teach as T
from stage2_lang import arms as S


def live(lf, seconds=100.0):
    ticks = int(round(seconds / lf.dt))
    b = lf.brain
    dbits = [0.0]
    orig = b.taste

    while lf.t < ticks:
        lf.step()
    n = max(b.ntaste, 1)
    sv = sorted(((getattr(N, "saved", 0.0) / n, N.kind) for N in b.nets), reverse=True)[:4]
    h, m = b.dkt
    q = (h + .5) / (m + 1)
    dflt = -(q * math.log2(q) + (1 - q) * math.log2(1 - q))   # the default's rate at its final record, a rough bits a taste
    raise StopIteration((b.pbits / n, dflt, sv, n))


def one(j):
    S.live = live
    try:
        T.job(j)
    except StopIteration as e:
        return e.value


if __name__ == "__main__":
    lad, n, arm, s0, k = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
    if lad.endswith(".json"):
        d = json.load(open(lad))
        r = next(x for x in d["rungs"] if x["size"] == n)
        text, secs = r["text"], float(r["seconds"])
    else:                                               # a built-in ladder by name (seq, time, combo), its rung's own life
        import ladders as L
        text, secs = L.LADDERS[lad]["world"](n), float(dict(L.LADDERS[lad]["rungs"])[n])
    jobs = [(text, arm, 2240, s, "red", secs) for s in range(s0, s0 + k)]
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        for j, (mix, dflt, sv, nt) in zip(jobs, ex.map(one, jobs)):
            print(f"seed {j[3]}: tastes {nt}; mixture {mix:.3f} bits a taste; default about {dflt:.3f}; best streams' saving a taste "
                  f"over the default: {[(k_, round(v, 3)) for v, k_ in sv]}")

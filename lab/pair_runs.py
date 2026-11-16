"""pair_runs.py: pair two grownet_pair runs of the same arm on the same seeds (an environment switch differs between them), share of the
gap closed, by rung (2026-11-16).
    .venv/bin/python lab/pair_runs.py A.pkl B.pkl ARM P SECS_BY_RUNG(json)"""
import json
import pickle
import sys

import numpy as np

sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import ladders as L
import stage3_random as R

A, B = pickle.load(open(sys.argv[1], "rb")), pickle.load(open(sys.argv[2], "rb"))
arm, P, secs = sys.argv[3], int(sys.argv[4]), {int(k): float(v) for k, v in json.loads(sys.argv[5]).items()}
n = len({j[3] for j, _ in A})
I = R.boot(n)
for N in sorted(secs):
    fr = {}
    for rows, lab in ((A, "with"), (B, "without")):
        g = lambda a, p: L.scored([r for (nn, aa, pp, _, _), r in rows if nn == N and aa == a and pp == p], secs[N], I)
        b, t, x = g("circuit", 0), g("vtold", 0), g(arm, P)
        fr[lab] = ((x[0] - b[0]) / (t[0] - b[0]), (x[1] - b[1]) / (t[1] - b[1]))
    d = fr["with"][1] - fr["without"][1]
    print(f"  rung {N}: with {fr['with'][0]:+.2f}, without {fr['without'][0]:+.2f}; with - without {fr['with'][0] - fr['without'][0]:+.2f} "
          f"[{np.percentile(d, 2.5):+.2f}, {np.percentile(d, 97.5):+.2f}]")

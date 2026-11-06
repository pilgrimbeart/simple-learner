"""bits_record.py: stage 1b's recorded streams (lab/bits_bank.py), kept in ~/nca-scratch-backup/bits (too large for git): the bank in real lives; the bank's default pinned (fix=0), which is the
stream every selector sees up to its own first pick; and its parts told the colour rightly and wrongly, for each taste kind's rate under each.
    .venv/bin/python lab/bits_record.py LO:HI"""
import os
import pickle
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np
import bits_bank as B
from minimal.spec import efficiency

OUT = os.path.expanduser("~/nca-scratch-backup/bits/")


def keep(L):
    return [dict(rows=l.rows.astype(np.float32), picks=l.picks, on=l.on, seed=l.seed, first=l.first, names=l.names, lived=list(l)) for l in L]


if __name__ == "__main__":
    lo, hi = (int(x) for x in sys.argv[1].split(":"))
    for name, arm, kw, seeds in (("bank", "v_rec", {}, range(lo, hi)), ("pinned", "fix", {"fix": 0.0}, range(lo, hi)), ("right", "vtold", {}, range(lo, lo + 200)), ("wrong", "vtold", {"wrong": 1.0}, range(lo, lo + 200))):
        out = {}
        for w in B.WORLDS9:
            L = B.run(w, arm, seeds, kw)
            out[w] = keep(L)
            print(name, w, f"{efficiency(L):.3f}", flush=True)
        with open(OUT + f"{name}_{lo}.pkl", "wb") as f:
            pickle.dump(out, f)

"""universal_unseen.py: the bank in mismatches it was not built or tuned on: other swap periods, other sequences (lengths its tables do and don't fit), other digest
windows, other lie rates; and each rival removed, to show which does the work (discrete/NOTEBOOK.md, D29).
    python lab/universal_unseen.py SETTINGS.json"""
import json
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np
import table as T
import universal as X
import universal_v as UV
from table_rows import VALID
from minimal.spec import efficiency
import ladder as Lad


def seqworld(name, order):
    """Food in a fixed order of A and B (0, 1): a colour out of turn is bad and leaves the turn where it is."""
    class S(T.Pattern):
        def seq(self):
            a = T.COL[1 - T.COL.index(self.first)]
            return tuple(a if k == 0 else self.first for k in order)

        def poison(self, t):
            want = self.seq()[self.i]
            return T.COL[1 - T.COL.index(want)]

        def ate(self, colour):
            if colour == self.seq()[self.i]:
                self.i = (self.i + 1) % len(order)
    T.WORLDS[name] = S


for name, order in dict(seq4=(0, 0, 1, 1), seq5=(0, 0, 0, 1, 1), seq6=(0, 0, 1, 0, 1, 1), seq4b=(0, 0, 0, 1), seq2again=(0, 1)).items():
    seqworld(name, order)
for per in (5, 20, 50):
    T.WORLDS[f"swap{per}"] = type(f"S{per}", (T.Swap,), {"T": float(per)})
for W in (0.5, 2.0, 3.0):
    T.WORLDS[f"digest{W:g}"] = type(f"D{W:g}", (T.Digest,), {"W": W})
for E in (0.1, 0.3, 0.4):
    T.WORLDS[f"unreliable{E:g}"] = type(f"U{E:g}", (T.Unreliable,), {"E": E})
UNSEEN = ["swap5", "swap20", "swap50", "seq2again", "seq4", "seq4b", "seq5", "seq6", "digest0.5", "digest2", "digest3", "unreliable0.1", "unreliable0.3", "unreliable0.4"]
OFF = {"no trust-0": 15, "no 2": 16, "no 3": 17, "no 6": 18}
UV.BANKS.update({15: [(2, 2), (3, 2), (6, 2)], 16: [(1, 0), (3, 2), (6, 2)], 17: [(1, 0), (2, 2), (6, 2)], 18: [(1, 0), (2, 2), (3, 2)]})

if __name__ == "__main__":
    kw = json.load(open(sys.argv[1]))
    if sys.argv[2:] and sys.argv[2] == "var":        # var WORLDS,  k=v,k=v ...: variants on the validation seeds at 100 and 400 s
        for var in sys.argv[4:]:
            k = {**kw, **(X.parse(var.split(",")) if var != "-" else {})}
            print("==", var, flush=True)
            for secs in (100.0, 400.0):
                out = []
                for w in sys.argv[3].split(","):
                    B, V = T.run(w, "circuit", list(VALID), seconds=secs), T.run(w, "v", list(VALID), k, secs)
                    d, i = T.paired(V, B)
                    out.append(f"{w[:9]} {efficiency(V):.2f} {d:+.2f}[{i[0]:+.2f},{i[1]:+.2f}] g{np.mean([bool(l.grew) for l in V]):.2f} p{np.mean([bool(l.on) for l in V]):.2f}")
                print(f" {secs:.0f} | " + " | ".join(out), flush=True)
        sys.exit()
    seeds = list(VALID)
    for w in UNSEEN:
        for secs in (100.0, 400.0):
            B, V = T.run(w, "circuit", seeds, seconds=secs), T.run(w, "v", seeds, kw, secs)
            d, i = T.paired(V, B)
            print(f"{w} {secs:.0f} s: base {efficiency(B):.2f}, bank {efficiency(V):.2f}, {d:+.2f} [{i[0]:+.2f}, {i[1]:+.2f}]; grew {np.mean([bool(l.grew) for l in V]):.2f} paused {np.mean([bool(l.on) for l in V]):.2f}", flush=True)
    print("-- each rival removed", flush=True)
    for name, b in OFF.items():
        out = []
        for w in ("swap10", "alternate", "pattern", "digest", "unreliable", "plain"):
            V, F = T.run(w, "v", seeds, kw), T.run(w, "v", seeds, {**kw, "bk": float(b)})
            d, i = T.paired(F, V)
            out.append(f"{w[:5]} {d:+.2f} [{i[0]:+.2f}, {i[1]:+.2f}]")
        print(name, "| " + " | ".join(out), flush=True)

"""table_fix.py: the automatic versions, tuned on both counts (lab/table.py; STORIES.md): each setting scored on training seeds
as its world's efficiency, less 3 x any shortfall against the base brain in the plain world; the best 3 on more training seeds;
the best held out, in its world, in plain and with both colours food, against the base brain.
    python lab/table_fix.py WORLD[:ARM] ..."""
import itertools
import json
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import table as T
from table_rows import SWEEP, VALID
from minimal.spec import efficiency


def grid(**k):
    return [dict(zip(k, v)) for v in itertools.product(*k.values())]


SG = dict(SWEEP, cal_first=32.0, cal_fast=32.0, bank=192.0)
FIX = {
    "swap10": [("volatile2", grid(k=[2.0, 3.0, 5.0], need=[1.0, 2.0], tau=[20.0, 40.0]), (100.0,))],
    "alternate": [("grow", grid(theta=[2.0, 2.5, 3.0], tau=[5.0, 10.0, 20.0]), (100.0, 400.0))],
    "pattern": [("grow", grid(theta=[2.0, 2.5, 3.0], tau=[5.0, 10.0, 20.0]), (100.0, 400.0))],
    "digest": [("learnpause2", grid(theta=[3.0, 5.0], tau_p=[100.0, 400.0], win=[1.2, 1.5, 2.0], down=[1.0, 2.0]), (100.0, 400.0))],
    "noisy": [("adapteye", grid(tau_e=[0.03, 0.05, 0.08], margin=[2.0, 3.0, 5.0], tau_s=[5.0, 10.0]), (100.0,))],
    "unreliable": [("bt", grid(short=[2.0, 3.0], tau_b=[300.0, 1000.0], top=[4.0, 6.0], step_b=[1.0, 2.0]), (100.0, 400.0))],
    "patchy": [("bt", grid(short=[3.0], tau_b=[300.0, 1000.0], top=[3.0, 4.0], step_b=[1.0, 2.0]), (100.0,))],
    "thrusters": [("sweepsg", [dict(SG, gate=g) for g in (8.0, 12.0, 15.0)], (1000.0,))],
    "ageing": [("sweepsg", [dict(SG, gate=g, stall=0.0, forget=f) for g in (12.0, 15.0) for f in (0.7, 0.9)], (1000.0,)),
               ("jitterg", grid(learn=[1.0], eta=[0.06, 0.12], sd=[0.15, 0.3], gate=[12.0, 15.0, 18.0]), (1000.0,))],
}


def score(w, arm, kw, seeds, s, base):
    return efficiency(T.run(w, arm, seeds, kw, s)) + 3 * min(0.0, efficiency(T.run("plain", arm, seeds, kw, s)) - base)


def row(w, only=None):
    for arm, settings, lengths in FIX[w]:
        if only and arm != only:
            continue
        s0 = lengths[0]
        kw = settings[0]
        if len(settings) > 1:
            b1, b2 = (efficiency(T.run("plain", "circuit", x, seconds=s0)) for x in (T.TRAIN, VALID))
            res = sorted(((score(w, arm, k, T.TRAIN, s0, b1), i) for i, k in enumerate(settings)), reverse=True)[:3]
            res = sorted(((score(w, arm, settings[i], VALID, s0, b2), i) for _, i in res), reverse=True)
            kw = settings[res[0][1]]
        for s in lengths:
            shown = {k: round(v, 3) for k, v in kw.items() if k not in SWEEP or k in ("gate", "bank", "stall")}
            L = T.run(w, arm, T.HELD, kw, s)
            T.line(f"{w} | fix {arm} {json.dumps(shown)} | {s:.0f} s", L)
            T.against(L, T.run(w, "circuit", T.HELD, seconds=s))
            for other in ("plain", "allfood"):
                P = T.run(other, arm, T.HELD, kw, s)
                d, i = T.paired(P, T.run(other, "circuit", T.HELD, seconds=s))
                print(f"   {other}: {efficiency(P):.2f}, against the base brain {d:+.2f} [{i[0]:+.2f}, {i[1]:+.2f}]; grew {sum(bool(l.grew) for l in P)}, turned on {sum(bool(l.on) for l in P)}, of {len(P)}", flush=True)


if __name__ == "__main__":
    for a in sys.argv[1:] or FIX:
        w, _, arm = a.partition(":")
        row(w, arm or None)

"""table_more.py: the table's second round (lab/table.py; discrete/NOTEBOOK.md, D28): automatic versions after tracing, and the
rows' missing pieces.  python lab/table_more.py STEP ..."""
import json
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import numpy as np
import table as T
import table_fix as F
from table_fix import grid, SG
from table_rows import VALID, spd, imm, rnd, trial
from minimal.spec import efficiency


def digest():
    F.FIX["digest"] = [("learnpause2", grid(theta=[2.0, 3.0], tau_p=[400.0], win=[1.2], down=[1.0], margin=[1.2, 1.4], shrink=[0.99, 0.995, 1.0]), (100.0, 400.0))]
    F.row("digest")


def thrusters():
    F.FIX["thrusters"] = [("sweepsg", [dict(SG, cal_first=64.0, gate=g) for g in (8.0, 12.0)], (1000.0,)),
                          ("jitterg", grid(learn=[1.0], eta=[0.06], sd=[0.3], gate=[15.0], win=[100.0]), (1000.0,))]
    F.row("thrusters")


def ageing():
    F.FIX["ageing"] = [("jitterg", grid(learn=[1.0], eta=[0.03, 0.06], sd=[0.15], gate=[14.0, 16.0, 18.0], win=[100.0, 200.0]), (1000.0,)),
                       ("sweepsg", [dict(SG, cal_first=64.0, gate=12.0, stall=0.0, forget=0.9)], (1000.0,))]
    F.row("ageing")


def noisy():
    base = T.run("noisy", "circuit")
    trial("noisy", "Store", "integrate", grid(eye_told=[1.0], tau_e=[0.03, 0.05, 0.1], theta=[1.5, 2.0, 3.0]), base)
    trial("noisy", "Judge", "filter", grid(eye_told=[1.0], win=[0.005, 0.01, 0.02, 0.03]), base)
    F.FIX["noisy"] = [("adapteye", [dict(tau_e=0.05, margin=3.0, tau_s=s) for s in (5.0, 10.0, 20.0)], (100.0,))]
    F.row("noisy")


def seq():
    for w in ("alternate", "pattern"):
        for kw in (dict(theta=3.0, tau=10.0), dict(theta=2.0, tau=20.0), dict(theta=2.5, tau=20.0)):
            print(f"{w} grow {kw}, more training seeds: {efficiency(T.run(w, 'grow', VALID, kw)):.2f}; plain against base {T.paired(T.run('plain', 'grow', VALID, kw), T.run('plain', 'circuit', VALID))}", flush=True)


def weak():
    """Is the target too high? The colour told, the weak eye still weak, settings searched for each case apart."""
    for w in ("weak",):
        for arm in ("circuit", "toldc"):
            L = T.run(w, arm)
            for case in (True, False):
                print(f"{w} {arm}, the weak eye is {'food' if case else 'poison'}'s: {efficiency([l for l in L if l.weak_food == case]):.2f}", flush=True)
        best = {}
        for case in (True, False):
            res = []
            for kw in rnd(imm, 32):
                L = T.run(w, "toldc", T.TRAIN, kw)
                res.append((efficiency([l for l in L if l.weak_food == case]), json.dumps(kw)))
            res.sort(reverse=True)
            res = sorted(((efficiency([l for l in T.run(w, "toldc", VALID, json.loads(k)) if l.weak_food == case]), k) for _, k in res[:3]), reverse=True)
            best[case] = json.loads(res[0][1])
            H = [l for l in T.run(w, "toldc", T.HELD, best[case]) if l.weak_food == case]
            print(f"  told the colour, searched for this case ({'food' if case else 'poison'}): {res[0][1]}: {efficiency(H):.2f}", flush=True)
            best[str(case)] = H
        print(f"  a searched ceiling, both cases: {efficiency(best['True'] + best['False']):.2f}", flush=True)


def patchy():
    S = rnd(imm, 32)
    res = sorted(((efficiency(T.run("patchy", "toldc", T.TRAIN, k)), i) for i, k in enumerate(S)), reverse=True)[:3]
    res = sorted(((efficiency(T.run("patchy", "toldc", VALID, S[i])), i) for _, i in res), reverse=True)
    T.line(f"patchy told the colour, searched {json.dumps(S[res[0][1]])}", T.run("patchy", "toldc", T.HELD, S[res[0][1]]))
    S2 = [dict(k, trust=3.0) for k in S]
    res = sorted(((efficiency(T.run("patchy", "circuit", T.TRAIN, k)), i) for i, k in enumerate(S2)), reverse=True)[:3]
    res = sorted(((efficiency(T.run("patchy", "circuit", VALID, S2[i])), i) for _, i in res), reverse=True)
    T.line(f"patchy trust 3, searched {json.dumps(S2[res[0][1]])}", T.run("patchy", "circuit", T.HELD, S2[res[0][1]]))


def row1():
    base = T.run("plain", "unwired")
    T.line("row 1 base: taste wired to nothing", base)
    T.line("row 1 target: told", T.run("plain", "told"))
    for cls, arm, kw in (("Immunise", "still", {}), ("Store", "B", {}), ("Use", "path", dict(theta=1.5, reverse=1.0, trust=2.0)), ("Judge", "circuit", {})):
        L = T.run("plain", arm, T.HELD, kw)
        T.line(f"row 1 {cls}: {arm} {kw}", L)
        T.against(L, base, "against taste wired to nothing")
    S = rnd(spd, 12)
    res = sorted(((efficiency(T.run("plain", "unwired", T.TRAIN, k)), i) for i, k in enumerate(S)), reverse=True)
    L = T.run("plain", "unwired", T.HELD, S[res[0][1]])
    T.line(f"row 1 Spend: unwired, slower {json.dumps(S[res[0][1]])}", L)
    T.against(L, base, "against taste wired to nothing")


if __name__ == "__main__":
    for step in sys.argv[1:]:
        print(f"== {step}", flush=True)
        globals()[step]()

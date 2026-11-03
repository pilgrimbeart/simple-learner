"""table_final.py: the table's judge, on seeds no tuning or looking has touched (54000-54063 x 2): each row's base, target, best manual
cure and automatic version, in its world, then the automatic version in the plain world and with both colours food, at the same
length; ties paired (discrete/NOTEBOOK.md, D28; STORIES.md, The table). Then every automatic version in every world.
    python lab/table_final.py rows | cross"""
import json
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import numpy as np
import table as T
from table_fix import SG
from table_rows import SWEEP
from minimal.spec import efficiency

FRESH = range(54000, 54064)
with open("/home/pilgrim/git/simple-learner/lab/table_settings.json") as f:
    ROWS = json.load(f)        # world: {long, target, manual: [name, arm, kw], cheaper: [...], auto: [arm, kw], lengths: [...]}


def s(L):
    return f"{efficiency(L):.2f}"


def pair(A, B):
    d, i = T.paired(A, B)
    return f"{d:+.2f} [{i[0]:+.2f}, {i[1]:+.2f}]"


def rows():
    for w, r in ROWS.items():
        world = r.get("world", w)
        secs = T.LONG.get(world, 100.0)
        base_arm, base_kw = r.get("base", ["circuit", {}])
        base = T.run(world, base_arm, FRESH, base_kw, secs)
        print(f"== {w}: base {s(base)}", flush=True)
        tgt = None
        if r.get("target"):
            tgt = T.run(world, r["target"][0], FRESH, r["target"][1], secs)
            print(f"   target {s(tgt)}; gap {pair(tgt, base)}", flush=True)
        best = None
        for name, arm, kw in r.get("manual", []):
            L = T.run(world, arm, FRESH, kw, secs)
            best = best or L
            print(f"   manual {name}: {s(L)}; against base {pair(L, base)}" + (f"; against target {pair(L, tgt)}" if tgt else "") + (f"; against the first manual {pair(L, best)}" if L is not best else ""), flush=True)
            P = T.run("plain", arm, FRESH, kw, secs)
            print(f"      in plain, always on: {s(P)}; against base {pair(P, T.run('plain', base_arm, FRESH, base_kw, secs))}", flush=True)
        if r.get("auto"):
            arm, kw = r["auto"]
            for sec in r.get("lengths", [secs]):
                L = T.run(world, arm, FRESH, kw, sec)
                B = T.run(world, base_arm, FRESH, base_kw, sec)
                print(f"   auto {arm} {sec:.0f} s: {s(L)}; against base {pair(L, B)}", flush=True)
                if best and sec == secs:
                    print(f"      against the best manual {pair(L, best)}", flush=True)
                for other in ("plain", "allfood"):
                    P = T.run(other, arm, FRESH, kw, sec)
                    print(f"      {other}: {s(P)}; against base {pair(P, T.run(other, base_arm, FRESH, base_kw, sec))}; flips {np.mean([l.flips for l in P]):.1f}", flush=True)


def cross():
    """Every automatic version in every world, 100 s or the world's own length: efficiency, and the difference from the base brain."""
    worlds = ["plain", "allfood"] + [r.get("world", w) for w, r in ROWS.items() if r.get("auto") and r.get("world", w) not in ("plain",)]
    worlds = list(dict.fromkeys(worlds + ["pattern", "weak", "patchy"]))
    autos = {w: r["auto"] for w, r in ROWS.items() if r.get("auto") and r["auto"][0] != "circuit"}
    base = {w: T.run(w, "circuit", FRESH) for w in worlds}
    print("worlds: base " + " ".join(f"{w} {s(base[w])}" for w in worlds), flush=True)
    for name, (arm, kw) in autos.items():
        for w in worlds:
            L = T.run(w, arm, FRESH, kw)
            print(f"{name} ({arm}) in {w}: {s(L)}; against base {pair(L, base[w])}", flush=True)


if __name__ == "__main__":
    for step in sys.argv[1:]:
        globals()[step]()

"""size_count.py: how big is the growing brain at birth and at the end of a life? (2026-11-15.) Streams, units (sense units and grown
blocks), clocks and integrators, by kind of stream.
    .venv/bin/python lab/size_count.py"""
import json
import sys
from collections import Counter

sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import ladders as L
import stage3_random as R
R._init(0.0025, False)
import teach as T
from stage2_lang import arms as S

OUT = {}


def kind(k):
    return "bank" if k.startswith("lb") else "clock" if k.startswith("clock") else "sense"


def snap(b):
    grown, senses = Counter(), Counter()
    for N in b.nets:
        for x in N.units.values():
            (senses if x.get("sym") is not None else grown)[kind(N.kind)] += 1
    return dict(streams=Counter(kind(N.kind) for N in b.nets), senses=senses, grown=grown)


def live(lf, seconds=100.0):
    ticks = int(round(seconds / lf.dt))
    lf.step()
    OUT["birth"] = snap(lf.brain)
    while lf.t < ticks:
        lf.step()
    OUT["end"] = snap(lf.brain)
    OUT["clocks"] = len(getattr(lf.brain, "clk", []))
    OUT["integrators"] = len(getattr(lf.brain, "lbr", {}))
    raise StopIteration


S.live = live
for name, text, secs in (("sequences 11", L.LADDERS["seq"]["world"](11), 300.0),
                         ("satiety rung 3", next(r for r in json.load(open("lab/sealed/heldout_ladder2.json"))["rungs"] if r["size"] == 3)["text"], 600.0)):
    try:
        T.job((text, "net10kc60SFBL", 2240, 139000, "red", secs))
    except StopIteration:
        pass
    b, e = OUT["birth"], OUT["end"]
    print(f"== {name}, {secs:.0f} s life, material 2240")
    print(f"  streams {dict(b['streams'])}; clocks {OUT['clocks']}; leaky integrators {OUT['integrators']}")
    print(f"  birth: sense units {dict(b['senses'])}, grown blocks {sum(b['grown'].values())}")
    print(f"  end:   sense units {sum(e['senses'].values())}, grown blocks {dict(e['grown'])} (total {sum(e['grown'].values())})")

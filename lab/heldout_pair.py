"""heldout_pair.py: grownet_pair.py's paired comparison on a sealed ladder that has been opened (development only now; lab/sealed/).
Registers the ladder as "heldout", then runs grownet_pair. Main session, 2026-11-15.
    LADDER=lab/sealed/heldout_ladder2.json .venv/bin/python lab/heldout_pair.py PAIRS RUNGS ARM:P,ARM:P s137000"""
import json
import os
import runpy
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import ladders as L

d = json.load(open(os.environ["LADDER"]))
texts = {r["size"]: r["text"] for r in d["rungs"]}
L.LADDERS["heldout"] = dict(world=lambda n: texts[n], rungs=[(r["size"], r["seconds"]) for r in d["rungs"]])
tag = os.path.basename(os.environ["LADDER"]).split(".")[0]
L.LADDERS[tag] = L.LADDERS["heldout"]
sys.argv = ["grownet_pair.py", sys.argv[1], tag] + sys.argv[2:]
runpy.run_path("/home/pilgrim/git/simple-learner/lab/grownet_pair.py", run_name="__main__")

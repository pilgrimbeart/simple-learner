"""heldout_run.py: the held-out ladder (PROGRAMME.md, Sealed), opened 2026-11-13 after the design was frozen (PROGRAMME.md, Decisions).
Runs teach.py's ladder table on lab/sealed/heldout_ladder.json's rungs, on held-out seeds. Main session.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/heldout_run.py PAIRS ARMS Ps s70000"""
import json
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import ladders as L
import teach as T

if __name__ == "__main__":
    import ledger
    ledger.start()
    d = json.load(open("/home/pilgrim/git/simple-learner/lab/sealed/heldout_ladder.json"))
    texts = {r["size"]: r["text"] for r in d["rungs"]}
    L.LADDERS["heldout"] = dict(world=lambda n: texts[n], rungs=[(r["size"], r["seconds"]) for r in d["rungs"]])
    a = sys.argv[1:]
    T.run(int(a[0]), arms=tuple(a[1].split(",")), name="heldout", Ps=tuple(int(x) for x in a[2].split(",")),
          seed0=next((int(x[1:]) for x in a if x.startswith("s") and x[1:].isdigit()), 70000))

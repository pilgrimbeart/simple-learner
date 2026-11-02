import sys; sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
from discrete.policies import judge
from discrete.bodies import draw
seeds = range(6000, 6024)
tries = [("hold_drive", dict(scan=16, drive=160, hold=0.05)), ("hold_drive", dict(scan=32, drive=40, hold=0.1)),
         ("reflex_hold", dict(scan=32, k=8, hold=0.1)), ("straight", dict(rate=300))]
with ProcessPoolExecutor(3) as ex:
    for spread in (1.01, 1.03, 1.1):
        asym = lambda s, x=spread: {"asymmetry": draw(s, {"asymmetry": x})["asymmetry"]}
        for kind, p in tries:
            b = judge(kind, p, seeds, 100, ex, asym)
            print(f"motors within x{spread}: {kind:12s} {str(p):40s} {b['eff']:5.2f}/{b['gain']:5.1f}", flush=True)

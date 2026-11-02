import sys; sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
from discrete.policies import judge
from discrete.bodies import draw
seeds = range(6000, 6024)
asym = lambda s: {"asymmetry": draw(s, {"asymmetry": 1.25})["asymmetry"]}
tries = [("hold_drive", dict(scan=16, drive=160, hold=0.05)), ("hold_drive", dict(scan=16, drive=80, hold=0.1)),
         ("hold_drive", dict(scan=32, drive=40, hold=0.1)),
         ("reflex_hold", dict(scan=16, k=4, hold=0.05)), ("reflex_hold", dict(scan=32, k=8, hold=0.1)),
         ("reflex_hold", dict(scan=16, k=2, hold=0.1)),
         ("counter", dict(scan=64, k=1)), ("counter", dict(scan=96, k=2)),
         ("straight", dict(rate=120)), ("straight", dict(rate=300))]
with ProcessPoolExecutor(3) as ex:
    for kind, p in tries:
        a = judge(kind, p, seeds, 100, ex)
        b = judge(kind, p, seeds, 100, ex, asym)
        print(f"{kind:12s} {str(p):40s} standard {a['eff']:5.2f}/{a['gain']:5.1f}  unequal {b['eff']:5.2f}/{b['gain']:5.1f}  lost {100*(1-b['eff']/a['eff']):3.0f}%", flush=True)

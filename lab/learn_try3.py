import sys; sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
from discrete.policies import judge_poison
seeds = range(7100, 7124)
B = dict(learn="toggle", n=2, blame="held", bored=2.0, roam=1.0, roam_rate=80)
tries = [("reflex_hold", dict(B, scan=32, k=8, hold=0.1)),
         ("reflex_hold", dict(B, scan=32, k=8, hold=0.1, avoid=2)),
         ("reflex_hold", dict(B, scan=16, k=8, hold=0.1)),
         ("reflex_hold", dict(B, scan=32, k=4, hold=0.1)),
         ("reflex_hold", dict(B, scan=32, k=8, hold=0.2)),
         ("reflex_hold", dict(B, scan=32, k=8, hold=0.1, bored=1.0, roam=0.5)),
         ("reflex_hold", dict(B, scan=32, k=8, hold=0.1, bored=3.0, roam=1.0)),
         ("reflex_hold", dict(B, scan=32, k=8, hold=0.1, roam_rate=40)),
         ("reflex_hold", dict(B, scan=32, k=8, hold=0.1, n=3)),
         ("hold_drive", dict(B, scan=16, drive=160, hold=0.05)),
         ("hold_drive", dict(B, scan=16, drive=80, hold=0.1)),
         ("hold_drive", dict(B, scan=32, drive=40, hold=0.1))]
with ProcessPoolExecutor(3) as ex:
    for kind, p in tries:
        r = judge_poison(kind, p, seeds, 100, ex)
        d = {k: v for k, v in p.items() if k not in ("learn", "blame") }
        print(f"{kind:11s} {str(d):95s} eff {r['eff']:5.2f} gain {r['gain']:4.1f} food {r['food']:4.1f} poison {r['poison']:3.1f} last {r['last']:3.1f} str {r['stranded']:3.0%} {r['job']}", flush=True)

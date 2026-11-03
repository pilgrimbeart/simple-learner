"""table_paired.py: the paired comparisons behind the table's "tied" (lab/table.py; STORIES.md), held out."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import table as T
from table_rows import SWEEP

G = dict(theta=3.0, tau=10.0)
C = [("swap10", ("volatile", dict(tau=40.0)), ("circuit", dict(trust=0.0))),
     ("swap10", ("circuit", dict(trust=0.0)), ("told", {})),
     ("alternate", ("cycle", dict(cycle=2.0)), ("told", {})),
     ("alternate", ("alteye", {}), ("cycle", dict(cycle=2.0))),
     ("pattern", ("cycle", dict(cycle=3.0)), ("told", {})),
     ("digest", ("pause", dict(pause=1.0)), ("toldpause", {})),
     ("noisy", ("adapteye", dict(tau_e=0.05, margin=3.0, tau_s=10.0)), ("filter", dict(win=0.02, eye_told=1.0))),
     ("noisy", ("filter", dict(win=0.02, eye_told=1.0)), ("told", {})),
     ("unreliable", ("circuit", dict(trust=3.0)), ("circuit", dict(trust=4.0))),
     ("unreliable", ("circuit", dict(trust=3.0)), ("told", {})),
     ("patchy", ("circuit", dict(trust=3.0)), ("told", {})),
     ("thrusters", ("sweeps", dict(SWEEP, bank=192.0)), ("told", {})),
     ("ageing", ("jitter", dict(learn=1.0, eta=0.06, sd=0.15)), ("told", {})),
     ("ageing", ("jitter", dict(learn=1.0, eta=0.06, sd=0.15)), ("sweeps", dict(SWEEP, stall=0.0, forget=0.7)))]
for w, (a, ka), (b, kb) in C:
    d, i = T.paired(T.run(w, a, T.HELD, ka), T.run(w, b, T.HELD, kb))
    print(f"{w}: {a} {[round(v, 2) for k, v in ka.items() if k in ('trust', 'tau', 'cycle', 'pause', 'win', 'bank', 'eta', 'margin')]} against {b} {[round(v, 2) for k, v in kb.items() if k in ('trust', 'cycle', 'win', 'forget')]}: {d:+.2f} [{i[0]:+.2f}, {i[1]:+.2f}]", flush=True)

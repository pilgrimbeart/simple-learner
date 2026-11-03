"""table_rows.py: each row's class-by-class trial (lab/table.py; STORIES.md). One setting is one kw; a space, many: each
setting on the training seeds, the best 3 on more training seeds, the best of those held out. Printed as it goes:
    python lab/table_rows.py WORLD [CLASS ...]"""
import json
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np
import table as T
from minimal.spec import efficiency

VALID = range(53016, 53048)
TUNE_S = {"ageing": 100.0, "thrusters": 100.0}          # settings of a fixed brain are chosen on short lives


def rnd(f, n=16):
    r = np.random.default_rng(1)
    return [f(r) for _ in range(n)]


def imm(r):
    return T.SPACES["immunise"](r)


def spd(r):
    return T.SPACES["spend"](r)


COMMON = [("Immunise", "circuit", rnd(imm, 24)), ("Spend", "circuit", rnd(spd, 12)),
          ("Judge", "circuit", [dict(trust=x) for x in (0.0, 2.0, 3.0)] + [dict(use=1.0, window=w, trust=x) for w in (0.1, 0.3) for x in (0.0, 1.0)]),
          ("Sense", "probe", [dict(probe_T=a, probe_len=b) for a in (3.0, 8.0, 20.0) for b in (1.0, 3.0)]),
          ("Use", "path", [dict(theta=t, tau=u, trust=2.0) for t in (0.5, 1.5) for u in (2.0, 8.0, 30.0)])]
SWEEP = dict(cal_every=32.0, cal_len=8.0, stall=0.05, stall_need=3000.0, gate=8.0, gate_rate=1.0, cal_first=0.0, cal_fast=12.0, bank=32.0, local=1.0, binary=1.0, cap=3.0)
ROWS = {
    "thrusters": [("Use", "scanside", [dict(scan_told=1.0), dict(scan_told=1.0, scan_flip=1.0)]),
                  ("Use", "scanlearn", [dict(trial=20.0), dict(trial=60.0)]),
                  ("Judge", "jitter", [dict(learn=1.0, eta=0.03, sd=0.3, N=1000.0)]),
                  ("Sense", "sweeps", [SWEEP, dict(SWEEP, bank=192.0)])],
    "swap10": [("Judge", "volatile", [dict(tau=t) for t in (10.0, 20.0, 40.0)]),
               ("Store", "rhythm3", [dict(agree=1.35)])],
    "alternate": [("Store", "cycle", [dict(cycle=2.0)]), ("Use", "flip", [{}]), ("Use", "alteye", [{}])],
    "pattern": [("Store", "cycle", [dict(cycle=3.0)]), ("Store", "cycle", [dict(cycle=6.0)])],
    "digest": [("Use", "pause", [dict(pause=x) for x in (0.8, 1.0, 1.2, 1.5)]), ("Judge", "judgesoon", [dict(W=1.0)])],
    "patchy": [("Store", "local", [dict(local_t=a, local_k=b, far_k=c) for a in (1.0, 3.0) for b in (2.0, 5.0) for c in (1.0, 3.0)])],
    "scarce": [("Spend", "rest", [dict(rest_after=a, rest_len=b) for a in (1.0, 3.0, 8.0) for b in (1.0, 3.0, 8.0)])],
    "noisy": [("Judge", "filter", [dict(win=w, eye_told=e) for w in (0.02, 0.05, 0.1) for e in (0.0, 1.0)]),
              ("Use", "filter", [dict(win=0.0, eye_told=1.0)]),
              ("Store", "integrate", [dict(tau_e=a, theta=b) for a in (0.05, 0.1, 0.2) for b in (1.5, 2.0, 3.0)])],
    "weak": [("Sense", "eyeslow", [dict(slow_k=a, slow_b=b) for a in (0.35, 0.5, 0.7, 1.0) for b in (0.5, 0.7, 1.0)]), ("Use", "eyehold", [dict(eye_k=x) for x in (2.0, 3.0, 4.0, 6.0)]),
             ("Store", "integrate", [dict(tau_e=0.1, theta=1.5)])],
    "unreliable": [("Store", "circuit", [dict(trust=x) for x in (4.0, 6.0, 8.0)])],
    "moving": [],
    "ageing": [("Use", "scanlearn", [dict(trial=20.0, again=200.0)]),
               ("Judge", "jitter", [dict(learn=1.0, eta=0.03, sd=0.3)]),
               ("Sense", "sweeps", [dict(SWEEP, stall=0.0, forget=f) for f in (0.7, 0.9)] + [dict(SWEEP, bank=192.0, stall=0.0, forget=0.8)])],
}


def trial(w, cls, arm, settings, base):
    seconds = T.LONG.get(w, 100.0)
    if len(settings) > 1:
        short = TUNE_S.get(w) if arm == "circuit" else None
        res = sorted(((efficiency(T.run(w, arm, T.TRAIN, kw, short or seconds)), i) for i, kw in enumerate(settings)), reverse=True)[:3]
        res = sorted(((efficiency(T.run(w, arm, VALID, settings[i], short or seconds)), i) for _, i in res), reverse=True)
        kw = settings[res[0][1]]
    else:
        kw = settings[0]
    L = T.run(w, arm, T.HELD, kw, seconds)
    T.line(f"{w} | {cls} | {arm} {json.dumps({k: round(v, 3) for k, v in kw.items()})}", L)
    T.against(L, base)


if __name__ == "__main__":
    w = sys.argv[1]
    want = set(sys.argv[2:])
    base = T.run(w, "circuit")
    T.line(f"{w} | base", base)
    for cls, arm, settings in ROWS.get(w, []) + COMMON:
        if not want or cls in want:
            trial(w, cls, arm, settings, base)

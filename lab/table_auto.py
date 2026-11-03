"""table_auto.py: each row's automatic version (lab/table.py; STORIES.md): in its world against the base brain, and, the test
of "only when needed", in the plain world against the base brain, on the same seeds and length of life.
    python lab/table_auto.py [WORLD ...]"""
import json
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import table as T
from table_rows import SWEEP, VALID
from minimal.spec import efficiency

GROW = dict(theta=3.0, tau=10.0)
AUTO = {
    "unreliable": [("learntrust", [dict(short=a, tau_b=b, top=c) for a in (2.0, 3.0, 5.0) for b in (30.0, 100.0) for c in (3.0, 5.0)], (100.0, 400.0))],
    "swap10": [("volatile", [dict(tau=40.0)], (100.0,)), ("diagnose", [dict(GROW, short=2.0, tau_v=40.0)], (100.0,))],
    "alternate": [("grow", [GROW], (100.0, 400.0))],
    "pattern": [("grow", [GROW], (100.0, 400.0))],
    "digest": [("learnpause", [{}], (100.0, 400.0))],
    "noisy": [("filter", [dict(win=w, eye_told=0.0) for w in (0.01, 0.02, 0.05)], (100.0,)), ("adapteye", [dict(tau_e=a, margin=b, tau_s=c) for a in (0.02, 0.05, 0.1) for b in (1.5, 3.0) for c in (10.0, 30.0)], (100.0,))],
    "weak": [("autohold", [dict(top=a, pow=b, tau_s=c) for a in (3.0, 6.0) for b in (0.5, 1.0) for c in (10.0, 30.0)], (100.0,))],
    "thrusters": [("sweeps", [SWEEP], (1000.0,)), ("sweeps", [dict(SWEEP, bank=192.0)], (1000.0,)), ("jitter", [dict(learn=1.0, eta=0.03, sd=0.3, N=1000.0)], (1000.0,))],
    "ageing": [("jitter", [dict(learn=1.0, eta=e, sd=s) for e in (0.03, 0.06, 0.12) for s in (0.15, 0.3)], (1000.0,)), ("sweeps", [dict(SWEEP, stall=0.0, forget=0.7)], (1000.0,))],
}


def row(w):
    for arm, settings, lengths in AUTO[w]:
        if len(settings) > 1:
            s0 = lengths[0]
            res = sorted(((efficiency(T.run(w, arm, T.TRAIN, kw, s0)), i) for i, kw in enumerate(settings)), reverse=True)[:3]
            res = sorted(((efficiency(T.run(w, arm, VALID, settings[i], s0)), i) for _, i in res), reverse=True)
            kw = settings[res[0][1]]
        else:
            kw = settings[0]
        for s in lengths:
            tag = f"{w} | auto {arm} {json.dumps({k: round(v, 3) for k, v in kw.items()})} | {s:.0f} s"
            T.against(_show(tag, T.run(w, arm, T.HELD, kw, s)), T.run(w, "circuit", T.HELD, seconds=s))
            L = T.run("plain", arm, T.HELD, kw, s)
            T.against(_show(f"   in plain", L), T.run("plain", "circuit", T.HELD, seconds=s), "plain, against the base brain")
            print(f"      plain: flips {sum(l.flips for l in L) / len(L):.1f}; grew in {sum(bool(l.grew) for l in L)}; turned on in {sum(bool(l.on) for l in L)}; of {len(L)}", flush=True)


def _show(name, L):
    T.line(name, L)
    return L


if __name__ == "__main__":
    for w in sys.argv[1:] or AUTO:
        row(w)

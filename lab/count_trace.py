"""count_trace.py: does a counter on a told clock keep its place in the world's cycle? (2026-11-14, after T9.) One timing life with the
frozen design plus counters on clock 0, told the slot length; at each of clock 0's beats, the counter's value modulo n against the
world's poison colour then (the told rule). If the count kept its place, each count would see one colour (purity 1). Also: which
stream the weighted majority trusts most at the end.
    .venv/bin/python lab/count_trace.py RUNG SEED [SECS]"""
import os
import sys
from collections import Counter, defaultdict

sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
os.environ["TOLDT"] = "1"
os.environ["NCOUNT"] = "1"
import ladders as L
import stage3_random as R
R._init(0.0025, False)
import teach as T
from stage2_lang import arms as S

OUT = {}


def live(lf, seconds=100.0):
    ticks = int(round(seconds / lf.dt))
    b, n = lf.brain, OUT["n"]
    seen = defaultdict(Counter)
    lastb = None
    while lf.t < ticks:
        lf.step()
        c = b.clk[0] if getattr(b, "clk", None) else None
        if c is not None and c.get("beats") is not None and c["beats"] != lastb:
            lastb = c["beats"]
            if lf.t * lf.dt > seconds / 3:
                seen[c["beats"] % n][lf.told_now] += 1
    OUT["seen"] = seen
    OUT["w"] = sorted(((getattr(N, "w", 1.0), N.kind) for N in b.nets), reverse=True)[:6]
    OUT["T"], OUT["tau"] = b.clk[0]["T"], getattr(lf, "v_tau", None)
    return orig(lf, 1e-9)


orig = S.live
S.live = live

if __name__ == "__main__":
    n, seed = int(sys.argv[1]), int(sys.argv[2])
    secs = float(sys.argv[3]) if len(sys.argv) > 3 else 1500.0
    OUT["n"] = n
    T.job((L.LADDERS["time"]["world"](n), "net10kc60Sc", 2240, seed, "red", secs))
    print(f"rung {n}, seed {seed}, {secs:.0f} s: clock 0 period {OUT['T']:.3f} s, the world's slot {OUT['tau']}")
    tot = 0
    for k in sorted(OUT["seen"]):
        v = OUT["seen"][k]
        tot += max(v.values())
        print(f"  count {k}: poison colours seen at its beats {dict(v)}  purity {max(v.values()) / sum(v.values()):.2f}")
    print(f"  overall purity {tot / sum(sum(v.values()) for v in OUT['seen'].values()):.2f}")
    print("  most trusted streams:", [(k, f"{w:.2g}") for w, k in OUT["w"]])

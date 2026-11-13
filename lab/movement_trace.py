"""movement_trace.py: why is lab/movement.py's play slower than uptake's graded play (learn3bINGV) with the same single kicks? One life
of each, the same seed; every 25 s after the new parts wake: trials per motor and the evidence (standard errors against no kick) for
each motor's kick unit. Main session, 2026-11-13.

    LENGTHS=1 GRADED=1 UPTAKE_SECS=600 .venv/bin/python lab/movement_trace.py [SEED]"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import numpy as np
import uptake as U


def trace(arm, seed):
    from stage2_lang import arms as S
    from stage2_lang.sim import WLife
    from stage2_lang.seconds import seconds_cls
    import table as T
    import movement as M
    q = T.numbers(seed, {"sync": 1})
    cls = M.move_cls(seconds_cls(T.Circuit)) if arm == "moveG" else U.arcs_cls(seconds_cls(T.Circuit))
    lf = WLife(seed, "red", (lambda s: cls(s, q)), S.world_of(U.WORLD_TEXT), seconds=True)
    right = [(lf.wire_h[h], lf.wire_m[len(lf.wire_m) - 2 + (0 if h == 1 else 1)]) for h in (0, 1)]
    lf.brain.setup(arm, right)
    b, out, nxt = lf.brain, [], None
    while b.t < U.SECS:
        lf.step()
        if b.woke is not None:
            nxt = b.woke if nxt is None else nxt
            if b.t >= nxt:
                N = b.gnet
                vals = {x["sym"]: x.get("val") for x in N.units.values() if x["sym"] is not None}
                ctrl = vals.get(len(U.MOTORS))
                z = {m: round(N.welch(vals.get(i), ctrl), 1) for i, m in enumerate(U.MOTORS)}
                n = {m: (vals.get(i) or [0])[0] for i, m in enumerate(U.MOTORS)}
                n[None] = (ctrl or [0])[0]
                tr = len(b.trials) if arm == "moveG" else sum(len(v) for v in b.shift.values())
                done = (b.play_over if arm == "moveG" else b.cands is not None)
                out.append((round(b.t - b.woke), tr, n, z, done))
                nxt += 25.0
                if done:
                    break
    return out


if __name__ == "__main__":
    U._init()
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 110002
    for arm in ("learn3bINGV", "moveG"):
        print(f"== {arm}, seed {seed}: s after waking, trials (moveG: all, looks included), kicks valued per motor, standard errors")
        for row in trace(arm, seed):
            print("  ", row, flush=True)

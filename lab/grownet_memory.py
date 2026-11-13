"""grownet_memory.py: in the A-B-A world (lab/grownet_switch.py's aba), which blocks survive B? For each brain, the blocks alive at the end
of life by when they were born (in A's first spell, in B's, or after A's return), on the stream the gate chose. Main session, 2026-11-12.

    OPENBLAS_NUM_THREADS=1 .venv/bin/python lab/grownet_memory.py [SEEDS, e.g. 95000,95001]"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import numpy as np
import stage3_random as R


def life(arm, seed, first):
    from stage2_lang import arms as S
    from stage2_lang.sim import WLife
    from stage2_lang.seconds import seconds_cls
    import grownet as GN
    import grownet_switch as G
    import table as T
    kw = dict(prune=False, supply=3.0, local=True, trophic=True, senses=True) if arm == "net5Lu3" else {}
    P = 160 if arm == "net5Lu3" else 64
    cls = seconds_cls(GN.net_cls(**kw))
    q = T.numbers(seed, {"P": P})
    q["P"] = P
    lf = WLife(seed, first, (lambda s: cls(s, q)), S.world_of(G.aba(11)), seconds=True)
    S.live(lf, 1500.0)
    out = {}
    for N in lf.brain.nets:
        b = [x["born"] for x in N.units.values() if x["sym"] is None]
        out[N.kind] = (sum(t < 400 for t in b), sum(400 <= t < 1000 for t in b), sum(t >= 1000 for t in b))
    return (lf.brain.best.kind if lf.brain.best else "-"), out


if __name__ == "__main__":
    R._init(0.0025, False)
    seeds = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else [95000, 95001, 95002]
    for s in seeds:
        for arm in ("net", "net5Lu3"):
            best, out = life(arm, s, "red")
            print(f"  {s} {arm:7s} chosen {best:6s} | alive at the end, born (before 400 s, 400 to 1000 s, after): "
                  + "; ".join(f"{k} {v}" for k, v in out.items() if sum(v)), flush=True)

"""grownet_why.py: why does the supply version lose in an unchanging world (R9)? One life at a time, net against netE3, on the pattern of 11:
in the last third, how often the network spoke, how often it was right, the length of look-back of the blocks that spoke, births and
deaths. Main session, 2026-11-12.

    .venv/bin/python lab/grownet_why.py [SEEDS, e.g. 87000,87001]"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import numpy as np
import ladders as L
import stage3_random as R


def life(arm, seed, first):
    from stage2_lang import arms as S
    from stage2_lang.sim import WLife
    from stage2_lang.seconds import seconds_cls
    import grownet as GN
    import table as T
    cls = seconds_cls(GN.net_cls(prune=arm == "net", supply=3.0 if arm == "netE3" else 0.0, economy=arm == "neteco"))
    q = T.numbers(seed, {"P": 64})
    q["P"] = 64
    lf = WLife(seed, first, (lambda s: cls(s, q)), S.world_of(L.seq(11)), seconds=True)
    b = lf.brain
    log = []
    old = b.taste

    def taste(value, at):
        N = b.nets[0]
        k, _ = N.says(b.place(N) - 1) if b.t > 1000 else (None, None)
        if k is not None and b.vouched():
            log.append((N.units[k]["span"], b.best is N))
        old(value, at)
    b.taste = taste
    l = S.live(lf, 1500.0)
    N = b.nets[0]
    return dict(third=l[2][0] - l[2][1], agree=N.agree, dis=N.dis, spans=[s for s, _ in log], chosen=np.mean([c for _, c in log]) if log else 0,
                births=N.births, gone=N.fades + N.dups + N.starved, alive=sum(1 for x in N.units.values() if x["sym"] is None))


if __name__ == "__main__":
    R._init(0.0025, False)
    seeds = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else [87000, 87001, 87002]
    for s in seeds:
        for arm in ("net", "neteco"):
            r = life(arm, s, "red")
            sp = r["spans"]
            print(f"  {s} {arm:5s} last third good-bad {r['third']:+4.0f} | pattern stream right {r['agree']} wrong {r['dis']} | spoke {len(sp)}"
                  f" times late, look-back median {np.median(sp) if sp else 0:.0f}, chosen {r['chosen']:.0%} | born {r['births']} gone {r['gone']}"
                  f" alive {r['alive']}", flush=True)

"""hidden_trace.py: why does the growing brain close only a third of the gap on hidden contexts (D61), when its best stream predicts the
food colour 85% of the time? One life at a time on the spent held-out ladder (development seeds; no verdict): each tick, the colour the
world makes food and the colour the brain heads for; after each change of the food colour, how long until the brain follows; and how
often the brain's own stream would have been right against how often it actually heads for food. Main session, 2026-11-13.

    OPENBLAS_NUM_THREADS=1 .venv/bin/python lab/hidden_trace.py [RUNG] [SEEDS]"""
import json
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import numpy as np
import stage3_random as R


def life(rung, seed, first, P=2240, arm="net"):
    from stage2_lang import arms as S
    from stage2_lang.sim import WLife
    from stage2_lang.seconds import seconds_cls
    import grownet as GN
    import table as T
    d = json.load(open("/home/pilgrim/git/simple-learner/lab/sealed/heldout_ladder.json"))
    text = {r["size"]: r["text"] for r in d["rungs"]}[rung]
    cls = seconds_cls(GN.net_cls(senses=True, split=True, clocks=60, reset="change", fade=False, ondemand=True, strict=True)) if arm == "net" \
        else seconds_cls(T.Circuit)
    q = T.numbers(seed, {"P": P})
    q["P"] = P
    lf = WLife(seed, first, (lambda s: cls(s, q)), S.world_of(text), seconds=True)
    b = lf.brain
    rows, last_food, changes = [], None, []
    t0 = None
    while b.t < 1000.0:
        lf.step()
        if lf.poison not in (0, 1):
            continue
        food = 1 - lf.poison                            # the colour that is food now
        head = lf.wire_s.index(b.food)                  # the colour the brain heads for (its eye, back to a colour)
        if food != last_food:
            changes.append([b.t, None])
            last_food = food
        if changes and changes[-1][1] is None and head == food:
            changes[-1][1] = b.t - changes[-1][0]
        rows.append((b.t, food == head, getattr(b, "best", None) is not None))
    r = np.array([(t, ok, g) for t, ok, g in rows], float)
    third = r[r[:, 0] > 2000 / 3]
    lags = [c[1] for c in changes[1:] if c[1] is not None]
    never = sum(1 for c in changes[1:] if c[1] is None)
    dwell = np.diff([c[0] for c in changes]) if len(changes) > 1 else np.array([0.0])
    return dict(right_time=third[:, 1].mean(), gate_on=third[:, 2].mean(), changes=len(changes) - 1, lag=np.median(lags) if lags else np.nan,
                lag90=np.percentile(lags, 90) if lags else np.nan, never=never, dwell=np.median(dwell))


if __name__ == "__main__":
    R._init(0.0025, False)
    rung = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    seeds = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else [84001, 84002, 84003]
    print(f"== hidden contexts, rung {rung} (spent ladder, development seeds): in the last third, the share of time heading for the food "
          f"colour; how often a stream steers; after each change of the food colour, the brain's delay to follow (median, 90th)")
    for s in seeds:
      for arm in ("base", "net"):
        x = life(rung, s, "red", arm=arm)
        print(f"  {s} {arm:4s}: heading right {x['right_time']:.0%} of the time | a stream steering {x['gate_on']:.0%} | food colour changed "
              f"{x['changes']} times, median dwell {x['dwell']:.1f} s | delay to follow {x['lag']:.1f} s (90th {x['lag90']:.1f}), "
              f"never followed before the next change {x['never']}", flush=True)

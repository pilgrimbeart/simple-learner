"""clocks_probe.py: why the fixed clock bank (teach.py clocks, D39) fails rung 5 of the time ladder: single lives taken apart. Watching only.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/clocks_probe.py [RUNG] [P] [SEEDS]"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import numpy as np
import ladders as L
import stage3_random as R
import teach as TC


def life(rung, P, seed, first, cls_maker=None):
    from stage2_lang import arms as S
    from stage2_lang.sim import WLife
    from stage2_lang.seconds import seconds_cls
    import table as T
    secs = dict(L.LADDERS["time"]["rungs"])[rung]
    w = S.world_of(L.LADDERS["time"]["world"](rung))
    C = seconds_cls((cls_maker or TC.clocks_cls)())
    q = T.numbers(seed, {"P": P})
    q["P"] = P
    lf = WLife(seed, first, (lambda s: C(s, q)), w, seconds=True)
    log, picks = [], []

    def tell(W):
        b = W.brain
        b.predict()
        tp = W.told_now
        f = W.wire_s[1 - tp] if tp is not None and tp >= 0 else -1
        log.append((W.now, b.food, f))
    lf.tell = tell
    S.live(lf, float(secs))
    b = lf.brain
    a = np.array(log)
    late = a[a[:, 0] > 2 * secs / 3]
    tau = lf.v_tau
    # each clock register: how well its beats tracked the slots (beats counted against slots passed), and its record
    rows = []
    for R_ in b.regs[2:]:
        k = int(np.argmax([R_["agree"][j] - 4 * R_["dis"][j] for j in range(1, len(R_["agree"]))])) + 1
        rows.append((R_["T"], R_["n"], secs / tau, k, R_["agree"][k], R_["dis"][k], max(R_["E"][1:])))
    best = b.best and (b.best[0]["kind"], b.best[1])
    return dict(tau=tau, right=float((late[:, 1] == late[:, 2]).mean()), right_all=float((a[:, 1] == a[:, 2]).mean()), best=best, rows=rows, bar=b.bar)


if __name__ == "__main__":
    R._init(0.0025, False)
    a = sys.argv[1:]
    rung, P = int(a[0]) if a else 5, int(a[1]) if len(a) > 1 else 416
    for seed in ([int(x) for x in a[2].split(",")] if len(a) > 2 else (84000, 84001, 84002)):
        d = life(rung, P, seed, "red")
        print(f"seed {seed}: slot {d['tau']:.2f} s; follows the told colour {d['right']:.2f} of the last third ({d['right_all']:.2f} of the life); following {d['best']}; bar {d['bar']:.1f}")
        near = sorted(d["rows"], key=lambda r: abs(np.log(r[0] / d["tau"])))[:3]
        top = sorted(d["rows"], key=lambda r: -(r[4] - 4 * r[5]))[:3]
        for name, rs in (("nearest clocks", near), ("best records", top)):
            print("   " + name + ": " + "; ".join(f"T {r[0]:.2f} beats {r[1]} (slots {r[2]:.0f}) best k {r[3]} agree {r[4]} dis {r[5]} E {r[6]:.1f}" for r in rs))


def where_wrong(rung=5, P=416, seeds=(84000, 84001, 84002, 84003)):
    """Of the last third: how often each arm follows the told colour, and for the clocks whether its wrong moments sit near a change
    of the told colour (within 1.5 s after, within 1.5 s before) or deep in a slot."""
    from stage2_lang import arms as S
    secs = dict(L.LADDERS["time"]["rungs"])[rung]
    text = L.LADDERS["time"]["world"](rung)
    for seed in seeds:
        out = []
        for arm in ("circuit", "designed", "clocks"):
            log = []
            if arm == "clocks":
                from stage2_lang.sim import WLife
                from stage2_lang.seconds import seconds_cls
                import table as T
                C = seconds_cls(TC.clocks_cls())
                q = T.numbers(seed, {"P": P})
                q["P"] = P
                lf = WLife(seed, "red", (lambda s: C(s, q)), S.world_of(text), seconds=True)
                inner = lambda W: W.brain.predict()
            else:
                lf = L.make(S.world_of(text), arm, seed, "red", dict(lad="time", size=rung))
                inner = lf.tell or (lambda W: None)

            def tell(W, inner=inner, log=log):
                inner(W)
                tp = W.told_now
                log.append((W.now, W.brain.food, W.wire_s[1 - tp] if tp is not None and tp >= 0 else -1))
            lf.tell = tell
            l = S.live(lf, float(secs))
            a = np.array(log)
            ch = a[1:][a[1:, 2] != a[:-1, 2], 0]                    # moments the told colour changed
            late = a[a[:, 0] > 2 * secs / 3]
            wrong = late[late[:, 1] != late[:, 2]]
            since = np.array([w - ch[ch <= w].max() if (ch <= w).any() else 99 for w in wrong[:, 0]])
            until = np.array([ch[ch > w].min() - w if (ch > w).any() else 99 for w in wrong[:, 0]])
            n = max(len(late), 1)
            g = sum(x - 4 * y for x, y, _ in l)
            out.append(f"{arm} right {1 - len(wrong) / n:.2f} (wrong: {((since < 1.5)).sum() / n:.2f} just after a change, {((until < 1.5) & (since >= 1.5)).sum() / n:.2f} just before, "
                       f"{((since >= 1.5) & (until >= 1.5)).sum() / n:.2f} deep) food {sum(x for x, _, _ in l):.0f} poison {sum(y for _, y, _ in l):.0f}")
        print(f"seed {seed}, slot {lf.v_tau:.1f} s, changes {len(ch)}:\n   " + "\n   ".join(out), flush=True)


if __name__ == "__main__" and len(sys.argv) > 3 and sys.argv[3] == "where":
    where_wrong(int(sys.argv[1]), int(sys.argv[2]))

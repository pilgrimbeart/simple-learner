"""stage3_summary.py: stage 3's result, read honestly (main session, 2026-11-07), from lab/stage3_random.py's saved lives. What
lab/v/stage3_analyse.log's own summary didn't do:
  - distinct worlds: two draws with the same text are one world (the same lives, on the same seeds); a fresh draw identical to a redo
    draw isn't fresh. Counted by text.
  - verdicts with their uncertainty: x's 95% interval against the bar max(.5 r, .25): surely passes (the interval above), surely
    fails (below), or can't tell at 60 pairs. Coverage is then a range: sure passes / N up to (sure + can't tell) / N.
  - harm surely shown (the interval of bank - base wholly below -.1), not merely not ruled out.
  - by construct: which kinds of world the bank surely fails, and which it covers.
  - in bits: the evidence on the wires against plain (lab/stage2_label.py's rate_kl: Poisson KL of the eyes' and tastes' rates,
    bits a life), under the base circuit's policy, and how soon the wires first differ.

    .venv/bin/python lab/stage3_summary.py > lab/v/stage3_summary.log"""
import sys
from collections import Counter, defaultdict
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import numpy as np
import stage3_random as R


def main():
    import stage2_label as L
    W, redo, fresh = R.worlds()
    rows = R._load("rows")
    wires = R._load("wires")
    plain_rates = {a: [w[2] for w in wires["plain"][a] if w is not None] for a in wires["plain"]}
    seen_text = {}
    for n in redo + fresh:
        seen_text.setdefault(W[n][0], n)

    def bits(n):
        if n not in wires:
            return np.nan, np.nan
        r = [w[2] for w in wires[n]["circuit"] if w is not None]
        fd = [L.first_diff(a, b) for a, b in zip(wires[n]["circuit"], wires["plain"]["circuit"]) if a is not None and b is not None]
        fd = [x * 0.01 for x in fd if x is not None]
        return L.rate_kl(r, plain_rates["circuit"]), (np.median(fd) if fd else np.inf)

    for label, names in (("redo: stage 2b's 100 draws, in seconds", redo), ("fresh: stage 3's 200 new draws", fresh)):
        prior = set() if label.startswith("redo") else {W[n][0] for n in redo}
        distinct, dup_within, dup_prior = [], 0, 0
        texts = set()
        for n in names:
            t = W[n][0]
            if t in prior:
                dup_prior += 1
                continue
            if t in texts:
                dup_within += 1
                continue
            texts.add(t)
            distinct.append(n)
        live = [n for n in distinct if n in rows and not rows[n]["out"]]
        out = [n for n in distinct if n in rows and rows[n]["out"]]
        gap = [n for n in live if not rows[n]["nothing"]]
        nothing = [n for n in live if rows[n]["nothing"]]
        sure_pass, sure_fail, unclear = [], [], []
        for n in gap:
            v = rows[n]
            bar = max(0.5 * v["r"] if np.isfinite(v["r"]) else 0.0, 0.25)
            lo, hi = v["x_ci"]
            (sure_pass if lo > bar else sure_fail if hi < bar else unclear).append(n)
        harm_sure = [n for n in nothing if rows[n]["harm"][1][1] < -0.1]
        harm_any = [n for n in nothing if rows[n]["harm"][1][1] < 0]
        help_sure = [n for n in nothing if rows[n]["harm"][1][0] > 0]
        N = len(gap)
        print(f"\n== {label}")
        print(f"  {len(names)} draws: {dup_within} repeat a draw in this set, {dup_prior} repeat a redo draw; {len(distinct)} distinct; "
              f"{len(out)} out (stage 5's kinds); {len(live)} judged")
        print(f"  something to learn (a gap): {N} of {len(live)} = {N / max(1, len(live)):.2f} [{R.wilson(N, len(live))[0]:.2f},{R.wilson(N, len(live))[1]:.2f}]")
        if N:
            print(f"  of those, the bank surely passes {len(sure_pass)}, surely fails {len(sure_fail)}, can't tell at 60 pairs {len(unclear)}")
            lo_c, hi_c = R.wilson(len(sure_pass), N)[0], R.wilson(len(sure_pass) + len(unclear), N)[1]
            print(f"  coverage: between {len(sure_pass) / N:.2f} and {(len(sure_pass) + len(unclear)) / N:.2f} of worlds with a gap "
                  f"(95% from {lo_c:.2f} to {hi_c:.2f})")
            print(f"  surely passes: {sure_pass}")
            print(f"  surely fails:  {sure_fail}")
            print(f"  can't tell:    {unclear}")
            rc = [n for n in gap if np.isfinite(rows[n]["r_ci"][0]) and rows[n]["r_ci"][0] > 0.25]
            print(f"  the reference surely closes over .25 in {len(rc)} of {N}; where it does, the bank surely passes in "
                  f"{sum(n in sure_pass for n in rc)}")
        print(f"  nothing to learn: {len(nothing)}; the bank surely below base there {len(harm_any)}, by more than .1 {len(harm_sure)} "
              f"{harm_sure}; surely above base {len(help_sure)}")
        # by construct
        tally = defaultdict(Counter)
        for grp, ns in (("pass", sure_pass), ("fail", sure_fail), ("unclear", unclear), ("nothing", nothing)):
            for n in ns:
                for link, name, course, _ in W[n][1]:
                    tally[f"{link} {name}"][grp] += 1
        print("  by construct (a world counted once for each of its statements): sure pass / sure fail / can't tell / nothing to learn")
        for k in sorted(tally, key=lambda k: (-tally[k]["fail"], -sum(tally[k].values()))):
            c = tally[k]
            print(f"    {k:18s} {c['pass']:3d} {c['fail']:3d} {c['unclear']:3d} {c['nothing']:3d}")
        # in bits
        print("  in bits (base's wires against plain's, 20 pairs at 10 ms): evidence a life (rate KL), and median first difference (s)")
        for grp, ns in (("sure pass", sure_pass), ("sure fail", sure_fail), ("can't tell", unclear), ("nothing", nothing)):
            b = [bits(n) for n in ns]
            kl = [x for x, _ in b if np.isfinite(x)]
            fd = [y for _, y in b if np.isfinite(y)]
            if kl:
                print(f"    {grp:10s} {len(ns):3d} worlds: bits a life median {np.median(kl):6.1f} (10-90% {np.percentile(kl, 10):.1f}-"
                      f"{np.percentile(kl, 90):.1f}); first difference median {np.median(fd) if fd else float('nan'):.1f} s")
        if label.startswith("fresh"):
            print("  each surely failed world:")
            for n in sure_fail:
                v = rows[n]
                kl, fd = bits(n)
                print(f"    {n:5s} gap {v['gap']:+.2f}  x {v['x']:+.2f} [{v['x_ci'][0]:+.2f},{v['x_ci'][1]:+.2f}]  r {v['r']:+.2f}  bits a life "
                      f"{kl:5.1f}  base {v['J']['base']:+.2f} bank {v['J']['bank']:+.2f} told {v['J']['told']:+.2f}   "
                      + "; ".join(f"{a} {b} {c}" for a, b, c, _ in W[n][1]))


if __name__ == "__main__":
    main()

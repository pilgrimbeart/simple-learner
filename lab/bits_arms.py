"""bits_arms.py: question 4 of stage 1b: real lives with the bank's evidence counters replaced, against the bank, the told arms and the row's manual cure (lab/table_settings.json).
Settings chosen on 61000-61063 x 2; judged on 60000-60199 x 2. "Surely": the interval of the paired difference excludes 0.

    .venv/bin/python lab/bits_arms.py"""
import json
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np
import bits_bank as B
import table as T
import universal as X
import universal_v as UV
from minimal.spec import efficiency

ROWS = json.load(open("/home/pilgrim/git/simple-learner/lab/table_settings.json"))
ROW = dict(plain="1 colour", swap10="3 swap10", alternate="4a alternate", pattern="4b pattern", digest="5 digest", unreliable="7 unreliable", patchy="10 patchy", weak="9 weak", noisy="6 noisy")
TUNE, JUDGE = range(61000, 61064), range(60000, 60200)
RIGHT = dict(plain={0}, swap10={1}, alternate={2, 4, 6}, pattern={3, 6}, digest={0}, unreliable={0}, patchy={0}, weak={0}, noisy={0})

GRID = [("map", dict(k=k)) for k in (0.5, 1.5, 2.5, 3.5, 4.5, 6.5)]
GRID += [("bma", dict(eps=e, pr=p)) for e in (0.05, 0.1, 0.2) for p in (1 / 7, 0.5, 0.9, 0.99)]
PARTS = [("ctr", dict(pen=3.0, floor=None)), ("ctr", dict(pen=1.0, floor=0.0)), ("ctr", dict(pen=1.0, floor=None)), ("ctr", dict(pen=1.0, floor=0.0, theta=3.0)), ("ctr", dict(pen=2.0, floor=0.0))]


def recovery(results, base):
    """The search's own score (universal_v.score): each world's recovery toward its best manual, clipped; the worst; plain's loss."""
    r = []
    for w in UV.WORLDS:
        if w in results and w != "plain":
            r.append(np.clip((efficiency(results[w]) - efficiency(base[w])) / max(X.BEST[w] - X.JUDGED[w], 0.2), -1, 1.2))
    d = efficiency(results["plain"]) - efficiency(base["plain"])
    return float(np.mean(r) + 0.5 * min(r) + 3 * min(0.0, d))


def name(a, kw):
    return a + "(" + ",".join(f"{k}={v:.3g}" if isinstance(v, float) else f"{k}={v}" for k, v in kw.items()) + ")"


def fp(L, right):
    first = [next((t for t, m in l.picks if m), None) for l in L]
    good = [next((t for t, m in l.picks if m in right and m), None) for l in L]
    a = np.mean([x is not None for x in first])
    g = [x for x in good if x is not None]
    return a, np.mean([x is not None for x in good]), (np.median(g) if g else -1)


def pr(tag, w, A, ref):
    d, i = T.paired(A, ref, boot=1000)
    return f"{tag} {efficiency(A):.3f} ({d:+.3f} [{i[0]:+.3f},{i[1]:+.3f}]{' SURE' if i[0] > 0 or i[1] < 0 else ''})"


if __name__ == "__main__":
    W = B.WORLDS9
    print("== tuning seeds: each setting's efficiency per world", flush=True)
    base = {w: B.run_plain(w, "circuit", TUNE) for w in W}
    bank = {w: B.run(w, "v_rec", TUNE) for w in W}
    print("base " + " ".join(f"{w[:5]} {efficiency(base[w]):.2f}" for w in W), flush=True)
    print("bank " + " ".join(f"{w[:5]} {efficiency(bank[w]):.2f}" for w in W) + f" score {recovery(bank, base):.3f}", flush=True)
    res = {}
    for a, kw in GRID + PARTS:
        res[(a, json.dumps(kw))] = {w: B.run(w, a, TUNE, kw) for w in W}
        print(name(a, kw) + " " + " ".join(f"{w[:5]} {efficiency(res[(a, json.dumps(kw))][w]):.2f}" for w in W) + f" score {recovery(res[(a, json.dumps(kw))], base):.3f}", flush=True)
    bayes = {k: v for k, v in res.items() if k[0] in ("map", "bma")}
    one = max(bayes, key=lambda k: recovery(bayes[k], base))
    best = {w: max(bayes, key=lambda k: efficiency(bayes[k][w])) for w in W}
    fixes = {w: {m: B.run(w, "fix", TUNE, dict(fix=float(m))) for m in range(7)} for w in W}
    for w in W:
        print(f"fix {w}: " + " ".join(f"{m}:{efficiency(fixes[w][m]):.2f}" for m in range(7)), flush=True)
    bestfix = {w: max(range(7), key=lambda m: efficiency(fixes[w][m])) for w in W}
    manual = {}
    for w in W:
        ms = ROWS[ROW[w]]["manual"]
        scored = [(efficiency(B.run_plain(w, a, TUNE, kw)), n, a, kw) for n, a, kw in ms]
        manual[w] = max(scored, key=lambda x: x[0])
    print(f"one Bayes setting for all worlds, by the search's own score: {one}", flush=True)
    print("per world: " + " ".join(f"{w}:{best[w]}" for w in W), flush=True)
    print("best model from birth: " + " ".join(f"{w}:{bestfix[w]}" for w in W), flush=True)
    print("manual: " + " ".join(f"{w}:{manual[w][1]}" for w in W), flush=True)

    print("\n== judged, seeds 60000-60199 x 2. Each against the bank, paired", flush=True)
    summary = {}
    for w in W:
        bk = B.run(w, "v_rec", JUDGE)
        print(f"-- {w}: bank {efficiency(bk):.3f}; rival picks in {fp(bk, RIGHT[w])[0]:.2f} of lives, a right pick in {fp(bk, RIGHT[w])[1]:.2f}, at {fp(bk, RIGHT[w])[2]:.1f} s", flush=True)
        b0 = B.run_plain(w, "circuit", JUDGE)
        print("   " + pr("base", w, b0, bk), flush=True)
        o = B.run(w, one[0], JUDGE, json.loads(one[1]))
        print("   " + pr(f"Bayes one setting {name(one[0], json.loads(one[1]))}", w, o, bk) + f"; picks {fp(o, RIGHT[w])[0]:.2f}, right {fp(o, RIGHT[w])[1]:.2f} at {fp(o, RIGHT[w])[2]:.1f} s", flush=True)
        pw = B.run(w, best[w][0], JUDGE, json.loads(best[w][1]))
        print("   " + pr(f"Bayes this world's best {name(best[w][0], json.loads(best[w][1]))}", w, pw, bk) + f"; picks {fp(pw, RIGHT[w])[0]:.2f}, right {fp(pw, RIGHT[w])[1]:.2f} at {fp(pw, RIGHT[w])[2]:.1f} s", flush=True)
        for a, kw in PARTS:
            q = B.run(w, a, JUDGE, kw)
            print("   " + pr(name(a, kw), w, q, bk), flush=True)
        f = B.run(w, "fix", JUDGE, dict(fix=float(bestfix[w])))
        print("   " + pr(f"best model from birth ({bestfix[w]})", w, f, bk), flush=True)
        v = B.run(w, "vtold", JUDGE)
        print("   " + pr("the bank's parts told the colour", w, v, bk), flush=True)
        tc = B.run_plain(w, "toldc", JUDGE)
        print("   " + pr("base movements told the colour, mismatch there", w, tc, bk), flush=True)
        ta, tk = ROWS[ROW[w]]["target"]
        tg = B.run_plain(w, ta, JUDGE, tk)
        print("   " + pr(f"row's target ({ta})", w, tg, bk), flush=True)
        m = B.run_plain(w, manual[w][2], JUDGE, manual[w][3])
        print("   " + pr(f"row's manual ({manual[w][1]})", w, m, bk), flush=True)
        for nm, A, Bb in (("Bayes(this world's best) - bank [crude inference]", pw, bk), ("birth - Bayes(this world's best) [time to gather evidence among the seven]", f, pw), ("told parts - birth [the model's own learning]", v, f), ("target - told parts [the bank's movements and parts]", tg, v), ("manual - told parts", m, v)):
            d, i = T.paired(A, Bb, boot=1000)
            print(f"   step {nm}: {d:+.3f} [{i[0]:+.3f},{i[1]:+.3f}]", flush=True)

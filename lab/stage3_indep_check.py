"""stage3_indep_check.py: the independent check of stage 3 (PROGRAMME.md, gate 3 to B), by an agent that didn't produce it,
2026-11-07. Recomputes from the raw saved lives (/home/pilgrim/nca-scratch-backup/stage3/{label,main,ref,more_*}.pkl), not from
the producer's rows.pkl; its own bootstrap (own RNG seed, B=4000), pairs resampled whole (a pair = one seed's red and blue lives,
saved at indices 2i, 2i+1: lab/stage3_random.py's `for s in SEEDS for c in COL`).

    .venv/bin/python lab/stage3_indep_check.py > lab/v/stage3_indep_check.log"""
import pickle
import re
import sys
from collections import defaultdict
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import numpy as np

D = "/home/pilgrim/nca-scratch-backup/stage3/"
B = 4000
Z = 1.959964


def load(k):
    return pickle.load(open(D + k + ".pkl", "rb"))


def wilson(k, n):
    p = k / n
    c = (p + Z * Z / (2 * n)) / (1 + Z * Z / n)
    h = Z * np.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / (1 + Z * Z / n)
    return c - h, c + h


def pairs_idx(npairs, seed):
    k = np.random.default_rng(seed).integers(0, npairs, (B, npairs))
    return np.concatenate((2 * k, 2 * k + 1), axis=1)


def gs(L, last=False):
    """gain and spent arrays of a list of lives; refusals are an error here (counted separately)."""
    assert not any(x[0] == "refused" for x in L)
    g = np.array([x[2] if last else x[0] for x in L], float)
    s = np.array([x[1] * (x[3] if last else 1.0) for x in L], float)
    return g, s


def effb(L, I, last=False):
    g, s = gs(L, last)
    return g.sum() / s.sum(), g[I].sum(1) / s[I].sum(1)


def q(v):
    v = v[np.isfinite(v)]
    return np.percentile(v, [2.5, 97.5])


def judge(A, I, ref=None):
    """A: {base, bank, told} lists of lives (same seeds, same order); ref likewise or None. Returns a dict."""
    b, k, t = (effb(A[a], I) for a in ("base", "bank", "told"))
    fl0, fl = max(b[0], 0.0), np.maximum(b[1], 0.0)
    g0, g = t[0] - fl0, t[1] - fl
    gl, gh = q(g)
    out = dict(base=b[0], bank=k[0], told=t[0], gap=g0, gap_ci=(gl, gh), learn=bool(gl > 0 and g0 >= 0.1))
    with np.errstate(divide="ignore", invalid="ignore"):
        x0, x = (k[0] - fl0) / g0, (k[1] - fl) / g
        if ref is not None:
            rr = effb(ref, I)
            r0, r = (rr[0] - fl0) / g0, (rr[1] - fl) / g
        else:
            r0, r = np.nan, np.full(len(I), np.nan)
    xl, xh = q(x)
    bar = max(0.5 * r0 if np.isfinite(r0) else 0.0, 0.25)
    out.update(x=x0, x_ci=(xl, xh), r=r0, bar=bar, verdict=("pass" if xl > bar else "fail" if xh < bar else "unclear"))
    # the bar's own uncertainty: interval of x - max(.5 r, .25), paired on the same resample
    if ref is not None:
        with np.errstate(invalid="ignore"):
            d = x - np.maximum(np.where(np.isfinite(r), 0.5 * r, 0.0), 0.25)
        dl, dh = q(d)
        out["verdict_rboot"] = "pass" if dl > 0 else "fail" if dh < 0 else "unclear"
    else:
        out["verdict_rboot"] = out["verdict"]
    out["harm"] = k[0] - b[0]
    out["harm_ci"] = tuple(q(k[1] - b[1]))
    return out


def skeleton(text):
    return re.sub(r"-?\d+(\.\d+)?(e-?\d+)?", "#", text), [float(m.group()) for m in re.finditer(r"-?\d+(\.\d+)?(e-?\d+)?", text)]


def main():
    import stage3_random as R
    W, redo, fresh = R.worlds()
    print(f"draws: redo {len(redo)} ({redo[0]}..{redo[-1]}), fresh {len(fresh)} ({fresh[0]}..{fresh[-1]})")
    # ---- distinctness
    redo_texts = {W[n][0] for n in redo}
    seen, distinct, dup_in, dup_redo = {}, [], [], []
    for n in fresh:
        t = W[n][0]
        if t in redo_texts:
            dup_redo.append(n)
        elif t in seen:
            dup_in.append((n, seen[t]))
        else:
            seen[t] = n
            distinct.append(n)
    print(f"[distinct] fresh repeats of a fresh draw {len(dup_in)} {dup_in}; repeats of a redo draw {len(dup_redo)} {dup_redo}; "
          f"distinct {len(distinct)}")
    # near-duplicates: same skeleton, every number within 5% (relative)
    sk = defaultdict(list)
    for n in redo + distinct:
        s, v = skeleton(W[n][0])
        sk[s].append((n, v))
    near = []
    for s, items in sk.items():
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                (a, va), (b, vb) = items[i], items[j]
                if len(va) == len(vb) and all(abs(x - y) <= 0.05 * max(abs(x), abs(y)) for x, y in zip(va, vb)):
                    if b in distinct:
                        near.append((a, b))
    print(f"[near-dup] pairs (a fresh distinct world with every number within 5% (relative) of an earlier world's, same form): {len(near)} {near}")
    # ---- outs
    lab = load("label")
    refused_lab = [n for n in distinct if lab[n]["refused"]]
    labelled = {n: lab[n]["labelled"] for n in distinct if lab[n]["labelled"]}
    out = [n for n in distinct if lab[n]["refused"] or lab[n]["labelled"] >= 3]
    print(f"[out] refused in labelling {refused_lab}; labelled lives by world (of 16) {labelled}; out {len(out)} {out}; "
          f"lives per world {set(lab[n]['lives'] for n in distinct)}")
    judged = [n for n in distinct if n not in out]
    print(f"[judged] {len(judged)}")
    # ---- refusals anywhere
    main_, ref = load("main"), load("ref")
    T, H, Lg = load("more_topup"), load("more_harm"), load("more_long")
    for name, d in (("main", main_), ("ref", ref), ("topup", T), ("harm", H), ("long", Lg)):
        cnt = 0
        for n, v in d.items():
            for L in (v.values() if isinstance(v, dict) else [v]):
                cnt += sum(x[0] == "refused" for x in L)
        print(f"[refusals] {name}: {cnt} refused lives")
    missing = [n for n in judged if n not in main_]
    print(f"[main] judged worlds without main lives: {missing}; lives per arm {set(len(main_[n][a]) for n in judged for a in main_[n])}")
    # ---- first pass, own bootstrap
    I60 = pairs_idx(60, 20261107)
    first = {}
    for n in judged:
        first[n] = judge(main_[n], I60, ref.get(n))
    learn = [n for n in judged if first[n]["learn"]]
    noref = [n for n in learn if n not in ref]
    print(f"\n[first pass, 60 pairs] something to learn {len(learn)}/{len(judged)}; learn-worlds lacking a ref run {noref}")
    c = defaultdict(list)
    for n in learn:
        c[first[n]["verdict"]].append(n)
    print(f"  sure pass {len(c['pass'])}, sure fail {len(c['fail'])}, can't tell {len(c['unclear'])}")
    for k in ("pass", "fail", "unclear"):
        print(f"  {k}: {c[k]}")
    diff_r = [n for n in learn if first[n]["verdict"] != first[n]["verdict_rboot"]]
    print(f"  verdicts that change if r's own uncertainty enters the bar: {[(n, first[n]['verdict'], first[n]['verdict_rboot']) for n in diff_r]}")
    big_r = [(n, round(first[n]["r"], 2)) for n in learn if np.isfinite(first[n]["r"]) and first[n]["r"] > 0.5]
    print(f"  worlds where .5 r sets the bar (r > .5): {big_r}")
    # ---- top-up
    unclear60 = c["unclear"]
    print(f"\n[top-up] first-pass can't-tell {len(unclear60)}; in more_topup {sum(n in T for n in unclear60)}; "
          f"topup worlds not in that list {[n for n in T if n not in unclear60]}")
    I300 = pairs_idx(300, 7)
    final = dict(first)
    tv = defaultdict(list)
    for n in unclear60:
        if n not in T:
            j = first[n]
            print(f"  {n:5s} NOT TOPPED UP: 60-pair gap {j['gap']:+.3f}[{j['gap_ci'][0]:+.3f},{j['gap_ci'][1]:+.3f}] x {j['x']:+.3f}"
                  f"[{j['x_ci'][0]:+.3f},{j['x_ci'][1]:+.3f}], no ref run; kept at its 60-pair verdict")
            continue
        A = {a: main_[n][a] + T[n][a] for a in ("base", "bank", "told")}
        Rf = ref[n] + T[n]["ref"]
        assert all(len(v) == 600 for v in A.values()) and len(Rf) == 600
        j = judge(A, I300, Rf)
        j["verdict_eff"] = j["verdict"] if j["learn"] else "nothing"
        final[n] = j
        tv[j["verdict_eff"]].append(n)
        print(f"  {n:5s} gap {j['gap']:+.3f}[{j['gap_ci'][0]:+.3f},{j['gap_ci'][1]:+.3f}] x {j['x']:+.3f}[{j['x_ci'][0]:+.3f},"
              f"{j['x_ci'][1]:+.3f}] r {j['r']:+.2f} bar {j['bar']:.3f} -> {j['verdict_eff']:8s} (bar with r's interval: "
              f"{j['verdict_rboot'] if j['learn'] else '-'})")
    print("  " + ", ".join(f"{k} {len(v)}" for k, v in tv.items()))
    # topup's top-up lives alone vs first-pass lives: are the topup lives different seeds (not copies of the first pass)?
    same = sum(T[n]["base"][i][:2] == main_[n]["base"][i][:2] for n in unclear60 if n in T for i in range(120))
    print(f"  first 120 top-up base lives identical to the first pass's (gain, spent): {same} of {120 * sum(n in T for n in unclear60)}")
    # the producer's own bootstrap (stage3_random.boot, seed 0) on the first pass, to see whether the borderline worlds move
    I0 = R.boot(60)
    flips = [(n, first[n]['learn'], judge(main_[n], I0, ref.get(n))['learn']) for n in judged]
    flips = [f for f in flips if f[1] != f[2]]
    print(f"  'something to learn' differs between my bootstrap and the producer's seed-0 bootstrap at 60 pairs: {flips}")
    # ---- final tally
    learnF = [n for n in judged if final[n]["learn"]]
    sp = [n for n in learnF if final[n]["verdict"] == "pass"]
    sf = [n for n in learnF if final[n]["verdict"] == "fail"]
    un = [n for n in learnF if final[n]["verdict"] == "unclear"]
    N, M = len(learnF), len(judged)
    lo, hi = wilson(len(sp), N), wilson(len(sp) + len(un), N)
    print(f"\n[final] something to learn {N}/{M} = {N / M:.3f} Wilson [{wilson(N, M)[0]:.3f},{wilson(N, M)[1]:.3f}]")
    print(f"  sure pass {len(sp)} {sp}\n  sure fail {len(sf)} {sf}\n  can't tell {len(un)} {un}")
    print(f"  coverage between {len(sp) / N:.3f} [{lo[0]:.3f},{lo[1]:.3f}] and {(len(sp) + len(un)) / N:.3f} [{hi[0]:.3f},{hi[1]:.3f}]")
    # near-duplicate collapse
    dropped = {b for a, b in near if a in judged or a in redo}
    learnD = [n for n in learnF if n not in dropped]
    spD = [n for n in sp if n not in dropped]
    unD = [n for n in un if n not in dropped]
    ND = len(learnD)
    print(f"  near-duplicates collapsed (drop {sorted(dropped)}): judged {len([n for n in judged if n not in dropped])}, "
          f"to learn {ND}, sure pass {len(spD)}, can't tell {len(unD)}: coverage {len(spD) / ND:.3f} [{wilson(len(spD), ND)[0]:.3f},"
          f"{wilson(len(spD), ND)[1]:.3f}] to {(len(spD) + len(unD)) / ND:.3f} [{wilson(len(spD) + len(unD), ND)[0]:.3f},"
          f"{wilson(len(spD) + len(unD), ND)[1]:.3f}]")
    for a, b in near:
        if a in main_ and b in main_:
            same = sum(main_[a][arm][i][:2] == main_[b][arm][i][:2] for arm in ("base", "bank", "told") for i in range(120))
            print(f"  near pair {a}/{b}: identical (gain, spent) lives in main {same}/360; verdicts {final.get(a, {}).get('verdict')}, "
                  f"{final.get(b, {}).get('verdict')}")
    # ---- the reference's step (2.5 ms against 1.25 ms for base, bank, told): stage2c_converge2 shows level shifts of up to about
    # .04 between the two steps; shift ref by +-.05 and see whether any verdict moves
    Iv = {n: (I300 if n in T else I60) for n in learnF}
    moved = []
    for n in learnF:
        if n not in ref:
            continue
        A = {a: main_[n][a] + (T[n][a] if n in T else []) for a in ("base", "bank", "told")}
        Rf = ref[n] + (T[n]["ref"] if n in T else [])
        for sh in (-0.08, -0.05, 0.05, 0.08):
            Rs = [(x[0] + sh * x[1],) + tuple(x[1:]) for x in Rf]      # shifts the ref's efficiency by sh exactly
            v = judge(A, Iv[n], Rs)["verdict"]
            if v != final[n]["verdict"]:
                moved.append((n, sh, final[n]["verdict"], v))
    print(f"\n[ref step] verdicts that move if the reference's efficiency shifts by +-.05 or +-.08 (D34's 'within about .08'): {moved}")
    margins = [(n, round(final[n]["x_ci"][0] - final[n]["bar"], 3), round(final[n]["x_ci"][1] - final[n]["bar"], 3)) for n in learnF
               if final[n]["verdict"] != "unclear" and min(abs(final[n]["x_ci"][0] - final[n]["bar"]), abs(final[n]["x_ci"][1] - final[n]["bar"])) < 0.03]
    print(f"  sure verdicts within .03 of the bar (x lower - bar, x upper - bar): {margins}")
    # ---- selection: worlds 'nothing' at 60 pairs that sit near the threshold (never topped up)
    near_thr = [(n, round(first[n]["gap"], 3), round(first[n]["gap_ci"][0], 3)) for n in judged
                if not first[n]["learn"] and first[n]["gap"] >= 0.07]
    print(f"\n[selection] nothing-to-learn at 60 pairs with gap >= .07 (not topped up; some would have a gap at 300): {len(near_thr)} {near_thr}")
    drop_top = [n for n in unclear60 if not final[n]["learn"]]
    print(f"  top-up worlds that lost their gap at 300 pairs: {len(drop_top)}; first-pass sure verdicts never re-checked: "
          f"{len(c['pass']) + len(c['fail'])}; sure-verdict worlds with gap < .2 at 60 pairs: "
          f"{[(n, round(first[n]['gap'], 3)) for n in c['pass'] + c['fail'] if first[n]['gap'] < 0.2]}")
    # expected miscalls from multiplicity: each sure verdict is a 2.5% one-sided test against the bar
    print(f"  multiplicity: {len(sp) + len(sf)} sure verdicts at one-sided 2.5% each: about {0.025 * (len(sp) + len(sf)):.1f} expected "
          f"false sure calls if every world sat on the bar (an upper figure)")
    # x above 1
    print(f"  x > 1 at 100 s among worlds to learn: {[(n, round(final[n]['x'], 2)) for n in learnF if final[n]['x'] > 1]}")
    # ---- harm in nothing-to-learn worlds (first pass)
    nothing = [n for n in judged if not final[n]["learn"]]
    hs = [n for n in nothing if final[n]["harm_ci"][1] < -0.1]
    hb = [n for n in nothing if final[n]["harm_ci"][1] < 0]
    ha = [n for n in nothing if final[n]["harm_ci"][0] > 0]
    print(f"\n[harm, first pass, nothing-to-learn {len(nothing)} incl. top-up drops] surely below base {len(hb)}, by > .1 {len(hs)} {hs}; "
          f"surely above {len(ha)}; rule 'lower bound > -.1' fails in {sum(final[n]['harm_ci'][0] <= -0.1 for n in nothing)}")
    Ih = pairs_idx(200, 11)
    print("[harm, 200 fresh pairs (more_harm)]")
    for n in H:
        b, k, t = (effb(H[n][a], Ih) for a in ("base", "bank", "told"))
        dl, dh = q(k[1] - b[1])
        tl, th = q(t[1] - b[1])
        print(f"  {n:5s} base {b[0]:+.3f} bank {k[0]:+.3f} told {t[0]:+.3f}  bank-base {k[0] - b[0]:+.3f}[{dl:+.3f},{dh:+.3f}]  "
              f"told-base {t[0] - b[0]:+.3f}[{tl:+.3f},{th:+.3f}]  {len(H[n]['base'])} lives")
    # ---- 1000 s
    Il = pairs_idx(20, 13)
    print("[1000 s, 20 pairs; last third; bar .25 (no ref at 1000 s)]")
    for n in Lg:
        A = Lg[n]
        b, k, t = (effb(A[a], Il, True) for a in ("base", "bank", "told"))
        fl0, fl = max(b[0], 0), np.maximum(b[1], 0)
        g0, g = t[0] - fl0, t[1] - fl
        gl, gh = q(g)
        with np.errstate(divide="ignore", invalid="ignore"):
            x0, x = (k[0] - fl0) / g0, (k[1] - fl) / g
        xl, xh = q(x)
        learn_ = gl > 0 and g0 >= 0.1
        v = ("pass" if xl > 0.25 else "fail" if xh < 0.25 else "unclear") if learn_ else "nothing"
        bk = k[0] - t[0]
        print(f"  {n:5s} 100s {first[n]['verdict']:7s} base {b[0]:+.2f} bank {k[0]:+.2f} told {t[0]:+.2f} gap {g0:+.2f}[{gl:+.2f},{gh:+.2f}] "
              f"x {x0:+.2f}[{xl:+.2f},{xh:+.2f}] -> {v:8s} {'bank>told' if bk > 0 else ''}")


if __name__ == "__main__":
    main()

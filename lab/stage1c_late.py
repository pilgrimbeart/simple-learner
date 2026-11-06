"""stage1c_late.py: stage 1c part 3. Does the floor pay? Worlds where the right model becomes right mid-life (lab/stage1c_arms.py, Late), plain until T then alternate, pattern or one permanent swap; and, an addition to the brief, one lie in five throughout (nlate), since a plain prefix may leave little to forget.

Measures, for each arm in each world, paired against the bank over seeds (a seed's two lives together):
  efficiency after T (food less 2 a poison, after T, over what the life spends after T), and over the life;
  delay: from T to the first right pick (alternate, pattern: a model of the right set is followed at or after T), censored at the life's end; for all rules also the first time, at or after T, that three scored tastes running found the followed colour the rule's;
  false picks: a rival not in the right set, before T and after it;
  range: the lowest and highest E any rival's counter reached, and the bits to hold it (log2 levels in steps of one).

Arms' state, in bits per rival: a counter from floor to top (10) in unit steps; a no-floor counter holds what it reached. MAP and Bayes arms hold each model's hit count (over a life at most the scored tastes, about 60-100, so about 6-7 bits a model).

    .venv/bin/python lab/stage1c_late.py [run|tally]"""
import json
import pickle
import sys
import time
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np
import stage1c_arms as A
import bits_bank as B
from minimal.spec import COST, NEED, THRUST, ENERGY, SPAN
from units import TICK

SEEDS = range(62000, 62200)
RULES = ("alternate", "pattern", "swap")
RIGHTSET = dict(alternate={2, 4, 6}, pattern={3, 6}, swap={0, 1})
BEST_RIVAL = dict(alternate=2, pattern=3, swap=1)
LIFE = 100.0
FSSET = None                                            # 2(a)'s setting: from fs_chosen.json


def arms():
    fs = json.load(open(A.OUT + "fs_chosen.json"))["one"]
    return [("bank", "banke", {}), ("+1/-1 floor 0", "ctrr", dict(pen=1.0, floor=0.0)), ("+1/-1 no floor", "ctrr", dict(pen=1.0, floor=None)), ("+1/-3 no floor", "ctrr", dict(pen=3.0, floor=None)),
            ("+1/-3 floor -3", "ctrr", dict(pen=3.0, floor=-3.0)), ("+1/-3 floor -10", "ctrr", dict(pen=3.0, floor=-10.0)), ("+1/-1 floor -3", "ctrr", dict(pen=1.0, floor=-3.0)), ("+1/-1 floor -10", "ctrr", dict(pen=1.0, floor=-10.0)),
            ("stationary MAP k=1.5", "map", dict(k=1.5)), ("stationary BMA e.2", "bma", dict(eps=0.2, pr=0.6)), ("fixed share (2a)", fs[0], json.loads(fs[1])), ("default from birth", "fix", dict(fix=0.0)), ("right rival from birth", "fix", None), ("told", "vtold", {})]


def after(l, Ton):
    """(gained, spent) after Ton s."""
    k = int(round(Ton / TICK))
    good = l.mt >= k
    g = (~l.mbad[good]).sum() - COST * l.mbad[good].sum()
    s = (NEED * (LIFE - Ton) / SPAN + THRUST * (l.ft >= k).sum() * SPAN / (LIFE - Ton) * (LIFE - Ton) / SPAN + ENERGY * l.power * (LIFE - Ton) / SPAN)
    return float(g), float(s)


def delays(l, rule, Ton):
    """First right pick at or after T (rule alternate, pattern; inf if none); first three running right followings; false picks before and after T."""
    x = l.rows
    right = RIGHTSET[rule]
    # model followed just before T
    act = 0
    pick = np.inf
    false_before, false_after = 0, 0
    for tt, m in l.picks:
        if tt < Ton:
            act = m
            if m:
                false_before += 1
    if rule != "swap":
        if act in right:
            pick = Ton
        for tt, m in l.picks:
            if tt >= Ton:
                if m and m not in right:
                    false_after += 1
                if m in right and pick == np.inf:
                    pick = tt
    s = x[x[:, B.COLS.index("scored")] > 0] if len(x) else x
    follow = np.inf
    if len(s):
        ok = s[:, B.COLS.index("followed")] == s[:, B.COLS.index("F")]
        ts = s[:, B.COLS.index("t")]
        r = 0
        for tt, o in zip(ts, ok):
            if tt < Ton:
                continue
            r = r + 1 if o else 0
            if r >= 3:
                follow = tt
                break
    return pick, follow, false_before, false_after


def erange(l):
    if not hasattr(l, "etrace") or not len(l.etrace):
        return None
    E = l.etrace[:, 2:]
    return E.min(0), E.max(0)


def e_at(l, Ton):
    if not hasattr(l, "etrace") or not len(l.etrace):
        return None
    i = np.searchsorted(l.etrace[:, 0], Ton)
    return l.etrace[i - 1, 2:] if i else np.zeros(6)


def measures(L, rule, Ton):
    a = np.array([after(l, Ton) for l in L])
    d = np.array([delays(l, rule, Ton) for l in L])
    return dict(a=a, d=d, g=A.gs(L)[0], s=A.gs(L)[1])


def boot_diff(fn, n, boot=1000):
    I = A.resample(n, boot)
    v = np.array([fn(i) for i in I])
    return fn(np.arange(n)), np.percentile(v, 2.5), np.percentile(v, 97.5)


def censor(d, Ton):
    return np.minimum(d, LIFE) - Ton


def main():
    t0 = time.time()
    AR = arms()
    out = {}
    worlds = [(f"late_{r}_{t}", r, t) for r in RULES for t in A.LATE_T] + [(f"nlate_{r}_{t}", r, t) for r in RULES for t in (30, 70)]
    print("== controls: T beyond the life reproduces plain, and with lies, unreliable, exactly, in the fresh seeds", flush=True)
    print("late_never = plain:", A.identical(A.run("late_never", "v_rec", range(62000, 62010)), A.run("plain", "v_rec", range(62000, 62010))), flush=True)
    print("nlate_never = unreliable:", A.identical(A.run("nlate_never", "v_rec", range(62000, 62010)), A.run("unreliable", "v_rec", range(62000, 62010))), flush=True)
    bank_streams = {}
    for w, rule, Ton in worlds:
        print(f"\n-- {w} [{time.time() - t0:.0f} s]", flush=True)
        res = {}
        for name, arm, kw in AR:
            if kw is None:
                kw = dict(fix=float(BEST_RIVAL[rule]))
            L = A.run(w, arm, SEEDS, kw)
            m = measures(L, rule, Ton)
            m["eff"] = A.eff_ci(L)
            m["L"] = None
            m["pd"] = None
            rng = [erange(l) for l in L]
            if rng[0] is not None:
                lo = np.array([r[0] for r in rng])
                hi = np.array([r[1] for r in rng])
                m["lo"], m["hi"] = lo, hi
                m["eT"] = np.array([e_at(l, Ton) for l in L])
            res[name] = m
            if name == "bank":
                bank_streams[w] = A.keep(L)
        ba = res["bank"]
        for name, m in res.items():
            n = len(m["a"])
            ef = lambda i: m["a"][i, 0].sum() / m["a"][i, 1].sum() - ba["a"][i, 0].sum() / ba["a"][i, 1].sum()
            d1 = boot_diff(ef, n)
            pk, pkb = censor(m["d"][:, 0], Ton), censor(ba["d"][:, 0], Ton)
            fo, fob = censor(m["d"][:, 1], Ton), censor(ba["d"][:, 1], Ton)
            dl = boot_diff(lambda i: fo[i].mean() - fob[i].mean(), n)
            dp = boot_diff(lambda i: pk[i].mean() - pkb[i].mean(), n) if rule != "swap" else (float("nan"),) * 3
            effa = m["a"][:, 0].sum() / m["a"][:, 1].sum()
            rg = ""
            if "lo" in m:
                lo = np.percentile(m["lo"].min(1), 1)
                rg = f"; E range to {lo:.0f} (1% of lives), at T median per rival {np.median(m['eT'], axis=0).round(1).tolist()}, {np.log2(10 - lo + 1):.1f} bits per rival"
            print(f"   {name:24s} after T {effa:6.3f} ({d1[0]:+.3f} [{d1[1]:+.3f},{d1[2]:+.3f}]{' SURE' if d1[1] > 0 or d1[2] < 0 else ''}); life {m['eff'][0]:.3f}; follow-delay {fo.mean():5.1f} s, median {np.median(fo):5.1f} ({dl[0]:+.1f} [{dl[1]:+.1f},{dl[2]:+.1f}]{' SURE' if dl[1] > 0 or dl[2] < 0 else ''}); pick-delay {pk.mean() if rule != 'swap' else float('nan'):5.1f} ({dp[0]:+.1f} [{dp[1]:+.1f},{dp[2]:+.1f}]); never {np.mean(m['d'][:, 1] >= LIFE):.2f}; false picks before T {np.mean(m['d'][:, 2] > 0):.3f} after {np.mean(m['d'][:, 3] > 0):.3f}{rg}", flush=True)
        out[w] = {k: {kk: vv for kk, vv in v.items() if kk not in ("L", "pd")} for k, v in res.items()}
        with open(A.OUT + "late.pkl", "wb") as f:
            pickle.dump(out, f)
        with open(A.OUT + "late_bank_streams.pkl", "wb") as f:
            pickle.dump(bank_streams, f)
    print(f"[done {time.time() - t0:.0f} s]", flush=True)


def tally():
    """Each arm's life efficiency against the bank: across the late-onset worlds, and with the nine stationary worlds run here on the same seeds; each world equal weight. Per-life g, s, paired by seed."""
    out = pickle.load(open(A.OUT + "late.pkl", "rb"))
    ARMS = [a[0] for a in arms() if a[0] not in ("told", "default from birth", "right rival from birth")]
    t0 = time.time()
    stat = {}
    for w in B.WORLDS9:
        stat[w] = {}
        for name, arm, kw in arms():
            if name in ARMS:
                L = A.run(w, arm, SEEDS, kw)
                stat[w][name] = A.gs(L)
        print(f"   {w} [{time.time() - t0:.0f} s]", flush=True)
    with open(A.OUT + "late_stat.pkl", "wb") as f:
        pickle.dump(stat, f)
    print("== tally: mean over worlds of life efficiency, each arm minus the bank, paired, 95% over seeds, each world equal weight", flush=True)
    late = [w for w in out if w.startswith("late_")]
    nlate = [w for w in out if w.startswith("nlate_")]
    for T_ in A.LATE_T:
        pass
    sets = {"nine stationary": [("s", w) for w in B.WORLDS9], "late-onset after plain": [("l", w) for w in late], "late-onset with lies": [("l", w) for w in nlate], "nine + late after plain": [("s", w) for w in B.WORLDS9] + [("l", w) for w in late], "all": [("s", w) for w in B.WORLDS9] + [("l", w) for w in late + nlate]}

    def get(kind, w, name):
        if kind == "s":
            return stat[w][name]
        return out[w][name]["g"], out[w][name]["s"]
    N = 400
    I = A.resample(N, 1000)
    for sn, S in sets.items():
        print(f"-- {sn}")
        for name in ARMS:
            d = []
            for kind, w in S:
                ga, sa = get(kind, w, name)
                gb, sb = get(kind, w, "bank")
                d.append(ga[I].sum(1) / sa[I].sum(1) - gb[I].sum(1) / sb[I].sum(1))
            d = np.mean(d, axis=0)
            pt = np.mean([get(k, w, name)[0].sum() / get(k, w, name)[1].sum() - get(k, w, "bank")[0].sum() / get(k, w, "bank")[1].sum() for k, w in S])
            print(f"   {name:24s} {pt:+.3f} [{np.percentile(d, 2.5):+.3f},{np.percentile(d, 97.5):+.3f}]{' SURE' if np.percentile(d, 2.5) > 0 or np.percentile(d, 97.5) < 0 else ''}", flush=True)
    print("-- per world: + surely above the bank, - surely below, . tied", flush=True)
    print(" " * 24 + " ".join(f"{(k + w)[:18]:>18s}" for k, w in sets["all"]))
    for name in ARMS:
        c = []
        for k, w in sets["all"]:
            ga, sa = get(k, w, name)
            gb, sb = get(k, w, "bank")
            v = ga[I].sum(1) / sa[I].sum(1) - gb[I].sum(1) / sb[I].sum(1)
            lo, hi = np.percentile(v, 2.5), np.percentile(v, 97.5)
            c.append(f"{v.mean():+.2f}{'+' if lo > 0 else '-' if hi < 0 else '.'}".rjust(18))
        print(f"{name:24s}" + " ".join(c), flush=True)


if __name__ == "__main__":
    (tally if sys.argv[1:] == ["tally"] else main)()

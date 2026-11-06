"""stage1c_replicate.py: stage 1c part 1. 1b's headline arms on fresh development seeds, settings as 1b chose them, no retuning. Streams 62000-62399 x 2; arms 62000-62199 x 2. Also tuning streams 61000-61063 x 2 for part 2a's replay.
    .venv/bin/python lab/stage1c_replicate.py"""
import pickle
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np
import stage1c_arms as A
import bits_bank as B
import time

W = B.WORLDS9
S, J = range(62000, 62400), range(62000, 62200)
ONE = dict(eps=0.2, pr=0.5)
BEST = dict(plain=("map", dict(k=1.5)), swap10=("map", dict(k=0.5)), alternate=("bma", dict(eps=0.05, pr=1 / 7)), pattern=("bma", dict(eps=0.05, pr=1 / 7)), digest=("bma", dict(eps=0.2, pr=0.99)), unreliable=("bma", dict(eps=0.2, pr=0.99)), patchy=("map", dict(k=3.5)), weak=("bma", dict(eps=0.2, pr=0.5)), noisy=("bma", dict(eps=0.1, pr=0.5)))
FIX = dict(plain=0, swap10=1, alternate=2, pattern=3, digest=0, unreliable=0, patchy=0, weak=2, noisy=2)
D31 = {"plain": (2.62, 2.63, 2.62, 2.63, 2.76), "swap10": (0.50, 0.64, 0.88, 1.00, 2.77), "alternate": (1.72, 2.04, 2.09, 2.32, 2.60), "pattern": (1.57, 1.83, 1.95, 2.10, 2.66), "digest": (-0.31, -0.29, -0.14, -0.13, 0.02), "unreliable": (0.48, 0.46, 0.55, 0.55, 0.75), "patchy": (0.70, 0.67, 0.71, 0.71, 0.81), "weak": (1.78, 1.78, 1.78, 1.74, 1.84), "noisy": (1.77, 1.77, 1.77, 1.74, 1.86)}
D31P = dict(swap10=(0.376, 0.576), alternate=(1.731, 1.714), pattern=(1.458, 1.593))
t0 = time.time()


def ce(L):
    v, a, b = A.eff_ci(L)
    return f"{v:.3f} [{a:.3f},{b:.3f}]"


rec = {}
for name, arm, kw, seeds in (("bank", "v_rec", {}, S), ("pinned", "fix", {"fix": 0.0}, S), ("right", "vtold", {}, J), ("wrong", "vtold", {"wrong": 1.0}, J)):
    out, lives = {}, {}
    for w in W:
        lives[w] = A.run(w, arm, seeds, kw)
        out[w] = A.keep(lives[w])
        print(name, w, f"{A.efficiency(lives[w]):.3f}  [{time.time() - t0:.0f} s]", flush=True)
    with open(A.OUT + f"{name}_62000.pkl", "wb") as f:
        pickle.dump(out, f)
    rec[name] = {w: lives[w][:len(J) * 2] for w in W}
for name, arm, kw, seeds in (("bank", "v_rec", {}, range(61000, 61064)), ("pinned", "fix", {"fix": 0.0}, range(61000, 61064))):
    out = {w: A.keep(A.run(w, arm, seeds, kw)) for w in W}
    with open(A.OUT + f"{name}_61000.pkl", "wb") as f:
        pickle.dump(out, f)
print(f"streams done {time.time() - t0:.0f} s", flush=True)

print("\n== headline arms, 62000-62199 x 2. Efficiency [95%]; each against the bank, paired; D31's value in ()", flush=True)
res = {}
for w in W:
    bk = rec["bank"][w]
    print(f"-- {w}: bank {ce(bk)} (D31 {D31[w][0]:.2f})", flush=True)
    one = A.run(w, "bma", J, ONE)
    bw = A.run(w, BEST[w][0], J, BEST[w][1])
    fx = A.run(w, "fix", J, dict(fix=float(FIX[w]))) if FIX[w] else rec["pinned"][w]
    told = rec["right"][w]
    n1 = A.run(w, "ctr", J, dict(pen=1.0, floor=None))
    n3 = A.run(w, "ctr", J, dict(pen=3.0, floor=None))
    hi = A.run(w, "bma", J, dict(eps=0.2, pr=0.5 + 1e-6))
    lo = A.run(w, "bma", J, dict(eps=0.2, pr=0.5 - 1e-6))
    base = A.run_plain(w, "circuit", J)
    for nm, L, d in (("Bayes one setting (bma e.2 pr.5, ties by rounding)", one, D31[w][1]), (f"Bayes world's best {BEST[w]}", bw, D31[w][2]), (f"best model from birth ({FIX[w]})", fx, D31[w][3]), ("told (bank's parts)", told, D31[w][4]), ("+1/-1 no floor", n1, None), ("+1/-3 no floor", n3, None), ("tie to default: bma pr .500001", hi, None), ("tie to rivals: bma pr .499999", lo, None), ("base", base, None)):
        extra = f" (D31 {d:.2f})" if d is not None else ""
        print(f"   {nm}: {ce(L)}{extra}; against bank {A.fmt_d(A.pdiff(L, bk))}", flush=True)
    res[w] = dict(bank=A.eff_ci(bk), one=A.eff_ci(one), best=A.eff_ci(bw), fix=A.eff_ci(fx), told=A.eff_ci(told), n1=A.eff_ci(n1), n3=A.eff_ci(n3), hi=A.eff_ci(hi), lo=A.eff_ci(lo), base=A.eff_ci(base))
    print(f"   [{time.time() - t0:.0f} s]", flush=True)
with open(A.OUT + "replicate.pkl", "wb") as f:
    pickle.dump(res, f)
print("\n== tally: new against D31's, inside the new 95% interval?", flush=True)
for w in W:
    r = res[w]
    print(w + ": " + " ".join(f"{k} {'yes' if r[k][1] <= d <= r[k][2] else 'NO'}({d:.2f} vs {r[k][0]:.2f})" for k, d in zip(("bank", "one", "best", "fix", "told"), D31[w])), flush=True)

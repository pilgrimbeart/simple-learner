"""bits_family.py: question 5 of stage 1b: how many models a life can tell apart, from the measured rate of scored tastes and bits per taste (lab/bits_analyse.py), in three forms:

  Fano, an upper bound for any brain reading the taste's sign through this channel: log2 N <= (n C + 1) / (1 - Pe), n the expected tastes, C the channel's bits a taste. A brain choosing what to eat is feedback, and feedback doesn't raise a memoryless
  channel's capacity (Shannon 1956), so this holds for a brain that experiments. It takes n as measured under the bank's policy, so read n's ceiling below too. Not a bound on what timing could add.
  Union, an estimate of what a family can reach: N models, every pair disagreeing on a share rho of tastes, each disagreement lied about independently with chance e: maximum likelihood fails with chance at most N 2^(-n rho B), B = -log2(2 sqrt(e(1-e))) (Bhattacharyya). So log2 N = n rho B - log2(1/Pe).
  Wald, a lower bound on the tastes to tell one pair apart at error alpha both ways (Wald 1945): n >= w(alpha) / (rho D), w = (1-2a) log2((1-a)/a), D = (1-2e) log2((1-e)/e): any test, sequential included.

    .venv/bin/python lab/bits_family.py"""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np
import bits_analyse as A
import bits_bank as B
from minimal.spec import efficiency


def fano(n, c, pe):
    return (n * c + 1) / (1 - pe)


def bhatt(e):
    return -np.log2(2 * np.sqrt(e * (1 - e)))


def kl(e):
    return (1 - 2 * e) * np.log2((1 - e) / e)


def wald(a):
    return (1 - 2 * a) * np.log2((1 - a) / a)


if __name__ == "__main__":
    bank = A.load("bank")
    print("== Fano upper bound on log2 N (and N), per world, at Pe 0.05; n, C from the bank's real lives. C = 1-H(e); digest's own, from told right and wrong, is larger (0.53), since its channel is lopsided, and shown beside it.")
    Rs = {}
    for w in A.WORLDS:
        n = {10: [], 30: [], 100: []}
        wrong, tot = 0, 0
        for l in bank[w]:
            x = l["rows"]
            s = x[x[:, A.C["scored"]] > 0]
            for T_ in n:
                n[T_].append((s[:, A.C["t"]] < T_).sum())
            ok = s[(s[:, A.C["F"]] >= 0) & (s[:, A.C["eaten"]] >= 0)]
            wrong += (np.where(ok[:, A.C["value"]] > 0, ok[:, A.C["followed"]], 1 - ok[:, A.C["followed"]]) != ok[:, A.C["F"]]).sum()
            tot += len(ok)
        e = wrong / tot
        C = 1 - A.h2(e)
        Rs[w] = dict(e=e, C=C, n={k: np.mean(v) for k, v in n.items()})
        print(f"{w:11s} e {e:.3f} C {C:.3f} | " + " | ".join(f"{T_} s: n {np.mean(n[T_]):.1f}, log2 N <= {fano(np.mean(n[T_]), C, .05):.1f} (N <= {2 ** fano(np.mean(n[T_]), C, .05):.3g})" for T_ in n))
    print("\n== Union estimate of log2 N at Pe 0.05, by rho; a family of tables drawn at random has rho 1/2, and a large family cannot have more (Plotkin). Negative: not even two models at this error.")
    for w in A.WORLDS:
        r = Rs[w]
        print(f"{w:11s} B {bhatt(r['e']):.3f} | " + " | ".join(f"{T_} s: " + " ".join(f"rho {rho}: {r['n'][T_] * rho * bhatt(r['e']) - np.log2(20):+.1f}" for rho in (0.5, 0.2, 0.05)) for T_ in (10, 30, 100)))
    print("\n== Wald: tastes to separate one pair at 5%% both ways, w = %.2f bits; then seconds at 0.63 scored tastes a s (the plain world's), by lie rate e and disagreement share rho. Over 100 s: a 100 s life is too short for that pair at that error, given this rate of tastes." % wald(.05))
    for e in (0.025, 0.05, 0.1, 0.2, 0.3, 0.35, 0.4, 0.45):
        print(f"  e {e}: D {kl(e):.3f} bits a disagreement, C {1 - A.h2(e):.3f} | " + " ".join(f"rho {rho}: {wald(.05) / (rho * kl(e)):.1f} tastes = {wald(.05) / (rho * kl(e)) / .63:.0f} s" for rho in (1.0, 0.5, 0.2, 0.05, 0.01)))
    print("\n== The ceiling on n: pulses of taste in a life under brains that don't choose, and the bank when both colours are food")
    for arm, w in (("unwired", "plain"), ("circuit", "allfood")):
        L = B.run_plain(w, arm, range(60000, 60100))
        m = [sum(a + b for a, b, _ in l) for l in L]
        print(f"  {arm} in {w}: meals a life {np.mean(m):.1f}, sd {np.std(m):.1f}, max {np.max(m)}; efficiency {efficiency(L):.2f}", flush=True)

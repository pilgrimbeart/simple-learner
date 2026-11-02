import sys, pickle, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from minimal.spec import efficiency
V = "/home/pilgrim/git/simple-learner/lab/v/"
def load(t): return pickle.load(open(V + t + ".lives", "rb"))
def paired(a, b, boot=2000, rng=np.random.default_rng(0)):
    n = len(a) // 2; d = []
    for _ in range(boot):
        k = [j * 2 + g for j in rng.integers(0, n, n) for g in (0, 1)]
        d.append(efficiency([a[j] for j in k]) - efficiency([b[j] for j in k]))
    return efficiency(a) - efficiency(b), np.percentile(d, [2.5, 97.5])
H = "_50000-50032"
G = "cal_every32_cal_len8_gate8_stall0.05_stall_need3000"
U = "cal_every32_cal_len8_stall0.05_stall_need3000"
for name, a, b in [
    ("standard: gated - B", f"pb_learn_2000_body0_{G}", "plainB_2000"),
    ("standard: gated - ungated", f"pb_learn_2000_body0_{G}", f"pb_learn_2000_body0_{U}"),
    ("standard: ungated - B", f"pb_learn_2000_body0_{U}", "plainB_2000"),
    ("lopsided: gated - ungated", f"pb_learn_2000_body1_{G}", f"pb_learn_2000_body1_{U}"),
    ("lopsided: gated - oracle", f"pb_learn_2000_body1_{G}", "db_oracle_2000"),
    ("allbody: gated - ungated", f"pb_learn_2000_allbody1_body1_{G}", f"pb_learn_2000_allbody1_{U}"),
    ("allbody: gated - oracle", f"pb_learn_2000_allbody1_body1_{G}", f"pb_oracle_2000_allbody1_{U}")]:
    A, B = load(a + H), load(b + H)
    m, (lo, hi) = paired(A, B)
    print(f"{name}: {efficiency(A):.2f} vs {efficiency(B):.2f}, {m:+.2f} [{lo:+.2f}, {hi:+.2f}]"
          + (f"  sweeps median {np.median([l.sweeps for l in A]):.0f} vs {np.median([getattr(l,'sweeps',0) for l in B]):.0f}"))

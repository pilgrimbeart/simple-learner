exec(open("/home/pilgrim/git/simple-learner/lab/gatepair.py").read().split("H = ")[0])
V += "sparse6/"
import sys
H = sys.argv[1] if len(sys.argv) > 1 else "0-32"
fl = f"tuner_b6_mistune3_tune0_{H}"
for a, b in [("eta0.003", fl), ("eta0.01", fl), ("eta0.03", fl), ("eta0.003", "eta0.01"), ("eta0.03", "eta0.01")]:
    A = load(a if a.startswith("tuner") else f"tuner_b6_{a}_mistune3_{H}")
    B = load(b if b.startswith("tuner") else f"tuner_b6_{b}_mistune3_{H}")
    m, (lo, hi) = paired(A, B); print(f"{a} - {b[:12]}: {efficiency(A):.2f} vs {efficiency(B):.2f}, {m:+.2f} [{lo:+.2f}, {hi:+.2f}]")

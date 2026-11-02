exec(open("/home/pilgrim/git/simple-learner/lab/gatepair.py").read().split("H = ")[0])
V += "sparse6/"
import glob, os
fl, e1 = "tuner_b6_mistune3_tune0_0-32", "tuner_b6_eta0.01_mistune3_0-32"
for a in sorted(glob.glob(V + "*tau_r*")):
    a = os.path.basename(a)[:-6]
    for b in (fl, e1):
        A, B = load(a), load(b); m, (lo, hi) = paired(A, B)
        print(f"{a} - {b}: {efficiency(A):.2f} vs {efficiency(B):.2f}, {m:+.2f} [{lo:+.2f}, {hi:+.2f}]")

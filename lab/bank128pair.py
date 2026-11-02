exec(open("/home/pilgrim/git/simple-learner/lab/gatepair.py").read().split("H = ")[0])
import glob, os
def f(pat):
    m = glob.glob(V + pat + ".lives"); assert len(m) == 1, (pat, m); return os.path.basename(m[0])[:-6]
b = "cal_every32_cal_fast12_cal_first0_cal_len8_"
ex = f"pb_learn_2000_body1_{b}gate8_gate_rate1_stall0.05_stall_need3000_sync1_50000-50032"
k = lambda n: f"pb_learn_2000_bank{n}_body1_{b}gate8_gate_rate1_local1_stall0.05_stall_need3000_sync1_50000-50032"
c3 = f("pb_learn_2000_bank128_binary1_body1_*cap3_*sync1_50000-50032")
for name, a, e in [("128 - exact", k(128), ex), ("192 - exact", k(192), ex), ("128 - 96", k(128), k(96)),
                   ("192 - 96", k(192), k(96)), ("128cap3 - 128", c3, k(128)), ("128cap3 - exact", c3, ex)]:
    A, B = load(a), load(e); m, (lo, hi) = paired(A, B)
    print(f"{name}: {efficiency(A):.2f} vs {efficiency(B):.2f}, {m:+.2f} [{lo:+.2f}, {hi:+.2f}]")

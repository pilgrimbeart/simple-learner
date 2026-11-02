exec(open("/home/pilgrim/git/simple-learner/lab/gatepair.py").read().split("H = ")[0])
import glob, os
def f(pat):
    m = glob.glob(V + pat + ".lives"); assert len(m) == 1, (pat, m); return os.path.basename(m[0])[:-6]
b = "cal_every32_cal_fast12_cal_first0_cal_len8_"; t = "gate8_gate_rate1_stall0.05_stall_need3000_sync1_50000-50032"
rows = [("lopsided", "pb_learn_2000_bank192_binary1_body1_*cap3_*sync1_50000-50032", [f"pb_learn_2000_body1_{b}{t}", "pb_oracle_2000_body1_sync1_50000-50032"]),
        ("allbody", "pb_learn_2000_allbody1_bank192_binary1_body1_*cap3_*sync1_50000-50032", [f"pb_learn_2000_allbody1_body1_{b}{t}", "pb_oracle_2000_allbody1_body1_sync1_50000-50032"]),
        ("standard", "pb_learn_2000_bank192_binary1_body0_*cap3_*sync1_50000-50032", [f"pb_learn_2000_body0_{b}{t}", "plainB_2000_50000-50032"])]
for name, a, bs in rows:
    A = load(f(a))
    for bb in bs:
        B = load(f(bb)); m, (lo, hi) = paired(A, B)
        print(f"{name}: {efficiency(A):.2f} vs {bb[:28]} {efficiency(B):.2f}, {m:+.2f} [{lo:+.2f}, {hi:+.2f}]")

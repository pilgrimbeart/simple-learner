exec(open("/home/pilgrim/git/simple-learner/lab/gatepair.py").read().split("H = ")[0])
import glob, os
def f(pat):
    m = glob.glob(V + pat + ".lives"); assert len(m) == 1, (pat, m); return os.path.basename(m[0])[:-6]
b = "cal_every32_cal_fast12_cal_first0_cal_len8_"
for name, a, e in [
  ("lopsided", "pb_learn_2000_bank96_binary1_body1_*cap1_*sync1_50000-50032", f"pb_learn_2000_body1_{b}gate8_gate_rate1_stall0.05_stall_need3000_sync1_50000-50032"),
  ("allbody", "pb_learn_2000_allbody1_bank96_binary1_body1_*cap1_*sync1_50000-50032", f"pb_learn_2000_allbody1_body1_{b}gate8_gate_rate1_stall0.05_stall_need3000_sync1_50000-50032"),
  ("standard", "pb_learn_2000_bank96_binary1_body0_*cap1_*sync1_50000-50032", f"pb_learn_2000_body0_{b}gate8_gate_rate1_stall0.05_stall_need3000_sync1_50000-50032"),
  ("lopsided vs oracle", "pb_learn_2000_bank96_binary1_body1_*cap1_*sync1_50000-50032", "pb_oracle_2000_body1_sync1_50000-50032"),
  ("lopsided vs fixed", "pb_learn_2000_bank96_binary1_body1_*cap1_*sync1_50000-50032", "pb_fixed_2000_body1_sync1_50000-50032"),
  ("train old+sync vs old", "pb_learn_2000_bank96_binary1_body1_cal_every32_cal_len8_cap1_gate8_local1_stall0.05_stall_need3000_sync1_0-32", "pb_learn_2000_bank96_binary1_body1_cal_every32_cal_len8_gate8_local1_stall0.05_stall_need3000_0-32"),
  ("train old+early vs old", "pb_learn_2000_bank96_binary1_body1_cal_every32_cal_fast12_cal_first0_cal_len8_cap1_gate8_gate_rate1_local1_stall0.05_stall_need3000_0-32", "pb_learn_2000_bank96_binary1_body1_cal_every32_cal_len8_gate8_local1_stall0.05_stall_need3000_0-32")]:
    A, B = load(f(a)), load(f(e)); m, (lo, hi) = paired(A, B)
    print(f"{name}: {efficiency(A):.2f} vs {efficiency(B):.2f}, {m:+.2f} [{lo:+.2f}, {hi:+.2f}]")

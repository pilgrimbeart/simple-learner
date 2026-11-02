exec(open("/home/pilgrim/git/simple-learner/lab/gatepair.py").read().split("H = ")[0])
import glob, os
def f(pat):
    m = glob.glob(V + pat + ".lives"); assert len(m) == 1, (pat, m); return os.path.basename(m[0])[:-6]
b = "cal_every32_cal_fast12_cal_first0_cal_len8_"
ex = f"pb_learn_2000_body1_{b}gate8_gate_rate1_stall0.05_stall_need3000_sync1_50000-50032"
bank = f"pb_learn_2000_bank96_body1_{b}gate8_gate_rate1_local1_stall0.05_stall_need3000_sync1_50000-50032"
c = {k: f(f"pb_learn_2000_bank96_binary1_body1_*cap{k}_*sync1_50000-50032") for k in ("1", "3", "1000")}
for name, a, e in [("bank - exact", bank, ex), ("cap1000 - bank", c["1000"], bank), ("cap3 - bank", c["3"], bank),
                   ("cap1 - bank", c["1"], bank), ("cap1 - cap1000", c["1"], c["1000"]), ("cap3 - exact", c["3"], ex)]:
    A, B = load(a), load(e); m, (lo, hi) = paired(A, B)
    print(f"{name}: {efficiency(A):.2f} vs {efficiency(B):.2f}, {m:+.2f} [{lo:+.2f}, {hi:+.2f}]")

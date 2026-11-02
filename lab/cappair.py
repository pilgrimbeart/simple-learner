import sys; sys.argv=[sys.argv[0]]
exec(open("/home/pilgrim/git/simple-learner/lab/gatepair.py").read().split("H = ")[0])
import glob, os
def f(pat):
    m = [p for p in glob.glob(V + pat + ".lives")]; assert len(m) == 1, (pat, m); return os.path.basename(m[0])[:-6]
import sys as _s
H = _s.argv_h if hasattr(_s, "argv_h") else "0-32"
base = "cal_every32_cal_fast12_cal_first0_cal_len8_"
for pre in ["", "allbody1_"]:
    try: bank = f(f"pb_learn_2000_{pre}bank96_body1_{base}gate8_gate_rate1_local1_stall0.05_stall_need3000_sync1_{H}")
    except AssertionError: continue
    for c in ["1", "2", "1000"]:
        try: a = f(f"pb_learn_2000_{pre}bank96_binary1_body1_{base}cap{c}_gate8*sync1_{H}")
        except AssertionError: continue
        A, B = load(a), load(bank); m, (lo, hi) = paired(A, B)
        print(f"{pre}{H} cap{c} - bank: {efficiency(A):.2f} vs {efficiency(B):.2f}, {m:+.2f} [{lo:+.2f}, {hi:+.2f}]")

"""sepfast.py: the fast-input idea tested by hand: from the silicon-tuned sepb, bit's chain at K 4 (sepscale), the taste
and/or eye leaks f times faster with the gains reading them f times larger (a pulse's time past threshold goes as
the leak's time constant), judged held out with each substrate's noise."""
import sys, os, json
os.environ["ONLY"] = "q,qn,DQ,FL,QL"
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import sepscale
from minimal.spec import score, summary
from discrete.poison import show

if __name__ == "__main__":
    base = dict(sepscale.final)
    for name, ft, fe in (("taste x4", 4, 1), ("eyes x4", 1, 4), ("both x4", 4, 4), ("both x8", 8, 8)):
        p = dict(base)
        p["r_t"] = 20e9 / ft
        p["g_dq"], p["g_dqf"] = base["g_dq"] * ft, base["g_dqf"] * ft
        p["r_eye"] = base["r_eye"] / fe
        p["g_f"], p["g_p"] = base["g_f"] * fe, base["g_p"] * fe
        sepscale.final = p
        s = sepscale.scaled(4.0)
        for sub in ("silicon", "biology", "biology x2"):
            print(show(f"{name}, {sub}", summary(score([s], range(50000, 50032), substrate=sub)[0])), flush=True)

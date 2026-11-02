"""sepjudge.py [SEEDS] [k=v ...]: sepb's circuit judged as the minimal line judges (held out, mismatch, the worst of
silicon, biology and twice biology's noise), with each substrate's own measures."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from sepb import spec
from minimal.spec import score, summary, parts, JUDGED
from discrete.poison import show

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if "=" not in a]
    lo, hi = (int(x) for x in (args[0] if args else "50000:50032").split(":"))
    kw = {k: float(v) for k, v in (a.split("=") for a in sys.argv[1:] if "=" in a)}
    s, names = spec(**kw)
    print(parts(s))
    lives = score([s], range(lo, hi))[0]
    print(show("worst substrate", summary(lives)))
    for sb in JUDGED:
        print(show(sb, summary([l for l in lives if l.substrate == sb])))

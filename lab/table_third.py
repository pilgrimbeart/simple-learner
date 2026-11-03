"""table_third.py: the table's third round (lab/table_diag.py traced the costs; discrete/NOTEBOOK.md, D28).  python lab/table_third.py STEP ..."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import table as T
import table_fix as F
from table_fix import grid, SG


def digest():
    F.FIX["digest"] = [("learnpause3", grid(theta=[2.0, 3.0, 4.0], late=[0.0, 0.5, 1.0], down_on=[0.0, 0.25], margin=[1.2]), (100.0, 400.0))]
    F.row("digest")


def thrusters():
    F.FIX["thrusters"] = [("sweepsg2", [dict(SG, gate=g, debounce=d, need=n) for g in (10.0, 12.0) for d in (2.0, 3.0) for n in (100.0, 1000.0)], (1000.0,))]
    F.row("thrusters")


def ageing():
    F.FIX["ageing"] = [("jitterg2", grid(learn=[1.0], eta=[0.03, 0.06], sd=[0.15], gate=[10.0, 12.0, 14.0], win=[100.0, 200.0], born=[1.5]), (1000.0,))]
    F.row("ageing")


def digest2():
    F.FIX["digest"] = [("learnpause3", grid(vouch=[1.0], win=[1.2], theta=[2.0, 3.0], tau_p=[60.0, 150.0], off=[0.5, 1.0], late=[1.0], down_on=[0.0], mtop=[4.0], margin=[1.2]), (100.0, 400.0))]
    F.row("digest")


def thrusters2():
    F.FIX["thrusters"] = [("sweepsg2", [dict(SG, gate=g, debounce=2.0, need=100.0) for g in (13.0, 14.0, 15.0, 16.0)], (1000.0,))]
    F.row("thrusters")


def ageing2():
    F.FIX["ageing"] = [("jitterg2", grid(learn=[1.0], eta=[0.06], sd=[0.15], gate=[15.0, 16.0, 17.0, 18.0], win=[200.0, 400.0], born=[1.5]), (1000.0,))]
    F.row("ageing")


if __name__ == "__main__":
    for step in sys.argv[1:]:
        print(f"== {step}", flush=True)
        globals()[step]()

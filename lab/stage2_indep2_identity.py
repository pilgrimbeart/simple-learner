"""stage2_indep2_identity.py: identity re-run on the stage-2b engine (fresh seeds 64550-64599): the instrument of
lab/stage2_indep_identity.py (lockstep against creature.Life, every brain call and body state), unchanged.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage2_indep2_identity.py"""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import stage2_indep_identity as I

if __name__ == "__main__":
    lo, hi = 64550, 64600
    I.run([(k, s, c, 100.0, "(world)") for k in ("model", "circuit", "bank") for s in range(lo, hi) for c in ("red", "blue")], "no rule, 100 s")
    for text in ("(world (const DRAG 50.000001))", "(world (on pulse (if (chance 0.001) (drop))))"):
        I.run([("circuit", s, c, 100.0, text) for s in range(lo, lo + 10) for c in ("red", "blue")], f"mutant {text}")

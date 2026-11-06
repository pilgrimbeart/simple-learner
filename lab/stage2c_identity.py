"""stage2c_identity.py: stage 2c, part 4. With the switch off (sim.WLife.seconds = False) the engine is still creature.Life:
  identity   the checker's instrument (lab/stage2_indep_identity.py), no rule, seeds 66620-66669 x 2, block model, base circuit and bank,
             every brain call and the body's state after every tick; and its two mutants, which must differ
  repro      stage 2a's instrument (lab/stage2_repro.py) against the existing wrappers, seeds 66620-66639 x 2, base, bank and told, for
             every world whose text stage 2c left alone (unreliable, coin and nlate_pattern now lie per meal, rarefeast is written at the
             meal, so they are not the wrappers' any more; digest as 2b)

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage2c_identity.py > lab/v/stage2c_identity.log"""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
from stage2_lang import sim
sim.WLife.seconds = False                               # before the pool forks: every worker runs the legacy loop
import stage2_indep_identity as I
import stage2_repro as R

R.SEEDS = range(66620, 66640)

if __name__ == "__main__":
    with ProcessPoolExecutor(7) as ex:
        print("== identity, switch off, seeds 66620-66669 x 2", flush=True)
        I.run([(k, s, c, 100.0, "(world)") for k in ("model", "circuit", "bank") for s in range(66620, 66670) for c in ("red", "blue")], "no rule, 100 s", ex=ex)
        for text in ("(world (const DRAG 50.000001))", "(world (on pulse (if (chance 0.001) (drop))))"):
            I.run([("circuit", s, c, 100.0, text) for s in range(66620, 66630) for c in ("red", "blue")], f"mutant {text}", ex=ex)
        print("\n== reproduction against the wrappers, switch off, seeds 66620-66639 x 2", flush=True)
        n = 20
        ok = R.run([(None, "plain")], n, arms=("circuit", "bank"), label="identity", ex=ex)
        ok &= R.run([("plain", "plain"), ("late_never", "never")], n, label="identity", ex=ex)
        ok &= R.run([(w, w) for w in ("swap10", "alternate", "pattern", "patchy", "weak", "noisy")], n, label="nine", ex=ex)
        ok &= R.run([(w, w) for w in ("allfood", "scarce", "moving", "late_alternate_50", "late_swap_50")], n, label="bonus", ex=ex)
        ok &= R.run([("thrusters", "thrusters")], n, arms=("circuit",), label="bonus", ex=ex)
        print("ALL EXACT" if ok else "DIFFERENCES", flush=True)

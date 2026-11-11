"""dance0_confirm.py: D0's mended observer, frozen, on fresh seeds (PROGRAMME.md, How we work: forking paths). The analysis is
lab/dance0.py's report as committed after its mending (mutual information in 12 bins, the better of the ridge decoder and the physical
estimator, the fundamental by excess over all multiples); only the seeds change, 89000+ against 87000+.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/dance0_confirm.py [BODIES]"""
import pickle
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import dance0 as D
import stage3_random as R

SEEDS0 = 89000

if __name__ == "__main__":
    import ledger
    ledger.start()
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 600
    rows = []
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        for c in ["forage"] + list(D.CYCLES):
            rows += list(ex.map(D.job, [(c, s, ("red", "blue")[s % 2]) for s in range(SEEDS0, SEEDS0 + n)], chunksize=4))
    pickle.dump(rows, open(f"/home/pilgrim/git/simple-learner/lab/v/dance0_confirm_{n}.pkl", "wb"))
    D.report(rows)

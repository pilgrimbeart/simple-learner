"""stage2_finer_ref.py: is plain's move at 5 ms the language's or the old simulator's? The real creature.Life with the reference loop (stage2_repro.ref), the tick set to 5 ms in every module, against the engine at 5 ms on the same seeds: lives compared exactly."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import stage2_repro as R
import stage2_checks as C
from stage2_lang import worlds as WW


def one(job):
    w, arm, seed, c = job
    C.set_tick(0.005)
    a = R.ref((w, arm, seed, c, 100.0))
    b = R.lang_life((WW.W[w]["text"], arm, seed, c, 100.0))
    return R.same(a, b)


if __name__ == "__main__":
    jobs = [(w, arm, s, c) for w in ("plain", "digest", "swap10") for arm in ("circuit", "bank") for s in range(63100, 63105) for c in ("red", "blue")]
    with ProcessPoolExecutor(7) as ex:
        res = list(ex.map(one, jobs))
    print(f"at 5 ms, the real Life and the engine: {sum(ok for ok, _ in res)}/{len(res)} lives exact" + ("" if all(ok for ok, _ in res) else f"; first: {next(w for ok, w in res if not ok)}"))

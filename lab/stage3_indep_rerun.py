"""stage3_indep_rerun.py: the independent check of stage 3 re-lives a handful of saved lives exactly as lab/stage3_random.py and
lab/stage3_more.py did (their own `one` and `live`, the same _init), and compares with the saved numbers. Saved seeds only. Two
worker processes.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage3_indep_rerun.py > lab/v/stage3_indep_rerun.log"""
import pickle
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import stage3_random as R
import stage3_more as M

D = "/home/pilgrim/nca-scratch-backup/stage3/"


def jobs():
    W, _, _ = R.worlds()
    main, ref, T, Lg = (pickle.load(open(D + k + ".pkl", "rb")) for k in ("main", "ref", "more_topup", "more_long"))
    out = []   # (label, dt, fn, job, saved)
    for n in ("g144", "g352", "g397"):
        t = W[n][0]
        for si, s in ((0, 80100), (59, 80159)):
            for c, col in enumerate(R.COL):
                for k, arm in (("base", "circuit"), ("bank", "bank"), ("told", R.told_arm(t))):
                    out.append((f"main {n} {k} {s} {col}", 0.00125, "one", (t, arm, s, col), main[n][k][2 * si + c][:2]))
    t = W["g352"][0]
    for si, s in ((0, 80500), (239, 80739)):
        for c, col in enumerate(R.COL):
            for k, arm in (("base", "circuit"), ("bank", "bank"), ("told", R.told_arm(t))):
                out.append((f"topup g352 {k} {s} {col}", 0.00125, "live", (t, arm, s, col, 100.0), T["g352"][k][2 * si + c][:2]))
    for c, col in enumerate(R.COL):
        out.append((f"ref g352 80100 {col} (2.5 ms)", 0.0025, "one", (t, "ref", 80100, col), ref["g352"][c][:2]))
        out.append((f"topup-ref g352 80500 {col} (2.5 ms)", 0.0025, "live", (t, "ref", 80500, col, 100.0), T["g352"]["ref"][c][:2]))
    t = W["g261"][0]
    out.append(("long g261 bank 81000 red (1000 s)", 0.00125, "live", (t, "bank", 81000, "red", 1000.0), Lg["g261"]["bank"][0]))
    return out


def run(item):
    label, dt, fn, job, saved = item
    from stage2_lang import sim
    assert abs(sim.WLife.dt - dt) < 1e-15
    r = (R.one if fn == "one" else M.live)(job)
    got = tuple(r[:4]) if fn == "live" and len(saved) == 4 else tuple(r[:2])
    return label, got, tuple(saved)


if __name__ == "__main__":
    J = jobs()
    same = 0
    for dt in (0.00125, 0.0025):          # one pool per step, each initialised once as the producer's were
        with ProcessPoolExecutor(2, initializer=R._init, initargs=(dt, False)) as ex:
            for label, got, saved in ex.map(run, [j for j in J if j[1] == dt]):
                ok = got == saved
                same += ok
                print(f"{'SAME' if ok else 'DIFF'}  {label:40s} re-run {got}  saved {saved}", flush=True)
    print(f"{same} of {len(J)} identical")

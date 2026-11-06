"""stage2_indep_digest.py: digest's two meals that disagreed with the description (lab/v/stage2_indep_worlds.log):
is it a meal exactly 1 s (100 ticks) after the last, judged by t - was < 1 in floating point? Every meal at a gap of
exactly 100 ticks, with the engine's verdict on its timing.

    .venv/bin/python lab/stage2_indep_digest.py"""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import stage2_indep_worlds as IW


def one(job):
    L = IW.one(job)
    rows = IW.meal_rows(L)
    out = []
    for (t0, *_), (t, c, bad, single) in zip(rows, rows[1:]):
        if t - t0 == 100 and c != L["P"]:
            out.append((L["seed"], L["first"], t0, t, bad, (t * 0.01 - t0 * 0.01) < 1))
    return out


if __name__ == "__main__":
    jobs = [("digest", k, s, c) for k in ("circuit", "bank") for s in range(64100, 64150) for c in IW.COL]
    with ProcessPoolExecutor(7) as ex:
        R = [x for r in ex.map(one, jobs, chunksize=2) for x in r]
    print(f"food-coloured meals exactly 100 ticks after the last meal: {len(R)}; judged bad: {sum(r[4] for r in R)};"
          f" of them, t*0.01 - was*0.01 < 1 in floating point: {sum(r[5] for r in R)}; bad iff that: {all(r[4] == r[5] for r in R)}")
    for r in R:
        print("  ", r)

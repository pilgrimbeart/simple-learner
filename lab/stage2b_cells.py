"""stage2b_cells.py: stage 2b, part 3: why the bank collapses in cells (D33: -41.6, sigma 93). Seeds 65070-65079 x 2, base and bank, traced.

Per life: meals, bad meals, firings, energy spent and gained, efficiency; how many meals were of the block eaten the tick before (a block
respawned in place, under the mouth); the longest run of ticks with a meal; and the same in plain and in cells with its respawn rule
replaced by the exclusion zone's (a block can't come back within 3 EAT + BODY of the creature), to test the cause.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage2b_cells.py > lab/v/stage2b_cells.log"""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from minimal.spec import COST, spent
from stage2_lang import arms as S, worlds as WW

SEEDS = range(65070, 65080)
CELLS = WW.W["cells"]["text"]
# the same world, an eaten block sent back to its cell only if that's clear of the creature, else left hidden until the next step
CELLS_CLEAR = CELLS.replace("(on respawn (set nx (bx block)) (set ny (by block)))",
                            "(on respawn (set nx (bx block)) (set ny (by block)) (if (< (dist nx ny) (+ (* 3 EAT) BODY)) (do (hide block) (put now block 0))))")


def life(job):
    text, arm, seed, first = job
    lf = S.make(S.world_of(text), arm, seed, first, trace=True)
    l = S.live(lf)
    m = lf.tr.meals                                     # (tick, colour, bad, amount, block, sign)
    same = sum(1 for a, b in zip(m, m[1:]) if b[4] == a[4] and b[0] - a[0] <= 1)
    ticks = sorted(set(x[0] for x in m))
    run = best = 0
    for a, b in zip(ticks, ticks[1:]):
        run = run + 1 if b == a + 1 else 0
        best = max(best, run)
    gain = sum(a - COST * b for a, b, _ in l)
    return dict(meals=len(m), bad=sum(x[2] for x in m), firings=len(lf.firings), gain=gain, spent=spent(l), same=same, run=best + 1 if ticks else 0)


def show(label, R):
    g, s = np.array([r["gain"] for r in R]), np.array([r["spent"] for r in R])
    print(f"  {label}: efficiency {g.sum() / s.sum():+.2f}; per life meals {np.mean([r['meals'] for r in R]):.0f} (max {max(r['meals'] for r in R)}),"
          f" bad {np.mean([r['bad'] for r in R]):.0f}, firings {np.mean([r['firings'] for r in R]):.0f}, spent {s.mean():.1f}, gain {g.mean():+.1f};"
          f" meals of the block eaten the tick before {np.mean([r['same'] for r in R]):.0f} a life; longest run of ticks with a meal, median {np.median([r['run'] for r in R]):.0f}, max {max(r['run'] for r in R)}", flush=True)
    worst = sorted(R, key=lambda r: r["gain"])[:3]
    print("     worst lives: " + "; ".join(f"meals {r['meals']} bad {r['bad']} same-block {r['same']} run {r['run']} gain {r['gain']:+.0f} spent {r['spent']:.1f}" for r in worst), flush=True)


if __name__ == "__main__":
    with ProcessPoolExecutor(7) as ex:
        for wname, text in (("plain", "(world)"), ("cells", CELLS), ("cells, respawn kept clear of the creature", CELLS_CLEAR)):
            print(f"== {wname}, seeds {SEEDS.start}-{SEEDS.stop - 1} x 2", flush=True)
            for arm in ("circuit", "bank"):
                show(arm, list(ex.map(life, [(text, arm, s, c) for s in SEEDS for c in S.COL])))

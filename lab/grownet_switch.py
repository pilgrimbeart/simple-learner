"""grownet_switch.py: stage 3 of the growing network (PROGRAMME.md): the hidden word changes mid-life. Do the old blocks fade, freeing
material for the new word? Predictions: lab/v/grownet_predictions.md, R5 and R6.

World: the sequence ladder's rung N, with a second word (drawn per life, its first two letters the other way round) replacing the first
at a moment drawn uniformly in 500 to 700 s; the control, the same rung unchanged. Arms circuit (the starting brain), tree, net, nonet
(teach.py's), P material, 1500 s lives scored on their last third, paired.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/grownet_switch.py [PAIRS] [N] [Ps, e.g. 32,64] [s85000]"""
import pickle
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import ladders as L
import stage3_random as R
import teach as T

SECS = 1500.0
import os
ARMS = tuple(os.environ.get("ARMS", "circuit,tree,net,nonet").split(","))   # ARMS=circuit,tree,net,netnf,netnd for the ablation (R7)


def switched(n):
    return (f"(world (meta (link L7) (q D) (cap Ladder) (group seq)) (let i (int {n})) (let k 0) (table w {n} 1 (int 2)) (table v {n} 1 (int 2))"
            f" (on birth (put w 0 0) (put w 1 1) (put v 0 1) (put v 1 0) (after (uniform 500 700) (set k 1)))"
            f" (on tick (set poison (if (= (if (= k 0) (at w i) (at v i)) 0) P F)))"
            f" (on score (if (= colour (if (= (if (= k 0) (at w i) (at v i)) 0) F P)) (set i (mod (+ i 1) {n})))))")


def aba(n):
    """Pattern A, then B (at 400 to 500 s), then A again (at 900 to 1000 s): does the brain remember A when it returns?"""
    return (f"(world (meta (link L7) (q D) (cap Ladder) (group seq)) (let i (int {n})) (let k 0) (table w {n} 1 (int 2)) (table v {n} 1 (int 2))"
            f" (on birth (put w 0 0) (put w 1 1) (put v 0 1) (put v 1 0) (after (uniform 400 500) (set k 1)) (after (uniform 900 1000) (set k 0)))"
            f" (on tick (set poison (if (= (if (= k 0) (at w i) (at v i)) 0) P F)))"
            f" (on score (if (= colour (if (= (if (= k 0) (at w i) (at v i)) 0) F P)) (set i (mod (+ i 1) {n})))))")


if __name__ == "__main__":
    a = sys.argv[1:]
    n = int(a[0]) if a and a[0].isdigit() else 10
    N = int(a[1]) if len(a) > 1 else 11
    Ps = tuple(int(x) for x in a[2].split(",")) if len(a) > 2 and "," in a[2] or (len(a) > 2 and a[2].isdigit()) else (32, 64)
    PA = {x.split(":")[0]: int(x.split(":")[1]) for x in os.environ.get("PARM", "").split(",") if ":" in x}   # an arm's own material
    s0 = next((int(x[1:]) for x in a if x.startswith("s") and x[1:].isdigit()), 85000)
    out = f"/home/pilgrim/git/simple-learner/lab/v/grownet_switch_{N}_{n}_s{s0}_{'-'.join(ARMS)}.pkl"
    worlds = {w: x for w, x in {"unchanged": L.seq(N), "changed": switched(N), "aba": aba(N)}.items() if w in os.environ.get("WORLDS", "unchanged,changed").split(",")}
    if "report" not in a:
        import ledger
        ledger.start()
        jobs = [(w, arm, P, s, c) for w in worlds for P in Ps for arm in ARMS for s in range(s0, s0 + n) for c in L.COL]
        with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
            res = list(ex.map(T.job, [(worlds[w], arm, PA.get(arm, P), s, c, SECS) for w, arm, P, s, c in jobs], chunksize=2))
        pickle.dump(list(zip(jobs, res)), open(out, "wb"))
    rows = pickle.load(open(out, "rb"))
    I = R.boot(n)
    print(f"== the hidden word changes mid-life: seq {N}, a new word at 500 to 700 s; {n} pairs, {SECS:.0f} s, last third, paired [95%]")
    for w in worlds:
        for P in Ps:
            e = {arm: L.scored([r for (ww, aa, pp, _, _), r in rows if ww == w and aa == arm and pp == P], SECS, I) for arm in ARMS}
            line = f"  {w:9s} P{P:<3d} circuit {e['circuit'][0]:+.2f}"
            for arm in ARMS[1:]:
                line += f" | {arm} {e[arm][0]:+.2f}"
            ref = "net" if "net" in ARMS else ARMS[-1]
            for x, y in [(ref, y) for y in ARMS if y not in ("circuit", ref)]:
                d = e[x][1] - e[y][1]
                line += f" | {x}-{y} {e[x][0] - e[y][0]:+.2f} [{np.percentile(d, 2.5):+.2f},{np.percentile(d, 97.5):+.2f}]"
            nn = [r[6] for (ww, aa, pp, _, _), r in rows if ww == w and aa == "net" and pp == P] or [(0, 0, 0, 0, 0)]
            line += f" | net blocks {int(np.median([x[1] for x in nn]))} faded {int(np.median([x[3] for x in nn]))} dup {int(np.median([x[4] for x in nn]))}"
            print(line, flush=True)

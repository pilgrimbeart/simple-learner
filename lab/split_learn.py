"""split_learn.py: how fast split.py's map is learned: when the counter last takes the right sign for good, and how
long it is wrong or unknown, per life (held out)."""
import sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import split as SP


def life(job):
    from discrete import model as M
    d, seed, poison = job
    lf = SP.SplitLife(seed, poison, brain=lambda s: None)
    food = lf.sensor[next(c for c in lf.sensor if c != poison)]
    p, sd = M.from_bench(); q = M.drawn(p, sd, seed); q["V_H"] = 99.0
    br = SP.SplitB(seed, q, d); br.food = food
    br.toward = {lf.hw[0]: lf.motor["right"], lf.hw[1]: lf.motor["left"]}
    lf.brain = br
    right = 1 if br.toward[0] == 0 else -1
    state = []
    while lf.t < 10000:
        lf.step()
        if lf.t % 10 == 0:
            state.append(np.sign(br.k) * right)
    s = np.array(state)
    bad = np.flatnonzero(s <= 0)
    settle = 0.0 if not len(bad) else (bad[-1] + 1) * 0.1
    return settle, np.mean(s == 0), np.mean(s < 0)


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    d = {k: (v if k == "map" else float(v)) for k, v in (x.split("=") for x in sys.argv[1].split(",") if x)}
    with ProcessPoolExecutor(7) as ex:
        R = np.array(list(ex.map(life, [(d, s, c) for s in range(*map(int, (sys.argv[2] if len(sys.argv) > 2 else "0:64").split(":"))) for c in ("red", "blue")])))
    print(f"settled right for good by: median {np.median(R[:, 0]):.1f} s, quartiles {np.percentile(R[:, 0], 25):.1f}"
          f" / {np.percentile(R[:, 0], 75):.1f} s, never (wrong at the end) {np.mean(R[:, 0] >= 99.9):.0%};"
          f" time unknown {R[:, 1].mean():.0%}, wrong {R[:, 2].mean():.0%}")

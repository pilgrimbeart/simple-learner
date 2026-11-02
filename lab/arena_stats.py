import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from arena import Arena
from units import TICK

def run(seed):
    A = Arena(seed, 4)
    for _ in range(int(1000 / TICK)):
        A.step()
    out = []
    for r, died in [(r, A.t) for r in A.robots] + A.dead:
        age = died - r.born
        if age > 20:
            out.append((r.brain.food == r.sensor["blue"], r.ate / age * 10, r.lost / age * 10, age, died < A.t))
    return out

if __name__ == "__main__":
    with ProcessPoolExecutor() as ex:
        rows = [x for res in ex.map(run, range(16)) for x in res]
    rows = np.array(rows, float)
    for right in (1, 0):
        s = rows[rows[:, 0] == right]
        print(f"believes {'blue (right)' if right else 'red (wrong)'}: {len(s)} robots, ate {s[:,1].mean():.2f} per 10 s, "
              f"lost {s[:,2].mean():.2f} per 10 s, age {s[:,3].mean():.0f} s")

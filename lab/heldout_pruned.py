"""learn_avoid with the pruning's cuts, judged held out (seeds 50000-50039, red then blue as poison)."""
import pickle, sys
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from discrete.prune import _one
from discrete.poison import show
from minimal.spec import summary

S = sys.argv[1]
for n, cuts in ((46, [(44, "short"), (43, "open")]), (45, [(44, "short"), (43, "open"), (30, "open")])):
    with ProcessPoolExecutor(8) as ex:
        lives = list(ex.map(_one, [("learn_avoid", {}, cuts, s, 100.0, None, None, c)
                                   for s in range(50000, 50040) for c in ("red", "blue")]))
    bad = [i for i, l in enumerate(lives) if l is None]
    print(n, "parts, failed lives:", bad, flush=True)
    lives = [l for l in lives if l is not None]
    print(show(f"learn_avoid_{n}", summary(lives)), flush=True)
    pickle.dump(lives, open(f"{S}/pruned_{n}.lives", "wb"))

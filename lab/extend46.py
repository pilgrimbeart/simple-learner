"""The 46-part learn_avoid on 40 more held-out seeds (50040-50079)."""
import pickle, sys
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from discrete.prune import _one
from discrete.poison import show
from minimal.spec import summary
S = sys.argv[1]
cuts = [(44, "short"), (43, "open")]
with ProcessPoolExecutor(8) as ex:
    lives = list(ex.map(_one, [("learn_avoid", {}, cuts, s, 100.0, None, None, c)
                               for s in range(50040, 50080) for c in ("red", "blue")]))
print("failed:", [i for i, l in enumerate(lives) if l is None])
pickle.dump(lives, open(f"{S}/avoid46_more.lives", "wb"))
first = pickle.load(open(f"{S}/avoid46.lives", "rb"))
print(show("learn_avoid_46, 50040-50079", summary(lives)))
print(show("learn_avoid_46, 50000-50079", summary(first + lives)))
print("stranded:", [(50000 + i // 2, ("red", "blue")[i % 2]) for i, l in enumerate(first + lives) if l[2][0] == 0])

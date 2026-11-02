"""sparse.py N [tuner args]: discrete.tuner in a world of N blocks of each colour (world.BLOCKS, 18 normally): sparser
meals (QUESTIONS step 2's open: does one fixed tuner rate survive?). Workers fork, so inherit the patch."""
import sys, os, pickle, multiprocessing
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
multiprocessing.set_start_method("fork")
import world
world.BLOCKS = int(sys.argv.pop(1))
from discrete import tuner, model as M
from discrete.poison import show
from minimal.spec import summary
args = [a for a in sys.argv[1:] if "=" not in a]
lo, hi = (int(x) for x in (args[0] if args else "50000:50032").split(":"))
kw = {k: float(v) for k, v in (a.split("=") for a in sys.argv[1:] if "=" in a)}
seconds = kw.pop("seconds", 10000.0)
p, spread = M.from_bench()
L = tuner.lives(dict(p, **kw), spread, range(lo, hi), seconds)
print(show(f"tuner blocks {world.BLOCKS} {kw} {lo}:{hi}", summary(L)), flush=True)
pickle.dump(L, open(os.path.join(os.environ["LIVES"], f"tuner_b{world.BLOCKS}" + "".join(
    f"_{k}{v:g}" for k, v in sorted(kw.items())) + f"_{lo}-{hi}.lives"), "wb"))

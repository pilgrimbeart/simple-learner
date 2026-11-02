"""sepsearch2.py GENS [substrate ...]: D14's robustness, structure and size together: sepb from the silicon-tuned
design with the bit's chain (bit, its copy, doubt, flip) at four times the capacitance and current (sepscale), its
knobs and the inputs' leaks (taste r_t, eyes r_eye, down to 1 GOhm: an input node's resting noise falls with its time
constant while a pulse that nearly fills it keeps its peak) polished by CMA-ES, judged by the worst of the
substrates; then held out."""
import sys, json, os
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
os.environ["ONLY"] = "q,qn,DQ,FL,QL"
import minimal.spec
import sepscale
from sepsearch import PARAMS as P0

G = 1e9
start = json.load(open("/home/pilgrim/git/simple-learner/lab/v/sep_search_silicon.json"))["final"]
PARAMS = {k: (start[k], lo, hi) for k, (_, lo, hi) in P0.items()}
PARAMS["r_eye"] = (start["r_eye"], 1 * G, 74 * G)
PARAMS["r_t"] = (20 * G, 1 * G, 74 * G)
K = 4.0


def build(p):
    sepscale.final = {**start, **p}
    return sepscale.scaled(K)


if __name__ == "__main__":
    gens = int(sys.argv[1])
    minimal.spec.JUDGED = tuple(sys.argv[2:]) or ("silicon",)
    from minimal.search import cmaes
    from minimal.spec import score, summary, parts
    from discrete.poison import show
    final, best, hist = cmaes(build, PARAMS, gens, 16, 8, by="efficiency", log=lambda s: print(s, flush=True))
    json.dump({"final": final, "best": best[1], "history": hist}, open(
        "/home/pilgrim/git/simple-learner/lab/v/sep_search2_" + "_".join(s.replace(" ", "") for s in minimal.spec.JUDGED) + ".json", "w"), indent=1)
    s = build(final)
    print(final)
    print(parts(s))
    for sub in ("silicon", "biology", "biology x2"):
        print(show(f"held out, {sub}", summary(score([s], range(50000, 50032), substrate=sub)[0])), flush=True)

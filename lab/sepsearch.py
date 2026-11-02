"""sepsearch.py GENS [substrate ...]: sepb's knobs polished by minimal.search's CMA-ES, by efficiency, on fresh seeds
each generation (from 10000), judged with those substrates' noise (default silicon); then judged held out."""
import sys, json
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import minimal.spec
from sepb import spec

n_, G = 1e-9, 1e9
PARAMS = {  # name: (start, lo, hi)
    "r_hd": (74 * G, 20 * G, 74 * G), "g_f": (0.15 * n_, 0.03 * n_, 0.6 * n_), "g_p": (0.3 * n_, 0.05 * n_, 1.2 * n_),
    "v_bored": (-0.40, -0.75, -0.1), "tau_xs": (0.25, 0.08, 0.8), "tau_xd": (0.055, 0.02, 0.15),
    "g_xp": (0.36 * n_, 0.1 * n_, 1.0 * n_), "g_xs": (0.7 * n_, 0.2 * n_, 2.0 * n_), "g_xd": (1.0 * n_, 0.3 * n_, 1.2 * n_),
    "g_mb": (0.25 * n_, 0.06 * n_, 0.6 * n_), "g_dq": (0.03 * n_, 0.01 * n_, 0.1 * n_),
    "g_dqf": (0.03 * n_, 0.01 * n_, 0.1 * n_), "v_h": (0.576, 0.2, 0.85), "v_l": (-0.705, -0.85, -0.3),
    "r_eye": (20 * G, 5 * G, 74 * G), "g_bt": (0.4 * n_, 0.1 * n_, 1.2 * n_), "g_dor": (0.06 * n_, 0.02 * n_, 0.2 * n_)}

if __name__ == "__main__":
    gens = int(sys.argv[1])
    minimal.spec.JUDGED = tuple(sys.argv[2:]) or ("silicon",)
    from minimal.search import cmaes
    from minimal.spec import score, summary, parts
    from discrete.poison import show
    final, best, hist = cmaes(lambda p: spec(**p)[0], PARAMS, gens, 16, 8, by="efficiency",
                              log=lambda s: print(s, flush=True))
    json.dump({"final": final, "best": best[1], "history": hist}, open(
        "/home/pilgrim/git/simple-learner/lab/v/sep_search_" + "_".join(s.replace(" ", "") for s in minimal.spec.JUDGED) + ".json", "w"), indent=1)
    s = spec(**final)[0]
    print(parts(s))
    for sub in ("silicon", "biology", "biology x2"):
        print(show(f"held out, {sub}", summary(score([s], range(50000, 50032), substrate=sub)[0])), flush=True)

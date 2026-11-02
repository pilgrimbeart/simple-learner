"""Held-out validation (seeds 100-163, all three substrates) of evolve_30's circuits of 26-36 parts, with HR_31p_pol and its pruning as references."""
import json, os, sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from minimal import spec as S
HERE = os.path.dirname(os.path.abspath(__file__))
if __name__ == "__main__":
    d = json.load(open("/home/pilgrim/git/simple-learner/minimal/results/evolve_30.json"))
    cands = {}
    for key in ("archive", "best_efficiency", "best_gain"):
        for k, (v, s) in d.get(key, {}).items():
            if 26 <= int(k) <= 36:
                cands.setdefault(json.dumps(s, sort_keys=True), (f"{key}_{k}", s))
    for ref in ("HR_31p_pol", "HR_31p_pol_pruned"):
        s = json.load(open(f"/home/pilgrim/git/simple-learner/minimal/results/{ref}.json"))["spec"]
        cands[json.dumps(s, sort_keys=True)] = (ref, s)
    names = [n for n, _ in cands.values()]
    specs = [s for _, s in cands.values()]
    for name, s, lives in zip(names, specs, S.score(specs, seeds=range(100, 164))):
        v = S.summary(lives)
        print(f"{name}: {S.parts(s)['total']} parts, score {v['net']:+.2f} [{v['lo']:+.2f}, {v['hi']:+.2f}], food {v['food']:.2f},"
              f" eff {v['efficiency']:.2f}, gain {v['gain']:.2f}, stranded {v['stranded']:.0%}"
              f" {[round(x, 3) for x in v['ci']['stranded']]}, job {v['job']}; "
              + "; ".join(f"{k} str {w['stranded']:.0%}" for k, w in v['by_substrate'].items()), flush=True)
        json.dump({"design": name, "spec": s}, open(os.path.join(HERE, f"e30_{name}.json"), "w"))

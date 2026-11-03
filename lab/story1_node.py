"""story1_node.py: the pilot story re-validated in the node-and-element simulator (mixed_feedback.py), silicon's noise
only: D14's tuned B at Sepulchre's level (lab/sepb.py), as it is; unwired (either eye charges the hold, no learning);
fixed (no learning: the lives whose bit happens right are told's, the others wrong's); and the circuit, doubt written
only while the hold is up (its two writes gated by HD), with doubt's numbers set so that an unbacked bit flips on one
vouched poison and a backed one on two.

    python lab/story1_node.py try [k=v ...]            # a quick look, training seeds
    python lab/story1_node.py tune GENS                # doubt's numbers polished, fresh seeds each generation
    python lab/story1_node.py judge                    # the final judgement, seeds 50200-50327 x 2"""
import copy, json, sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import numpy as np
import minimal.spec
from sepb import spec
minimal.spec.JUDGED = ("silicon",)
from minimal.spec import score, summary, parts, violations, efficiency, gain, interval, one
from discrete.poison import show

ROOT = "/home/pilgrim/git/simple-learner/lab/v/"
FINAL = json.load(open(ROOT + "sep_search_silicon.json"))["final"]
n_ = 1e-9
START = dict(g_dq=3.5e-11, g_dqf=3.5e-11, v_h=0.30, v_l=-0.35)
PARAMS = {"g_dq": (3.5e-11, 1e-11, 1.5e-10), "g_dqf": (3.5e-11, 1e-11, 1.5e-10), "v_h": (0.30, 0.0, 0.7),
          "v_l": (-0.35, -0.7, 0.0)}


def circuit(limit=True, **k):
    s, names = spec(**{**FINAL, **START, **{a: b for a, b in k.items() if a not in ("g_rt", "v_back")}})
    s = copy.deepcopy(s)
    DQ0, T0, HD0 = names.index("DQ"), names.index("T"), names.index("HD")
    for e in s["elements"]:
        if e[0] == DQ0 and e[1] == T0:
            e[2] = HD0                                  # a taste writes doubt only while the hold is up
    if limit:
        s = limited(s, names, **{a: k[a] for a in ("g_rt", "v_back") if a in k})
    return s


G_RT, C_RT, R_RT, G_RP, G_RR, G_BR, V_BACK = 8e-12, 5e-12, 74e9, 3e-11, 2e-10, 3e-10, 0.1


def limited(s, names, g_rt=G_RT, v_back=V_BACK):
    """The run's limit as elements: a slow node RT charged only while bored (BT below its level), so while running; past
    0 V it latches by its own positive feedback and lifts boredom's node to about where a drive leaves it (v_back), which
    ends the run, resets RT, and starts boredom's wait again, so the creature scans (lab/story1.py, RunLimit)."""
    s = copy.deepcopy(s)
    BT = names.index("BT")
    level = next(e[4] for e in s["elements"] if e[1] == BT and e[5] < 0)
    RT = len(s["nodes"])
    s["nodes"].append(["RT", -0.6 / R_RT, R_RT, C_RT, None, None, None, False])
    s["elements"] += [[RT, BT, -1, g_rt, level, -20.0, 0.0, True],       # charged while running
                      [RT, RT, -1, G_RP, 0.0, 20.0, 0.0, True],          # past 0 V it latches
                      [RT, BT, -1, -G_RR, v_back, 20.0, 0.0, True],      # until boredom's node is back up
                      [BT, RT, -1, G_BR, 0.0, 20.0, 0.0, True]]          # which it lifts
    return s


def unlearning(s, names):
    """No learning: taste's two writes to doubt taken away."""
    DQ, T = names.index("DQ"), names.index("T")
    s["elements"] = [e for e in s["elements"] if not (e[0] == DQ and e[1] == T)]
    return s


def unwired():
    s, names = spec(**FINAL)
    s = limited(unlearning(copy.deepcopy(s), names), names)
    HD, q, qn, S0, S1 = (names.index(x) for x in ("HD", "q", "qn", "S0", "S1"))
    s["elements"] = [e for e in s["elements"] if not (e[0] == HD and e[3] < 0)]   # (nothing empties the hold)
    for e in s["elements"]:
        if e[0] == HD and e[1] == qn:
            e[1] = q                                    # either eye charges it
    return s


def fixed():
    s, names = spec(**FINAL)
    return limited(unlearning(copy.deepcopy(s), names), names)


def right_lives(L, seeds):
    """Of a fixed bit's paired lives, those whose bit happens right: S0 is food, so poison is on sensor 1."""
    from creature import Life
    from discrete.model import Model
    R = []
    for i, seed in enumerate(seeds):
        for j, c in enumerate(("red", "blue")):
            lf = Life(seed, c, brain=lambda s: Model(s, {"V_L": 0.0}))
            if lf.sensor[c] == 1:
                R += [L[2 * i + j]] * 2
    return R


def paired(A, B, f=efficiency, boot=2000):
    rng = np.random.default_rng(0)
    n = len(A) // 2
    d = []
    for _ in range(boot):
        k = rng.integers(0, n, n)
        d.append(f([l for i in k for l in (A[2 * i], A[2 * i + 1])]) - f([l for i in k for l in (B[2 * i], B[2 * i + 1])]))
    return f(A) - f(B), interval(d)


if __name__ == "__main__":
    cmd = sys.argv[1]
    kw = {a.split("=")[0]: float(a.split("=")[1]) for a in sys.argv[2:] if "=" in a}
    if cmd == "try":
        seeds = range(0, 32)
        tuned = json.load(open(ROOT + "story1_node.json"))["final"]
        print(show("no limit", summary(score([circuit(limit=False, **tuned)], seeds, substrate="silicon")[0])), flush=True)
        s = circuit(**{**tuned, **kw})
        print("violations", violations(s), "parts", parts(s))
        print(show("circuit", summary(score([s], seeds, substrate="silicon")[0])), flush=True)
    elif cmd == "tune":
        from minimal.search import cmaes
        gens = int(sys.argv[2])
        final, best, hist = cmaes(lambda p: circuit(**p), PARAMS, gens, 16, 8, by="efficiency", log=lambda m: print(m, flush=True))
        json.dump({"final": final, "best": best[1], "history": hist}, open(ROOT + "story1_node.json", "w"), indent=1)
        print(final)
    elif cmd == "judge":
        seeds = range(50200, 50328)
        tuned = json.load(open(ROOT + "story1_node.json"))["final"]
        sp = {"unwired": unwired(), "fixed": fixed(), "B": limited(*spec(**FINAL)), "circuit": circuit(**tuned)}
        R = {}
        for n, s in sp.items():
            print(n, "parts", parts(s), "violations", violations(s), flush=True)
            R[n] = score([s], seeds, substrate="silicon")[0]
        R["told"] = right_lives(R.pop("fixed"), seeds)
        for n in R:
            print(show(n, summary(R[n])), flush=True)
        for a, b in (("circuit", "B"), ("circuit", "unwired")):
            for lab, f in (("efficiency", efficiency), ("gain", gain)):
                d, i = paired(R[a], R[b], f)
                print(f"{a} - {b} {lab}: {d:+.2f} [{i[0]:+.2f}, {i[1]:+.2f}]", flush=True)

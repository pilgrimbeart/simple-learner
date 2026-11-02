import json, sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from minimal import spec as S
if __name__ == "__main__":
    s = json.load(open(sys.argv[1]))["spec"]
    a = int(sys.argv[2])
    v = S.summary(S.score([s], seeds=range(a, a + 64))[0])
    print(f"fresh seeds {a}-{a + 63}: score {v['net']:+.2f} [{v['lo']:+.2f}, {v['hi']:+.2f}], food {v['food']:.2f}, efficiency"
          f" {v['efficiency']:.2f} {[round(x, 2) for x in v['ci']['efficiency']]}, gain {v['gain']:.2f}"
          f" {[round(x, 2) for x in v['ci']['gain']]}, stranded {v['stranded']:.0%} {[round(x, 3) for x in v['ci']['stranded']]},"
          f" job {v['job']}")
    for k, w in v["by_substrate"].items():
        print(f"  {k}: score {w['net']:+.2f}, efficiency {w['efficiency']:.2f}, stranded {w['stranded']:.0%}, job {w['job']}")

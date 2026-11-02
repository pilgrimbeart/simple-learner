import sys, json, pickle
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from sepb import spec
from minimal.spec import score
if __name__ == "__main__":
    s = spec(**json.load(open("/home/pilgrim/git/simple-learner/lab/v/sep_search.json"))["final"])[0]
    json.dump(s, open("/home/pilgrim/git/simple-learner/lab/v/sepB_tuned_spec.json", "w"))
    L = score([s], range(50000, 50032), substrate="silicon")[0]
    pickle.dump(L, open("/home/pilgrim/git/simple-learner/lab/v/sepB.lives", "wb"))

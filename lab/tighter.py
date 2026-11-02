import sys, json, pickle
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import discrete.life as life
life.ACCURACY = ".options trtol=1 reltol=1e-5"
from discrete.judge import judge, HELD_OUT
r = json.load(open("discrete/results/hold_drive_tuned.json"))
j = judge("hold_drive", r["best"], [], range(HELD_OUT, HELD_OUT + 32), 100.0)
print(f"reltol 1e-5: efficiency {j['efficiency']:.2f} {j['eff_ci']} gain {j['gain']:.2f} firings {j['firings']:.0f} power {j['power']*1e9:.0f} nW")
pickle.dump(j["all"], open("discrete/results/hold_drive_tuned_reltol5.lives", "wb"))

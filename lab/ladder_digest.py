"""ladder_digest.py: the digest test, training seeds (lab/ladder.py)."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from ladder import run, line
S = range(0, 64)
for arm, kw in [("circuit", {}), ("told", {}), ("pause", dict(told=1.0, pause=1.0)), ("pause", dict(told=1.0, pause=0.8)), ("pause", dict(told=1.0, pause=1.2)), ("pause", dict(told=1.0, pause=1.5)), ("pause", dict(pause=1.0)), ("learnpause", {}), ("learnpause", dict(theta=5.0)), ("learnpause", dict(down=0.5))]:
    line(f"digest {arm} {kw}", run("digest", arm, S, kw))
line("plain learnpause", run("plain", "learnpause", S))
line("plain learnpause theta 5", run("plain", "learnpause", S, dict(theta=5.0)))

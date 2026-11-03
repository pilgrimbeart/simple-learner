"""table_gate.py: row 8's gate between 14 and 17, on training and validation seeds (lab/table.py; discrete/NOTEBOOK.md, D28)."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import table as T
from table_rows import VALID
from minimal.spec import efficiency
S = list(T.TRAIN) + list(VALID)
b = T.run("plain", "circuit", S, seconds=1000.0)
for g in (14.0, 15.0, 16.0, 17.0):
    kw = dict(learn=1.0, eta=0.06, sd=0.15, gate=g, win=200.0, born=1.5)
    print(g, f"ageing {efficiency(T.run('ageing', 'jitterg2', S, kw)):.2f}", "plain against base", T.paired(T.run("plain", "jitterg2", S, kw, 1000.0), b), flush=True)

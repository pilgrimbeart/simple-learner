"""ledger.py: one line per run in lab/v/LEDGER.md (PROGRAMME.md, How we work), so that where the CPU goes, and how often a run tells
us something we didn't know, can be read off after a week. Main session, 2026-11-10.

A script calls `ledger.start()` in its __main__. The belief the run could move and the prediction (with how sure) come from the
environment, written before the run:

    BELIEF="the lock limits timing, not material" PREDICT="rung 5 solved at P 416, 55%" .venv/bin/python lab/teach.py ...

The last column, surprised?, is filled in by hand when the result is read: no (as predicted), yes (and what), or void (the run broke)."""
import atexit
import datetime
import os
import sys
import time

PATH = "/home/pilgrim/git/simple-learner/lab/v/LEDGER.md"
HEAD = ("# The ledger\n\nOne line per run (`lab/ledger.py`). CPU is all cores' time, in hours. Surprised? is filled in by hand.\n\n"
        "| date | run | wall min | CPU h | belief it could move | prediction, and how sure | surprised? |\n|---|---|---|---|---|---|---|\n")


def start():
    t0, pid = time.time(), os.getpid()
    run = " ".join([os.path.basename(sys.argv[0])] + sys.argv[1:])
    belief, predict = os.environ.get("BELIEF", "(none given)"), os.environ.get("PREDICT", "(none given)")

    def done():
        if os.getpid() != pid:                          # a pool's worker
            return
        c = os.times()
        cpu = c.user + c.system + c.children_user + c.children_system
        if not os.path.exists(PATH):
            open(PATH, "w").write(HEAD)
        with open(PATH, "a") as f:
            f.write(f"| {datetime.date.today()} | `{run}` | {(time.time() - t0) / 60:.1f} | {cpu / 3600:.2f} | {belief} | {predict} | |\n")
    atexit.register(done)


def fill(match, text):
    """Fill the "surprised?" column of the latest unfilled row whose run contains `match`. Usage:
    .venv/bin/python -c "import sys; sys.path.insert(0, 'lab'); import ledger; ledger.fill('couple.py 20', 'no: as predicted')"."""
    rows = open(PATH).read().rstrip("\n").split("\n")
    for i in range(len(rows) - 1, -1, -1):
        r = rows[i]
        if r.startswith("| 20") and match in r and r.endswith("| |"):
            rows[i] = r[:-1] + text.replace("|", "/") + " |"         # "... | prediction | |" -> "... | prediction | text |"
            assert rows[i].count("|") == 8, rows[i]
            open(PATH, "w").write("\n".join(rows) + "\n")
            return True
    return False

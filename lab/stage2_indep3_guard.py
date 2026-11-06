"""stage2_indep3_guard.py: third independent check, 4 (fast.py's guard). On a temporary copy of the repository in my scratch folder
(never the repository itself; lab/sealed/ not copied), each mutation applied alone, then: does fast.fast_cls refuse, and if not, are
the fast and ordinary paths' lives still identical (lab/stage2_indep3_fast.fingerprint, plain, circuit and bank, seeds 69960-69961,
30 s at 10 ms)? The guard is meant to refuse whenever Python the compiled step copies has changed.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage2_indep3_guard.py SCRATCH_DIR"""
import json
import os
import shutil
import subprocess
import sys

REPO = "/home/pilgrim/git/simple-learner"

# (name, file, old, new): one textual change to the copy; None for a runtime patch in the driver
MUTATIONS = [
    ("none (control)", None, None, None),
    ("hashed step: RunLimit.step, a comment added (control: must refuse)", "lab/story1.py", "    def step(self):\n",
     None),                                   # filled below: the second 'def step' after class RunLimit
    ("hashed step: SecondsModel._beat, phase advance changed (control: must refuse)", "lab/stage2_lang/seconds.py",
     "        self.phase = (self.phase + w * span) % 1.0\n        if not on:", "        self.phase = (self.phase + 1.01 * w * span) % 1.0\n        if not on:"),
    ("SecondsModel.stimulate: each pulse's moment halved", "lab/stage2_lang/seconds.py",
     "        self._ev.append((self.t + at, sensor))", "        self._ev.append((self.t + 0.5 * at, sensor))"),
    ("Model.stimulate: pulses in a tick's first 2 ms not counted", "discrete/model.py",
     "        self.seen[sensor] += 1", "        if at > 0.002:\n            self.seen[sensor] += 1"),
    ("a layer's non-step method: Watched._events drops each tick's first pulse", "lab/story1.py", None,
     "\n\ndef _ev_drop_first(self):\n    return super(Watched, self)._events()[1:]\n\n\nWatched._events = _ev_drop_first\n"),
    ("a module constant a hashed step reads: universal.TICK 1% longer", "lab/universal.py",
     "from table import RunLimit, Gated, DB, TICK\n", "from table import RunLimit, Gated, DB, TICK\nTICK = TICK * 1.01\n"),
    ("runtime: RunLimit.step patched after the guard's first check", "RUNTIME", None, None),
]

DRIVER = r"""
import sys, json
sys.path.insert(0, COPY + "/lab"); sys.path.insert(0, COPY)
import numpy as np
from stage2_lang import arms, fast
from stage2_lang.sim import WLife
from stage2_indep3_fast import fingerprint
import table as T, bits_bank as B
out = dict(refused=None, lives=0, same=0, differ=[])
try:
    fast.fast_cls(T.Circuit); fast.fast_cls(B.Recorder)
except Exception as e:
    out["refused"] = f"{type(e).__name__}: {str(e)[:160]}"
if RUNTIME:
    import story1
    old = story1.RunLimit.step
    def step(self):
        out_ = old(self)
        self.dq = getattr(self, "dq", 0.0) * 0.999
        return out_
    story1.RunLimit.step = step
if out["refused"] is None:
    for arm in ("circuit", "bank"):
        for seed in (69960, 69961):
            for first in ("red", "blue"):
                fps = []
                for fastp in (True, False):
                    arms.FAST = fastp
                    WLife.instruments = not fastp
                    lf = arms.make(arms.world_of("(world)"), arm, seed, first)
                    l = arms.live(lf, 30.0)
                    fps.append(fingerprint(lf, l)[0])
                out["lives"] += 1
                if fps[0] == fps[1]:
                    out["same"] += 1
                else:
                    out["differ"].append((arm, seed, first, sorted(k for k in fps[0] if fps[0][k] != fps[1][k])))
print("RESULT " + json.dumps(out))
"""


def make_copy(dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(REPO, dst, ignore=shutil.ignore_patterns(".git", ".venv", "sealed", "__pycache__", "*.pkl", "*.npz"), symlinks=True)
    for root, _, files in os.walk(dst):
        for f in files:
            if f.endswith(".py"):
                p = os.path.join(root, f)
                s = open(p).read()
                if REPO in s:
                    open(p, "w").write(s.replace(REPO, dst))


if __name__ == "__main__":
    scratch = sys.argv[1]
    copy = os.path.join(scratch, "repo_copy")
    make_copy(copy)
    print(f"copy made at {copy}", flush=True)
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1")
    for name, f, old, new in MUTATIONS:
        backup = None
        runtime = f == "RUNTIME"
        if f and not runtime:
            p = os.path.join(copy, f)
            backup = open(p).read()
            s = backup
            if name.startswith("hashed step: RunLimit"):
                i = s.index("class RunLimit")
                j = s.index("    def step(self):\n", i) + len("    def step(self):\n")
                s = s[:j] + "        # a comment\n" + s[j:]
            elif old is None:
                s = s + new
            else:
                assert s.count(old) == 1, (name, s.count(old))
                s = s.replace(old, new)
            open(p, "w").write(s)
        code = f"COPY = {copy!r}\nRUNTIME = {runtime}\n" + DRIVER
        r = subprocess.run([REPO + "/.venv/bin/python", "-c", code], cwd=copy, env=env, capture_output=True, text=True, timeout=3000)
        line = next((x for x in r.stdout.splitlines() if x.startswith("RESULT ")), None)
        res = json.loads(line[7:]) if line else dict(crash=r.stderr[-400:])
        verdict = ("refused" if res.get("refused") else ("accepted, lives identical" if res.get("same") == res.get("lives")
                   else "accepted, lives DIFFER")) if "crash" not in res else "crash"
        print(f"{name}\n    {verdict}: {res}", flush=True)
        if backup is not None:
            open(p, "w").write(backup)
    shutil.rmtree(copy)

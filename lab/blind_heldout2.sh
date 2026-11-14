#!/bin/bash
# blind_heldout2.sh: a second held-out ladder (PROGRAMME.md, Sealed; the user agreed, 2026-11-14), written by a fresh agent under the tighter
# seal of blind_agents.sh: run from an empty, neutrally named directory, with no setting sources and no MCP servers, so it gets no project
# instructions, memory or git status. It is given a brief (the creature, the wires, the world language, the existing ladders' kinds with one
# example world each), a checker that compiles a world, and a checker that runs the starting brain and a told brain on a rung. It never sees
# a brain design. The seal isn't perfect: its checkers import the project's engine by path, so it could read the engine's files if it
# chose; it is asked not to. The ladder moves into lab/sealed unread; its reply gives counts and a hash.
R=/home/pilgrim/git/simple-learner
W=$(mktemp -d /tmp/blind_XXXXXX)
mkdir -p "$W/work"
cd "$R" && .venv/bin/python - "$W/work" <<'EOF'
import sys, re
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import ladders as L
out = sys.argv[1]
src = open("/home/pilgrim/git/simple-learner/lab/stage2_lang/lang.py").read()
doc = src.split('"""')[1]
vocab = "\n".join(l for l in src.splitlines() if re.match(r"^(STAGES|LOCALS|EVENT_REG|TICKED|FIXED_AT_BIRTH|WORTH_RANGE|CONSTS|BODYREG|READONLY|REG|PURE|FUNCS|DRAWS|READS|STMTS|ARGC|TOP|CONTROL) ", l))
brief = f"""# Brief

## The creature
A simulated creature lives on a flat 60 mm square world whose edges wrap around (a torus). It is a small disc, 4 mm across, with a mouth
at the front. 18 red and 18 blue blocks, 1 mm in radius, sit still; a block touched by the mouth while moving forward is eaten and
reappears somewhere random. Time runs in ticks of 10 ms; a life lasts as long as a rung sets (100 s to a few thousand).

The body: two thrusters on the rear rim both push forward; one alone also turns the creature away from its side; speed and turning fade
by drag. Two eyes look ahead along a narrow corridor; each eye sees only one colour and fires random pulses at a rate that rises as a
block of its colour gets nearer. Nearer blocks hide those behind them.

The brain connects to the body only by these wires: two eye inputs (pulses), one taste input (+1 food or -1 poison, for one tick, when a
block is eaten), and two motor outputs (firings). It is not told which eye is which colour or which motor is which thruster. It is scored
on food eaten minus twice the poison, against the energy it spends; in a long life, on the last third. It learns during its life. In the
ordinary world one colour is food and the other poison for the whole life, which is which drawn per life.

## The task: a ladder
A ladder is a series of worlds, rungs, each bigger than the last in one way, so that a brain that scales should climb it as it is given
more raw material. A rung counts if the starting brain (a small fixed circuit that approaches one colour and flips after a poison) falls
short, by at least .25 in efficiency, of a told brain: the same body steered to the colour a world's (told e) expression names as poison
at each moment. The told expression must be information a learner could in principle get from its senses (eyes, taste, its own actions
and their timing) within the life; a told brain that knows what no sense could reveal in time makes a gap no learner can close.

## The world language
{doc}

The vocabulary, exactly as the compiler holds it:
```
{vocab}
```

## Ladders that exist (their kinds are taken: write a different kind)
- Sequences: which colour is food follows a secret repeating word of n letters, moved on by each good meal. Example, n = 5:
```
{L.seq(5)}
```
- Timing: the same word, but in time slots of a length drawn per life, whatever the creature does. Example, n = 3:
```
{L.timing(3)}
```
- Combinations: a meal's meaning depends on the last k colours eaten, good or bad, by a secret table. Example, k = 2:
```
{L.combo(2)}
```
- Hidden contexts: recurring hidden contexts, each shown only by a background pulse rate on the eyes, each with its own secret food
  colour (also taken).

## Tools here
- `python check_world.py FILE`: compiles each rung of a ladder file and reports errors.
- `python check_rung.py FILE RUNG [PAIRS]`: lives the starting brain and the told brain on a rung (about a minute for 4 pairs of 1000 s
  lives) and reports their efficiencies and the gap.
Don't open files outside this directory.
"""
open(out + "/brief.md", "w").write(brief)
open(out + "/check_world.py", "w").write('''import json, sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from stage2_lang import lang
d = json.load(open(sys.argv[1]))
for r in d["rungs"]:
    try:
        lang.World(r["text"], compile_only=True)
        print("rung", r["size"], "compiles")
    except Exception as e:
        print("rung", r["size"], "ERROR:", e)
''')
open(out + "/check_rung.py", "w").write('''import json, sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import ladders as L, stage3_random as R
d = json.load(open(sys.argv[1])); size = int(sys.argv[2]); n = int(sys.argv[3]) if len(sys.argv) > 3 else 4
r = next(x for x in d["rungs"] if x["size"] == size)
jobs = [(r["text"], arm, {}, s, c, float(r["seconds"])) for arm in ("circuit", "vtold") for s in range(200000, 200000 + n) for c in ("red", "blue")]
with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
    res = list(ex.map(L.job, jobs))
I = R.boot(n)
b = L.scored(res[:2 * n], float(r["seconds"]), I); t = L.scored(res[2 * n:], float(r["seconds"]), I)
print(f"rung {size}: starting {b[0]:+.2f}, told {t[0]:+.2f}, gap {t[0] - b[0]:+.2f} [{np.percentile(t[1] - b[1], 2.5):+.2f},{np.percentile(t[1] - b[1], 97.5):+.2f}]")
''')
EOF
P="Read brief.md in this directory: it describes a simulated creature, a small language for its worlds, and ladders of challenges that
exist. Your job: invent a ladder of a new kind, different from the existing ones, that tests something a growing brain would need in order
to cope with harder worlds of this sort, drawing on what animal learning, ecology, control or machine-learning research finds hard (you may
use web search). Write it as heldout_ladder2.json in this directory, with the fields name, kind (a paragraph), source (what it draws on),
and rungs: 6 rungs of increasing size, each with size, seconds (a life long enough for the rung), text (the world, in the language,
including a (told e) expression) and desc (what the rung is and what must be learned, in bits if you can). Use check_world.py until every
rung compiles, and check_rung.py on at least three rungs to show the starting brain falls short of the told brain by at least .25 (adjust
the rungs if not). Don't open files outside this directory.

When finished, reply in under 8 lines with: the number of rungs, how many compile, the gaps you measured (numbers only, by rung size), and
any difficulty. Do not describe the ladder's kind or rules in your reply: the people reading it must not learn them."
(cd "$W/work" && timeout 5400 claude -p --setting-sources "" --strict-mcp-config --no-session-persistence --model sonnet \
  --tools "Read,Write,Edit,Bash,WebSearch,WebFetch" --allowedTools "Read,Write,Edit,Bash,WebSearch,WebFetch" > "$W/reply.txt" 2> "$W/err.txt" <<< "$P")
if [ -s "$W/work/heldout_ladder2.json" ]; then
  mv "$W/work/heldout_ladder2.json" "$R/lab/sealed/heldout_ladder2.json"
  cp "$W/reply.txt" "$R/lab/v/heldout_ladder2_reply.log"
  sha256sum "$R/lab/sealed/heldout_ladder2.json"
else
  echo "no ladder was written; see $W/reply.txt and $W/err.txt"
fi

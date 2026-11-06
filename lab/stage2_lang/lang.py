"""lang.py: a world is data: text in S-expressions, parsed, validated against a written vocabulary, put in canonical form (for its description length) and compiled to Python.

A world:   (world (meta ...) (stream N) (const NAME e)* (let NAME e)* (table NAME n m e)* (told e) (told-wait e) (on STAGE stmt ...)*)
Stages run in a fixed order, the pipeline, in sim.WLife.step:
    birth   once, after the body and wiring
    tick    each tick's start: the rule's registers, time courses, forces, blocks moved, pulses injected
    see     per colour: seen (what reaches the eye, 0 to 1 and not clipped after); read (raw c)
    pulse   per eye pulse: eye, colour; (drop)
    fire    per thruster firing: thruster, motor; gain, (drop)
    move    after the body has moved and before anything is eaten: x y heading vx vy spin
    meal    per block touched: block, colour; sign (what the taste adds: -1 poison, +1 food), (drop) leaves the block uneaten
    respawn per eaten block, in place of a uniform draw: block, nx, ny
    taste   the one pulse of a tick with a non-zero sum: value (already clipped), (drop)
    score   per meal, after the taste, in order: colour, block; bad, amount. Rule state about meals is written here.
A rule's draws come from the world's own stream, never the body's, so a rule that doesn't act can't change a life.

Only the vocabulary below is accepted; the compiler emits nothing else. The stage-5 mark is computed, not declared: `stage5(world)`.

Stage 2b (lab/v/stage2b_*.log):
- The brain is reached only through its three calls, by the engine. `bp` and `bpget` are gone from the language (a world that names them
  doesn't compile), and the compiled code is checked against an allowlist of the life's attributes (`_ALLOWED`), so no text can reach the brain.
- The guard goes by what a world can do. `World(text)` refuses, statically, any world that can inject a taste, drop one, write a taste
  from anything but the literal 1 or -1, end a life, rewire, add a score with no meal, or set a sign, an amount, COST or THRUST to a literal
  that breaks the score's agreement with the taste; the engine (sim.WLife) checks the rest in every tick of every life (sim.Refused).
  `World(text, compile_only=True)` compiles to show a program runs, and keeps no functions, so it can't be lived.
- Description length is of a normal form (`normalise`): constants folded, never-acting rules removed over lives up to H_LIFE, identity
  writes removed, single-use variables inlined, lets in a fixed order, commutative operands sorted. The stream offset of a world that names
  none still comes from stage 2a's canonical form, so no life changed."""
from __future__ import annotations

import hashlib
import lzma
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
STAGES = ("birth", "tick", "see", "pulse", "fire", "move", "meal", "respawn", "score")
LOCALS = {"pulse": ("eye", "colour"), "fire": ("thruster", "motor"), "see": ("colour",), "meal": ("block", "colour"), "respawn": ("block",), "score": ("block", "colour", "worth")}
EVENT_REG = {"see": {"seen"}, "fire": {"gain"}, "meal": {"worth"}, "respawn": {"nx", "ny"}}
TICKED = ("tick", "see", "move")                         # stages run once a tick: a draw or an event there must be a rate in seconds
FIXED_AT_BIRTH = {"COST", "THRUST"}                     # the score's constants: (const ...) only
WORTH_RANGE = (0.1, 10.0)                               # a meal's worth is 0 or its size in this range, either sign (sim.WLife._worth)
# world.py's constants, and two of the score's (L9). Each a register of the life: read anywhere, written by (const ...) or (set ...).
CONSTS = {"RADIUS", "WORLD", "BODY", "BLOCKS", "EAT", "SENSE", "REACH", "RANGE", "RAYS", "BLOCK", "PUSH", "TURN", "DRAG", "COST", "THRUST"}
GEOMETRY = {"EAT", "RAYS", "BLOCK"}                     # derived arrays follow (sim.Body.geometry)
BODYREG = {"x": "W.body.pos[0]", "y": "W.body.pos[1]", "vx": "W.body.speed[0]", "vy": "W.body.speed[1]", "heading": "W.body.heading", "spin": "W.body.spin"}
READONLY = {"t": "W.now", "P": "W.P", "F": "W.F", "TICK": "W.dt", "N": "W.body.n", "PI": "3.141592653589793", "TWOPI": "6.283185307179586", "speed": "W.body.fspeed()"}
REG = {"poison": "W.poison"}
PURE = {"+": ("(", " + ", ")"), "*": ("(", " * ", ")"), "-": ("(", " - ", ")"), "/": ("(", " / ", ")"), "=": ("(", " == ", ")"), "!=": ("(", " != ", ")"), "<": ("(", " < ", ")"), "<=": ("(", " <= ", ")"), ">": ("(", " > ", ")"), ">=": ("(", " >= ", ")"),
        "and": ("(", " and ", ")"), "or": ("(", " or ", ")"), "mod": ("(", " % ", ")")}
FUNCS = {"min": "min", "max": "max", "abs": "abs", "floor": "math.floor", "exp": "math.exp", "log": "math.log", "sqrt": "math.sqrt", "sin": "math.sin", "cos": "math.cos", "pow": "math.pow", "atan2": "math.atan2"}
DRAWS = {"chance": "(W.r.random() < {0})", "uniform": "float(W.r.uniform({0}, {1}))", "normal": "float(W.r.normal({0}, {1}))", "int": "int(W.r.integers({0}))", "poisson": "int(W.r.poisson({0}))"}
READS = {"raw": "W.raw[{0}]", "sensor": "W.wire_s[{0}]", "motorof": "W.wire_m[{0}]", "bx": "W.body.xy[{0}, 0]", "by": "W.body.xy[{0}, 1]", "kind": "W.body.kind[{0}]", "look": "W.body.look[{0}]", "bright": "W.body.bright[{0}]", "alive": "W.body.alive[{0}]",
         "dist": "W.dist({0}, {1})", "wdist": "W.wdist({0}, {1}, {2}, {3})", "near": "W.near({0}, {1})", "nearest": "W.nearest({0})"}
STMTS = {"pulse": "W.inject_pulse({0})", "thrust": "W.inject_thrust({0})", "bset": "W.bset({0}, {1}, {2})", "bkind": "W.body.kind.__setitem__({0}, {1})", "blook": "W.body.look.__setitem__({0}, {1})", "bbright": "W.body.bright.__setitem__({0}, {1})",
         "hide": "W.hide({0})", "show": "W.show({0})", "respawn": "W.respawn_now({0})"}
ARGC = {"chance": 1, "uniform": 2, "normal": 2, "int": 1, "poisson": 1, "raw": 1, "sensor": 1, "motorof": 1, "bx": 1, "by": 1, "kind": 1, "look": 1, "bright": 1, "alive": 1, "dist": 2, "wdist": 4, "near": 2, "nearest": 1,
        "pulse": 1, "thrust": 1, "bset": 3, "bkind": 2, "blook": 2, "bbright": 2, "hide": 1, "show": 1, "respawn": 1}
TOP = ("world", "meta", "stream", "const", "let", "table", "told", "told-wait", "on")
CONTROL = ("set", "if", "do", "repeat", "each", "until", "after", "drop", "put", "at", "not")
VOCAB = TOP + STAGES + tuple(sorted(CONSTS)) + tuple(BODYREG) + tuple(READONLY) + tuple(REG) + tuple(PURE) + tuple(FUNCS) + tuple(DRAWS) + tuple(READS) + tuple(STMTS) + CONTROL + tuple(sorted(x for v in LOCALS.values() for x in v)) + tuple(sorted(x for v in EVENT_REG.values() for x in v))


class LangError(ValueError):
    pass


class Refused(LangError):
    """A world that can change the rules of the current constraints (GRAMMAR.md, the user's decision 1): not run."""


class LifeRefused(RuntimeError):
    """Raised in a life: a rule raised a Python error, or wrote a worth outside its range, or a constant broke its bounds (sim.Refused)."""


# ---------------------------------------------------------------- text and data
def parse(text):
    """Text to nested lists of symbols and numbers. ; to the line's end is a comment."""
    tokens = re.findall(r"[()]|[^\s()]+", re.sub(r";[^\n]*", "", text))
    pos = 0

    def one():
        nonlocal pos
        if pos >= len(tokens):
            raise LangError("unexpected end")
        tk = tokens[pos]
        pos += 1
        if tk == "(":
            out = []
            while pos < len(tokens) and tokens[pos] != ")":
                out.append(one())
            if pos >= len(tokens):
                raise LangError("unclosed (")
            pos += 1
            return out
        if tk == ")":
            raise LangError("stray )")
        try:
            return float(tk) if re.search(r"[.eE]", tk) else int(tk)
        except ValueError:
            return tk
    tree = one()
    if pos != len(tokens):
        raise LangError("text after the world")
    if not tree or tree[0] != "world":
        raise LangError("a world starts (world")
    return tree


def show(x):
    if isinstance(x, list):
        return "(" + " ".join(show(y) for y in x) + ")"
    return repr(x) if isinstance(x, float) else str(x)


# ---------------------------------------------------------------- the world's structure
class World:
    """A parsed, validated, compiled world. It holds no life's state: that is all in sim.WLife."""

    def __init__(self, text, name=None, compile_only=False):
        self.text = text
        self.tree = parse(text)
        self.name = name
        self.meta, self.stream, self.consts, self.lets, self.tables, self.told, self.told_wait = {}, None, [], [], [], None, None
        self.rules = {s: [] for s in STAGES}
        for item in self.tree[1:]:
            if not isinstance(item, list) or not item:
                raise LangError(f"not a clause: {show(item)}")
            k = item[0]
            if k == "meta":
                self.meta.update({m[0]: m[1:] for m in item[1:]})
            elif k == "stream":
                self.stream = int(item[1])
            elif k == "const":
                if item[1] not in CONSTS:
                    raise LangError(f"not a constant: {item[1]}")
                self.consts.append((item[1], item[2]))
            elif k == "let":
                self.lets.append((self.name_ok(item[1]), item[2]))
            elif k == "table":
                self.tables.append((self.name_ok(item[1]), item[2], item[3], item[4]))
            elif k == "told":
                self.told = item[1]
            elif k == "told-wait":
                self.told_wait = item[1]
            elif k == "on":
                if item[1] not in STAGES:
                    raise LangError(f"not a stage: {item[1]}")
                self.rules[item[1]].extend(item[2:])
            else:
                raise LangError(f"not a clause: {k}")
        self.vars = {n for n, _ in self.lets}
        self.tabs = {n for n, *_ in self.tables}
        if self.vars & self.tabs:
            raise LangError("a name used twice")
        self.refused = self.stage5()
        fn = compile_world(self)                       # compiles (and checks the code) whether or not it is refused
        if compile_only:
            self.fn = None                             # nothing to run: sim.WLife won't take it
        elif self.refused:
            raise Refused(f"{name or 'this world'} can change the rules of the current constraints: {'; '.join(self.refused)}")
        else:
            self.fn = fn

    @staticmethod
    def name_ok(n):
        if not isinstance(n, str) or n in VOCAB or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", n):
            raise LangError(f"a state variable's name can't be {n}")
        return n

    def ops(self):
        """Every symbol at the head of a list in the world's rules."""
        out = set()

        def walk(x):
            if isinstance(x, list):
                if x and isinstance(x[0], str):
                    out.add(x[0])
                for y in x:
                    walk(y)
        for s in self.rules.values():
            walk(s)
        return out

    def writes(self):
        """Every register a rule writes, with its stage."""
        out = set()

        def walk(x, s):
            if isinstance(x, list):
                if len(x) > 1 and x[0] == "set":
                    out.add((s, x[1]))
                if x and x[0] == "drop":
                    out.add((s, "drop"))
                for y in x:
                    walk(y, s)
        for s, rs in self.rules.items():
            walk(rs, s)
        return out

    def sets(self):
        """Every (stage, register, expression) a rule writes with (set ...), at any depth; consts as stage 'const'."""
        out = [("const", n, v) for n, v in self.consts]

        def walk(x, s):
            if isinstance(x, list):
                if len(x) == 3 and x[0] == "set":
                    out.append((s, x[1], x[2]))
                for y in x:
                    walk(y, s)
        for s, rs in self.rules.items():
            walk(rs, s)
        return out

    def stage5(self):
        """Why this world is refused, from its text. Since stage 2c the interface is enforced by construction (sim.WLife): a world writes
        only a meal's worth, never a taste or a score; each meal's taste is its worth's sign at its own moment, its score its worth; COST
        and THRUST are fixed at birth; a rule's Python error refuses the life. So the text is checked only for what can be decided from it:
          marks                         (stage 5) or (lying ...)
          the score's constants         COST <= 0 or THRUST < 0 as literals (the engine checks the rest at birth)
          a worth out of range          a literal worth outside 0 and +-WORTH_RANGE (the engine checks every meal)
          counted in ticks              in a stage run once a tick (TICKED): a draw that isn't a rate, (chance e) or (poisson e) with
                                        TICK a factor of e; a pulse or thrust not under such a draw; a variable stepped by a literal with
                                        no condition (a count of ticks)
        The stage-5 kinds a world can still bring about through honest parts (a rewiring by see, look or fire; a body frozen; a block put
        back under the mouth) are labelled from the lives by instruments (instruments.py), not refused here."""
        why = []
        if self.tag() == 5:
            why.append("marked stage 5")
        if self.meta.get("lying"):
            why.append("marked as lying")
        lit = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)
        lo, hi = WORTH_RANGE
        for st, n, v in self.sets():
            if n == "COST" and lit(v) and v <= 0:
                why.append(f"COST {v}: poison not bad")
            if n == "THRUST" and lit(v) and v < 0:
                why.append(f"THRUST {v}: a firing that pays")
            if st == "meal" and n == "worth" and lit(v) and v != 0 and not lo <= abs(v) <= hi:
                why.append(f"a meal's worth {v}, outside 0 and +-[{lo}, {hi}]")
        why += _ticked(self)
        return list(dict.fromkeys(why))

    def tag(self):
        return self.meta.get("stage", [None])[0]


def _rate(e):
    """(chance e) or (poisson e) is a rate in seconds if TICK is a factor of e."""
    if e == "TICK":
        return True
    return isinstance(e, list) and bool(e) and e[0] == "*" and any(_rate(y) for y in e[1:])


def _ticked(w):
    """What in a stage run once a tick is counted in ticks (stage5's last item)."""
    why = []

    def walk(x, gated, cond):
        if not isinstance(x, list) or not x:
            return
        op = x[0]
        if op in DRAWS and not (op in ("chance", "poisson") and len(x) == 2 and _rate(x[1])):
            why.append(f"a draw once a tick, {show(x)}: write it as a rate, (chance (* r TICK)) or (poisson (* r TICK))")
        if op in ("pulse", "thrust") and not gated:
            why.append(f"{show(x)} once a tick: put it under (if (chance (* r TICK)) ...) or (repeat (poisson (* r TICK)) ...)")
        if op == "set" and not cond and isinstance(x[2], list) and len(x[2]) == 3 and x[2][0] in ("+", "-") and x[1] in x[2][1:] \
                and any(_num(y) for y in x[2][1:]) and x[1] in w.vars:
            why.append(f"{show(x)} with no condition: a count of ticks")
        g = gated or (op == "if" and isinstance(x[1], list) and x[1] and x[1][0] == "chance" and _rate(x[1][1])) \
            or (op == "repeat" and isinstance(x[1], list) and x[1] and x[1][0] == "poisson" and _rate(x[1][1]))
        if op == "after":
            return                                      # a deferral runs once, at its own moment: an event, not a tick
        for y in x[1:]:
            walk(y, g, cond or op in ("if", "until"))
    for st in TICKED:
        for r in w.rules[st]:
            walk(r, False, False)
    return why


# ---------------------------------------------------------------- the compiler
class _Gen:
    def __init__(self, w, stage, in_after=False):
        self.w, self.stage, self.in_after = w, stage, in_after
        self.names = list(LOCALS.get(stage, ()))
        self.bound = set()
        self.fresh = 0

    def err(self, x, why):
        raise LangError(f"{why}: {show(x)} (stage {self.stage})")

    def read(self, s):
        if s in self.bound or s in self.names:
            return "x_" + s if s in self.bound else s
        if s in EVENT_REG.get(self.stage, ()):
            return s                                    # in an (after): its value when the (after) ran
        if s in BODYREG:
            return BODYREG[s]
        if s in READONLY:
            return READONLY[s]
        if s in REG:
            return REG[s]
        if s in CONSTS:
            return "W." + s
        if s in self.w.vars:
            return "W.v_" + s
        self.err(s, "not a word of the language")

    def e(self, x):
        if isinstance(x, (int, float)):
            return repr(x)
        if isinstance(x, str):
            return self.read(x)
        if not x or not isinstance(x[0], str):
            self.err(x, "not an expression")
        op, *a = x
        if op == "if":
            if len(a) != 3:
                self.err(x, "an expression's if needs 3")
            return f"({self.e(a[1])} if {self.e(a[0])} else {self.e(a[2])})"
        if op == "not":
            return f"(not {self.e(a[0])})"
        if op == "-" and len(a) == 1:
            return f"(-{self.e(a[0])})"
        if op in ("mod", "/", "=", "!=", "<", "<=", ">", ">=") and len(a) != 2:
            self.err(x, "needs 2")
        if op in PURE:
            if not a:
                self.err(x, "needs arguments")
            o, m, c = PURE[op]
            return o + m.join(self.e(y) for y in a) + c
        if op in FUNCS:
            return f"{FUNCS[op]}(" + ", ".join(self.e(y) for y in a) + ")"
        if op == "at":
            if a[0] not in self.w.tabs:
                self.err(x, "not a table")
            j = self.e(a[2]) if len(a) > 2 else "0"
            return f"W.t_{a[0]}[int({self.e(a[1])})][int({j})]"
        if op in DRAWS or op in READS:
            if len(a) != ARGC[op]:
                self.err(x, f"needs {ARGC[op]}")
            return (DRAWS.get(op) or READS[op]).format(*[self.e(y) for y in a])
        self.err(x, "not a word of the language")

    def st(self, x, ind, out):
        pad = "    " * ind
        if not isinstance(x, list) or not x or not isinstance(x[0], str):
            self.err(x, "not a statement")
        op, *a = x
        if op == "set":
            if len(a) != 2 or not isinstance(a[0], str):
                self.err(x, "(set name e)")
            n = a[0]
            v = self.e(a[1])
            if n in EVENT_REG.get(self.stage, ()):
                if self.in_after:
                    self.err(x, "an event's register can't be written in an (after)")
                out.append(f"{pad}{n} = {v}")
            elif n in BODYREG:
                out.append(f"{pad}{BODYREG[n]} = {v}")
            elif n in REG:
                out.append(f"{pad}{REG[n]} = {v}")
            elif n in CONSTS:
                if n in FIXED_AT_BIRTH:
                    self.err(x, f"{n} is fixed at birth: (const {n} e) only")
                out.append(f"{pad}W.set_const({n!r}, {v})")
            elif n in self.w.vars:
                out.append(f"{pad}W.v_{n} = {v}")
            else:
                self.err(x, "not writable here")
        elif op == "if":
            if not 2 <= len(a) <= 3:
                self.err(x, "(if c s [s])")
            out.append(f"{pad}if {self.e(a[0])}:")
            self.st(a[1], ind + 1, out)
            if len(a) == 3:
                out.append(f"{pad}else:")
                self.st(a[2], ind + 1, out)
        elif op == "do":
            if not a:
                out.append(f"{pad}pass")
            for y in a:
                self.st(y, ind, out)
        elif op == "repeat":
            out.append(f"{pad}for _ in range(int({self.e(a[0])})):")
            self.block(a[1:], ind + 1, out)
        elif op == "each":
            v = a[0]
            if not isinstance(v, str) or v in VOCAB or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", v):
                self.err(x, "(each name s ...)")
            self.bound.add(v)
            out.append(f"{pad}for x_{v} in range(W.body.n):")
            self.block(a[1:], ind + 1, out)
            self.bound.discard(v)
        elif op == "until":
            out.append(f"{pad}for _ in range(int({self.e(a[1])})):")
            self.block(a[2:], ind + 1, out)
            out.append(f"{pad}    if {self.e(a[0])}:")
            out.append(f"{pad}        break")
        elif op == "after":
            self.fresh += 1
            f = f"later{ind}_{self.fresh}"
            cap = [n for n in self.names] + sorted(EVENT_REG.get(self.stage, ())) + ["x_" + b for b in self.bound]
            out.append(f"{pad}def {f}(W" + "".join(f", {c}={c}" for c in cap) + "):")
            sub = _Gen(self.w, self.stage, in_after=True)
            sub.names, sub.bound = self.names, set(self.bound)
            sub.block(a[1:], ind + 1, out)
            out.append(f"{pad}W.later({self.e(a[0])}, {f})")
        elif op == "drop":
            if self.stage not in ("pulse", "fire", "meal") or self.in_after:
                self.err(x, "nothing to drop here")
            out.append(f"{pad}drop = True")
        elif op == "put":
            if a[0] not in self.w.tabs:
                self.err(x, "not a table")
            if len(a) == 4:
                out.append(f"{pad}W.t_{a[0]}[int({self.e(a[1])})][int({self.e(a[2])})] = {self.e(a[3])}")
            else:
                out.append(f"{pad}W.t_{a[0]}[int({self.e(a[1])})][0] = {self.e(a[2])}")
        elif op in STMTS:
            if len(a) != ARGC[op]:
                self.err(x, f"needs {ARGC[op]}")
            out.append(pad + STMTS[op].format(*[self.e(y) for y in a]))
        else:
            self.err(x, "not a statement")

    def block(self, rs, ind, out):
        if not rs:
            out.append("    " * ind + "pass")
        for r in rs:
            self.st(r, ind, out)


# What compiled code may touch: the life's registers and helpers, the body's state, the world's stream, math. Never the brain.
_ALLOWED = {"W": {"now", "P", "F", "dt", "body", "poison", "r", "raw", "wire_s", "wire_m", "dist", "wdist", "near", "nearest", "set_const",
                  "later", "inject_pulse", "inject_thrust", "bset", "respawn_now", "hide", "show"} | CONSTS,
            "W.body": {"pos", "speed", "heading", "spin", "xy", "kind", "look", "bright", "alive", "n", "fspeed"},
            "W.r": {"random", "uniform", "normal", "integers", "poisson"},
            "math": set(FUNCS[f][5:] for f in FUNCS if FUNCS[f].startswith("math.")) | {"floor"}}
_SETITEM = {"W.body.kind", "W.body.look", "W.body.bright"}
_NAMES = {"W", "math", "int", "float", "min", "max", "abs", "range", "drop", "_", "_i", "_j", "consts", "init", "told", "told_wait", "pass"}


def _check_code(code, w):
    """Every attribute chain in the compiled code is on the allowlist, and every bare name is a builtin the compiler uses, a local, a
    register, a loop variable or a deferred function. Sound by construction: there is no other way for compiled code to reach an object."""
    import ast
    tree = ast.parse(code)
    locals_ = set(x for v in LOCALS.values() for x in v) | set(x for v in EVENT_REG.values() for x in v)

    def chain(node):
        parts = []
        while isinstance(node, ast.Attribute):
            parts.append(node.attr)
            node = node.value
        if isinstance(node, ast.Name):
            parts.append(node.id)
            return ".".join(reversed(parts))
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            c = chain(node)
            if c is None:
                raise LangError(f"compiled code reaches an attribute of an expression: {ast.unparse(node)}")
            head, _, attr = c.rpartition(".")
            if head in _ALLOWED and (attr in _ALLOWED[head] or (head == "W" and (attr.startswith("v_") or attr.startswith("t_")))):
                continue
            if attr == "__setitem__" and head in _SETITEM:
                continue
            raise LangError(f"compiled code touches {c}: not on the allowlist")
        if isinstance(node, ast.Name):
            n = node.id
            if not (n in _NAMES or n in locals_ or n.startswith("x_") or n.startswith("later") or n.startswith("on_")):
                raise LangError(f"compiled code names {n}: not on the allowlist")
        if isinstance(node, (ast.Import, ast.ImportFrom)) and not (isinstance(node, ast.Import) and [a.name for a in node.names] == ["math"]):
            raise LangError("compiled code imports")


def compile_world(w):
    """World to functions. Each stage's function takes its locals and its registers, and returns the registers. A stage with no rules has no function: the engine skips it."""
    src = ["import math", "def consts(W):"]
    g = _Gen(w, "birth")
    for n, v in w.consts:
        src.append(f"    W.{n} = {g.e(v)}")
    src += ["    pass", "def init(W):"]
    for n, v in w.lets:
        src.append(f"    W.v_{n} = {g.e(v)}")
    for n, a, b, v in w.tables:
        src.append(f"    W.t_{n} = [[{g.e(v)} for _j in range(int({g.e(b)}))] for _i in range(int({g.e(a)}))]")
    src.append("    pass")
    for s, rs in w.rules.items():
        if not rs:
            continue
        g = _Gen(w, s)
        regs = sorted(EVENT_REG.get(s, ()))
        args = ["W"] + list(LOCALS.get(s, ())) + regs
        src.append(f"def on_{s}(" + ", ".join(args) + "):")
        if s in ("pulse", "fire", "meal"):
            src.append("    drop = False")
        g.block(rs, 1, src)
        ret = regs + (["drop"] if s in ("pulse", "fire", "meal") else [])
        if ret:
            src.append("    return " + ", ".join(ret) + ("," if len(ret) == 1 else ""))
    for x in (w.told, w.told_wait):
        if x is not None and _draws(x):
            raise LangError(f"(told {show(x)}) draws: what a told arm is told is a function of the world's state, never a draw (it is read inside brain calls)")
    if w.told is not None:
        src += ["def told(W):", f"    return {_Gen(w, 'tick').e(w.told)}"]
    if w.told_wait is not None:
        src += ["def told_wait(W):", f"    return {_Gen(w, 'tick').e(w.told_wait)}"]
    ns = {}
    code = "\n".join(src)
    _check_code(code, w)
    exec(compile(code, f"<world {w.name}>", "exec"), ns)
    w.source = code
    return {k: _guarded(ns[k], k) for k in ns if k in ("consts", "init", "told", "told_wait") or k.startswith("on_")}


def _guarded(f, name):
    """A rule's Python error (1/0, log of a negative, ...) refuses the life, as LifeRefused, instead of crashing it."""
    def g(*a):
        try:
            return f(*a)
        except LifeRefused:
            raise
        except Exception as e:
            raise LifeRefused(f"a rule raised a Python error in {name}: {type(e).__name__}: {e}") from None
    return g


# ---------------------------------------------------------------- canonical form and description length (D30)
ORDER = ("const", "let", "table", "told", "told-wait", "on")


def _reads_names(x, names, out):
    if isinstance(x, list):
        for y in x:
            _reads_names(y, names, out)
    elif isinstance(x, str) and x in names:
        out.add(x)


def _prune(w):
    """Keep what connects to a port: a state variable or table read by nothing that reaches a port is removed, and so are the writes to it. Fixpoint."""
    state = set(w.vars) | set(w.tabs)
    live = set()

    def reads(x):
        o = set()
        _reads_names(x, state, o)
        return o

    def stmts(rs):
        for r in rs:
            yield r

    def collect(r, enclosing):
        """Walk statements: anything read by a write to a port or a live variable, or by the control around it, is live."""
        if not isinstance(r, list) or not r:
            return
        op = r[0]
        if op == "set" and r[1] in state:
            if r[1] in live:
                live.update(reads(r[2]) | enclosing)
        elif op == "put":
            if r[1] in live:
                live.update(reads(r[2:]) | enclosing)
        elif op == "if":
            enc = enclosing | reads(r[1])
            for y in r[2:]:
                collect(y, enc)
        elif op in ("do",):
            for y in r[1:]:
                collect(y, enclosing)
        elif op == "repeat" or op == "after":
            enc = enclosing | reads(r[1])
            for y in r[2:]:
                collect(y, enc)
        elif op == "each":
            for y in r[2:]:
                collect(y, enclosing)
        elif op == "until":
            enc = enclosing | reads(r[1]) | reads(r[2])
            for y in r[3:]:
                collect(y, enc)
        else:
            live.update(reads(r) | enclosing)
    before = -1
    told = [x for x in (w.told, w.told_wait) if x is not None]
    while len(live) != before:
        before = len(live)
        live.update(reads(told))
        for rs in w.rules.values():
            for r in rs:
                collect(r, set())
        for n, *rest in list(w.lets) + list(w.tables):
            if n in live:
                live.update(reads(rest))

    def clean(r):
        if not isinstance(r, list) or not r:
            return r
        op = r[0]
        if op == "set" and r[1] in state and r[1] not in live:
            return None
        if op == "put" and r[1] not in live:
            return None
        if op == "if":
            parts = [clean(y) for y in r[2:]]
            if all(p is None for p in parts):
                return None
            return ["if", r[1]] + [p if p is not None else ["do"] for p in parts]
        if op in ("do", "repeat", "after", "each", "until"):
            k = {"do": 1, "repeat": 2, "after": 2, "each": 2, "until": 3}[op]
            body = [c for c in (clean(y) for y in r[k:]) if c is not None]
            return r[:k] + body if body or op == "repeat" else None
        return r
    rules = {s: [c for c in (clean(r) for r in rs) if c is not None] for s, rs in w.rules.items()}
    return live, rules


def _canonical_2a(w):
    """Stage 2a's canonical form, kept unchanged only for the stream offset of a world that names no stream (so no life changes). (structure, parameters) as two strings. Comments, meta and stream gone; stages in pipeline order; consts sorted; unconnected state removed; state names numbered by first use; numbers on a 5% log grid, moved to the parameter string."""
    live, rules = _prune(w)
    names = {}
    params = []

    def nm(s):
        if s not in names:
            names[s] = f"v{len(names)}"
        return names[s]

    def go(x):
        if isinstance(x, list):
            return "(" + " ".join(go(y) for y in x) + ")"
        if isinstance(x, (int, float)):
            params.append(grid(x))
            return "#"
        if x in live or x in w.vars or x in w.tabs:
            return nm(x)
        if x in VOCAB:
            return x
        return nm(x)                                    # an (each) variable
    parts = []
    for n, v in sorted(w.consts, key=lambda c: c[0]):
        parts.append("(const " + n + " " + go(v) + ")")
    for s in STAGES:
        if rules[s]:
            parts.append(f"(on {s} " + " ".join(go(r) for r in rules[s]) + ")")
    if w.told is not None:
        parts.append("(told " + go(w.told) + ")")
    if w.told_wait is not None:
        parts.append("(told-wait " + go(w.told_wait) + ")")
    # state declarations, after the rules so that numbering follows use; unused ones are gone
    for n, v in w.lets:
        if n in live:
            parts.append("(let " + nm(n) + " " + go(v) + ")")
    for n, a, b, v in w.tables:
        if n in live:
            parts.append("(table " + nm(n) + " " + go(a) + " " + go(b) + " " + go(v) + ")")
    return "\n".join(parts), " ".join(params)


# ---------------------------------------------------------------- the normal form (stage 2b): rewrites that keep the meaning
H_LIFE = 1000.0          # s: "never acts" is judged over lives up to this long, the longest the programme plans (GRAMMAR.md, step 7: 10x)
_ARITH = {"+": lambda *a: sum(a[1:], a[0]), "*": lambda *a: math.prod(a), "-": lambda a, b=None: -a if b is None else a - b, "/": lambda a, b: a / b,
          "mod": lambda a, b: a % b, "=": lambda a, b: a == b, "!=": lambda a, b: a != b, "<": lambda a, b: a < b, "<=": lambda a, b: a <= b,
          ">": lambda a, b: a > b, ">=": lambda a, b: a >= b, "min": min, "max": max, "abs": abs, "floor": math.floor, "exp": math.exp,
          "log": math.log, "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "pow": math.pow, "atan2": math.atan2}
_CMP = {"<", "<=", ">", ">=", "=", "!="}
_BOOLISH = _CMP | {"and", "or", "not", "chance"}
_COMM = {"+", "*", "=", "!=", "min", "max"}
_SIDE = set(STMTS) | {"put", "drop", "after"}


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _draws(x):
    if isinstance(x, list):
        return bool(x) and ((isinstance(x[0], str) and x[0] in DRAWS) or any(_draws(y) for y in x))
    return False


_IMPURE = set(BODYREG) | {"speed"} | set(READS)


def _impure(x):
    """Reads the body's or blocks' state, which statements other than (set name ...) can change (a thrust, bset, respawn, a velocity
    written): never inlined (stage 2c; the checker's speed-past-vx case)."""
    if isinstance(x, list):
        return any(_impure(y) for y in x)
    return isinstance(x, str) and x in _IMPURE


def _syms(x, out=None):
    out = set() if out is None else out
    if isinstance(x, list):
        for y in x:
            _syms(y, out)
    elif isinstance(x, str):
        out.add(x)
    return out


class _Norm:
    """The world's parts after rewriting, in the shape canonical() and _prune() read."""

    def __init__(self, w):
        self.consts, self.lets, self.tables = list(w.consts), list(w.lets), list(w.tables)
        self.told, self.told_wait, self.stream = w.told, w.told_wait, w.stream
        self.rules = {s: list(r) for s, r in w.rules.items()}
        self.vars, self.tabs = set(w.vars), set(w.tabs)


def _range(x, stage):
    """(lo, hi, integer) of an expression over every life up to H_LIFE, or None if unknown. t's hi is just below H_LIFE."""
    if _num(x):
        return (x, x, float(x).is_integer())
    if isinstance(x, str):
        if x == "t":
            return (0.0, H_LIFE - 1e-9, False)
        if x in ("P", "F") or (x in ("eye", "thruster", "motor") and stage in LOCALS and x in LOCALS[stage]):
            return (0, 1, True)
        return None
    op, *a = x
    r = [_range(y, stage) for y in a]
    if any(v is None for v in r):
        return None
    if op == "floor":
        return (math.floor(r[0][0]), math.floor(r[0][1]), True)
    if op == "/" and _num(a[1]) and a[1] > 0:
        return (r[0][0] / a[1], r[0][1] / a[1], False)
    if op == "*" and len(a) == 2 and _num(a[1]) and a[1] > 0:
        return (r[0][0] * a[1], r[0][1] * a[1], r[0][2] and float(a[1]).is_integer())
    if op == "+":
        return (sum(v[0] for v in r), sum(v[1] for v in r), all(v[2] for v in r))
    if op == "-" and len(a) == 2:
        return (r[0][0] - r[1][1], r[0][1] - r[1][0], r[0][2] and r[1][2])
    if op == "mod" and _num(a[1]) and a[1] > 0 and float(a[1]).is_integer():
        if r[0][2] and 0 <= r[0][0] and r[0][1] < a[1]:
            return r[0]
        return (0, a[1] - 1, True) if r[0][2] else (0, a[1], False)
    return None


def _truth(x, stage):
    """True, False, or None if not known in every life."""
    if _num(x):
        return bool(x)
    if isinstance(x, list) and x and x[0] in _CMP and len(x) == 3:
        a, b = _range(x[1], stage), _range(x[2], stage)
        if a is None or b is None:
            return None
        op = x[0]
        if op == "<":
            return True if a[1] < b[0] else False if a[0] >= b[1] else None
        if op == "<=":
            return True if a[1] <= b[0] else False if a[0] > b[1] else None
        if op == ">":
            return True if a[0] > b[1] else False if a[1] <= b[0] else None
        if op == ">=":
            return True if a[0] >= b[1] else False if a[1] < b[0] else None
        if op in ("=", "!="):
            if a[1] < b[0] or b[1] < a[0]:
                return op == "!="
            if a[0] == a[1] == b[0] == b[1]:
                return op == "="
    return None


def _fold(x, stage):
    """An expression, simplified with its value unchanged in every life up to H_LIFE: arithmetic on literals done, identities (x + 0, x * 1,
    x - 0, x / 1) removed, comparisons and conditions decided where every life agrees. Draws are never removed or duplicated."""
    if not isinstance(x, list):
        return x
    op, *a = x
    a = [_fold(y, stage) for y in a]
    if op in ("and", "or"):
        while len(a) > 1 and _truth(a[0], stage) is not None and not _draws(a[0]):
            t = _truth(a[0], stage)
            if (op == "and") == t:                     # a leading truthy in and, or falsy in or, is skipped
                a = a[1:]
            else:
                return a[0] if _num(a[0]) else int(t)     # the value Python's and/or would return
        return a[0] if len(a) == 1 else [op] + a
    if op == "if" and len(a) == 3:
        t = _truth(a[0], stage)
        if t is not None and not _draws(a[0]):
            return a[1] if t else a[2]
        if a[1] == a[2] and not _draws(a[0]):
            return a[1]
        return [op] + a
    if op == "not":
        t = _truth(a[0], stage)
        return [op] + a if t is None or _draws(a[0]) else int(not t)
    if op in _ARITH and a and all(_num(y) for y in a):
        try:
            v = _ARITH[op](*a)
            if isinstance(v, bool):
                v = int(v)
            if _num(v) and math.isfinite(v):
                return v
        except (ValueError, ZeroDivisionError, OverflowError, TypeError):
            pass
    if op == "+":
        b = [y for y in a if not (_num(y) and y == 0)]
        return b[0] if len(b) == 1 else ([op] + b if b else 0)
    if op == "*":
        b = [y for y in a if not (_num(y) and y == 1)]
        return b[0] if len(b) == 1 else ([op] + b if b else 1)
    if op == "-" and len(a) == 2 and _num(a[1]) and a[1] == 0:
        return a[0]
    if op == "/" and len(a) == 2 and _num(a[1]) and a[1] == 1:
        return a[0]
    if op in _CMP:
        t = _truth([op] + a, stage)
        if t is not None and not _draws(a):
            return int(t)
    if op == "mod" and len(a) == 2:
        r = _range(a[0], stage)
        if r and _num(a[1]) and a[1] > 0 and r[2] and 0 <= r[0] and r[1] < a[1]:
            return a[0]
    if op == "floor":
        r = _range(a[0], stage)
        if r and math.floor(r[0]) == math.floor(r[1]) and not _draws(a[0]):
            return math.floor(r[0])
    return [op] + a


def _fold_st(x, stage):
    """A statement, simplified: a list of statements (empty if it provably never acts within H_LIFE)."""
    op, *a = x
    if op == "set":
        e = _fold(a[1], stage)
        return [] if e == a[0] else [["set", a[0], e]]
    if op == "if":
        c = _fold(a[0], stage)
        t = _truth(c, stage)
        if t is not None and not _draws(c):
            return _fold_st(a[1], stage) if t else (_fold_st(a[2], stage) if len(a) > 2 else [])
        th = _fold_st(a[1], stage)
        el = _fold_st(a[2], stage) if len(a) > 2 else []
        if not th and not el and not _draws(c):
            return []
        one = lambda b: b[0] if len(b) == 1 else ["do"] + b
        return [["if", c, one(th)] + ([one(el)] if el else [])]
    if op == "do":
        return [y for s in a for y in _fold_st(s, stage)]
    if op in ("repeat", "after"):
        n = _fold(a[0], stage)
        if _num(n) and ((op == "repeat" and n < 1) or (op == "after" and n >= H_LIFE)):
            return []                                   # (repeat 0 ...) never runs; (after d ...) with d past every life never runs
        body = [y for s in a[1:] for y in _fold_st(s, stage)]
        return [[op, n] + body] if body or _draws(n) else []
    if op == "each":
        body = [y for s in a[1:] for y in _fold_st(s, stage)]
        return [[op, a[0]] + body] if body else []
    if op == "until":
        c, n = _fold(a[0], stage), _fold(a[1], stage)
        body = [y for s in a[2:] for y in _fold_st(s, stage)]
        return [[op, c, n] + body] if body else []
    return [[op] + [_fold(y, stage) for y in a]]


def _walk_sets(x, out, path=()):
    if isinstance(x, list) and x:
        if x[0] == "set" and len(x) == 3:
            out.append((x, path))
        for i, y in enumerate(x):
            _walk_sets(y, out, path + (x[0],))


def _count(x, name):
    if isinstance(x, list):
        return sum(_count(y, name) for y in x)
    return int(x == name)


def _writes_of(x):
    """Symbols a statement may change, and whether it has other side effects (any statement but set)."""
    out, side = set(), False
    if isinstance(x, list) and x:
        if x[0] == "set":
            out.add(x[1])
        elif x[0] == "put":
            out.add(x[1])
        elif x[0] in _SIDE:
            side = True
        for y in x[1:]:
            o, s = _writes_of(y)
            out |= o
            side |= s
    return out, side


def _subst(x, name, e):
    if isinstance(x, list):
        return [_subst(y, name, e) for y in x]
    return e if x == name else x


def _inline(n):
    """A state variable written by one top-level (set v e) and read once, later in the same stage's list, not in a loop or deferral, with
    nothing between that changes what e reads, and e draw-free: e takes the read's place, and the set goes. Its value never outlives the
    tick, so the let's start is never read. Fixpoint."""
    changed = True
    while changed:
        changed = False
        for v in sorted(n.vars):
            sets = []
            for s, rs in n.rules.items():
                for r in rs:
                    _walk_sets(r, sets)
            mine = [(x, p) for x, p in sets if x[1] == v]
            if len(mine) != 1 or mine[0][1]:
                continue
            stmt = mine[0][0]
            st = next(s for s, rs in n.rules.items() if any(r is stmt for r in rs))
            rs = n.rules[st]
            i = next(k for k, r in enumerate(rs) if r is stmt)
            e = stmt[2]
            if _draws(e) or _count(e, v) or _impure(e):
                continue
            others = sum(_count(r, v) for s, rr in n.rules.items() for r in rr) - 1
            others += _count([n.told, n.told_wait] + [x for _, x in n.lets] + [list(t[1:]) for t in n.tables] + [x for _, x in n.consts], v)
            if others != 1:
                continue
            j = next((k for k, r in enumerate(rs) if k != i and _count(r, v)), None)
            if j is None or j < i:
                continue
            reads = _syms(e)
            between = rs[i + 1:j + 1]
            blocked = False
            for b in between:
                w_, side = _writes_of(b)
                if (w_ & reads) or (side and b is not rs[j]):
                    blocked = True
            target = rs[j]

            def in_loop(x, inside=False):
                if isinstance(x, list):
                    inner = inside or bool(x and x[0] in ("each", "repeat", "until", "after"))
                    return any(in_loop(y, inner) for y in x)
                return inside and x == v
            if blocked or in_loop(target):
                continue
            # the read within the target must come before any write in it to what e reads: only a plain (set r expr) or (if c ...) whose writes miss e's reads
            if _writes_of(target)[0] & reads:
                continue
            n.rules[st] = rs[:i] + rs[i + 1:j] + [_subst(target, v, e)] + rs[j + 1:]
            changed = True
            break


def normalise(w):
    """The normal form: every rewrite keeps every life the same within H_LIFE (lab/stage2b_dl.py checks lives exact on the hand worlds)."""
    n = _Norm(w)
    n.consts = [(c, _fold(v, "birth")) for c, v in n.consts if _fold(v, "birth") != c]
    n.lets = [(k, _fold(v, "birth")) for k, v in n.lets]
    n.tables = [(k, _fold(a, "birth"), _fold(b, "birth"), _fold(v, "birth")) for k, a, b, v in n.tables]
    n.told = _fold(n.told, "tick") if n.told is not None else None
    n.told_wait = _fold(n.told_wait, "tick") if n.told_wait is not None else None
    for s in STAGES:
        n.rules[s] = [y for r in n.rules[s] for y in _fold_st(r, s)]
    _inline(n)
    for s in STAGES:                                    # (inlining may leave something to fold)
        n.rules[s] = [y for r in n.rules[s] for y in _fold_st(r, s)]
    # a register written only with its own default never changes: poison is P unless written; a firing's gain is 1 on entry
    sets = []
    for s, rs in n.rules.items():
        for r in rs:
            _walk_sets(r, sets)
    for reg, default, stages in (("poison", "P", STAGES), ("gain", 1, ("fire",))):
        mine = [x for x, _ in sets if x[1] == reg]
        if mine and all(x[2] == default for x in mine):
            for s in stages:
                n.rules[s] = [y for r in n.rules[s] for y in _fold_st(_drop_sets(r, reg), s)]
    return n


def _drop_sets(x, reg):
    """The statement with every (set reg ...) replaced by (do)."""
    if isinstance(x, list) and x:
        if x[0] == "set" and x[1] == reg:
            return ["do"]
        return [x[0]] + [_drop_sets(y, reg) for y in x[1:]]
    return x


def to_text(n, stream=None):
    """A normal form as world text, to compile and live (the exact-lives check)."""
    parts = ["world"]
    if stream is not None:
        parts.append(["stream", stream])
    parts += [["const", c, v] for c, v in n.consts] + [["let", k, v] for k, v in n.lets] + [["table", k, a, b, v] for k, a, b, v in n.tables]
    if n.told is not None:
        parts.append(["told", n.told])
    if n.told_wait is not None:
        parts.append(["told-wait", n.told_wait])
    parts += [["on", s] + n.rules[s] for s in STAGES if n.rules[s]]
    return show(parts)


def canonical(w, normal=True):
    """(structure, parameters) of the normal form. As stage 2a's (_canonical_2a), and: lets and tables emitted in order of first use (a let
    read by another's start stays after it); the operands of +, *, =, !=, min, max (and of and/or when all are truth values) sorted; each
    operand's numbers go with it to the parameter string."""
    n = normalise(w) if normal else _Norm(w)            # normal=False: the text as written (pruned and rendered alike)
    live, rules = _prune(n)
    names = {}

    def nm(s):
        if s not in names:
            names[s] = f"v{len(names)}"
        return names[s]

    def go(x):
        if isinstance(x, list):
            parts = [go(y) for y in x]
            head, rest = parts[0], parts[1:]
            op = x[0] if x and isinstance(x[0], str) else None
            exact = op in ("=", "!=", "min", "max") or (op in ("+", "*") and len(x) == 3)      # (3 or more floats don't commute exactly)
            if not any(_draws(y) for y in x[1:]) and (exact or (op in ("and", "or") and all(isinstance(y, list) and y and y[0] in _BOOLISH for y in x[1:]))):
                rest = sorted(rest)                     # never operands that draw: their order is the order of draws (stage 2c)
            return ("(" + " ".join([head[0]] + [r[0] for r in rest]) + ")", head[1] + [p for r in rest for p in r[1]])
        if _num(x):
            return ("#", [grid(x)])
        if x in live or x in n.vars or x in n.tabs:
            return (nm(x), [])
        if x in VOCAB:
            return (x, [])
        return (nm(x), [])                              # an (each) variable
    parts, params = [], []

    def emit(s, p):
        parts.append(s)
        params.extend(p)
    for c, v in sorted(n.consts, key=lambda c: c[0]):
        s, p = go(v)
        emit("(const " + c + " " + s + ")", p)
    for s in STAGES:
        if rules[s]:
            g = [go(r) for r in rules[s]]
            emit(f"(on {s} " + " ".join(x[0] for x in g) + ")", [p for x in g for p in x[1]])
    if n.told is not None:
        s, p = go(n.told)
        emit("(told " + s + ")", p)
    if n.told_wait is not None:
        s, p = go(n.told_wait)
        emit("(told-wait " + s + ")", p)
    decl = [(k, ("let", v)) for k, v in n.lets if k in live] + [(k, ("table", a, b, v)) for k, a, b, v in n.tables if k in live]
    for k, _ in decl:
        nm(k)
    done, out = set(), []
    drawn = [d for d in decl if _draws(list(d[1][1:]))]           # these keep their order (lets, then tables, as init runs them):
    pending = sorted([d for d in decl if d not in drawn], key=lambda d: int(names[d[0]][1:])) + drawn      # it is the order of draws
    while pending:                                      # first-use order, a declaration after any it reads
        for d in pending:
            needs = _syms(list(d[1][1:])) & (set(k for k, _ in decl) - done - {d[0]})
            if not needs:
                break
        pending.remove(d)
        done.add(d[0])
        k, (kind, *rest) = d
        g = [go(y) for y in rest]
        emit(f"({kind} " + nm(k) + " " + " ".join(x[0] for x in g) + ")", [p for x in g for p in x[1]])
    return "\n".join(parts), " ".join(params)


def grid(x):
    """A number on a 5% log grid (D30), its sign kept, zero its own."""
    if x == 0:
        return "z"
    i = int(round(math.log(abs(x)) / math.log(1.05)))
    return ("-" if x < 0 else "") + str(i)


LZ = [{"id": lzma.FILTER_LZMA2, "preset": 9 | lzma.PRESET_EXTREME, "dict_size": 1 << 24}]


def _lz(s):
    return 8 * len(lzma.compress(s.encode(), format=lzma.FORMAT_RAW, filters=LZ)) if s else 0


def corpus():
    a, b = open(os.path.join(HERE, "corpus.txt")).read().split("\n%%\n")
    return a, b


CORPUS_SHA = "see corpus.sha256"


def bits(w, normal=True):
    """Description length, bits: LZMA of the canonical form given the frozen corpus, structure and parameters apart (lab/synth_controls.py's method)."""
    a, b = canonical(w, normal)
    ra, rb = corpus()
    if not a and not b:
        return 0
    return (_lz(ra + "\n" + a) - _lz(ra)) + (_lz(rb + "\n" + b) - _lz(rb) if b else 0)


def canon_sha(w):
    return hashlib.sha256("\n%\n".join(canonical(w)).encode()).hexdigest()


def canon_sha_2a(w):
    return hashlib.sha256("\n%\n".join(_canonical_2a(w)).encode()).hexdigest()


def write_corpus():
    """The vocabulary, every word once, in a fixed order; the grid indices of the numbers 1 to 16, and a spread of others, as parameters. No world is in it. Run once, then frozen."""
    a = " ".join("(" + v + ")" for v in VOCAB) + "\n# #\n"
    b = " ".join(grid(x) for x in list(range(1, 17)) + [0, 0.5, 0.25, 0.1, 0.05, 0.01, 100, 1000])
    p = os.path.join(HERE, "corpus.txt")
    with open(p, "w") as f:
        f.write(a + "\n%%\n" + b)
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    with open(p + ".sha256", "w") as f:
        f.write(h + "\n")
    return h


def _canon_stream(self):
    """A stream offset from the canonical form, when a world names none (so two different worlds don't share draws)."""
    return int(canon_sha_2a(self)[:7], 16)


World.canon_stream = _canon_stream

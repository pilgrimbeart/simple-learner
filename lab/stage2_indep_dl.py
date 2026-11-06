"""stage2_indep_dl.py: independent check 4 (PROGRAMME.md, gate 2 to 3): description length (lang.bits). Is it
invariant to renaming state and (each) variables, to comments, meta, stream and whitespace, as claimed; what does it do
under changes that keep the meaning (declarations reordered, a dead variable, x+0) and under small changes that don't
(10 s to 10.1 s, 11 s); and how does it rank worlds.

    .venv/bin/python lab/stage2_indep_dl.py"""
import random
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from stage2_lang import lang, worlds as WW


def names_of(tree):
    out = set()
    for item in tree[1:]:
        if item[0] in ("let", "table"):
            out.add(item[1])

    def walk(x):
        if isinstance(x, list):
            if x and x[0] == "each":
                out.add(x[1])
            for y in x:
                walk(y)
    walk(tree)
    return out


def renamed(text, seed):
    tree = lang.parse(text)
    r = random.Random(seed)
    m = {n: "q" + "".join(r.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(6)) for n in names_of(tree)}

    def sub(x):
        if isinstance(x, list):
            if x and x[0] == "meta":
                return x
            return [sub(y) for y in x]
        return m.get(x, x) if isinstance(x, str) else x
    return lang.show(sub(tree)), m


def stripped(text):
    tree = lang.parse(text)
    return lang.show([x for x in tree if not (isinstance(x, list) and x and x[0] in ("meta", "stream"))])


def reorder_lets(text, seed):
    tree = lang.parse(text)
    lets = [x for x in tree[1:] if x[0] == "let"]
    rest = [x for x in tree[1:] if x[0] != "let"]
    random.Random(seed).shuffle(lets)
    return lang.show(["world"] + lets + rest)


def b(text):
    return lang.bits(lang.World(text))


if __name__ == "__main__":
    print("== invariance, every world of worlds.py", flush=True)
    bad = []
    for name, d in WW.W.items():
        t = d["text"]
        b0, s0 = b(t), lang.canon_sha(lang.World(t))
        for k in range(3):
            t2, m = renamed(t, k)
            if b(t2) != b0 or lang.canon_sha(lang.World(t2)) != s0:
                bad.append((name, "rename", m, b0, b(t2)))
        t3 = "; a comment\n" + stripped(t).replace(" ", "  \n ")
        if b(t3) != b0:
            bad.append((name, "comments, meta, stream, whitespace", b0, b(t3)))
        if sum(1 for x in lang.parse(t) if isinstance(x, list) and x[0] == "let") > 1:
            for k in range(3):
                t4 = reorder_lets(t, k)
                if b(t4) != b0:
                    bad.append((name, "lets reordered", b0, b(t4)))
                    break
    print(f"  {len(WW.W)} worlds, 3 renamings each, comments/meta/stream/whitespace, lets reordered: {len(bad)} changes", flush=True)
    for x in bad:
        print("   ", x, flush=True)
    print("== meaning kept, text changed / meaning changed, text nearly kept", flush=True)
    base = "(world (on tick (set poison (mod (+ P (floor (/ t 10))) 2))))"
    for label, t in [("swap10", base),
                     ("swap10, a dead variable", "(world (let junk 3) (on tick (set junk (+ junk 1)) (set poison (mod (+ P (floor (/ t 10))) 2))))"),
                     ("swap10, + 0", "(world (on tick (set poison (+ 0 (mod (+ P (floor (/ t 10))) 2)))))"),
                     ("swap10, operands commuted", "(world (on tick (set poison (mod (+ (floor (/ t 10)) P) 2))))"),
                     ("swap10, via a variable", "(world (let k 0) (on tick (set k (floor (/ t 10))) (set poison (mod (+ P k) 2))))"),
                     ("swap every 10.1 s", "(world (on tick (set poison (mod (+ P (floor (/ t 10.1))) 2))))"),
                     ("swap every 11 s", "(world (on tick (set poison (mod (+ P (floor (/ t 11))) 2))))"),
                     ("swap every 1000 s (never)", "(world (on tick (set poison (mod (+ P (floor (/ t 1000))) 2))))")]:
        w = lang.World(t)
        print(f"  {label}: {lang.bits(w)} bits, canonical {lang.canon_sha(w)[:8]}", flush=True)
    print("== ranking, every world of worlds.py", flush=True)
    rows = sorted((lang.bits(lang.World(d["text"], n)), n) for n, d in WW.W.items())
    for bits, n in rows:
        print(f"  {bits:5d}  {n}", flush=True)

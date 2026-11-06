"""stage2_indep2_dl.py: description length on the stage-2b normal form (lang.normalise, lang.canonical, lang.bits).

  invariance   my earlier rewrites (lab/stage2_indep_dl.py) on every world of worlds.py, and new meaning-preserving ones
  soundness    is the normal form's meaning the world's? to_text(normalise(w)) lived in lockstep against w; and pairs of worlds with
               different lives that get one canonical form
  ranking      every world

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage2_indep2_dl.py"""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from stage2_lang import lang, worlds as WW
from stage2_indep_dl import renamed, stripped, reorder_lets
from stage2_indep_identity import Proxy, brain_maker, state_life

COL = ("red", "blue")


def b(t):
    return lang.bits(lang.World(t, compile_only=True))


def sha(t):
    return lang.canon_sha(lang.World(t, compile_only=True))[:8]


SW = "(mod (+ P (floor (/ t 10))) 2)"
# (label, original, rewrite): each rewrite means the same in every life
SAME = [
    ("+ 0", f"(world (on tick (set poison {SW})))", f"(world (on tick (set poison (+ 0 {SW}))))"),
    ("operands commuted", f"(world (on tick (set poison {SW})))", "(world (on tick (set poison (mod (+ (floor (/ t 10)) P) 2))))"),
    ("via a variable", f"(world (on tick (set poison {SW})))", "(world (let k 0) (on tick (set k (floor (/ t 10))) (set poison (mod (+ P k) 2))))"),
    ("a dead variable", f"(world (on tick (set poison {SW})))", f"(world (let junk 3) (on tick (set junk (+ junk 1)) (set poison {SW})))"),
    ("never", "(world)", "(world (let last -1) (on tick (set poison (if (< t 1000) P last))) (on score (if (>= t 1000) (set last colour))))"),
    ("> against <", "(world (on tick (set poison (if (> t 50) F P))))", "(world (on tick (set poison (if (< 50 t) F P))))"),
    ("if negated, branches swapped", "(world (on tick (set poison (if (> t 50) F P))))", "(world (on tick (set poison (if (not (> t 50)) P F))))"),
    ("<= against not >", "(world (on tick (set poison (if (<= t 50) P F))))", "(world (on tick (set poison (if (not (> t 50)) P F))))"),
    ("statement if against expression if", "(world (on tick (set poison (if (> t 50) F P))))", "(world (on tick (if (> t 50) (set poison F) (set poison P))))"),
    ("(* 2 x) against (+ x x)", "(world (on fire (set gain (* 2 gain))))", "(world (on fire (set gain (+ gain gain))))"),
    ("(* 0.5 PUSH) as const against gain .5", "(world (const PUSH (* 0.5 PUSH)) (const TURN (* 0.5 TURN)))", "(world (on fire (set gain 0.5)))"),
    ("one tick clause against two", "(world (let a 0) (on tick (set a (+ a 1)) (set poison (mod (floor (/ a 1000)) 2))))",
     "(world (let a 0) (on tick (set a (+ a 1))) (on tick (set poison (mod (floor (/ a 1000)) 2))))"),
    ("De Morgan", "(world (on tick (set poison (if (and (> t 20) (< t 60)) F P))))", "(world (on tick (set poison (if (not (or (<= t 20) (>= t 60))) F P))))"),
    ("nested do", "(world (on tick (set poison (if (> t 50) F P))))", "(world (on tick (do (do (set poison (if (> t 50) F P))))))"),
    ("(- 0 x) against (- x)", "(world (on meal (set sign (- 0 sign))))", "(world (on meal (set sign (- sign))))"),
    ("double not", "(world (on tick (set poison (if (> t 50) F P))))", "(world (on tick (set poison (if (not (not (> t 50))) F P))))"),
    ("F against (- 1 P)", "(world (on tick (set poison (if (> t 50) F P))))", "(world (on tick (set poison (if (> t 50) (- 1 P) P))))"),
    ("swap by mod against by if", f"(world (on tick (set poison {SW})))", "(world (on tick (set poison (if (= (mod (floor (/ t 10)) 2) 0) P F))))"),
    ("a never-acting rule on a counter", "(world)", "(world (let n 0) (on score (set n (+ n 1))) (on tick (if (> n 100000) (set poison F))))"),
    ("a rule acting at 33 s written as t*30 > 1000", "(world (on tick (if (> t 33.34) (set poison F))))", "(world (on tick (if (> (* t 30) 1000) (set poison F))))"),
]

# pairs that look alike but live differently: they must not share a normal form (and to_text(normalise) must live as the world)
DIFFER = {
    "speed read before vx halves (inlined past it?)": "(world (let s 0) (on move (set s speed) (set vx (* 0.5 vx)) (set vy (* 0.5 vy)) (if (> s 0.012) (set spin (* 0.5 spin)))))",
    "the same, speed read after": "(world (on move (set vx (* 0.5 vx)) (set vy (* 0.5 vy)) (if (> speed 0.012) (set spin (* 0.5 spin)))))",
    "dist read before x moves (inlined past it?)": "(world (let d 0) (on tick (set d (dist 0.03 0.03)) (set x (+ x 0.0005)) (if (< d 0.02) (set poison F))))",
    "the same, dist read after": "(world (on tick (set x (+ x 0.0005)) (if (< (dist 0.03 0.03) 0.02) (set poison F))))",
    "near read before a meal-time move": "(world (let q 0) (on move (set q (near -1 0.003)) (set heading (+ heading 0.3)) (if (> q 0) (set spin 0))))",
    "the same, near read after": "(world (on move (set heading (+ heading 0.3)) (if (> (near -1 0.003) 0) (set spin 0))))",
    "draws: chance first": "(world (on tick (set poison (if (and (chance 0.5) (< t 50)) F P))))",
    "draws: chance second": "(world (on tick (set poison (if (and (< t 50) (chance 0.5)) F P))))",
}


def nf_text(w):
    """The normal form as text, drawing from the world's own stream (a world naming none draws at an offset of its 2a canonical form)."""
    return lang.to_text(lang.normalise(w), w.stream if w.stream is not None else 7_000_000 + int(w.canon_stream()))


def lockstep(job):
    ta, tb, kind, seed, first = job
    from stage2_lang.sim import WLife
    A = WLife(seed, first, lambda s: Proxy(brain_maker(kind)(s)), lang.World(ta))
    B = WLife(seed, first, lambda s: Proxy(brain_maker(kind)(s)), lang.World(tb))
    for k in range(10000):
        A.step()
        B.step()
        if not np.array_equal(state_life(A), state_life(B)) or A.brain.log != B.brain.log:
            return k
    return None


if __name__ == "__main__":
    print("== invariance on every world of worlds.py: 3 renamings, comments/meta/stream/whitespace, lets reordered", flush=True)
    bad, n = [], 0
    for name, d in WW.W.items():
        t = d["text"]
        try:
            b0 = b(t)
        except Exception as e:
            print(f"  {name}: {type(e).__name__} {e}", flush=True)
            continue
        n += 1
        for k in range(3):
            t2, m = renamed(t, k)
            if b(t2) != b0:
                bad.append((name, "rename", b0, b(t2)))
        if b("; c\n" + stripped(t).replace(" ", "  \n ")) != b0:
            bad.append((name, "comments etc", b0))
        for k in range(3):
            t4 = reorder_lets(t, k)
            if b(t4) != b0:
                bad.append((name, "lets reordered", b0, b(t4)))
                break
    print(f"  {n} worlds: {len(bad)} changes {bad}", flush=True)
    print("== meaning-preserving rewrites: bits original -> rewrite (canonical)", flush=True)
    moved = 0
    for label, a, c in SAME:
        ba, bc = b(a), b(c)
        moved += ba != bc
        print(f"  {'MOVES ' if ba != bc else 'same  '} {label}: {ba} -> {bc} ({sha(a)} {sha(c)})", flush=True)
    print(f"  {moved} of {len(SAME)} move", flush=True)
    names = list(DIFFER)
    with ProcessPoolExecutor(7) as ex:
        print("== do the rewrites in SAME really keep the lives? (lockstep, 20 lives each)", flush=True)
        for label, a, c in SAME:
            R = list(ex.map(lockstep, [(a, c, "circuit", s, col) for s in range(64700, 64710) for col in COL]))
            print(f"  {label}: {sum(r is None for r in R)} of {len(R)} identical", flush=True)
        print("== soundness: the world against to_text(normalise(world)), lockstep; and pairs that differ", flush=True)
        for name in names:
            t = DIFFER[name]
            w = lang.World(t)
            nt = nf_text(w)
            R = list(ex.map(lockstep, [(t, nt, "circuit", s, col) for s in range(64700, 64710) for col in COL]))
            print(f"  {name}: bits {lang.bits(w)}, canonical {lang.canon_sha(w)[:8]}; normal form {nt}; lives as the world {sum(r is None for r in R)} of {len(R)}", flush=True)
        for i in range(0, len(names), 2):
            a, c = DIFFER[names[i]], DIFFER[names[i + 1]]
            R = list(ex.map(lockstep, [(a, c, "circuit", s, col) for s in range(64700, 64710) for col in COL]))
            print(f"  pair '{names[i]}' / '{names[i + 1]}': same canonical {sha(a) == sha(c)}; lives identical {sum(r is None for r in R)} of {len(R)}", flush=True)
        print("== every world of worlds.py: its normal form lives as it does? (lockstep, 6 lives each)", flush=True)
        for name, d in WW.W.items():
            try:
                w = lang.World(d["text"], name)
            except Exception:
                continue
            nt = nf_text(w)
            R = list(ex.map(lockstep, [(d["text"], nt, "circuit", s, col) for s in range(64710, 64713) for col in COL]))
            if any(r is not None for r in R):
                print(f"  {name}: {sum(r is None for r in R)} of {len(R)} identical; first ticks {[r for r in R if r is not None][:3]}", flush=True)
        print("  (only worlds whose normal form lives differently are listed)", flush=True)
    print("== ranking", flush=True)
    rows = []
    for nme, d in WW.W.items():
        try:
            rows.append((b(d["text"]), nme))
        except Exception as e:
            rows.append((-1, f"{nme} ({type(e).__name__})"))
    print("  " + ", ".join(f"{n} {x}" for x, n in sorted(rows)), flush=True)

"""stage2b_gen.py: stage 2b, part 3. A generator of worlds from the grammar (GRAMMAR.md: a world is one or more statements, "at this link,
change this, in this way"), with a written prior over constructs. Frozen, with its SHA-256 logged, before any world was drawn.

World number n (n = 0, 1, 2, ...) is drawn from its own stream, numpy's default_rng(first 8 hex digits of SHA-256 of "gen2b:n"), so a
world is a function of its number alone. A world number held out by PROGRAMME.md's rule (the first byte of SHA-256 of "world:n" divisible
by 4) is never drawn: `development(k)` gives the first k numbers that aren't held out.

The prior (every probability here is the generator's whole definition):
  statements in a world      1: .6, 2: .3, 3: .1
  link of a statement        L1 motor to thrust .14, L2 the body's dynamics .12, L3 blocks .12, L4 optics .10, L5 eye to pulse .12,
                             L6 the mouth .08, L7 a meal's worth .24, L9 the score .08. (L8, the taste, and L0, the brain, have nothing
                             within the current constraints: stage 5's and outside the language.)
  construct within a link    uniform over the link's list in CONSTRUCTS
  time course                fixed .45; on from a moment T ~ U(20, 80) s .2; off from T .1; a cycle, on for half of a period
                             P ~ U(5, 40) s .15; bursts, on and off by a hidden chain flipping at lam ~ log-U(.05, .5) a second, .1.
                             A construct marked "fixed" (it acts at birth, or as a constant) ignores the draw.
  parameters                 each construct's own draws, stated beside it below
Lie constructs (L7 lie) go last among a world's tick rules, so they lie about whatever rule the others set; the first one's told clause
tells the rule before the lie. Names are suffixed by the statement's index, so statements never share state."""
import hashlib
import math
import sys
import numpy as np

LINKS = {"L1": 0.14, "L2": 0.12, "L3": 0.12, "L4": 0.10, "L5": 0.12, "L6": 0.08, "L7": 0.24, "L9": 0.08}
NSTAT = {1: 0.6, 2: 0.3, 3: 0.1}
COURSE = {"fixed": 0.45, "from": 0.2, "until": 0.1, "cycle": 0.15, "bursts": 0.1}


def lu(r, a, b):
    return float(math.exp(r.uniform(math.log(a), math.log(b))))


def g(x):
    """A number in the text, rounded to 4 significant figures."""
    return float(f"{x:.4g}")


# Each construct: (name, fixed?, maker(r, i, G) -> dict(stage -> [rules], lets=[...], tables=[...], consts=[...], told=..., told_wait=...))
# G is the gate's condition (text) or None for always.
def _gate(G, s):
    return s if G is None else f"(if {G} {s})"


def c_gain_one(r, i, G):
    k = g(lu(r, 0.25, 4.0))
    return dict(lets=[f"(let k{i} (int 2))"], fire=[_gate(G, f"(if (= thruster k{i}) (set gain {k}))")], what=f"one thruster's gain x{k}")


def c_gain_both(r, i, G):
    k = g(lu(r, 0.25, 4.0))
    return dict(fire=[_gate(G, f"(set gain {k})")], what=f"both thrusters' gain x{k}")


def c_fail(r, i, G):
    return dict(lets=[f"(let k{i} (int 2))"], fire=[_gate(G, f"(if (= thruster k{i}) (drop))")], what="one thruster fails")


def c_flaky(r, i, G):
    p = g(r.uniform(0.1, 0.6))
    return dict(fire=[_gate(G, f"(if (chance {p}) (drop))")], what=f"each firing lost with chance {p}")


def c_spurious(r, i, G):
    f = g(lu(r, 0.5, 5.0))
    return dict(lets=[f"(let k{i} (int 2))"], tick=[_gate(G, f"(if (chance (* {f} TICK)) (thrust k{i}))")], what=f"one thruster fires by itself, {f} a second")


def c_lag(r, i, G):
    d = g(r.uniform(0.02, 0.5))
    return dict(fire=[_gate(G, f"(do (drop) (after {d} (thrust thruster)))")], what=f"thrust {d} s late")


def c_mirror(r, i, G):
    return dict(fire=["(do (drop) (thrust (- 1 thruster)))"], what="steering reversed from birth")


def _const(name, lo, hi):
    def c(r, i, G):
        f = g(lu(r, lo, hi))
        if G is None:
            return dict(consts=[f"(const {name} (* {f} {name}))"], what=f"{name} x{f}")
        return dict(lets=[f"(let z{i} {name})"], tick=[f"(set {name} (if {G} (* {f} z{i}) z{i}))"], what=f"{name} x{f}")
    return c


def c_current(r, i, G):
    v, a = g(lu(r, 0.002, 0.02)), g(r.uniform(0, 2 * math.pi))
    return dict(move=[_gate(G, f"(do (set x (+ x (* {g(v * math.cos(a))} TICK))) (set y (+ y (* {g(v * math.sin(a))} TICK))))")], what=f"a current {v * 1000:.3g} mm/s")


def c_spinbias(r, i, G):
    w = g(lu(r, 0.05, 1.0) * (1 if r.random() < 0.5 else -1))
    return dict(move=[_gate(G, f"(set heading (+ heading (* {w} TICK)))")], what=f"the body turns by itself, {w} rad/s")


def c_blocks(r, i, G):
    n = int(r.integers(2, 25))
    return dict(consts=[f"(const BLOCKS {n})"], what=f"{n} blocks of each colour")


def c_moving(r, i, G):
    v = g(lu(r, 0.001, 0.01))
    return dict(tables=[f"(table a{i} N 1 (uniform 0 TWOPI))"],
                tick=[_gate(G, f"(each b (bset b (+ (bx b) (* {v} (cos (at a{i} b)) TICK)) (+ (by b) (* {v} (sin (at a{i} b)) TICK))))")], what=f"blocks drift {v * 1000:.3g} mm/s")


def c_clumps(r, i, G):
    c, sd = int(r.integers(1, 7)), g(lu(r, 0.002, 0.01))
    return dict(tables=[f"(table c{i} {c} 2 (uniform 0 WORLD))"], lets=[f"(let j{i} 0)"], birth=["(each b (respawn b))"],
                respawn=[f"(until (> (dist nx ny) (+ (* 3 EAT) BODY)) 100 (set j{i} (int {c})) (set nx (mod (+ (at c{i} j{i} 0) (normal 0 {sd})) WORLD)) (set ny (mod (+ (at c{i} j{i} 1) (normal 0 {sd})) WORLD)))"],
                what=f"blocks in {c} clumps, sd {sd * 1000:.3g} mm")


def c_onescarce(r, i, G):
    m = int(r.integers(1, 5))
    return dict(lets=[f"(let k{i} (int 2))"], birth=[f"(each b (if (and (= (kind b) k{i}) (>= (mod b BLOCKS) {m})) (hide b)))"], what=f"one colour (by a coin) has only {m} blocks")


def c_dim(r, i, G):
    a = g(r.uniform(0.1, 0.7))
    return dict(lets=[f"(let k{i} (int 2))"], see=[_gate(G, f"(if (= colour k{i}) (set seen (* {a} seen)))")], what=f"one colour {a} as bright")


def c_dimall(r, i, G):
    a = g(r.uniform(0.1, 0.7))
    return dict(see=[_gate(G, f"(set seen (* {a} seen))")], what=f"everything {a} as bright")


def c_cross(r, i, G):
    a = g(r.uniform(0.1, 0.6))
    return dict(see=[_gate(G, f"(set seen (+ seen (* {a} (raw (- 1 colour)))))")], what=f"each eye sees {a} of the other colour")


def c_weak(r, i, G):
    p = g(r.uniform(0.3, 0.9))
    return dict(lets=[f"(let e{i} (int 2))"], pulse=[_gate(G, f"(if (and (= eye e{i}) (chance {p})) (drop))")], what=f"one eye loses {p} of its pulses")


def c_noisy(r, i, G):
    f = g(lu(r, 2.0, 20.0))
    return dict(lets=[f"(let e{i} (int 2))"], tick=[_gate(G, f"(repeat (poisson (* {f} TICK)) (pulse e{i}))")], what=f"one eye fires at random too, {f} a second")


def c_blind(r, i, G):
    d = g(r.uniform(0.02, 0.2))
    return dict(lets=[f"(let f{i} -1)"], fire=[f"(set f{i} t)"], pulse=[_gate(G, f"(if (< (- t f{i}) {d}) (drop))")], what=f"a firing blinds both eyes for {d} s")


def c_mouth(r, i, G):
    f = g(lu(r, 0.5, 2.0))
    if G is None:
        return dict(consts=[f"(const EAT (* {f} EAT))"], what=f"EAT x{f}")
    return dict(lets=[f"(let z{i} EAT)"], tick=[f"(set EAT (if {G} (* {f} z{i}) z{i}))"], what=f"EAT x{f}")


def c_bruise(r, i, G):
    v = g(r.uniform(0.01, 0.05))
    return dict(meal=[_gate(G, f"(if (> speed {v}) (set sign -1))")], what=f"a meal at above {v * 1000:.3g} mm/s is bad")


def c_bounce(r, i, G):
    p = g(r.uniform(0.2, 0.7))
    return dict(meal=[_gate(G, f"(if (chance {p}) (drop))")], what=f"a block bounces off uneaten with chance {p}")


def c_swap(r, i, G):
    T = g(r.uniform(5.0, 60.0))
    return dict(tick=[_gate(G, f"(set poison (mod (+ P (floor (/ t {T}))) 2))")], what=f"the colours swap every {T} s")


def c_alternate(r, i, G):
    return dict(lets=[f"(let l{i} -1)"], tick=[_gate(G, f"(set poison l{i})")], score=[f"(set l{i} colour)"], what="the colour just eaten is poison")


def c_region(r, i, G):
    ax = "x" if r.random() < 0.5 else "y"
    return dict(tick=[_gate(G, f"(set poison (if (< {ax} (/ WORLD 2)) P F))")], what=f"the food colour depends on the half of the world ({ax})")


def c_keylock(r, i, G):
    w = g(r.uniform(2.0, 10.0))
    return dict(lets=[f"(let q{i} -99)"], tick=[_gate(G, f"(if (< (- t q{i}) {w}) (set poison -1))")], score=[f"(if (= colour F) (set q{i} t))"], what=f"food makes poison edible for {w} s")


def c_nth(r, i, G):
    n = int(r.integers(3, 13))
    return dict(lets=[f"(let n{i} 0)"], meal=[_gate(G, f"(if (= (mod n{i} {n}) {n - 1}) (set sign (- sign)))")], score=[f"(set n{i} (+ n{i} 1))"], what=f"every {n}th meal's worth is the opposite")


def c_allfood(r, i, G):
    return dict(tick=[_gate(G, "(set poison -1)")], what="both colours food")


def c_allbad(r, i, G):
    return dict(meal=[_gate(G, "(set sign -1)")], what="both colours bad")


def c_satiety(r, i, G):
    d = g(lu(r, 0.3, 3.0))
    return dict(lets=[f"(let w{i} -1000000000.0)"], meal=[_gate(G, f"(if (< (- t w{i}) {d}) (set sign -1))"), f"(set w{i} t)"], told_wait=d, what=f"a meal within {d} s of the last is bad")


def c_lie(r, i, G):
    e = g(r.uniform(0.05, 0.4))
    return dict(lets=[f"(let u{i} P)"], lie=[f"(set u{i} poison)", _gate(G, f"(if (and (>= poison 0) (chance {e})) (set poison (- 1 poison)))")], told=f"u{i}", what=f"a meal's worth the other colour's with chance {e}")


def c_thrustcost(r, i, G):
    f = g(lu(r, 2.0, 10.0))
    return dict(consts=[f"(const THRUST {f})"], what=f"firings cost x{f}")


def c_cost(r, i, G):
    f = g(lu(r, 0.5, 3.0))
    return dict(consts=[f"(const COST (* {f} COST))"], what=f"poison costs x{f}")


def c_feast(r, i, G):
    p, k = g(r.uniform(0.02, 0.2)), g(lu(r, 2.0, 10.0))
    return dict(score=[_gate(G, f"(if (and (not bad) (chance {p})) (set amount {k}))")], what=f"a food meal worth {k} with chance {p}")


CONSTRUCTS = {
    "L1": [("gain_one", False, c_gain_one), ("gain_both", False, c_gain_both), ("fail", False, c_fail), ("flaky", False, c_flaky),
           ("spurious", False, c_spurious), ("lag", False, c_lag), ("mirror", True, c_mirror)],
    "L2": [("drag", False, _const("DRAG", 0.33, 3.0)), ("push", False, _const("PUSH", 0.33, 3.0)), ("turn", False, _const("TURN", 0.33, 3.0)),
           ("current", False, c_current), ("spinbias", False, c_spinbias)],
    "L3": [("blocks", True, c_blocks), ("moving", False, c_moving), ("clumps", True, c_clumps), ("onescarce", True, c_onescarce)],
    "L4": [("dim", False, c_dim), ("dimall", False, c_dimall), ("cross", False, c_cross), ("reach", True, _const("REACH", 0.33, 3.0))],
    "L5": [("weak", False, c_weak), ("noisy", False, c_noisy), ("blind", False, c_blind), ("sense", True, _const("SENSE", 0.33, 3.0))],
    "L6": [("mouth", False, c_mouth), ("bruise", False, c_bruise), ("bounce", False, c_bounce)],
    "L7": [("swap", False, c_swap), ("alternate", False, c_alternate), ("region", False, c_region), ("keylock", False, c_keylock),
           ("nth", False, c_nth), ("allfood", False, c_allfood), ("allbad", False, c_allbad), ("satiety", False, c_satiety), ("lie", False, c_lie)],
    "L9": [("thrustcost", True, c_thrustcost), ("cost", True, c_cost), ("feast", False, c_feast)],
}
STAGES = ("birth", "tick", "see", "pulse", "fire", "move", "meal", "respawn", "taste", "score")


def held_out(n):
    return hashlib.sha256(f"world:{n}".encode()).digest()[0] % 4 == 0


def development(k):
    out, n = [], 0
    while len(out) < k:
        if not held_out(n):
            out.append(n)
        n += 1
    return out


def pick(r, d):
    keys = list(d)
    return keys[int(r.choice(len(keys), p=np.array([d[k] for k in keys]) / sum(d.values())))]


def draw(n):
    """World number n: (text, list of (link, construct, course, what))."""
    assert not held_out(n), f"world {n} is held out"
    r = np.random.default_rng(int(hashlib.sha256(f"gen2b:{n}".encode()).hexdigest()[:8], 16))
    k = pick(r, NSTAT)
    parts = {s: [] for s in STAGES}
    lets, tables, consts, lie, told, told_wait, desc = [], [], [], [], None, None, []
    for i in range(k):
        link = pick(r, LINKS)
        name, fixed, mk = CONSTRUCTS[link][int(r.integers(len(CONSTRUCTS[link])))]
        course = "fixed" if fixed else pick(r, COURSE)
        G = None
        if course == "from":
            G = f"(>= t {g(r.uniform(20, 80))})"
        elif course == "until":
            G = f"(< t {g(r.uniform(20, 80))})"
        elif course == "cycle":
            P = g(r.uniform(5, 40))
            G = f"(< (mod t {P}) {g(P / 2)})"
        elif course == "bursts":
            lam = g(lu(r, 0.05, 0.5))
            lets.append(f"(let h{i} 0)")
            parts["tick"].append(f"(if (chance (* {lam} TICK)) (set h{i} (- 1 h{i})))")
            G = f"(= h{i} 1)"
        c = mk(r, i, G)
        for s in STAGES:
            parts[s] += c.get(s, [])
        lets += c.get("lets", [])
        tables += c.get("tables", [])
        consts += c.get("consts", [])
        lie += c.get("lie", [])
        if c.get("told") and told is None:
            told = c["told"]
        if c.get("told_wait") is not None:
            told_wait = c["told_wait"] if told_wait is None else min(told_wait, c["told_wait"])
        desc.append((link, name, course if not fixed else "fixed", c["what"] + ("" if G is None else f", gated {G}")))
    parts["tick"] += lie
    text = "(world " + " ".join(consts + lets + tables) + (f" (told {told})" if told else "") + (f" (told-wait {told_wait})" if told_wait else "")
    text += "".join(f" (on {s} " + " ".join(parts[s]) + ")" for s in STAGES if parts[s]) + ")"
    return text, desc


if __name__ == "__main__":
    from stage2_lang import lang
    for n in development(int(sys.argv[1]) if len(sys.argv) > 1 else 10):
        t, d = draw(n)
        print(n, lang.bits(lang.World(t)), d, t)

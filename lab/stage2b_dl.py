"""stage2b_dl.py: stage 2b, part 1 (c). Description length of the normal form (lang.normalise, lang.canonical), against stage 2a's.

  checker    the independent check's cases again (lab/stage2_indep_dl.py, its functions reused): invariance to renaming, comments, meta,
             stream, whitespace, lets reordered; meaning kept with the text changed; meaning changed with the text nearly kept; the ranking
  more       a few more rewrites that keep the meaning, and the pairs with identical lives
  exact      the normal form keeps every life: each hand world's normal form compiled (its stream offset carried over) and lived beside the
             world on seeds 65050-65059 x 2, base and bank, every scored meal, firing and the body's final state compared

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage2b_dl.py > lab/v/stage2b_dl.log"""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from stage2_lang import lang, worlds as WW
import stage2_indep_dl as C

SEEDS = range(65050, 65060)


def W(t, name=None):
    return lang.World(t, name, compile_only=True)      # (compile only: the stage-5 worlds are measured too, never lived)


def b(t):
    return lang.bits(W(t))


def b2a(t):
    """Stage 2a's measure, for comparison: LZMA of _canonical_2a."""
    a, bb = lang._canonical_2a(W(t))
    ra, rb = lang.corpus()
    if not a and not bb:
        return 0
    return (lang._lz(ra + "\n" + a) - lang._lz(ra)) + (lang._lz(rb + "\n" + bb) - lang._lz(rb) if bb else 0)


ALL = {**{n: d["text"] for n, d in WW.W.items()}, **{n: d["text"] for n, d in WW.STAGE5.items()}}


def checker():
    print("== the checker's invariance tests, every world of worlds.py (stage 5's included, compiled only)", flush=True)
    bad = []
    for name, t in ALL.items():
        b0, s0 = b(t), lang.canon_sha(W(t))
        for k in range(3):
            t2, m = C.renamed(t, k)
            if b(t2) != b0 or lang.canon_sha(W(t2)) != s0:
                bad.append((name, "rename", m, b0, b(t2)))
        t3 = "; a comment\n" + C.stripped(t).replace(" ", "  \n ")
        if b(t3) != b0:
            bad.append((name, "comments, meta, stream, whitespace", b0, b(t3)))
        if sum(1 for x in lang.parse(t) if isinstance(x, list) and x[0] == "let") > 1:
            for k in range(3):
                t4 = C.reorder_lets(t, k)
                if b(t4) != b0:
                    bad.append((name, "lets reordered", b0, b(t4)))
                    break
    print(f"  {len(ALL)} worlds, 3 renamings each, comments/meta/stream/whitespace, lets reordered 3 ways: {len(bad)} changes (stage 2a: 4, all lets reordered)", flush=True)
    for x in bad:
        print("   ", x, flush=True)
    print("== meaning kept, text changed / meaning changed, text nearly kept: stage 2a's bits -> the normal form's", flush=True)
    base = "(world (on tick (set poison (mod (+ P (floor (/ t 10))) 2))))"
    cases = [("swap10", base),
             ("swap10, a dead variable", "(world (let junk 3) (on tick (set junk (+ junk 1)) (set poison (mod (+ P (floor (/ t 10))) 2))))"),
             ("swap10, + 0", "(world (on tick (set poison (+ 0 (mod (+ P (floor (/ t 10))) 2)))))"),
             ("swap10, operands commuted", "(world (on tick (set poison (mod (+ (floor (/ t 10)) P) 2))))"),
             ("swap10, via a variable", "(world (let k 0) (on tick (set k (floor (/ t 10))) (set poison (mod (+ P k) 2))))"),
             ("swap every 10.1 s", "(world (on tick (set poison (mod (+ P (floor (/ t 10.1))) 2))))"),
             ("swap every 11 s", "(world (on tick (set poison (mod (+ P (floor (/ t 11))) 2))))"),
             ("swap every 1000 s (never)", "(world (on tick (set poison (mod (+ P (floor (/ t 1000))) 2))))"),
             # more, mine
             ("swap10, period folded from (* 2 5)", "(world (on tick (set poison (mod (+ P (floor (/ t (* 2 5)))) 2))))"),
             ("swap10, * 1 and - 0", "(world (on tick (set poison (- (mod (+ P (* 1 (floor (/ t 10)))) 2) 0))))"),
             ("swap10, a rule that never acts added", "(world (on tick (set poison (mod (+ P (floor (/ t 10))) 2))) (on score (if (> t 5000) (set poison F))))"),
             ("swap10, an (if) whose branches agree", "(world (on tick (set poison (if (> x 0.1) (mod (+ P (floor (/ t 10))) 2) (mod (+ P (floor (/ t 10))) 2)))))"),
             ("plain, (set seen seen)", "(world (on see (set seen seen)))"),
             ("plain, (set poison P)", "(world (on tick (set poison P)))"),
             ("plain, (set gain 1)", "(world (on fire (set gain 1)))"),
             ("plain, (const PUSH PUSH)", "(world (const PUSH PUSH))"),
             ("plain, (after 2000 (pulse 0))", "(world (on tick (after 2000 (pulse 0))))"),
             ("plain, never (worlds.py)", WW.W["never"]["text"]),
             ("halfthrust_const", WW.W["halfthrust_const"]["text"]),
             ("halfthrust_gain (identical lives)", WW.W["halfthrust_gain"]["text"]),
             ("weak", WW.W["weak"]["text"]),
             ("dim25 (equal in distribution)", WW.W["dim25"]["text"]),
             ("parity", WW.W["parity"]["text"]),
             ("parity, lets reordered", C.reorder_lets(WW.W["parity"]["text"], 0))]
    for label, t in cases:
        print(f"  {label:42s} {b2a(t):5d} -> {b(t):5d} bits, canonical {lang.canon_sha(W(t))[:8]}", flush=True)
    print("== ranking, every world of worlds.py: stage 2a's -> the normal form's", flush=True)
    rows = sorted((b(t), b2a(t), n) for n, t in ALL.items())
    for bits, old, n in rows:
        print(f"  {old:5d} -> {bits:5d}  {n}", flush=True)
    print("== the normal form of a few worlds", flush=True)
    for n in ("never", "parity", "digest", "keylock", "cells"):
        print(f"  {n}: {lang.to_text(lang.normalise(W(ALL[n])))}", flush=True)


def pair(job):
    """A world and its normal form, lived on one seed: identical?"""
    from stage2_lang import arms as S
    text, arm, seed, first = job
    w = lang.World(text)
    stream = w.stream if w.stream is not None else 7_000_000 + int(w.canon_stream())
    t2 = lang.to_text(lang.normalise(w), stream=stream)
    out = []
    for t in (text, t2):
        lf = S.make(lang.World(t), arm, seed, first)
        S.live(lf)
        b = lf.body
        out.append((lf.scored, lf.meals, lf.firings, b.pos.tobytes(), b.xy.tobytes(), lf.rng.bit_generator.state["state"]["state"]))
    return out[0] == out[1]


def exact(ex):
    print(f"\n== exact: each hand world against its normal form, compiled and lived, seeds {SEEDS.start}-{SEEDS.stop - 1} x 2, base and bank", flush=True)
    tot = bad = 0
    for n, d in WW.W.items():
        R = list(ex.map(pair, [(d["text"], a, s, c) for a in ("circuit", "bank") for s in SEEDS for c in ("red", "blue")], chunksize=2))
        tot += len(R)
        bad += len(R) - sum(R)
        print(f"  {n:20s} {sum(R)}/{len(R)} lives identical", flush=True)
    print(f"  in all {tot - bad}/{tot} lives identical", flush=True)


if __name__ == "__main__":
    checker()
    with ProcessPoolExecutor(7) as ex:
        exact(ex)

"""stage2c_dl.py: stage 2c, part 3. Description length after the two soundness fixes (no inlining of a body read, no reordering of
operands that draw), with the rule that a normal form is kept only if its lives are identical to the world's on 40 lives (seeds
66670-66689 x 2, base, seconds mode), else the world's own text is measured (lang.bits(w, normal=False)).

  checker    the checker's 20 meaning-preserving rewrites and 10 look-alike pairs (lab/stage2_indep2_dl.py: SAME, DIFFER), translated
             word for word to stage 2c (sign -> worth); the slack left
  hand       every hand world: its normal form verified, the description length kept

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage2c_dl.py > lab/v/stage2c_dl.log"""
import re
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from stage2_lang import lang, worlds as WW
import stage2_indep2_dl as C

SEEDS = range(66670, 66690)
COL = ("red", "blue")


def tr(t):
    return re.sub(r"\bsign\b", "worth", t).replace("(on tick (set poison (if (and (chance 0.5)", "(on tick (set poison (if (and (chance (* 50 TICK))").replace("(< t 50) (chance 0.5))", "(< t 50) (chance (* 50 TICK)))")


def W(t):
    return lang.World(t, compile_only=True)


def nf_text(t):
    w = lang.World(t)
    return lang.to_text(lang.normalise(w), w.stream if w.stream is not None else 7_000_000 + int(w.canon_stream()))


def life_key(job):
    from stage2_lang import arms as S
    text, seed, first = job
    lf = S.make(S.world_of(text), "circuit", seed, first, seconds=True)
    S.live(lf)
    b = lf.body
    return (tuple(lf.scored), tuple(lf.meals), tuple(lf.firings), b.pos.tobytes(), b.xy.tobytes(), lf.rng.bit_generator.state["state"]["state"])


def same_lives(a, c, ex):
    A = list(ex.map(life_key, [(a, s, col) for s in SEEDS for col in COL], chunksize=2))
    B = list(ex.map(life_key, [(c, s, col) for s in SEEDS for col in COL], chunksize=2))
    return sum(x == y for x, y in zip(A, B)), len(A)


def kept(t, ex):
    """(bits kept, normal form verified?, bits normal, bits as written)."""
    w = W(t)
    bn, br = lang.bits(w), lang.bits(w, normal=False)
    k, n = same_lives(t, nf_text(t), ex)
    return (bn if k == n else br), k == n, bn, br, k, n


if __name__ == "__main__":
    with ProcessPoolExecutor(7) as ex:
        print(f"== the checker's meaning-preserving rewrites (translated): bits kept, a -> c; normal form verified on {2 * len(SEEDS)} lives each", flush=True)
        slack = []
        for label, a, c in C.SAME:
            a, c = tr(a), tr(c)
            try:
                ka, va, *_ = kept(a, ex)
                kc, vc, *_ = kept(c, ex)
            except lang.LangError as e:
                print(f"  {label}: not a stage-2c program ({str(e)[:90]})", flush=True)
                continue
            k, n = same_lives(a, c, ex)
            slack.append(kc - ka)
            print(f"  {'MOVES ' if ka != kc else 'same  '} {label}: {ka} -> {kc} (normal form kept: {va}, {vc}); the two texts' lives identical {k}/{n}", flush=True)
        s = np.array(slack)
        print(f"  {np.sum(s != 0)} of {len(s)} move; |change| median {np.median(np.abs(s)):.0f}, max {np.abs(s).max():.0f} bits; range {s.min():+.0f} to {s.max():+.0f}", flush=True)
        print("\n== the checker's look-alike pairs (translated): different lives must not share a canonical form; each normal form verified", flush=True)
        names = list(C.DIFFER)
        for i in range(0, len(names), 2):
            a, c = tr(C.DIFFER[names[i]]), tr(C.DIFFER[names[i + 1]])
            k, n = same_lives(a, c, ex)
            sa, sc = lang.canon_sha(W(a))[:8], lang.canon_sha(W(c))[:8]
            ka, va, bna, bra, kk, nn = kept(a, ex)
            print(f"  '{names[i]}' / '{names[i + 1]}': lives identical {k}/{n}; normal forms {sa} {sc} (shared: {sa == sc}); the first's normal form lives as it {kk}/{nn}", flush=True)
        print("\n== every hand world: normal form verified on 40 lives; bits kept (normal / as written)", flush=True)
        rows = []
        for name, d in WW.W.items():
            kb, v, bn, br, k, n = kept(d["text"], ex)
            rows.append((kb, name))
            print(f"  {name:20s} kept {kb:5d}  (normal {bn}, as written {br}; normal form lives identical {k}/{n})", flush=True)
        print("  ranking: " + ", ".join(f"{n} {b}" for b, n in sorted(rows)), flush=True)

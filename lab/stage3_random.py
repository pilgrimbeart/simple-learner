"""stage3_random.py: stage 3 (PROGRAMME.md), main session, 2026-11-06. The present circuit (the bank, lab/universal_v.py with
lab/v/universal_v7.json), unchanged, on random worlds from the frozen generator lab/stage3_gen.py (SHA in lab/v/stage3_gen.sha256),
development world numbers only (held-out numbers are never drawn), development seeds 80000-89999. In seconds (sim.WLife.seconds).

World sets: `redo`, the first 100 development numbers (stage 2b's, re-run in seconds); `fresh`, the next 200, never run before: stage 3's
coverage is measured on these.

Phases, each saved as it goes in /home/pilgrim/nca-scratch-backup/stage3/ (re-running a phase skips worlds already done):
  label   instruments on, 10 ms: base and bank on seeds 80000-80003 x 2; any stage-5 label (rewiring, a frozen life, a block placed
          under the mouth) in any life keeps the world out of every result (it belongs to stage 5).
  main    1.25 ms (fine enough, D34): base, bank and told (vtold, or vtoldw where the world states a wait), seeds 80100-80159 x 2.
  ref     the frozen reference (lab/v/stage2b_reference.md), 2.5 ms (within about .08 of the finest step, D34), on worlds with a gap
          only (the user's decision, 2026-11-06), the same seeds.
  wires   the first differences on the wires and the rates, against plain, base, bank and unwired, 10 ms, seeds 80200-80219 x 2 (stage
          2a's labels in bits: lab/stage2_label.py).
  analyse per world: base, bank, told, ref; gap = told - max(base, 0) with its 95% interval; nothing to judge if the gap's interval
          reaches 0 or the gap is under .1; x, r; the pass rule x > max(.5 r, .25) (a world with no ref run has r = nan and the floor
          .25); doing no harm where there is nothing to judge; and per set the share with a gap, the bank's pass rate among them
          (coverage, Wilson 95%), and the bits a life (stage 2a's labels).

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage3_random.py label|main|ref|wires|analyse"""
import os
import pickle
import sys
import time
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np

OUT = "/home/pilgrim/nca-scratch-backup/stage3/"
PLAIN = "(world)"
LABEL_SEEDS = range(80000, 80004)
SEEDS = range(80100, 80160)
FD_SEEDS = range(80200, 80220)
COL = ("red", "blue")


def worlds():
    import stage3_gen as G
    nums = G.development(300)
    W = {f"g{n}": G.draw(n) for n in nums}
    return W, [f"g{n}" for n in nums[:100]], [f"g{n}" for n in nums[100:]]


def _init(dt, inst):
    import stage2_checks as C
    from stage2_lang import sim
    if abs(sim.WLife.dt - dt) > 1e-15:
        C.set_tick(dt)
    sim.WLife.seconds = True
    sim.WLife.instruments = inst


def one(job):
    """(text, arm, seed, first) -> (gain, spent, labels or None, cpu), or ("refused", why)."""
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    from stage2_lang.sim import Refused, WLife
    text, arm, seed, first = job
    t0 = time.perf_counter()
    try:
        l = S.live(S.make(S.world_of(text), arm, seed, first))
    except Refused as e:
        return ("refused", str(e)[:200])
    lab = l.labels if WLife.instruments else None
    return (sum(a - COST * b for a, b, _ in l), spent(l), lab, time.perf_counter() - t0)


def wire(job):
    import stage2_label as L
    from stage2_lang.sim import Refused
    try:
        return L.wire(job)
    except Refused:
        return None


def told_arm(text):
    from stage2_lang import arms as S
    return "vtoldw" if "told_wait" in S.world_of(text).fn else "vtold"


def _load(name):
    p = OUT + name + ".pkl"
    return pickle.load(open(p, "rb")) if os.path.exists(p) else {}


def _save(name, d):
    tmp = OUT + name + ".tmp"
    with open(tmp, "wb") as f:
        pickle.dump(d, f)
    os.replace(tmp, OUT + name + ".pkl")


def _texts():
    W, redo, fresh = worlds()
    return [("plain", PLAIN)] + [(n, W[n][0]) for n in redo + fresh]


def phase_label():
    from stage2_lang.instruments import any_label
    done = _load("label")
    t00 = time.time()
    with ProcessPoolExecutor(7, initializer=_init, initargs=(0.01, True)) as ex:
        for n, text in _texts():
            if n in done:
                continue
            R = list(ex.map(one, [(text, a, s, c) for a in ("circuit", "bank") for s in LABEL_SEEDS for c in COL]))
            refused = [r[1] for r in R if r[0] == "refused"]
            labs = [r[2] for r in R if r[0] != "refused"]
            done[n] = dict(refused=refused, labelled=sum(any_label(x) for x in labs), lives=len(labs),
                           kinds={k: sum(bool(x[k]) for x in labs) for k in ("rewired_eye", "rewired_motor", "frozen", "placed")})
            _save("label", done)
            print(f"label {n} {done[n]['labelled']}/{done[n]['lives']} {done[n]['kinds'] if done[n]['labelled'] else ''} "
                  f"{'REFUSED ' + refused[0] if refused else ''} ({time.time() - t00:.0f} s)", flush=True)


def _out_of_results(lab):
    """Out if any life was refused, or at least 3 of the 16 lives carry a stage-5 label: a real rewiring, freeze or placement is
    labelled in nearly every life, a false one in about 1 in 1,000 (D34), so 3 of 16 by chance is about 6e-7 (fixed before any result)."""
    return bool(lab["refused"]) or lab["labelled"] >= 3


def phase_main():
    lab = _load("label")
    done = _load("main")
    t00 = time.time()
    with ProcessPoolExecutor(7, initializer=_init, initargs=(0.00125, False)) as ex:
        for n, text in _texts():
            if n in done or n not in lab or _out_of_results(lab[n]):
                continue
            done[n] = {k: list(ex.map(one, [(text, arm, s, c) for s in SEEDS for c in COL], chunksize=4))
                       for k, arm in (("base", "circuit"), ("bank", "bank"), ("told", told_arm(text)))}
            _save("main", done)
            print(f"main {n} ({time.time() - t00:.0f} s)", flush=True)


def gap_of(R, I=None):
    """(gap, its 95% interval) from main's lives."""
    I = I if I is not None else boot(len(SEEDS))
    b, k, t = (eff(R[a], I) for a in ("base", "bank", "told"))
    fl0, fl = max(b[0], 0.0), np.maximum(b[1], 0.0)
    g0, g = t[0] - fl0, t[1] - fl
    lo, hi = np.percentile(g, [2.5, 97.5])
    return g0, (lo, hi)


def has_gap(R):
    g, (lo, _) = gap_of(R)
    return lo > 0 and g >= 0.1


def phase_ref():
    main = _load("main")
    done = _load("ref")
    t00 = time.time()
    with ProcessPoolExecutor(7, initializer=_init, initargs=(0.0025, False)) as ex:
        for n, text in _texts():
            if n in done or n not in main or (n != "plain" and not has_gap(main[n])):
                continue
            done[n] = list(ex.map(one, [(text, "ref", s, c) for s in SEEDS for c in COL], chunksize=2))
            _save("ref", done)
            print(f"ref {n} ({time.time() - t00:.0f} s)", flush=True)


def phase_wires():
    import stage2_label as L
    lab = _load("label")
    done = _load("wires")
    t00 = time.time()
    with ProcessPoolExecutor(7, initializer=_init, initargs=(0.01, False)) as ex:
        for n, text in _texts():
            if n in done or n not in lab or _out_of_results(lab[n]):
                continue
            done[n] = {arm: list(ex.map(wire, [(text, arm, s, c) for s in FD_SEEDS for c in COL], chunksize=2))
                       for arm in ("circuit", "bank", "unwired")}
            _save("wires", done)
            print(f"wires {n} ({time.time() - t00:.0f} s)", flush=True)


# ---------------------------------------------------------------- analysis
def boot(n, B=2000, seed=0):
    k = np.random.default_rng(seed).integers(0, n, (B, n))
    return np.concatenate((2 * k, 2 * k + 1), axis=1)


def eff(L, I):
    g = np.array([x[0] for x in L], float)
    s = np.array([x[1] for x in L], float)
    return g.sum() / s.sum(), g[I].sum(1) / s[I].sum(1)


def ci(v):
    v = v[np.isfinite(v)]
    return tuple(np.percentile(v, [2.5, 97.5])) if len(v) else (np.nan, np.nan)


def wilson(k, n):
    if n == 0:
        return (np.nan, np.nan)
    p, z = k / n, 1.96
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return c - h, c + h


def analyse():
    W, redo, fresh = worlds()
    lab, main, ref = _load("label"), _load("main"), _load("ref")
    I = boot(len(SEEDS))
    print(f"generator SHA-256 {open('/home/pilgrim/git/simple-learner/lab/v/stage3_gen.sha256').read().split()[0][:16]}; "
          f"seeds {SEEDS.start}-{SEEDS.stop - 1} x 2 at 1.25 ms (ref 2.5 ms); development draws", flush=True)
    rows = {}
    print(f"{'world':6s} {'base':>6s} {'bank':>6s} {'told':>6s} {'ref':>6s} {'gap[95%]':>17s} {'x[95%]':>20s} {'r[95%]':>20s} judge   what", flush=True)
    for n in ["plain"] + redo + fresh:
        if n not in lab:
            continue
        if _out_of_results(lab[n]):
            rows[n] = dict(out=True, why=lab[n]["refused"][:1] or lab[n]["kinds"])
            continue
        if n not in main:
            continue
        R = main[n]
        J = {a: eff(R[a], I) for a in ("base", "bank", "told")}
        fl0, fl = max(J["base"][0], 0.0), np.maximum(J["base"][1], 0.0)
        gap = (J["told"][0] - fl0, J["told"][1] - fl)
        gl, gh = ci(gap[1])
        nothing = not (gl > 0 and gap[0] >= 0.1)
        with np.errstate(divide="ignore", invalid="ignore"):
            x = ((J["bank"][0] - fl0) / gap[0], (J["bank"][1] - fl) / gap[1])
            if n in ref:
                J["ref"] = eff(ref[n], I)
                r = ((J["ref"][0] - fl0) / gap[0], (J["ref"][1] - fl) / gap[1])
            else:
                r = (np.nan, np.full(len(I), np.nan))
        xl, xh = ci(x[1])
        rl, rh = ci(r[1])
        harm = ci(J["bank"][1] - J["base"][1])
        verdict = "-" if nothing else ("pass" if x[0] > max(0.5 * r[0] if np.isfinite(r[0]) else 0.0, 0.25) else "no")
        what = "plain" if n == "plain" else "; ".join(f"{a} {b} {c}" for a, b, c, _ in W[n][1])
        refv = J["ref"][0] if "ref" in J else np.nan
        print(f"{n:6s} {J['base'][0]:+6.2f} {J['bank'][0]:+6.2f} {J['told'][0]:+6.2f} {refv:+6.2f} {gap[0]:+5.2f}[{gl:+5.2f},{gh:+5.2f}] "
              + (f"{x[0]:+6.2f}[{xl:+5.2f},{xh:+5.2f}] {r[0]:+6.2f}[{rl:+5.2f},{rh:+5.2f}]" if not nothing else
                 f"{'harm ' + format(J['bank'][0] - J['base'][0], '+.2f') + ' [' + format(harm[0], '+.2f') + ',' + format(harm[1], '+.2f') + ']':41s}")
              + f" {verdict:5s}   {what}", flush=True)
        rows[n] = dict(out=False, J={k: v[0] for k, v in J.items()}, gap=gap[0], gap_ci=(gl, gh), nothing=nothing, x=x[0], x_ci=(xl, xh),
                       r=r[0], r_ci=(rl, rh), verdict=verdict, harm=(J["bank"][0] - J["base"][0], harm))
    _save("rows", rows)
    for label, names in (("redo (stage 2b's 100, in seconds)", redo), ("fresh (stage 3's coverage set)", fresh)):
        R = {n: rows[n] for n in names if n in rows}
        out = [n for n, v in R.items() if v["out"]]
        live = {n: v for n, v in R.items() if not v["out"]}
        gap = [n for n, v in live.items() if not v["nothing"]]
        passes = [n for n in gap if live[n]["verdict"] == "pass"]
        rclose = [n for n in gap if np.isfinite(live[n]["r_ci"][0]) and live[n]["r_ci"][0] > 0.25]
        harmed = [n for n, v in live.items() if v["nothing"] and v["harm"][1][0] <= -0.1]
        N = len(live)
        print(f"\n== {label}: {len(R)} worlds run; {len(out)} out (stage 5's kinds or refused); {N} judged", flush=True)
        if N:
            print(f"  a gap: {len(gap)}/{N} = {len(gap) / N:.2f} [{wilson(len(gap), N)[0]:.2f},{wilson(len(gap), N)[1]:.2f}]", flush=True)
        if gap:
            print(f"  the bank passes: {len(passes)}/{len(gap)} = {len(passes) / len(gap):.2f} [{wilson(len(passes), len(gap))[0]:.2f},"
                  f"{wilson(len(passes), len(gap))[1]:.2f}]  {passes}", flush=True)
            print(f"  the reference surely closes over .25: {len(rclose)}/{len(gap)}  {rclose}", flush=True)
        print(f"  harm not ruled out (nothing to judge, lower bound of bank - base <= -.1): {len(harmed)}  {harmed}", flush=True)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    {"label": phase_label, "main": phase_main, "ref": phase_ref, "wires": phase_wires, "analyse": analyse}[sys.argv[1]]()

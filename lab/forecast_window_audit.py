"""Job A (PROGRAMME, after D103): forecast comparisons on one footing, from saved accepted-taste rows only.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/forecast_window_audit.py --check
    timeout 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/forecast_window_audit.py --analyse
Conventions: windows are full life and last third (sequence from 200 s of 300, timing from 2000 s of 3000).
Hindsight best single stream: the stream (completed by the default when silent) of least loss, chosen either
over the full life or within the window, ties to the lower index; both use future knowledge and bound nothing.
"""
import hashlib
import json
import math
from pathlib import Path
import pickle
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
import numpy as np

BASE = ROOT / "lab/v/forecast_window_audit"
SETS = {"sequence D93 (seeds 142000-142009)": ("lab/v/room_prediction.pkl", 300., ("high", "low")),
        "sequence D102 (seeds 176000-176009)": ("lab/v/followup_fresh.pkl", 300., ("high", "low")),
        "timing D101 (seeds 142000-142009)": ("lab/v/followup_timing.pkl", 3000., ("design2240", "design560"))}
CLIP = 1e-12


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def loss(p, y):
    return -math.log2(min(1 - CLIP, max(CLIP, p if y else 1 - p)))


def err(p, y):
    return .5 if p == .5 else float((p > .5) != bool(y))


def reconstruct(r):
    awake = np.isfinite(r["q"])
    return (r["wd"] * r["pd"] + np.dot(r["w"][awake], r["q"][awake])) / (r["wd"] + r["w"][awake].sum())


def stream_probs(rows, j):
    return [r["q"][j] if np.isfinite(r["q"][j]) else r["pd"] for r in rows]


def best_single(rows, mask):
    """Index of least total loss over rows where mask is True; strict < keeps the lower index on ties."""
    best, bj = None, None
    for j in range(len(rows[0]["q"])):
        L = sum(loss(p, r["letter"]) for p, r, m in zip(stream_probs(rows, j), rows, mask) if m)
        if best is None or L < best - 1e-12:
            best, bj = L, j
    return bj


def life_measures(life, secs):
    rows = life["rows"]
    fam = np.array(life["fam"])
    errs = []
    for r in rows:
        assert r["t"] <= r["taste_t"] + 1e-12, "forecast after taste"
        e = abs(reconstruct(r) - r["p1"])
        assert e <= 1e-12, ("native reconstruction", e)
        errs.append(e)
    out = {}
    full = [True] * len(rows)
    jf = best_single(rows, full)
    for w, start in (("full", 0.), ("last_third", 2 * secs / 3)):
        m = [r["taste_t"] >= start for r in rows]
        jw = best_single(rows, m)
        sel = [(r, i) for i, (r, k) in enumerate(zip(rows, m)) if k]
        n = len(sel)
        ys = [r["letter"] for r, _ in sel]
        d = dict(n=n, rate_per_s=n / (secs - start))
        for name, ps in (("native", [r["p1"] for r, _ in sel]), ("default", [r["pd"] for r, _ in sel]), ("uniform", [.5] * n),
                         ("best single chosen over full life", [stream_probs(rows, jf)[i] for _, i in sel]),
                         ("best single chosen within window", [stream_probs(rows, jw)[i] for _, i in sel])):
            d[name] = dict(bits=sum(loss(p, y) for p, y in zip(ps, ys)), errors=sum(err(p, y) for p, y in zip(ps, ys)))
        spans = [s for r, _ in sel for s in r["span"][(fam == "event") & np.isfinite(r["q"])]]
        d["event_span_mean"] = float(np.mean(spans)) if spans else None
        d["best_full_family"], d["best_window_family"] = life["fam"][jf], life["fam"][jw]
        d["best_differs"] = jf != jw
        out[w] = d
    return out, max(errs)


def per_life(v, w, key, stat):
    d = v[w]
    return d[key][stat] / d["n"] if d["n"] else float("nan")


def boot(diffs, k):
    return [float(x) for x in np.quantile(np.nanmean(diffs[k], 1), [.025, .975])]


def compare(M, a, b, seeds):
    order = [(s, c) for s in seeds for c in ("red", "blue")]
    k = np.random.default_rng(0).integers(0, len(seeds), (2000, len(seeds)))
    idx = np.concatenate((2 * k, 2 * k + 1), axis=1)
    out = {}
    for w in ("full", "last_third"):
        for key in ("native", "default", "best single chosen over full life", "best single chosen within window"):
            for stat in ("bits", "errors"):
                d = np.array([per_life(M[a, s, c], w, key, stat) - per_life(M[b, s, c], w, key, stat) for s, c in order])
                out[f"{w} | {key} | {stat} per taste"] = dict(per_life_mean=float(np.nanmean(d)), ci95=boot(d, idx))
        d = np.array([M[a, s, c][w]["event_span_mean"] - M[b, s, c][w]["event_span_mean"] for s, c in order])
        out[f"{w} | event speaker span"] = dict(per_life_mean=float(np.nanmean(d)), ci95=boot(d, idx))
        d = np.array([M[a, s, c][w]["n"] - M[b, s, c][w]["n"] for s, c in order], dtype=float)
        out[f"{w} | accepted tastes"] = dict(per_life_mean=float(d.mean()), ci95=boot(d, idx))
    return out


def levels(M, arm, seeds):
    order = [(s, c) for s in seeds for c in ("red", "blue")]
    out = {}
    for w in ("full", "last_third"):
        n = sum(M[arm, s, c][w]["n"] for s, c in order)
        o = dict(tastes=n, per_life_tastes=[M[arm, s, c][w]["n"] for s, c in order],
                 rate_per_s=float(np.mean([M[arm, s, c][w]["rate_per_s"] for s, c in order])),
                 event_span_per_life_mean=float(np.mean([M[arm, s, c][w]["event_span_mean"] for s, c in order])),
                 best_differs_lives=sum(M[arm, s, c][w]["best_differs"] for s, c in order))
        for key in ("native", "default", "uniform", "best single chosen over full life", "best single chosen within window"):
            o[key] = dict(pooled_bits_per_taste=sum(M[arm, s, c][w][key]["bits"] for s, c in order) / n,
                          pooled_errors_per_taste=sum(M[arm, s, c][w][key]["errors"] for s, c in order) / n,
                          per_life_mean_bits=float(np.mean([per_life(M[arm, s, c], w, key, "bits") for s, c in order])))
        out[w] = o
    return out


def fixture_life(rows_spec):
    rows = []
    for t, q0, q1, y in rows_spec:
        q = np.array([q0, q1])
        w = np.array([1., 1.])
        r = dict(t=t, taste_t=t + .1, wd=1., pd=.5, w=w, q=q, letter=y, span=np.array([1, 3], np.int16), grown=np.array([False, True]))
        r["p1"] = float(reconstruct(r))
        rows.append(r)
    return dict(rows=rows, fam=["event", "event"])


def check():
    checks = []
    # stream 0 right early, wrong late; stream 1 the reverse: full-life choice differs from last-third choice
    spec = [(t, .9, .1, 1) for t in range(0, 150, 10)] + [(t, .9, .1, 0) for t in range(200, 300, 25)] + [(t, .9, .1, 1) for t in range(150, 200, 25)]
    life = fixture_life(sorted(spec))
    m, e = life_measures(life, 300.)
    assert e <= 1e-15
    assert m["full"]["best_differs"] is False and m["last_third"]["best_differs"] is True
    assert m["last_third"]["best single chosen within window"]["bits"] < m["last_third"]["best single chosen over full life"]["bits"]
    checks.append("best single over the full life differs from best within the last third; both reported")
    a = fixture_life([(t, .9, .5, 1) for t in range(0, 300, 10)])            # 30 tastes, all right at .9
    b = fixture_life([(t, .5, .5, 1) for t in range(250, 300, 10)])          # 5 tastes, all uniform
    ma, _ = life_measures(a, 300.)
    mb, _ = life_measures(b, 300.)
    M = {("x", 0, "red"): ma, ("x", 0, "blue"): mb}
    lv = levels(M, "x", [0])
    pl = lv["full"]["native"]["per_life_mean_bits"]
    po = lv["full"]["native"]["pooled_bits_per_taste"]
    q = (.5 + .9 + .5) / 3                                                 # default, stream 0, stream 1, equal weights
    assert abs(pl - (loss(q, 1) + 1.) / 2) < 1e-12 and abs(po - (30 * loss(q, 1) + 5) / 35) < 1e-12 and abs(pl - po) > .05
    checks.append("unequal tastes per life: per-life mean and pooled per-taste mean differ and are kept apart")
    bad = fixture_life([(0., .9, .1, 1)])
    bad["rows"][0]["p1"] += 1e-9
    try:
        life_measures(bad, 300.)
    except AssertionError:
        checks.append("a reconstruction error above 1e-12 is refused")
    else:
        raise AssertionError("bad reconstruction accepted")
    late = fixture_life([(0., .9, .1, 1)])
    late["rows"][0]["taste_t"] = -1.
    try:
        life_measures(late, 300.)
    except AssertionError:
        checks.append("a forecast after its taste is refused")
    else:
        raise AssertionError("late forecast accepted")
    out = dict(success=True, checks=checks)
    BASE.with_name(BASE.name + "_checks").with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


def analyse():
    out = dict(success=False, conventions=dict(
        windows="full life; last third from 200 s (sequence, 300 s lives) or 2000 s (timing, 3000 s lives), by taste time",
        hindsight="best single stream chosen over the full life, and chosen within the window; ties to lower index; default completes silence",
        pairing="per-life differences on the same seed and colour order; 2000 seed-pair bootstraps, both colours together",
        pooled="pooled per-taste levels are reported separately and never paired across lives",
        old="D93 chose over the full life and scored the last third; D101/D102 chose within the window; D93 spans were full-life",
        credit="historical pre-D82 credit in all three sets"), provenance=dict(
        revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        dirty=subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
        script_sha256=digest(__file__), inputs={p: digest(ROOT / p) for p, _, _ in SETS.values()},
        command="timeout 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/forecast_window_audit.py --analyse"))
    t0 = time.monotonic()
    try:
        res = {}
        for name, (path, secs, (a, b)) in SETS.items():
            data = pickle.loads((ROOT / path).read_bytes())
            lives = data["lives"] if isinstance(data, dict) else data
            M, maxerr = {}, 0.
            for l in lives:
                if "rows" not in l:
                    continue
                M[l["name"], l["seed"], l["first"]], e = life_measures(l, secs)
                maxerr = max(maxerr, e)
            seeds = sorted({s for _, s, _ in M})
            arms = sorted({n for n, _, _ in M})
            res[name] = dict(lives=len(M), arms=arms, seeds=[seeds[0], seeds[-1]], life_s=secs, max_reconstruction_error=maxerr,
                             levels={x: levels(M, x, seeds) for x in arms}, paired=compare(M, a, b, seeds), pair=f"{a} - {b}")
            print(name, "lives", len(M), "max reconstruction error", maxerr, flush=True)
        out["results"] = res
        out["success"] = True
    except Exception as e:
        out["error"] = repr(e)
        raise
    finally:
        out["wall_s"] = time.monotonic() - t0
        BASE.with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    print("wall_s", out["wall_s"])
    for name, r in out["results"].items():
        print("\n==", name, r["pair"])
        for x, lv in r["levels"].items():
            for w in ("full", "last_third"):
                o = lv[w]
                print(f"  {x:18s} {w:10s} tastes {o['tastes']:5d} rate {o['rate_per_s']:.3f}/s span {o['event_span_per_life_mean']:.2f} "
                      f"native {o['native']['pooled_bits_per_taste']:.3f}/{o['native']['pooled_errors_per_taste']:.3f} "
                      f"default {o['default']['pooled_bits_per_taste']:.3f} "
                      f"best(full) {o['best single chosen over full life']['pooled_bits_per_taste']:.3f} "
                      f"best(window) {o['best single chosen within window']['pooled_bits_per_taste']:.3f} differs {o['best_differs_lives']}")
        for k, v in r["paired"].items():
            print(f"  {k:70s} {v['per_life_mean']:+.3f} [{v['ci95'][0]:+.3f},{v['ci95'][1]:+.3f}]")


if __name__ == "__main__":
    {"--check": check, "--analyse": analyse}[sys.argv[1]]()

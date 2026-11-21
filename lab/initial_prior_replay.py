"""Job E (PROGRAMME after D108): two initial selector priors replayed on saved histories, fixed share .01.
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/initial_prior_replay.py --check
    timeout 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/initial_prior_replay.py --analyse
Read-only helpers: selection_share_audit.update/replay_check, selection_share_extension.update_share,
scoring_order_replay.chronology/probability. Their main functions are never called.
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
sys.path[:0] = [str(ROOT / "lab"), str(ROOT)]
import numpy as np
import selection_share_audit as SA
import selection_share_extension as SE
import scoring_order_replay as SR

BASE = ROOT / "lab/v/initial_prior_replay"
SHARE = .01
N_STREAMS = 168
PRIORS = {"baseline": (1., 1.), "alternative": (84.5, 169 / 336)}
INPUTS = ("lab/v/contest_prediction.pkl", "lab/v/ruler_ingredients.pkl", "lab/v/followup_timing.pkl", "lab/v/active_mixture_audit.pkl")


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def loss(p, y):
    return -math.log2(min(1 - 1e-12, max(1e-12, p if y else 1 - p)))


def err(p, y):
    return .5 if p == .5 else float((p > .5) != bool(y))


def prior(name, n=N_STREAMS):
    wd, ws = PRIORS[name]
    return wd, np.full(n, ws)


def issued_replay(rows, name):
    """Causal: probability from current weights, then update with that row's label. Weights persist."""
    wd, w = prior(name, len(rows[0]["w"]))
    ps = []
    for r in rows:
        aw = np.isfinite(r["q"])
        ps.append(float((wd * r["pd"] + np.dot(w[aw], r["q"][aw])) / (wd + w[aw].sum())))
        wd, w = SA.update(wd, w, r["q"], r["pd"], r["letter"], SHARE)
    return ps


def scored_replay(life, name):
    """D79: update from scored forecasts at accepted tastes; evaluate the issued prediction before each accepted taste."""
    wd, ws = PRIORS[name]
    w = np.full(len(life["names"]), ws)
    w[0] = wd
    probs, maxerr = {}, 0.
    for kind, row in SR.chronology(life):
        if kind == "prediction":
            p = SR.probability(w, row["q"])
            probs[id(row)] = p
            if name == "baseline":
                maxerr = max(maxerr, abs(p - row["p1"]), float(np.max(np.abs(w - row["w"]))))
        elif row["accepted"]:
            SE.update_share(w, row["scored_q"], row["letter"], SHARE)
    preds = life["predictions"]
    rows = [(t["t"], probs[id(preds[t["issued"]])], t["letter"]) for t in life["tastes"] if t["accepted"] and t["issued"] is not None]
    return rows, maxerr


def windows(T):
    return (("first_third", 0., T / 3), ("last_third", 2 * T / 3, T + 1), ("full", 0., T + 1))


def measures(ts, pb, pa, ys, T):
    out = {}
    for w, lo, hi in windows(T):
        idx = [i for i, t in enumerate(ts) if lo <= t < hi]
        n = len(idx)
        out[w] = dict(n=n, base_bits=sum(loss(pb[i], ys[i]) for i in idx) / n, alt_bits=sum(loss(pa[i], ys[i]) for i in idx) / n,
                      base_errors=sum(err(pb[i], ys[i]) for i in idx) / n, alt_errors=sum(err(pa[i], ys[i]) for i in idx) / n,
                      changed_choices=int(sum((pb[i] > .5) != (pa[i] > .5) for i in idx)))
        out[w]["delta_bits"] = out[w]["alt_bits"] - out[w]["base_bits"]
        out[w]["delta_errors"] = out[w]["alt_errors"] - out[w]["base_errors"]
    return out


def keyed(lives, arm):
    out = {}
    for l in lives:
        if l.get("name") != arm:
            continue
        k = (arm, l["seed"], l["first"])
        assert k not in out, ("duplicate life key", k)
        out[k] = l
    return out


def complete_pairs(d, arm, n_seeds):
    seeds = sorted({s for _, s, _ in d})
    assert len(seeds) == n_seeds, (arm, len(seeds))
    for s in seeds:
        assert (arm, s, "red") in d and (arm, s, "blue") in d, ("incomplete pair", arm, s)
    return seeds


def boot(vals_by_seed_colour, seeds):
    order = [(s, c) for s in seeds for c in ("red", "blue")]
    x = np.array([vals_by_seed_colour[o] for o in order])
    k = np.random.default_rng(0).integers(0, len(seeds), (2000, len(seeds)))
    idx = np.concatenate((2 * k, 2 * k + 1), axis=1)
    return dict(per_life_mean=float(x.mean()), ci95=[float(v) for v in np.quantile(x[idx].mean(1), [.025, .975])])


def check():
    checks = []
    for n in PRIORS:
        wd, w = prior(n)
        assert abs(wd + w.sum() - 169.) < 1e-12
    assert abs(prior("alternative")[0] / 169 - .5) < 1e-15
    checks.append("both priors total 169; the alternative puts exactly half on the default, streams equal")
    rows = [dict(q=np.array([.9, np.nan]), pd=.5, letter=1, w=np.ones(2), wd=1.), dict(q=np.array([.2, .7]), pd=.5, letter=0, w=np.ones(2), wd=1.)]
    a = issued_replay(rows, "alternative")
    rows2 = [rows[0], dict(rows[1], letter=1)]
    b = issued_replay(rows2, "alternative")
    assert a == b
    checks.append("no label is used before its prediction: changing the second label leaves both probabilities unchanged")
    wd, w = prior("alternative", 2)
    wd2, w2 = SA.update(wd, w, np.array([.9, np.nan]), .5, 1, SHARE)
    assert w2[1] == w[1]
    checks.append("a sleeping stream's weight is preserved by the update")
    try:
        keyed([dict(name="R", seed=1, first="red"), dict(name="R", seed=1, first="red")], "R")
    except AssertionError:
        checks.append("duplicate life keys are rejected")
    else:
        raise AssertionError("duplicate accepted")
    try:
        complete_pairs({("R", 1, "red"): 0}, "R", 1)
    except AssertionError:
        checks.append("an incomplete red/blue pair is rejected")
    else:
        raise AssertionError("incomplete pair accepted")
    out = dict(success=True, checks=checks)
    BASE.with_name(BASE.name + "_checks").with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


def analyse():
    t0 = time.monotonic()
    out = dict(success=False, priors=dict(baseline="default 1, each stream 1 (total 169; default share 1/169)",
                                          alternative="default 84.5, each stream 169/336 (total 169; default share 1/2)"),
               share=SHARE, credit="historical (pre-D82)", provenance=dict(
                   revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                   dirty=subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
                   sha256={p: digest(ROOT / p) for p in ("lab/initial_prior_replay.py", "lab/selection_share_audit.py",
                                                          "lab/selection_share_extension.py", "lab/scoring_order_replay.py", *INPUTS)},
                   command="timeout 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/initial_prior_replay.py --analyse"))
    try:
        sets = {}
        cp = pickle.loads((ROOT / INPUTS[0]).read_bytes())["lives"]
        ri = pickle.loads((ROOT / INPUTS[1]).read_bytes())["lives"]
        ft = pickle.loads((ROOT / INPUTS[2]).read_bytes())
        sets["R"] = (keyed(cp, "R"), 300.)
        sets["R+1"] = (keyed(ri, "R+1"), 300.)
        sets["design560 timing"] = ({("design560 timing", s, c): l for (_, s, c), l in keyed(ft, "design560").items()}, 3000.)
        counts = {k: len(v[0]) for k, v in sets.items()}
        assert counts == {"R": 20, "R+1": 20, "design560 timing": 20}, counts
        per, base_err = {}, {}
        for arm, (lives, T) in sets.items():
            complete_pairs(lives, arm, 10)
            for key, l in lives.items():
                rows = l["rows"]
                tr = SA.replay_check(rows)
                assert all(t["exact"] for t in tr), ("baseline transition not exact", key)
                assert all(abs(x - 1.) == 0 for x in rows[0]["w"]) and rows[0]["wd"] == 1., ("first row not the baseline prior", key)
                pb, pa = issued_replay(rows, "baseline"), issued_replay(rows, "alternative")
                e = max(abs(p - r["p1"]) for p, r in zip(pb, rows))
                assert e <= 1e-9, ("baseline probability", key, e)
                base_err[str(key)] = e
                per[key] = measures([r["taste_t"] for r in rows], pb, pa, [r["letter"] for r in rows], T)
        raw = pickle.loads((ROOT / INPUTS[3]).read_bytes())
        d79 = {}
        for life in [l for l in raw["lives"] if l["observe"]]:
            key = ("D79 " + life["rule"], life["seed"], life["first"])
            assert key not in d79
            rb, eb = scored_replay(life, "baseline")
            ra, _ = scored_replay(life, "alternative")
            assert eb <= 1e-9, ("D79 baseline", key, eb)
            base_err[str(key)] = eb
            assert [t for t, _, _ in rb] == [t for t, _, _ in ra]
            d79[key] = measures([t for t, _, _ in rb], [p for _, p, _ in rb], [p for _, p, _ in ra], [y for _, _, y in rb], 300.)
        assert len(d79) == 4, len(d79)
        out["counts"] = dict(counts, D79=len(d79))
        out["max_baseline_error"] = max(base_err.values())
        out["baseline_errors_per_life"] = base_err
        famcount = {"default": 0}
        for f in sets["R"][0][next(iter(sets["R"][0]))]["fam"]:
            famcount[f] = famcount.get(f, 0) + 1
        out["prior_mass"] = {name: dict(default=PRIORS[name][0] / 169., **{f"{f} ({c} streams)": c * PRIORS[name][1] / 169.
                                                                          for f, c in famcount.items() if f != "default"})
                             for name in PRIORS}
        summary = {}
        for arm, (lives, T) in sets.items():
            seeds = sorted({s for _, s, _ in lives})
            for w, _, _ in windows(T):
                for m in ("delta_bits", "delta_errors"):
                    summary[f"{arm} | {w} | alternative - baseline {m}"] = boot({(s, c): per[arm, s, c][w][m] for s, c in [(s, c) for s in seeds for c in ("red", "blue")]}, seeds)
                summary[f"{arm} | {w} | baseline bits level"] = float(np.mean([per[arm, s, c][w]["base_bits"] for s in seeds for c in ("red", "blue")]))
                summary[f"{arm} | {w} | changed choices / tastes"] = f"{sum(per[arm, s, c][w]['changed_choices'] for s in seeds for c in ('red', 'blue'))} / {sum(per[arm, s, c][w]['n'] for s in seeds for c in ('red', 'blue'))}"
        seeds = sorted({s for _, s, _ in sets["R"][0]})
        for w, _, _ in windows(300.):
            summary[f"R minus R+1 effect | {w} | bits"] = boot({(s, c): per["R", s, c][w]["delta_bits"] - per["R+1", s, c][w]["delta_bits"] for s in seeds for c in ("red", "blue")}, seeds)
        out["summary"] = summary
        out["per_life"] = {str(k): v for k, v in per.items()}
        out["D79_per_life"] = {str(k): v for k, v in d79.items()}
        out["success"] = True
    except Exception as e:
        out["error"] = repr(e)
        raise
    finally:
        out["wall_s"] = time.monotonic() - t0
        BASE.with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    for k, v in out["summary"].items():
        print(k, json.dumps(v))
    for k, v in out["D79_per_life"].items():
        print(k, {w: (round(x["delta_bits"], 4), round(x["delta_errors"], 4), x["changed_choices"], x["n"]) for w, x in v.items()})
    print("max baseline error", out["max_baseline_error"], "wall", out["wall_s"])


if __name__ == "__main__":
    {"--check": check, "--analyse": analyse}[sys.argv[1]]()

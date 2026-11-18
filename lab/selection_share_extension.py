"""D107: prior mass for Job C's lives; share .01 vs 0 on D79's exactly replayable recording (large brain and contest);
replayability and share comparison on D100's lives. Offline only.
    timeout 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/selection_share_extension.py
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
import scoring_order_replay as SR

OUT = ROOT / "lab/v/selection_share_extension.json"
FAMS = ("event", "clock", "integrator", "rhythm")
loss = lambda p, y: -math.log2(min(1 - 1e-12, max(1e-12, p if y else 1 - p)))
err = lambda p, y: .5 if p == .5 else float((p > .5) != bool(y))


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def mass(row, fam):
    tot = row["wd"] + row["w"].sum()
    aw = np.isfinite(row["q"])
    atot = row["wd"] + row["w"][aw].sum()
    return dict(stored=dict(default=row["wd"] / tot, **{f: float(row["w"][fam == f].sum() / tot) for f in FAMS}),
                awake=dict(default=row["wd"] / atot, **{f: float(row["w"][aw & (fam == f)].sum() / atot) for f in FAMS}))


def prior_mass():
    out = {}
    for name, path in SA.SETS.items():
        d = pickle.loads((ROOT / path).read_bytes())
        lives = [l for l in (d["lives"] if isinstance(d, dict) else d) if "rows" in l]
        T = 3000. if "timing" in name else 300.
        per = {}
        for l in lives:
            fam = np.array(l["fam"])
            first = l["rows"][0]
            late = next(r for r in l["rows"] if r["taste_t"] >= 2 * T / 3)
            per.setdefault(l["name"], []).append((mass(first, fam), mass(late, fam)))
        out[name] = {a: dict(first_accepted_taste={k: {f: float(np.mean([m[0][k][f] for m in v])) for f in ("default",) + FAMS} for k in ("stored", "awake")},
                             start_of_last_third={k: {f: float(np.mean([m[1][k][f] for m in v])) for f in ("default",) + FAMS} for k in ("stored", "awake")},
                             first_row_weights_all_one=bool(all(True for _ in v)))
                     for a, v in per.items()}
        # initial weights: all streams and the default start at 1 (grownet getattr defaults)
        out[name]["_initial"] = {"default": 1 / 169, "per stream": 1 / 169, "event (10 streams)": 10 / 169, "other (158 streams)": 158 / 169}
    return out


def update_share(w, q, letter, share):
    active = np.flatnonzero(np.isfinite(q[1:])) + 1
    lik = q if letter else 1 - q
    pd = float(lik[0])
    total = float(w[0]) + sum(float(w[j]) for j in active)
    pm = (float(w[0]) * pd + sum(float(w[j]) * float(lik[j]) for j in active)) / total
    w[0] *= pd / pm
    for j in active:
        w[j] *= float(lik[j]) / pm
    if share and len(active):
        even = share * total / (len(active) + 1)
        w[0] = (1 - share) * w[0] + even
        for j in active:
            w[j] = (1 - share) * w[j] + even
    top = float(max(w))
    if top < 1e-6:
        w /= top


def d79_replay():
    raw = pickle.loads(SR.RAW.read_bytes())
    lives = [l for l in raw["lives"] if l["observe"]]
    res = []
    for life in lives:
        out = {}
        scored = {}
        for share in (.01, 0.):
            w = np.ones(len(life["names"]))
            probs, maxerr = {}, 0.
            for i, (kind, row) in enumerate(SR.chronology(life)):
                if kind == "prediction":
                    p = SR.probability(w, row["q"])
                    probs[id(row)] = p
                    if share == .01:
                        maxerr = max(maxerr, abs(p - row["p1"]), float(np.max(abs(w - row["w"]))))
                elif row["accepted"]:
                    update_share(w, row["scored_q"], row["letter"], share)
            if share == .01:
                assert maxerr <= 1e-10, ("D79 share .01 replay mismatch", maxerr)
                out["max_reproduction_error"] = maxerr
            preds = life["predictions"]
            rows = [(t["t"], probs[id(preds[t["issued"]])], t["letter"]) for t in life["tastes"] if t["accepted"] and t["issued"] is not None]
            scored[share] = rows
        for w_, lo, hi in (("first_third", 0, 100), ("last_third", 200, 301), ("full", 0, 301)):
            a = [(p, y) for t, p, y in scored[.01] if lo <= t < hi]
            b = [(p, y) for t, p, y in scored[0.] if lo <= t < hi]
            n = len(a)
            out[w_] = dict(n=n, share_bits=sum(loss(p, y) for p, y in a) / n, zero_bits=sum(loss(p, y) for p, y in b) / n,
                           delta_bits=(sum(loss(p, y) for p, y in b) - sum(loss(p, y) for p, y in a)) / n,
                           delta_errors=(sum(err(p, y) for p, y in b) - sum(err(p, y) for p, y in a)) / n,
                           choice_changes=sum((p > .5) != (q > .5) for (p, _), (q, _) in zip(a, b)))
        res.append(dict(rule=life["rule"], first=life["first"], seed=life.get("seed"), **out))
    return res


def d100_lives():
    pools = {"contest_prediction.pkl": ("R",), "ruler_ingredients.pkl": ("R+1",), "followup_silent.pkl": ("R silent", "R+1 silent")}
    lives = []
    for f, names in pools.items():
        d = pickle.loads((ROOT / "lab/v" / f).read_bytes())
        lives += [l for l in (d["lives"] if isinstance(d, dict) else d) if l.get("name") in names and "rows" in l]
    exact = {}
    for l in lives:
        exact.setdefault(l["name"], []).append(all(t["exact"] for t in SA.replay_check(l["rows"])))
    out = dict(replay_fully_exact={k: f"{sum(v)}/{len(v)}" for k, v in exact.items()})
    if all(all(exact.get(k, [False])) for k in ("R", "R+1")):
        per = {}
        for l in lives:
            if l["name"] not in ("R", "R+1"):
                continue
            rows = l["rows"]
            p1, p0 = SA.replay_probs(rows, SA.SHARE), SA.replay_probs(rows, 0.)
            assert max(abs(a - r["p1"]) for a, r in zip(p1, rows)) <= 1e-9
            v = {}
            for w_, lo, hi in (("first_third", 0, 100), ("last_third", 200, 301), ("full", 0, 301)):
                idx = [i for i, r in enumerate(rows) if lo <= r["taste_t"] < hi]
                v[w_] = (sum(loss(p0[i], rows[i]["letter"]) - loss(p1[i], rows[i]["letter"]) for i in idx) / len(idx))
            per[l["name"], l["seed"], l["first"]] = v
        seeds = sorted({s for _, s, _ in per})
        order = [(s, c) for s in seeds for c in ("red", "blue")]
        k = np.random.default_rng(0).integers(0, len(seeds), (2000, len(seeds)))
        idx = np.concatenate((2 * k, 2 * k + 1), axis=1)
        for w_ in ("first_third", "last_third", "full"):
            for name in ("R", "R+1"):
                dd = np.array([per[name, s, c][w_] for s, c in order])
                out[f"{name} | {w_} | share 0 - share .01, bits per taste"] = dict(mean=float(dd.mean()), ci95=[float(x) for x in np.quantile(dd[idx].mean(1), [.025, .975])])
            dd = np.array([per["R", s, c][w_] - per["R+1", s, c][w_] for s, c in order])
            out[f"(R) - (R+1) effect | {w_}"] = dict(mean=float(dd.mean()), ci95=[float(x) for x in np.quantile(dd[idx].mean(1), [.025, .975])])
    return out


def main():
    t0 = time.monotonic()
    out = dict(provenance=dict(revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                               dirty=subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
                               sha256={p: digest(ROOT / p) for p in ("lab/selection_share_extension.py", "lab/selection_share_audit.py",
                                                                      "lab/scoring_order_replay.py", "lab/v/active_mixture_audit.pkl",
                                                                      "lab/v/contest_prediction.pkl", "lab/v/ruler_ingredients.pkl",
                                                                      "lab/v/followup_silent.pkl", *SA.SETS.values())},
                               command="timeout 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/selection_share_extension.py"))
    out["prior_mass"] = prior_mass()
    print("prior mass done", flush=True)
    out["d79_large_brain"] = d79_replay()
    print(json.dumps(out["d79_large_brain"], indent=1), flush=True)
    out["d100"] = d100_lives()
    print(json.dumps(out["d100"], indent=1), flush=True)
    out["wall_s"] = time.monotonic() - t0
    OUT.write_text(json.dumps(out, indent=1, default=float) + "\n")
    print("wall_s", out["wall_s"])


if __name__ == "__main__":
    main()

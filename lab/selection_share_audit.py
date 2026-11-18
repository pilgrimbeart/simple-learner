"""Job C (PROGRAMME, after D103): replay the historical Bayes selector with fixed share on saved accepted-taste rows;
compare share .01 with 0 only if the replay reproduces the native weights exactly.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/selection_share_audit.py --check
    timeout 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/selection_share_audit.py --analyse
"""
import hashlib
import json
from pathlib import Path
import pickle
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
import numpy as np

BASE = ROOT / "lab/v/selection_share_audit"
SETS = {"sequence D93": "lab/v/room_prediction.pkl", "sequence D102": "lab/v/followup_fresh.pkl", "timing D101": "lab/v/followup_timing.pkl"}
SHARE = 0.01
TOL = 1e-9


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def update(wd, w, q, pd1, y, share):
    """grownet.py:782-815 with BT=1: Bayes over the default and the awake speakers, then fixed share among them,
    then the common rescale when the largest weight falls below 1e-6. q: probability of letter 1, NaN when asleep."""
    w = w.copy()
    awake = np.isfinite(q)
    lik = lambda p: p if y else 1. - p
    pd = lik(pd1)
    qa = lik(q[awake])
    W0 = wd + w[awake].sum()
    pm = (wd * pd + np.dot(w[awake], qa)) / W0
    wd = wd * pd / pm
    w[awake] = w[awake] * qa / pm
    if share and awake.any():
        even = share * W0 / (awake.sum() + 1)
        wd = (1 - share) * wd + even
        w[awake] = (1 - share) * w[awake] + even
    top = max(w.max(), wd)
    if top < 1e-6:
        w, wd = w / top, wd / top
    return wd, w


def normalise(wd, w):
    t = wd + w.sum()
    return wd / t, w / t


def replay_check(rows):
    """Per transition: does the update from row k reproduce row k+1's issued weights (normalised)?"""
    out = []
    for a, b in zip(rows, rows[1:]):
        wd, w = update(a["wd"], a["w"], a["q"], a["pd"], a["letter"], SHARE)
        x, y = normalise(wd, w), normalise(b["wd"], b["w"])
        dev = max(abs(x[0] - y[0]), float(np.max(np.abs(x[1] - y[1]))))
        changed = np.where(np.abs(x[1] - y[1]) > TOL)[0]
        out.append(dict(dev=dev, exact=dev <= TOL, n_changed=len(changed),
                        changed_awake_at_issue=int(np.isfinite(a["q"][changed]).sum()) if len(changed) else 0))
    return out


def check():
    checks = []
    q = np.array([.9, np.nan, .2])
    w = np.array([1., 1., 1.])
    wd1, w1 = update(1., w, q, .5, 1, 0.)
    pm = (.5 + .9 + .2) / 3
    assert abs(wd1 - .5 / pm) < 1e-12 and abs(w1[0] - .9 / pm) < 1e-12 and w1[1] == 1. and abs(w1[2] - .2 / pm) < 1e-12
    checks.append("Bayes step: awake weights times likelihood over the mixture; the sleeping stream keeps weight 1")
    wd2, w2 = update(1., w, q, .5, 1, .3)
    W0 = 3.
    assert abs(wd2 - (.7 * wd1 + .3 * W0 / 3)) < 1e-12 and w2[1] == 1. and abs(w2[0] - (.7 * w1[0] + .1 * W0)) < 1e-12
    assert abs((wd2 + w2[0] + w2[2]) - (wd1 + w1[0] + w1[2])) < 1e-12
    checks.append("fixed share returns weight evenly among the default and awake speakers, conserving their total; sleepers untouched")
    # a sleeping stream that wakes: its kept weight counts again
    r0 = dict(wd=1., w=w.copy(), q=q, pd=.5, letter=1)
    wd3, w3 = update(1., w, q, .5, 1, SHARE)
    r1 = dict(wd=wd3, w=w3, q=np.array([.5, .8, .5]), pd=.5, letter=0)
    assert replay_check([r0, r1])[0]["exact"]
    bad = dict(r1, w=w3 * np.array([1., 1., 1.1]))
    assert not replay_check([r0, bad])[0]["exact"]
    checks.append("replay check passes a consistent transition and refuses a perturbed one (sleeping/waking stream fixture)")
    out = dict(success=True, checks=checks)
    BASE.with_name(BASE.name + "_checks").with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


def analyse():
    out = dict(success=False, provenance=dict(
        revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        dirty=subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
        sha256={p: digest(ROOT / p) for p in ("lab/selection_share_audit.py", "lab/grownet.py", *SETS.values())},
        command="timeout 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/selection_share_audit.py --analyse",
        selector="grownet.py:782-815, BT=1, SHARE=.01 (teach.py:473, arm flag F), credit historical (pre-D82)"))
    try:
        rep = {}
        for name, path in SETS.items():
            d = pickle.loads((ROOT / path).read_bytes())
            lives = [l for l in (d["lives"] if isinstance(d, dict) else d) if "rows" in l]
            tr = [t for l in lives for t in replay_check(l["rows"])]
            per_life_exact = [all(t["exact"] for t in replay_check(l["rows"])) for l in lives]
            devs = np.array([t["dev"] for t in tr])
            bad = [t for t in tr if not t["exact"]]
            rep[name] = dict(lives=len(lives), transitions=len(tr), exact=int(sum(t["exact"] for t in tr)),
                             lives_fully_exact=int(sum(per_life_exact)), max_dev=float(devs.max()), median_dev=float(np.median(devs)),
                             inexact_changed_streams=dict(median=float(np.median([t["n_changed"] for t in bad])) if bad else None,
                                                          awake_at_issue_share=(sum(t["changed_awake_at_issue"] for t in bad) /
                                                                                max(1, sum(t["n_changed"] for t in bad)))))
            print(name, json.dumps(rep[name]), flush=True)
        out["replay"] = rep
        exact = all(r["exact"] == r["transitions"] for r in rep.values())
        out["replay_exact"] = exact
        if not exact:
            out["stopped"] = ("Saved rows hold issued forecasts at the last prediction; the historical selector updates with forecasts "
                              "scored at taste time, after earlier streams' learn calls, over the streams speaking then. Exact replay "
                              "is impossible from these rows, so the share comparison was not run.")
            out["capture_specification"] = dict(
                per_accepted_taste=["letter", "p_def(y) and the default's weight before the update",
                                    "for every stream: weight before and after the update, issued q(y), scored q(y), spoke at taste (bool)",
                                    "order of learn calls in the taste", "fixed share value and the rescale factor applied"],
                checks=["unobserved lives identical (fingerprint, result tuple)", "replay of the recorded scored forecasts reproduces "
                        "every next weight vector within 1e-12", "fail closed before any share comparison"],
                lives="the same D93, D102 and D101 lives (historical credit), or D82's issued contract lives, where issued = scored by construction",
                not_launched=True)
        out["success"] = True
    except Exception as e:
        out["error"] = repr(e)
        raise
    finally:
        BASE.with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    print("replay exact:", out.get("replay_exact"))


if __name__ == "__main__" and sys.argv[1] in ("--check", "--analyse"):
    {"--check": check, "--analyse": analyse}[sys.argv[1]]()


def replay_probs(rows, share):
    wd, w = rows[0]["wd"], rows[0]["w"].copy()
    ps = []
    for r in rows:
        awake = np.isfinite(r["q"])
        ps.append(float((wd * r["pd"] + np.dot(w[awake], r["q"][awake])) / (wd + w[awake].sum())))
        wd, w = update(wd, w, r["q"], r["pd"], r["letter"], share)
    return ps


def compare():
    import math
    loss = lambda p, y: -math.log2(min(1 - 1e-12, max(1e-12, p if y else 1 - p)))
    err = lambda p, y: .5 if p == .5 else float((p > .5) != bool(y))
    secs = {"sequence D93": 300., "sequence D102": 300., "timing D101": 3000.}
    out = dict(subset="lives whose every transition replays exactly (P=560 designs; D105: inert market)", results={})
    for name, path in SETS.items():
        d = pickle.loads((ROOT / path).read_bytes())
        lives = [l for l in (d["lives"] if isinstance(d, dict) else d) if "rows" in l and all(t["exact"] for t in replay_check(l["rows"]))]
        T = secs[name]
        per = {}
        maxerr = 0.
        for l in lives:
            rows = l["rows"]
            p1, p0 = replay_probs(rows, SHARE), replay_probs(rows, 0.)
            maxerr = max(maxerr, max(abs(a - r["p1"]) for a, r in zip(p1, rows)))
            ys = [r["letter"] for r in rows]
            ts = [r["taste_t"] for r in rows]
            v = {}
            for w, lo, hi in (("first_third", 0, T / 3), ("last_third", 2 * T / 3, T + 1), ("full", 0, T + 1)):
                idx = [i for i, t in enumerate(ts) if lo <= t < hi]
                n = len(idx)
                v[w] = dict(n=n, share=(sum(loss(p1[i], ys[i]) for i in idx) / n, sum(err(p1[i], ys[i]) for i in idx) / n),
                            zero=(sum(loss(p0[i], ys[i]) for i in idx) / n, sum(err(p0[i], ys[i]) for i in idx) / n),
                            choice_changes=sum((p1[i] > .5) != (p0[i] > .5) for i in idx))
            per[l["seed"], l["first"]] = v
        assert maxerr <= 1e-9, ("share .01 replay does not reproduce native", maxerr)
        seeds = sorted({s for s, _ in per})
        order = [(s, c) for s in seeds for c in ("red", "blue")]
        k = np.random.default_rng(0).integers(0, len(seeds), (2000, len(seeds)))
        idx = np.concatenate((2 * k, 2 * k + 1), axis=1)
        r = dict(lives=len(per), max_native_reproduction_error=maxerr)
        for w in ("first_third", "last_third", "full"):
            for j, m in ((0, "bits"), (1, "errors")):
                dd = np.array([per[o][w]["zero"][j] - per[o][w]["share"][j] for o in order])
                r[f"{w} | {m} per taste, share 0 - share .01"] = dict(per_life_mean=float(dd.mean()),
                                                                      ci95=[float(x) for x in np.quantile(dd[idx].mean(1), [.025, .975])])
            r[f"{w} | share .01 level bits"] = float(np.mean([per[o][w]["share"][0] for o in order]))
            r[f"{w} | choice changes"] = int(sum(per[o][w]["choice_changes"] for o in order))
            r[f"{w} | tastes"] = int(sum(per[o][w]["n"] for o in order))
        out["results"][name] = r
        print(name, json.dumps(r), flush=True)
    BASE.with_name(BASE.name + "_compare").with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__" and sys.argv[1] == "--compare":
    compare()

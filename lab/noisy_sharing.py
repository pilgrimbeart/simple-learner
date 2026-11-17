"""D74: learn readout partitions from past labels on fixed histories.

Diagnostic, not a robot component. Implements ordered-context weighting (Willems,
Shtarkov & Tjalkens 1996, class II) with either their uniform-option prior or a
half-stop prior. The latter gives stopping probability 1/2 at each nonsingleton
interval, sharing the other half among its possible cuts. Neither prior supplies
a particular boundary or label orientation. All leaves use Beta(1/2,1/2).
The fixed value order, alphabet, stationary conditional model and priors ARE supplied.
No current label, hidden target, actual eaten colour or future event enters prediction.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import pickle
import subprocess
import time

import numpy as np
from numba import njit

ROOT = Path(__file__).resolve().parents[1]
K = 15
PRIORS = ("uniform_options", "half_stop")
PERMUTATION = np.random.default_rng(740).permutation(K)


@njit(cache=True)
def interval_replay(x, y, train, size, half_stop):
    """Exact Bayesian mixture over all recursive interval splittings.

    Only intervals containing the observed symbol are touched. Counts and log
    likelihoods are unbounded exact software state, not a circuit cost model.
    Returns forecasts, final local posterior weights, and expected group counts.
    """
    counts = np.zeros((size, size + 1, 2))
    log_est = np.zeros((size, size + 1))
    log_mix = np.zeros((size, size + 1))
    pred = np.zeros((size, size + 1))
    out = np.zeros(len(x))
    for event in range(len(x)):
        symbol = x[event]
        # Shorter intervals supply predictions to their parents, before any update.
        for width in range(1, size + 1):
            for left in range(max(0, symbol - width + 1), min(symbol, size - width) + 1):
                right = left + width
                p = (counts[left, right, 1] + .5) / (counts[left, right].sum() + 1.)
                if width > 1:
                    stop_prior = .5 if half_stop else 1. / width
                    split_prior = .5 / (width - 1) if half_stop else 1. / width
                    p *= math.exp(math.log(stop_prior) + log_est[left, right] - log_mix[left, right])
                    for cut in range(left + 1, right):
                        mass = math.exp(math.log(split_prior) + log_mix[left, cut]
                                        + log_mix[cut, right] - log_mix[left, right])
                        child = pred[left, cut] if symbol < cut else pred[cut, right]
                        p += mass * child
                pred[left, right] = p
        out[event] = pred[0, size]
        if not train[event]:
            continue
        # Sequential likelihood update, bottom up, AFTER issuing the forecast.
        for width in range(1, size + 1):
            for left in range(max(0, symbol - width + 1), min(symbol, size - width) + 1):
                right = left + width
                p = (counts[left, right, y[event]] + .5) / (counts[left, right].sum() + 1.)
                log_est[left, right] += math.log(p)
                counts[left, right, y[event]] += 1
                if width == 1:
                    log_mix[left, right] = log_est[left, right]
                else:
                    stop_prior = .5 if half_stop else 1. / width
                    split_prior = .5 / (width - 1) if half_stop else 1. / width
                    total = math.log(stop_prior) + log_est[left, right]
                    for cut in range(left + 1, right):
                        term = math.log(split_prior) + log_mix[left, cut] + log_mix[cut, right]
                        total = np.logaddexp(total, term)
                    log_mix[left, right] = total
    stop = np.zeros((size, size + 1))
    cuts = np.zeros((size, size + 1, size))
    groups = np.zeros((size, size + 1))
    for width in range(1, size + 1):
        for left in range(size - width + 1):
            right = left + width
            if width == 1:
                stop[left, right] = 1.
                groups[left, right] = 1.
            else:
                stop_prior = .5 if half_stop else 1. / width
                split_prior = .5 / (width - 1) if half_stop else 1. / width
                stop[left, right] = math.exp(math.log(stop_prior) + log_est[left, right] - log_mix[left, right])
                groups[left, right] = stop[left, right]
                for cut in range(left + 1, right):
                    mass = math.exp(math.log(split_prior) + log_mix[left, cut]
                                    + log_mix[cut, right] - log_mix[left, right])
                    cuts[left, right, cut] = mass
                    groups[left, right] += mass * (groups[left, cut] + groups[cut, right])
    return out, stop, cuts, groups, log_mix[0, size]


@njit(cache=True)
def categorical_replay(x, y, train, size):
    counts = np.full((size, 2), .5)
    out = np.zeros(len(x))
    for event in range(len(x)):
        out[event] = counts[x[event], 1] / counts[x[event]].sum()
        if train[event]:
            counts[x[event], y[event]] += 1
    return out


def forecasts(x, y, train):
    out = {"independent": categorical_replay(x, y, train, K),
           "supplied_sign_groups": categorical_replay((x > 7).astype(np.int64), y, train, 2),
           "single_group": categorical_replay(np.zeros_like(x), y, train, 1)}
    posterior = {}
    for name, values, half in (("uniform_options", x, False), ("half_stop", x, True),
                                ("permuted_half_stop", PERMUTATION[x], True)):
        p, stop, cuts, groups, lm = interval_replay(values, y, train, K, half)
        out[name] = p
        posterior[name] = dict(expected_groups=float(groups[0, K]),
                               root_stop=float(stop[0, K]), root_cuts=cuts[0, K].tolist(),
                               cumulative_label_bits=float(-lm / math.log(2)))
    return out, posterior


def loss(p, y):
    return -np.log2(np.clip(np.where(y, p, 1-p), 1e-15, 1.))


def metrics(pred, t, target, labels, train, seconds):
    ans = {}
    for period, start in (("whole", 0.), ("last_third", seconds * 2 / 3)):
        use = (t >= start) & (t < seconds)
        learn = use & train
        ans[period] = dict(n_events=int(use.sum()), n_labels=int(learn.sum()), accuracy={}, label_bits={})
        for name, p in pred.items():
            # Match D73/current brain's tie rule: probability .5 chooses label 0.
            ans[period]["accuracy"][name] = float(np.mean((p[use] > .5) == target[use]))
            ans[period]["label_bits"][name] = float(loss(p[learn], labels[learn]).mean())
    return ans


def summary(rows):
    seeds = sorted({r["seed"] for r in rows})
    draws = np.random.default_rng(74).integers(len(seeds), size=(10000, len(seeds)))
    result = {}
    for period in ("whole", "last_third"):
        result[period] = {}
        for metric in ("accuracy", "label_bits"):
            names = rows[0]["metrics"][period][metric]
            values = {name: np.array([np.mean([r["metrics"][period][metric][name]
                      for r in rows if r["seed"] == seed]) for seed in seeds]) for name in names}
            result[period][metric] = {}
            for name, vals in values.items():
                d = vals - values["independent"]
                result[period][metric][name] = dict(mean=float(vals.mean()),
                    difference_from_independent=float(d.mean()),
                    paired_ci95=np.quantile(d[draws].mean(1), [.025, .975]).tolist())
    return result


def raw_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def provenance():
    return dict(revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                dirty=subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
                script_sha256=raw_sha(Path(__file__)), permutation=PERMUTATION.tolist(),
                supplied_priors="15 ordered symbols; stationary Bernoulli per interval; Beta(.5,.5); stated split priors")


@lru_cache(None)
def explicit_models(left, right, half):
    """Independent exhaustive enumeration of recursive models, for small checks."""
    if right-left == 1:
        return [(((left, right),), 1.)]
    stop = .5 if half else 1/(right-left)
    split = .5/(right-left-1) if half else stop
    out = [(((left, right),), stop)]
    for cut in range(left+1, right):
        for a, pa in explicit_models(left, cut, half):
            for b, pb in explicit_models(cut, right, half):
                out.append((a+b, split*pa*pb))
    return out


def exhaustive_replay(x, y, train, size, half):
    models = explicit_models(0, size, half)
    weights = np.array([p for _, p in models])
    counts = [np.full((len(parts), 2), .5) for parts, _ in models]
    out = []
    for symbol, label, learn in zip(x, y, train):
        indices = [next(j for j, (lo, hi) in enumerate(parts) if lo <= symbol < hi) for parts, _ in models]
        pred = np.array([c[j, 1]/c[j].sum() for c, j in zip(counts, indices)])
        out.append(weights @ pred / weights.sum())
        if learn:
            weights *= np.where(label, pred, 1-pred)
            for c, j in zip(counts, indices):
                c[j, label] += 1
    groups = sum(w*len(m[0]) for w, m in zip(weights, models))/weights.sum()
    return np.array(out), groups, math.log(weights.sum())


def checks():
    rng = np.random.default_rng(741)
    x, y, train = rng.integers(5, size=70), rng.integers(2, size=70), rng.random(70) < .8
    for half in (False, True):
        actual, _, _, groups, lm = interval_replay(x, y, train, 5, half)
        expected, eg, el = exhaustive_replay(x, y, train, 5, half)
        np.testing.assert_allclose(actual, expected, atol=1e-12, rtol=0)
        assert abs(groups[0, 5]-eg) < 1e-12
        assert abs(lm-el) < 1e-12
        np.testing.assert_array_equal(interval_replay(x[:30], y[:30], train[:30], 5, half)[0], actual[:30])
        assert abs(loss(actual[train], y[train]).sum()+lm/math.log(2)) < 1e-10
    print("PASS: interval recursion equals exhaustive model enumeration; likelihood, group count and prefix causality", flush=True)


def recorded(path):
    data = pickle.loads(path.read_bytes())
    out = []
    for life in data["lives"]:
        rows = life["rows"]
        x = np.array([r["signed_bank"][16.]["symbol"] for r in rows], dtype=np.int64)
        y = np.array([r["inferred_eye"] ^ (r["value"] < 0) for r in rows], dtype=np.int64)
        train = np.array([r["vouched"] for r in rows])
        t = np.array([r["t"] for r in rows])
        target = np.array([r["truth"] for r in rows])
        p, post = forecasts(x, y, train)
        np.testing.assert_allclose(p["independent"], [r["signed_bank"][16.]["root_q"] for r in rows], atol=1e-13, rtol=0)
        p["brain"] = np.array([r["p1"] for r in rows])
        out.append(dict(seed=life["seed"], first=life["first"],
                        metrics=metrics(p, t, target, y, train, life["seconds"]), posterior=post,
                        label_counts=np.bincount(x[train], minlength=K).tolist(),
                        prediction={key: val.tolist() for key, val in p.items()}))
    print("PASS: all 8 native independent readouts reproduced from the exact stored symbols", flush=True)
    return dict(record_path=str(path.resolve()), record_sha256=raw_sha(path), source_provenance=data["provenance"],
                source_config=data["config"], per_life=out, summary=summary(out))


def artificial():
    rows = {name: {1000.: [], 10000.: []} for name in ("shifted_boundary", "alternating", "no_signal")}
    for seed in range(174000, 174024):
        rng = np.random.default_rng(seed)
        duration, rate, error = 10000., .6, .35
        # A Poisson point process: uniform event times conditional on its Poisson count.
        n = rng.poisson(rate*duration)
        t = np.sort(rng.uniform(0., duration, n))
        x = rng.integers(K, size=n)
        orientation = rng.integers(2)
        flip = rng.random(n) < error
        cases = {"shifted_boundary": ((x >= 4) ^ orientation).astype(np.int64),
                 "alternating": ((x % 2) ^ orientation).astype(np.int64),
                 "no_signal": rng.integers(2, size=n)}
        train = np.ones(n, dtype=np.bool_)
        for name, target in cases.items():
            labels = (target ^ flip).astype(np.int64)
            pred, post = forecasts(x, labels, train)
            pred["known_mapping"] = np.full(n, .5) if name == "no_signal" else error+(1-2*error)*target
            for seconds in rows[name]:
                rows[name][seconds].append(dict(seed=seed, metrics=metrics(pred, t, target, labels, train, seconds),
                    # Long-horizon posterior only. Do not label it a 1000 s posterior.
                    posterior_at_10000s=post if seconds == 10000. else None))
    return {name: {str(int(seconds)): dict(per_life=r, summary=summary(r)) for seconds, r in bytime.items()}
            for name, bytime in rows.items()}


def resource_account():
    def full_prior(n, half):
        p = np.ones(n+1)
        for m in range(2, n+1):
            split = .5/(m-1) if half else 1/m
            p[m] = split*sum(p[k]*p[m-k] for k in range(1, m))
        return p[n]
    # Each split product has two child inputs and one parent output; intervals
    # also have a stop estimate. These are logical links, not transistor counts.
    return dict(alphabet=K, intervals=K*(K+1)//2, possible_splits=K*(K-1)*(K+1)//6,
                max_intervals_touched=max((x+1)*(K-x) for x in range(K)),
                uniform_mean_intervals_touched=float(np.mean([(x+1)*(K-x) for x in range(K)])),
                two_group_boundary_prior_bits={"uniform_options": math.log2(K*4*(K-4)),
                                               "half_stop": math.log2(8*(K-1))},
                all_separate_prior_bits={name: -math.log2(full_prior(K, name == "half_stop")) for name in PRIORS})


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--record", type=Path, default=ROOT/"lab/v/noisy_path_signed.pkl")
    ap.add_argument("--out", type=Path, default=ROOT/"lab/v/noisy_sharing.json")
    args = ap.parse_args()
    start, cpu = time.monotonic(), time.process_time()
    checks()
    if args.check:
        return
    result = dict(provenance=provenance(), resources=resource_account(), recorded=recorded(args.record))
    print("Recorded final-third:", json.dumps(result["recorded"]["summary"]["last_third"]), flush=True)
    result["artificial"] = artificial()
    for name, horizons in result["artificial"].items():
        for horizon, row in horizons.items():
            print(name, horizon, json.dumps(row["summary"]["last_third"]), flush=True)
    result["wall_seconds"] = time.monotonic()-start
    result["cpu_seconds"] = time.process_time()-cpu
    args.out.write_text(json.dumps(result, indent=2)+"\n")
    print("Resources", result["resources"], flush=True)
    print("wall_seconds", result["wall_seconds"], "cpu_seconds", result["cpu_seconds"], flush=True)


if __name__ == "__main__":
    main()

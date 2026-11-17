"""D75: exact copies isolate the information-free effect of predictor multiplicity.

This is a fixed-history selector diagnostic. Copying does not invent observations,
change the expert forecasts or alter their waking patterns. A preserved prior also
divides the weight redistributed at each accepted label, not just at birth.
"""
from pathlib import Path
import json
import pickle
import subprocess
import time

import numpy as np

from noisy_path_replay import mix
from noisy_sharing import metrics, raw_sha, summary

ROOT = Path(__file__).resolve().parent


def weighted_mix(q, y, train, scored, initial, share_prior, share=.01):
    w = initial.copy()
    out = []
    for row, scored_row, label, learn in zip(q, scored, y, train):
        on = np.isfinite(row)
        out.append(float(w[on] @ row[on] / w[on].sum()))
        if learn:
            on = np.isfinite(scored_row)
            total = w[on].sum()
            likelihood = np.where(label, scored_row[on], 1-scored_row[on])
            mean = w[on] @ likelihood / total
            w[on] *= likelihood / mean
            w[on] = (1-share)*w[on] + share*total*share_prior[on]/share_prior[on].sum()
            w /= w.max()
    return np.array(out)


def copied(q, scored, index, copies=8):
    indices = np.r_[np.arange(q.shape[1]), np.full(copies-1, index)]
    prior = np.ones(len(indices))
    prior[indices == index] /= copies
    return q[:, indices], scored[:, indices], prior


def checks():
    q = np.array([[.8, .2], [np.nan, .9], [.7, .1]])
    y, v, prior = np.array([1, 0, 1]), np.ones(3, bool), np.array([.6, .4])
    p = weighted_mix(q, y, v, q, prior, prior, .1)
    expected_a = .9*(.6*.8/.56) + .1*.6
    np.testing.assert_allclose(p, [.56, .9, expected_a*.7+(1-expected_a)*.1], atol=1e-14, rtol=0)
    rng = np.random.default_rng(75)
    q = rng.uniform(.05, .95, (100, 6))
    q[rng.random(q.shape)<.3] = np.nan
    q[:, 0] = .5  # ensure a waking specialist
    y, v = rng.integers(2, size=100), rng.random(100)<.8
    for share in (0., .01):
        base = weighted_mix(q, y, v, q, np.ones(6), np.ones(6), share)
        qq, ss, prior = copied(q, q, 2)
        p = weighted_mix(qq, y, v, ss, prior, prior, share)
        np.testing.assert_allclose(p, base, atol=1e-13, rtol=0)
        np.testing.assert_array_equal(weighted_mix(q[:30], y[:30], v[:30], q[:30],
                                     np.ones(6), np.ones(6), share), base[:30])
    print("PASS: independent three-event calculation; exact-copy invariance with sleepers and sharing; causal prefix")


def main():
    start, cpu = time.monotonic(), time.process_time()
    checks()
    path = ROOT / "v/noisy_path_signed.pkl"
    source = pickle.loads(path.read_bytes())
    results = {"default": [], "signed_16s": []}
    for life in source["lives"]:
        rows = life["rows"]
        q, scored = np.stack([r["q"] for r in rows]), np.stack([r["scored_q"] for r in rows])
        y = np.array([r["inferred_eye"] ^ (r["value"]<0) for r in rows], dtype=int)
        train = np.array([r["vouched"] for r in rows])
        target, t = np.array([r["truth"] for r in rows]), np.array([r["t"] for r in rows])
        base = weighted_mix(q, y, train, scored, np.ones(q.shape[1]), np.ones(q.shape[1]))
        np.testing.assert_allclose(base, [r["p1"] for r in rows], atol=1e-12, rtol=0)
        for name, column in (("default", "default"), ("signed_16s", "lbldt4")):
            index = life["names"].index(column)
            qq, ss, prior = copied(q, scored, index)
            uniform = np.ones(len(prior))
            pred = {"independent": base,  # shared summariser calls its reference 'independent'
                    "eight_equal_copies": weighted_mix(qq, y, train, ss, uniform, uniform),
                    "divide_initial_only": weighted_mix(qq, y, train, ss, prior, uniform),
                    "divide_initial_and_share": weighted_mix(qq, y, train, ss, prior, prior)}
            np.testing.assert_allclose(pred["divide_initial_and_share"], base, atol=1e-12, rtol=0)
            # Without redistribution, conserving only the initial weight is sufficient.
            noshare, _ = mix(q, y, train, 0., scored)
            np.testing.assert_allclose(weighted_mix(qq, y, train, ss, prior, uniform, 0.), noshare, atol=1e-12, rtol=0)
            result = dict(seed=life["seed"], first=life["first"], copied_column=column,
                          metrics=metrics(pred, t, target, y, train, life["seconds"]),
                          max_prediction_difference={k: float(np.max(np.abs(p-base))) for k, p in pred.items()},
                          last_third_changed_choice={k: float(np.mean((p[t>=life["seconds"]*2/3]>.5)
                            != (base[t>=life["seconds"]*2/3]>.5))) for k, p in pred.items()})
            results[name].append(result)
    provenance = dict(revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                      dirty=subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
                      supplied_knowledge="Exact clone identity is declared, not inferred from observations.",
                      hashes={p: raw_sha(ROOT/p) for p in ("noisy_redundancy.py", "noisy_path_replay.py", "noisy_sharing.py")})
    payload = dict(provenance=provenance, script_sha256=raw_sha(Path(__file__)),
                   record_path=str(path), record_sha256=raw_sha(path), copies=8,
                   source_config=source["config"], source_provenance=source["provenance"],
                   reference_label="independent means the unmodified recorded selector, not independent readout bins",
                   comparisons={k: dict(per_life=r, summary=summary(r)) for k, r in results.items()},
                   wall_seconds=time.monotonic()-start, cpu_seconds=time.process_time()-cpu)
    (ROOT / "v/noisy_redundancy.json").write_text(json.dumps(payload, indent=2)+"\n")
    for name, d in payload["comparisons"].items():
        print(name, json.dumps(d["summary"]["last_third"]))
        print("changed choices", {k: np.mean([r["last_third_changed_choice"][k] for r in d["per_life"]])
                                   for k in d["per_life"][0]["last_third_changed_choice"]})
        print("max preserved-mass error", max(r["max_prediction_difference"]["divide_initial_and_share"] for r in d["per_life"]))
    print("PASS: all original selector probabilities reconstructed; copies with conserved initial and shared mass are invariant")
    print("wall_seconds", payload["wall_seconds"], "cpu_seconds", payload["cpu_seconds"])


if __name__ == "__main__":
    main()

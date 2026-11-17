"""D74 post-run diagnosis: exact model evidence, prior costs and sequence-loss checks."""
from pathlib import Path
import json
import math
import pickle

import numpy as np

from noisy_sharing import loss, resource_account

ROOT = Path(__file__).resolve().parent
result = json.loads((ROOT / "v/noisy_sharing.json").read_text())
record = pickle.loads((ROOT / "v/noisy_path_signed.pkl").read_bytes())
LN2 = math.log(2)


def kt_bits(counts):
    a, b = counts
    return -(math.lgamma(a+.5)+math.lgamma(b+.5)-math.lgamma(a+b+1)
             -2*math.lgamma(.5))/LN2


print("Same recorded symbols: cumulative evidence for the supplied sign partition versus a single probability")
diagnosis = []
for life, saved in zip(record["lives"], result["recorded"]["per_life"]):
    counts = np.zeros((15, 2), dtype=int)
    labels, train = [], []
    for row in life["rows"]:
        z = row["inferred_eye"] ^ (row["value"] < 0)
        labels.append(z)
        train.append(row["vouched"])
        if row["vouched"]:
            counts[row["signed_bank"][16.]["symbol"], z] += 1
    labels, train = np.array(labels), np.array(train)
    one = kt_bits(counts.sum(0))
    sign = kt_bits(counts[:8].sum(0)) + kt_bits(counts[8:].sum(0))
    independent = sum(kt_bits(c) for c in counts)
    item = dict(seed=life["seed"], first=life["first"], labels=int(counts.sum()),
                one_group_bits=one, sign_group_bits=sign, independent_bits=independent,
                evidence_bits_sign_over_one=one-sign, posterior_sign_partition={})
    for prior in ("uniform_options", "half_stop"):
        prior_sign = 1/(15*8*7) if prior == "uniform_options" else 1/(8*14)
        mix_bits = saved["posterior"][prior]["cumulative_label_bits"]
        item["posterior_sign_partition"][prior] = 2**(mix_bits-sign+math.log2(prior_sign))
        # Pointwise mixture bound, independent of whether the model generated the data.
        bound = resource_account()["all_separate_prior_bits"][prior]
        assert mix_bits <= independent+bound+1e-9
    # Independent integrated likelihood and sequential predictions must match.
    for name, bits in (("single_group", one), ("supplied_sign_groups", sign), ("independent", independent)):
        pred = np.array(saved["prediction"][name])
        assert abs(loss(pred[train], labels[train]).sum()-bits) < 1e-8
    diagnosis.append(item)
    print(life["seed"], life["first"], "labels", counts.sum(), "sign versus one bits", round(one-sign, 3),
          "posterior supplied sign partition", {k: round(v, 4) for k, v in item["posterior_sign_partition"].items()})

print("Prior odds sign partition / single group are 1/56 in BOTH tested priors: a 5.807-bit evidence hurdle.")
print("This is an odds scale, not a performance guarantee or a stopping threshold supplied to a brain.")
print("PASS: independent Beta-integrated likelihood equals causal sequential loss; mixture regret within declared prior bound")
for case, horizons in result["artificial"].items():
    for horizon, data in horizons.items():
        for prior in ("uniform_options", "half_stop"):
            differences = []
            for life in data["per_life"]:
                m = life["metrics"]["whole"]
                delta = m["n_labels"] * (m["label_bits"][prior]-m["label_bits"]["independent"])
                differences.append(delta)
                assert delta <= resource_account()["all_separate_prior_bits"][prior]+1e-8
            print(case, horizon, prior, "cumulative extra bits over independent mean/max",
                  round(float(np.mean(differences)), 3), round(float(max(differences)), 3))
print("PASS: all artificial streams satisfy the pointwise mixture bound, including short alternating failures")
(ROOT / "v/noisy_sharing_evidence.json").write_text(json.dumps(diagnosis, indent=2)+"\n")

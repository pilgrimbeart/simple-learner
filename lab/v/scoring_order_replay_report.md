# D80 selector-credit replay

2026-11-17. This is a fixed-history diagnostic, not a repaired closed-loop brain.
Protocol, interpretation and subsequent branch: [discrete notebook D80](../../discrete/NOTEBOOK.md#d80-scoring-replay).

The original likelihood and fixed-share updates reproduce all four D79 lives: maximum weight error
2.28e-13, probability error 3e-15 and cumulative code-length error 1.43e-14 bits. Final stream weights
and saved-bit records also match the independent D78 dilution records. The hand-computable update,
sleeping-weight invariance and active-mass conservation checks pass. This is exact rule replay within
floating arithmetic, not a claim of bit-for-bit equality: stored p(1) must be complemented for label 0.

Correcting the forecast used for credit, while freezing all observations, labels, gates, future forecasts
and memory, gives:

| brain / poison colour | changed issued choices / predictions | reversed distinguishable weight comparisons at accepted tastes | corrected minus original loss on accepted labels |
|---|---:|---:|---:|
| original / red | 0 / 5700 | 2841 / 2397510 | +.00211 bits / 184 labels |
| original / blue | 0 / 5722 | 1145 / 2448275 | +.00104 bits / 187 labels |
| weight contest / red | 1 / 5920 | 84857 / 2097888 | −.00833 bits / 163 labels |
| weight contest / blue | 1 / 5705 | 90742 / 2279680 | −.05339 bits / 176 labels |

None of the changed choices is within 1e-12 of probability .5. The final dominant stream remains
good:colour throughout. Pairwise comparisons exclude the default and pairs whose normalized weight
gap is at most 1e-12 in either branch. They use weights at taste entry, before this taste's learning
and contests. Sleeping streams belong in this allocation comparison because the actual allocator
compares their stored weights too. Repeated pair comparisons are not independent samples and are
not the actual contests: sampled opponents and eligible leaves were not recorded.

The direct prediction effect is small, but about 4% of distinguishable stream-weight comparisons
reverse under the contest. A small change in output probability does not establish a small effect
on memory allocation. This motivated D81's separately budgeted closed-loop check. No new allocator,
population inference, information-theoretic bound or physical cost claim follows from this replay.

The lower-effort agent completed the original validation but hit its usage limit after an output
summary error. The lead inspected the code and fixed the summary: rejected tastes have no labelled
loss, so loss aggregation now selects the labelled records and reports their denominator. The failed
JSON/log are retained as scoring_order_replay_failed_summary.{json,log}; their run took 1.38 s.
The successful replay took 2.88 s. No simulation was run for D80. Tolerances and science metrics did
not change. The lead also reconstructed the two changed-choice times in scoring_feedback_analysis.py.

Files: [script](../scoring_order_replay.py), [JSON](scoring_order_replay.json),
[log](scoring_order_replay.log). JSON records revision d37dac6, dirty files, source/input hashes,
command, tolerances, each validation error, per-life/window outputs and final per-stream changes.
The source of the specialist likelihood update is [Freund et al. (1997), section 3.1](https://cseweb.ucsd.edu/~yfreund/papers/SpecializedExperts.pdf);
the .01 sharing rule is the recorded brain's implementation, not a newly fitted parameter.

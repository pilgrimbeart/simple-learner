# Phase-bias decomposition — D137

Original transfer-equation prediction: RMSE **0.020 mV**, maximum error 0.048 mV; observed RMS bias 99.21 mV. Fourier resolution change 5.55e-17 V.

| Informed algebraic intervention | Predicted RMS zero-phase bias (mV) |
|---|---:|
| original | 99.210 |
| zero output offsets | 71.273 |
| equal output gains | 85.834 |
| equal upstream | 63.621 |
| equal output transfers | 56.765 |
| both matched | 0.000 |

These are counterfactual transfer-equation calculations, not new circuit results. Effects interact and are not additive. Averaging away manufacturing differences requires information unavailable to the brain. The analysis retains nonlinear source/gate functions and finite-window periodic ripple, but omits rail fading, stochastic variation and startup transients. Validation error is reported against the original noisy runs. No calibrated control, phase locking or learned reference has been demonstrated.

Reproduce with lab/phase_bias.py in a fresh output folder. Protocol, all predictions, source hashes and raw source provenance are retained.

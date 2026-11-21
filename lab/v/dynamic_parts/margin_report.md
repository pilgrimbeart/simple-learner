# Oscillator operating-margin diagnosis — D127

Offline analysis of the 40 D126 component draws. No new oscillator trajectories or fresh performance evaluation.

Offsets are the clearest discriminator: setting only connection offsets to zero makes every located equilibrium unstable. Restoring nominal gains, slopes, leaks or capacitances does not remove stable equilibria from the three failed draws. This is an algebraic counterfactual, not a buildable zero-mismatch cure.

| Seed | Original cycle result | Original maximum eigenvalue real part, /s | Offsets removed, /s | Recovery gain ×1.4, /s |
|---|---|---:|---:|---:|
| 51005 | pass | -1.964 | 75.671 | 3.739 |
| 51006 | fail | -5.847 | 91.527 | 1.331 |
| 51011 | fail | -6.607 | 29.781 | -4.729 |
| 51036 | fail | -6.550 | 120.682 | -0.559 |

Positive means perturbations grow locally; negative means they decay near this equilibrium. Seed 51005 shows why this cannot classify cycles alone: it sustained a cycle while its located resting point is also locally stable. This supports possible coexistence of attractors; their basins have not been mapped.

For the local Jacobian [[p,-b],[c,-d]], an unstable nonsaddle rest requires p>d and bc>pd. Away from rail effects, nominal fast self-feedback gives p=150 sech²((x-offset)/0.15)-50 per second and d=5 per second. Thus the first condition requires |x-offset|<0.163 V. This is a local state-dependent range, not a global parameter guarantee.

The single predicted adjustment (recovery-to-fast current ×7/5) leaves two failed roots stable. It is rejected as an established repair; no second knob trial was made. Next investigate equilibrium structure and offset tolerance, including the successful seed with stable rest.

Sources and pre-work predictions: discrete/NOTEBOOK.md D127. Exact inputs and algebraic results: margin_v1.json and margin_v2.json. Source snapshots: lab/dynamic_parts_margin_v1.py (hash matches v1) and lab/dynamic_parts_margin.py. Original noise engine unchanged. A single Newton root per condition is not proof that no other equilibria exist.

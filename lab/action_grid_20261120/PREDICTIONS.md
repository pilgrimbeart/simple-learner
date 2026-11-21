# Action grid — predictions, frozen before any grid simulation (2026-11-20)

Written from D181/D182's saved summaries only (baseline informed final-third food 0.19/10 s, informed-minus-neutral
net +0.056 [0.005, 0.108], all-food informed 0.47/10 s, rail excursions in 52/64 informed lives). Probabilities are my
subjective uncertainty, not tests.

1. Baseline development reproduces D180's 384 lives exactly (meals, counts, traces): 97%.
2. Marginals on informed net (level minus baseline level): sensory gain 2× small positive (p(sign>0) 0.6);
   gain 0.5× negative (0.65). Motor decay 2.5 ms: more motor events and re-arms under sustained input in benches
   (0.8); its life effect on net uncertain (0.5). Exploration threshold 0.30 V: fewer exploratory events and shorter
   path (0.8), lower informed net through fewer encounters (0.6). Oscillator speed 1.5: more events/path (0.7),
   net effect uncertain (0.5).
3. Best development informed net among the 80 non-baseline settings: about 0.10–0.25 per 10 s (selection-inflated).
4. Fresh confirmation: selected candidates shrink towards baseline by about half. P(at least one candidate's
   corrected primary lower bound > 0 at all three ratios) = 0.35; P(practically established, > +0.10) = 0.10.
5. No candidate meets D180's absolute food-rate gate (≥ 1 food/10 s lower bound): 0.95.
6. Rail excursions persist (P memories / writers or motors), so no candidate is physically eligible: 0.8.
7. Integration convergence within ±0.05 for the primary contrast at both halvings: 0.6.
8. All-food no-harm for the selected candidates: 0.6; stranding no-harm: 0.5.

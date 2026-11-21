# Contract — the shared-readout candidate (D170, frozen 2026-11-20 before any trajectory)

**Status: hypothetical connection, studied only in a labelled mathematical reference. Not a catalogue part.**
Numbers: [bounds.json](bounds.json), from `lab/shared_readout_20261120/bounds.py` (units.py, chip.py and D168's saved
arithmetic only; no trajectory or outcome). Sources: [SOURCE_REVIEW.md](SOURCE_REVIEW.md).

## 1. What it does, in one paragraph

The order detector has a balance knob d. Its output u should read zero on average when two inputs arrive together
(an anchor). One differential pair reads the difference between u and a quiet-tracking node m. Its output current is
split by the coincidence voltage: a share w goes to the knob's memory, the share 1 − w to m. In quiet time (w ≈ 0) m
follows u, so it holds u's resting level minus the pair's own offset. During an anchor (w → 1) m is starved and holds,
and the knob is written by u − m: the anchor's response above the resting level, with the pair's offset cancelled
because the same pair made both readings.

## 2. Equations (all SI)

Order output (unchanged circuit, node 7, leak g7, capacitance C7; branch currents I5 from node 4 and I6 from node 5,
the existing tanh connections):

    C7 dv7/dt = -g7 v7 + (1 + d) I5 + (1 - d) I6,   d = clip(V_d / V_TYP, -1, 1)

The knob scales the positive-path connection by 1 + d and the negative-path one by 1 − d, which is exactly the setting
`score_branches` scores (y = u + d·v). Its gate law: the stored voltage V_d controls the two gains through D145's
complementary-gate construction, nominal transfer d = V_d/V_TYP clipped to ±1 (V_TYP = RAIL/3 = 0.3 V; units.py's comment "0.2 V" is stale). Errors of that gating are inside the
knob loop (D168 error map, stage 8): they change B (speed) and the reachable range, not the equilibrium output, and are
not modelled further. **Feedback sign**: B = ∂(∫w·u)/∂d > 0 in every D163 record and by construction (raising d
strengthens the positive path that dominates the anchor response), so the knob must move *against* the reading.

Shared reading (the candidate), with T = tanh(s·(v7 − m − e)):

    I_k = k_w I0 [ (1+α/2) w1 (1+T)/2 − (1−α/2) w2 (1−T)/2 ]          (to the knob writer)
    I_m = k_q I0 [ (1+β/2) (1−w1) (1+T)/2 − (1−β/2) (1−w2) (1−T)/2 ]  (to the tracker)
    C_m dm/dt  = −g_m (m − V_bias) + I_m
    C_d dV_d/dt = −sign(I_k) · max(|I_k| − DEAD·k_w·I0, 0)            (memory write, chip.DEAD dead band)

w_i = clip((V6 − g_i)/V_TYP, 0, 1): the engine's gate law on the existing coincidence voltage V6; g_i are the two
steering pairs' offsets, zero in the nominal condition (the engine draws none). With w1 = w2 = w these reduce to
I_k = k_w I0 w (T + α/2) and I_m = k_q I0 (1 − w)(T + β/2). Current is conserved: for each branch the knob's and the
tracker's shares sum to the branch current.

Separate reading paths (control), each pair with its own gated tail, T_w = tanh(s(v7 − m − e)), T_q = tanh(s(v7 − m − e_q)):

    I_k = k_w I0 w1 (T_w + α/2),   I_m = k_q I0 (1 − w2)(T_q + β/2)

With e_q = e and w1 = w2 the two forms are identical (checked in `checks.py`).

Internal states: v7 (existing), m (new dynamic node), V_d (new retained memory). The upstream nodes 0–6 are the unchanged
analytic trajectories (no feedback from the new parts reaches them). Rails: m and V_d clamped at ±RAIL; excursions
recorded. Rail fading near the supply is omitted, as in the analytic trajectories (D167/D168 limitation).

## 3. Fixed points, stability, residuals, settling (derivation; numbers in bounds.json)

- **Tracker at rest** (w = 0, u constant): g_m m = k_q I0 tanh(s(u − m − e)) + β-term. Linearised, the input-referred
  residual is x_q = u − m − e ≈ −β/(2s) + (m − V_bias)/G with loop gain **G = k_q I0 s / g_m**. Stable: one pole,
  τ_m = C_m / (g_m (1 + G)).
- **The leak bound.** The slowest designed leak is g_m = 1/R_MAX (an amplifier at I_MIN), so τ_m ≤ C_MAX·R_MAX/G =
  TAU_MAX/G. Accuracy (small m/G) forces a *fast* tracker. Budget: leak residual ≤ 1 mV RMS with the tracker's quiet
  level RMS 47 mV (resting level 36 mV ⊕ offset 30 mV) needs G ≥ 47; frozen G = 50, so τ_m = 76 ms at C_m = C_MAX.
  A cheaper (smaller) C_m only makes the tracker faster; nothing slower is available on chip at this accuracy.
- **Knob at equilibrium** (anchors only write it): the w-weighted mean of T is −α/2 (nominal gates), so the knob nulls
  the anchor response measured from the tracker's held level. Readout error relative to the ideal shared reference:
  **ε ≈ (β − α)/(2s) − (m − V_bias)/G + dead-band bias**, linear approximation.
- **Gain factors.** k_w, k_q, I0 scale each loop's current; each loop's equilibrium is a zero crossing, so they drop out
  of the static equilibria. They do set τ_m and the knob's rate κ = k_w I0 s/(C_d V_TYP), and so change causal operation:
  how much of an anchor the tracker follows before w closes it off (erosion), and how fast and noisily the knob settles.
- **Knob rate.** κ chosen so one anchor of median evidence (B = 6.9 mV·s, D168 Task E) corrects 25% of the knob's
  error; 90th-percentile anchors 33%. Below 1, so no overshoot in the linear regime.
- **Curvature.** tanh is within 8% of linear for |x| < 0.5/s (39 mV at P1, 10 mV at P2). Anchor excursions are tens of
  mV, so the knob equalises w-weighted tanh, not the mean: a bias that depends on each anchor's shape. Not bounded
  analytically; measured by the replay (P1 vs P2 differ mainly here and in the mirror term).
- **Gate opening at rest** (sensitivity). If a steering pair's offset is negative, its gate is open at V6 = 0. Shared:
  the knob then receives k_w I0 δ/(2(1 − w̄)) continuously; it tunnels whenever |δ| > ~2·DEAD, i.e. one offset beyond
  ~6 mV, and drives the knob to its limit within ~5 s (P1) to ~20 s (P2). Separate: the open knob pair reads e_q − e ≈ 42 mV RMS and drifts
  likewise. P(at least one gate open) = 75% at the 30 mV scale. While both are open during anchors the shared arm alone
  adds δ/(2s)·(T_open/W): SD ≥ 5.5 mV at P1, ≥ 1.4 mV at P2.

## 4. Errors: shared, independent and matched across arms

One fixed draw per component draw, `numpy.random.default_rng([seed, 170, 1]).standard_normal(6)` →
(e, e_q, α, β, g1, g2), scaled by 30 mV (e, e_q, g1, g2: MISMATCH·V_TYP, the connection-offset scale) and MISMATCH
(α, β: one mirror ratio is one part off by 10%). Frozen before any result; none selected.

| error | shared arm | separate arm | role |
|---|---|---|---|
| e (reading pair offset) | one pair, both readings | knob pair | cancels only when shared |
| e_q | — | tracker pair, independent | the error separate paths add |
| α, β (output mirror imbalance) | knob, tracker outputs | the same | after the split: not cancelled |
| g1, g2 (steering/gate offsets) | sensitivity condition only | sensitivity condition only | rest opening; δ during anchors |

## 5. Parameter points (frozen; at most two)

| | P1: least-cost feasible | P2: higher-cost sensitivity |
|---|---|---|
| slope s | pair's own, 12.96 /V | 4× with a preamplifier (shared, before the split), 51.8 /V |
| I0 (k_q = 1) | 50 pA | 12.5 pA (same loop gain and speed as P1) |
| tracker | C_m = 50 pF, g_m = 1/R_MAX, V_bias = 0, G = 50, τ_m = 76 ms | same |
| knob | k_w = 0.25, C_d = 14.9 pF, κ = 36 /(V·s) | same |
| static budget (nominal gates) | shared 5.6 mV RMS; separate 42.8 mV | shared 1.7 mV; separate 42.5 mV |
| resting supply power | 0.19–1.09 nW (range: level shifters, steering reference) | 0.59–1.36 nW (adds the preamplifier) |
| transistors | 35–53 (range: topology not fixed) + knob memory block | 42–64 (adds the preamplifier) and a resistor |
| capacitors | 50 pF + 14.9 pF ≈ 13,000 µm² | same |

P2 isolates slope: the output-stage terms shrink by 4, curvature grows. Both are within the step limits (τ_m = 60
TAU_LOOP; per-step moves ≪ STEP_MOVE) and the rails (tracker level 3σ = 0.14 V). Unknown costs are ranges, not zero:
the knob memory's high-voltage write supply (chip.py's recorded anomaly) is excluded as in every memory.

**Initial states (frozen):** upstream nodes as D168 (`stream_trajectory`'s own random starts); m(0) = 0 V (= V_bias, not
the resting level); V_d(0) = 0, so d(0) = 0, the uncalibrated nominal design. The removal control holds d = 0.

## 6. Unavailable operations (all three must be added for the candidate; none further for the nominal contract)

1. One pair reading the difference of two node voltages (D154: a connection reads one node against a fixed offset).
2. One pair's branch currents steered to two destinations with complementary weights (a Gilbert-type steering quad).
3. For the separate control only: a 1 − w gate (engine gates are clip(V/V_TYP, 0, 1)); granted to it here so that the
   comparison isolates the reading path.
Under the gate-mismatch sensitivity, a closed-at-rest gate margin would be a fourth requirement; it is not tested.

## 7. Noise and evidence (analytic, silicon)

Order node ≈ 0.045 mV per anchor (D168), tracker √(kT/C) = 9 µV at 50 pF, knob write shot noise ≈ 21 µV of V_d per
anchor (0.0001 in d): bound ~0.1 mV, two orders below the screen. Anchors one per ~85 s (5–18 per life). One explorer
(the knob) per credit window. No bit count: the unknowns are the offsets and the balance setting, with no prior or
likelihood established for this candidate.

## 8. Harness rules

The candidate sees v7, its own m and V_d, and V6. Event labels, A/B/W, component arrays and future samples are used
only by the harness (building controls, scoring). Node 7 is propagated causally from the branch currents with the
moving knob (exact exponential step, as `stream_trajectory`); the affine form u + d·der is computed only to measure how
far a moving knob departs from it. Integration 0.5 ms explicit Euler for m and V_d, with d held over each step.

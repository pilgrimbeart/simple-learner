# Where the order calibration's readout error would live (D168 Task B)

Work order: [Task B](../../../WORK_ORDER_2026-11-20_calibration_precision.md#5-task-b--where-the-fixed-error-physically-lives-mandatory-reading-and-small-arithmetic).
Numbers: `arithmetic.json` here, made by `lab/calibration_precision_20261120/b_error_arithmetic.py` (log `../b.log`).
Noise numbers: Task E, `../e/noise_wall.json`.

## The question

D164 and D167 added one readout error `e` to the baseline-relative order signal `r` (in volts), so that the
calibration's observation `A = ∫w·r` became `A + e·W`. That `e` had no physical home. Here the observer chain is
written as it would have to exist in the catalogue's three parts (dynamic node, controlled connection, retained
memory; [PARTS.md §2](../../../../PARTS.md#2-the-catalogue-primitives-dynamical-motifs-and-learning)), and each
stage's error is traced to where it enters `A`, `B` and `W`.

## Where the scales come from

| quantity | value | source |
|---|---|---|
| offset of one controlled connection, input-referred | SD 30 mV = `MISMATCH × V_TYP` | `units.py:40,61`; drawn per element in `mixed_feedback.py:251` (`el[1, j] += MISMATCH * d[1] * self.volt`) |
| gain, slope of a connection | relative SD 10% each | `mixed_feedback.py:250,252` |
| leak, capacitance, bias of a node | relative SD 10% each | `mixed_feedback.py:246` |
| DC gain of one unity stage `k = gain × slope / leak` | relative SD ≈ 17% (√3 × 10%, first order) | derived |
| `k1 − k2·kb` for a feed-forward difference of unit stages | SD ≈ 30% (√9 × 10%) | derived |
| gate (coincidence weight) | `clip(V/V_TYP, 0, 1)`, **no offset or scale draw in the engine** | `mixed_feedback.py:120`; `chip.py:14` builds it as a second differential pair, which physically has one |
| memory write dead band | a write tunnels only above `DEAD = 1%` of the writer's full current, and every write is reduced by that amount | `chip.py:63`, `mixed_feedback.py:137` |
| slowest leak a node can hold | `TAU_MAX` ≈ 3.7–3.9 s (`R_MAX × C_MAX`) | `units.py:84–89` |
| order output's resting level `u_rest` on the 40 reused draws | −77 to +114 mV, median −1.9, RMS 36 mV | `arithmetic.json`, from the saved component draws by the trajectories' own feed-forward equations |
| coincidence node at rest | exactly 0 V on all 40 draws (its gate, B, rests at 0) | `arithmetic.json` |

## The chain, stage by stage

The equilibrium of an online calibration loop is the knob value at which the net write into its memory is zero:
`A + d·B + (additive errors)·W = 0`. Because it is a **zero crossing**, a gain error anywhere in the measurement
path scales every term and drops out; an additive error in the measurement path does not. Errors after the knob,
in the path the knob controls, sit inside the loop and are absorbed. This is the organising rule below.

| stage | catalogue part | its error and scale | where it enters | cancelled later? | shared with a second (quiet) reading? |
|---|---|---|---|---|---|
| 1. order output `u` (node 7) | exists: dynamic node + two tanh connections | the circuit's own offsets: resting level `u_rest`, RMS 36 mV | raw mode: `A` gains `∫w·u_rest` | yes, by any baseline once settled, or by a quiet self-reference (Task D: raw mode 28→38/40) | shared (upstream of both) |
| 2a. baseline, feed-forward low-pass | dynamic node (C ≤ 50 pF, τ ≤ TAU_MAX) + follower connection | follower offset SD 30 mV; DC gain `kb` SD 17% | `r` shifted by `kb·o_b`, plus `(1−kb)·u_rest` | no | shared if the second reading uses the same `r` node |
| 2b. baseline, integral feedback (D128's change-detector form) | `r` node with two input connections; baseline node driven by a connection reading `r` | the baseline's reading of `r` has offset SD 30 mV; the loop then holds `r`'s quiet level at that offset; the two inputs' offsets are inside the loop | `r` shifted by `o_3` | no; finite loop gain of a leaky baseline leaves a further residual, unanchored until parameters are chosen | shared if the same `r` node |
| 3. difference `r = u − b` (feed-forward form only) | dynamic node + two connections (a connection reads one node against its own fixed offset; it cannot read a difference, D154) | two offsets, SD 30 mV each; gain mismatch × `u_rest`: 30% × 36 mV ≈ 10.9 mV RMS | `r` | no | shared if the same `r` node |
| 4. coincidence weight `w` | the connection's gate (exists) | none in the engine; physically the gate pair's offset and scale, **unanchored** | changes the weights, not `e`; a negative gate offset would open `w` at rest (the coincidence node rests at 0 V) and admit quiet-time residual | — | one steering pair gives `w` and `1 − w` from the same tail current, so they stay complementary |
| 4'. `w*w` | **no part**: would need a further node and connection (V6 read and gated by V6), each with its own offset | unanchored | weights | — | — |
| 5. product `w·r` | gated controlled connection reading `r`, gate = coincidence node | **offset SD 30 mV: this is D164/D167's `e`**; gain error (drops out at the zero crossing); tanh nonlinearity shifts the zero crossing when `|r|` is not small beside 1/slope (unquantified) | `A + e·W` | no | only if the quiet reading uses **the same pair**; two gated connections carry independent offsets |
| 6. accumulate | retained memory (the knob), written by stage 5 | dead band: `|x| < atanh(0.01/w)/slope` = 3.0 mV at slope 3.3/V, 1.0 mV at 10/V, 0.8 mV at the pair's native 13/V; wider as `w` falls; biases the zero crossing only by asymmetry of `x`, ≤ the band; write shot noise 0.02 mV equivalent (Task E) | equilibrium | — | — |
| 7. "comparison that sets d" | none needed: the memory's net write crossing zero | — | — | — | — |
| 8. stored knob → gains `1+d`, `1−d` | two memory-gated connections (D145's complementary gates) | offsets and gain errors of the gating | inside the loop: they change which memory voltage is the equilibrium and the size of `B` (speed), not the equilibrium output | absorbed, given enough authority | — |

**The three baseline timescales.** The offsets do not depend on the timescale; what each needs does. For
0.15 s and 1 s, 25 pF and 6 or 40 GΩ are within the chip limits. The slowest, 3.86 s, sits at `TAU_MAX`. It needs
50 pF and about `R_MAX`, which per `units.py:88` is an amplifier biased at `I_MIN` = 1 pA, near leakage. Its
startup (D157) and its share of quiet-time residual (Task D: median 0.2 mV per unit weight over all 1000 s, against
0.01 mV at 0.15 s) are the largest of the three. None of them removes any offset listed here.

`W` and `B` are never accumulated physically in this online form. `W` multiplies `e` only because the offset is
present whenever the product connection is open; `B` matters only through its sign (Task E, observability).

## Combined readout error, `e` (independent offsets, unit stage gains, root-sum-square)

| observer chain | independent additive errors | combined SD |
|---|---|---|
| raw output, product reads `u` directly | product offset | **30 mV** (the D164/D167 probe) |
| integral-feedback baseline + product | baseline's reading of `r`, product | **42 mV** |
| feed-forward baseline + difference node + product | follower, two difference inputs, product; gain mismatch × `u_rest` | **61 mV** (60 mV ⊕ 10.9 mV) |

So D167's 30 mV is the **smallest** chain, and it exists only for raw output, whose resting level is itself an
error unless removed. Any baseline-relative chain built from the catalogue carries at least two independent
offsets. Gain before the product divides later offsets when referred back to `r`, but not the first stage's, and
the rails limit it (the stream trajectories already reach 0.77 V on some node).

Against Task A's requirement (95% of the error-free count at SD ≤ 10 mV on the 80 D165 histories, ≤ 15 mV on the
40 D163 draws), the shortfall is a factor of about 3 for raw output and 3–6 for baseline chains.

## Shared or independent, for a rejection scheme (D149/D151's rule)

- **Shared, cancels in any self-reference:** `u_rest` and every offset upstream of the point where the two readings
  part; the baseline's errors, if both readings use the same `r` node.
- **Independent unless one pair does both readings:** the product connection's offset. Two separately gated
  connections (the only form the catalogue offers) give `e_w − e_q`, SD 42 mV: D149's pattern, the error replaced
  rather than removed (Task D: 23–26 expected adequate draws of 40, against 29–32 for one 30 mV offset).
- **Complementary by construction:** the weights `w` and `1 − w` taken from the two branches of one steering pair.
- **Mirror gains of two outputs:** independent (SD ≈ 14% for their difference), but they drop out at the zero
  crossings of a loop realisation (Task D); in the stationary arithmetic with an explicit ratio they leave
  `e·(k_w − k_q)`, 4–9 mV.

## Unanchored, stated rather than given a number

- the gate pair's offset and scale (the engine draws none);
- the tanh nonlinearity's shift of the zero crossing (depends on a slope not yet chosen);
- finite loop gain of a leaky baseline or quiet tracker;
- the dead band's bias (bounded by the band, sign set by the residual's asymmetry);
- the memory's write supply, the existing explicit exclusion in `chip.py`.

## Noise of nodes that would exist (silicon)

From Task E, per anchor and in volts of `e`: order node ≈ 0.045 mV, baseline node 0.013 mV (√(kT/C) at 25 pF),
knob memory writes ≈ 0.02 mV; combined ≈ 0.05 mV, about 200–300 times below the requirement. A knob is a memory
node, noisy only when written. Noise is not where the precision is lost; the fixed offsets are.

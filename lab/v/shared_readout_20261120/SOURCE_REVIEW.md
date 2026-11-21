# Source check for the shared-readout candidate (D170, 2026-11-20)

Scope (work order §1): verify only the claims the candidate leans on — shared-path cancellation, continuous-time
correction and finite-gain residuals — in the primary sources linked from
[MIXED_FEEDBACK.md, offset rejection](../../../MIXED_FEEDBACK.md#offset-rejection-review-2026-11-20). No new survey.

## Enz & Temes (1996), Proc. IEEE 84(11), DOI 10.1109/5.542410

Downloaded from the link in MIXED_FEEDBACK (31-page scan) to the session scratch folder; pages rendered with
PyMuPDF (`~/.venvs/simple-learner-tools`, run with `python -I`) and **read as page images today: pp. 1585, 1586,
1598, 1599, 1601, 1602.** The PDF and images were not kept. Pages 1597 and 1600 were rendered but not re-read today
(D168's reading of them stands, not re-verified here).

| claim the candidate needs | where | verified |
|---|---|---|
| Autozero cancels an offset by reading **the same amplifier** in a sampling phase (inputs short-circuited, nulling control stored) and a signal phase; the stage is offset-free only "if it is used under the same conditions as during sampling". | II A, p. 1585 (Figs. 1–2) and top of p. 1586 | yes |
| Autozero acts as a high-pass on the error: subtracting a recent sample of the same noise, a zero at dc (eq. 4, \|H0\| ≈ πfT_h); slow errors cancel, wideband noise is aliased (eqs. 1–2, 5). | II B, p. 1586 | yes |
| **Closed-loop offset compensation through an auxiliary (nulling) input** leaves the input-referred residual V_os,res ≈ −V_os/(A2·A3) (eq. 30): the residual falls with loop gain; with charge injection, −V_os/(A2A3) − (g_m2/g_m1)·q_inj/C_h (eq. 31). | IV E, pp. 1598–1599 (Figs. 23, 25) | yes |
| The nulling port's transconductance ratio g_m1/g_m2 is bounded below by the injection residual and above by the control's range against the largest offset to be compensated (eqs. 32–33): a range/precision trade. | p. 1599 | yes |
| **Continuous-time autozero** (feedforward, Fig. 26): a nulling amplifier, itself autozeroed in alternate phases, drives the main amplifier's nulling input; the residual is (α_m V_os-m + α_n V_os-n)/A_n + charge terms (eq. 39): **the corrector's own offset still enters, divided by its gain**. | IV F, p. 1601 | yes |
| Signals at the virtual ground near multiples of the clock are aliased into an apparent offset, so the nulling path should **low-pass filter** the sensed voltage (an OTA loaded by a large capacitor) to track its **mean**; the OTA's linear range must avoid saturation by offset plus parasitic signal. | p. 1602 | yes |

**What transfers and what does not.**
- The candidate is a closed-loop nulling loop in the sense of IV E: the tracker m is a stored control on the
  reading pair's second input, set by negative feedback during quiet time. Eq. 30's lesson transfers in form: the
  stored control's own error (here the tracker's leak and the output path's own mismatch) is divided by loop gain
  only where it is inside the loop. The reading pair's offset is inside both loops (tracker and knob) and cancels;
  the **output stage after the split** (two steering pairs, two output mirrors) is not shared and is not cancelled.
  This is the analogue of eq. 39's second-amplifier term.
- The candidate has no switch, so the charge-injection, kT/C-sampling and clock-aliasing terms of eqs. 24, 31, 39–40
  have no counterpart. Its phases are set by the coincidence voltage instead of a clock; the paper's requirement
  "used under the same conditions as during sampling" becomes: the same pair, at nearly the same common mode, with
  the offset unchanged between quiet and coincident moments.
- p. 1602's low-pass/mean-tracking advice assumes a capacitor large enough for a very low cut-off. On chip our
  slowest leak is TAU_MAX ≈ 3.7 s, which bounds the tracker's loop gain against its speed (CONTRACT §3). No accuracy
  figure in the paper transfers to this candidate.

## Shieh, Patil & Sheu (1987), IEEE JSSC SC-22(2) 277–281

**Not re-read today.** Its only claim relevant to D168 — that switch charge injection is millivolt-scale and depends
on the signal level — concerns switched alternatives, which this candidate does not use. D168's reading stands
unverified by this worker.

## Standard names and closest alternatives (named, not read today)

- Steering one differential pair's two branch currents to two destinations by a second, upper pair per branch is
  the current-steering quad of the **Gilbert cell** (B. Gilbert, IEEE JSSC 1968). **Not read**; named only as the
  standard construction. The quad's own mismatch is the error the candidate introduces (CONTRACT §4).
- Closest alternatives: autozero/CDS and chopper stabilisation (need switches or polarity routing, D154), two
  separately gated reading pairs (D149/D151/D168: independent offsets), a nulling port driven by a second amplifier
  (Enz & Temes IV E–F: the second amplifier's offset enters divided by its gain).
- Mead (1989), *Analog VLSI and Neural Systems*, is the source `chip.py` cites for the blocks; not read today.

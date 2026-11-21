# REPORT — robot action and exploration (D178)

**Lead finding: exploration failure.** In silicon, the substrate we actually intend to use, the historical designed
circuit loses the motor activity that biology's noise had been supplying. That activity was the creature's
exploration. Behind it there is also a sensor-to-motor transfer shortfall. These are development results on 32 reused
seeds (64 lives per arm), not a fresh confirmation.
Status: **the assigned branch is completed up to its stage-3 gate.** That gate failed by measurement, so stages 3–4 were not
triggered. Nothing is incomplete. Work order:
[WORK_ORDER_2026-11-20_robot_action.md](../WORK_ORDER_2026-11-20_robot_action.md). Ledger: [CHECKLIST.md](CHECKLIST.md).
Notebook: [D178](../../discrete/NOTEBOOK.md#d178-robot-action). Started 14:23 GMT; compute and writing done by about 14:50.

## Incomplete items
None. Not triggered, each with its measured evidence: R9, R10, R11 (stage-3 gate condition 3 false) and R12 (no working
behaviour claimed). See CHECKLIST.

## What we learned
1. **Lower noise doesn't fix the shortfall.** Under silicon's noise, no arm meets the job's limits.
   - Informed reference (privileged), net food per 10 s in the fixed final third: +0.05 [−0.09, +0.21].
   - Learning minus frozen: +0.08 [−0.01, +0.18].
   - Learning, silicon minus biology: +0.06 [−0.13, +0.23], which is inconclusive.
2. **Silicon removes the exploration.** On identical inputs, silicon's sensor spikes are mostly real responses: the share
   that follow a pulse rises from a median of 0.15 to 0.95. But motors' own firing falls from about 5/s to 0.2/s. In
   closed loop, stranded lives (no meal at all) rise from 12 to 40 of 64, and all-food intake falls by 0.67 [0.09, 1.28]
   per 10 s.
3. **The knob settings are not the bottleneck.** The best of the eight informed settings on seeds 0–7 did not hold on
   seeds 8–31: −0.05 [−0.22, +0.11] in silicon and +0.04 [−0.28, +0.36] in biology.
4. **An existing knob, the motors' bias, restores encounters but not avoidance.** It works by switching mismatched units
   from silent to fast own firing (15–23/s); no setting gives a slow exploratory rate. At −1.3 nA:
   - stranded lives fall from 32 to 11 of 64;
   - all-food intake rises by 1.15 [0.10, 2.23] per 10 s;
   - food and poison rise by the same amount, so net is +0.005 [−0.23, +0.24];
   - it costs about 1000 extra thruster firings a life.
5. **Why avoidance stays at chance.** A body pulse adds a median of only 0.11 motor spikes. That is 0.33 sensor spikes per
   pulse times 0.36 motor spikes per sensor spike, set against the motors' own firing of about 14/s. The knob, which
   is held correctly, gates only the spikes the sensor causes, so it barely changes which colour gets eaten.
6. **The historical neurons can't be put on the chip.** Converted to 0.3 V typical, they would rest near −1.06 V and swing
   from −2.5 to +1.6 V, outside the ±0.9 V rails. A physical candidate needs a redesigned neuron. That failure is why the
   stage-3 gate is closed.

**Bits.** The unknown is one bit: which colour is poison.
- Tastes arrive at about 0.11–0.14 per second after the creature starts moving.
- When a taste arrives, the larger trace belongs to the eaten colour at 80% (biology) and 83% (silicon) of tastes. Under
  the textbook independence assumption that is about 0.3 bits per taste, an assumption-labelled figure, not summed
  across tastes.
- The informed reference already holds the whole bit and still gains nothing measurable. The loss is in turning
  that bit into action, not in acquiring it.

**Changed belief.** D176's "relay" shortfall turns out to be two problems, and they have to be treated separately:
- exploration, which biology's noise was providing and silicon takes away;
- sensor-caused steering, which is too weak compared with the motors' own activity.

**Next conditional branch (a decision for the user).** First, a neuron and relay contract that fits the chip's rails.
Then compare one sensory stage with a large incremental effect per pulse against the current one, keeping the
exploration source fixed. The prediction is that informed net reward rises if hypothesis 5 holds.

## Evidence index (scripts → raw output)
| claim | script | output |
|---|---|---|
| identity, logging, wiring | [checks.py](checks.py) | [checks.json](../v/robot_action_20261120/checks.json), [checks.log](../v/robot_action_20261120/checks.log) |
| windows | [bench.py](bench.py) | [bench.json](../v/robot_action_20261120/bench.json), [addendum 1](../v/robot_action_20261120/addendum_1_windows.md) |
| stage 1 arms, contrasts, replay | [capture.py](capture.py), [stage1.py](stage1.py), [stage1_resp.py](stage1_resp.py) | [stage1.json](../v/robot_action_20261120/stage1.json), [stage1_resp.json](../v/robot_action_20261120/stage1_resp.json), [ledger/](../v/robot_action_20261120/ledger/) |
| evidence budget | inline, recorded | [evidence_budget.txt](../v/robot_action_20261120/evidence_budget.txt) |
| transfer/omission | [transfer.py](transfer.py), [replay.py](replay.py) | transfer_informed_{silicon,biology}[_bias-motor…].json |
| grid | [grid.py](grid.py), [grid_eval.py](grid_eval.py) | grid_{silicon,biology}.json, grid_eval.json |
| knob family | [motor_bias_bench.py](motor_bias_bench.py), [family_eval.py](family_eval.py) | motor_bias_bench.json, family_eval.json, [addendum 3](../v/robot_action_20261120/addendum_3_knob_family.md) |
| costs | [costs.py](costs.py) | [costs.json](../v/robot_action_20261120/costs.json) |
| frozen protocol | [make_manifest.py](make_manifest.py) | [manifest.json](../v/robot_action_20261120/manifest.json), code_hashes_*.txt, [addendum 2](../v/robot_action_20261120/addendum_2_stage2.md) |

Provenance: revision 5700eaa, with the working tree's uncommitted documents. Engine, body and brain files are unmodified;
their hashes are in manifest.json. Full traces are in `~/nca-scratch-backup/robot_action_20261120/` (out of git), with a
sha256 of each life's trace in the per-life ledgers. Commands are run with `.venv/bin/python` and one maths thread per
worker:
`checks.py`; `capture.py <arm> silicon 0 31`; `bench.py`; `stage1.py`; `stage1_resp.py`; `transfer.py silicon|biology [bias=motor:I]`;
`capture.py informed@F,Q <sub> 0 7`; `grid.py <sub>`; `capture.py informed@… <sub> 8 31`; `grid_eval.py`; `motor_bias_bench.py`;
`capture.py informed|allfood silicon 0 31 bias=motor:-1.3e-9`; `family_eval.py`; `costs.py`.

**Limitations:**
- These are development seeds, reused from D176.
- Only one integration step was run. Halving it was not triggered, and D176 found its reward comparisons were not
  converged in the step.
- The historical contract runs at 1 V and off chip.
- The informed arm is privileged: it is told the answer.
- The windows count association, not cause. Only the omission replay measures cause.
- Four of 256 replays differ in which tick a spike falls in (seed 7, silicon).
- Unmeasured costs: material is counted in graph parts, not transistors, and the memory nodes' write supply is not
  counted.

Logged bug fixes:
- stage1.json's sensor-response contrast came out as NaN; it was recomputed in stage1_resp.json.
- stage1.json's taste rate was wrong, because it treated a life that started moving at tick 0 as never moving; it was
  corrected in evidence_budget.txt.

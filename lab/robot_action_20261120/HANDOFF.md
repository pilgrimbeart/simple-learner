# Handoff to autonomous repair — proposal only (R14, D178)

Based only on completed evidence. Nothing new was run or designed for this page.

**Candidate local shortfall signal: a motor unit's own long silence.** A motor neuron can measure, locally, the time
since its own last spike (a leaky node charged by its spikes, which it already has in its recovery variable). In
silicon, 35 of 64 informed lives had a motor that never fired on its own, and those lives strand
([transfer_informed_silicon.json](../v/robot_action_20261120/transfer_informed_silicon.json)). A unit long silent could
raise its own bias until it fires, the repair that cut stranding from 32 to 11 of 64 when imposed by hand
([family_eval.json](../v/robot_action_20261120/family_eval.json)).

**Counterexample.** Silence does not distinguish *absent input* from *failed response*: a motor in a creature sitting
still facing nothing is silent because nothing arrives, and one with a dead sensor upstream is silent for the same
local reason. Nor does it distinguish *task-useful exploration* from *waste*: the hand repair restored encounters but
raised food and poison alike (net +0.005 [−0.23, +0.24]) and cost about 1000 extra firings a life
([costs.json](../v/robot_action_20261120/costs.json)). And the units do not offer a slow setting: each jumps from silent
to 15–23/s ([motor_bias_bench.json](../v/robot_action_20261120/motor_bias_bench.json)), so a local bias rule would
switch a unit to fast own firing, not tune a rate.

**Prior assumptions.** That some own motor activity is useful in every life (true when the creature starts out of sight of
blocks, as stranded lives do); that the unit's silence timescale is long beside the body's pulse statistics (no body
setpoint may be used, so the timescale must come from the unit's own recovery, measured at 20–100 ms, or a slower
explicit node). **Observation time:** at encounter rates of about 2.5 pulses per second, seconds of silence separate
"nothing seen" from "seeing but not responding" only if the unit also senses its input current, which a motor does not
see apart from its sensors' synapses. **Exploration cost:** firings at about 20 nJ each (minimal/spec.py's guess).
**Neighbours needed:** the motor's own state only for the silence rule; to tell useful from wasted activity, the taste
node's signed pulses (already local to the knobs, not to the motors).

**Verdict.** The silence signal is identifiable for *whether* to explore, not for *whether exploring pays*, and the
existing bias offers only on/off. Whether a taste-gated version (more own activity after food, less after poison) could
tell useful from wasted exploration is unidentified from present evidence. No body signal is proposed. The following
investigation, under its own frozen protocol, would compare fixed tuned, autonomous adjustment and adjustment-removed
controls, then the unchanged rule on a second use; it needs first a neuron whose operating region fits the chip's rails
(the stage-3 gate's failure, D178).

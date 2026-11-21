# HANDOFF — the next local-repair question (R11; a proposal only, nothing run)

**Shortfall found.** One taste writes a memory by an amount set by how open its eligibility trace is. A burst
of sensor pulses (10 in 0.2 s; a block approaching produces bursts like this) opens the trace to about 60%, and
one taste then moves the memory by 0.21–0.99 V. That is two to ten times the whole useful range of 0.3 V
(the readout's gate is fully shut at 0 V and fully open at 0.3 V). In one bench case it reached the
+0.9 V supply rail. Isolated pulses write 0.03–0.13 V, as designed. Nothing in the circuit limits the size of a
single write ([bench_B](../v/catalogue_brain_20261120/bench_B.json), [diag_rail](../v/catalogue_brain_20261120/diag_rail.json)).

**One locally accessible signal.** The memory node's own voltage relative to the readout's two clip points:
P > V_TYP or P < 0. The gate pair that reads P already compares P with these levels (its current stops changing
outside them), so the neighbours needed are P itself, its two writers and its gate pair. No other unit, the body
or the world is involved. The signal is available within one write (~12 ms, the taste node's decay) and costs, at
most, one more differential pair per memory (~2 × 4–8 transistors per P at chip.py's block sizes, plus its bias). This
reuses an existing quantity, so "knobs first" applies: the writer's gain (or threshold) is the existing knob it would
turn.

**Counterexample (why the signal is ambiguous).** P beyond V_TYP is not necessarily wrong: "very sure this colour
is food" saturates the readout too, with identical behaviour. The signal shows that **the store is spending range
the readout cannot use**. It does not show that the stored sign is wrong. Turning the writer down on this signal
could also slow correct acquisition when the trace is weak. And a write that stays inside [0, V_TYP] but has the
wrong sign (a taste credited to the sensor that was not responsible) produces no signal at all.

**Silence versus unprofitable action.** This signal detects *excess internal writing* (saturation), which a
node can see by itself. It is not a detector of silence (no motor events, no tastes), and it is not a detector of
*unprofitable action* (moving towards poison). Unprofitable action can be judged only from taste outcomes over
many encounters, and so needs a slower, outcome-correlated signal that is not designed here.

**Question for the reviewer (one page, proposal only).** Can each memory's writer pair lower its own write
gain when its own memory leaves the readout's range, so that a burst-gated taste writes at most about the
readout range? Must it do so without slowing acquisition from weak (isolated-pulse) traces, and without
removing the evidence of later opposite tastes? Discriminating test (not run): the B train and single-pulse
cases, before and after, with the work order's write gate and no rail excursion, then R5/R6 unchanged.
Alternatives to compare, from the existing catalogue only: (a) a lower fixed writer gain, which is a knob
setting and not a repair, and would weaken isolated-pulse writes 0.03 V → ~0.01 V; (b) the writer's offset
raised, so that only the strongest tastes write; (c) eligibility E clipped by its own sigmoid saturation (a
lower E gain). None of these is authorised by this work order, and no new algorithm, learning rule or
recruitment was run.

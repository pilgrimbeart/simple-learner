# Oscillator starting-state audit — D130

Same four existing component draws, five starts, three timesteps, original noise and50s pulse. This is diagnosis, not fresh reliability evidence.

| Draw | Start | Before pulse | After pulse |
|---|---|---|---|
| 51005 | original | cycle | cycle |
| 51005 | rest | rest | cycle |
| 51005 | near_rest | rest | cycle |
| 51005 | far_positive | cycle | cycle |
| 51005 | far_negative | cycle | cycle |
| 51006 | original | rest | rest |
| 51006 | rest | rest | rest |
| 51006 | near_rest | rest | rest |
| 51006 | far_positive | rest | rest |
| 51006 | far_negative | rest | rest |
| 51011 | original | rest | rest |
| 51011 | rest | rest | rest |
| 51011 | near_rest | rest | rest |
| 51011 | far_positive | rest | rest |
| 51011 | far_negative | rest | rest |
| 51036 | original | rest | rest |
| 51036 | rest | rest | rest |
| 51036 | near_rest | rest | rest |
| 51036 | far_positive | rest | rest |
| 51036 | far_negative | rest | rest |

Window classifications agree across all three timesteps: True. Original-start finest amplitudes reproduced D126 exactly.

Draw51005 supports coexistence: near-rest starts stay quiet until the pulse, then cycle; other starts already cycle. The three previously failing draws remain at rest from every sampled start. This weakens a generic startup-kick repair, but does not prove those draws have no other attractors.

Raw metrics and initial voltages: rows.jsonl. Specification: protocol.json. Provenance: provenance.json. Script: lab/oscillator_basins.py. No noise-free trajectories, tuning or new mechanism. Large traces stay locally at /home/pilgrim/git/simple-learner/lab/v/oscillator_basins/*.npz, with hashes in trace_manifest.json.

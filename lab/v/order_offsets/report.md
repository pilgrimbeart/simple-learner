# Temporal-order parameter diagnosis — D134

All 204 conditions on the six previously failed draws were replayed at the existing finest step. Original metrics reproduce within 1e-12 V. Noise, starting states and stimuli remain paired. This is selected-case diagnosis, not fresh reliability evidence.

| Parameter group restored to nominal | Cases passing / 204 | Original failures rescued / 20 | Previously passing cases harmed / 184 |
|---|---:|---:|---:|
| original | 184 | 0 | 0 |
| trace offsets | 197 | 13 | 0 |
| detector offsets | 190 | 9 | 3 |
| difference offsets | 185 | 4 | 3 |
| connection gains | 192 | 10 | 2 |

Trace thresholds account for the largest isolated rescue without observed harm in this selected set. They do not explain all failures. Other groups rescue and harm different cases, so nominalising the entire circuit or adding these rescue counts would be unjustified. These interventions use knowledge unavailable to the circuit; they are not a manufacturable cure.

Detailed rescue/harm counts by event class: failure_classes.json. Protocol and source hashes: protocol.json and provenance.json. All 1,020 raw rows: rows.jsonl. Reproduction: lab/order_offset_diagnose.py (new output folder required); audit: lab/order_offset_report.py. No engine or body change, no additional topology, no fresh-seed claim.

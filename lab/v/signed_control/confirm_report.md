# Explicit signed gain control — D145



39/40 draws meet every frozen sign, contrast, recovery and rail criterion across all three steps. Wilson95: [0.8711863103652591, 0.9955731684973186]. Refinement passes: True.

Minimum signed raw mean: 0.0164355 V (criterion > .02 V). Null-input/control range: [-0.12136957833808765, 0.11217427686147009] V. Those null errors are reported, not removed.

Core: {'T': 172, 'R': 29, 'C': 13, 'D': 0, 'sources': 20}. Supply power (mean,95% interval): [2.3604927987443073e-08, 2.331766648084302e-08, 2.3900115868792578e-08] W. Gross charge and threshold crossings are separately recorded in confirm_audit.json.



The frozen reliability requirement is NOT met; this remains a partial witness. It does not establish a precision multiplier, zero feedthrough, learned weight or calibrated timing. Matched worlds and fresh component draws are distinct notions; these are fresh component draws of the same bench family.



All raw rows, protocol, source hashes and simulator revision are retained. Large NPZ traces stay local; trace_manifest.json records absolute paths and hashes. Schematic is a block diagram with explicit physical nodes/elements; no SPICE claim.

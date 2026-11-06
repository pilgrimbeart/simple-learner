# Independent re-attack of the stage-2b language and engine: predictions (written before any run, 2026-11-06)

Read before writing: D34, and lab/stage2_lang/lang.py and sim.py as changed (the allowlist `_ALLOWED`, `stage5`, `normalise`,
`canonical`, sim.WLife._honest). Not read: stage2b_guard/dl/repro scripts or logs, lab/sealed/. Seeds 64550-64999.

## 1. The brain channel
- P1.1 No world text compiles that touches the brain object: names, dotted tokens, let/table/each names, numbers like 1e999. 90%.
- P1.2 One indirect route remains: a (told e) expression is evaluated inside the bank's taste call (arms.py's spy, for the
  Recorder arm), so a told expression that draws shifts the world's stream with the brain's calls: bank lives through
  arms.py then differ from universal_v.V's in the same world. Not a channel into the brain, but a life that depends on
  the arm's instrumentation. 60% that I can show lives differ.

## 2. The guard
- P2.1 Every one of my 16 earlier attacks is refused (statically or in the first offending tick) or is honest. 85%.
- P2.2 Accepted, though they do what stage 5 is for, in effect: a see/look/fire swap from 50 s (rewiring); a body frozen
  after the first poison (a life ended); a poison block hidden on contact and put under the mouth 1 s later (a delayed
  taste); swapped verdicts in ticks with a food and a poison meal (taste 0, score swapped); a meal scored bad under a +1
  taste in a tick of three food meals; worth decoupled from taste by amounts (food worth 1e-6) and by COST set mid-life
  (which then applies to the whole life). 75% that at least five of these seven are accepted.
- P2.3 A world raising a Python error (1/0) mid-life is not a Refused but a crash. 70%.

## 3. Description length
- P3.1 My earlier rewrites (renaming, lets reordered, + 0, commuted operands, via a variable, a dead variable) now all
  cost the same as the original. 80%.
- P3.2 New meaning-preserving rewrites still move it: (> a b) against (< b a); (if c a b) against (if (not c) b a);
  (* 2 x) against (+ x x); one (on tick) clause split in two; De Morgan. 80% that at least two move.
- P3.3 The normal form is unsound in at least one case: inlining a variable read from `speed` (or `dist`) past a write
  to vx, vy (or x) that the inliner doesn't see as changing it, so two worlds with different lives get one normal form
  and to_text(normalise(w)) lives differently from w. 65%.

## 4. Identity
- P4.1 Base, story 1's circuit and the bank: 300 of 300 lives identical to creature.Life on seeds 64550-64599. 90%.

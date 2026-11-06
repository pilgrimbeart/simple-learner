# Stage 2c predictions, written before anything runs (2026-11-06)

The coordinator's brief after the checker's second attack (discrete/NOTEBOOK.md, D34's end). Seeds 66600-67999 only, chosen now:

| use | seeds |
|---|---|
| smoke tests while building | 66600-66619 |
| identity, the switch off, against creature.Life | 66620-66669 |
| normal form kept only if lives are identical (40 lives a world) | 66670-66689 |
| instruments: false positives on the hand worlds, the checker's attacks labelled | 66690-66709 |
| the nine and plain at 10 ms, the switch off against on, paired | 66710-66809 |
| halving, before the conversion (switch off), 10 / 5 / 2.5 / 1.25 / 0.625 ms | 66810-66909 / 66910-67009 / 67010-67109 / 67110-67209 / 67210-67309 |
| halving, after the conversion (switch on), the same steps | 67310-67409 / 67410-67509 / 67510-67609 / 67610-67709 / 67710-67809 |
| spare | 67810-67999 |

## Part 1, the interface by construction
- C1.1 With a meal's worth the only thing a world writes about a meal (its taste the worth's sign, its score the worth, COST fixed at birth), every one of the checker's taste and score attacks stops compiling or becomes honest; out-of-range worth (1e-6, 1000) is refused in its first meal; 1/0 and log(-1) are refused, not crashes.
- C1.2 The spy leak closes: a (told e) that draws no longer compiles, and the bank through arms is identical to universal_v.V in such a world's honest version.
## Part 2, instruments
- C2.1 Rewiring by see, look and fire from 50 s is labelled in at least 90% of lives; swap10, alternate and every other hand world but cells in under 2% of lives.
- C2.2 Cells is labelled "placed under the mouth" in most lives (its respawn), as is the checker's delayed poison; the frozen body is labelled in every life where a poison is eaten before about 90 s.
## Part 3, description length
- C3.1 After the fixes the two unsound pairs get different normal forms; most of the checker's 12 moving rewrites still move (by up to ~50 bits): slack stays about +-50 bits.
## Part 4, seconds
- C4.1 The switch off: identity 300 of 300 again.
- C4.2 The switch on at 10 ms moves plain's levels by more than .2 for every arm (exact integration of drag over a tick moves the body about 21% less far than the Euler step), and bank minus base by under .1.
## Part 5, halving
- C5.1 Before: levels keep moving down to 1.25 ms, by about .1 a halving, and 100 pairs can't show two successive halvings within +-.05 (the interval's half-width is about .12): the strict criterion is not met anywhere.
- C5.2 After: the steps' differences are within noise from 10 ms on (point differences under .05), since the body is integrated exactly and only the brain's once-a-tick decision remains; bank minus base settles at 10 or 5 ms.

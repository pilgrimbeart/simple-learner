# Stage 2a: predictions, written before running anything of the language (2026-11-05)

Not edited after the first run. Written after reading `PROGRAMME.md`, `GRAMMAR.md`, `AGENTS.md`, D29-D32, `world.py`, `creature.py`, `lab/table.py`, `lab/bits_bank.py`, `lab/stage1c_arms.py`. No engine exists yet.

## Decisions taken with these (I have no one to ask)

- D1. A world is text in a small S-expression language; that text, once canonical, is the world's data. It is compiled to Python, never hand-written Python, and a validator rejects any symbol outside the written vocabulary.
- D2. Python or numba: settled by measurement (P2 below), default Python, since the brain and `Life.step` are Python already.
- D3. A world's random draws come from a stream of its own (`seed + offset`). The body's stream is never touched by a rule, so an inactive rule can't change a life. The stream offset is left out of the description, since it changes the sample and not the world.
- D4. Corpus for description length: `lab/stage2_lang/corpus.txt`, the vocabulary only (no worlds), frozen by SHA-256 before any world's length is read.
- D5. `told` is `bits_bank.VTold` (the bank's parts, told the colour), as in D31-D32; plus a told pause where a world has a soon-after-a-meal penalty, since D31's digest shows the colour alone misses it (.02 against 1.81).
- D6. Classes, fixed now. `D` = expected evidence in a life at the bank's rate, bits, separating this world's tastes from plain's: n [ rho (1-2e) log2((1-e)/e) + KL(e || e_plain) ], with rho the share of scored tastes on which the rule's food colour isn't the life's majority colour. **A**: no difference on the wires within a life, or a taste that says nothing (e's interval reaches .49 and nothing else differs in a usable way), or a symmetry argument with its check. **B**: D plus eye and taste rate evidence below Wald's 3.82 bits (one pair, 5% each way), at this rate. **Ordinary**: otherwise.
- D7. rho and e come from the bank's scored tastes (`bits_bank.Recorder`), so "at the bank's rate" throughout. Bits a life = n (1 - H(e)).
- D8. Rule-changing worlds (stage 5: delayed, lost or lying taste, mid-life rewiring, meals ending a life) are expressible and marked; the runner refuses them as results.

## Predictions

### The engine
- P1.1 Identity: exact, tick by tick, for base and bank, once two or three copying slips are fixed. The likeliest slip: numba's `BLOCK ** 2` with a compile-time global against an argument.
- P1.2 Reproduction of the nine: exact for at least seven at first attempt. Likeliest to need a trace: patchy (numpy `%`, `norm`, a vector draw against scalars) and digest (the taste is decided from the tick's start, while scoring updates within the tick).
- P1.3 Bonus worlds (coin, allfood, scarce, late_*, nlate_*): exact. `moving` the likeliest to differ, by a unit in the last place: numpy's array `cos` against scalar `cos`.
- P2.1 `GRAMMAR.md`'s "hundreds of thousands" of rule runs a life is too high by an order for most worlds: about 10,000 ticks and 1,000-3,000 pulses, so tens of thousands; only per-block rules reach hundreds of thousands.
- P2.2 Compiled to Python, rules add under 15% to a life for a typical world, up to 2x for per-block rules. So numba's interpreter isn't needed.
- P2.3 A life costs about 0.7-1.5 s of one core for base and the bank. The bank is slower than base by 1.5-2.5x.
- P3 The mutation test catches at least 90% of what's planted, and at least one mutation slips through the first set of checks and shows a check too weak.

### The worlds
- P4.1 The language handles at least 85% of the catalogue in under 30 lines, mostly under 5; fewer than 10% can't be expressed. Those that can't: the clone probe ("what would you do?", not in this catalogue), brain-specific ones (memory wiped, tumour, recruits multiplying), and anything needing marks beyond a table.
- P4.2 The worst handled: cellular-automaton blocks, sorted-blocks goal, "pushed blocks", tag; hard but expressible.
- P4.3 Description lengths, given the vocabulary corpus: plain 0 bits, single-rule worlds 100-300 bits, hardest hand worlds 800-1500 bits.
- P4.4 Planted duplicates: `halfthrust_gain` and `halfthrust_const` are the same lives exactly. `dim25` and `weak` are equal in distribution, not in lives. `mirror` ties plain within its interval and yet differs from plain tick by tick from the first firing, so "first difference" reads early for a world with no learnable difference: an honest weakness of that instrument.

### The labels (at the bank's rate)
- P5.1 Plain, swap10, alternate, pattern, unreliable, digest, patchy, weak, noisy: bits a life within 5% of D31/D32 (52, 49, 48, 49, 15, 11, 33, 32, 37).
- P5.2 A: coin, never, allfood, mirror, costly (L9), rarefeast (no wire carries the amount). Coin's e within .02 of .5.
- P5.3 B: few. I guess 1 to 3 of about 35, the likeliest being a very rare-rule world or a late onset under lies (nlate_pattern_50 is the nearest to it, and I still guess ordinary: its D is about 10 bits after onset).
- P5.4 `every5th` has the same e as `unreliable`, within .03, though its lies are deterministic: e and bits per taste can't tell them apart, which is the point of the pair. `swapmeals6` looks like swap10 in rho within .1.

### The numbers (development, hand-picked)
- P6.1 Base and the bank repeat D31/D32 on fresh seeds: bank swap10 .5, alternate 1.6, pattern 1.5, unreliable .5, patchy .7, weak 1.8, noisy 1.8, plain 2.6; intervals overlapping theirs at about 50 pairs (half-width about .15-.25).
- P6.2 Sigma of a pair's efficiency: median about .7, range .4 to 1.3. So se .1 takes about 50 pairs at the median and up to about 170 at worst; 300 worlds with base, bank-like circuit at about 100 lives a world: about 30,000 lives, at about 6 lives a second on 6 workers: 1-2 hours a circuit.
- P6.3 Doing no harm in coin and allfood: bank minus base within -.1 at 50 pairs. Bank's lower bound in coin may fall a bit below -.1 by noise alone: I guess it holds.
- P6.4 The told pass rule (x > max(.5, .25) with r absent: told only) reaches a pass on about 40% of the worlds with a gap, the bank doing best on sequence rules and not on swaps.
- P6.5 Finer step (5 ms): plain and swap10 within their intervals; digest too. The one I expect to move: `blind` (50 ms against a coarser tick) and `noisy`, if at all.

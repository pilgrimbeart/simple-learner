# Stage 2b predictions, written before each part runs

Seeds, chosen before anything runs (development only, 65000-69999; held-out 70000-79999 and `lab/sealed/` untouched):

| use | seeds |
|---|---|
| part 1(b) attacks, dynamic refusal | 65100-65119 |
| part 1(d) identity against `creature.Life` | 65000-65049 |
| part 1(d) reproduction against the wrappers, exact-lives checks of the normal form | 65050-65069 |
| part 3 judging (base, bank, told, reference) and labels (bank's tastes) | 65200-65259 (60 pairs) |
| part 3 first differences on the wires | 65300-65319 |
| part 4 near-duplicates | 65400-65599 |
| part 5 doing no harm | 65600-65799 (200 pairs) |

Random worlds are numbered from 0; any world number held out by `PROGRAMME.md`'s rule (first byte of SHA-256 of `world:n` divisible by 4) is skipped, never drawn.

## Part 1, before any fix

- P1.1 Removing `bp`/`bpget` changes no life of any world but sag; sag is the only hand world lost.
- P1.2 The static guard alone refuses the checker's unmarked liar, random liar, taste of 0, taste of .5, both `bp` worlds; the score-against-taste world needs the dynamic check (its text writes only `bad`), and is refused in its first life with a meal.
- P1.3 "Meal dropped, block uneaten", "colours swapped (truthful)", "world fires a thruster" and "taste from the score stage" stay accepted: none sends a taste that disagrees with its scored meal.
- P1.4 The hand-written digest is caught by the dynamic check in a few per cent of lives (two meals in one tick within a second of the last); rewritten at the meal stage it is honest by construction and differs from the wrapper only in those lives.
- P1.5 Every other world of `worlds.py` runs 20 lives each with no dynamic refusal.
- P1.6 After normalising: never, swap every 1000 s, + 0, via a variable and lets reordered all reach their plain or swap10 lengths exactly; operands commuted too. halfthrust const against gain still differ (different links, the same physics): that stays, and is the reason near-duplicates go by lives.
- P1.7 Identity and reproduction stay exact: 300 of 300 lives against `creature.Life`, every row of the wrapper reproduction, since no fix touches a world that acts honestly.

Added seeds (before they run): cells traced 65070-65079 x 2.

## Part 2, before the reference runs on any world (frozen 07:26; `lab/v/stage2b_reference.sha256`)

- P2.1 The reference is within noise of the bank or above it in the sequence and swap worlds (alternate, pattern, swap-like random worlds), and surely below the bank where lies are dense (unreliable-like), as D32 found for this setting (-.33 there).
- P2.2 In worlds with a gap whose rule isn't about which colour is food (body, eyes, mouth, place), r is within noise of x: the reference is the bank with another selector, so it can't do better than the bank there.

## Part 3, before any random world is lived (generator frozen 07:29, `lab/v/stage2b_gen.sha256`; drawn once, as text, to see each compiles)

- P3.1 About 30-45% of random worlds have something to judge (a gap); most of the rest are body, eye and mouth changes that hurt base and told alike, or L9 constants.
- P3.2 Of worlds with a gap, the reference surely closes more than .25 in under a third: those whose rule its family holds (swap, alternate, keylock-like, gated by a time course it can track).
- P3.3 Labels: about 15% A (nothing learnable), 5-10% B, the rest ordinary; "ordinary" is again a poor guide to a usable gap.
- P3.4 No random world is refused by the engine (the generator has no stage-5 construct).
- P3.5 Cells: the collapse is the world's respawn rule putting an eaten block back under the mouth, so a creature moving forward eats it every tick; the bank keeps moving onto a poison cell. With the respawn kept clear of the creature the bank returns to the ordinary range.

## Part 4

- P4.1 Rewritten pairs: lives identical where no draw moved (halfthrust); equal in distribution otherwise, with bits a life within noise of 0 and p roughly uniform.
- P4.2 Nudged constants: swap10/swap11 and DRAG x2/x2.1 not told apart in 200 pairs (bits a life below .02, so hundreds of lives); unreliable .2/.22 likewise; dim .25/.30 likewise.
- P4.3 Few ticks: indistinguishable in outcomes, though the wires differ from about the moment of the change in every life where a meal fell in it.
- P4.4 Distinct controls separate surely (plain/swap10 by several bits a life).

## Part 5

- P5.1 Sigma of a pair: median .45-.6 for bank on random worlds, a long tail where meals are few; se .1 in efficiency needs a median 25-40 pairs; in x a median 60-150 pairs, far more where the gap is small.
- P5.2 Doing no harm at 200 pairs: shown (lower bound above -.1) for allfood, never, costly and rarefeast; coin and mirror borderline, mirror the likeliest to fail, as in D33.

# The growing network (the user, 2026-11-12; `lab/grownet.py`; PROGRAMME.md, the current stage)

Blocks born beneath contradictions, joining any two co-active units (senses or blocks), readouts on every unit, use flowing back from
right guesses, unused blocks fading (with their dependants), duplicates removed. Arms: tree (D40), net, nonet (net without fading or
duplicate removal). Smoke (3 pairs, P 64, seq rungs 5, 11, 17; last third's gain summed): tree 56, 148, -28; net 73, 115, 75; nonet
75, 142, 35. The tree fills its material at 17 (32 of 32 nodes); net keeps under it (28 to 30).

R1. (teach.py 20 tree,net,nonet seq 16,64 5,11,17; seeds 84000+) net ties the tree (interval of the difference includes 0) at 5 and 11,
    P 64. 55%.
R2. At 17, and at every rung with P 16, net surely above the tree (the tree runs out of material; fading recycles). 45%.
R3. net above nonet at P 16 (where material is scarce, recycling matters), not at P 64. 50%.
R4. net's block count rises with the rung (5 < 11 < 17), and stays below the material at P 64. 65%.
**Scored R1-R4** (`lab/v/grownet_seq.log`; teach.py prints unpaired intervals): R1 right: ties at 5 (.57 both, P 64) and at 11 net .84
[.77, .92] against .73 [.65, .81]. R2 wrong at P 16: all three arms the same at every rung (material full in all: 6 blocks a stream, the
tree's 8 nodes); at 17, P 64, net .62 [.55, .69], solved, against .50 [.42, .58], not solved; unpaired, so not yet sure. R3 void: in 100
to 300 s lives a block can hardly fade (FADE 200 s: 0 to 3 faded), so net and nonet differ only by the duplicates removed (about 20 at P
64, whose material went to new blocks: 103 born against 60). R4 right at P 64: blocks 8, 27, 30 (material 30 a stream); at P 16 full.
So far the growing network matches the tree and, with duplicates removed, perhaps beats it on the longest word; pruning isn't tested yet.

# Stage 3 first: the world changes mid-life (`lab/grownet_switch.py`), where fading should matter
seq 11 with a second hidden word replacing the first at a moment drawn uniformly in 500 to 700 s; 1500 s lives (last third after the
change), P 32 and 64, 10 pairs, seeds 85000+; paired against the tree; the unchanged word as control.
R5. Changed world, P 32: net surely above nonet and the tree (their material holds the old word; net's old blocks fade). 55%.
R6. Unchanged world: net ties nonet and the tree at both P. 60%.
Smoke (one life, changed, P 32): tree -86, net -37 (10 faded, 40 duplicates removed), nonet -90.
**Scored R5-R6** (`lab/v/grownet_switch.log`, paired): R5 wrong at P 32, where none learns either word (14 blocks a stream are too few
for 11 letters: tree -.29, net -.25, nonet -.43, all near the starting brain's -2.05 only by the default); but at P 64 the clearest result
of the stage: after the change net +1.15, the tree -.46 and nonet -.44: net surely above both by +1.61 [+1.18, +2.03] and +1.60 [+1.18,
+1.98], recovering nearly all it had with the word unchanged (+1.34). R6 partly: unchanged, net ties nonet at both P and the tree at 64,
but is surely above the tree at 32 (+.44 [+.16, +.77]).
R7. Which part does it, fading or removing duplicates? (changed world, P 64, fresh seeds 86000+, 10 pairs; arms net, net without
    fading, net without duplicate removal, tree.) net surely above the tree again (confirming R5 at P 64). 75%. Without fading surely
    below net; without duplicate removal not surely. 45%.
**Scored R7** (`lab/v/grownet_switch_ablate.log`, fresh seeds 86000+): first half right: net surely above the tree again, +1.36 [+.94,
+1.77] (confirming R5 at P 64 on fresh seeds). Second half the wrong way round: without fading only -.24 [-.02, +.49] (not sure);
without duplicate removal surely below, -.94 [+.41, +1.42]. Removing duplicates is what frees the material: births beneath contradiction
keep making blocks already there (140 removed a life, against 35 faded), and without removal they fill the material, so nothing is left
to learn the new word with. Fading alone, at 200 s, is too slow to keep up.

# Stage 2, the blood supply (netE<r>: no explicit fading or duplicate removal; blocks firing together share the pool by their use)
Smoke only (2 pairs, changed world, P 64, last third summed): net 417; supply 1, 3, 10 a second: 202, 212, 212 (3 and 10 identical: the
pool never runs short, so what acts is the split by use, a zero-sum competition among blocks firing together). Newborn's store H0 5: 900
births, 250 to 300 starved; H0 20: 26 and -58; H0 60: -224, -359 (too little turnover, material full, as without removal). So the
competition trades turnover against keeping: a store small enough to recycle copies quickly also kills newborns before they prove
themselves. No run yet; not a result.
Then: a newborn inherits its weaker parent's use (no new number), so the young are protected by their parents' standing; a copy, never
the one that speaks (the older twin wins ties), loses its inheritance and starves.
R8. (changed world, P 64, 10 pairs, seeds 85000+, netE3 with inheritance against net) ties net (interval of the difference includes 0),
    and surely above nonet's -.44. 40%.
**Scored R8** (`lab/v/grownet_supply.log`, paired with the earlier run's lives on the same seeds): right. With inheritance, the supply
alone (no written fading or copy removal) +1.19 against net's +1.15 (-.04 [-.35, +.28]: tie), above nonet by +1.63 [+1.36, +1.95] and
the tree by +1.65 [+1.33, +1.97]. About 450 births and 110 starved a life (net: 145 copies removed, 36 faded).
R9. Confirmation on fresh seeds (87000+, 10 pairs, P 64, both worlds; circuit, tree, net, netE3): netE3 ties net in both worlds and is
    surely above the tree in the changed one. 60%.
**Scored R9** (`lab/v/grownet_supply_confirm.log`, fresh seeds 87000+): partly. Changed world: the supply version ties net (+.97 against
+.80; -.16 [-.43, +.09]) and is surely above the tree, +1.77 [+1.53, +2.02]. Unchanged world: surely below net, -.35 [-.02 to -.65], and
the tree, -.38 [-.62, -.12]. Competition keeps recycling in a world that doesn't change, at a cost. Cause to be traced (lab/grownet_why.py).
**Cause** (`lab/v/grownet_why.log`, 4 lives, pattern of 11, unchanged): with the supply, the blocks that speak late in life look back
less far (median 4 colours against 5 to 6), and are wrong more often (e.g. 170 against 136). A block that looks far back fires only with
its shorter ancestors, which always fire with it and hold more use (every descendant's success is passed down to them), so in the shared
split the specialist loses to its own parents and starves. Competition pitted a block against the blocks it is built from.
Fix (no new number): a block with dependants alive is fed by them (support flows back from users): it neither draws nor pays; the rest
compete by their own record of being right when they spoke, not by credit passed down. A copy has no dependants and no record, so it still
starves.
R10. (seeds 85000+, both worlds, circuit, net, netE3) netE3 ties net in both worlds. 50%.
**Scored R10** (`lab/v/grownet_supply2.log`): wrong, and worse: netE3 below net by .64 (unchanged) and 1.05 (changed), both sure.
Cause (`lab/v/grownet_why2.log`, a life): turnover collapsed (50 born, 20 starved, against net's 138 and 87); material full, half the
blocks exempt as parents, and a leaf firing with only its exempt parents gets the whole share and never loses; only resting burns it.
The deeper fault, in both versions: the pool never runs short (supply 1, 3, 10 a second gave the same lives), so the "competition" is
only a zero-sum split of whatever the firing blocks need. The user's idea is a supply that really limits. Next: the supply at .3 and 1 a
second (fewer than the blocks firing each moment need), so a moment's crowd truly shares too little.
R11. (seeds 85000+, both worlds) with a supply that runs short, netE ties net in at least one world. 35%.
**Scored R11** (`lab/v/grownet_supply3.log`): wrong. A supply that runs short helps (.3 a second better than 1 in both worlds: +1.06 and
+.67 against +.70 and +.17), but still below net (-.28 [.00, .52] unchanged, not sure; -.48 [.12, .95] changed, sure). The scarcer the
better, so far.
R12. (one more step down: .1 and .03 a second; same seeds) the scarcest ties net in both worlds. 30%. If not, the supply is parked.
**Scored R12** (`lab/v/grownet_supply4.log`): wrong. Supply .1 and .03 a second: +.98 and +.74 unchanged, +.41 and +.50 changed; best near
.3, all surely below net when the pattern changes. Parked: as built (parents fed by their dependants, the rest sharing by their own
record), competition for a supply does not yet replace removing copies. The first version (all firing blocks sharing by use, newborns
inheriting) came closest: tied when the pattern changes on two seed sets, but cost .35 when it doesn't, by starving specialists beside
their parents.

# Stage 4: does the network's size follow what there is to learn? (`lab/grownet_scale.py 10 256`, seeds 88000+, 1500 s lives)
Patterns of 2, 3, 5, 7, 11, 13, 17 colours, material plentiful (128 a stream). An ideal learner needs one context for each place in the
pattern, each as long as the shortest look-back telling every place apart (about log2 n plus a little): so roughly n log n units.
R13. The blocks alive at the end rise with the pattern's length, roughly in proportion to n log n, and stay well below the material
     (under 100 of 128) at 17. 50%.
R14. Its share of the gap closed (from the starting brain to the told) stays above .5 up to 11, and falls by 17. 55%.
**Scored R13-R14** (`lab/v/grownet_scale.log`): R13 mostly right: blocks alive rise with the pattern, 17, 20, 28, 40, 44, 43, 48 for 2 to 17
colours, far below the material (128 a stream); but closer to a fixed 15 plus about 2 a colour than to n log n. R14 half: share of the gap
closed .91, .95, .89, .88, .88, .82, .81: above .5 everywhere, and not falling away at 17 (with P 64 it was .62): given more material,
the network learns the longest pattern well, and uses only what it needs.
R15. (pattern of 17, fresh seeds 89000+, material P 16, 32, 64, 128, 256, 512) share closed rises with material and levels off; blocks
     used level off near 50 however much more is given. 60%.
**Scored R15** (`lab/v/grownet_material_*.log`, fresh seeds 89000+, pattern 17 steps long): right. Share of the gap closed with material 16,
32, 64, 128, 256, 512: .32, .31, .60, .86, .85, .85; blocks used 6, 14, 30 (all there was), then 45, 49, 49. It rises with material until
it has what it needs (about 50 blocks), then stops growing and stops improving; 256 and 512 gave identical lives (the limit never touched).

# The economy (the user: competition defined by the graph; Baum 1999's conserved credit, van Ooyen & Willshaw 1999's trophic support)
A right guess earns 1; the block keeps half and pays the rest to the two units it is made of, which do the same (nothing minted along a
chain). Firing costs .05, existing .005 a second; a parent funds its newborn (1) from its savings, so only blocks that have earned can
reproduce (the senses are paid by the world); a block in debt is recycled with its dependants. No written fading, copy removal or supply.
A copy never speaks (its older twin does), so it earns nothing and dies; a specialist pays its parents rather than competing with them.
Smoke (2 pairs, P 64, last third summed): without rent, material filled (10 starved a life): unchanged 280, changed -306 (net 456, 417);
with rent: 378 and 403.
R16. (seeds 85000+, 10 pairs, both worlds; circuit, net, neteco) neteco ties net in both worlds. 45%.
**Scored R16** (`lab/v/grownet_economy.log`): wrong. neteco below net when the pattern is unchanged, -.54 [+.23, +.84] sure; changed -.28
[-.04, +.61], not sure. Cause (`lab/v/grownet_why3.log`): fewer blocks alive (20 against 30), look-back shorter, more wrong guesses. A
short-look-back block fires at nearly every step, so it pays the firing cost constantly, while its income comes only as shares from
descendants; it goes into debt and its recycling takes its good specialists with it. Charging for activity starved the general blocks
everything rests on. Smoke (`lab/v/grownet_economy_smoke.log`, 2 pairs): no firing cost, keep half: 474 and 404 (net 456, 417); a firing
cost with keep a fifth: -139, 69; no firing cost, keep a fifth: 271, 148. The firing cost is dropped (FIRE_COST 0): rent alone.
R17. (seeds 85000+, 10 pairs, both worlds; neteco with rent only) ties net in both worlds. 55%.
**Scored R17** (`lab/v/grownet_economy2.log`): nearly. Changed: neteco +1.02 against net +1.15, -.13 [-.23, +.55], a tie. Unchanged: +1.13
against +1.34, -.21 [+.01, +.40], just surely below. The economy, with rent alone, does nearly all the clearing out the written rules did.
R18. Confirmation on fresh seeds (90000+, 10 pairs, both worlds; circuit, tree, net, neteco): neteco surely above the tree in the
     changed world, and within .25 of net in both. 55%.
**Scored R18** (`lab/v/grownet_economy_confirm.log`, fresh seeds 90000+): partly. Changed world: neteco +.91, net +.89 (tie, -.02
[-.42, +.40]), the tree -.38: neteco surely above the tree, +1.29 [+.92, +1.59]. Unchanged: neteco +1.18, net +1.50, the tree +1.27: .33
below net (not sure, [-.13, +.79]), tied with the tree (-.09). So on two seed sets the economy matches the written rules when the world
changes and costs about .2 to .3 when it doesn't.

# Stage 5, first step: one stream we didn't choose (arms net1, eco1: every taste, its symbol the colour eaten and whether it was good)
The two streams so far were our choice, and one (the food colour at each good meal) moves exactly as the pattern lesson does: a hint.
Smoke (2 pairs, P 64, last third summed): pattern 5 steps: tree 50, net 45, net1 19, eco1 24; pattern 11: 79, 103, -17, 26; food by the
last 2 colours eaten (combo 2): 88, 123, 89, 86; last 3: 48, 137, 99, 98. One stream does the combination lessons well and the pattern
lessons badly: there a bad meal doesn't move the pattern on, so bad tastes break up the run of colours a block must recognise.
R19. (teach.py 10 tree,net,net1,eco1, seq 5,11 and combo 2,3, P 64) net1 and eco1 surely below net on the pattern lessons, tied with it
     on the combination lessons. 60%.
**Scored R19** (`lab/v/grownet_one_seq.log`, `grownet_one_combo.log`, 10 pairs, unpaired): right. Pattern lessons: one stream .38 and
.37 against net's .56 (5 steps), .50 and .46 against .77 (11 steps), intervals apart. Combination lessons: tied (.52 to .64 against .64 at
2; .73 and .64 against .79 at 3). The stream we chose was doing real work on the pattern lessons.

# Stage 5, second step: separate sense lines with clocks (Net2; arms net2, eco2; bench lab/grownet_bench.py)
Four sense lines (good, bad, ate red, ate blue); a block keeps time by a clock (every taste, or one line's firings), its output held
between ticks; a block made on a sense draws its clock at random, one made on a block keeps its clock. Smoke (2 pairs): worse than one
stream everywhere (pattern 5: -20; 11: -13; combination 3: 5). Bench (no body, the creature eating what the net says): the two-stream net
right 98% of the time on a pattern 5 steps long, Net2 about 70%. Fixes tried on the bench: ties among senses broken at random (no change);
the surest unit speaks rather than the longest, and growth beneath the speaker (84%, flat from 2000 to 8000 tastes; 11 steps: 70%); a
stronger prior against newcomers (no change). Cause, as far as traced: only a fifth of new roots draw the useful clock (good meals), the
rest grow lineages on clocks that carry nothing, and these lineages, being the speakers, are where growth happens; at the end of a bench
run only 3 of 22 blocks kept time by good meals (1850 born, 418 copies removed). Not run at scale; parked. The question it raises: how can
a network find which clock matters, by local rules? (QUESTIONS.md.)
Further bench work (seeds 1 to 3, 4000 tastes, last quarter right, patterns 5 and 11 steps; the two-stream net .98-.99 and .91-.94):
clocks drawn by their own record of foretelling (CLOCKS="earned") instead of evenly: no change (.71-.84, .65-.72). With the good-meal
clock forced on every root, still .84: so the clock was not the limit. Traced: two senses fire at each taste (good, and the colour eaten),
but a block could join only units at different ticks, and the sense "good" (right 80% of the time on its own) spoke and was grown beneath
almost always, so every block's newest part was "good", never the colour just eaten. Fixes: a block may join two units at the same tick
(a coincidence), and growth goes beneath the most specific contradicted unit while the surest speaks: .70-.89 and .66-.73. Better, not
there. Parked here, with the bench (lab/grownet_bench.py) as the place to continue.

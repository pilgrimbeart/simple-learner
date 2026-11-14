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

# A stream for every sense line (arms net5, eco5; the user agreed, 2026-11-12): streams ticking at every taste, good taste, bad taste,
red eaten, blue eaten, each recording the same four symbols; the gate chooses among them by their record. None is ours.
Smoke (2 pairs, last third summed; net = our two streams at P 64): the gate picks the good-meal stream on the pattern lessons and the
every-taste stream on the combination lesson, by itself. Pattern 5: net 45, net5 34 (P 64) and 37 (P 160), eco5 59; pattern 11: 103,
14, 59, -4; combination 3: 137, 61, 105, 87. Below our streams with the same material each (P 160 is 32 a stream, as net's P 64): our
good-meal stream also wrote the food colour learned from a bad taste (a bad red means blue is food) into the current place of the
pattern, a second hint; net5's good-meal stream sees only good meals.
R20. (teach.py 10 net,net5,eco5, seq 5,11 and combo 2,3, P 64 and 160) the gate picks the good-meal stream in most pattern lives and the
     every-taste stream in most combination lives. 75%. net5 at P 160 within .15 of net at P 64 on every rung. 35%.
**Scored R20** (`lab/v/grownet_five_seq.log`, `grownet_five_combo.log`, 10 pairs, unpaired): right. The gate picks the good-meal stream
on the pattern lessons and the every-taste stream on the combination lessons. With the same material a stream (P 160, against our two
streams at P 64): pattern 5 steps .56 against .56, 11 steps .76 against .77, combination 2 .49 against .64 (intervals wide and
overlapping), combination 3 .70 against .79. At P 64 (13 a stream) it falls short on 11 steps (.49). The economy version a little lower
(.52, .63, .48, .71). So the network finds the stream that matters among five, at the price of material for all five; our stream's
second hint (bad tastes written into the pattern's place) mattered little.

# Plan B1: no symmetry told (arms net5c; PROGRAMME.md, the plan)
Each unit's readout is a table of what each eye led to (good or bad), not the food colour; a taste teaches only about the eye eaten.
First smoke: the network never steered (the gate scored a stream only on tastes where its choice was eaten, and the creature always ate
the default's choice, so a stream that disagreed could never prove itself): the explore-or-exploit problem the told symmetry had hidden.
Who steers is now chosen by sampling each source's record when followed (Thompson sampling: the brain's own noise). Smoke (2 pairs, P 160,
last third summed; net5 alongside): plain 35 (36), pattern 5: 10 (37), pattern 11: 95 (59), combination 3: 113 (105).
R21. (teach.py 10 net5,net5c, seq 1,5,11 and combo 2,3, P 160) net5c within .15 of net5 on every rung, the plain world included. 45%.
**Scored R21** (`lab/v/grownet_b1_*.log`, 10 pairs, P 160): mostly right. Without the symmetry told: plain world -.10 [-.19, -.03] (the
cost of trying the other eye now and then), pattern 5 steps .45 against .56, 11 steps .65 against .76 (still solved), combination 2 .22
against .49 (the one rung beyond .15), combination 3 .57 against .70. A cost of .1 to .27 everywhere. In bits: told the symmetry, every
taste says something about both eyes; untold, only about the eye eaten, so it needs about twice the tastes, and must spend some on
trying. Kept as the honest baseline for B2 and B3? Not yet: parked as a measured price, with the question whether a network can learn
the symmetry itself (that the two eyes' outcomes are opposite) and so earn back the evidence.

# B1 continued: can each unit learn the symmetry? (arm net5s)
Each unit compares, on its own record, the evidence that the two eyes are opposites (one chance: eye 0 good is the same news as eye 1
bad) against independent (a chance each): MacKay's Occam factor, uniform priors, even odds; it pools when opposites wins. In the
all-food world opposites should lose. Smoke (2 pairs, P 160, last third summed; net5 told, net5c untold): plain 36, 35, 35; all-food
52, 52, 52; pattern 11: 59, 95, 54; combination 2: 60, 124, 124 (2 pairs: noise).
R22. (teach.py 10 net5,net5c,net5s; seq 1,5,11; combo 2,3; P 160) net5s above net5c on the pattern and combination rungs on average,
     earning back at least half the price of not being told. 45%.
**Scored R22** (`lab/v/grownet_sym_*.log`): wrong. Learned symmetry no better than none (pattern 5: .42 against .45; 11: .61 against .65;
combination 2: .42 against .22, wide; 3: .61 against .57). Before guessing why, which part of B1 costs: the readouts (no symmetry), or
the change to who steers (sampling instead of the Occam gate) and to the default (judged only on its own eye)? Arm net5t: B1's machinery
with the symmetry always pooled (told): net5 - net5t is the cost of the steering change, net5t - net5c the cost of the readouts.
**Ablation** (`lab/v/grownet_t_*.log`, net5t: B1's steering, symmetry told): pattern 5 .44, 11 .60, combination 2 .54, 3 .67, plain
-.10. So on the pattern lessons the whole price of B1 is the change of steering (sampling who steers, the default judged on its own eye),
not the readouts (net5c .45, .65); on the combination lessons the told readouts do help (.54 against .22, .67 against .57; intervals
wide). My "halved evidence" explanation was wrong for the pattern lessons. Next: score every source on each taste where its choice was
the eye eaten, not only the one steering, so sources earn records without steering (arm net5c2).
Smoke (3 pairs, last third summed; net5, net5c, net5c2, net5t2): plain 62, 64, 88, 88; pattern 5: 55, 31, 50, 35; 11: 105, 164, 105, 100.
R23. (teach.py 10 net5c2,net5t2, same rungs) net5c2 within .1 of net5 (told, Occam gate) on the pattern rungs and the plain world. 45%.
**Scored R23** (`lab/v/grownet_c2_*.log`): partly. With every agreeing source scored, told and untold readouts are now equal (pattern 5
.52 and .53, 11 .64 and .66, combination 2 .31 and .33, 3 .61 and .55): the symmetry in the readouts no longer matters. Against net5
(told, Occam gate): pattern 5 -.04, 11 -.12, combination 2 -.18 and 3 -.09 (wide), plain -.10. The rest is the price of exploring: a
brain not told that the other colour is food when this one is poison must sometimes try the other to find out, and in the plain world
that costs .1. Told, it never needs to. B1 closed: the told symmetry was worth .05 to .15, all as exploring it spared.
R24. (paired, fresh seeds 91000+, pattern 17 steps long, 1500 s, P 64; lab/grownet_switch.py with WORLDS=unchanged N=17) net surely above
     the tree (D59's unpaired .62 against .50). 60%.
**Scored R24** (`lab/v/grownet_17_paired.log`, fresh seeds 91000+, paired, 1500 s, P 64): wrong. Pattern 17 steps long, unchanged: net
+.40, the tree +.40, difference .00 [-.35, +.38]. D59's unpaired "solved where the tree is not" (.62 against .50, 300 s lives) does not
hold up paired on fresh seeds: the two tie. (The run also did the changed world, through a bug in WORLDS's matching, "changed" being in
"unchanged", now fixed: there net +.37 [-.02, +.76] above the tree, not sure.)

# Plan B2, first step: no vouching (arm net5v): learn from every taste, what was eaten taken as the eye that pulsed last; no hand rule
for which tastes the eyes vouch for (followed eye pulsed within the hold, the other not since).
R25. (teach.py 10 net5,net5v; seq 1,5,11; combo 2,3; P 160) net5v within .15 of net5 on every rung. 40%.
**Scored R25** (`lab/v/grownet_v_*.log`, after a misrouted first run, `_misrouted`, void): right. Learning from every taste, without the
hand rule for which tastes to trust: pattern 5 .58 (net5 .56), 11 .70 (.76), combination 2 .52 (.49), 3 .74 (.70); plain -.10 [-.24,
.00] (net5 .00). The vouching rule is not needed by the growing network, at a small cost in the plain world.
R26. Both removed at once (untold symmetry with every agreeing source scored, and no vouching; arm net5cv): within .15 of net5 on every
     rung. 45%.
**Scored R26** (`lab/v/grownet_cv_*.log`): partly. Lessons within .15 of net5 (pattern 5 .50, 11 .66, combination 2 .38, 3 .69), but the
plain world surely costs: -.37 [-.65, -.11]. Cause (three plain lives, traced): without vouching, a taste of the other colour eaten by
accident counts against the sources that chose the eye that pulsed last, so the records of all sources pick up false poisons, and
sampling who steers then sometimes follows a wrong eye late in life (2 of 21 tastes in one life). Each removal alone costs .1 in the
plain world; together the false evidence feeds the exploring.

# Confirming the stream-per-sense result paired, on fresh seeds (lab/grownet_pair.py, seeds 92000+, 10 pairs)
R27. net5 at P 160 against net (our two streams) at P 64: the paired difference's interval includes 0 on pattern 5 and 11 and on
     combination 2 and 3. 55%.
**Scored R27** (`lab/v/grownet_pair_*.log`, paired, fresh seeds 92000+): right. A stream for every sense (P 160) against our two (P 64):
pattern 5 -.05 [-.12, +.01], 11 -.10 [-.19, +.04], combination 2 -.01 [-.25, +.29], 3 -.04 [-.22, +.16]. Confirmed: none surely worse.

# The user's local competition: siblings share their parent's pool (arms netL<r>; no written fading or copy removal)
Every unit holds a pool refilled at r a second; blocks built on it (their v) that fire together share it by their own record; a block
never competes with its parents nor with blocks under another parent; resting burns; the starved are recycled with their dependants;
newborns inherit the weaker parent's record. Smoke (2 pairs, P 64, last third summed; net 456 unchanged, 417 changed): r .3: 289, 190;
r 1: 493, 355; r 3: 422, 345.
R28. (seeds 85000+, 10 pairs, both worlds) netL1 ties net in the unchanged world (unlike the earlier supply, which cost .35 there), and
     is within .3 of it in the changed world. 45%.
**Scored R28** (`lab/v/grownet_local.log`): half. Changed world: netL1 +1.09 against net +1.15 (-.06 [-.26, +.38]): a tie; unchanged
+1.13 against +1.34, -.21 [+.02, +.43]: just surely below (netL3 alike). The same as the economy on these seeds (+1.02, +1.13).
R29. (fresh seeds 90000+, where the economy was confirmed) netL1 ties net in the changed world and is within .3 in the unchanged. 55%.
**Scored R29** (`lab/v/grownet_local_confirm.log`, fresh seeds 90000+): partly. Changed: netL1 +1.14 against net +.89 (+.25 [-.04, +.53]
in its favour, not sure). Unchanged: +1.06 against +1.50, -.45 [-.72, -.18]: sure, and more than the economy's -.33 here.
Both generic clearers (economy, local competition) keep paying a turnover cost when nothing changes. Idea (the user's earlier thought:
go back to organising when rewards stop): let the pressure to recycle follow surprise. Each block's resting burn scaled by its stream's
recent rate of wrong guesses (twice it, so chance is the full burn): low when the world is learned, high after a change. Arm netLs1.
R30. (seeds 85000+ and 90000+, both worlds) netLs1 within .15 of net in the unchanged world on both seed sets, and still ties it in the
     changed. 40%.
**Scored R30** (`lab/v/grownet_surprise*.log`): wrong. Unchanged: -.41 [+.18, +.61] below net on seeds 85000 (worse than netL1's -.21),
-.26 [-.01, +.53] on 90000 (better than -.45); changed: ties. No clear gain: the turnover cost isn't the resting burn. Tracing it.
Cause (`lab/v/grownet_why4.log`, three unchanged lives, seeds 90000+): under sibling competition the blocks alive fall to 13 to 23 of 30,
the look-back to 4 (net 4 to 8), wrong guesses up by a third. A block in the middle of a chain seldom speaks (its children do), so its
own record is poor; it starves among its siblings, and its recycling takes every specialist below it. Fix (trophic): siblings compete
on standing that includes credit passed down from the blocks built on them, and newborns inherit it (arm netLu). Smoke (3 pairs, seeds
90000+, last third summed): unchanged net 741, netL1 465, netLu1 610; changed 403, 550, 588 (newborns inheriting: 606, 535).
R31. (seeds 90000+, 10 pairs) netLu1 or netLu3 within .2 of net in the unchanged world and tied or above in the changed. 40%.
**Scored R31** (`lab/v/grownet_trophic.log`, seeds 90000+): right. Supply 3: unchanged +1.39 against net +1.50 (-.11 [-.23, +.03], a
tie), changed +1.12 against +.89 (+.23 [-.17, +.60]); supply 1: unchanged -.19 [-.32, -.06], changed +.32 [+.03, +.63] surely above the
written rules. Siblings competing on credit that flows down from their users nearly closes the stable-world cost and beats the written
rules when the world changes.
R32. Confirmation on fresh seeds 93000+ (10 pairs; circuit, tree, net, netLu1, netLu3): netLu3 within .15 of net unchanged, and netLu1
     or netLu3 at least level with net when the pattern changes; both surely above the tree when it changes. 50%.
**Scored R32** (`lab/v/grownet_trophic_confirm.log`, fresh seeds 93000+): mostly right. Supply 3: unchanged +1.17 against net +1.23
(-.06 [-.26, +.18]); changed +.79 against +1.02 (-.23 [-.59, +.17]), neither sure; above the tree when the pattern changes, +1.47
[+1.09, +1.76] (supply 1: +1.52). On two seed sets it is never surely below the written rules, and on one surely above at supply 1.

# Does energy alone limit size? (lab/grownet_scale.py 10 1024, seeds 88000+, ARMS circuit,vtold,net,netLu3; patterns 2 to 17 steps)
With material all but unlimited (512 a stream), the written rules have only fading and copy removal to hold size; the trophic version
also its supply.
R33. netLu3's blocks rise with the pattern and stay far below the material (under 120 at 17), and its share closed is within .1 of the
     run at P 256 (D59: .81 to .95). 50%. net's blocks also stay bounded (copy removal and fading). 60%.
**Scored R33** (`lab/v/grownet_scale_1024.log`): partly. With material unlimited, the written rules' network is exactly as at P 256
(17 to 48 blocks; fading and copy removal bound it). The trophic version is bounded by its supply alone and grows with the pattern, 14 to
28 blocks, but smaller than needed for the long ones: share .93 to .70, against .91 to .81 (13 steps .72 against .82, 17 steps .70
against .81). Its supply (3 a second) now sets its size, as material did.
R34. (patterns 11 and 17, P 1024, supply 10 and 30) more supply, more blocks and a higher share, approaching net's. 60%.
**Scored R34** (`lab/v/grownet_scale_supply.log`): wrong. Supply 10 and 30: the same shares (.82, .69) and sizes (25 to 29) as 3. Above
about 3 a second the pool never runs short, so what bounds size is the split among siblings firing together (zero-sum), not the supply:
the size is set by the competition itself, with no rate to tune, but it comes out a little small for the longest patterns.

# The generic brain so far: a stream for every sense, cleared by trophic sibling competition (arm net5Lu3), against net5 (every sense,
written rules), paired (lab/grownet_pair.py, seeds 92000+, P 160)
R35. net5Lu3 within .1 of net5 on patterns 5 and 11 and combinations 2 and 3 (none surely below). 45%.
**Scored R35** (`lab/v/grownet_generic_*.log`, paired): mostly right. Pattern 5 +.01 [-.02, +.03], 11 -.03 [-.17, +.10], combination 2
+.10 [-.02, +.24], combination 3 -.14 [-.39, -.02] (the one sure shortfall, small). Every sense a stream, cleared by trophic sibling
competition, with no rule written for which stream or which block to keep, does about as well as the written rules.

# The growing network on the muscle-like body (MUSCLE=1; D53), unchanged, paired against the tree (lab/grownet_pair.py, seeds 92000+)
R36. On the muscle body, net (P 64) and net5Lu3 (P 160) each within .15 of the tree (P 64) or above on patterns 5 and 11 and combinations
     2 and 3. 60%.
**Scored R36** (`lab/v/grownet_muscle_*.log`, muscle body, paired against the tree): right. Pattern 5: net +.11 [+.06, +.19] and
net5Lu3 +.09 [.00, +.17] above the tree; 11: -.04 and -.12, ties; combination 3: +.18 and +.07, ties; combination 2 unreadable (on this
body the told brain barely beats the starting one, so shares of the gap explode). The growing network carries over to the muscle body
unchanged, as the coupling principle did (D53).

# The timing ladder (food colour changes with time slots, whatever the creature does): the growing network has no clock among its
streams, so it should fail where D40's tree with clocks (treec) climbs. A measurement of what's missing, not a hope.
R37. (teach.py 10 tree,treec,net5,net5Lu3 time 160 2,3) net5 and net5Lu3 far below treec at both rungs (under .2 where treec is above .5). 80%.
**Scored R37** (`lab/v/grownet_time.log`, unpaired): wrong. On the timing ladder the growing networks do better than the tree with clocks
here: rung 2 net5 .33, net5Lu3 .40, treec .28, tree .22; rung 3 .19, .25, -.08, -.09. None solves either rung. They lean on the
every-taste and bad-taste streams: a bad taste marks a swap, so the run of tastes since the last bad one stands in for a clock. (treec
far below D40's .94 at rung 2; its clock bank and material differ here; not pursued.)
The brain's own clocks offered as streams (net5k8: 8 clocks, periods 3 to 30 s, random phase, drifting; each recording what was last
tasted since its last beat): smoke only (2 pairs): timing rung 2: 61 against net5's 73; rung 3: 12 against 20; pattern 5: 19 against 37
(first version, with a bug in what each clock recorded, fixed). No gain: an unlocked clock drifts against the world's slots, so its
contexts smear; D39 found the phase must be set by the world's changes. Parked, not run at scale.

# The generic brain when the pattern changes (lab/grownet_switch.py, fresh seeds 94000+; circuit, tree P 64, net5 P 160, net5Lu3 P 160)
R38. Changed world: net5Lu3 surely above the tree, and within .3 of net5. Unchanged: within .2 of net5. 55%.
**Scored R38** (`lab/v/grownet_generic_switch_report.log`, fresh seeds 94000+; the script's own report failed with no plain net among
the arms, fixed): right. Changed: net5Lu3 +.83, net5 +.65, the tree -.53: net5Lu3 above the tree by +1.36 [+1.00, +1.70], tied with
net5 (+.18 [-.30, +.63]). Unchanged: .91, 1.05, 1.00: ties (-.13 [-.46, +.20] against net5). The generic brain relearns a changed pattern.

# Remembering: pattern A, then B (400 to 500 s), then A again (900 to 1000 s); scored on the last third (A's return)
(lab/grownet_switch.py WORLDS=changed,aba, fresh seeds 95000+; circuit, tree, nonet, net, net5Lu3). The tree and nonet keep everything
but filled their material on A; net and net5Lu3 cleared A's blocks while B ruled, if unused for long enough (200 s fading; B rules 400
to 600 s), so they must relearn A as if new.
R39. In the A-B-A world, net and net5Lu3 score about as in the changed world (relearning, not remembering): within .3 of their changed-
     world scores; the tree and nonet do better than in the changed world (A is back in their memory). 50%.
**Scored R39** (`lab/v/grownet_aba.log`, fresh seeds 95000+): right. A-B-A, last third (A back): the tree +.78 and nonet +.81 (A still in
their memory; they never learned B: changed world -.52, -.67); net +.86, about its changed-world +.75 (relearning A); net5Lu3 +1.13,
above its changed-world +.76 and surely above net (+.27 [+.00, +.55]): the generic brain keeps some of A through B, or relearns it
faster. No brain loses to the tree when A returns, and the growing ones gain 1.3 to 1.4 when the pattern changes for good.
Traced (`lab/v/grownet_memory.log`, three lives): the generic brain's +1.13 is fast relearning, not memory: none of its blocks alive at
the end was born before 400 s. The written-rules net keeps 10 to 17 of 30 from A's first spell, without scoring better for it.

# The scaling curve (README, the scaling test 1 and 4) for the generic brain (net5Lu3: every sense a stream, trophic sibling competition)
teach.py 10 net5Lu3 on every rung of all three ladders, material 40, 80, 160, 320, 640 (8 to 128 a stream), development seeds 84000+.
R40. Sequences: the highest rung solved rises with material over at least two doublings (e.g. 5 at 40, 11 or more at 160+). 55%.
R41. Combinations: rises with material, at least two rungs between the smallest and largest. 45%.
R42. Timing: no rung above 2 solved at any material (no clocks). 75%.
R43. Plain world (sequence rung 1): blocks alive under a tenth of the material at every size. 50%.
**Scored R40-R43** (`lab/v/grownet_curve_*.log`, 10 pairs, development seeds): R40 right, more than predicted: on sequences the
highest rung solved goes 3, 5, 11, 17, 17 with material 40, 80, 160, 320, 640 (the ladder's top reached at 320); at 320 and 640 rungs 11,
13, 17 at .78 to .89. R41 partly: combinations 1, 1, 3, 3, 3 (rises once, rungs 4 to 6 unsolved at any size; 4 reaches .61 at 640, not
surely). R42 right: timing solves nothing above rung 1 (rung 2 best .48 at 40), and more material does worse there (rung 6: .44 at 40,
.12 to .18 above): the cost of size, measured. R43: the plain world's score is exactly 0 at every size, the gate never adopting a
stream, so no material is committed (affects behaviour) where nothing is to be learned.
R44. Confirmation on fresh seeds 96000+ (sequences, material 40, 80, 160, 320): highest rung solved rises over the three doublings to at
     least 11 at 320. 65%.
**Scored R44** (`lab/v/grownet_curve_seq_fresh.log`, fresh seeds 96000+): right. Highest rung solved 3, 3, 13, 17 with material 40,
80, 160, 320; at 320 rungs 11, 13, 17 at .91, .77, .68. Rungs 5 and 7 (100 s lives) are solved at no size (.58, .49 at best): the
ladder's 100 s rungs are harder for this brain than its 300 s ones; their lives may be too short for it (AGENTS: a rung's life as long
as it needs).

# Why combinations stall: the size cap of sibling competition? (D59: about 28 blocks a stream whatever the supply; rung 5 needs 32
contexts, rung 6 64). teach.py 10 net5 combo 320,640 4,5,6 (written rules, no such cap), against D60's net5Lu3.
R45. net5 surely above net5Lu3's D60 shares on rungs 5 and 6 at 640 (e.g. .5 or more against .32 and .17). 50%.
**Scored R45** (`lab/v/grownet_combo_cap.log`): wrong. Without the cap (written rules, 45 to 74 blocks) the combinations stall just the
same: rung 4 .46, .47 (net5Lu3 .53, .61), rung 5 .41, .44 (.47, .32), rung 6 .25, .21 (.09, .17). The size cap is not the bottleneck.
Not traced; candidates: evidence (rung 6 has 64 contexts, and a life of 1000 s gives a few hundred trusted tastes, spread unevenly since
the creature's own choices shape which histories occur), or the every-taste stream's symbols (good and bad tastes break a history of
colours eaten into four symbols where two would do).
R46. (the four-symbol hypothesis) teach.py 10 tree,net combo 320,640 5,6: the two-symbol eaten stream (net) and the tree (D40: rungs 5
     and 6 climbed at 20 pairs) surely above net5 on rungs 5 and 6. 50%.
**Scored R46** (`lab/v/grownet_combo_sym.log`, unpaired): partly. The two-symbol eaten stream: rung 5 .55, rung 6 .35 (net5 .44, .21):
higher, not surely. The tree does best, .65 (solved at 320) and .55, holding 160 to 206 nodes: it never prunes. Two things seem to hold
the growing networks back on combinations: four symbols where two would do, and pruning: of 64 contexts, the rarely visited ones go
unused longer than the fading horizon (200 s) and are recycled, where the tree keeps them.

# Recycling on demand (arm netR; Dohare et al. 2024's comparator): no fading; copies removed; when a birth is due and material is full,
the least used of four blocks drawn at random (with nothing built on them) is recycled. Rare contexts survive unless room is needed.
Smoke (2 pairs, last third summed; net, netR): combination 5 (P 320): 179, 209; changed pattern (P 64): 262, 530; unchanged: 449, 541.
R47. (10 pairs) netR above net on combinations 4 to 6 (P 320), and at least ties it in both worlds of the changing pattern (P 64). 45%.
**Scored R47** (`lab/v/grownet_ondemand_*.log`): half. Combinations (P 320): no gain (rung 4 .56 against .54, 5 .55 both, 6 .38 against
.35): pruning by fading was not what held them back after all. The changing pattern (P 64): netR surely above net in both worlds,
unchanged +1.69 against +1.34 (+.35 [+.17, +.53]), changed +1.57 against +1.15 (+.42 [+.11, +.75]); above the tree by about 2 when the
pattern changes. Where material is short, recycling only when room is needed keeps what works and still frees room for what's new.
R48. Confirmation on fresh seeds 97000+ (circuit, tree, net, netR): netR surely above net in at least one world and not below in either. 60%.
**Scored R48** (`lab/v/grownet_ondemand_confirm.log`, fresh seeds 97000+): right, strongly. netR above net in both worlds: unchanged
+1.67 against +1.14 (+.53 [+.25, +.79]), changed +1.48 against +.73 (+.74 [+.49, +1.06]); above the tree by +.73 unchanged and +2.30
changed. Recycling only when room is needed is the best clearer so far.
R49. The generic brain with recycling on demand (net5R: every sense a stream) on the sequence curve, fresh seeds 96000+ (as D60's
     net5Lu3: 3, 3, 13, 17 at 40 to 320): solves the same or higher rungs with the same material, at least one rung higher at 80. 50%.
**Scored R49** (`lab/v/grownet_curve_R_fresh.log`, fresh seeds 96000+): partly. net5R's highest rung solved 3, 3, 17, 17 with material
40, 80, 160, 320 (net5Lu3: 3, 3, 13, 17): it reaches the ladder's top with half the material; not higher at 80.
R50. (development seeds) net5R on combinations 40 to 320 and timing 40 and 160: combinations no higher than net5Lu3's (3); timing nothing. 70%.
**Scored R50** (`lab/v/grownet_curve_R_combo.log`, `_time.log`): right. Combinations 1, 1, 3, 3 at 40 to 320 (rung 2 .72 at 320, not
sure); timing nothing (rung 2 .42 at best), more material again a little worse.

# Streams that record one sense each (arm net10R): every clock (every taste, good, bad, red, blue) times every recorded sense (the
colour eaten; good or bad), ten streams of two symbols each, instead of five of four. Generic (no choice of what to record), and lets a
combination lesson read colours alone.
R51. (development seeds, P 640 = 64 a stream) net10R on combinations 4 to 6 above net5R at 320 (.44, .46, .22) by .1 or more on at
     least two rungs; on sequences 11 and 17 no worse than net5R at 320 by more than .1. 40%.
Smoke (2 pairs): picks every:colour on combination 4 (24 against net5R's 18) and good:colour on sequence 11 (107 against 72).
**Scored R51** (`lab/v/grownet_split_*.log`, unpaired): right. Combinations at 640: rung 4 .57 (net5R at 320 .44), 5 .49 (.46), 6 .36
(.22); sequences 11 .76 (.76), 17 .72 (.65). Better on combinations 4 and 6 by .13 and .14, no worse on sequences; no new rung solved
(4's interval starts at .46). Still below the never-pruning tree on 5 and 6 (.65, .55).
R52. Paired on fresh seeds 98000+ (combinations 4, 5, 6; net5R at 320 against net10R at 640, the same material a stream): net10R above
     on at least two rungs, surely on one. 45%.
**Scored R52** (`lab/v/grownet_split_pair.log`, fresh seeds 98000+, paired): right. Rung 4 +.19 [+.02, +.39] (.59 against .40); 5
+.02, 6 +.03, ties. One sense a stream surely helps the combination of four, not yet the longer ones.
R53. Are rungs 5 and 6 short of evidence? The same rungs in lives three times as long (3000 s, judged on the last third; tree P 320,
     net10R P 640, paired, seeds 98000+): both rise by .15 or more. 55%.
**Scored R53** (`lab/v/grownet_combo_long.log`, 3000 s, paired): half. The tree rises to .76 and .72 (solves both); net10R only to .49
and .38, surely below the tree by .28 and .34. Not evidence alone. Traced (two lives, combination 6, 3000 s): net10R makes about 9000
blocks a life but keeps 60 to 70, even with 256 a stream: removing a copy recycled every block built on it, though its twin fires alike.
Fix: merge copies (the copy's dependants handed to its twin; arm net10M). Two lives: 119 to 184 blocks kept at 256 a stream (the tree
160), last third 12 and 125 (net10R -24, -66; tree 203, 183).
R54. (3000 s, paired, seeds 98000+; tree P 320, net10M P 2560) net10M within .15 of the tree on combinations 5 and 6. 35%.
**Scored R54** (`lab/v/grownet_merge_long.log`): wrong. Merged copies, 256 a stream: .38 and .36, the tree .76 and .72. Keeping more
blocks did not help. Likely cause (not yet traced): churn. The network grows a block beneath every contradiction, about 9000 a life,
recycling to make room; the tree stops growing when its material is full and keeps counting. With 32 or 64 contexts, many rarely seen,
a block is often recycled before it has counted enough to be right. Open: growth that slows when it stops paying (boredom, D46), e.g.
a parent grows a child only when its own record is surely worse than chance after its last child had time to prove itself.
Smokes on churn (two lives, combination 6, 3000 s, 64 a stream): growth stopping when full (net10F, no evictions, copies merged):
111, -76; 252 kept at 256 a stream: 20, -27 (copies still born and removed by the thousand). The simplest partner (one step longer, as
the tree): -133, -105, worse (sequence 11 alike). Not run at scale. Parked: what the tree does that these don't, on many rare contexts.

# A fault in copy removal (bench, `lab/v/grownet_bench_combo.log`): a parent and its child fire alike while the parent's other branches
rest, so over a 30-step window they look like copies and one is removed (and with it its dependants). On the combination bench (no
body, 3000 tastes, 128 units) the network with no pruning is right 99-100% with about 100 blocks and no copies at all; with copy removal
93% and 800 blocks born, 450 "copies" removed. Strict copies (never a block and its own ancestor or descendant): 97-99%, 100 to 280 born.
Every D59 result with written rules used the faulty rule; "copy removal does the work" (R7) partly measured freeing material by this
fault. To be rechecked with strict copies.
R55. (3000 s, paired, seeds 98000+) net10X (ten streams, recycling on demand, strict copies) on combinations 5 and 6 within .15 of the tree. 45%.
**Scored R55** (`lab/v/grownet_strict_long.log`): wrong in letter, a large step. Strict copies: .60 and .51 (from .49 and .38), the
tree .76 and .72: the gap halved (-.17 [-.27, -.10], -.21 [-.27, -.17]) but still sure. At 64 a stream the material is full and
recycling on demand churns; the tree has 160 a register.
R56. net10X with 256 a stream (P 2560): within .1 of the tree on both rungs. 45%.
**Scored R56** (`lab/v/grownet_strict_big.log`): right. With 256 a stream, strict copies: combination 5 .67 [.54, .77], 6 .62 [.56, .68],
both solved; the tree .76 and .72; differences -.09 and -.10 (sure, small). The growing network now solves the combinations of 5 and 6.
R57. Rechecking D59 with strict copies (changing pattern, fresh seeds 99000+, P 64): netX (fading, strict copies) and netRX (on demand,
     strict) relearn a changed pattern as well as their faulty forms did (net, netR), within .3, and above the tree. 60%.
**Scored R57** (`lab/v/grownet_strict_switch.log`, fresh seeds 99000+): half, and a correction. Recycling on demand doesn't depend on the
fault: netRX +1.64 unchanged, +1.69 changed (netR +1.62, +1.70). But fading with strict copies (netX) is stuck when the pattern changes
(.00, against net's 1.04; unchanged .87 against 1.36): the faulty copy rule, by recycling parents and children it took for copies, was
doing the clearing D59 credited to copy removal. Corrected in D59 and the README: what lets the network relearn is recycling to keep
room free; with true copies only, fading by a timer is too slow, and recycling on demand does it.

# The scaling curve of the best generic brain so far (net10X: ten streams, recycling on demand, strict copies), fresh seeds 96000+
(sequences, as D60's fresh run) and development seeds 84000+ (combinations, as D60), material 40 to 640.
R58. Sequences: reaches 17 by 320 at the latest. Combinations: highest rung solved rises above D60's 3 (at least 4) by 640. 50%.
**Scored R58** (`lab/v/grownet_curve_X_*.log`): right. Sequences (fresh seeds): 3, 3, 11, 17 at 40, 80, 160, 320 (17 at .69 [.58,
.78]). Combinations (development seeds): 1, 3, 5, 3 at 40, 160, 640, 2560 (rung 5 .63 [.54, .73] at 640; at 2560 .58 [.41, .68], not
sure; rung 4, a 300 s life, .60 to .65, never surely). Highest combination solved rises from D60's 3 to 5.

# Timing: clocks restarted by surprise (arm net5kr8: five sense streams and 8 own clocks, periods 3 to 30 s, each restarted at every
bad taste so its beats count time since the last surprise; recycling on demand, strict copies). A bad taste is the brain's own sense;
nothing about the world's timing is told. Smoke (2 pairs, last third summed; net10X alongside): rung 2: 81 (80); 3: 86 (32); 5: 154 (114).
R59. (teach.py 10 net10X,net5kr8 time, rungs 2, 3, 5, 7) net5kr8 solves at least one timing rung, and is above net10X on at least two. 35%.
**Scored R59** (`lab/v/grownet_reset_time*.log`, unpaired): half. Clocks restarted by surprise: rung 2 .40 (net10X .28), 3 .34 (.12),
5 .14 (.21), 7 .34 (.32); above on two rungs, none solved. Timing parked: the growing brain's best is about a third of the gap.

# Doing no harm (README scaling test 4) for net10X: the plain world (sequence rung 1) and the all-food world, material 40 to 2560,
paired against the starting brain (lab/grownet_pair.py won't do all-food; inline, logged to lab/v/grownet_noharm.log).
R60. Plain and all-food: net10X within .1 of the starting brain at every size (in raw efficiency). 60%.
**Scored R60** (`lab/v/grownet_noharm.log`, 20 pairs): right, exactly. Plain and all-food, material 40 to 2560: lives identical to the
starting brain's (difference .00): the gate never hands the steering to a stream, so behaviour is the starting brain's. Caveat: the
material's power is not charged in these scores (the scaling test's sixth part asks that it be).

# The best generic brain on the changing pattern (lab/grownet_switch.py, fresh seeds 100000+; circuit, tree P 64, netRX P 64, net10X P 640)
R61. net10X surely above the tree when the pattern changes and within .3 of netRX in both worlds. 60%.
**Scored R61** (`lab/v/grownet_best_switch.log`, fresh seeds 100000+): right. net10X +1.77 unchanged (above the tree by +.53 [+.33,
+.74]), +1.75 changed (above the tree by +2.20 [+1.83, +2.48], and netRX by +.28 [+.04, +.49]): the best generic brain loses almost
nothing when the pattern changes.

# The best generic brain when an old pattern returns (A-B-A; fresh seeds 101000+; circuit, tree P 64, net10X P 640)
R62. net10X at least ties the tree when A returns (the tree never learned B and keeps A). 55%.
**Scored R62** (`lab/v/grownet_best_aba.log`, fresh seeds 101000+): right, more than predicted. When A returns, net10X +1.55 against the
tree's +.70 (+.86 [+.49, +1.22]); when the change is for good, +1.67 against -.49. The best generic brain handles a returning pattern
better than the brain that never forgets (whether by memory or by relearning fast, not traced).

# Sequence rungs 5 and 7 in longer lives (300 s, as rungs 11 to 17; fresh seeds 96000+, net10X at 160 and 320, paired against circuit)
R63. Both solved at 160 or 320 given 300 s (they were .57 and .46 in 100 s). 60%.
**Scored R63** (`lab/v/grownet_seq_long57.log`, fresh seeds 96000+): right. In 300 s lives rungs 5 and 7 are solved at 160 and 320
(.96, .97; .84, .90): the 100 s life was the limit, not the brain. With lives as long as the larger rungs', every sequence rung is
solved by 160 to 320 units.

# The scaling test's third part: recruitment switched off (net10X with 20 units, two a stream: only its senses, no block can be born)
against on (320), paired, fresh seeds 96000+ (sequences 11, 17) and 98000+ (combination 3).
R64. Surely better with recruitment on, on every rung. 85%.
**Scored R64** (`lab/v/grownet_recruit_off_*.log`): mostly right. Recruitment on against off: sequence 11 +.46 [+.29, +.63], 17 +.37
[+.26, +.46], sure; combination 3 +.17 [-.05, +.35], not sure (with only its senses the brain already reads one colour back, half the
lesson).

# The best generic brain on the muscle-like body (MUSCLE=1, paired against the tree, seeds 92000+; sequences 5 and 11, combination 3)
R65. net10X (320) at or above the tree (64) on all three, none surely below. 65%.
**Scored R65** (`lab/v/grownet_best_muscle_*.log`): right. On the muscle body net10X ties the tree on all three (+.04, -.08, +.01, none
sure).

# Timing with D39's clocks in the growing brain (arm net5kc60: five sense streams and 60 own clocks, periods 3 to 30 s, each re-phased
when the revealed food colour changes, a beat recording the food colour last revealed, held; recycling on demand, strict copies). The
clocked tree (treec) solved timing rung 2 in D40 with about 1000 units. Smoke (2 pairs, last third summed; treec 992 alongside):
recording the last taste or "nothing" at a beat: rung 2 75 (149); recording the held colour: rung 2 112 (149), rung 5 181 (256).
R66. (paired, 10 pairs, seeds 84000+, rungs 2, 5, 7; treec 992, net5kc60 1040) net5kc60 within .2 of treec on each, and solves rung 2. 35%.
**Scored R66** (`lab/v/grownet_clocks_time.log`, paired): right. net5kc60 solves timing rung 2 (.64 [.53, .75]; the clocked tree .81),
and is within .2 of the tree on 5 (.41 against .35) and 7 (.31 against .40). The growing brain's first timing rung.

# One design for all three ladders (arm net10kc60: ten sense streams and 60 clocks re-phased by revealed changes; recycling on demand,
strict copies; the README's scaling test, part 2: one description across the curve). Smoke (2 pairs): it picks good:colour on
sequence 11 (150), every:colour on combination 3 (86), a clock on timing 2 (71), by itself.
R67. (fresh seeds 102000+, paired; net10kc60 at 2240 against each ladder's specialist: net10X 320 on sequences 11 and 17, net10X 640
     on combinations 3 and 5, net5kc60 1040 on timing 2) the one design solves sequence 11 and 17, combination 3 and timing 2, and is
     within .15 of each specialist. 40%.
**Scored R67** (`lab/v/grownet_one_design_*.log`, fresh seeds 102000+): partly. The one design is within .15 of each specialist
everywhere (sequences -.06, -.01; combinations -.09, -.11; timing +.10) and solves sequences 11 and 17 (.83, .65), but not combination 3
(.50 [.20, .71]) nor 5 (.48), nor timing 2 (.47). And on these fresh seeds the timing specialist itself reaches only .37 [.23, .51]:
R66's solved timing rung (.64 on development seeds) does not hold on fresh ones. README corrected.

# The one design's scaling curve on all three ladders (net10kc60, material 560, 1120, 2240, 4480 = 8 to 64 a stream; fresh seeds
103000+; sequences 3, 5, 11, 17 at their own lives; combinations 1 to 5; timing 2 and 5).
R68. Sequences: highest solved rises to 17 by 4480. Combinations: rises to at least 3. Timing: rung 2 solved at no size (fresh seeds).
     Overall: the scaling test's first part on two of three ladders with one design. 40%.
**Scored R68** (`lab/v/grownet_one_curve_*.log`, fresh seeds 103000+): partly. Sequences: highest solved 3, 11, 17, 17 at 560 to 4480.
Combinations: 1 at every size, though every rung rises with material (3: .36 to .63, 5: .16 to .56, neither surely above .5). Timing:
rung 2 .37 to .54, rung 5 .38 to .48, rising, not solved. The one design climbs one ladder outright and rises on the other two.

# Plan B2 on the body, first step: a taste is about the eye the brain was following (its own action), not the eye that pulsed last;
no vouching (arms net5a, net5at with the symmetry told; recycling on demand, strict copies, every agreeing source scored).
Smoke (2 pairs, last third summed; net10X alongside): plain 23 and 27 (36); pattern 11: -9, -12 (95); combination 3: 5, 28 (95). Far
worse. Its own action is a poor witness of what it ate: the creature often eats the other colour by accident while approaching one,
and those tastes then count against the eye it was following. The eye that pulsed last at the moment of eating is a sense, and it is
what makes the earlier versions work (net5v, without vouching, lost only .1 in the plain world). Not run at scale.

# The held-out ladder (opened 2026-11-13 after freezing the design; PROGRAMME.md, Decisions): hidden contexts, each flagged only by a
background pulse rate on the eyes, each with its own secret food colour, recurring; rungs of 1 to K contexts, 1000 s lives. Frozen
design net10kc60 at 560 to 4480; the tree (P 64) as a reference; held-out seeds 70000+, 10 pairs.
H1. The frozen design solves rung 1 (one context: plain learning) and no rung above 2: its streams are built from tastes and never read
    a background rate on the eyes, which is what tells the contexts apart. 70%.
**Scored H1** (`lab/v/heldout_ladder.log`, held-out seeds 70000+): half. Rung 1 can't be credited: the told brain is below the starting
one (1.70 against 2.05), so there is no gap. Rungs 2 to 6: the frozen design closes .28 to .36 of the gap at 560 to 2240 units, surely
above the starting brain on rungs 2, 3 and 4 (lower ends .15 to .23 at 560), above the tree (which loses, -.14 to -.31), but solves none,
does not climb with material, and does worse with the most (4480: .12 to .24). Rung 8's gap is too small to read (told .69, base .42).
The verdict on generality: a third of the way on an unseen ladder, by reading recent tastes (a context lasts about 10 s); not the
background rates on the eyes that would tell the contexts apart, which no stream offers.

# The price of size (D61; the scaling test 6): break-even power a unit (lab/sizecost.py) from paired lives of the frozen design at 560,
1120, 2240, 4480 units on sequences 11 and 17 (lab/grownet_pair.py, seeds 103000+, as D60's curve).
S1. Going from 560 to 2240 units pays as long as a unit draws under about 1 nW (a thousandth of the creature's resting burn). 40%.
**Scored S1** (`lab/v/sizecost.log`, `lab/sizecost.py`): about right. Extra material pays while a unit draws under: from 560 to 1120
units 3.1 nW (rung 11) and .5 nW (17); to 2240, 2.0 and 1.7 nW; to 4480, .7 and .6 nW. The creature rests at 1000 nW: at break-even 2240
units draw about 4 uW, four times the creature's resting burn. (A first version of the calculation equated efficiencies and gave
negative powers, a smaller brain's net gain being below zero; replaced by extra meals against extra energy.)

# Closing the gaps (PROGRAMME, the user: continue through the programme): timing rungs 2 and 3 in lives three times as long (900 and
1350 s; fresh seeds 104000+; the frozen design at 2240, the clocked tree at 992), paired.
T1. Both rise by .15 or more over their 300 s / 450 s levels on fresh seeds (.47 and about .3), and rung 2 is solved. 45%.
**Scored T1** (`lab/v/timing_long2.log`, `timing_long3.log`, fresh seeds 104000+): partly. Timing rung 2 in 900 s lives is solved by the
frozen design, .57 [.54, .60] (the clocked tree .60, a tie); rung 3 in 1350 s .39 [.28, .48], not (tree .47). Timing was partly short of
evidence: three times the life solves the first rung on fresh seeds.

# Streams over the eyes' own pulses (arm net10kc60e: the frozen design plus three own clocks an eye, each beat recording how many pulses
that eye gave since the last: 0, 1-2, 3-8, 9+). Development only on the held-out ladder, now spent (its numbers here are no verdict).
Smoke (2 pairs, last third summed; the frozen design alongside): hidden contexts 3: 157 (131), the gate choosing clocks, never an eye
stream; sequence 11: 99 (150). Likely: the eyes' pulses while approaching a block swamp the background rate that marks a context, so a
count per beat says more about the approach than the context. Parked at the smoke: what would separate them (a slow average of each eye's
rate, or counts only while not driving) is a design choice to make with the user, since it touches what the eyes are taken to mean.

# Running averages of every eye (the user: a measure to try for any signal; arm net10kc60a: for each eye three averages of its pulse
rate, time constants 0.5 to 10 s drawn per life, recorded low, middle or high against the thirds of their own history).
Smoke (2 pairs): hidden contexts 3 (spent ladder, development only) 125 (the frozen design 131), the gate never choosing an average;
sequence 11: 113 (150). Traced (one hidden-context life): the averages do carry the context: an eye's "high" third predicts the food
colour 86 to 32, its streams right about 70% of the time; but the best taste stream ("colour at each bad taste") is right 77% and the
averages stay under the gate's bar (their scores 2 to 4 against 4.2). What's missing is not the measure but the joining: a block can't
combine "this eye has been busy" with "the last tastes were", because blocks live within one stream. Next mechanism: blocks that join
units of different streams active at the same moment (a coincidence across streams), so that one context can use several senses.

# Joint detectors across streams (JointNet; arm net10kc60aj: the frozen design, the eyes' running averages, and a joint stream whose
units join one unit of one stream with one of another, co-active). Smoke (2 pairs): hidden contexts 3 (spent, development only) 208
against 125 without; sequence 11: 119 against 113.
J1. (development seeds 84000+, 10 pairs; the spent held-out ladder's rungs 2, 3, 4, 6 via heldout_run.py at 2368, development only)
    net10kc60aj above net10kc60a by .1 or more on at least two rungs. 45%.
J2. (sequences 11, 17; combinations 3, 5; development seeds 84000+, paired) net10kc60aj no worse than net10kc60 by more than .1. 60%.
**Scored J1** (`lab/v/joint_hidden_dev.log`): wrong. On the spent held-out ladder (development seeds), joint detectors change nothing:
rungs 2 to 4 .16 to .21 against .19 to .25 without (rungs 6 and 8 unreadable). **Scored J2** (`joint_seq.log`, `joint_combo.log`): right:
no harm elsewhere (sequence 11 -.08, just sure; 17, combinations 3 and 5 ties).
Traced (one hidden-context life): the joint stream is right 77% of the time (316 against 93) but holds only 17 units (110 born, most
lost when their parts were recycled in their own streams), and its partners are mostly clocks; the best stream here is a clock re-phased
by revealed changes, right 85%. In this world the brain already tracks the contexts best by noticing when the food colour changes; the
eyes' averages add little. The gap left (a third closed) is not the joining.
Traced (`lab/v/hidden_trace.log`): heading right 82-89% (growing) against 84% (starting brain); following changes in 1.0 s against 1.9 s.
The third of the gap is quicker following; the rest needs foreseeing changes, which the eyes reveal hardly faster than a taste. The told
yardstick (the food colour at every moment) is beyond any learner here. Recorded in D61.

# Overnight confirmation: the best generic brain's combination curve on fresh seeds (net10X at 40, 160, 640, 2560; seeds 105000+; D60
gave 1, 3, 5, 3 on development seeds).
C1. Highest combination rung solved rises to at least 3 by 640 on fresh seeds. 55%.
**Scored C1** (`lab/v/grownet_curve_X_combo_fresh.log`, fresh seeds 105000+): wrong. Only rung 1 surely solved at any size; every higher
rung rises with material (rung 4 .14 to .35, 5 .29 to .61, 6 .19 to .45; rung 5 at 640 .61 [.44, .74], not sure), and rung 2's gap is
small here (base 1.79, told 2.34). The development seeds' "1 to 5" does not hold on fresh ones: a rise, not a climb. README corrected.
C2. The same curve with 3000 s lives (SECS=3000; rungs 3 to 6; fresh seeds 106000+): highest rung solved rises with material to at least
    5 by 2560. 50%.
**Scored C2** (`lab/v/grownet_curve_X_combo_long.log`, 3000 s lives, fresh seeds 106000+): right. Highest combination rung solved: 40
units none of 3 to 6 (3 at .57, not sure), 160: 3, 640: 4, 2560: 6 (.59 [.54, .64]; rung 5 .58 [.47, .64], not sure). Given lives as long
as they need, the combination ladder climbs with material on fresh seeds: every rung rises, and the highest solved goes 3, 4, 6.

# Timing with lives as long as they need (SECS=3000; the one design net10kc60 at 560, 1120, 2240; rungs 2, 3, 5, 7; fresh seeds 107000+)
T2. Highest timing rung solved rises with material to at least 3. 35%.
**Scored T2** (`lab/v/grownet_curve_time_long.log`, 3000 s, fresh seeds 107000+): wrong in letter. Timing rung 2 solved at 1120 and 2240
(.55, .58); rungs 3, 5 and 7 rise with material (.40 to .52, .36 to .53, .36 to .47) but none surely passes half (5 at 2240 .53 [.49,
.56] just short). Timing rises with material and life; it climbs only its first rung.
T3. (3000 s, fresh seeds 107000+, rungs 3 and 5) more clocks and material: net10kc120 at 4480 (about 33 a stream, as 2240 with 60)
    surely above net10kc60 at 2240 on both, and solves at least one. 35%.
**Scored T3** (`lab/v/timing_more_clocks.log`): wrong. Twice the clocks and material: rung 3 .52 (.51), rung 5 .48 (.53). Timing plateaus
near half whatever the clocks: the limit is not their number. Likely the phase: re-phased only when the revealed colour changes, a clock
drifts unchecked through runs of one letter, which longer words in time have more of (D39: phase moved no further than the evidence
says). Parked.

# No gate: a vote (arm net10kc60v): every stream adds its evidence over the default (its E) for its speaker's guess; the default holds
unless the sum passes the Occam bar. The one central choice (the argmax over streams) replaced by a sum, as inputs converge on a motor.
V1. (paired, development seeds 84000+; sequences 11, 17; combinations 3; timing 2 at 900 s) the vote within .1 of the gate everywhere. 50%.
**Scored V1** (`lab/v/vote_*.log`): wrong, badly. The plain vote: sequence 11 .28 against .91, 17 .32 against .71, combination 3 .37
against .75; timing 2 tied (.52, .49). Summed evidence lets many middling streams outvote the best.
V2. Weighted majority instead (arm net10kc60m: each stream's weight halved at each of its own wrong guesses, the default an expert too;
    Littlestone & Warmuth 1994): within .1 of the gate on all four. 45%.
**Scored V2** (`lab/v/wmaj_*.log`): partly. Weighted majority: sequence 11 .72 against .91 (-.19 [-.37, -.05]), 17 .57 against .71
(-.14, just sure); combination 3 .70 (.75, tie); timing 2 .51 (.49, tie). Close, behind on sequences.
V3. A gentler weight (a wrong guess multiplies by .8, not .5; WM_BETA=0.8; one try, not tuned further): within .1 of the gate on all. 40%.
**Scored V3** (`lab/v/wmaj8_*.log`): wrong. Gentler (.8) is worse: sequence 11 -.27, 17 -.36, combination 3 -.14. The harsher the
penalty, the closer to the gate.
V4. (the trend's other side, .25; one try) within .1 of the gate on sequences 11 and 17. 45%.
**Scored V4** (`lab/v/wmaj25_seq.log`): wrong. Harsher (.25): sequence 11 -.23, 17 -.15: no better than .5. A weighted majority settles
.15 to .2 below the gate on sequences whatever its penalty, ties it on combinations and timing. Parked; the gate stays.
V5. Weighted majority with the gate's caution (WM_BAR=1, beta .5: a stream votes only once its weight beats the default's): within .1
    of the gate on sequences 11 and 17. 40%.
**Scored V5** (`lab/v/wmajbar_seq.log`): wrong. With the caution: sequence 11 -.16, 17 -.17: the same gap as without. The weighted
majority's shortfall on sequences is not the missing bar. Parked with the question (QUESTIONS.md).
Traced (two sequence-11 lives): weights only fall at mistakes, so streams that rarely speak keep high weight: clocks with 1 right and 1
wrong held .5 while the best stream (135 right, 21 wrong) sank to 5e-7. Silent streams outweigh reliable ones.
V6. Specialists (WM_SPEC=1, beta .5; Freund, Schapire, Singer & Warmuth 1997: only the streams that spoke are updated, their total weight
    kept, so reliable speakers gain against the rest): within .1 of the gate on sequences 11 and 17. 55%.
**Scored V6** (`lab/v/wmajspec_seq.log`): right. Specialists: sequence 11 .83 against .91 (-.08 [-.16, -.01]), 17 .70 against .71 (-.01).
V7. (WM_SPEC=1; development seeds: combinations 3 and 5, timing 2 at 900 s; fresh seeds 108000+: sequences 11 and 17) within .1 of the
    gate everywhere. 50%.
**Scored V7** (`lab/v/wmajspec_*.log`): right. Specialists tie the gate everywhere: combinations 3 +.01, 5 +.02; timing 2 -.01; fresh
seeds 108000+, sequences 11 +.03, 17 -.03 (all intervals across 0). The central gate can be replaced by a local weighted majority of
specialists at no cost.

# Why timing plateaus near half: a diagnosis (NODRIFT=1, clocks without drift: not allowed in a design, AGENTS; only to find the cause)
T4. (3000 s, fresh seeds 107000+, rungs 3 and 5, net10kc60 at 2240, paired with and without drift) without drift surely higher on both,
    by .1 or more. 45%.
**Scored T4** (`lab/v/timing_nodrift.log`): wrong. Without drift, rungs 3 and 5 .51 and .51 (with drift .51 and .53): drift is not what
holds timing near half. Remaining candidates: the nearest clock's period mismatch (60 clocks over a decade, about 4% apart, a phase error
growing between re-phasings much as drift would), or a ceiling at slot boundaries (a learner unsure of a boundary by a second loses
there, while the yardstick is told the moment). Parked.
T5. (diagnosis) The designed brain told the slot length but not the phase reaches no more than .65 on timing rungs 3 and 5 (3000 s, the
    same lives): the plateau is mostly a ceiling at slot boundaries. 45%.
**Scored T5** (`lab/v/timing_ceiling.log`): wrong, usefully. Told the slot length (not the phase), the designed brain reaches .83 and .78
on rungs 3 and 5 against the growing brain's .51 and .53: not a ceiling. What's missing is the period: the brain's clocks keep the
periods they were born with.
T6. Period locking (LOCK=0.2: at each revealed change every clock nudges its period a fifth of the way toward the interval since the last
    change over its nearest whole number of beats; a phase-locked loop, generic): rungs 3 and 5 surely higher than without, by .1. 45%.
**Scored T6** (`lab/v/timing_lock.log`): wrong. Locking every clock (rate .2, window ±50%): rungs 3 and 5 .42 and .36, below no locking
(.51, .53): every clock pulled by noisy intervals, the bank loses its spread.
T7. (one more try, then parked) only clocks already within 10% adjust, at rate .1 (LOCK=0.1 LOCK_WIN=0.1): above no locking on both. 35%.
**Scored T7** (`lab/v/timing_lock_narrow.log`): wrong. Narrow locking: .53 and .50 (without .51, .53): no change. Period locking parked.
T8. (diagnosis: TOLDT=1, one clock told the exact slot length) rungs 3 and 5 rise to .7 or more: the period's precision is the whole
    story. 40%.
**Scored T8** (`lab/v/timing_toldT.log`, diagnosis): wrong. With one clock told the exact slot length, rungs 3 and 5 stay at .50 and .47.
So the period is not what timing lacks either. The designed brain (told the period) counts its place in the whole cycle (a clock of n
slots, five bins a slot) and keeps a letter per place; the growing brain reads the letters at past beats, and a beat with no taste in
its slot records a stale colour, so its contexts are corrupted where the designed brain's place is not. What's missing is a count of
place (beats modulo a cycle), not a better clock. Parked, with that as the candidate (QUESTIONS.md).
Counters as streams (smoke, 2 pairs, 3000 s; arm net10kc20c: 20 clocks, each with counters of its beats modulo 2 to 8): timing 3: 992
against 1096 without; 5: 916 against 1000. The gate sometimes follows a counter, without gain: a counter's cycle (n beats of a clock a few
percent off the slot) slides against the world's within a few cycles, and re-phasing the clock at changes doesn't re-align its count.
A counter would need its count, not only its beat, set by the world's changes. Parked at the smoke.

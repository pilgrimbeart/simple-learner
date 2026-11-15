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

# The frozen design's scaling curve (net10kc60S; PROGRAMME.md, Decisions 2026-11-14), fresh seeds 120000+, material 560 to 4480;
sequences 3, 5, 7, 11, 13, 17 in 300 s lives; combinations 2 to 6 and timing 2, 3, 5, 7 in 3000 s lives.
F1. Sequences: highest solved rises to 17. Combinations: rises to at least 5. Timing: rung 2 only. 50%.
**Scored F1** (`lab/v/frozen_curve_*.log`, the frozen design, fresh seeds 120000+): right. Sequences: highest solved 5, 11, 17, 17 at 560
to 4480 (300 s). Combinations (3000 s): rung 5 solved at 4480 (.67), every rung rising with material (2: .34 to .62, 3: .29 to .54, 4: .31
to .54, 6: .19 to .38), none surely solved below. Timing (3000 s): rung 2 solved from 1120 (.53 to .56); rungs 3, 5, 7 rise to .4-.5.

# The second held-out ladder (sealed, lab/sealed/heldout_ladder2.json; opened now, after freezing net10kc60S; held-out seeds 71000+;
the tree P 64 as reference; material 560 to 4480; each rung's own life)
H2. The frozen design solves at least one rung and rises with material on at least half the rungs. 40%.
**Scored H2** (`lab/v/heldout_ladder2.log`, held-out seeds 71000+): wrong. On the second sealed ladder the frozen design solves no rung:
rung 1 closes about .3 of the gap (raw +.84 to +1.05 on a gap of 3.5; the tree +.92), rungs 2 to 8 .17 to .34, flat with material
(no climb), above the tree on rungs 3, 4, 6 and 8 (tree .16 to -.09). The scaling test's second part is not met on a second unseen
ladder either. (The ladder read only now, after this verdict.)

# Development on the spent satiety ladder: running averages of every signal (arm net10kc60SA: the frozen design plus three averages of
each of the eyes, good tastes, bad tastes and each motor, time constants .5 to 30 s, read low, middle or high against their history).
Smoke (2 pairs): satiety 3 40 (frozen design 77); sequence 11 118 (86). Traced (one satiety-3 life): every stream predicts the food
colour about 80% of the time (the best, "outcome at each blue eaten", 81%); the good-meal averages (time constants 1.4, 10, 17 s; the
world's 21 s) are not among the best ten. Read as thirds of its own history, a leaky average doesn't mark the threshold (k recent
meals) that the rule turns on. Not run at scale; recorded as development, since the ladder is spent.
Beats since the food colour last changed, a count the world's changes reset (arm net10kc20SZ; smoke, 2 pairs, 3000 s): timing 3: 936
(975 without); 5: 883 (920); the gate sometimes follows a "since" stream, without gain. Parked; timing's open question stands.

# The steering grown, first build (lab/steer.py; G1-G2 of PROGRAMME.md's design): the starting circuit's drive removed; play tries
thruster 0, thruster 1, both or none in random trials; graded readouts of each eye's pulse change after each (context, option) pair
(the sixteen pairs present from birth); reflexes wired where an option surely raises the eye that matters against none.
Smokes (plain world, 300 s, three lives; last third; circuit 30, 39, 41): play 60 s, trials of .3 s: scans found (spinning on one
thruster raises that thruster's eye when nothing is seen), no approach: grown 0 food in the last third. Trials of .3 s are too short to
see straight-on approach raise an eye's rate (it rises only as the distance shrinks), while turning loses the block at once. Play 120 s,
trials 1 s: fewer trials (about six a pair), even fewer reflexes, grown 0 again. The evidence is the limit: in random play a block is in
view in few trials, and an approach shows only over a second or more.
Not run at scale. Next for the steering: keep learning the pairs during the whole life (not only in play), the creature's own driving
then supplying trials with a block in view; and judge an option by what follows over a longer horizon (the eye's rate over seconds, or
a taste), as the hand-built drive's hold does.
Lifelong (LIFELONG=1: after play every moment a trial, the best option so far in its context taken, another one time in ten): smokes
(three plain lives, last third) -5, 0, -5: no better. The value chased (an eye's rate within a second) is the wrong one: driving straight
pays when the block is reached, seconds later, at a taste; the hand-built drive solves this by holding its course (its hold timer). The
steering needs value over seconds: a taste credited back to the options that led to it (an eligibility trace), the growing network's
pairs carrying it. Parked for review.

# The eligibility trace (lab/steer.py, arm traced; the user: implement it, 2026-11-14): every .3 s a choice for the context (followed
eye, other eye, seen within the circuit's own hold); each (context, option) pair's mark fades over 3 s; a taste (+1, -1) credited to the
marked pairs; value = reward credited per use; best value chosen, untried first, random one time in ten (always in the first 60 s).
Smoke (three plain lives): in every life it learned by itself to go straight when the followed eye has just pulsed; in one life traced,
after play: followed eye seen, straight (.59 a use); nothing seen, spin on one thruster (.31, a scan); only the other colour seen, spin
away (.30); 38 good meals and 13 bad in 180 s. Last thirds 5, -4, -3 against the circuit's 30 to 41: it eats, but less and worse; it
never runs off to new places when bored, as the hand-built drive does.
E1. (plain world, 10 pairs, 300 s; circuit, traced, still) traced surely above still (0) and surely below the circuit. 80%.
**Scored E1** (`lab/v/steer_traced_plain.log`, 10 pairs): wrong in letter. traced +.07 [-.09, +.26] against the circuit's +2.36; still
eats nothing (its efficiency undefined, nothing spent). Not surely above zero: in most lives the trace finds "straight when the followed
eye has just pulsed" by itself (seven of the ten pairs' best options shown agree), but what it does with nothing in view (stand still,
spin, or go straight, by life) and with the other colour seen varies, and the food it finds barely covers its poison.

# Longer credit, two generic ways (the user: try both rigorously; lab/steer.py arms tracedM, tracedQ, tracedMQ)
M: marks at four time constants drawn per life (1 to 30 s), value the mean over them of credit per use. Q: "the followed eye starts
pulsing" (after a silence of the circuit's hold) an event with marks of its own, credited by tastes, paying its learned worth to the
pairs marked when it happens (secondary reinforcement). Checked: M's time constants and values do differ (one life: 1.5, 1.6, 6.6, 23 s);
in that life the options' ranking didn't, so its choices matched the single trace's.
Run: plain world, 300 s, 10 pairs, development seeds 131000+, paired on the same lives: circuit, traced, tracedM, tracedQ, tracedMQ.
L1. tracedM surely above traced. 40%. L2. tracedQ surely above traced. 45%. L3. the best of them surely above zero and within 1.0 of the
    circuit (+2.4). 25%.
**Scored L1-L3** (`lab/v/steer_credit.log`, development seeds 131000+, paired): all wrong. traced -.13 [-.34, +.07]; multiple traces
-.32 (-.19 against traced, [-.46, +.11]); the cue's learned worth -.24 (-.11, [-.49, +.26]); both -.32 (-.19). None better, none above
zero; the circuit +2.25. Which option each life ends up preferring varies widely (on these seeds even the approach is found in only
some). Likely starved of evidence: in 300 s a learner from scratch gets few tastes.
L4. (the same arms, lives four times as long, 1200 s, judged on the last third; 10 pairs, same seeds) traced and its variants improve
    with life (above their 300 s levels by .3 or more), and one is surely above zero. 45%.
**Scored L4** (`lab/v/steer_credit_long.log`, 1200 s): wrong. No improvement with life: traced +.04, multiple traces -.16, cue -.11, both
-.26 (circuit +2.39). Not starved of experience: stuck. Traced (two lives, 600 s): the colour followed is right all the time (so the
steering, not the colour, fails); most meals come from going straight with the followed colour in view (31 and 51), but most poison is
eaten with the other colour in view, where the trace learned "stand still" as least bad, turning away being blamed for poisons that come
seconds later (credit blurred by marks).
TD (SARSA, arm td: each pair moves towards the tastes since it began plus the discounted value of the next pair) learns to stand still
when nothing is in view (no taste, value 0: a trap); average-reward TD (AVGR=1, Schwartz 1993: each choice judged against the creature's
own running reward rate, so idling falls below the usual) smokes mixed.
L5. (1200 s, 10 pairs, seeds 131000+, paired; circuit, traced, td, td with AVGR as a separate run) TD or average-reward TD surely above
    traced. 35%.
**Scored L5** (`lab/v/steer_td.log`, `steer_td_avgr.log`, 1200 s, paired): wrong. TD -.03 [-.13, +.07], average-reward TD -.12 [-.23,
-.01], the trace +.04, the circuit +2.39. No credit rule tried (one trace, four traces, a learned cue, TD, average-reward TD) gets the
grown steering above zero. Parked for review.

# Options held while their context lasts (the user: build it, test every hypothesis; lab/steer.py arms opt, optN)
An option chosen when the context changes (or at a taste, or at random, mean 2 s) and held until then; the ended episode updates its pair
by semi-Markov TD: Q += .1 (R - rho d + Q(next) - Q); opt charges each episode its length at the creature's running reward rate (rho,
forgetting over 100 s); optN doesn't. First smoke: without random ending, standing still with nothing in view never ended (no choice
again): the idling trap. With it (three plain lives, 300 s, last third): opt 29, 30, 18 (the circuit 30 to 40 on such lives); optN -2, 4,
0. Learned in every opt life, nothing written: straight with the followed colour in view; with nothing in view a spin; with the other
colour, a spin away in two of three.
O1. (300 s, 10 pairs, seeds 131000+, paired) opt surely above traced and td. 75%.
O2. opt surely above optN: the duration charge is needed. 75%.
O3. opt within .5 of the circuit. 35%.
O4. (1200 s) opt's gap to the circuit narrower than at 300 s. 50%.
**Scored O1-O4** (`lab/v/steer_opt.log`, `steer_opt_long.log`, paired): O1 right: opt +.99 (300 s) and +1.27 (1200 s), above traced by
+1.12 [+.73, +1.47] and +1.24, above td by +1.21 and +1.30. O2 right: above optN by +.68 [+.42, +.93] and +.44 [+.11, +.79]. O3 wrong:
the circuit +2.25 and +2.39, opt about half. O4 right, narrowly: the gap -1.26 at 300 s, -1.11 at 1200 s.
Traced (two lives, after 400 s of 1200): opt 291 and 262 good meals, 75 and 65 bad; the circuit 466 and 404, 57 and 52. opt spends 22%
of its time with the other colour in view (turning away at the slow scan rate) and 16% with the followed one. The pairing of rate with
context (drive when the followed eye is seen, scan otherwise) is the last thing written by hand: opt8 lets each option carry either rate
(eight options), chosen like the rest.
O5. (300 and 1200 s, 10 pairs, paired) opt8 surely above opt. 45%.
**Scored O5** (`lab/v/steer_opt8*.log`): wrong. Options with their own rate: -.22 [-.60, +.18] (300 s) and -.16 [-.33, .00] (1200 s)
against opt: no gain; twice the choices to learn. The four-option version stays.
O6. Confirmation on fresh seeds 133000+ (1200 s, 10 pairs; circuit, traced, opt, optN): opt surely above traced and above optN. 70%.
**Scored O6** (`lab/v/steer_opt_fresh.log`, fresh seeds 133000+, 1200 s): right. opt +1.32 [+1.14, +1.50], above traced by +1.33
[+1.19, +1.47] and above optN by +.52 [+.23, +.80]; the circuit +2.47.

# G3: the growing network's choice of colour with grown steering (lab/steer.py arms net: net10kc60S with the hand-built drive; netopt:
the same with held options; opt: held options with the starting circuit's colour). Smoke (sequence 5, 1200 s, one life, last third): net
142, netopt 28, opt -8: the two grown halves work together, at a fifth of the network with the hand-built drive.
G3a. (sequences 5 and 11, 1200 s, 10 pairs, seeds 131000+, paired) netopt surely above opt and above the circuit on both. 60%.
G3b. netopt reaches at least a third of net's gain over the circuit. 40%.
**Scored G3a-G3b** (`lab/v/steer_g3_*.log`, 1200 s, paired): right. netopt above opt by +.66 [+.29, +1.01] (sequence 5) and +.35 [+.12,
+.60] (11), above the circuit by +2.58 and +2.11; it takes .64 and .58 of the network-with-hand-built-drive's gain over the circuit (net
+1.90 and +1.73, netopt +.46 and +.19). The grown rule and the grown steering work together; the shortfall is the steering's.
O7. Is the context too brief? "In view" lasts the circuit's hold (.17 s) after a pulse, so a distant block's sparse pulses keep ending
    the option. With in view lasting .5 s or 1 s (OPTW; plain, 1200 s, 10 pairs, seeds 131000+), opt surely higher. 45%.
**Scored O7** (`lab/v/steer_optw*.log`): wrong. Longer "in view" is worse: .5 s -.55 [-.75, -.36], 1 s -1.08 [-1.26, -.91] against the
hold (+1.27): a stale context blurs situations. The hold stays.
O8. Exploration costs a trained creature: EPS .1 for the whole life. Exploration fading with experience (each context's chance of a random
    option 1/sqrt(1 + its uses / 10); EXPL=fade) or a fixed .03 (EPS=0.03): opt surely higher than with .1. 45%.
**Scored O8** (`lab/v/steer_expl_fade.log`, `steer_eps03.log`): wrong. Fading exploration -.02 [-.18, +.15], a fixed .03 +.05 [-.09, +.19]:
exploration isn't what costs.
Traced (two lives, after 400 s): time by context, circuit / opt: nothing in view .55 / .55, followed colour .22 / .17, other .18 / .22,
both .05 / .06: nearly the same; the gap is in what is done there. The circuit runs off at its run rate when bored; opt has only the scan
and drive rates. opt12: each pattern at any of the circuit's three rates (scan, drive, run), twelve options, chosen like the rest.
O9. (1200 s, 10 pairs, seeds 131000+) opt12 surely above opt. 35%.
**Scored O9** (`lab/v/steer_opt12.log`): wrong. Twelve options -.24 [-.38, -.11] against four: like eight (O5), more choices cost more
learning. Neither the repertoire, the exploration, nor the context's length is the gap.
O10. On the muscle-like body (MUSCLE=1; the circuit with its frozen muscle retune, table.numbers), 1200 s, 10 pairs, seeds 131000+:
     opt's gap to the circuit smaller than on the original body (-1.11). 50%.
**Scored O10** (`lab/v/steer_opt_muscle.log`): right in letter. On the muscle body opt +.75, the retuned circuit +1.53: the gap -.78
(original body -1.11), but in proportion the same (about half).
O11. The hand-built drive without its muscle retune (circraw: as if the body changed after birth; the retune was found by search) on the
     muscle body, against opt (which adapts by itself): opt surely above circraw. 40%.
**Scored O11** (`lab/v/steer_opt_muscle_raw.log`; its report crashed for want of a circuit arm, the pairing done after): void as framed:
the frozen muscle retune (`lab/v/retune_muscle.json`) is all zeros (the search found nothing to change), so circraw is the circuit and
O10 already compared the learned steering with an untuned hand-built drive. On a body the drive was never tuned for, it still beats the
learned steering two to one (+1.53 against +.75).
O12. Finer contexts (optF: each eye's pulses within the hold counted none, one or several, a rough near and far; nine contexts instead of
     four): 1200 s, 10 pairs, seeds 131000+: surely above opt. 35%. (Smoke, one life, 300 s: last third 9.)
**Scored O12** (`lab/v/steer_optF.log`): wrong. Finer contexts -.63 [-.78, -.49]. Every added option or distinction has cost (O5, O9,
O12): the gap looks like the price of learning from scratch in one life.
O13. (4800 s, judged on the last third; 10 pairs, seeds 131000+) opt keeps rising with experience (300 s .99, 1200 s 1.27): above 1.5. 45%.
**Scored O13** (`lab/v/steer_opt_4800.log`): wrong. At 4800 s opt +1.25, as at 1200 s (+1.27): it has stopped learning, not run short.
The policies it settles on are the circuit's own (straight with the followed colour, spin with nothing, spin away from the other, in
most of the twenty lives); what the circuit has besides is time: bored (no food for its bored timer) it runs straight to somewhere new.
The options' contexts have no time in them, so "nothing in view" for a moment and for twenty seconds are one.
O14. Boredom as context (optB: a fifth bit, no followed-colour pulse or food for longer than the circuit's own bored timer): 1200 s, 10
     pairs, seeds 131000+: surely above opt. 50%.
Smoke (one life, 1200 s): optB last third 86 (efficiency 1.54); it learned by itself, bored with nothing in view: go straight (the circuit's run).
**Scored O14** (`lab/v/steer_optB.log`): wrong in letter: boredom as context +.10 [-.06, +.25] above opt (+1.37), not sure. A small part.
O15. (a diagnosis) The options machinery carrying out the circuit's own policy, forced (FORCE=1: nothing in view, spin on thruster 0;
     the followed colour, straight; the other or both, spin), no learning or play: if near the circuit (+2.4), the gap is what is learned;
     if near opt (+1.3), it is the machinery (episodes, random endings, rates). Expect: near the circuit. 55%.
**Scored O15** (`lab/v/steer_force.log`, diagnosis): wrong, and decisive. Carried out by the options machinery, the circuit's own policy
(forced, no learning) scores +.42, below the learned options (+1.27) and far below the circuit (+2.39): the gap is not in what is
learned. Checked and ruled out: the step's length (2.5 ms, as the circuit's), a balance between the thrusters (the circuit has none here).
Left: the circuit runs straight at its run rate when bored, the other colour in view or not.
O16. (diagnosis, FORCE=2: the forced policy with optB's bored contexts running straight at the run rate) near the circuit. 50%.
**Scored O16** (`lab/v/steer_force2.log`, diagnosis): partly. With running when bored, the circuit's policy forced through the options
machinery scores +1.65 (from +.42 without): relocation was most of the machinery's gap. Still -.73 below the circuit: the circuit's run
lasts at most its run_max (1 s), then scanning resumes for its bored time; here a bored run goes on until something is seen. The learned
version with boredom as context (optB, +1.37) reaches .83 of the forced policy: learning costs about a sixth; the rest is the circuit's
tuned timing (its scan-run rhythm), found by search, not learnable from these contexts.
O17. Contexts carrying time (optT: when the followed colour isn't in view, how long since it was last seen, under 1 s, 1-4, 4-16, over 16;
     beyond the first step options run at the run rate, a choice still learned): 1200 s, 10 pairs, seeds 131000+: surely above opt, and
     at least optB's +1.37. 45%.
**Scored O17** (`lab/v/steer_optT.log`): wrong. Contexts carrying time: +1.07, -.20 [-.48, +.10] against opt, -.30 [-.56, -.01] against
optB. Sixteen contexts split the evidence four ways where it mattered.
O18. Shared values (optTS: optT's sixteen contexts, each fine context's value pulled towards its coarse parent's until it has ten uses of
     its own; the parent learns from every episode): 1200 s, 10 pairs, seeds 131000+: surely above optT, and at least opt. 50%.
**Scored O18** (`lab/v/steer_optTS.log`): wrong. Shared values: +1.03, as optT (-.04 [-.33, +.25]), below opt (-.24 [-.44, -.09]). Sharing
didn't rescue the time contexts. (A confound noted: in optT and optTS every option beyond the first time step runs at the run rate, a
spin included; optB's single bored bit does the same; the rate mapping may be what costs, not the splitting.)
O19. The confound removed (NATRATE=1: time contexts' options at the scan rate, as plain opt's): optT and optTS at 1200 s, 10 pairs, seeds
     131000+. If the fast rate was what cost, both rise to at least opt's +1.27; if the splitting, they stay below. Expect: they rise. 45%.
**Scored O19** (`lab/v/steer_optT_natrate.log`): partly right, and a correction. Without the fast rate the time contexts tie opt (+1.35,
+.08 [-.09, +.24]): their earlier loss (O17) was the rate, not the splitting. Shared values still cost (-.20 [-.33, -.06]). So the "law"
(every added distinction costs) was partly the confound for the time contexts; it stands for the extra options (O5, O9) and the
pulse-count contexts (O12, whose rates were the circuit's), and for sharing as built.

## The habit space's ceiling (2026-11-14 evening, `lab/habits.py`)
H3. Screening all 256 forced habits (5 pairs, 300 s, seeds 132000+): the best is the circuit's own habit or its mirror (0200 / 1200 and
    variants differing only where it matters little, contexts 2 and 3). 55%.
H4. Re-judged (top 10, 10 pairs, 1200 s, seeds 131000+): the best forced habit without boredom within .2 of opt (+1.27): learning costs
    under .2 of the space's ceiling. 50%. With bored extensions: the best near the forced circuit-plus-run (+1.65), and above optB surely. 60%.

## The rhythm's settings learned (knobs first; `lab/steer.py` optK*, D64)
Bits: five settings (scan, drive and run rates, bored time, run length), each over a 16-fold range at a factor 1.41: 8 levels, 3 bits
each, 15 bits. Noise wall: an epoch of 20 s holds 3 to 8 meals (Poisson sd 2 to 3); a 1.41-fold change in one setting moves the meal rate
perhaps 5 to 10%, .3 to .6 meals; five settings perturbed at once share each pair's difference, so a pair carries a signal to noise of
about .1 per setting; a 4800 s life has 115 pairs after play, so about 1 (sd) of evidence per setting: barely enough to move from a bad
start, not to fine-tune. Taste only: the learner doesn't feel what its firings cost (a third of what it spends).
K1. (4800 s, 10 pairs, seeds 131000+) from random starts, tuned (optK) surely above the same starts untuned (optK0). 55%.
K2. From the circuit's values, tuned (optKw) ties untuned (optKw0): no gain, no harm. 60%.
K3. optKw0 (optB plus the circuit's run length) surely above optB. 50%.
**Scored H3** (`lab/v/habits_screen.log`, 6 min): partly. The best screened habits all go straight with the followed colour in view (2 in
the second place) and spin with nothing in view; but the circuit's own (0200) is not in the top 20: the best (1203, 0212) spin one way with
nothing in view and the other way, or stop, with the other colour in view. 5 pairs of 300 s lives are noisy (intervals .4 to .9 wide).
**Scored H4** (`lab/v/habits_top.log`, `habits_top10_10_1200s_bored.pkl`): first part about right (the best habit without boredom, 1203,
+1.49 against opt's +1.27: learning costs .22 of a ceiling of 1.49); second part wrong in the useful direction: with the bored contexts
the best forced habit (0203 2223: nothing in view spin, the followed colour straight, the other spin, both stop; bored, nothing in view,
straight at the run rate) scores +2.36 [+2.21, +2.54], the circuit's own level (+2.39). The habit space holds the circuit's performance;
the earlier forced version (FORCE=2, +1.65) differed in one choice (both colours in view: spin rather than stop). So D63's "the rest is
the circuit's tuned rhythm, not expressible" is wrong: the remaining gap (optB +1.37 against 2.36) is the cost of learning, a full 1.0.
In bits: the space is 4^6 (12 bits, contexts 5 and 7 never occur); the learner gets the followed colour (straight, 20 of 20) but the bored
choice (straight) in 10 of 20 lives and "both: stop" in 10 of 20. Suspect: the fixed step (ALPHA .1) keeps only the last ten or so
episodes' evidence in each value, so its noise never falls with experience (and the 4800 s plateau).
O20. Values as averages (optBn: each pair's step 1/n, floor .01, so a value keeps all its evidence): 1200 s, 10 pairs, seeds 131000+:
     surely above optB. 55%. And at 4800 s, higher than at 1200 s. 55%.
**Scored O20** (`lab/v/steer_optBn.log`): wrong. Averaged values -.20 [-.42, +.03]: early play's random episodes stay in the averages.
Per life (optB): lives ending on a habit whose forced score is 2.2 (0203 2_1_) score 1.1 to 1.6 in their last third, so the loss is not
mainly the final choice but how it is carried out while learning: exploration, or the habit flickering as values move.
O21. (diagnosis) optB greedy after play (EPS=0): if exploration is the cost, near the forced 2.2; if flicker, unchanged. Expect: unchanged
     (EPS .03 didn't move opt). 60%.
**Scored O21** (`lab/v/steer_optB_eps0.log`): right that exploration isn't the cost: greedy after play is worse (+1.15): some lives lock
into a bad habit (stop with nothing in view: 0.0). Lives ending on a good habit (0203 20__, forced 2.33) still score 1.7: the loss is in
how the habit changes over the life (flicker), measured next (the habit's changes over the last third, at 10 s looks).
Flicker measured (`lab/v/steer_optB_flicker.log`): the best option of some context changes 19 times in the last third's 40 looks (7 to
30): a fixed step .1 holds about 19 episodes' evidence per value (an average's effective count (2 - a)/a), too few to separate close
options, so the habit wanders and the life is spent half on worse habits.
O22. A step shrinking with each pair's uses after play (optBa: 1/(n + 10), floor .01): 1200 s, 10 pairs, seeds 131000+: surely above optB,
     and flicker at least halved. 55%.
**Scored O22** (`lab/v/steer_optBa.log`): wrong in its score, right in its flicker: a shrinking step cuts flicker 19 to 4, gains nothing
(+.01 [-.19, +.19]). Replay (`lab/v/habit_replay_optBa.log`, `lab/habit_replay.py`): each life's final habit forced on the same life
scores +1.35 against the learned +1.38: carrying out costs nothing; the whole loss is which habit is learned. The habits missed: "both in
view: stop" (3 of 20 lives) and the spin with nothing in view matching the spin with the other colour in view (sweeping on past it,
rather than back into it); both pay late (the next many seconds), so one-step credit (Q of the next episode only) can't see them.
O23. Credit reaching back over earlier episodes (optBl: SMDP TD(lambda) over options, lambda .5 and .8): 1200 s, 10 pairs, seeds
     131000+: at least one surely above optBa. 40%.
**Scored O23** (`lab/v/steer_optBl.log`): wrong. Credit over earlier episodes costs: lambda .5 -.48 [-.75, -.25], .8 -.67 [-.91, -.41]:
later episodes' noise swamps each choice's own effect.
O24. Habit search (optH: the values learn as optBa until 400 s; then the habit is fixed to their best, and one change at a time is tried
     in alternate 20 s epochs against it, kept when its mean difference in tastes beats twice its standard error over at least 3 pairs).
     Bits: a pair of epochs carries ~.4 bits on a big change, ~.05 on a small one; 1200 s leaves 20 pairs, so few changes are decided.
     1200 s, 10 pairs: ties optBa. 50%. 4800 s: surely above optBa at 4800 s. 45%.
**Scored O24** (`lab/v/steer_optH*.log`): first part right (1200 s: -.19 [-.41, +.05], a tie), second wrong (4800 s: -.02 [-.35, +.30]).
Single changes don't reach the best habit: its two late-paying choices interact (both in view stop pays only with bored straight: 0203
without the bored run scores .05, the worst of the screened top), so from most learned habits each change alone is neutral or worse, a
valley a one-change search can't cross. The good habit is a joint change of two choices: 4 x 4 = 16 pairs per two contexts, 15 pairs of
contexts, 240 joint changes, each needing several epoch pairs; out of reach of a life's evidence at this rate.

## Counting place in the cycle (step 3; D61's open question)
Bits: timing rung n needs the word (n bits), the brain's place in the cycle (log2 n bits, renewed whenever the count slips) and the slot
length (continuous). D61: told the slot length, the designed brain (which counts place) reaches .8; the growing brain told one clock's
slot length stays at .5, and counters on drifting clocks gave nothing (smoke). The clean diagnosis is both together.
T9. (diagnosis; TOLDT=1, clock 0 told the slot length; NCOUNT=1: that clock's beats counted modulo 2 to 8, each a stream; 10 pairs, 3000 s,
    seeds 107000+, 2240 units, the frozen design net10kc60S against itself with counters) rungs 3 and 5: counters surely above, by .15
    or more. If yes, place is the missing representation and the period is the remaining bits to learn; if no, the readout can't use a
    count. 45%.
**Scored K1-K3** (`lab/v/steer_knobs_4800.log`): all wrong. Tuning from random starts costs (-.22 [-.41, -.08]); from the circuit's values
it costs more (-.55 [-.69, -.43]); the run length alone ties (+.05 [-.02, +.11]). The settings random-walk: from the circuit's values they
end about 1 (log2) away, which is what a step of .1 over 115 pairs of pure noise gives (.1 x sqrt(115) = 1.07); scan and drive rates drift
up (+.7, +.5 on average: taste only, the firings' cost unfelt). The noise wall as estimated: about one standard deviation of evidence per
setting in a 4800 s life, so the steps follow noise. Knob tuning by perturbation is evidence-starved here; the settings' bits are
evolution's to supply, or a measurement's (D44: the stride measured by sweeps), not trial and error's.
**Scored T9** (`lab/v/timing_count_toldT.log`): wrong. Counters on the told clock: rung 3 .48 (without .51), rung 5 .46 (.49): no gain.
Traced (`lab/count_trace.py`, `lab/v/count_trace_3*.log`): by the life's second third each count sees a mix of colours (purity .67 for
rung 3, near chance), even with the count read from time since an anchor (.67). The clock is re-phased at every revealed change
(next beat half a period on), so its beats fall anywhere in a slot, and a taste in the slot's first part reads the count of the slot
before: the brain's place in the cycle (log2 n bits) is lost at each change. A place needs a phase that is never re-phased, read finely.
T10. (diagnosis; TOLDT=1, PHASES=1: a clock of a fifth of the told slot length, never re-phased, its beats counted modulo 5m for m = 2 to
     8, each a stream of 5m symbols: a place in a cycle of m slots, five bins a slot, as the designed brain's) rungs 3 and 5, 10 pairs,
     3000 s, seeds 107000+: surely above the frozen design, by .15 or more. 55%.
Smoke (one life, rung 3, 1500 s): last third 213 food-gain on 91.9 spent (2.32; the told brain 2.33); the trusted stream ph6.
**Scored T10** (`lab/v/timing_phase_toldT.log`, diagnosis): right, strongly. With a phase that is never re-phased (period told), the
frozen design closes .96 [.86, 1.09] and .91 [.84, .98] of the gap on rungs 3 and 5 (without: .51, .49; the designed brain told the slot
length .83, .78). Timing's plateau was the missing place in the cycle. What's left to learn is the period: the slot length (5 to 20 s) to
about a bin's worth over the stretch the readouts use, roughly 1%: log2(4 / .01) = 8.6 bits, against the revealed changes' timing.
T11. (generic: PHASES=2, six oscillators of drawn slot lengths 3 to 30 s, never jumped, drifting 1% a slot; at each revealed change each
     nudges its slot length a fifth toward the interval since the last change over its nearest whole number of slots (within 25%) and
     its phase .3 toward a slot's start; five bins a slot counted modulo 5m, m 2 to 8) rungs 3 and 5, 10 pairs, 3000 s, seeds 107000+:
     surely above the frozen design (.51, .49), and at least one solved. 45%.
**Scored T11** (`lab/v/timing_phase_pll.log`): wrong. Locking oscillators (gain .2, drift 1% a slot): .53 and .46, no gain. Traced
(`lab/osc_trace.py`, `lab/v/osc_trace_3.log`): few lock; the near ones 2% off. In bits: a revealed change marks a boundary only to within
the wait for the next taste (seconds), but a life's ~100 changes over ~250 slots fix the slot length to about .03% by a fit of them all;
a gain of .2 keeps only the last five intervals, and a drift of 1% a slot erases the rest.
Averaging (step 1/(n+2), floor .02; `lab/v/osc_trace_3_avg.log`): at drift 1% the nearest oscillators 1 to 4% off; at .1% drift four of
seven lives lock within .4% (two to .2%), and those lives trust the phase streams.
T12. (PLL_AVG=1, PDRIFT=.001; otherwise T11) rungs 3 and 5: surely above the frozen design. 50%. (How much a brain's clock may drift is a
     substrate's number, not yet the user's decision; 1% a slot was my choice for the clocks.)
**Scored T12** (`lab/v/timing_phase_avg.log`): wrong. Averaging oscillators at .1% drift: .50, .45, no gain, though traced lives lock.
T13. (diagnosis: TOLDT=1 TOLDT_AT=1000, PHASES=1: the told phase, but only from 1000 s; before, clock 0's own drawn period) If the
     readouts' tallies (never forgetting) are polluted by what the phase streams wrote before locking, rungs 3 and 5 stay near .5; if
     late locking is harmless, near T10's .9. Expect near .5. 60%.
**Scored T13** (`lab/v/timing_phase_late.log`, diagnosis): right. Told only from 1000 s, the phase barely helps (.54, .58 against .96,
.91 told from birth). Evidence from before a stream became right is never forgotten: the weighted majority halves a stream's weight at
each wrong guess (a stream wrong for 1000 s ends near 2^-300, unrecoverable), and the readouts' tallies keep every count.
T14. Fixed share among the speakers (WM_SHARE=.01: after each update, 1% of the speakers' weight returned to them evenly; Herbster &
     Warmuth 1998, tracking a best expert that changes) on the late-told diagnosis (T13's setting): rungs 3 and 5 surely above T13. 50%.
**Scored T14** (`lab/v/timing_phase_late_share.log`): right. With fixed share (.01) the late-told phase closes .90 [.78, 1.03] and .88
[.76, 1.01], both solved (without .54, .58; told from birth .96, .91). The weights were the block, not the tallies.
T15. (generic, nothing told: PHASES=2 PLL_AVG=1 PDRIFT=.001 WM_SHARE=.01) rungs 3 and 5 surely above the frozen design, and both
     solved. 50%.
**Scored T15** (`lab/v/timing_phase_generic.log`): wrong. Generic (averaging oscillators, .1% drift, fixed share): .53, .51.
Traced (`lab/phase_trace.py`, `lab/v/phase_trace_3.log`, last thirds of 3000 s lives): in 5 of 7 lives an oscillator locks (slot within
.1 to 3.5%) and its place tells the colour with purity .82 to .94 (no information .67); so the place is there, unused. Suspect: material.
Six oscillators x seven cycles add 42 streams; the fixed material (2240) split evenly leaves ~20 units a stream, against phase streams of
up to 40 symbols (T10 added 7 streams: ~30 units each).
T16. (T15 at 4480 units) rungs 3 and 5 surely above the frozen design at 4480. 50%.
**Scored T16** (`lab/v/timing_phase_generic_4480.log`): mostly wrong: at 4480 units rung 3 .59 (just solved), rung 5 .52. Not material.
Per life (`lab/v/phase_trace_3b.log`, rung 3, 3000 s, red): where a phase stream is the most trusted (3 of 7 lives) the last third's
gain is 295, 282, 246 against the frozen design's 258, 203, 249 and the told brain's 450, 248, 431: sometimes the told level, sometimes
none, though the place's purity is .83 to .94. A difference from the told phase: a correction pulling the phase back repeats bins (7, 8,
7, 8), breaking the regular sequence the network's contexts are built on.
T17. (T15 plus PMONO=1: a bin written only when the phase moves on past it) rungs 3 and 5 at 2240: surely above the frozen design. 40%.
**Scored T17** (`lab/v/timing_phase_mono.log`): wrong: .57, .54 (not surely above .51, .49).
T18. (bridge diagnosis: TOLDT=1 POSC_TOLD=1 PHN=1 PHASES=2 PMONO=1 WM_SHARE=.01: one locking oscillator told the slot length, its phase
     set by locking to the changes; seven phase streams as in T10) If near T10's .9, the period's estimate is what fails in the generic
     version; if near .5, the phase locking itself (jitter of the changes) spoils the place. 50/50.
**Scored T18** (`lab/v/timing_phase_bridge.log`, diagnosis): told the slot length, with the phase set by locking to the changes, .77
[.64, .89] and .84 [.72, .96], both solved: phase locking works; the generic failure is the period's estimate.
In bits: averaging intervals between successive changes (each error the difference of two noticing delays) throws information away;
the errors telescope, so the span since the first change over its whole number of slots has error ~(delay sd) / span: ~.1% after 250
slots, against ~1.5% for an average of 100 intervals.
T19. (generic: PLL_SPAN=1, PMONO=1, WM_SHARE=.01, PDRIFT=.001, six oscillators) rungs 3 and 5 surely above the frozen design, both
     solved. 50%.
**T19, traced instead of run** (`lab/v/phase_trace_3_span.log`): the span estimator (bootstrapped from ten averaged intervals) locks no
better (nearest 1.5 to 7% off in most lives; two lives .94, .95 purity late, still untrusted). In bits: a change is noticed only at the
next telling taste, seconds after the boundary, sometimes falsely; for slots of 5 to 20 s each change places a boundary only to a third
or half a slot, with outliers, so the whole number of slots in a span is often ambiguous. A robust estimator over all changes (a
resonator: the circular mean of change times at a trial period, tuned by its drift) is the next candidate. Open.
F2. Fixed share among the speakers (WM_SHARE=.01) on the frozen design, nothing else changed, fresh seeds 136000+, 10 pairs, 2240 units:
    sequences 11 (300 s), combinations 3 (3000 s), timing 2 (900 s): no rung surely worse; at least one surely better. 40%.
**Scored F2** (`lab/v/fshare_*.log`, fresh seeds 136000+): half right. Fixed share costs nothing anywhere: sequences 11 +.06 [-.04, +.16],
timing 2 +.06 [-.00, +.14], combinations 3 -.00 [-.10, +.11]; none surely better (timing 2 at the edge).
T20. (traced first) The resonator (PLL_RES=1 after ten averaged intervals: phase never moved, the rate corrected by the slide of the
     changes' forgetting circular mean): the best oscillator within .5% in most traced lives and purity above .85 in at least 4 of 7. 40%.
**Scored T20** (`lab/v/phase_trace_3_res.log`): wrong. The resonator (rate only, phase never nudged) is worse: even an oscillator .36% off
tells the colour at .69 (chance .67), since .36% slips a third of a slot over the last third's 80 slots. A place needs the phase held
too; the period line is parked here (D65, QUESTIONS.md).
F3. Fixed share on the two opened held-out ladders (development seeds 137000+, 10 pairs, 2240 units, every rung, its own life): on the
    first (hidden contexts) surely better on at least two rungs; on the second (satiety) no change (its rule needs a count no stream
    carries). 35%.
**Scored F3** (`lab/v/fshare_heldout*.log`, development seeds 137000+): wrong on the first ladder (no rung surely better; its gaps are so
small that rungs 1, 6 and 8 have intervals wider than 1), right on the second (no change, -.05 to +.06).
T21. (fresh-seed confirmation of T10, 138000+, paired: the frozen design with and without the told steady phase, rungs 3 and 5, 3000 s)
     the phase surely above on both. 85%.
**Scored T21** (`lab/v/timing_phase_toldT_fresh_paired.log`, fresh seeds 138000+): right. Told steady phase .93 [.84, 1.02] and .90
[.87, .95] against .50 and .42; paired +.43 [+.34, +.52] and +.49 [+.42, +.56].
S1. (development, the opened satiety ladder, seeds 137000+, 10 pairs, 2240, ACOUNT=1: running averages of every signal read as whole
    counts of recent events, 0 to 4+; arm net10kc60SA against net10kc60S, paired) surely better on at least two rungs. 35%.
**Scored S1** (`lab/v/satiety_counts.log`): wrong: no rung surely better (-.04 to +.04). Reading the opened ladder (now spent): the rule is
a leaky tally of meals of the food colour (recovery 3.6 to 9.6 s). The brain's averages covered eyes, good and bad tastes and motors,
not meals of each colour (a good-taste average mixes both colours), and were read at their own beats, up to 30 s stale.
S2. (ACOUNT=1 now also: a leaky count of meals of each colour, and every average's count written at each taste) on the same ladder and
    seeds: surely better on at least two rungs. 45%. Smoke (rung 1, 300 s, one life): trusts the red-meal count; last third +1 against -9
    (told 44).
**Scored S2** (`lab/v/satiety_counts2.log`): wrong: rung 4 +.06 [+.01, +.13], the rest within -.02 to +.03. A fault found in the build:
the counts were updated and written before the taste was learned from, so the brain learned "a context already counting this meal means
this colour", while at the moment of choosing the count hadn't included it. Moved to just after the learning.
S3. (S2 with the fault fixed) surely better on at least two rungs. 45%.
**Scored S3** (`lab/v/satiety_counts3.log`): wrong: +.06 at most (rung 1), none sure. Traced (`lab/count_purity.py`,
`lab/v/count_purity_1.log`, rung 1): at the time constant nearest the world's recovery, a colour's meal count tells the poison colour with
purity .8 to .9 (base rates .56 to .76) and is among the most trusted streams in 5 of 7 lives; the information is there and used, the gain
small. Suspect (untested): acting on it, steering to the other colour within the few seconds before recovery.
T22. (told steady phase, scaling) timing rung 7 (3000 s, 10 pairs, seeds 107000+) at 2240 and 4480 units: solved at 4480, and higher
     than at 2240. 45%.
**Scored T22** (`lab/v/timing_phase_toldT_r7.log`): half right. Rung 7 solved at both sizes (.90 [.79, 1.03] at 2240, .80 [.64, .93] at
4480); no climb with material (lower at 4480, not surely). Without the phase rung 7 rose only to about .5 (D61).
T23. (told steady phase, cycles up to 13 slots, PH_MAX=13) rungs 11 and 13 (3000 s, 10 pairs, seeds 107000+) at 2240 and 4480: at
     least one solved at 4480. 40%.
**Scored T23** (`lab/v/timing_phase_toldT_r11.log`): right. With the told phase (cycles to 13 slots) rungs 11 and 13 are solved at both
sizes: 11 1.00 [.88, 1.17] and .99 [.90, 1.12]; 13 .89 [.78, .96] and .91 [.85, .97]. Every timing rung tested (3 to 13) is solved once
the brain has a steady place in the cycle; the only part not grown is the slot length (about 8.6 bits).
T24. (fresh-seed confirmation of T14, 138000+, paired by seed across two runs: late-told phase with and without fixed share, rungs 3 and 5) fixed share surely above on both. 80%.
**Scored T24** (`lab/v/timing_late_share_fresh_paired.log`, fresh seeds 138000+): right. Phase told from 1000 s: with fixed share .83 and
.82, without .51 and .50; paired +.32 [+.21, +.43] and +.33 [+.25, +.42].

## Bits as the currency (the user, 2026-11-15: agreed; D67)
Each speaking stream predicts a probability (its unit's KT estimate, Krichevsky & Trofimov 1981); the default predicts from its own record
of the last letter repeating; the brain mixes the speakers by Bayes (weights times each one's probability for what happened, over the
speakers' mixture: sleeping experts, total kept), with fixed share .01; it chooses the colour more likely food. Each taste costs the brain
-log2 P(what happened) bits (prequential code length), and each stream's bits saved over the default are kept. Arm suffix B (net10kc60SFB).
Smoke (sequence 11, 300 s, one life): last third 29 against 10; .72 bits a taste over the life.
B1. Fresh seeds 139000+, 10 pairs, 2240, paired against net10kc60S: sequences 11 (300 s), combinations 3 (3000 s), timing 2 (900 s): no
    rung surely worse, at least one surely better. 45%. On the two opened held-out ladders (development seeds 137000+): no rung surely
    worse. 60%. And the brain's bits a taste fall rung by rung where the gap closed rises (the currency tracks the score). 70%.
The leaky-integrator bank (arm letter L; Shankar & Howard 2012): every event type (each eye's pulses, good and bad tastes, meals of each
colour, each motor's firings), integrators at 1, 4, 16 and 64 s, read at each taste (after learning) as a recent count on a log scale
(eight symbols), each a stream. Smoke (satiety rung 1, 300 s, one life): the blue-meal count at 4 s leads; last third -2 against 4,
.98 bits a taste against .87 (one life).
L1. (after B1; net10kc60SFBL against net10kc60SFB, paired, same seeds and ladders as B1) on the opened satiety ladder surely better on at
    least two rungs, and fewer bits a taste there; elsewhere no rung surely worse. 40%.
**Scored B1** (`lab/v/bayes_*.log`): mostly right. Bayes mixing ties the weighted majority: no rung surely worse (sequences 11 -.06
[-.12, +.02] at the edge); one surely better (held-out 1 rung 4, +.21 [+.03, +.40]); not one on the three main ladders. Bits a taste (the
brain's prequential code length, whole lives): combinations 3 .51, sequences 11 .65, timing 2 .63; the opened satiety ladder .77 to .87,
near the 1 bit of knowing nothing, where the gap closed is .2: the currency reads the brain's ignorance where the score does.
**Scored L1** (`lab/v/bank_*.log`): partly. The bank: held-out 1 rung 3 +.30 [+.08, +.53] surely, rung 6 +.46 [-.07, +1.71]; satiety rung 3
+.06 [+.01, +.10] surely, the rest ties; sequences 11 -.05, timing 2 +.04 (ties). Bits a taste on satiety fall only .00 to .04 (to .81 on
rung 1), though one meal-count stream alone (purity ~.85) would be worth ~.61 bits a taste: the information is there, not taken up.
L2. (trace, satiety rung 3, 7 lives, the bank brain) the best single stream in hindsight saves at least .1 bits a taste over the
    mixture: the loss is in the mixing, not the streams. 50%.
**Scored L2** (`lab/v/bits_split_sat3.log`, `lab/bits_split.py`): wrong. The mixture is within ~.02 bits a taste of the best single stream
in hindsight (default minus mixture .07 to .18; best stream's saving .09 to .21): Bayes mixing loses almost nothing. The best streams are
the bank's meal counts in 5 of 7 lives (lbc0/lbc1 at 4 or 16 s): the bank found the right memory by itself. The limit is what each stream
extracts: ~.15 to .2 bits a taste saved, with the brain at .64 to .92 bits a taste.

# D40: a context tree over registers. Predictions (main session, 2026-11-10), before any life

`lab/tree.py` through `lab/teach.py tree`, 5 pairs, the ladders' lives unchanged. The belief it could move: that one generic unit (a
node of a context tree), recruited on novelty beneath a contradiction, climbs the combination ladder, where nothing of ours does, and
the sequence ladder too, with no setting changed between them.

**The sums.** Material P is nodes, half to each of two trees (over the good-meal letters and over the colours eaten).
- Combo k needs the full tree of depth k: 2^(k+1) - 1 nodes. So P 16 holds k = 2, P 32 k = 3, P 64 k = 4, P 128 k = 5, P 256 k = 6.
- Time to grow it: a node at depth d is met every 2^d tastes, needs two or three visits to be contradicted and two or three more for
  its children: about 6 x 2^k tastes in all. Rung 3: 48 of a life's 195. Rung 4: 96 of 195, done only just before the last third. Rung 5:
  192 of 650. Rung 6: 384 of 650, too late for the last third to be clean.
- Seq n needs about 2n nodes and a depth of about 2 log2 n; about 6n good meals to grow, against 43 in a 100 s life and 130 in 300 s.
  So rung 5 (30) fits, 7 (42 of 43) is on the edge, 11 (66 of 130) fits, 17 (102 of 130) only just.
- The designed brains, told each rung's structure, reach x .60 to .81 on combo and .87 to .98 on seq.

Run: combo rungs 1, 3, 4, 5, 6 at P 16, 64, 256; seq rungs 1, 5, 11, 17 at P 16, 64, 256.
1. Combo 1 solved (surely above half at 5 pairs) at every P. 70%.
2. Combo 3 solved at P 64 and 256, not at 16 (7 nodes for a tree of 15). 55%; the failing at 16, 75%.
3. Combo 4 at P 64 and 256: x above .3, 60%; solved, 35%.
4. Combo 5 solved at P 256, not at 64. 40%. Combo 6 at P 256: not solved, 70%.
5. Seq 5 solved at P 64 and 256. 55%. Seq 11 solved at P 64 and 256, 40%. Seq 17, 25%.
6. Plain (seq 1): x not surely below 0. 75%: a tree that never gets ahead of the default is never followed.
7. The tree followed is `eaten` on combo and `good` on seq in most solved lives. 80%.
Least sure of: what the brain's own eating does to the contexts it meets (a good eater goes round a short cycle of histories, D37), and
guessed colours (untrusted tastes) spoiling contexts.

**Scored (`lab/v/tree_combo.log`, `tree_seq.log`; 5 pairs).**
- 6 right: plain exactly 0, 6 nodes used. 7 right: `eaten` followed on combo, `good` on seq.
- 5: seq 11 solved at P 64 and 256 (x .90, .93) and seq 17 at P 256 (.83, with 43 nodes; .36 at P 64): better than I expected (40%, 25%).
  Seq 5 not solved (.54 [.40, .68]): its 100 s life is too short for the growing, as the sum half said.
- 1 to 4, combo: x is .63 to .70 wherever the nodes suffice (rung 1 .67, 3 .68, 4 .55, 5 .70 at P 256, 6 .57), about the designed
  brain's .60 to .81, and it rises with material where the tree is big (rung 5: .44, .56, .70; rung 4: .20, .53, .55). But at 5 pairs
  none is surely above half (lower ends .06 to .47), so no prediction of "solved" is scored right. And rung 3 at P 16 was .63 with 8
  nodes for a tree of 15, where I predicted failure: a good eater meets only some of the histories.
So the picture is the predicted one, a little better on seq and unproven on combo. Combo's lives are noisy (its gaps come from few,
costly mistakes), and this is the claim stage 2 rests on, so it gets one larger run.

## Combo at 20 pairs. Prediction before its lives
8. Surely solved: rungs 1 and 3 at P 64 (70%); rungs 4 and 5 at P 256 (55%); rung 6 at P 256 not (65%).

**Scored 8 (`lab/v/tree_combo_20.log`, 20 pairs).** Rung 1 solved at every P (.67 to .68). Rung 3 solved at P 64 (.64 [.50, .72]). Rung 5
solved at P 256 (.70 [.58, .79]; .45 and .60 at P 16 and 64). Rung 6 solved at P 256 (.58 [.50, .65]; .31, .38 below), which I had
predicted it wouldn't be. Rung 4 not surely (.62 [.46, .74] at P 64). And more nodes than a rung needs cost a little: rungs 3 and 4 fall
from .64 and .62 at P 64 to .56 and .51 at P 256, the spare nodes growing on misreads and guessed colours.

## The tree with clocks: one design on all three ladders. Predictions before its lives
`lab/tree.py` treec: the same nodes and rules, with D39's bank of 60 clocks as a third kind of register (62 trees). P 992 gives each tree
16 nodes, P 1984 gives 32. 5 pairs. A word of n slots needs about 2n nodes and a depth of about 2 log2 n in the right clock's tree.
9. Time 2: x at or above .6 at both P. 65%.
10. Time 5: x at or above .5 at P 992 (D39's look-backs reached .63). 50%. Time 7 at P 1984: x above .4, 40%.
11. With the clocks beside them, the other ladders hold: seq 11 solved at P 1984 (70%); combo 3 at P 1984 x at or above .55 (60%).
12. Plain not surely below 0. 70%.
Least sure of: beats with no taste, whose letters are filled in by the tree's own guess, and 60 wrong clocks' trees competing with the right one.

**Scored 9-12 (`lab/v/treec.log`, 5 pairs).** 9 right, and better: time 2 at x .94 [.76, 1.17] at both P (the designed brain, told the
slot's length, has .82; D39's look-backs .74 to .83). 12 right: plain exactly 0, 6 nodes. 11 right: seq 11 solved (.89 [.80, .98]) and
combo 3 at .74 [.49, .92], each following its own register with 62 trees competing. 10 half right: time 5 at .42 and .45, short of the
.5 I gave even odds and of the look-backs' .63; time 7 at .34 and .51 [.10, .72]. Not yet traced: why the tree does better than
look-backs at rung 2 and worse at 5.

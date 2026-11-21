# D178 addendum 2 — stage 2 plan and predictions (written after stage 1, before any stage-2 run)

Budget estimate: transfer/omission replays 64 lives x 2 replays x 2 substrates ~ 1.5 min; motor-bias bench ~1 min;
grid 8 settings x 16 lives x 2 substrates + 1 x 48 lives x 2 ~ 2 min; knob-family replay screen 5 settings x 64 lives
~ 2 min, one closed-loop finalist (4 arms x 64 lives) ~ 1 min; analysis/writing ~40 min. Fits by 16:23.
Order (stage-1 branch: lower noise reduced movement): exploration explanation first.
1. R7 transfer.py on informed lives, silicon (primary) and biology (historical replication), omission 20% (i % 5 == 2).
2. R8.1 informed grid, silicon and biology: food {0.5,0.75,1.0} x poison {0,0.25,0.5} minus (0.5,0.5); screen seeds 0-7,
   rank by net_ft (food rate and stranding shown); selected point evaluated on 8-31 against nominal (1,0) there.
3. R8.2 one knob family chosen from R7 (decision written before its settings are run).
Predictions: in silicon, most stranded lives have both motors' own rates near zero (70%); omission shows a sensor's
pulse adds well under one motor spike on average (60%); units are heterogeneous (dead, reliable, oscillating) rather than
uniformly weak (80%). Grid: no setting reaches the +0.10 margin over nominal on 8-31 (65%): knob setting is not the
action bottleneck.

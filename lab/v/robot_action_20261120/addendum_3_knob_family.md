# D178 addendum 3 — R8 grid result and the single knob family (written before the family's settings are run)

Grid (R8.1, [grid_silicon.json](grid_silicon.json), [grid_biology.json](grid_biology.json), [grid_eval.json](grid_eval.json)):
screen winners (silicon food 1.0 / poison 0.5; biology 0.75 / 0.25) did not hold on seeds 8-31: selected - nominal
-0.05 [-0.22, +0.11] (silicon), +0.04 [-0.28, +0.36] (biology). The nominal setting is not shown to be poor.

Family chosen from R7 (transfer_informed_silicon.json): in silicon 35 of 64 informed lives have a motor with no own
firing, and the stage-1 branch puts exploration first. The family: the motor neurons' bias current (an existing
parameter, `Circuit.neuron(bias=...)`, both motors), predicted direction: less negative bias -> more own motor activity
-> fewer stranded lives. Operating region measured ([motor_bias_bench.json](motor_bias_bench.json), silicon, no input,
10 s, 64 motor units): own firing is all-or-none per unit: at -1.6 nA 58% silent, the rest at about 15-23/s; at
-1.5 / -1.45 / -1.4 / -1.3 nA, 50 / 41 / 38 / 28% silent, firing units at 15-23/s. No setting yields a low exploratory
rate: units jump from silent to fast firing (an onset at non-zero rate).
Frozen settings (SI): baseline -1.6 nA; -1.5, -1.45, -1.4, -1.3 nA.
Screen: identical-input replay of the 64 silicon informed lives (transfer.py with bias). Finalist rule: fewest lives
with a silent motor (own rate < 0.05/s); tie -> larger median incremental side-motor spikes per pulse. Finalist only
in closed loop: informed and all-food, silicon, seeds 0-31, paired with the baseline.
Predictions: the finalist reduces stranding (70%) but does not improve informed net_ft by the +0.10 lower bound (70%),
because fast own firing of one motor turns the body in circles rather than exploring (motor imbalance rises, 60%).

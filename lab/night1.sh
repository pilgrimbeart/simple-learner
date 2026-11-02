#!/bin/bash
# Step 3 night, stage 1: training seeds 0-15, lopsided, 10,000 s.
S=/home/pilgrim/git/simple-learner/lab
cd /home/pilgrim/git/simple-learner
export OMP_NUM_THREADS=1
P=".venv/bin/python $S/trick2.py"
$P plain 0:16
$P trick 0:16 eta=0.01
for s in 0.003 0.01 0.03 0.1; do $P trick 0:16 eta=0.01 sight=$s; done
$P trick 0:16 eta=0.01 sight=0.01 taste=0

#!/bin/bash
# Step 3 night, stage 2: the right detector planted; does each credit find it? Training seeds 0-15, 10,000 s.
S=/home/pilgrim/git/simple-learner/lab
cd /home/pilgrim/git/simple-learner
export OMP_NUM_THREADS=1
P=".venv/bin/python $S/trick2.py"
$P trick 0:16 eta=0.01 planted=1
$P trick 0:16 eta=0.01 sight=0.003 planted=1
$P trick 0:16 eta=0.01 sight=0.03 planted=1
$P trick 0:16 eta=0.01 sight=0.03 taste=0 planted=1
$P trick 0:16 eta=0.01 n=2 planted=1
$P trick 0:16 eta=0.01 n=2 sight=0.03 planted=1

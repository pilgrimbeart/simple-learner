#!/bin/bash
# Stage 9: explorers take turns (duty). Seeds 0-15, 10,000 s; the planted pair first, then planted among 50.
S=/home/pilgrim/git/simple-learner/lab
cd /home/pilgrim/git/simple-learner
export OMP_NUM_THREADS=1
P=".venv/bin/python $S/trick2.py"
B="burst=0.3 p0=0.05 charge=1 pmin=0.0 pmax=1.0"
for d in 0.1 0.3; do
  $P trick 0:16 n=2 planted=1 $B duty=$d eta=0.03
done
for d in 0.02 0.05; do
  $P trick 0:16 n=50 planted=1 $B duty=$d eta=0.03
  $P trick 0:16 n=50 planted=1 $B duty=$d eta=0.03 sight=0.03
done

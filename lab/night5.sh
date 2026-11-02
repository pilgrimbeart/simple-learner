#!/bin/bash
# Stage 5: one coin per burst (capped at 2 s); planted pair alone. Seeds 0-15, 10,000 s.
S=/home/pilgrim/git/simple-learner/lab
cd /home/pilgrim/git/simple-learner
export OMP_NUM_THREADS=1
P=".venv/bin/python $S/trick2.py"
$P trick 0:16 n=2 planted=1 burst=0.3 p0=0.5 learn=0
for b in "eta=0.01" "eta=0.03" "eta=0.01 sight=0.01" "eta=0.01 sight=0.03" "taste=0 sight=0.03"; do
  $P trick 0:16 n=2 planted=1 burst=0.3 p0=0.5 $b
done

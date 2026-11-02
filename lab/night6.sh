#!/bin/bash
# Stage 6: nothing planted: a random reservoir with burst coins. Seeds 0-15, 10,000 s.
S=/home/pilgrim/git/simple-learner/lab
cd /home/pilgrim/git/simple-learner
export OMP_NUM_THREADS=1
P=".venv/bin/python $S/trick2.py"
for n in 20 50 200; do
  for p0 in 0.05 0.2; do
    $P trick 0:16 n=$n burst=0.3 p0=$p0 eta=0.01 sight=0.01
  done
done
$P trick 0:16 n=50 burst=0.3 p0=0.2 eta=0.01

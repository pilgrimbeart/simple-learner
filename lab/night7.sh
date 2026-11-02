#!/bin/bash
# Stage 7: burst coins with each beat's cost charged to its detector. Seeds 0-15, 10,000 s.
S=/home/pilgrim/git/simple-learner/lab
cd /home/pilgrim/git/simple-learner
export OMP_NUM_THREADS=1
P=".venv/bin/python $S/trick2.py"
$P trick 0:16 n=2 planted=1 burst=0.3 p0=0.5 eta=0.01 sight=0.01 charge=1
for n in 20 200; do
  $P trick 0:16 n=$n burst=0.3 p0=0.05 eta=0.01 charge=1
  $P trick 0:16 n=$n burst=0.3 p0=0.05 eta=0.01 sight=0.01 charge=1
done
$P trick 0:16 n=200 burst=0.3 p0=0.05 eta=0.01 sight=0.01 charge=1 lam=10

#!/bin/bash
# Stage 11: poison weighed more; beats priced lower. n=50 planted, seeds 0-15, 10,000 s.
S=/home/pilgrim/git/simple-learner/lab
cd /home/pilgrim/git/simple-learner
export OMP_NUM_THREADS=1
P=".venv/bin/python $S/trick2.py"
B="burst=0.3 p0=0.0 charge=1 pmin=0.0 pmax=1.0 duty=0.05 eta=0.03 zthr=3 sight=0.03 n=50 planted=1"
for pv in 4 8; do
  for lam in 0.5 2; do
    $P trick 0:16 $B pv=$pv lam=$lam
  done
done

#!/bin/bash
# Stage 14: stage 12's learners with the evidence's noise scale fading (tau_v 10,000 s). Seeds 0-15.
S=/home/pilgrim/git/simple-learner/lab
cd /home/pilgrim/git/simple-learner
export OMP_NUM_THREADS=1
P=".venv/bin/python $S/trick2.py"
L="seconds=100000 judge=10000 seg=10000"
B="burst=0.3 p0=0.0 charge=1 lam=0.5 pmin=0.0 pmax=1.0 duty=0.01 eta=0.03 zthr=3 sight=0.03 tau_v=10000"
$P trick 0:16 $L $B n=2 planted=1
$P trick 0:16 $L $B n=50 planted=1
$P trick 0:16 $L $B n=50

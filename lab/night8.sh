#!/bin/bash
# Stage 8: forgetting. Seeds 0-15, 10,000 s.
S=/home/pilgrim/git/simple-learner/lab
cd /home/pilgrim/git/simple-learner
export OMP_NUM_THREADS=1
P=".venv/bin/python $S/trick2.py"
B="burst=0.3 p0=0.1 charge=1"
$P trick 0:16 n=2 planted=1 $B eta=0.01 tau_w=1000
for tw in 300 1000; do
  for e in 0.003 0.01; do
    $P trick 0:16 n=200 $B eta=$e tau_w=$tw
  done
done
$P trick 0:16 n=200 $B eta=0.01 tau_w=1000 sight=0.01
$P trick 0:16 n=20 $B eta=0.01 tau_w=1000

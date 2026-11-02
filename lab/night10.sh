#!/bin/bash
# Stage 10: turns, w free, exploit on clear evidence (zthr). Seeds 0-15, 10,000 s.
S=/home/pilgrim/git/simple-learner/lab
cd /home/pilgrim/git/simple-learner
export OMP_NUM_THREADS=1
P=".venv/bin/python $S/trick2.py"
B="burst=0.3 p0=0.0 charge=1 pmin=0.0 pmax=1.0 duty=0.05 eta=0.03"
$P trick 0:16 n=2 planted=1 $B zthr=2
for z in 2 3; do
  $P trick 0:16 n=50 planted=1 $B zthr=$z
  $P trick 0:16 n=50 planted=1 $B zthr=$z sight=0.03
done
$P trick 0:16 n=50 $B zthr=2

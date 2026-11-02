#!/bin/bash
# Stage 3: does the planted steer pay at all? One detector, learning off, fixed odds. Seeds 0-15, 2000 s.
S=/home/pilgrim/git/simple-learner/lab
cd /home/pilgrim/git/simple-learner
export OMP_NUM_THREADS=1
P=".venv/bin/python $S/trick2.py"
$P plain 0:16 seconds=2000
for p0 in 0.25 0.5 0.9; do
  $P trick 0:16 seconds=2000 n=1 learn=0 planted=1 p0=$p0 pmax=1
  $P trick 0:16 seconds=2000 n=1 learn=0 planted=-1 p0=$p0 pmax=1
done

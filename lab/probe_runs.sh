#!/bin/bash
S=/home/pilgrim/git/simple-learner/lab
cd /home/pilgrim/git/simple-learner
export OMP_NUM_THREADS=1
for pr in 6,0.5 12,0.5 24,0.5 12,1.0; do
  echo "== probe $pr"
  .venv/bin/python $S/timing.py seeds=32 probe=$pr 2>&1 | grep -v Warning
done

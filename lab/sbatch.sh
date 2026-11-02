#!/bin/bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
cd /home/pilgrim/git/simple-learner
P=.venv/bin/python; SEEDS=50000:50032
{ $P /home/pilgrim/git/simple-learner/lab/shadow.py holdfix $SEEDS
  $P /home/pilgrim/git/simple-learner/lab/shadow.py shadow $SEEDS
  $P /home/pilgrim/git/simple-learner/lab/ctune.py $SEEDS eta=0.01 hold_only=1; } 2>&1 | grep -v "^\s*$\|diff_b_a\|RuntimeWarning"
cp -a /home/pilgrim/git/simple-learner/lab/. ~/nca-scratch-backup/

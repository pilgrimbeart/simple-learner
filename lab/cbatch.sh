#!/bin/bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
cd /home/pilgrim/git/simple-learner
P=.venv/bin/python; C=/home/pilgrim/git/simple-learner/lab/ctune.py; SEEDS=50000:50032
for b in 0 1; do
  $P $C $SEEDS body=$b eta=0.005
  $P $C $SEEDS body=$b eta=0.003
done 2>&1 | grep -v "^\s*$\|diff_b_a\|RuntimeWarning"
cp -a /home/pilgrim/git/simple-learner/lab/. ~/nca-scratch-backup/

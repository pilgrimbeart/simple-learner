#!/bin/bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
cd /home/pilgrim/git/simple-learner
P=.venv/bin/python; T=/home/pilgrim/git/simple-learner/lab/trick.py; SEEDS=50000:50032
for b in 1 0; do
  $P $T plain $SEEDS body=$b
  $P $T trick $SEEDS body=$b p0=0.01 eta=0.01
done 2>&1 | grep -v "^\s*$\|diff_b_a\|RuntimeWarning"
cp -a /home/pilgrim/git/simple-learner/lab/. ~/nca-scratch-backup/

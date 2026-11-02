#!/bin/bash
# headroom: a faster balance by hand (held out); then the rate chosen honestly, on training seeds 0-31
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 LIVES=/home/pilgrim/git/simple-learner/lab/v/train
mkdir -p $LIVES
cd /home/pilgrim/git/simple-learner
P=".venv/bin/python -m discrete.tuner"
{ LIVES=/home/pilgrim/git/simple-learner/lab/v $P 50000:50032 body=1 eta=0.01 fbal=3
  LIVES=/home/pilgrim/git/simple-learner/lab/v $P 50000:50032 body=1 eta=0.01 fbal=10
  for b in 0 1; do for e in 0.003 0.005 0.01 0.02; do $P 0:32 body=$b eta=$e; done; done
  for b in 0 1; do $P 0:32 body=$b tune=0; done; } 2>&1 | grep -v "^\s*$\|diff_b_a\|RuntimeWarning"
cp -a /home/pilgrim/git/simple-learner/lab/. ~/nca-scratch-backup/

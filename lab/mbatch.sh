#!/bin/bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
cd /home/pilgrim/git/simple-learner; export LIVES=/home/pilgrim/git/simple-learner/lab/v
for b in 0 1; do for th in 0.002 0.0005; do
  .venv/bin/python -m discrete.tuner 50000:50032 body=$b meta=1 theta=$th lag=100
done; done 2>&1 | grep -v "^\s*$\|diff_b_a\|RuntimeWarning"
cp -a /home/pilgrim/git/simple-learner/lab/. ~/nca-scratch-backup/

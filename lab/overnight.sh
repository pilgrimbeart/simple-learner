#!/bin/bash
# The yardstick for self-tuning, overnight (2026-10-29): 32 held-out seeds x 2, lives of 10,000 s, one job at a time.
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
cd /home/pilgrim/git/simple-learner
P=.venv/bin/python; B=/home/pilgrim/git/simple-learner/lab/bo2.py; SEEDS=50000:50032
date
for body in 0 1; do
  $P $B floor $SEEDS body=$body
  $P $B ceiling $SEEDS body=$body
  $P $B bo $SEEDS body=$body beta=0.02
done
date
$P /home/pilgrim/git/simple-learner/lab/selftune.py $SEEDS seconds=10000 beta=0.02 delta=0.3 only=1
for body in 0 1; do
  for v in "W=20 beta=0.02" "W=80 beta=0.02" "beta=0"; do
    $P $B bo $SEEDS body=$body $v
  done
done
date
cp -a /home/pilgrim/git/simple-learner/lab/. ~/nca-scratch-backup/

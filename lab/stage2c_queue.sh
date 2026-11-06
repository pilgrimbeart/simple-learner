#!/bin/bash
# stage 2c's runs, one at a time (AGENTS.md: one job, one maths thread per worker)
cd /home/pilgrim/git/simple-learner
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
P=.venv/bin/python
$P lab/stage2c_guard.py > lab/v/stage2c_guard.log 2>&1
$P lab/stage2c_identity.py > lab/v/stage2c_identity.log 2>&1
$P lab/stage2c_dl.py > lab/v/stage2c_dl.log 2>&1
$P lab/stage2c_steps.py nine > lab/v/stage2c_nine.log 2>&1
$P lab/stage2c_steps.py halve > lab/v/stage2c_halve_run.log 2>&1
$P lab/stage2c_steps.py analyse > lab/v/stage2c_halve.log 2>&1
echo QUEUE DONE

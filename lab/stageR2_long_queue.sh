#!/bin/bash
# stageR2_long_queue.sh: after the PID given, stage R2's 1000 s lives, then their analysis.
cd /home/pilgrim/git/simple-learner
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
while [ -n "$1" ] && kill -0 "$1" 2>/dev/null; do sleep 30; done
echo "R2 long start $(date)" >> lab/v/stageR2_queue.log
.venv/bin/python lab/stageR2.py long > lab/v/stageR2_long_run.log 2>&1 || { echo "R2 long FAILED $(date)" >> lab/v/stageR2_queue.log; exit 1; }
.venv/bin/python lab/stageR2.py analyse_long > lab/v/stageR2_long.log 2>&1
echo "R2 long done $(date)" >> lab/v/stageR2_queue.log

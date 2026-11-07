#!/bin/bash
# stageR2_queue.sh: after the PID given (one job at a time), stage R2's lives, then its analysis.
cd /home/pilgrim/git/simple-learner
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
while [ -n "$1" ] && kill -0 "$1" 2>/dev/null; do sleep 30; done
echo "R2 start $(date)" > lab/v/stageR2_queue.log
.venv/bin/python lab/stageR2.py run > lab/v/stageR2_run.log 2>&1 || { echo "R2 FAILED $(date)" >> lab/v/stageR2_queue.log; exit 1; }
.venv/bin/python lab/stageR2.py analyse > lab/v/stageR2.log 2>&1
echo "R2 done $(date)" >> lab/v/stageR2_queue.log

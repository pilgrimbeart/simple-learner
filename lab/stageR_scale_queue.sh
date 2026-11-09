#!/bin/bash
# stageR_scale_queue.sh: after the PID given, stage R's 10,000 s scaling test, then its analysis.
cd /home/pilgrim/git/simple-learner
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
while [ -n "$1" ] && kill -0 "$1" 2>/dev/null; do sleep 30; done
echo "scale start $(date)" >> lab/v/stageR2_queue.log
.venv/bin/python lab/stageR_scale.py run > lab/v/stageR_scale_run.log 2>&1 || { echo "scale FAILED $(date)" >> lab/v/stageR2_queue.log; exit 1; }
.venv/bin/python lab/stageR_scale.py analyse > lab/v/stageR_scale.log 2>&1
echo "scale done $(date)" >> lab/v/stageR2_queue.log

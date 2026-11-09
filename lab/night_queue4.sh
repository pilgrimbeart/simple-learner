#!/bin/bash
# night_queue4.sh (night of 2026-11-08): after the PID given (night_queue3.sh), v9 on fresh seeds (lab/rprop_fresh9.py).
cd /home/pilgrim/git/simple-learner
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
log=lab/v/night_queue.log
while [ -n "$1" ] && kill -0 "$1" 2>/dev/null; do sleep 15; done
echo "v9 start $(date)" >> $log
.venv/bin/python lab/rprop_fresh9.py > lab/v/rprop_fresh9.log 2>&1 || echo "v9 FAILED $(date)" >> $log
echo "v9 done $(date)" >> $log

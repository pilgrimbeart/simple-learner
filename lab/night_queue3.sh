#!/bin/bash
# night_queue3.sh (night of 2026-11-08): after the PID given (night_queue2.sh), v7 firmed up: 20 more pairs of the double thruster, plain
# and nearly plain at 10,000 s (lab/rprop_fresh.py 7m).
cd /home/pilgrim/git/simple-learner
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
log=lab/v/night_queue.log
while [ -n "$1" ] && kill -0 "$1" 2>/dev/null; do sleep 15; done
echo "v7 more start $(date)" >> $log
.venv/bin/python lab/rprop_fresh.py 7m > lab/v/rprop_fresh7m.log 2>&1 || echo "v7 more FAILED $(date)" >> $log
echo "v7 more done $(date)" >> $log

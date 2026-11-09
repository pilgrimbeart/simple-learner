#!/bin/bash
# night_queue2.sh (night of 2026-11-08): after the PID given (night_queue.sh), stage 3's 100 s worlds with the cure named in lab/v/cure_choice.
cd /home/pilgrim/git/simple-learner
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
log=lab/v/night_queue.log
while [ -n "$1" ] && kill -0 "$1" 2>/dev/null; do sleep 15; done
cure=$(cat lab/v/cure_choice 2>/dev/null || echo v8)
echo "stage3 cure $cure start $(date)" >> $log
.venv/bin/python lab/stage3_cure.py run $cure > lab/v/stage3_cure_run.log 2>&1 || { echo "stage3 cure FAILED $(date)" >> $log; exit 1; }
.venv/bin/python lab/stage3_cure.py analyse > lab/v/stage3_cure.log 2>&1
echo "stage3 cure done $(date)" >> $log

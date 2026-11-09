#!/bin/bash
# night_queue.sh (night of 2026-11-08): after the PID given (v7's run), v8's tests, then the scaling test with the cure. The cure is
# the version named in lab/v/cure_choice (written after v8's results are read), v8 if none appears within 10 minutes. One job at a time.
cd /home/pilgrim/git/simple-learner
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
log=lab/v/night_queue.log
while [ -n "$1" ] && kill -0 "$1" 2>/dev/null; do sleep 15; done
echo "v8 start $(date)" >> $log
.venv/bin/python lab/rprop_fresh.py 8 > lab/v/rprop_fresh8.log 2>&1 || echo "v8 FAILED $(date)" >> $log
echo "v8 done $(date)" >> $log
for i in $(seq 60); do [ -f lab/v/cure_choice ] && break; sleep 10; done
cure=$(cat lab/v/cure_choice 2>/dev/null || echo v8)
echo "scale cure $cure start $(date)" >> $log
.venv/bin/python lab/stageR_scale_cure.py run $cure > lab/v/stageR_scale_cure_run.log 2>&1 || { echo "scale cure FAILED $(date)" >> $log; exit 1; }
.venv/bin/python lab/stageR_scale_cure.py analyse > lab/v/stageR_scale_cure.log 2>&1
echo "scale cure done $(date)" >> $log

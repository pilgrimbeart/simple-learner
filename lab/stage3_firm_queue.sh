#!/bin/bash
# stage3_firm_queue.sh: after the PID given (the job before, one job at a time), lab/stage3_firm.py's phases, then final.
cd /home/pilgrim/git/simple-learner
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
Q=lab/v/stage3_firm_queue.log
while [ -n "$1" ] && kill -0 "$1" 2>/dev/null; do sleep 30; done
for p in harm retest longref; do
  echo "phase $p start $(date)" >> $Q
  .venv/bin/python lab/stage3_firm.py $p > lab/v/stage3_firm_$p.log 2>&1 || { echo "phase $p FAILED $(date)" >> $Q; exit 1; }
  echo "phase $p done $(date)" >> $Q
done
.venv/bin/python lab/stage3_firm.py final > lab/v/stage3_firm.log 2>&1
echo "queue finished $(date)" >> $Q

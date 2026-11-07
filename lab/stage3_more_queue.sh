#!/bin/bash
cd /home/pilgrim/git/simple-learner
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
for ph in harm long topup; do
  .venv/bin/python lab/stage3_more.py $ph >> lab/v/stage3_more_$ph.log 2>&1 || { echo "phase $ph failed" >> lab/v/stage3_more_queue.log; exit 1; }
  echo "phase $ph done $(date)" >> lab/v/stage3_more_queue.log
  .venv/bin/python lab/stage3_more.py analyse > lab/v/stage3_more.log 2>&1
done
echo "queue finished $(date)" >> lab/v/stage3_more_queue.log

#!/bin/bash
# stage3_queue.sh: stage 3's phases in order (lab/stage3_random.py), one job at a time; logs in lab/v/stage3_*.log
cd /home/pilgrim/git/simple-learner
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
for ph in ${PHASES:-label main ref wires}; do
  .venv/bin/python lab/stage3_random.py $ph >> lab/v/stage3_$ph.log 2>&1 || { echo "phase $ph failed" >> lab/v/stage3_queue.log; exit 1; }
  echo "phase $ph done $(date)" >> lab/v/stage3_queue.log
done
.venv/bin/python lab/stage3_random.py analyse > lab/v/stage3_analyse.log 2>&1
echo "queue finished $(date)" >> lab/v/stage3_queue.log

#!/bin/bash
# stage 2a's remaining long jobs, one at a time, after stage2_run.py run
cd /home/pilgrim/git/simple-learner
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
until grep -qE "^done|Traceback" lab/v/stage2_run.log; do sleep 10; done
.venv/bin/python lab/stage2_label.py sens > lab/v/stage2_labels_sens.log 2>&1
.venv/bin/python lab/stage2_cost.py > lab/v/stage2_cost.log 2>&1
.venv/bin/python lab/stage2_checks.py finer > lab/v/stage2_finer.log 2>&1
echo queue finished >> lab/v/stage2_finer.log

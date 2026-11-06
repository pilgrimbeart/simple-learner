#!/bin/bash
# after the rerun of policies and tables: part 3's additions, part 5's correction. One maths thread per worker.
cd /home/pilgrim/git/simple-learner
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
while pgrep -f "^.venv/bin/python lab/stage1c_limit" >/dev/null; do sleep 10; done
.venv/bin/python lab/stage1c_late2.py > lab/v/stage1c_late2.log 2>&1
.venv/bin/python lab/stage1c_synth.py control > lab/v/stage1c_synth_control2.log 2>&1
.venv/bin/python lab/stage1c_synth.py gaming2 > lab/v/stage1c_synth_gaming2.log 2>&1
echo queue3 done

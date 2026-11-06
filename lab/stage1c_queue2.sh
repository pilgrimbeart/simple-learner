#!/bin/bash
# stage1c_queue2.sh: the rest of stage1c_queue.sh, from the changing-rule learners on, one maths thread per worker. Each pool worker had started 8 BLAS threads on 8 cores: 72.3 s against 1.4 s for the same lives, identical results.
cd /home/pilgrim/git/simple-learner
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
P=.venv/bin/python
for job in "change.py hmm:hmm" "limit.py oracle:limit_oracle" "limit.py policies:limit_policies" "limit.py tables:limit_tables" "synth.py control:synth_control" "synth.py table:synth_table" "synth.py gaming:synth_gaming" "synth.py nine:synth_nine"; do
  $P lab/stage1c_${job%%:*} > lab/v/stage1c_${job##*:}.log 2>&1
  echo "${job##*:} exit $? $(date +%H:%M)"
done
echo queue2 done

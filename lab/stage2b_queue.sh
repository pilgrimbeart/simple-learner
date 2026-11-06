cd /home/pilgrim/git/simple-learner
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
P=.venv/bin/python
$P lab/stage2b_dl.py > lab/v/stage2b_dl.log 2>&1
$P lab/stage2b_cells.py > lab/v/stage2b_cells.log 2>&1
$P lab/stage2b_random.py run > lab/v/stage2b_random_run.log 2>&1
$P lab/stage2b_random.py analyse > lab/v/stage2b_random.log 2>&1
$P lab/stage2b_neardup.py > lab/v/stage2b_neardup.log 2>&1
$P lab/stage2b_noharm.py > lab/v/stage2b_noharm.log 2>&1
$P lab/stage2b_cost.py > lab/v/stage2b_cost.log 2>&1
echo CHAIN DONE

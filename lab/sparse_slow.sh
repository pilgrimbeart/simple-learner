cd /home/pilgrim/git/simple-learner
S=/home/pilgrim/git/simple-learner/lab
export OMP_NUM_THREADS=1 LIVES=$S/v/sparse6
.venv/bin/python $S/sparse.py 6 0:32 mistune=3 eta=0.01 tau_r=60 wig=60 tau_b=600
.venv/bin/python $S/sparse.py 6 0:32 mistune=3 eta=0.01 tau_r=120 wig=120 tau_b=1200
.venv/bin/python $S/sparse.py 6 0:32 mistune=3 eta=0.003 tau_r=60 wig=60 tau_b=600

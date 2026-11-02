cd /home/pilgrim/git/simple-learner
S=/home/pilgrim/git/simple-learner/lab
export OMP_NUM_THREADS=1 LIVES=$S/v/sparse6
.venv/bin/python $S/sparse.py 6 0:32 mistune=3 tune=0
for e in 0.003 0.01 0.03; do .venv/bin/python $S/sparse.py 6 0:32 mistune=3 eta=$e; done

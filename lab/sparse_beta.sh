cd /home/pilgrim/git/simple-learner
S=/home/pilgrim/git/simple-learner/lab
export OMP_NUM_THREADS=1 LIVES=$S/v/sparse6
for b in 0 0.1 0.3; do .venv/bin/python $S/sparse.py 6 0:32 mistune=3 eta=0.01 beta=$b; done

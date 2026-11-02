cd /home/pilgrim/git/simple-learner
S=/home/pilgrim/git/simple-learner/lab
export OMP_NUM_THREADS=1
.venv/bin/python $S/periodbal.py fixed 0:32 body=0 g0=1.0001 g1=0.9999 sync=1
.venv/bin/python $S/periodbal.py oracle 0:32 body=1 sync=1

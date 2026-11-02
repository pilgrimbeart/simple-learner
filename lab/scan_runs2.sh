cd /home/pilgrim/git/simple-learner
S=/home/pilgrim/git/simple-learner/lab
export OMP_NUM_THREADS=1
.venv/bin/python $S/periodbal.py learn 0:32 body=1 scan_skip=0.5 scan_min=1 scan_rate=1
.venv/bin/python $S/periodbal.py learn 0:32 body=1 scan_rate=1

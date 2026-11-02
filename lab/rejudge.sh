cd /home/pilgrim/git/simple-learner
S=/home/pilgrim/git/simple-learner/lab
export OMP_NUM_THREADS=1 LIVES=$S/v
.venv/bin/python $S/drivebal.py learn 50000:50032 N=1000 eta=0.03 sync=1
.venv/bin/python -m discrete.tuner 50000:50032 seconds=2000 body=1 mistune=1 sync=1
.venv/bin/python -m discrete.tuner 50000:50032 seconds=2000 body=1 mistune=1

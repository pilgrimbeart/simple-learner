cd /home/pilgrim/git/simple-learner
S=/home/pilgrim/git/simple-learner/lab
export OMP_NUM_THREADS=1
C="cal_every=32 cal_len=8 stall=0.05 stall_need=3000 gate=8 bank=96 local=1 binary=1"
.venv/bin/python $S/periodbal.py learn 0:32 body=1 $C
.venv/bin/python $S/periodbal.py learn 0:32 body=1 allbody=1 $C

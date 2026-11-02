cd /home/pilgrim/git/simple-learner
S=/home/pilgrim/git/simple-learner/lab
export OMP_NUM_THREADS=1
C="body=1 cal_every=32 cal_len=8 stall=0.05 stall_need=3000 gate=8 bank=96 local=1"
.venv/bin/python $S/periodbal.py learn 0:32 $C plain=1
.venv/bin/python $S/periodbal.py learn 50000:50032 $C
.venv/bin/python $S/periodbal.py learn 50000:50032 $C allbody=1
.venv/bin/python $S/periodbal.py learn 50000:50032 body=0 cal_every=32 cal_len=8 stall=0.05 stall_need=3000 gate=8 bank=96 local=1

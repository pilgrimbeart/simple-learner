cd /home/pilgrim/git/simple-learner
S=/home/pilgrim/git/simple-learner/lab
export OMP_NUM_THREADS=1
C="cal_every=32 cal_len=8 stall=0.05 stall_need=3000"
.venv/bin/python $S/periodbal.py learn 0:32 body=0 $C gate=8
.venv/bin/python $S/periodbal.py learn 0:32 body=1 $C gate=8
for g in 6 8 10; do .venv/bin/python $S/periodbal.py learn 0:32 body=1 allbody=1 $C gate=$g; done

cd /home/pilgrim/git/simple-learner
S=/home/pilgrim/git/simple-learner/lab
export OMP_NUM_THREADS=1
C="body=1 cal_every=32 cal_len=8 stall=0.05 stall_need=3000 gate=8"
.venv/bin/python $S/periodbal.py learn 0:32 $C bank=96 local=1
.venv/bin/python $S/periodbal.py learn 0:32 $C bank=96 local=1 wide=0.5
.venv/bin/python $S/periodbal.py learn 0:32 $C bank=128 local=1
.venv/bin/python $S/periodbal.py learn 0:32 $C bank=96 allbody=1

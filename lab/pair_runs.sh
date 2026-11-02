cd /home/pilgrim/git/simple-learner
S=/home/pilgrim/git/simple-learner/lab
export OMP_NUM_THREADS=1
.venv/bin/python $S/periodbal.py fixed 0:32 body=0 g0=1.0001 g1=0.9999 paired=1
.venv/bin/python $S/periodbal.py oracle 0:32 body=1 paired=1
.venv/bin/python $S/periodbal.py oracle 0:32 body=1
C="cal_every=32 cal_len=8 stall=0.05 stall_need=3000 gate=8 gate_rate=1 cal_first=0 cal_fast=12 paired=1"
.venv/bin/python $S/periodbal.py learn 0:32 body=1 $C
.venv/bin/python $S/periodbal.py learn 0:32 body=0 $C

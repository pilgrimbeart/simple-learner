cd /home/pilgrim/git/simple-learner
S=/home/pilgrim/git/simple-learner/lab
export OMP_NUM_THREADS=1
C="body=1 cal_every=32 cal_len=8 stall=0.05 stall_need=3000 gate=8"
.venv/bin/python $S/periodbal.py learn 0:32 $C cal_first=0
.venv/bin/python $S/periodbal.py learn 0:32 $C cal_first=0 cal_fast=12
.venv/bin/python $S/periodbal.py learn 0:32 $C cal_first=0 cal_fast=16 fast_need=2000
.venv/bin/python $S/periodbal.py learn 0:32 body=0 cal_every=32 cal_len=8 stall=0.05 stall_need=3000 gate=8 cal_first=0 cal_fast=12

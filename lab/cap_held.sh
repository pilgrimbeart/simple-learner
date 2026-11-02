cd /home/pilgrim/git/simple-learner
S=/home/pilgrim/git/simple-learner/lab
export OMP_NUM_THREADS=1
C="cal_every=32 cal_len=8 stall=0.05 stall_need=3000 gate=8 gate_rate=1 cal_first=0 cal_fast=12 sync=1 bank=96 local=1 binary=1 cap=1"
.venv/bin/python $S/periodbal.py learn 50000:50032 body=1 $C
.venv/bin/python $S/periodbal.py learn 50000:50032 body=1 allbody=1 $C
.venv/bin/python $S/periodbal.py learn 50000:50032 body=0 $C
# attribution, training seeds: one-bit stages without the early sweeps, with and without sync
O="cal_every=32 cal_len=8 stall=0.05 stall_need=3000 gate=8 bank=96 local=1 binary=1 cap=1"
.venv/bin/python $S/periodbal.py learn 0:32 body=1 $O sync=1
.venv/bin/python $S/periodbal.py learn 0:32 body=1 $O gate_rate=1 cal_first=0 cal_fast=12

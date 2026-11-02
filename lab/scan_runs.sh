cd /home/pilgrim/git/simple-learner
S=/home/pilgrim/git/simple-learner/lab
export OMP_NUM_THREADS=1
.venv/bin/python $S/periodbal.py learn 0:32 body=1 scan_skip=0.5 scan_min=1
.venv/bin/python $S/periodbal.py learn 0:32 body=1 scan_skip=0.3 scan_min=2
.venv/bin/python $S/periodbal.py learn 0:32 body=1 cal_every=32 cal_len=8 stall=0.05 stall_need=3000 gate=8 gate_rate=1 cal_first=0 cal_fast=12 scans=1 scan_skip=0.5 scan_min=1

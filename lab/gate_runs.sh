cd /home/pilgrim/git/simple-learner
S=/home/pilgrim/git/simple-learner/lab
export OMP_NUM_THREADS=1
for g in 6 10; do for b in 0 1; do
  .venv/bin/python $S/periodbal.py learn 0:32 body=$b cal_every=32 cal_len=8 stall=0.05 stall_need=3000 gate=$g
done; done
.venv/bin/python $S/periodbal.py fixed 0:32 body=0
.venv/bin/python $S/periodbal.py fixed 0:32 body=1
.venv/bin/python $S/periodbal.py learn 0:32 body=1 cal_every=32 cal_len=8 stall=0.05 stall_need=3000

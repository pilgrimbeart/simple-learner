cd /home/pilgrim/git/simple-learner
S=/home/pilgrim/git/simple-learner/lab
export OMP_NUM_THREADS=1
C="body=1 cal_every=32 cal_len=8 stall=0.05 stall_need=3000 gate=8"
for K in 32 48 64 96; do .venv/bin/python $S/periodbal.py learn 0:32 $C bank=$K; done
for K in 48 64; do .venv/bin/python $S/periodbal.py learn 0:32 $C bank=$K local=1; done

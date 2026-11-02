cd /home/pilgrim/git/simple-learner/lab
P=/home/pilgrim/git/simple-learner/.venv/bin/python
export OMP_NUM_THREADS=1
echo "== pursuit (arenas 0-15)"
for m in left right both; do for d in 0.2 0.5; do echo "-- $m $d"; $P pursuit.py 0:16 mode=$m dur=$d | tail -1; done; done
echo "== alert (arenas 0-15)"
for m in run still; do for T in 3 10; do echo "-- $m $T"; $P alert.py 0:16 mode=$m T=$T | tail -1; done; done

cd /home/pilgrim/git/simple-learner/lab
P=/home/pilgrim/git/simple-learner/.venv/bin/python
export OMP_NUM_THREADS=1
echo "== escape grower vs the tuned tracker (scan x2, hold x0.5), held out"
$P grow_escape.py 100:148 knob=1 w0=0 t_scan=2 t_hold=0.5 | tail -4
$P grow_escape.py 100:148 knob=1 w0=-2 t_scan=2 t_hold=0.5 | tail -4
$P grow_escape.py 100:148 knob=1 w0=0 phantom=1 t_scan=2 t_hold=0.5 | tail -2

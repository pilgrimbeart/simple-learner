cd /home/pilgrim/git/simple-learner/lab
P=/home/pilgrim/git/simple-learner/.venv/bin/python
export OMP_NUM_THREADS=1
echo "== scripted, beats added (held out 100-147)"
for m in left right both; do echo "-- $m"; $P escape.py 100:148 mode=$m add=1; done
echo "== grower, two knobs (held out)"
$P grow_escape.py 100:148 knob=1 w0=0
$P grow_escape.py 100:148 knob=1 w0=-2
echo "== control: phantom pain"
$P grow_escape.py 100:148 knob=1 w0=0 phantom=1

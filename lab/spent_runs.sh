cd /home/pilgrim/git/simple-learner/lab
P=/home/pilgrim/git/simple-learner/.venv/bin/python
export OMP_NUM_THREADS=1
echo "== firings charged. escape scripted, held out"
for m in left both; do $P escape.py 100:148 mode=$m add=1 | tail -1; done
echo "== escape grower and control, held out"
$P grow_escape.py 100:148 knob=1 w0=0 | tail -2
$P grow_escape.py 100:148 knob=1 w0=0 phantom=1 | tail -2
echo "== pursuit, beats added, timed vs random (0-15)"
$P pursuit.py 0:16 mode=both dur=0.5 add=1 | tail -1
$P pursuit.py 0:16 mode=both dur=0.5 add=1 prand=0.8 | tail -1
echo "== keep moving always, keep still always (0-15)"
$P alert.py 0:16 mode=run always=1 | tail -1
$P alert.py 0:16 mode=still always=1 | tail -1

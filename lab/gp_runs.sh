cd /home/pilgrim/git/simple-learner/lab
P=/home/pilgrim/git/simple-learner/.venv/bin/python
export OMP_NUM_THREADS=1
echo "== scripted ceiling, beats added (arenas 0-15)"
$P pursuit.py 0:16 mode=both dur=0.5 add=1 | tail -1
$P pursuit.py 0:16 mode=both dur=0.5 add=1 prand=0.8 | tail -1
echo "== pursuit grower (arenas 0-15)"
$P grow_pursuit.py 0:16 w0=-2
$P grow_pursuit.py 0:16 w0=0

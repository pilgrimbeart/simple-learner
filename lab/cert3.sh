cd /home/pilgrim/git/simple-learner/lab
P=/home/pilgrim/git/simple-learner/.venv/bin/python
export OMP_NUM_THREADS=1
echo "== pursuit control: bursts at random, the bite-end rate"
$P pursuit.py 0:16 mode=both dur=0.5 prand=0.8
echo "== alert still control: at random, the bite-end rate"
$P alert.py 0:16 mode=still T=10 prand=1.0
echo "== pursuit, held out, real vs random"
$P pursuit.py 100:148 mode=both dur=0.5
$P pursuit.py 100:148 mode=both dur=0.5 prand=0.8

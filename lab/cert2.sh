cd /home/pilgrim/git/simple-learner/lab
P=/home/pilgrim/git/simple-learner/.venv/bin/python
export OMP_NUM_THREADS=1
echo "== alert, with rates"
$P alert.py 0:16 mode=run T=10
$P alert.py 0:16 mode=still T=10
echo "== alert controls: always"
$P alert.py 0:16 mode=run always=1
$P alert.py 0:16 mode=still always=1
echo "== pursuit both 0.5, with rates"
$P pursuit.py 0:16 mode=both dur=0.5

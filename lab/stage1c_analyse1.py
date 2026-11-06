"""stage1c_analyse1.py: 1b's sums (lab/bits_analyse.py, unchanged) on the fresh streams 62000-62399 x 2.
    .venv/bin/python lab/stage1c_analyse1.py"""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np
import bits_analyse as A
import stage1c_arms as Arms
A.D = Arms.OUT
np.set_printoptions(precision=3, suppress=True)
bank, pinned = A.load("bank", 62000), A.load("pinned", 62000)
A.budget(bank)
A.rates(A.load("right", 62000), A.load("wrong", 62000))
cal = A.calibration(bank)
A.shadow(bank, pinned)
A.efficiency_table(bank, pinned)
A.rule(bank, pinned, cal)

#!/bin/bash
# Stage 13: does the fixed right steer still pay in 100,000 s lives (judged on the last 10,000 s)? Seeds 0-15.
S=/home/pilgrim/git/simple-learner/lab
cd /home/pilgrim/git/simple-learner
export OMP_NUM_THREADS=1
P=".venv/bin/python $S/trick2.py"
L="seconds=100000 judge=10000 seg=10000"
$P trick 0:16 $L n=1 learn=0 planted=1 p0=0.9 pmax=1
$P trick 0:16 $L n=1 learn=0 planted=1 p0=0.9 pmax=1 burst=0.3
$P trick 0:16 $L n=1 learn=0 planted=-1 p0=0.9 pmax=1 burst=0.3

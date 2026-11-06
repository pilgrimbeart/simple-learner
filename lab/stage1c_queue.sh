#!/bin/bash
# stage1c_queue.sh: stage 1c's long jobs, one at a time, each to its own log, after part 1. A failure is logged and the next goes on.
cd /home/pilgrim/git/simple-learner
P=.venv/bin/python
busy() { pgrep -f "^.venv/bin/python lab/stage1c_(replicate|analyse1)" >/dev/null; }
while busy; do sleep 20; done; sleep 30; while busy; do sleep 20; done
$P lab/stage1c_change.py replay  > lab/v/stage1c_fs_replay.log 2>&1
$P lab/stage1c_change.py fslives > lab/v/stage1c_fs_lives.log 2>&1
$P lab/stage1c_late.py           > lab/v/stage1c_late.log 2>&1
$P lab/stage1c_late.py tally     > lab/v/stage1c_late_tally.log 2>&1
$P lab/stage1c_change.py hmm     > lab/v/stage1c_hmm.log 2>&1
$P lab/stage1c_limit.py oracle   > lab/v/stage1c_limit_oracle.log 2>&1
$P lab/stage1c_limit.py policies > lab/v/stage1c_limit_policies.log 2>&1
$P lab/stage1c_limit.py tables   > lab/v/stage1c_limit_tables.log 2>&1
$P lab/stage1c_synth.py control  > lab/v/stage1c_synth_control.log 2>&1
$P lab/stage1c_synth.py table    > lab/v/stage1c_synth_table.log 2>&1
$P lab/stage1c_synth.py gaming   > lab/v/stage1c_synth_gaming.log 2>&1
$P lab/stage1c_synth.py nine     > lab/v/stage1c_synth_nine.log 2>&1
echo queue done

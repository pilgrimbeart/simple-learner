#!/bin/bash
# The four checks on a clean checkout of the commit, in a fresh venv; push only if they pass. Silent unless it fails.
REPO=/home/pilgrim/git/simple-learner
SP=/home/pilgrim/git/simple-learner/lab
SHA=$(git -C $REPO rev-parse HEAD)
WT=$SP/ci-$SHA; VENV=$SP/ci-venv-$SHA
fail() { echo "FAILED: $1"; git -C $REPO worktree remove --force $WT 2>/dev/null; rm -rf $VENV; exit 1; }
git -C $REPO worktree add --detach $WT $SHA >/dev/null 2>&1 || fail "worktree"
/usr/bin/python3 -m venv $VENV && $VENV/bin/pip install -q -r $WT/requirements.txt || fail "venv"
cd $WT
for step in test_rules.py test_compiled.py "-m minimal.test_minimal" "-m discrete.test_model"; do
  $VENV/bin/python $step > $SP/ci-step.log 2>&1 || { tail -30 $SP/ci-step.log; fail "python $step"; }
done
cd $REPO
git push -q 2>&1 || fail "push"
git -C $REPO worktree remove --force $WT; rm -rf $VENV
echo "ok"

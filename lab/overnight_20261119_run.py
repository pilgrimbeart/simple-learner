"""Single-job, bounded launcher for NEW overnight scripts; never rewrites an old run.
Use: .venv/bin/python lab/overnight_20261119_run.py TASK TIMEOUT_SECONDS SCRIPT
"""
import argparse,fcntl,json,os,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'lab/v/overnight_20261119'
def main():
    p=argparse.ArgumentParser();p.add_argument('task');p.add_argument('timeout',type=int);p.add_argument('script');a=p.parse_args()
    if not a.task.replace('_','').isalnum():raise ValueError('Use an alphanumeric task name')
    if not 1<=a.timeout<=2400:raise ValueError('Per-job timeout must be 1..2400 seconds')
    script=(ROOT/a.script).resolve()
    if script.parent!=ROOT/'lab/overnight_20261119' or script.suffix!='.py':raise ValueError('Only new scripts in lab/overnight_20261119 may be run')
    OUT.mkdir(exist_ok=True)
    with (OUT/'compute.lock').open('a') as lock:
      try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
      except BlockingIOError:raise RuntimeError('Another overnight job holds the lock; do not bypass it')
      run=OUT/a.task;run.mkdir()  # An existing task directory is never silently reused.
      env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
      cmd=[str(ROOT/'.venv/bin/python'),str(script)];start=time.time()
      with (run/'stdout.log').open('x') as log:
        child=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
        state=dict(task=a.task,command=cmd,pid=child.pid,start_unix_s=start,timeout_s=a.timeout,status='running')
        (run/'start.json').write_text(json.dumps(state,indent=2)+'\n');print(json.dumps(state),flush=True)
        try:
            code=child.wait(timeout=a.timeout);status='complete' if code==0 else 'failed'
        except (subprocess.TimeoutExpired,KeyboardInterrupt) as exc:
            status='timed_out' if isinstance(exc,subprocess.TimeoutExpired) else 'interrupted'
            child.terminate()
            try:code=child.wait(timeout=10)
            except subprocess.TimeoutExpired:child.kill();code=child.wait()
        state.update(status=status,exit_code=code,elapsed_s=time.time()-start)
        (run/'finish.json').write_text(json.dumps(state,indent=2)+'\n');print(json.dumps(state),flush=True)
      return 0 if status=='complete' else 1
if __name__=='__main__':raise SystemExit(main())

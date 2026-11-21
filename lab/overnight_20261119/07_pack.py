"""Task G (overnight 2026-11-19): index every overnight output with its size and hash; list files over 1 MiB.
The morning report itself is written by hand from these outputs.
"""
import hashlib,json,platform,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'lab/v/overnight_20261119';HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    files=[];large=[]
    for p in sorted(BASE.rglob('*')):
        if not p.is_file() or p.name in('result_index.json','large_artifacts.json') or p.name=='compute.lock':continue
        if 'packaging' in p.parts:continue
        item=dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=sha(p));files.append(item)
        if item['bytes']>1<<20:large.append(dict(absolute_path=str(p.resolve()),bytes=item['bytes'],sha256=item['sha256']))
    scripts={str(p.relative_to(ROOT)):sha(p) for p in sorted(HERE.glob('*.py'))+[HERE/'matrix.json',ROOT/'lab/overnight_20261119_support.py',ROOT/'lab/overnight_20261119_run.py',ROOT/'lab/overnight_20261119_preflight.py',ROOT/'lab/overnight_20261119_inputs.json',ROOT/'lab/OVERNIGHT_WORK_ORDER_2026-11-19.md']}
    runs={}
    for d in sorted(BASE.iterdir()):
        if d.is_dir() and (d/'finish.json').exists():runs[d.name]=json.loads((d/'finish.json').read_text())
        elif d.is_dir() and (d/'start.json').exists():runs[d.name]=dict(json.loads((d/'start.json').read_text()),status='no finish record')
    import numpy
    env=dict(python=platform.python_version(),numpy=numpy.__version__,revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())
    try:
        import numba;env['numba']=numba.__version__
    except Exception as e:env['numba']=f'unavailable: {e}'
    idx=dict(environment=env,scripts_sha256=scripts,runs=runs,files=files)
    (BASE/'result_index.json').write_text(json.dumps(idx,indent=2)+'\n');(BASE/'large_artifacts.json').write_text(json.dumps(large,indent=2)+'\n')
    print(json.dumps(dict(files=len(files),large=large,runs={k:v.get('status') for k,v in runs.items()},environment=env),indent=2))
if __name__=='__main__':main()

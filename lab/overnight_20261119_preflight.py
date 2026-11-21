"""Read-only frozen-input preflight for the overnight work order; optional new audit file."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'lab'))
from overnight_20261119_support import self_check
MANIFEST=ROOT/'lab/overnight_20261119_inputs.json'
def main():
    p=argparse.ArgumentParser();p.add_argument('--output');args=p.parse_args()
    manifest=json.loads(MANIFEST.read_text());fail=[]
    for rel,expected in manifest['files'].items():
        path=ROOT/rel
        if not path.is_file():fail.append({'path':rel,'error':'missing'});continue
        actual=hashlib.sha256(path.read_bytes()).hexdigest()
        if actual!=expected['sha256']:fail.append({'path':rel,'error':'hash_changed'})
    counts={}
    for rel,n in manifest['record_counts'].items():
        path=ROOT/rel
        if not path.is_file():continue
        rows=[json.loads(l) for l in path.read_text().splitlines()] if path.suffix=='.jsonl' else json.loads(path.read_text())
        counts[rel]=len(rows)
        if len(rows)!=n:fail.append({'path':rel,'error':'wrong_record_count','expected':n,'actual':len(rows)})
    import numpy,numba
    result=dict(passed=not fail,failures=fail,checked_files=len(manifest['files']),record_counts=counts,
        helper_checks=self_check(),python=sys.version.split()[0],numpy=numpy.__version__,numba=numba.__version__,
        frozen_revision=manifest['revision'],current_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        note='A dirty worktree is expected. Content hashes, not cleanliness or revision alone, protect scientific inputs.')
    if args.output:
        target=Path(args.output).resolve()
        if not target.is_relative_to(ROOT/'lab/v'):raise ValueError('Audit output must be under lab/v')
        target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result,indent=2));return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())

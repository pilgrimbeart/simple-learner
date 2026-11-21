"""Write lab/v/shared_readout_20261120/index.json last: sha256 of every final output and script, excluding itself."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'lab/v/shared_readout_20261120'
files=sorted([p for p in (ROOT/'lab/shared_readout_20261120').glob('*.py')]+[p for p in OUT.rglob('*') if p.is_file() and p.name!='index.json'])
ix={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(OUT/'index.json').write_text(json.dumps(ix,indent=1)+'\n');print(len(ix),'files indexed')

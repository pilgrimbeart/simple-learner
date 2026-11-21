"""D154 source-review manifest, not an executable proof about all macro compositions."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'lab/v/routing_contract_audit';out.mkdir(exist_ok=True)
    ranges={'mixed_feedback.py':[[82,150],[225,240]],'chip.py':[[1,38]],'minimal/spice.py':[[198,267]],'PARTS.md':[[65,108]]}
    data=dict(revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        source_review={name:dict(sha256=hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),line_ranges=lines) for name,lines in ranges.items()},
        conclusion='No direct reciprocal conductance or dynamically swapped differential input contract. Composite impossibility not established. No simulator or circuit change.',
        scope='Read-only source review; line ranges refer to recorded content hashes; dirty documentation and lab work remain.')
    (out/'audit.json').write_text(json.dumps(data,indent=2)+'\n')
    print(data['conclusion'])
if __name__=='__main__':main()

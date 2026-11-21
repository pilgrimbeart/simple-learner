"""Audit D155-D156 provenance and retain the contradictory knob constraints."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,digest
from order_balance_information import bounds
OUT=ROOT/'lab/v/order_balance_review'
def main():
    OUT.mkdir(exist_ok=True);verified=[]
    for directory in ['order_balance_information','order_local_calibration']:
        p=ROOT/'lab/v'/directory;prov=json.loads((p/'provenance.json').read_text())
        for name,h in prov['files'].items():assert digest(ROOT/name)==h,name
        assert digest(p/'protocol.json')==prov['protocol_sha256'];verified.append(directory)
        rows=json.loads((p/'rows.json').read_text());assert len(rows)==5440
        assert len({(r['seed'],r['mode'],r['case']['id']) for r in rows})==5440
    p=ROOT/'lab/v/order_balance_information';draws=json.loads((p/'draws.json').read_text());rows=json.loads((p/'branches.json').read_text());conflicts=[]
    for d in draws:
        if d['feasible_order']:continue
        active=[]
        for r in rows:
            if r['seed']!=d['seed']:continue
            lo,hi=bounds(r['case']);a,b=sorted([(lo-r['u_V'])/r['v_V'],(hi-r['u_V'])/r['v_V']])
            if abs(a-d['feasible_interval'][0])<1e-10:active.append(dict(case=r['case'],requires_d_greater_than=a))
            if abs(b-d['feasible_interval'][1])<1e-10:active.append(dict(case=r['case'],requires_d_less_than=b))
        conflicts.append(dict(seed=d['seed'],constraints=active))
    assert len(conflicts)==1 and len(conflicts[0]['constraints'])==2
    report=dict(verified=verified,scored_rows_each=5440,conflicts=conflicts,script_sha256=digest(Path(__file__)))
    (OUT/'audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()

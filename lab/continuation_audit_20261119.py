"""Review D141-D153 provenance, denominators and explicit unresolved outcomes."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'lab/v/continuation_20261119'
DIRECTORIES=['phase_baseline','phase_gate_diagnosis','phase_signed_drift','phase_drift_feedthrough','signed_control',
    'signed_control_diagnosis','filter_state_audit','signed_control_zero','calibration_error_floor','partial_calibration','correction_cell_budget','shared_path_reversal','reversal_own_error']
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(rel):return json.loads((ROOT/'lab/v'/rel).read_text())
def main():
    OUT.mkdir(exist_ok=True);verified=[];late=[]
    for directory in DIRECTORIES:
        paths=list((ROOT/'lab/v'/directory).glob('*provenance*.json'));assert paths,directory
        for path in paths:
            p=json.loads(path.read_text())
            for name,h in p['files'].items():assert digest(ROOT/name)==h,(directory,name)
            protocol=path.parent/'protocol.json'
            if 'protocol_sha256' in p:assert digest(protocol)==p['protocol_sha256'],directory
            else:late.append(dict(directory=directory,protocol_hash_at_review=digest(protocol),note='No protocol hash in original provenance; this review does not backdate one.'))
            verified.append(str(path.relative_to(ROOT)))
    counts={'phase_baseline/rows.json':2880,'phase_gate_diagnosis/rows.json':3840,'phase_signed_drift/rows.json':960,
        'phase_drift_feedthrough/rows.json':320,'signed_control_diagnosis/original_predictions.json':1000,
        'filter_state_audit/trace.json':20,'signed_control_zero/rows.json':6000,'calibration_error_floor/rows.json':200,'partial_calibration/rows.json':600,'shared_path_reversal/rows.json':1000,'reversal_own_error/rows.json':80}
    for rel,n in counts.items():assert len(read(rel))==n,(rel,n)
    pilot=read('signed_control/pilot.json');confirm=read('signed_control/confirm.json')
    assert pilot['passed']==8 and pilot['control_pass'] and pilot['refinement_pass']
    assert confirm['passed']==39 and confirm['failed_seeds']==[2026113011] and not confirm['reliability_pass'] and confirm['refinement_pass']
    failures=[g for g in confirm['groups'] if g['failures']];assert len(failures)==3
    for g in failures:
        assert len(g['failures'])==1 and g['failures'][0][:3]==['sign',-.15,.15]
    for stage,n in [('pilot',1200),('confirm',3000)]:
        rows=[json.loads(l) for l in (ROOT/f'lab/v/signed_control/{stage}.jsonl').read_text().splitlines()]
        assert len(rows)==n and len({(r['seed'],r['dt'],r['case']['id'],r['control']) for r in rows})==n
    manifest=read('signed_control/manifest.json');assert sum(manifest['parts'].values())==234
    assert read('signed_control/confirm_audit.json')['saved_trace_max_error_V']==0
    assert 'Live saved-trace replay completed' in (ROOT/'lab/v/signed_control_report.log').read_text()
    filter_result=read('filter_state_audit/summary.json');assert filter_result['filter_exactly_constant']
    assert sum(v['connections'] for v in filter_result['witness_protocols'].values())==34
    assert all(not v['positive_tau'] for v in filter_result['witness_protocols'].values())
    partial=read('partial_calibration/summary.json');assert partial['comparisons']['0.5']['conditional_expected_RMS_V']<partial['comparisons']['1.0']['conditional_expected_RMS_V']
    assert partial['gaussian_reference_information_bits']==.5
    # Preserve large local artifacts by absolute path and content hash; do not put their bytes into git.
    big=[]
    for directory in DIRECTORIES+['phase_gate_diagnosis_serialization_failure']:
        for p in (ROOT/'lab/v'/directory).glob('*'):
            if p.is_file() and (p.suffix=='.npz' or p.stat().st_size>1024*1024):
                big.append(dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=digest(p)))
    result=dict(verified_provenance=verified,protocol_hash_limitations=late,row_counts=counts,
        signed_control='39/40: frozen reliability failed; pilot controls/refinements and saved-trace audit pass; live replay completed',
        calibration='Conditional expected errors only; no physical calibration demonstrated',large_local_artifacts=big,script_sha256=digest(Path(__file__)))
    (OUT/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'Checked {len(verified)} final provenance records, all declared row counts, signed-control failure, live replay, filter gap, and conditional calibration claims. {len(big)} large local artifacts hashed.')
    print('Protocol hashes absent at original recording:',','.join(r['directory'] for r in late) or 'none')
if __name__=='__main__':main()

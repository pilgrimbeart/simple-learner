"""Recompute the D126 verdict from complete per-seed rows; write a compact reviewable report."""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import OUT, DT, definitions, interval, summary, digest
from dynamic_parts_view import manifest


def main():
    proto=json.loads((OUT/'protocol_v2.json').read_text())
    stored=json.loads((OUT/'confirm_v2.json').read_text())
    rows=[json.loads(line) for line in (OUT/'confirm_v2.jsonl').read_text().splitlines()]
    keys=[(r['name'],r['seed'],r['dt']) for r in rows]
    expected={(name,seed,dt) for name in definitions() for seed in proto['confirm_seeds'] for dt in proto['steps']}
    assert len(keys)==len(set(keys)) and set(keys)==expected
    assert all(not r['control'] for r in rows)
    assert stored['protocol_sha256']==digest(OUT/'protocol_v2.json')
    computed=summary(rows,proto['confirm_seeds'])
    assert computed==stored['summary']
    pilot=json.loads((OUT/'pilot_v2.json').read_text())
    assert all(s['control_passed'] for s in pilot['summary'].values())
    material=manifest(); details={}
    text=['# First four dynamic circuit witnesses — D126', '',
          'Silicon-noise bench results with component mismatch. These are component tests, not robot learning.', '',
          '| Circuit | Fresh seeds passing all 3 steps | Wilson 95% interval | Both refinements | Mean core power, 95% bootstrap | States / connections | Verdict |',
          '|---|---:|---|---|---|---|---|']
    for name,s in computed.items():
        lo,hi=s['wilson95']; p,pl,ph=np.array(s['power_W'])*1e9
        m=material[name]; verdict='demonstrated within this protocol' if s['demonstrated'] else 'unresolved under this protocol'
        text.append(f'| {name} | {s["successes"]}/{s["n"]} | {lo:.3f}–{hi:.3f} | {s["refinement_passed"]} | {p:.4g} nW [{pl:.4g}, {ph:.4g}] | {m["states"]} / {m["connections"]} | {verdict} |')
        rr=[r for r in rows if r['name']==name and r['dt']==DT/4]
        numeric={}
        for key,value in rr[0]['metrics']['values'].items():
            if isinstance(value,(float,int)):
                vals=[r['metrics']['values'][key] for r in rr]
                numeric[key]=dict(mean_ci95=interval(vals),min=min(vals),max=max(vals))
        max_refinement=max(max(abs(v[1]),abs(v[2])) for half in s['refinement'].values() for v in half.values())
        valid=[r for r in rr if r['metrics']['passed']]
        if name=='oscillator':
            numeric['frequency_interpretation']='Raw crossing counts on the 3 failed sub-mV traces measure noise, not rhythm. Frozen metrics retained; use the explicitly conditional successful subset below.'
            numeric['successful_frequency_Hz']=dict(n=len(valid),denominator=len(rr),mean_ci95=interval([r['metrics']['values']['frequency_Hz'] for r in valid]))
        details[name]=dict(metrics=numeric,physical_core_parts=m['counts'],max_refinement_interval_absolute=max_refinement)
    text+=['', 'Each seed is a separate component-tolerance draw. Its three timestep evaluations are paired, not three independent seeds.',
           'The threshold is a Wilson lower bound of 0.90; the 40/40 outcome supports a lower bound of about 0.912, not universal reliability.',
           'Removal controls passed on the eight pilot seeds. Core power excludes external bench stimulation and recording equipment.', '',
           '## What changed after the first pilot', '',
           'All original graphs/settings were retained. A gentler, longer programming pulse removed memory rail overdrive.',
           'The resonator criterion changed explicitly from a peak at the exact nominal frequency to a measured interior peak,',
           'with a denser fixed frequency grid. This confirms frequency selection, not immunity of frequency to mismatch.',
           'The oscillator removal check was corrected to measure fluctuation rather than static voltage offset.',
           'The initial protocol, source snapshot, results and diagnosis remain alongside the revised files.', '',
           '## Oscillator failure diagnosis', '',
           'All three failed draws settle near stable fixed points. Replaying with noise and analysing the local mean-drift Jacobian',
           'finds eigenvalue real parts between -5.85 and -6.61 per second. This explains decay toward rest, not a sustained cycle.',
           'The tiny voltage fluctuations yield noise crossings; their raw crossing rates are not oscillation frequencies.',
           'Diagnosis: `oscillator_failure_diagnosis_v2.json`; script: `lab/dynamic_parts_failure.py`.', '',
           '## Reproduction and limits', '',
           'Frozen specification: `protocol_v2.json`; all rows: `confirm_v2.jsonl`; provenance and file hashes: `confirm_provenance_v2.json`.',
           'Run `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/dynamic_parts_bench.py confirm` from the repository.',
           'The runner refuses to overwrite existing results; archive the result files deliberately before a separate replication.',
           'View `confirm_replay.html` or run `lab/dynamic_parts_view.py --stage confirm --live-seconds 15` with that Python.',
           'No engine/noise edits, internal filtered channels, biological-noise claim, SPICE validation or body/interface change.',
           'Retained nonvolatile memory and controlled writes remain untested. The bit here is actively held bistable state.',
           'Source analysis: `lab/dynamic_parts_report.py`; full numeric detail: `confirm_detail_v2.json`.']
    (OUT/'report.md').write_text('\n'.join(text)+'\n')
    (OUT/'confirm_detail_v2.json').write_text(json.dumps(details,indent=2)+'\n')
    print('\n'.join(text[:12]))
    print('Independent completeness and summary reconstruction passed:',len(rows),'rows')


if __name__=='__main__': main()

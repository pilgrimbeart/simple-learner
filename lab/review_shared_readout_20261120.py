"""D171: read-only arithmetic audit of D170 artifacts; no simulator imports.
Run from the repository root; stdout is the review artifact.
"""
import hashlib
import json
import math
import statistics
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'lab/v/shared_readout_20261120'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

result = {'scope': 'saved-record audit, not simulation replication',
          'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
          'script_sha256': digest(Path(__file__)), 'hash_checks': {}}
for filename, key in [('index.json', None), ('manifest_addendum_pre_replay.json', 'files')]:
    entries = json.loads((BASE / filename).read_text())
    if key:
        entries = entries[key]
    failures = []
    for name, expected in entries.items():
        path = ROOT / name
        actual = digest(path) if path.exists() else None
        if actual != expected:
            failures.append({'path': name, 'expected': expected, 'actual': actual})
    result['hash_checks'][filename] = {'checked': len(entries), 'failures': failures}

records = [json.loads(line) for line in (BASE / 'replay/records.jsonl').read_text().splitlines()]
groups = defaultdict(dict)
for row in records:
    assert len(row['case_pass']) == 34
    assert sum(row['case_pass']) == row['passed']
    assert all(row['case_pass']) == row['all_pass']
    name = row['point'] + '|' + row['arm']
    assert row['seed'] not in groups[name]
    groups[name][row['seed']] = row
assert len(records) == 280
result['groups'] = {}
for name, rows in groups.items():
    assert len(rows) == 40
    summary = {'draws': sum(r['all_pass'] for r in rows.values()),
               'cases': sum(r['passed'] for r in rows.values())}
    values = [r['eps_vs_offline_final_third_1000s_mV'] for r in rows.values()
              if 'eps_vs_offline_final_third_1000s_mV' in r]
    if values:
        summary['equivalent_error_rms_mV'] = math.sqrt(statistics.mean(x*x for x in values))
    result['groups'][name] = summary

fixed = groups['none|fixed']
result['paired'] = {}
for name in ['P1_native|shared', 'P2_preamp|shared']:
    rows = groups[name]
    rescues = [s for s in rows if rows[s]['all_pass'] and not fixed[s]['all_pass']]
    harms = [s for s in rows if fixed[s]['all_pass'] and not rows[s]['all_pass']]
    failures = [s for s in rows if not rows[s]['all_pass']]
    result['paired'][name] = {'rescues': rescues, 'harms': harms, 'failures': failures,
        'settling_seconds_rescued': [rows[s]['calibration_delay_s'] for s in rescues]}
    assert len(rescues) == 5 and not harms and failures == [2026112215]

result['inputs'] = {str(p.relative_to(ROOT)): digest(p) for p in
                    [BASE/'index.json', BASE/'manifest_addendum_pre_replay.json', BASE/'replay/records.jsonl']}
print(json.dumps(result, indent=2))

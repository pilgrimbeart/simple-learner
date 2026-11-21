"""Saved-summary arithmetic/provenance review only; no simulation or raw-trace replication."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'lab/v/robot_shortfall_20261120'

def read(name):
    return json.loads((OUT / name).read_text())

checks = []
for line in (OUT / 'provenance.log').read_text().splitlines()[1:]:
    fields = line.split(maxsplit=1)
    if len(fields) != 2 or len(fields[0]) != 64:
        continue
    expected, name = fields
    p = ROOT / name
    checks.append(dict(path=name, matches=p.exists() and hashlib.sha256(p.read_bytes()).hexdigest() == expected))

summaries = {}
for name in ('summary_100s.json', 'summary_100s-mem.json', 'summary_100s-mem-thr.json',
             'summary_100s_half.json', 'summary_100s_quarter.json'):
    data = read(name)
    summaries[name] = {}
    for arm, row in data.items():
        if not isinstance(row, dict) or 'food' not in row:
            continue
        ratio = row['food'] / max(row['poison'], 1)
        assert abs(ratio - row['food_poison_last_third']) < 1e-12
        summaries[name][arm] = {k: row[k] for k in ('food', 'poison', 'food_poison_last_third',
            'stranded', 'final_P_right_order', 'final_P_learned_0.2') if k in row}
    summaries[name]['learn_minus_frozen'] = data.get('net_learn_minus_frozen')

result = dict(scope=__doc__, revision=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              provenance=checks, summaries=summaries, relay=read('relay_reference.json'),
              acquisition=read('acquisition.json'))
target = ROOT / 'lab/v/review_d176_20261120.json'
target.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(dict(output=str(target), hashes_checked=len(checks), mismatches=[x['path'] for x in checks if not x['matches']]), indent=2))

"""Independent saved-data review of D165; no simulation or production imports."""
import collections
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'lab/v/overnight_20261119'

def read(path):
    return json.loads(path.read_text())

def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]

def limits(c):
    paired = c['a'] > 0 and c['b'] > 0
    delay = c['delay']
    if paired and 0 < abs(delay) <= .15:
        return (.03, float('inf')) if delay > 0 else (-float('inf'), -.03)
    margin = .06 if paired and delay == 0 else .03
    return -margin, margin

def main():
    index = read(BASE / 'result_index.json')
    mismatch = []
    for item in index['files']:
        p = ROOT / item['path']
        if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != item['sha256']:
            mismatch.append(item['path'])
    script_mismatch = [p for p, h in index['scripts_sha256'].items()
                       if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != h]
    branches = collections.defaultdict(list)
    for b in read(ROOT / 'lab/v/order_balance_information/branches.json'):
        branches[b['seed']].append(b)
    intervals = {}
    for seed, bb in branches.items():
        assert len(bb) == 34
        lower, upper = -1., 1.
        for b in bb:
            lo, hi = limits(b['case'])
            u, v = b['u_V'], b['v_V']
            if v == 0:
                if not lo < u < hi:
                    lower, upper = 1., -1.
            else:
                a, z = sorted(((lo-u)/v, (hi-u)/v))
                lower, upper = max(lower, a), min(upper, z)
        intervals[seed] = [lower, upper]
    for f in read(BASE / 'failures_results/feasible_intervals.json'):
        assert max(abs(a-b) for a, b in zip(intervals[f['seed']], f['interval'])) < 1e-12
    settings = rows(BASE / 'histories_results/settings.jsonl')
    keys = {(r['seed'], r['replicate'], r['mode'], r['window']) for r in settings}
    assert len(settings) == len(keys) == 1920
    counts = collections.Counter()
    for r in settings:
        d = max(-1., min(1., -r['A_Vs']/r['B_Vs']))
        assert abs(d-r['d']) < 1e-12
        good = []
        for b in branches[r['seed']]:
            lo, hi = limits(b['case'])
            good.append(lo < b['u_V']+d*b['v_V'] < hi and b['coincidence_adequate'])
        assert sum(good) == r['passed'] and all(good) == r['all_pass']
        counts[r['mode']+'|'+r['window']] += all(good)
    summary = read(BASE / 'histories_results/history_summary.json')
    assert all(n == summary['by_mode_window'][k]['all_pass'] for k, n in counts.items())
    events = rows(BASE / 'attribution_results/event_contributions.jsonl')
    aggregates = rows(BASE / 'attribution_results/aggregate_settings.jsonl')
    max_error = 0.
    for r in aggregates:
        if r['aggregate'] == 'fallback_d0':
            continue
        chosen = [e for e in events if e['seed'] == r['seed'] and e['label'] in r['intervals']]
        for field in ['A_Vs', 'B_Vs']:
            error = abs(sum(e[field][r['mode']] for e in chosen)-r[field])
            max_error = max(max_error, error)
    assert max_error < 1e-12
    result = dict(indexed_files=len(index['files']), indexed_file_mismatches=mismatch,
                  script_mismatches=script_mismatch, settings_independently_rescored=len(settings),
                  cases_rescored=len(settings)*34, feasible_draws=sum(a<b for a,b in intervals.values()),
                  intervals=intervals, all_pass_counts=dict(counts),
                  aggregate_count=len(aggregates), aggregate_max_error_Vs=max_error,
                  limits='Saved-data arithmetic only; no independent trajectory replay or oscillator remeasurement.')
    inputs = [Path(__file__).resolve(), BASE / 'result_index.json',
              ROOT / 'lab/v/order_balance_information/branches.json',
              BASE / 'failures_results/feasible_intervals.json',
              BASE / 'histories_results/settings.jsonl', BASE / 'histories_results/history_summary.json',
              BASE / 'attribution_results/event_contributions.jsonl',
              BASE / 'attribution_results/aggregate_settings.jsonl']
    result['input_sha256'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in inputs}
    result['revision'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    out = ROOT / 'lab/v/review_overnight_20261120.json'
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['intervals','all_pass_counts','input_sha256']}, indent=2))
    assert not script_mismatch

if __name__ == '__main__':
    main()

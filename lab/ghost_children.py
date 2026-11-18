"""D92 (D91's frozen protocol): would the missing children have predicted, compared with actual children
scored by the same rule? Offline only, on D84's frozen trace; no simulated step.

  .venv/bin/python lab/ghost_children.py --check
  .venv/bin/python lab/ghost_children.py --run
"""
import json
import math
from pathlib import Path
import pickle
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'lab'), str(ROOT)]
import growth_parent_census as G
from future_evidence import activates
from retained_prediction import probability

BASE = ROOT/'lab/v/ghost_children'
PARTNER = ROOT/'lab/v/growth_missing_partner.pkl'
PARTNER_JSON = ROOT/'lab/v/growth_missing_partner.json'
CENSUS = ROOT/'lab/v/growth_parent_census.pkl'
COMBINED = ROOT/'lab/v/retained_mixture.json'
TOL = 1e-10
LAST_THIRD = 200.
BINS = ((0, 30), (30, 100), (100, 200), (200, 300))


def ghosts_from_calls(calls):
    """One ghost per (stream, word), at its first call (by position) where no living unit duplicates u."""
    out = {}
    for c in sorted(calls, key=lambda c: c['seq']):
        for a in c['associations']:
            if a['u_equivalent_living']:
                continue
            key = (c['stream'], a['word'])
            if key not in out:
                out[key] = dict(stream=c['stream'], word=a['word'], family=c['family'], form_seq=c['seq'], form_taste=c['taste'],
                                form_t=c['t'], dead_ancestors=a['dead_ancestors'])
    return list(out.values())


def new_unit(u, label):
    counts = [0, 0]
    counts[label] = 1
    return dict(u, counts=counts, rows=[])


def score_units(units, accepted, snapshots, combined):
    """accepted: list of (taste, t, label, prediction_seq) in order; snapshots[pred_seq] = (hists, indices)."""
    by_stream = {}
    for x in units:
        by_stream.setdefault(x['stream'], []).append(x)
    for taste, t, label, pseq in accepted:
        hists, index = snapshots[pseq]
        pc = combined[pseq]
        for j, xs in by_stream.items():
            for x in xs:
                if taste == x['form_taste'] or pseq <= x['form_seq']:
                    continue
                if not activates(x['word'], hists[j], index[j]):
                    continue
                p = probability(x['counts'])                       # before the update
                q = p if label else 1-p
                m = pc if label else 1-pc
                x['rows'].append(dict(taste=taste, t=t, vs_combined=math.log2(q/m), vs_uniform=math.log2(q/.5)))
                x['counts'][label] += 1
    return units


def causal_prior_bits(gains):
    """log2 likelihood ratio against native of the D87 prior: half native, unit j (1-based, formation order)
    1/[2j(j+1)], the unformed remainder 1/[2(N+1)] predicting natively."""
    N = len(gains)
    r = .5 + .5/(N+1) + sum(2**g/(2*j*(j+1)) for j, g in enumerate(gains, 1))
    return math.log2(r)


def summarize(units, window):
    lo = LAST_THIRD if window == 'last_third' else 0.
    per = []
    for x in units:
        rs = [r for r in x['rows'] if r['t'] >= lo]
        if rs:
            per.append((sum(r['vs_combined'] for r in rs), sum(r['vs_uniform'] for r in rs), len(rs)))
    c = [a for a, b, n in per]
    ordered = sorted(units, key=lambda x: x['form_seq'])
    gains = [sum(r['vs_combined'] for r in x['rows'] if r['t'] >= lo) for x in ordered]
    return dict(units=len(units), scored=len(per), zero_opportunity=len(units)-len(per),
                unit_taste_pairs=sum(n for a, b, n in per),
                better=sum(a > TOL for a in c), worse=sum(a < -TOL for a in c), equal=sum(abs(a) <= TOL for a in c),
                better_fraction_of_scored=(sum(a > TOL for a in c)/len(per)) if per else None,
                beat_combined_and_uniform=sum(a > TOL and b > TOL for a, b, n in per),
                saving_vs_combined_bits=G.distribution(c), saving_vs_uniform_bits=G.distribution(b for a, b, n in per),
                causal_prior_log2_ratio_vs_native=causal_prior_bits(gains))


def bins(units, accepted):
    out = {}
    for lo, hi in BINS:
        xs = [x for x in units if lo <= G.LIFE-x['form_t'] < hi or (hi == 300 and G.LIFE-x['form_t'] == 300)]
        out[f'[{lo},{hi}{"]" if hi == 300 else ")"} s'] = dict(units=len(xs), zero_opportunity=sum(not x['rows'] for x in xs),
            later_accepted=G.distribution(sum(p > x['form_seq'] for _, _, _, p in accepted) for x in xs))
    return out


def table(s):
    lines = ['| arm | formed | scored | better / worse / equal vs combined | share better | beat both | median saving | causal prior vs native |',
             '|---|---:|---:|---:|---:|---:|---:|---:|']
    for k, v in s.items():
        f = v['better_fraction_of_scored']
        m = v['saving_vs_combined_bits'].get('median')
        lines.append(f"| {k} | {v['units']} | {v['scored']} | {v['better']} / {v['worse']} / {v['equal']} | "
                     f"{'-' if f is None else f'{f:.3f}'} | {v['beat_combined_and_uniform']} | "
                     f"{'-' if m is None else f'{m:+.3f}'} | {v['causal_prior_log2_ratio_vs_native']:+.3f} bits |")
    return '\n'.join(lines)


class Snap:
    def __init__(self):
        self.snapshots = {}

    def predict(self, R, e, speakers, probs):
        self.snapshots[e['seq']] = ([dict(h) for h in R.hist], list(R.index))


def check():
    checks = []
    assert causal_prior_bits([0.]*5) == 0. and causal_prior_bits([]) == 0.
    assert causal_prior_bits([-50.]*10) >= -1. and causal_prior_bits([10.]) > 0
    checks.append('causal prior: zero gains give ratio 1; loss bounded by one bit; a winner raises it')
    calls = [dict(stream=0, family='event', taste=5, seq=20, t=9., associations=[
                 dict(word=(1, 0), u_equivalent_living=False, dead_ancestors=0), dict(word=(0, 0), u_equivalent_living=True, dead_ancestors=0)]),
             dict(stream=0, family='event', taste=2, seq=10, t=5., associations=[dict(word=(1, 0), u_equivalent_living=True, dead_ancestors=0)]),
             dict(stream=0, family='event', taste=6, seq=30, t=12., associations=[dict(word=(1, 0), u_equivalent_living=False, dead_ancestors=1)])]
    g = ghosts_from_calls(calls)
    assert len(g) == 1 and g[0]['form_seq'] == 20 and g[0]['dead_ancestors'] == 0
    checks.append('one ghost per word, at the first call by position lacking a living equivalent parent')
    snaps = {1: ([{0: 1, 1: 0}], [1]), 2: ([{0: 1, 1: 0}], [1]), 3: ([{1: 1, 2: 0}], [2])}
    acc = [(5, 9., 1, 1), (7, 10., 1, 2), (8, 11., 0, 3)]
    x = new_unit(dict(stream=0, word=(1, 0), form_seq=1, form_taste=5, form_t=9.), 0)
    a = new_unit(dict(stream=0, word=(1, 0), form_seq=1, form_taste=5, form_t=9.), 0)
    score_units([x], acc, snaps, {1: .5, 2: .5, 3: .5})
    assert len(x['rows']) == 2 and [r['taste'] for r in x['rows']] == [7, 8]
    assert abs(x['rows'][0]['vs_uniform']-math.log2(.25/.5)) < 1e-12           # counts [1,0] -> p1=.25, label 1
    assert x['counts'] == [2, 1]
    checks.append('formation taste and predictions not after formation excluded; score before update')
    acc2 = [(5, 9., 1, 1), (7, 10., 0, 2), (8, 11., 0, 3)]
    score_units([a], acc2, snaps, {1: .5, 2: .5, 3: .5})
    assert a['rows'][0]['vs_uniform'] != x['rows'][0]['vs_uniform']
    b = new_unit(dict(stream=0, word=(1, 0), form_seq=1, form_taste=5, form_t=9.), 0)
    score_units([b], [(5, 9., 1, 1), (7, 10., 1, 2), (8, 11., 1, 3)], snaps, {1: .5, 2: .5, 3: .5})
    assert b['rows'][0] == x['rows'][0]
    checks.append('a later outcome cannot change an earlier score')
    out = dict(success=True, checks=checks, simulated_steps=0)
    BASE.with_name(BASE.name+'_checks').with_suffix('.json').write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps(out, indent=2))


def run():
    started = time.monotonic()
    out = dict(success=False, checks={}, provenance=G.provenance(
        ('lab/ghost_children.py', 'lab/growth_parent_census.py', 'lab/growth_missing_partner.py', 'lab/future_evidence.py',
         'lab/retained_prediction.py'), (G.RAW, PARTNER, PARTNER_JSON, CENSUS, COMBINED),
        'timeout --signal=TERM --kill-after=5s 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 '
        '.venv/bin/python lab/ghost_children.py --run'), rows_path=str(BASE.with_suffix('.pkl')))
    try:
        pj = json.loads(PARTNER_JSON.read_text())
        assert pj['success'] and pj['provenance']['input_sha256'][str(G.RAW)] == G.digest(G.RAW)
        partner = pickle.loads(PARTNER.read_bytes())
        census = pickle.loads(CENSUS.read_bytes())['rows']
        cap = json.loads(COMBINED.read_text())
        assert all(cap['identity'].values()) and cap['provenance']['baseline_sha256'] == G.digest(G.RAW)
        combined = {p['seq']: p['p1'] for p in cap['predictions']}
        raw = G.load_raw()
        assert list(combined) == raw['prediction_positions']
        snap = Snap()
        R = G.Replay(raw, snap).run()
        tastes = R.tastes
        accepted = sorted(((k, v['t'], v['label'], v['prediction_seq']) for k, v in tastes.items()), key=lambda a: a[3])
        assert len(accepted) == 163
        ghosts = [new_unit(g, tastes[g['form_taste']]['label']) for g in ghosts_from_calls(partner['calls'])]
        expected = pj['summary']['full_remaining_life']['all']['unique_words_absent_and_no_living_equivalent_parent_at_some_occurrence']
        assert len(ghosts) == expected, (len(ghosts), expected)
        kids = []
        for (j, k), r in census.items():
            assert tastes[r['birth_taste']]['label'] == raw['events'][tastes[r['birth_taste']]['learn_seq']]['letter']
            kids.append(new_unit(dict(stream=j, word=R.words[j][k], family=r['family'], form_seq=r['birth_seq'],
                                      form_taste=r['birth_taste'], form_t=r['birth_t']), tastes[r['birth_taste']]['label']))
        score_units(ghosts, accepted, snap.snapshots, combined)
        score_units(kids, accepted, snap.snapshots, combined)
        out['checks'] = dict(R.checks, ghosts=len(ghosts), actual_children=len(kids), accepted=len(accepted),
                             ghost_count_matches_D90=True, tolerance_bits=TOL)
        print('VALIDATION', json.dumps(out['checks']), flush=True)
        arms = {'ghost children': ghosts, 'actual children (same rule)': kids}
        for f in G.FAMILIES:
            arms['ghost, '+f] = [x for x in ghosts if x['family'] == f]
            arms['actual, '+f] = [x for x in kids if x['family'] == f]
        arms['ghost, no removed ancestor needed'] = [x for x in ghosts if x['dead_ancestors'] == 0]
        arms['ghost, removed ancestors needed'] = [x for x in ghosts if x['dead_ancestors'] > 0]
        summ = {w: {k: summarize(v, w) for k, v in arms.items()} for w in ('full', 'last_third')}
        out['summary'] = dict(windows=summ, remaining_life_bins={'ghost children': bins(ghosts, accepted),
                              'actual children (same rule)': bins(kids, accepted)},
                              native_combined_bits_full=sum(-math.log2(combined[p] if l else 1-combined[p]) for _, _, l, p in accepted))
        out['table_full'] = table(summ['full'])
        out['table_last_third'] = table(summ['last_third'])
        out['limits'] = ['Offline tallies on one unchanged history: no action, allocation or displacement effects.',
                         'Ghosts and actual-child copies persist to life end; both ignore deletion and pay no material.',
                         'Per-unit comparisons overlap in tastes; only the causal prior counts each label once.',
                         'Formation order prior is supplied, not fitted; not a bound on all selection rules.']
        BASE.with_suffix('.pkl').write_bytes(pickle.dumps(dict(ghosts=ghosts, children=kids, summary=out)))
        out['success'] = True
        print('FULL\n'+out['table_full'], flush=True)
        print('LAST THIRD\n'+out['table_last_third'], flush=True)
        print('BINS', json.dumps(out['summary']['remaining_life_bins']), flush=True)
    except Exception as e:
        out['error'] = dict(type=type(e).__name__, message=str(e))
        raise
    finally:
        out['wall_s'] = time.monotonic()-started
        BASE.with_suffix('.json').write_text(json.dumps(out, indent=2)+'\n')
        print('wall_s', out['wall_s'], flush=True)


if __name__ == '__main__':
    assert sys.argv[1:] in (['--check'], ['--run'])
    check() if sys.argv[1] == '--check' else run()

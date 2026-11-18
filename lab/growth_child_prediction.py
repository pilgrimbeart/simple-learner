"""Job 2 of PROGRAMME.md's 2026-11-18 work queue: did actual children ever add predictive evidence?

Offline only. For each accepted taste, the last actual prediction before learning: every stream whose
issued speaker is a grown child is scored log2(P_child(label)/P_combined(label)) and against uniform 1/2,
before any update. Combined forecasts are D87's, joined by prediction-event position. Groups use the
parent state recorded at birth by Job 1 (lab/v/growth_parent_census.pkl).

  .venv/bin/python lab/growth_child_prediction.py --check
  .venv/bin/python lab/growth_child_prediction.py --run
"""
import copy
import json
import math
from pathlib import Path
import pickle
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'lab'), str(ROOT)]
import growth_parent_census as G

BASE = ROOT/'lab/v/growth_child_prediction'
CENSUS = ROOT/'lab/v/growth_parent_census.pkl'
CENSUS_JSON = ROOT/'lab/v/growth_parent_census.json'
COMBINED = ROOT/'lab/v/retained_mixture.json'
TOL = 1e-10
LAST_THIRD = 200.
BINS = ((0, 30), (30, 100), (100, 200), (200, 300))


class Scorer:
    """Records child speakers at the last prediction before each accepted taste. Probabilities are
    copied at the prediction; the label is applied afterwards, so it cannot reach them."""

    def __init__(self, combined, grown):
        self.combined, self.grown = combined, grown
        self.rows = []
        self.accepted = []

    def accepted_hook(self, R, e, last):
        pc = self.combined[last['seq']]
        assert 0 < pc < 1
        self.accepted.append(dict(taste=e['taste'], t=e['t'], label=e['letter'], prediction_seq=last['seq']))
        for j, k in enumerate(last['speakers']):
            if k is None or (j, k) not in self.grown:
                continue
            p1 = last['probs'][j]
            lab = e['letter']
            child = p1 if lab else 1-p1
            comb = pc if lab else 1-pc
            self.rows.append(dict(stream=j, child=k, taste=e['taste'], t=e['t'], label=lab, prediction_seq=last['seq'],
                                  p_child=p1, p_combined=pc, vs_combined=math.log2(child/comb), vs_uniform=math.log2(child/.5)))


def make_observer(scorer):
    class O:
        pass
    o = O()
    o.accepted = scorer.accepted_hook
    return o


def score(raw, combined, grown):
    s = Scorer(combined, grown)
    R = G.Replay(raw, make_observer(s)).run()
    return R, s


def group_summary(children, rows_by_child, window):
    lo = LAST_THIRD if window == 'last_third' else 0.
    per_child, pairs, tastes = [], [], set()
    for key in children:
        rs = [r for r in rows_by_child.get(key, ()) if r['t'] >= lo]
        if not rs:
            continue
        pairs += rs
        tastes |= {r['taste'] for r in rs}
        per_child.append((sum(r['vs_combined'] for r in rs), sum(r['vs_uniform'] for r in rs)))
    c = [a for a, b in per_child]
    return dict(born_children=len(children), children_scored=len(per_child),
                children_zero_opportunities=len(children)-len(per_child),
                child_taste_pairs=len(pairs), unique_accepted_tastes=len(tastes),
                children_better_than_combined=sum(a > TOL for a in c),
                children_worse_than_combined=sum(a < -TOL for a in c),
                children_numerically_equal=sum(abs(a) <= TOL for a in c),
                pairs_better=sum(r['vs_combined'] > TOL for r in pairs), pairs_worse=sum(r['vs_combined'] < -TOL for r in pairs),
                pairs_numerically_equal=sum(abs(r['vs_combined']) <= TOL for r in pairs),
                median_child_saving_vs_combined_bits=G.distribution(c).get('median'),
                child_saving_vs_combined_bits=G.distribution(c),
                child_saving_vs_uniform_bits=G.distribution([b for a, b in per_child]),
                children_beating_combined_and_uniform=sum(a > TOL and b > TOL for a, b in per_child))


def analyse(census_rows, scorer, R):
    rows_by_child = {}
    for r in scorer.rows:
        rows_by_child.setdefault((r['stream'], r['child']), []).append(r)
    for key, rs in rows_by_child.items():
        assert len({r['taste'] for r in rs}) == len(rs), 'A child scored twice at one taste'
    groups = {'any grown parent not yet spoken': [k for k, r in census_rows.items() if r['grown_silent']],
              'any one-tally grown parent': [k for k, r in census_rows.items() if r['grown_one_tally']],
              'neither': [k for k, r in census_rows.items() if not r['grown_silent'] and not r['grown_one_tally']],
              'all children': list(census_rows)}
    for f in G.FAMILIES:
        groups['family '+f] = [k for k, r in census_rows.items() if r['family'] == f]
    out = {w: {g: group_summary(ks, rows_by_child, w) for g, ks in groups.items()} for w in ('full', 'last_third')}
    accepted = scorer.accepted
    bins = {}
    for lo, hi in BINS:
        ks = [k for k, r in census_rows.items() if lo <= r['remaining_s'] < hi or (hi == 300 and r['remaining_s'] == 300)]
        later = [sum(a['prediction_seq'] > census_rows[k]['birth_seq'] for a in accepted) for k in ks]
        bins[f'[{lo},{hi}{"]" if hi == 300 else ")"} s'] = dict(children=len(ks), later_accepted_tastes=G.distribution(later),
            children_with_no_later_accepted_taste=sum(x == 0 for x in later),
            zero_score_children=sum(k not in rows_by_child for k in ks))
    assert sum(b['children'] for b in bins.values()) == len(census_rows)
    return out, bins, rows_by_child


def table(summary):
    lines = ['| group | born children | scored ≥1 | child–taste pairs | unique tastes | better / worse / equal vs combined '
             '(per child) | median per-child saving vs combined (bits) | beat combined and uniform |',
             '|---|---:|---:|---:|---:|---:|---:|---:|']
    for g, s in summary.items():
        m = s['median_child_saving_vs_combined_bits']
        lines.append(f"| {g} | {s['born_children']} | {s['children_scored']} | {s['child_taste_pairs']} | "
                     f"{s['unique_accepted_tastes']} | {s['children_better_than_combined']} / {s['children_worse_than_combined']} / "
                     f"{s['children_numerically_equal']} | {'-' if m is None else f'{m:+.3f}'} | {s['children_beating_combined_and_uniform']} |")
    return '\n'.join(lines)


def check():
    checks = []
    raw = G.fixture()
    combined = {e['seq']: .3 + .01*e['seq'] for e in raw['events'] if e['kind'] == 'predict'}
    grown = {(0, 2), (0, 3), (0, 4)}
    R, s = score(raw, combined, grown)
    assert len(s.accepted) == 5 and [a['prediction_seq'] for a in s.accepted] == [2, 2, 10, 15, 21]
    rows = s.rows
    assert len(rows) == 1, rows
    r = rows[0]
    assert (r['child'], r['taste'], r['prediction_seq']) == (2, 3, 15)
    checks.append('two predictions at the same time: the later call position (15) is used, not 14')
    assert r['p_child'] == .25 and abs(r['p_combined']-combined[15]) < 1e-15
    assert abs(r['vs_combined']-math.log2(.25/combined[15])) < 1e-12 and abs(r['vs_uniform']-math.log2(.5)) < 1e-12
    checks.append('issued speaker deleted during the following taste is still scored with its issued probability')
    assert all(x['taste'] != 2 or x['child'] != 3 for x in rows)
    checks.append('child 3 spoke at seq 8, but the last prediction before taste 2 is seq 10 (speaker fixed): not scored')
    flip = copy.deepcopy(raw)
    learn = [e for e in flip['events'] if e['kind'] == 'learn' and e['taste'] == 3][0]
    learn['letter'] = 0
    rem = {e['k']: e for e in flip['events'] if e['kind'] == 'remove'}
    rem[2]['counts'] = [2, 0]
    _, s2 = score(flip, combined, grown)
    r2 = s2.rows[0]
    assert (r2['p_child'], r2['p_combined']) == (r['p_child'], r['p_combined']) and r2['vs_combined'] != r['vs_combined']
    checks.append('changing the outcome leaves the preceding probabilities unchanged; only the score changes')
    census = {(0, 2): dict(grown_silent=False, grown_one_tally=False, family='event', remaining_s=299., birth_seq=4),
              (0, 3): dict(grown_silent=True, grown_one_tally=True, family='event', remaining_s=298., birth_seq=7),
              (0, 4): dict(grown_silent=True, grown_one_tally=True, family='event', remaining_s=297., birth_seq=12)}
    summ, bins, _ = analyse(census, s, R)
    a = summ['full']['all children']
    assert a['born_children'] == 3 and a['children_scored'] == 1 and a['children_zero_opportunities'] == 2
    assert summ['full']['any one-tally grown parent']['children_scored'] == 0
    assert bins['[200,300] s']['zero_score_children'] == 2
    checks.append('zero-opportunity children kept in denominators, separate from numerical equalities')
    out = dict(success=True, checks=checks, simulated_steps=0)
    BASE.with_name(BASE.name+'_checks').with_suffix('.json').write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps(out, indent=2))


def run():
    started = time.monotonic()
    out = dict(success=False, checks={}, provenance=G.provenance(
        ('lab/growth_child_prediction.py', 'lab/growth_parent_census.py', 'lab/future_evidence.py', 'lab/retained_prediction.py'),
        (G.RAW, CENSUS, CENSUS_JSON, COMBINED), 'timeout --signal=TERM --kill-after=5s 240s env OPENBLAS_NUM_THREADS=1 '
        'OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/growth_child_prediction.py --run'),
        rows_path=str(BASE.with_suffix('.pkl')))
    try:
        cj = json.loads(CENSUS_JSON.read_text())
        assert cj['success'] and cj['provenance']['input_sha256'][str(G.RAW)] == G.digest(G.RAW)
        census = pickle.loads(CENSUS.read_bytes())['rows']
        assert len(census) == G.EXPECTED['births']
        cap = json.loads(COMBINED.read_text())
        assert 'failure' not in cap and all(cap['identity'].values())
        assert cap['provenance']['baseline_sha256'] == G.digest(G.RAW), 'D87 capture belongs to another trace'
        combined = {p['seq']: p['p1'] for p in cap['predictions']}
        raw = G.load_raw()
        assert list(combined) == raw['prediction_positions'], 'Combined forecasts do not align by call position'
        R, s = score(raw, combined, set(census))
        assert len(s.accepted) == G.EXPECTED['accepted_tastes'] and R.checks['predictions'] == G.EXPECTED['predictions']
        out['checks'] = dict(R.checks, combined_forecasts_aligned_by_position=len(combined), accepted_tastes=len(s.accepted),
                             census_children=len(census), tolerance_bits=TOL)
        print('VALIDATION', json.dumps(out['checks']), flush=True)
        summary, bins, by_child = analyse(census, s, R)
        out['summary'] = dict(windows=summary, remaining_life_at_birth=bins,
                              accepted_tastes_last_third=sum(a['t'] >= LAST_THIRD for a in s.accepted))
        out['table_full'] = table(summary['full'])
        out['table_last_third'] = table(summary['last_third'])
        out['limits'] = ['Descriptive relative score: the combined forecast already includes the child; not a leave-out effect.',
                         'Children share tastes and ancestry: no independent-unit intervals; sums are not learned bits.',
                         'Equality means |difference| <= 1e-10 bits, not a statistical tie.',
                         'Late birth limits exposure; zero opportunities are not shown to be caused by birth time.',
                         'One frozen corrected contest life.']
        BASE.with_suffix('.pkl').write_bytes(pickle.dumps(dict(rows=s.rows, accepted=s.accepted, summary=out)))
        out['success'] = True
        print('FULL LIFE\n'+out['table_full'], flush=True)
        print('LAST THIRD\n'+out['table_last_third'], flush=True)
        print('BINS', json.dumps(bins), flush=True)
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

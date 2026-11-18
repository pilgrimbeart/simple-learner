"""Job 1 of PROGRAMME.md's 2026-11-18 work queue: were weak or silent units used to build children?

Purely offline replay of D84's saved event trace (corrected contest life: sequence rung 17, seed 177000,
red first, 300 s, dt=.0025 s, total cap 3042). No simulated step, learning change or ghost feedback.
Also provides the checked native replay (`replay`) that Jobs 2-3 reuse.

  .venv/bin/python lab/growth_parent_census.py --check   # deterministic fixtures
  .venv/bin/python lab/growth_parent_census.py --run     # saved-data analysis
"""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import pickle
import subprocess
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'lab'), str(ROOT)]
from future_evidence import signature, activates, write_history
from future_evidence_analysis import family
from retained_prediction import probability, speaker

RAW = ROOT/'lab/v/future_evidence.pkl'
BASE = ROOT/'lab/v/growth_parent_census'
LIFE = 300.
FAMILIES = ('event', 'clock', 'integrator', 'rhythm')
EXPECTED = dict(births=10236, removals=9236, initial_units=2042, final_units=3042, predictions=5883,
                learns=27384, accepted_tastes=163)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def provenance(sources, inputs, command):
    return dict(revision=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                dirty=subprocess.check_output(['git', 'status', '--short'], cwd=ROOT, text=True),
                source_sha256={p: digest(ROOT/p) for p in sources},
                input_sha256={str(p): digest(p) for p in inputs}, command=command,
                life=dict(rung='sequence 17', seed=177000, poison_first='red', life_s=LIFE, dt_s=.0025, total_cap=3042,
                          design='corrected weight contest (D84 trace)'))


def distribution(a):
    a = np.array(list(a), dtype=float)
    if not len(a):
        return dict(n=0)
    return dict(n=int(len(a)), minimum=float(a.min()), median=float(np.median(a)), q90=float(np.quantile(a, .9)),
                maximum=float(a.max()), total=float(a.sum()))


class Replay:
    """Native-order reconstruction of living tallies, histories and issued speakers (D85 semantics).

    Hooks (all optional) on `observer`: predict(R, e, speakers, probs); accepted(R, e, last_prediction);
    learn(R, e) after the current label's increments and before any removal inside that learn;
    birth(R, e, row); remove(R, e). Every check is an assertion: the first mismatch stops the replay."""

    def __init__(self, raw, observer=None):
        assert all(c == 'Net' for c in raw['classes'])
        assert all(not h for h in raw['initial_histories'])
        self.raw, self.obs = raw, observer
        self.defs = [{k: r['definition'] for k, r in ds.items()} for ds in raw['definitions']]
        self.words = [{} for _ in self.defs]
        for j, ds in enumerate(self.defs):
            for k in ds:
                signature(ds, k, self.words[j])
        self.fam = [family(n) for n in raw['names']]
        self.living = [{k: [0, 0] for k, r in ds.items() if r['birth_seq'] == -1} for ds in raw['definitions']]
        assert all(self.defs[j][k]['sym'] is not None for j, ns in enumerate(self.living) for k in ns)
        self.hist = [dict(h) for h in raw['initial_histories']]
        self.index = [-1]*len(self.hist)
        self.versions = [0]*len(self.hist)
        self.speaking = {}
        self.tastes = {}
        self.last_prediction = None
        self.last_learn = {}
        self.checks = Counter(initial_units=sum(len(x) for x in self.living))
        self.pending_write = None

    def _hook(self, name, *a):
        f = getattr(self.obs, name, None)
        if f is not None:
            f(self, *a)

    def _orphans(self, j):
        ns = self.living[j]
        for k in ns:
            d = self.defs[j][k]
            if d['sym'] is None:
                assert d['u'] in ns and d['v'] in ns, ('Living unit with a removed parent', j, k)

    def run(self):
        raw = self.raw
        for e in raw['events']:
            kind = e['kind']
            if kind == 'write':
                j = e['stream']
                assert e['i'] == self.index[j]+1, ('Nonsequential write', e['seq'])
                self.index[j] = e['i']
                self.pending_write = j
                changed = write_history(self.hist[j], e['i'], e['sym'], e['keep'], raw['hist_limit'])
                self.versions[j] += int(changed)
                assert changed == e['changed'] and self.versions[j] == e['version']
                self.checks['writes'] += 1
            elif kind == 'predict':
                self.pending_write = None
                speakers, probs = [], []
                for j, ns in enumerate(self.living):
                    k = speaker(ns, self.words[j], self.hist[j], self.index[j])
                    speakers.append(k)
                    probs.append(.5 if k is None else probability(ns[k]))
                    if k is not None:
                        rec = self.speaking.setdefault((j, k), dict(first_seq=e['seq'], count=0))
                        rec['count'] += 1
                self.last_prediction = dict(seq=e['seq'], t=e['t'], speakers=speakers, probs=probs)
                self.checks['predictions'] += 1
                self._hook('predict', e, speakers, probs)
            elif kind == 'learn':
                self.pending_write = None
                j = e['stream']
                assert self.index[j] == e['i']
                assert list(self.living[j]) == e['living'], ('Living set mismatch', e['seq'])
                self._orphans(j)
                fired = [k for k in self.living[j] if activates(self.words[j][k], self.hist[j], self.index[j])]
                assert fired == e['firing'], ('Firing mismatch', e['seq'])
                if e['taste'] not in self.tastes:
                    assert self.last_prediction is not None
                    self.tastes[e['taste']] = dict(t=e['t'], label=e['letter'], prediction_seq=self.last_prediction['seq'],
                                                   learn_seq=e['seq'])
                    self.checks['accepted_tastes'] += 1
                    self._hook('accepted', e, self.last_prediction)
                else:
                    a = self.tastes[e['taste']]
                    assert (a['t'], a['label']) == (e['t'], e['letter'])
                for k in fired:
                    self.living[j][k][e['letter']] += 1
                self.last_learn[j] = e
                self.checks['learns'] += 1
                self._hook('learn', e)
            elif kind == 'birth':
                self.pending_write = None
                j, k = e['stream'], e['k']
                d = self.defs[j][k]
                assert k not in self.living[j] and self.raw['definitions'][j][k]['birth_seq'] == e['seq']
                assert self.last_learn[j]['taste'] == e['taste']
                assert d['sym'] is None and d['u'] in self.living[j] and d['v'] in self.living[j], ('Parent absent at birth', e['seq'])
                assert d['span'] == self.defs[j][d['u']]['span'] + self.defs[j][d['v']]['span'], ('Spans do not add', e['seq'])
                assert len(self.words[j][k]) == d['span']
                row = self.birth_row(e)
                counts = [0, 0]
                counts[self.last_learn[j]['letter']] = 1
                self.living[j][k] = counts
                self.checks['births'] += 1
                self._hook('birth', e, row)
            elif kind == 'remove':
                j, k = e['stream'], e['k']
                if self.index[j] != e['i']:
                    assert e['i'] == self.index[j]-1 and self.pending_write == j, ('Unexplained removal index', e['seq'])
                    self.checks['tidy_removals_before_index_increment'] += 1
                assert k in self.living[j], ('Removal of a unit not living', e['seq'])
                assert self.living[j][k] == e['counts'], ('Removal tally mismatch', e['seq'], self.living[j][k], e['counts'])
                assert self.defs[j][k]['sym'] is None, 'Fixed unit removed'
                self._hook('remove', e)
                del self.living[j][k]
                self.checks['removals'] += 1
                self.checks['one_tally_removals'] += int(sum(e['counts']) == 1)
            else:
                raise AssertionError(('Unknown event', kind))
        for j in range(len(self.living)):
            self._orphans(j)
        assert self.speaking == raw['speaking'], 'Native speaking first positions/counts differ'
        self.checks['native_speaking_records_exact'] = len(self.speaking)
        c = raw['counters']
        assert (self.checks['predictions'], self.checks['learns'], self.checks['births'], self.checks['removals']) == \
            (c['predict_calls'], c['learn_calls'], c['adds'], c['removals'])
        self.checks['final_units'] = sum(len(x) for x in self.living)
        assert self.checks['final_units'] == self.checks['initial_units']+self.checks['births']-self.checks['removals']
        total_defs = sum(len(ds) for ds in self.defs)
        assert total_defs == self.checks['initial_units']+self.checks['births']
        return self

    def birth_row(self, e):
        """Parents' state at the birth: tallies after the current lesson's increments (native order), and
        whether each had spoken at an actual prediction strictly before this birth."""
        j, k = e['stream'], e['k']
        d = self.defs[j][k]
        parents = []
        for role in ('u', 'v'):
            p = d[role]
            pd = self.defs[j][p]
            rec = self.speaking.get((j, p))
            spoke = rec is not None and rec['first_seq'] < e['seq']
            parents.append(dict(role=role, id=p, fixed=pd['sym'] is not None, span=pd['span'],
                                counts=list(self.living[j][p]), spoke_before=spoke))
        grown = [p for p in parents if not p['fixed']]
        return dict(stream=j, child=k, name=self.raw['names'][j], family=self.fam[j], birth_seq=e['seq'], birth_t=e['t'],
                    birth_taste=e['taste'], remaining_s=LIFE-e['t'], child_span=d['span'], parents=parents,
                    repeated_parent=d['u'] == d['v'],
                    grown_silent=any(not p['spoke_before'] for p in grown),
                    grown_one_tally=any(sum(p['counts']) == 1 for p in grown),
                    grown_two_plus=any(sum(p['counts']) >= 2 for p in grown),
                    fixed_only=not grown)


class Census:
    def __init__(self):
        self.rows = {}

    def birth(self, R, e, row):
        key = (row['stream'], row['child'])
        assert key not in self.rows
        self.rows[key] = row


def descendants(defs):
    kids = defaultdict(set)
    for k, d in defs.items():
        if d['sym'] is None:
            kids[d['u']].add(k)
            kids[d['v']].add(k)
    memo = {}

    def below(k):
        if k not in memo:
            out = set()
            for c in kids[k]:
                out |= {c} | below(c)
            memo[k] = out
        return memo[k]
    return kids, below


def summarize(rows, defs_by_stream):
    rows = list(rows)
    appearances = Counter()
    uniq = defaultdict(set)
    for r in rows:
        seen_here = set()
        for p in r['parents']:
            key = (r['stream'], p['id'])
            if p['fixed']:
                appearances['fixed'] += 1
                uniq['fixed'].add(key)
                continue
            appearances['grown'] += 1
            uniq['grown'].add(key)
            n = sum(p['counts'])
            if not p['spoke_before']:
                appearances['grown_not_yet_spoken'] += 1
                uniq['grown_not_yet_spoken'].add(key)
            if n == 1:
                appearances['grown_one_tally'] += 1
                uniq['grown_one_tally'].add(key)
            if n >= 2:
                appearances['grown_two_plus_tallies'] += 1
                uniq['grown_two_plus_tallies'].add(key)
            if n == 1 and not p['spoke_before']:
                appearances['grown_one_tally_and_not_yet_spoken'] += 1
            seen_here.add(key)
    weak = uniq['grown_not_yet_spoken'] | uniq['grown_one_tally']
    kid_counts, desc_counts, desc_spans = [], [], []
    cache = {}
    for (j, p) in sorted(weak):
        if j not in cache:
            cache[j] = descendants(defs_by_stream[j])
        kids, below = cache[j]
        kid_counts.append(len(kids[p]))
        b = below(p)
        desc_counts.append(len(b))
        desc_spans += [defs_by_stream[j][c]['span'] for c in b]
    spans = [r['child_span'] for r in rows]
    return dict(births=len(rows),
                births_using_grown_parent_not_yet_spoken=sum(r['grown_silent'] for r in rows),
                births_using_one_tally_grown_parent=sum(r['grown_one_tally'] for r in rows),
                births_using_grown_parent_with_two_plus_tallies=sum(r['grown_two_plus'] for r in rows),
                births_with_fixed_parents_only=sum(r['fixed_only'] for r in rows),
                births_with_repeated_parent=sum(r['repeated_parent'] for r in rows),
                parent_appearances=dict(appearances, total=2*len(rows)),
                unique_parents={k: len(v) for k, v in uniq.items()},
                distinct_grown_parents=len(uniq['grown']),
                weak_unique_parents=len(weak),
                weak_parent_direct_children=distribution(kid_counts),
                weak_parent_descendants=distribution(desc_counts),
                weak_parent_descendant_spans=distribution(desc_spans),
                child_span=distribution(spans))


def table(summary):
    lines = ['| family | births | births using a grown parent not yet spoken | births using a one-tally grown parent '
             '| distinct grown parents | median / max child span |', '|---|---:|---:|---:|---:|---:|']
    for name, s in summary.items():
        cs = s['child_span']
        lines.append(f"| {name} | {s['births']} | {s['births_using_grown_parent_not_yet_spoken']} | "
                     f"{s['births_using_one_tally_grown_parent']} | {s['distinct_grown_parents']} | "
                     f"{cs.get('median', '-')} / {cs.get('maximum', '-')} |")
    return '\n'.join(lines)


# ---------------------------------------------------------------- fixtures

def fixture():
    """One stream. Unit 2=(0,0) repeats a parent; 2 then parents 3=(2,1) and 4=(2,0) before it first speaks;
    removing 2 cascades to 3 and 4."""
    defs = {0: dict(sym=0, u=None, v=None, span=1), 1: dict(sym=1, u=None, v=None, span=1),
            2: dict(sym=None, u=0, v=0, span=2), 3: dict(sym=None, u=2, v=1, span=3), 4: dict(sym=None, u=2, v=0, span=3)}
    births = {2: (4, 0), 3: (7, 1), 4: (12, 2)}
    events = []

    def emit(kind, **kw):
        events.append(dict(seq=len(events), kind=kind, **kw))
    v = 0

    def write(i, s):
        nonlocal v
        v += 1
        emit('write', stream=0, i=i, sym=s, keep=False, changed=True, version=v)
    write(0, 0); write(1, 0)
    emit('predict', t=0.)                                                         # 2: silent
    emit('learn', stream=0, i=1, t=1., taste=0, letter=0, living=[0, 1], firing=[0])
    emit('birth', stream=0, k=2, t=1., taste=0)                                   # 4
    write(2, 1)
    emit('learn', stream=0, i=2, t=2., taste=1, letter=1, living=[0, 1, 2], firing=[1])
    emit('birth', stream=0, k=3, t=2., taste=1)                                   # 7
    emit('predict', t=2.)                                                         # 8: speaker 3
    write(3, 0)
    emit('predict', t=3.)                                                         # 10: speaker 0
    emit('learn', stream=0, i=3, t=3., taste=2, letter=0, living=[0, 1, 2, 3], firing=[0])
    emit('birth', stream=0, k=4, t=3., taste=2)                                   # 12
    write(4, 0)
    emit('predict', t=4.)                                                         # 14: speaker 2 (first time)
    emit('predict', t=4.)                                                         # 15: same time, later position
    emit('learn', stream=0, i=4, t=4., taste=3, letter=1, living=[0, 1, 2, 3, 4], firing=[0, 2])
    emit('remove', stream=0, k=2, i=4, t=4., taste=3, counts=[1, 1])
    emit('remove', stream=0, k=3, i=4, t=4., taste=3, counts=[0, 1])
    emit('remove', stream=0, k=4, i=4, t=4., taste=3, counts=[1, 0])
    write(5, 1)
    emit('predict', t=5.)                                                         # 21
    emit('learn', stream=0, i=5, t=5., taste=4, letter=1, living=[0, 1], firing=[1])
    rawdefs = [{k: dict(definition=d, birth_seq=births[k][0] if k in births else -1,
                        birth_taste=births[k][1] if k in births else None) for k, d in defs.items()}]
    speaking = {(0, 3): dict(first_seq=8, count=1), (0, 0): dict(first_seq=10, count=1),
                (0, 2): dict(first_seq=14, count=2), (0, 1): dict(first_seq=21, count=1)}
    return dict(classes=['Net'], names=['every:colour'], definitions=rawdefs, initial_histories=[{}], events=events,
                prediction_positions=[e['seq'] for e in events if e['kind'] == 'predict'], speaking=speaking,
                hist_limit=96, counters=dict(predict_calls=6, learn_calls=5, adds=3, removals=3))


def expect_failure(raw, why):
    try:
        Replay(raw).run()
    except AssertionError:
        return
    raise AssertionError('Corrupt fixture accepted: '+why)


def check():
    import copy
    checks = []
    raw = fixture()
    c = Census()
    R = Replay(raw, c).run()
    rows = c.rows
    r2, r3, r4 = rows[0, 2], rows[0, 3], rows[0, 4]
    assert r2['repeated_parent'] and r2['fixed_only'] and [p['id'] for p in r2['parents']] == [0, 0]
    s = summarize([r2], R.defs)
    assert s['parent_appearances']['fixed'] == 2 and s['unique_parents']['fixed'] == 1
    checks.append('repeated parent u==v: two appearances, one unique parent, fixed kept separate')
    assert r3['parents'][0] == dict(role='u', id=2, fixed=False, span=2, counts=[1, 0], spoke_before=False)
    assert r4['parents'][0]['counts'] == [1, 0] and not r4['parents'][0]['spoke_before']
    assert r4['parents'][1]['counts'] == [2, 0], 'Current lesson must increment the firing parent before the child'
    checks.append('child born before its parent first speaks: parent 2 later speaks (seq 14) but is silent at both births')
    s = summarize(rows.values(), R.defs)
    assert s['births'] == 3 and s['births_using_grown_parent_not_yet_spoken'] == 2
    assert s['births_using_one_tally_grown_parent'] == 2 and s['distinct_grown_parents'] == 1
    assert s['weak_parent_direct_children']['maximum'] == 2 and s['weak_parent_descendants']['maximum'] == 2
    checks.append('parent shared by two children: one distinct grown parent, two children, two births counted once each')
    assert R.checks['final_units'] == 2 and R.checks['removals'] == 3
    bad = copy.deepcopy(raw)
    del bad['events'][19]
    for i, e in enumerate(bad['events']):
        e['seq'] = i
    bad['events'][-1]['living'] = [0, 1, 4]                                         # so only the orphan check can refuse it
    bad['counters']['removals'] = 2
    expect_failure(bad, 'cascade removal missing a descendant')
    checks.append('cascade removal reconciles; a missing cascade removal (orphan) is refused')
    bad = copy.deepcopy(raw)
    assert bad['events'][17]['kind'] == 'remove'
    bad['events'][17]['counts'] = [0, 2]
    expect_failure(bad, 'wrong removal tally')
    bad = copy.deepcopy(raw)
    bad['speaking'][0, 2]['first_seq'] = 15
    expect_failure(bad, 'wrong speaking record')
    checks.append('corrupt removal tally and speaking record refused')
    out = dict(success=True, checks=checks, simulated_steps=0)
    BASE.with_name(BASE.name+'_checks').with_suffix('.json').write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps(out, indent=2))


def load_raw():
    data = pickle.loads(RAW.read_bytes())
    s, raw = data['summary'], data['raw']
    assert 'failure' not in s and all(s['identity'].values())
    for p, h in s['provenance']['source_sha256'].items():
        assert digest(ROOT/p) == h, ('Source changed since the trace', p)
    return raw


def run():
    started = time.monotonic()
    out = dict(success=False, checks={}, provenance=provenance(
        ('lab/growth_parent_census.py', 'lab/future_evidence.py', 'lab/future_evidence_analysis.py', 'lab/retained_prediction.py'),
        (RAW,), 'timeout --signal=TERM --kill-after=5s 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 '
        '.venv/bin/python lab/growth_parent_census.py --run'), rows_path=str(BASE.with_suffix('.pkl')))
    try:
        raw = load_raw()
        c = Census()
        R = Replay(raw, c).run()
        checks = dict(R.checks)
        for k, v in EXPECTED.items():
            got = len(R.tastes) if k == 'accepted_tastes' else checks[k]
            assert got == v, ('Expected count differs', k, got, v)
        assert len(c.rows) == EXPECTED['births']
        out['checks'] = dict(checks, expected_counts_matched=EXPECTED, parents_living_at_every_birth=True,
                             spans_add=True, no_orphan_at_any_learn_or_end=True)
        print('VALIDATION', json.dumps(out['checks']), flush=True)
        rows = list(c.rows.values())
        summary = {'all': summarize(rows, R.defs)}
        for f in FAMILIES:
            summary[f] = summarize([r for r in rows if r['family'] == f], R.defs)
        out['summary'] = summary
        out['table'] = table(summary)
        out['limits'] = ['One frozen corrected contest life; counts are structural observations, not forecasts or value.',
                         'Categories overlap (not-yet-spoken and one-tally); do not add them.',
                         'Speaking means issued native speaker at an actual prediction strictly before the birth event.',
                         'Unit counts describe software allocation, not physical cost.']
        BASE.with_suffix('.pkl').write_bytes(pickle.dumps(dict(rows=c.rows, summary=out)))
        out['success'] = True
        print(out['table'], flush=True)
        print('SUMMARY', json.dumps(summary['all']), flush=True)
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

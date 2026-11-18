"""Job 3 of PROGRAMME.md's 2026-11-18 work queue: could deleted units have supplied a missing earlier parent?

Offline only, on D84's frozen trace. For every one-tally removal u (D85's 5369), at each later native learning
call in u's stream (its deletion taste excluded): native deepest firing unit v (first longest in recorded firing
order, Net.learn's tie rule), its tally after the current label; continue only if v has seen both labels.
With s=span(v) and i the learning index, u qualifies if it would fire at i-s on the recorded history and
span(u)+s <= HIST//2. The hypothetical child word is word(u)+word(v). Equivalence checks use the pre-learning
living set (tallies just updated, before any removal inside this learn). No partner is drawn, no child born.
The trigger reconstruction is validated against every actual birth (its v is the native deep unit; its u fires
at i-s).

  .venv/bin/python lab/growth_missing_partner.py --check
  .venv/bin/python lab/growth_missing_partner.py --run
"""
from collections import defaultdict
import json
from pathlib import Path
import pickle
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'lab'), str(ROOT)]
import growth_parent_census as G
from future_evidence import activates

BASE = ROOT/'lab/v/growth_missing_partner'
HALF = 96//2                       # grownet.HIST // 2, checked against the source in --run
HORIZON = 100.
STAGE = 'pre-learning living set: tallies updated for the current label, before any removal inside this learn'


def native_deep(firing, span):
    """Net.learn: max(firing, key=span); Python's max keeps the first of equal keys."""
    return max(firing, key=span, default=None)


def opportunities(call, cands):
    """Associations of deleted candidates with one triggering call. call: stream, taste, seq, t, i, hist,
    deep_word, living_ids, living_words. cand: word, death_seq, death_taste, death_t, grown_ancestors."""
    s = len(call['deep_word'])
    out = []
    for c in cands:
        if c['death_seq'] >= call['seq'] or c['death_taste'] == call['taste']:
            continue
        if len(c['word'])+s > HALF:
            continue
        if not activates(c['word'], call['hist'], call['i']-s):
            continue
        out.append(dict(cand=c['index'], word=c['word']+call['deep_word'], u_word=c['word'],
                        concat_living=c['word']+call['deep_word'] in call['living_words'],
                        u_equivalent_living=c['word'] in call['living_words'],
                        dead_ancestors=sum(a not in call['living_ids'] for a in c['grown_ancestors']),
                        within_100s=c['death_t'] <= 200. and call['t']-c['death_t'] <= HORIZON))
    return out


class Partner:
    def __init__(self):
        self.cands = defaultdict(list)
        self.all_cands = []
        self.calls = []                 # (stream, family, taste, seq, t, associations)
        self.trigger = {}               # stream -> (learn seq, deep, i, s) of the stream's last learn
        self.validated_births = 0
        self.anc_memo = {}

    def ancestors(self, R, j, k):
        if (j, k) not in self.anc_memo:
            d = R.defs[j][k]
            a = set() if d['sym'] is not None else ({d['u'], d['v']} | self.ancestors(R, j, d['u']) | self.ancestors(R, j, d['v']))
            self.anc_memo[j, k] = a
        return self.anc_memo[j, k]

    def remove(self, R, e):
        if sum(e['counts']) != 1:
            return
        j, k = e['stream'], e['k']
        grown = {a for a in self.ancestors(R, j, k) if R.defs[j][a]['sym'] is None}
        c = dict(index=len(self.all_cands), stream=j, k=k, family=R.fam[j], word=R.words[j][k], death_seq=e['seq'],
                 death_t=e['t'], death_taste=e['taste'], grown_ancestors=grown)
        self.cands[j].append(c)
        self.all_cands.append(c)

    def learn(self, R, e):
        j = e['stream']
        span = lambda k: R.defs[j][k]['span']
        deep = native_deep(e['firing'], span)
        due = deep is not None and min(R.living[j][deep]) >= 1
        self.trigger[j] = (e['seq'], deep if due else None, e['i'], R.index[j])
        if not due:
            return
        living_ids = set(e['living'])
        call = dict(stream=j, taste=e['taste'], seq=e['seq'], t=e['t'], i=e['i'], hist=R.hist[j],
                    deep_word=R.words[j][deep], living_ids=living_ids, living_words={R.words[j][k] for k in e['living']})
        assoc = opportunities(call, self.cands[j])
        self.calls.append(dict(stream=j, family=R.fam[j], taste=e['taste'], seq=e['seq'], t=e['t'], associations=assoc))

    def birth(self, R, e, row):
        j = e['stream']
        seq, deep, i, index_now = self.trigger[j]
        d = R.defs[j][e['k']]
        assert index_now == R.index[j], 'History moved between learn and birth'
        assert deep is not None and d['v'] == deep, ('Actual birth without the reconstructed native trigger', e['seq'])
        s = R.defs[j][deep]['span']
        assert activates(R.words[j][d['u']], R.hist[j], i-s), ('Actual partner does not fire at i-s', e['seq'])
        assert d['span'] <= HALF
        self.validated_births += 1


def summarize(calls, n_cands, horizon=False):
    calls = list(calls)
    keep = (lambda a: a['within_100s']) if horizon else (lambda a: True)
    raw = qualifying_calls = 0
    occ = {}
    for c in calls:
        assoc = [a for a in c['associations'] if keep(a)]
        raw += len(assoc)
        qualifying_calls += bool(assoc)
        for a in assoc:
            key = (c['stream'], c['taste'], a['word'])
            o = occ.setdefault(key, dict(concat_living=a['concat_living'], u_equivalent_living=a['u_equivalent_living'],
                                         dead_ancestors=a['dead_ancestors'], raw=0, cands=set()))
            assert (o['concat_living'], o['u_equivalent_living']) == (a['concat_living'], a['u_equivalent_living'])
            o['dead_ancestors'] = min(o['dead_ancestors'], a['dead_ancestors'])
            o['raw'] += 1
            o['cands'].add(a['cand'])
    words = defaultdict(list)
    for (j, taste, w), o in occ.items():
        words[j, w].append(o)
    absent = [o for o in occ.values() if not o['concat_living']]
    lacking = [o for o in absent if not o['u_equivalent_living']]
    return dict(eligible_native_contradiction_calls=len(calls), calls_with_any_qualifying_deleted_parent=qualifying_calls,
                raw_candidate_associations=raw, unique_stream_taste_words=len(occ),
                unique_potential_child_words=len(words),
                unique_words_absent_from_living_memory_at_some_occurrence=sum(any(not o['concat_living'] for o in os) for os in words.values()),
                unique_words_absent_at_every_occurrence=sum(all(not o['concat_living'] for o in os) for os in words.values()),
                stream_taste_words_absent=len(absent), stream_taste_words_absent_and_no_living_equivalent_parent=len(lacking),
                unique_words_absent_and_no_living_equivalent_parent_at_some_occurrence=sum(
                    any(not o['concat_living'] and not o['u_equivalent_living'] for o in os) for os in words.values()),
                deleted_candidates_ever_qualifying=len(set().union(*[o['cands'] for o in occ.values()])) if occ else 0,
                deleted_candidates=n_cands,
                additional_dead_ancestors_per_stream_taste_word=G.distribution(o['dead_ancestors'] for o in occ.values()),
                additional_dead_ancestors_absent_no_equivalent=G.distribution(o['dead_ancestors'] for o in lacking),
                stream_taste_words_needing_no_extra_ancestor=sum(o['dead_ancestors'] == 0 for o in occ.values()))


def table(summary):
    lines = ['| family | eligible native contradiction calls | calls with a qualifying deleted parent | unique potential child words '
             '| absent from living memory (≥1 occurrence) | also lacking a living equivalent parent | extra deleted ancestors, median / max |',
             '|---|---:|---:|---:|---:|---:|---:|']
    for f, s in summary.items():
        d = s['additional_dead_ancestors_per_stream_taste_word']
        lines.append(f"| {f} | {s['eligible_native_contradiction_calls']} | {s['calls_with_any_qualifying_deleted_parent']} | "
                     f"{s['unique_potential_child_words']} | {s['unique_words_absent_from_living_memory_at_some_occurrence']} | "
                     f"{s['unique_words_absent_and_no_living_equivalent_parent_at_some_occurrence']} | "
                     f"{d.get('median', '-')} / {d.get('maximum', '-')} |")
    return '\n'.join(lines)


def check():
    checks = []
    assert native_deep([5, 3, 7], {5: 2, 3: 2, 7: 1}.get) == 5 and native_deep([], len) is None
    checks.append('native tie rule: first longest firing unit in recorded order')
    base = dict(stream=0, taste=9, seq=100, t=150., living_ids={0, 1}, living_words={(0,), (1,)})

    def cand(word, index=0, death_seq=50, death_taste=3, death_t=100., anc=()):
        return dict(index=index, word=word, death_seq=death_seq, death_taste=death_taste, death_t=death_t, grown_ancestors=set(anc))
    call = dict(base, i=2, hist={0: 0, 1: 0, 2: 1}, deep_word=(0,))
    assert opportunities(call, [cand((1,))]) == []                      # fires at i=2, not at i-s=1
    call = dict(base, i=2, hist={0: 1, 1: 0, 2: 0}, deep_word=(0,))
    assert opportunities(call, [cand((1,))]) == []                      # fires at i-2, not i-s=1
    assert len(opportunities(call, [cand((0,))])) == 1                  # fires at i-s=1
    checks.append('partner looked for at i-s, not at i or another offset')
    call = dict(base, i=3, hist={0: 0, 1: 1, 2: 0, 3: 0}, deep_word=(0, 0))
    a = opportunities(call, [cand((1,))])
    assert a and a[0]['word'] == (1, 0, 0)
    checks.append('concatenation is word(u)+word(v), not reversed')
    a = opportunities(call, [cand((1,), 0), cand((1,), 1)])
    s = summarize([dict(stream=0, family='event', taste=9, seq=100, t=150., associations=a)], 2)
    assert s['raw_candidate_associations'] == 2 and s['unique_stream_taste_words'] == 1 and s['unique_potential_child_words'] == 1
    checks.append('duplicate deleted definitions: two raw associations, one deduplicated word')
    a = opportunities(call, [cand((1,), anc={7})])
    assert a[0]['dead_ancestors'] == 1
    a = opportunities(dict(call, living_ids={0, 1, 7}), [cand((1,), anc={7})])
    assert a[0]['dead_ancestors'] == 0
    checks.append('a removed grown ancestor is counted as extra storage; a living one is not')
    hist = {i: 0 for i in range(100)}
    call = dict(base, i=99, hist=hist, deep_word=(0,))
    assert len(opportunities(call, [cand((0,)*(HALF-1))])) == 1 and opportunities(call, [cand((0,)*HALF)]) == []
    checks.append('maximum allowed span: span(u)+s == HIST//2 accepted, one more refused')
    call = dict(base, i=2, hist={0: 1, 1: 0, 2: 0}, deep_word=(0,))
    assert opportunities(call, [cand((0,), death_taste=9)]) == []
    assert opportunities(call, [cand((0,), death_seq=100)]) == [] and opportunities(call, [cand((0,), death_seq=101)]) == []
    checks.append('deletion taste and calls not strictly after the deletion are excluded')
    a = opportunities(dict(call, living_words={(0,), (1,), (0, 0)}), [cand((0,))])
    assert a[0]['concat_living'] and a[0]['u_equivalent_living']
    checks.append('living-equivalence labels for the concatenated word and for u')
    p = Partner()
    R = G.Replay(G.fixture(), p)
    try:
        R.run()
    except AssertionError as e:
        assert 'native trigger' in str(e), e
    else:
        raise AssertionError('Fixture births lack the native trigger and must be refused by birth validation')
    checks.append('birth validation refuses a birth whose deep parent has not seen both labels')
    out = dict(success=True, checks=checks, simulated_steps=0)
    BASE.with_name(BASE.name+'_checks').with_suffix('.json').write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps(out, indent=2))


def run():
    started = time.monotonic()
    out = dict(success=False, checks={}, provenance=G.provenance(
        ('lab/growth_missing_partner.py', 'lab/growth_parent_census.py', 'lab/future_evidence.py', 'lab/grownet.py'),
        (G.RAW,), 'timeout --signal=TERM --kill-after=5s 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 '
        '.venv/bin/python lab/growth_missing_partner.py --run'), rows_path=str(BASE.with_suffix('.pkl')), stage=STAGE)
    try:
        import grownet as GN
        assert GN.HIST//2 == HALF and not GN.SURP
        raw = G.load_raw()
        p = Partner()
        R = G.Replay(raw, p).run()
        assert len(p.all_cands) == R.checks['one_tally_removals'] == 5369
        assert p.validated_births == G.EXPECTED['births']
        out['checks'] = dict(R.checks, deleted_one_tally_candidates=len(p.all_cands),
                             actual_births_matching_reconstructed_trigger=p.validated_births,
                             triggering_calls=len(p.calls))
        print('VALIDATION', json.dumps(out['checks']), flush=True)
        # Structural identity: a living exact equivalent of word(u)+word(v) would fire at i and be longer than v,
        # contradicting v as the deepest firing unit; so every potential word must be absent from living memory.
        assert all(not a['concat_living'] for c in p.calls for a in c['associations'])
        out['checks']['concatenated_word_never_living_by_construction'] = True
        summary, horizon = {}, {}
        for name, keep in [('all', lambda f: True)]+[(f, (lambda g: lambda f: f == g)(f)) for f in G.FAMILIES]:
            calls = [c for c in p.calls if keep(c['family'])]
            n = sum(keep(c['family']) for c in p.all_cands)
            summary[name] = summarize(calls, n)
            horizon[name] = summarize(calls, sum(keep(c['family']) and c['death_t'] <= 200. for c in p.all_cands), True)
        out['summary'] = dict(full_remaining_life=summary, horizon_100s_deletions_by_200s=horizon)
        out['table_full'] = table(summary)
        out['table_100s'] = table(horizon)
        out['limits'] = ['An opportunity reference only: no partner drawn, no child born, no room check; it does not show the native '
                         'random draw would choose u, that a child would predict well, or that keeping u beats what the cap removes.',
                         'Zero narrows only the earlier-partner route; a deleted unit could instead be the deepest unit.',
                         'Equivalence is checked on the pre-learning living set, not the post-recycling partner pool.',
                         'Extra deleted ancestors overlap between candidates; their storage cannot be summed.',
                         'One frozen corrected contest life; counts are software allocation, not physical cost.']
        BASE.with_suffix('.pkl').write_bytes(pickle.dumps(dict(calls=p.calls, candidates=p.all_cands, summary=out)))
        out['success'] = True
        print('FULL REMAINING LIFE\n'+out['table_full'], flush=True)
        print('100 s HORIZON, DELETIONS BY 200 s\n'+out['table_100s'], flush=True)
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

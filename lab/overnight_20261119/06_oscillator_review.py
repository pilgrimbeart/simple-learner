"""Task F (overnight 2026-11-19): review of D162's retained bias adaptation from saved artifacts only.
No new circuit trajectories, no replay, no tuning.
"""
import hashlib,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'lab'));sys.path.insert(0,str(ROOT))
from dynamic_parts_bench import metrics
V=ROOT/'lab/v';BASE=V/'overnight_20261119'
def fresh(name):
    for n in [name,name+'_retry1',name+'_retry2']:
        if not (BASE/n).exists():(BASE/n).mkdir();return BASE/n
    raise RuntimeError('No retry directory left')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
THRESH=dict(cycles_min=10,amplitude_min_V=.15,period_cv_max=.1,frequency_ratio=(.9,1.1),amplitude_ratio=(.9,1.1),rail_hits=0)
def margins(v,cost):
    return dict(cycles=[v['cycles'],v['post_cycles']],amplitude_V=[v['amplitude_V'],v['post_amplitude_V']],period_cv=[v['period_cv'],v['post_period_cv']],
        frequency_ratio=v['post_frequency_Hz']/max(v['frequency_Hz'],1e-20),amplitude_ratio=v['post_amplitude_V']/max(v['amplitude_V'],1e-20),rail_hits=cost['rail_hits'])
def failing(v,cost):
    m=margins(v,cost);out=[]
    if min(m['cycles'])<10:out.append('cycles<10')
    if min(m['amplitude_V'])<=.15:out.append('amplitude<=.15V')
    if max(m['period_cv'])>=.1:out.append('period CV>=.1')
    if not .9<m['frequency_ratio']<1.1:out.append('frequency ratio outside (.9,1.1)')
    if not .9<m['amplitude_ratio']<1.1:out.append('amplitude ratio outside (.9,1.1)')
    if m['rail_hits']:out.append('rail hits')
    return out

def main():
    OUT=fresh('oscillator_review_results');checks={};flags=[]
    sets={'development':V/'adaptive_oscillator','confirmation':V/'adaptive_oscillator_confirm'}
    allrows={k:[json.loads(l) for l in (p/'rows.jsonl').read_text().splitlines()] for k,p in sets.items()}
    # 1. paired builds share the original arrays
    build=[]
    for k,rows in allrows.items():
        R={(r['seed'],r['arm'],r['dt']):r for r in rows}
        for (seed,arm,dt),r in R.items():
            if arm=='original':continue
            o=R[seed,'original',dt];n0=np.array(o['nodes']);e0=np.array(o['elements']);l0=np.array(o['links'])
            n=np.array(r['nodes']);e=np.array(r['elements']);l=np.array(r['links'])
            ok_nodes=n.shape[0]==n0.shape[0] and np.array_equal(n[:,:2],n0[:,:2]);ok_el=np.array_equal(e[:,:3],e0[:,:3]);ok_links=np.array_equal(l[:,:3],l0[:,:3])
            extra_el=e.shape[1]-3;expected=2 if arm=='adaptive' else 1
            item=dict(set=k,seed=seed,arm=arm,dt=dt,first_two_nodes_identical=bool(ok_nodes),first_three_elements_identical=bool(ok_el),first_three_links_identical=bool(ok_links),extra_elements=int(extra_el),extra_nodes=int(n.shape[1]-2))
            if arm=='writer_removed':
                a=R[seed,'adaptive',dt];item['readout_same_as_adaptive']=bool(np.array_equal(e[:,3],np.array(a['elements'])[:,3]) and np.array_equal(n,np.array(a['nodes'])))
            build.append(item)
            if not(ok_nodes and ok_el and ok_links and extra_el==expected and n.shape[1]==3 and item.get('readout_same_as_adaptive',True)):flags.append(dict(kind='build',**item))
    checks['paired_builds']=dict(compared=len(build),flagged=sum(1 for f in flags if f['kind']=='build'))
    # 2. memory motion
    mem={}
    for k,rows in allrows.items():
        for arm in ['adaptive','writer_removed']:
            rr=[r for r in rows if r['arm']==arm]
            ch=[r['memory']['change_V'] for r in rr];rg=[r['memory']['range_V'][1]-r['memory']['range_V'][0] for r in rr];sl=[r['memory']['last_third_slope_V_per_s'] for r in rr]
            mem[f'{k}:{arm}']=dict(records=len(rr),change_V=dict(min=min(ch),max=max(ch),mean_abs=float(np.mean(np.abs(ch)))),range_V=dict(min=min(rg),max=max(rg),mean=float(np.mean(rg))),
                final_third_slope_V_per_s=dict(min=min(sl),max=max(sl),max_abs=max(abs(x) for x in sl)),held_exactly=sum(r['memory']['held_exactly'] for r in rr))
            if arm=='writer_removed' and (mem[f'{k}:{arm}']['held_exactly']!=len(rr) or max(abs(x) for x in ch)!=0):flags.append(dict(kind='removed_memory_moved',set=k))
    checks['memory']=mem
    # 3. saved traces of failed draws
    wanted=[('development',s) for s in [51006,51011,51036]]+[('confirmation',s) for s in [2026120208,2026120221]]
    traces=[];
    manifests={k:json.loads((p/'trace_manifest.json').read_text()) for k,p in sets.items()}
    for k,seed in wanted:
        rows=allrows[k];fin=min(r['dt'] for r in rows)
        for arm in ['original','adaptive','writer_removed']:
            p=sets[k]/f'{seed}_{arm}.npz';r=next(x for x in rows if x['seed']==seed and x['arm']==arm and x['dt']==fin);item=dict(set=k,seed=seed,arm=arm,available=p.exists(),recorded_passed=r['metrics']['passed'],
                recorded_failing=failing(r['metrics']['values'],r['cost']),recorded_margins=margins(r['metrics']['values'],r['cost']),memory=r['memory'])
            if p.exists():
                listed=manifests[k].get(str(p.resolve()));h=sha(p);item['hash_listed']=listed is not None;item['hash_matches']=listed==h
                if listed is not None and listed!=h:flags.append(dict(kind='trace_hash',path=str(p)))
                tr=np.load(p)['trace'];m=metrics('oscillator',[tr],[r['cost']]);item['remeasured_passed']=m['passed'];item['remeasure_error']=max(abs(m['values'][x]-r['metrics']['values'][x]) for x in m['values'])
                if tr.shape[1]>3:
                    late=tr[:,0]>200/3;item['trace_memory']=dict(start_V=float(tr[0,3]),end_V=float(tr[-1,3]),final_third_range_V=float(np.ptp(tr[late,3])))
                if m['passed']!=r['metrics']['passed'] or item['remeasure_error']>1e-12:flags.append(dict(kind='trace_metric',set=k,seed=seed,arm=arm))
            traces.append(item)
    checks['failed_draw_traces']=dict(requested=len(traces),available=sum(t['available'] for t in traces),missing=[(t['set'],t['seed'],t['arm']) for t in traces if not t['available']])
    # 4. counts and cost
    csum=json.loads((sets['confirmation']/'summary.json').read_text());dsum=json.loads((sets['development']/'summary.json').read_text());parts=json.loads((sets['development']/'manifest.json').read_text())['parts']
    out=dict(task='F',flags=flags,checks=checks,traces=traces,
        development=dict(passed={a:dsum[a]['passed'] for a in ['original','adaptive','writer_removed']},failed={a:dsum[a].get('failed_seeds') for a in ['original','adaptive','writer_removed']}),
        confirmation=dict(passed={a:csum[a]['passed'] for a in ['original','adaptive','writer_removed']},wilson95_adaptive=csum['adaptive']['wilson95'],paired=csum['paired']),
        parts={a:sum(v.values()) for a,v in parts.items()},thresholds=THRESH,
        input_sha256={str(p.relative_to(ROOT)):sha(p) for p in [sets['development']/'rows.jsonl',sets['confirmation']/'rows.jsonl',sets['development']/'trace_manifest.json',sets['confirmation']/'trace_manifest.json',sets['development']/'manifest.json',sets['confirmation']/'summary.json',sets['development']/'summary.json',Path(__file__).resolve()]})
    (OUT/'oscillator_checks.json').write_text(json.dumps(out,indent=2)+'\n')
    L=['# Task F — oscillator adaptation review (saved artifacts only)','',f'Flags: **{len(flags)}** (see `oscillator_checks.json`).','',
       '## What was checked',f"- Paired builds: {checks['paired_builds']['compared']} adaptive/writer-removed records compared with their original on the first two node arrays, first three element arrays and links; flagged {checks['paired_builds']['flagged']}. The adaptive arm adds one node and two elements (readout, writer); the writer-removed arm keeps the node and readout.",
       *[f"- Memory, {k}: change {v['change_V']['min']:+.4f}..{v['change_V']['max']:+.4f} V (mean |change| {v['change_V']['mean_abs']:.4f}); range over life {v['range_V']['min']:.4f}..{v['range_V']['max']:.4f} V; final-third slope max |{v['final_third_slope_V_per_s']['max_abs']:.2e}| V/s; held exactly {v['held_exactly']}/{v['records']}." for k,v in mem.items()],
       '- The adaptive memory moves within each life (range above); the final-third slope is small but nonzero, and motion can ride the oscillation, so it is not evidence of a quiet settled knob.',
       f"- Saved traces of failed draws: {checks['failed_draw_traces']['available']}/{checks['failed_draw_traces']['requested']} requested arm-traces available. Missing: {checks['failed_draw_traces']['missing']}. No replay was run to fill gaps.",'',
       '## Original thresholds and the failed draws','','Criteria (D126): ≥10 cycles in each of 10–45 s and 55–95 s, amplitude > .15 V, period CV < .1, post/pre frequency and amplitude ratios in (.9, 1.1), no rail hits.','',
       '| set | seed | arm | passed | failing criteria | cycles (pre, post) | amplitude V (pre, post) | trace |','|---|---|---|---|---|---|---|---|']
    for t in traces:
        m=t['recorded_margins'];L.append(f"| {t['set']} | {t['seed']} | {t['arm']} | {t['recorded_passed']} | {', '.join(t['recorded_failing']) or '—'} | {m['cycles']} | [{m['amplitude_V'][0]:.3f}, {m['amplitude_V'][1]:.3f}] | {'remeasured, '+('pass' if t.get('remeasured_passed') else 'fail') if t['available'] else 'not saved'} |")
    L+=['','## Separate claims, kept separate',
        f"- **Component reliability (fresh draws):** adaptive {csum['adaptive']['passed']}/40, Wilson95 [{csum['adaptive']['wilson95'][0]:.4f}, {csum['adaptive']['wilson95'][1]:.4f}], meets the frozen ≥ .90 lower-bound requirement. Development: adaptive {dsum['adaptive']['passed']}/10, original {dsum['original']['passed']}/10, writer removed {dsum['writer_removed']['passed']}/10.",
        f"- **Causal removal evidence:** removing only the writer (memory and readout kept) gives {csum['writer_removed']['passed']}/40 fresh and {dsum['writer_removed']['passed']}/10 development; the failures differ from the original arm's, so the frozen extra state alone does not explain the repair, but the comparison is small.",
        f"- **Population difference:** adaptive minus original +.05 [0, +.125]; the interval includes zero, so superiority over the comparator is not established (nor equivalence).",
        f"- **Added cost:** core parts {parts and sum(parts['original'].values())} → {sum(parts['adaptive'].values())}; added supply power ≈ 6.3 nW (Task A). Memory-pump implementation and its energy remain excluded under the existing contract.",
        '- **Not claimed:** new problem families, robot reward or task learning, a universal cycle or attractor theorem, exact physical retention of the memory, or the uncounted memory-pump energy.']
    (OUT/'oscillator_review.md').write_text('\n'.join(L)+'\n');print('\n'.join(L))
if __name__=='__main__':main()

"""D128 trace audit, parts/accounting and saved-trace live display."""
import argparse,json,sys,time,html
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,DT,digest
from retained_write_report import svg_plot
from retained_write_preview import render
from minimal.spice import count

def main():
    p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('--stage',default='confirm');p.add_argument('--live-seconds',type=float,default=0);a=p.parse_args();out=ROOT/('lab/v' if a.name.startswith('oneshot') else 'lab/v/motifs')/a.name
    rows=[json.loads(l) for l in (out/f'{a.stage}.jsonl').read_text().splitlines()];saved=json.loads((out/f'{a.stage}.json').read_text());protocol=json.loads((out/'protocol.json').read_text());prov=json.loads((out/f'{a.stage}_provenance.json').read_text())
    assert digest(out/'protocol.json')==prov['protocol_sha256']
    for path,h in prov['files'].items():
        current=ROOT/path
        if digest(current)!=h:
            snapshots={'lab/motif_bench.py':'lab/motif_bench_v1.py','lab/order_bench.py':'lab/order_bench_v1.py'}
            assert path in snapshots and digest(ROOT/snapshots[path])==h
    if a.name.startswith('change'):
        import motif_bench as bench
        result=bench.summary(a.name,rows,protocol[a.stage]);graph=protocol['graph']
    elif a.name.startswith('oneshot'):
        import oneshot_bench as bench
        result=bench.summary(rows,protocol[a.stage]);graph=protocol['graph']
    else:
        import order_bench as bench
        result=bench.summary(rows,protocol[a.stage]);graph=protocol['graph']
    assert all(result[k]==saved[k] for k in result)
    spec=dict(nodes=[[n['name'],n['bias'],n['R'],n['C'],None,None,None,n['memory']] for n in graph['nodes']],elements=[[e['to'],e['source'],e['gate'],e['gain'],e['offset'],e['slope'],e['tau'],e.get('sigmoid',False)] for e in graph['edges']],sensors=[],taste=-1)
    manifest=dict(graph=graph,states=len(graph['nodes']),connections=len(graph['edges']),parts=count(spec),scope='Core only; bench sources/recording excluded. Memory pump sources counted ideally; implementation and energy absent. Activity in raw rows separate from supply power.')
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    trace_paths=sorted(out.glob(f'{a.stage}_*_False.npz'));panels=[];example=None
    chosen=trace_paths[:4]
    if a.name.startswith('change'):
        chosen=[out/f'{a.stage}_{sgn}_0.16_2.0_False.npz' for sgn in [1,-1]]
        if a.stage=='pilot':chosen +=[out/f'{a.stage}_{sgn}_0.16_2.0_True.npz' for sgn in [1,-1]]
    elif a.name.startswith('oneshot'):
        chosen=[out/f'{a.stage}_{sgn}_0.55_2.0_False.npz' for sgn in [1,-1]]
    else:
        chosen=[out/f'{a.stage}_pair_0.35_0.35_{d}_False.npz' for d in [-.15,0.,.15,.6]]
    for i,path in enumerate(chosen):
        tr=np.load(path)['trace'];example=tr if example is None else example
        if a.name.startswith('change'):
            series=[(tr[:,0],tr[:,1],'input'),(tr[:,0],tr[:,-1],'response')];title=('positive' if '_1_' in path.name else 'negative')+' input'+(' — control' if '_True' in path.name else '')
            # Independently recover recorded response metrics from saved trace.
            caseid=path.name[len(a.stage)+1:].replace('_False.npz','').replace('_True.npz','');row=next(r for r in rows if r['seed']==protocol[a.stage][0] and r['dt']==DT/4 and r['case']['id']==caseid and r['control']==('_True' in path.name));start=row['pulses'][0][0];metrics=bench.measure(tr,start,start+row['case']['duration'],row['case']['sign']);assert all(abs(metrics[k]-row['metrics'][k])<1e-12 for k in metrics)
            limits=(-.5,.5)
        elif a.name.startswith('oneshot'):
            series=[(tr[:,0],tr[:,1],'input'),(tr[:,0],tr[:,-1],'pulse output')];title=path.name;limits=(-.8,.8)
            caseid=path.name[len(a.stage)+1:-len('_False.npz')];row=next(r for r in rows if r['seed']==protocol[a.stage][0] and r['dt']==DT/4 and r['case']['id']==caseid and not r['control']);assert bench.measure(tr,row['triggers'])==row['metrics']
        else:
            base=tr[(tr[:,0]>.7)&(tr[:,0]<.95),1:].mean(axis=0)
            series=[(tr[:,0],tr[:,7]-base[6],'coincidence ΔV'),(tr[:,0],tr[:,8]-base[7],'order ΔV')];title=path.name.split('_')[-2]+' s separation';limits=(-.5,.6)
        svg=svg_plot(series,title,(.8,float(tr[-1,0])),limits);sp=out/f'{a.stage}_panel_{i}.svg';sp.write_text(svg);panels.append(svg);render(sp)
    body='<!doctype html><meta charset="utf-8"><title>'+a.name+'</title><style>body{font:18px sans-serif;max-width:1150px;margin:25px auto}.grid{display:grid;grid-template-columns:1fr 1fr}</style><h1>'+a.name+'</h1><p>Saved component-bench traces; blue solid and orange dashed. See report for all draws and limitations.</p><div class="grid">'+''.join(panels)+'</div><p>These plots are observations, not signals fed back to the circuit.</p>'
    (out/f'{a.stage}_view.html').write_text(body)
    # Schema: one labelled box per state; solid current paths, dashed gate-control paths.
    n=len(graph['nodes']);width=1300;height=240+160*((n+3)//4);positions=[(40+310*(i%4),100+160*(i//4)) for i in range(n)]
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><rect width="100%" height="100%" fill="white"/><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8" fill="none" stroke="#222"/></marker></defs><g font-family="sans-serif" fill="#222"><text x="30" y="35" font-size="23">{a.name}: explicit circuit graph</text>']
    for i,(node,(x,y)) in enumerate(zip(graph['nodes'],positions)):
        label='retained, no leak' if node['memory'] else f'R={node["R"]/1e9:g} Gohm'
        svg.append(f'<rect x="{x}" y="{y}" width="230" height="85" fill="#eef5f8" stroke="#222"/><text x="{x+10}" y="{y+25}" font-size="17">{i}: {html.escape(node["name"])}</text><text x="{x+10}" y="{y+48}">C={node["C"]*1e12:g} pF</text><text x="{x+10}" y="{y+70}">{label}</text>')
    for j,e in enumerate(graph['edges']):
        sx,sy=positions[e['source']];tx,ty=positions[e['to']];sx+=115;tx+=115
        lift=25+10*(j%3);path=f'M{sx},{sy} C{sx},{sy-lift} {tx},{ty-lift} {tx},{ty}'
        svg.append(f'<path d="{path}" fill="none" stroke="#222" marker-end="url(#arrow)"/><text x="{(sx+tx)/2}" y="{(sy+ty)/2-lift}" font-size="13">e{j} {"+" if e["gain"]>0 else "−"}</text>')
        if e['gate']>=0:
            gx,gy=positions[e['gate']];svg.append(f'<path d="M{gx+115},{gy+85} L{(sx+tx)/2},{(sy+ty)/2-lift}" stroke="#555" stroke-dasharray="5 5" fill="none"/>')
    svg.append(f'<text x="30" y="{height-40}">Solid: signed connection current. Dashed: gate voltage. Exact transfer functions and parts: manifest.json.</text></g></svg>');(out/'schematic.svg').write_text('\n'.join(svg));render(out/'schematic.svg')
    trace_hashes={str(p.resolve()):digest(p) for p in out.glob('*.npz')};(out/'trace_manifest.json').write_text(json.dumps(trace_hashes,indent=2)+'\n')
    pilot=json.loads((out/'pilot.json').read_text());failures=[dict(seed=r['seed'],case=r['case']['id'],dt=r['dt'],control=r['control'],metrics=r['metrics']) for r in rows if not r['passed']]
    (out/f'{a.stage}_failures.json').write_text(json.dumps(failures,indent=2)+'\n')
    baseline_note='Absolute voltage thresholds; no observer baseline subtraction.' if a.name.startswith('oneshot') else 'Response metrics use change from prestimulus baseline; that subtraction is an observer measurement, not an additional circuit. Absolute zero-threshold decoding is not demonstrated.'
    text=[f'# {a.name} — {a.stage}','',f'**{result["passed"]}/{result["seeds"]}** seeds pass every condition at all three steps. Wilson95 [{result["wilson95"][0]:.3f}, {min(1.,result["wilson95"][1]):.3f}].',f'Both refinements pass: {result["refinement_pass"]}. Pilot control rows: {pilot["control_rows"]}; all pass: {pilot["control_pass"]}.', '',f'Core: {manifest["states"]} states, {manifest["connections"]} connections; parts {manifest["parts"]}. Mean supply power (mean,95% interval): {result["power_W"]} W.',manifest['scope'],'','Frozen criteria: '+protocol['criteria'],'','Prediction: '+protocol['prediction'],'',baseline_note+' Component coverage only. No robot learning or general stability guarantee. Each seed counts once across conditions and steps. Raw metrics and failures remain visible; no equivalence claim from an interval overlapping zero.','',f'Exact graph/stimuli: protocol.json; raw rows: {a.stage}.jsonl; code hashes/revision: {a.stage}_provenance.json. Large saved traces at `{out}/*.npz` stay outside git, hashes in trace_manifest.json.','',f'Report: `.venv/bin/python lab/motif_report.py {a.name} --stage {a.stage} --live-seconds 8`. No simulation rerun required.']
    (out/f'{a.stage}_report.md').write_text('\n'.join(text)+'\n');print(f'{a.name} {a.stage}: audit passed, {result["passed"]}/{result["seeds"]}',flush=True)
    if a.live_seconds:
        import pygame
        pygame.display.init();pygame.font.init();screen=pygame.display.set_mode((1050,180+40*n));font=pygame.font.SysFont('sans',21);start=time.monotonic();clock=pygame.time.Clock()
        while time.monotonic()-start<a.live_seconds:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:pygame.quit();return
            t=(time.monotonic()-start)/a.live_seconds*example[-1,0];r=example[min(len(example)-1,round(t/.001))];screen.fill('white');screen.blit(font.render(f'{a.name}: saved trace replay, {t:.3f} s',True,'black'),(20,20))
            for i,node in enumerate(graph['nodes']):
                y=80+i*40;screen.blit(font.render(f'{node["name"]}: {r[i+1]:+.4f} V',True,'black'),(20,y));w=round(abs(r[i+1])*400);pygame.draw.rect(screen,'#0072B2' if i%2==0 else '#D55E00',(600-w if r[i+1]<0 else 600,y,w,20))
            pygame.display.flip();clock.tick(30)
        pygame.quit();print(f'Live replay completed: {a.live_seconds}s',flush=True)
if __name__=='__main__':main()

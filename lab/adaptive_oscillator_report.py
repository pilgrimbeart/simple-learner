"""D162 saved-trace audit, complete macro schematic/count and optional live replay."""
import argparse,json,html,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from adaptive_oscillator import OUT,graph,DT,SEEDS
from dynamic_parts_bench import definitions,digest,metrics,interval
from minimal.spice import count
from retained_write_report import svg_plot
from retained_write_preview import render

def main():
    p=argparse.ArgumentParser();p.add_argument('--live-seconds',type=float,default=0);args=p.parse_args()
    rows=[json.loads(l) for l in (OUT/'rows.jsonl').read_text().splitlines()];assert len(rows)==90 and len({(r['seed'],r['arm'],r['dt']) for r in rows})==90
    saved=json.loads((OUT/'summary.json').read_text());error=0.;traces={}
    for r in rows:
        if r['dt']!=DT/4:continue
        tr=np.load(OUT/f'{r["seed"]}_{r["arm"]}.npz')['trace'];m=metrics('oscillator',[tr],[r['cost']])
        assert m['passed']==r['metrics']['passed'];error=max(error,max(abs(m['values'][k]-r['metrics']['values'][k]) for k in m['values']))
        if r['seed']==51006:traces[r['arm']]=tr
    assert error<1e-12
    counts={}
    for arm in ['original','adaptive','writer_removed']:
        g=definitions()['oscillator'] if arm=='original' else graph();es=g['edges'][:-1] if arm=='writer_removed' else g['edges']
        spec=dict(nodes=[[n['name'],n['bias'],n['R'],n['C'],None,None,None,n['memory']] for n in g['nodes']],elements=[[e['to'],e['source'],e['gate'],e['gain'],e['offset'],e['slope'],e['tau'],False] for e in es],sensors=[],taste=-1)
        counts[arm]=count(spec)
    power={arm:{r['seed']:r['cost']['power_W'] for r in rows if r['arm']==arm and r['dt']==DT/4} for arm in counts}
    delta=interval([power['adaptive'][s]-power['original'][s] for s in SEEDS])
    manifest=dict(parts=counts,power_difference_W=delta,scope='Complete circuit core; external bench pulse/observer excluded. Memory pump implementation and energy remain excluded under existing contract. Selected development draws, no fresh reliability claim.')
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    g=graph();svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1050" height="670"><rect width="1050" height="670" fill="white"/><g font-family="sans-serif" fill="#222"><text x="25" y="30" font-size="23">D162: local retained bias adjustment</text>']
    pos=[(90,90),(450,90),(780,90)]
    for i,(n,(x,y)) in enumerate(zip(g['nodes'],pos)):
        svg.append(f'<rect x="{x}" y="{y}" width="180" height="110" fill="#eef5f8" stroke="#222"/>')
        labels=[f'{i}: {n["name"]}',f'C={n["C"]*1e12:g}pF','retained, no leak' if n['R'] is None else f'R={n["R"]/1e9:g}Gohm']
        for j,label in enumerate(labels):svg.append(f'<text x="{x+8}" y="{y+25+30*j}">{html.escape(label)}</text>')
    for j,e in enumerate(g['edges']):
        sx=pos[e['source']][0]+60;tx=pos[e['to']][0]+110;y=235+45*j
        path=f'M{sx} 200 V{y} H{tx} V200'
        svg.append(f'<path d="{path}" fill="none" stroke="#222"/><text x="{min(sx,tx)+10}" y="{y-5}">E{j}: {e["source"]} to {e["to"]}, {"positive" if e["gain"]>0 else "negative"}</text>')
        svg.append(f'<text x="25" y="{495+27*j}">E{j}: gain {e["gain"]*1e12:g}pA; slope {e["slope"]:.4g}/V; offset 0V; no gate or filter</text>')
    svg.append('</g></svg>');(OUT/'schematic.svg').write_text('\n'.join(svg));render(OUT/'schematic.svg')
    plots=[]
    for index,(window,title) in enumerate([((0,10),'Development draw51006: startup'),((60,62),'Development draw51006: sustained response')]):
        series=[(traces[a][:,0],traces[a][:,1],label) for a,label in [('original','original'),('adaptive','adaptive'),('writer_removed','writer removed')]]
        text=svg_plot(series,title,window,(-.5,.5));path=OUT/f'panel_{index}.svg';path.write_text(text);render(path);plots.append(text)
    tr=traces['adaptive'];text=svg_plot([(tr[:,0],tr[:,3],'bias memory')],'The circuit writes its own correction',(0,100),(-.4,.4));(OUT/'memory.svg').write_text(text);render(OUT/'memory.svg');plots.append(text)
    (OUT/'view.html').write_text('<!doctype html><meta charset="utf-8"><title>Adaptive oscillator</title><h1>Development diagnostic, not confirmation</h1>'+''.join(plots))
    report=['# Local bias adaptation — development result','', 'Original7/10, adaptive10/10, writer removed6/10 across all three steps. Original criteria unchanged; all refinement checks pass. The selected set includes the previously failed component draws, so these are not fresh reliability estimates.',f'Parts: {counts}. Paired added power mean/95% bootstrap: {delta} W.', 'The memory is written by the oscillator’s own voltage and alters its bias through an explicit connection. No outside frequency, phase or state assignment is supplied. The control holds the memory exactly. This supports the operating-point explanation on these draws; it is not robot learning or a universal cycle theorem.', 'Fresh confirmation is still required. Activity, memory motion and supply power are retained separately in rows.jsonl. Every saved finest trace was remeasured; source hashes and trace_manifest.json identify the data.']
    (OUT/'report.md').write_text('\n\n'.join(report)+'\n');(OUT/'trace_manifest.json').write_text(json.dumps({str(p.resolve()):digest(p) for p in OUT.glob('*.npz')},indent=2)+'\n')
    (OUT/'audit.json').write_text(json.dumps(dict(rows=len(rows),saved_trace_metric_error=error,script_sha256=digest(Path(__file__))),indent=2)+'\n')
    print(json.dumps(manifest,indent=2),flush=True)
    if args.live_seconds:
        import pygame
        pygame.display.init();pygame.font.init();screen=pygame.display.set_mode((1050,540));font=pygame.font.SysFont('sans',22);clock=pygame.time.Clock();start=time.monotonic()
        while time.monotonic()-start<args.live_seconds:
            elapsed=time.monotonic()-start;at=60+elapsed
            for event in pygame.event.get():
                if event.type==pygame.QUIT:pygame.quit();raise RuntimeError('Replay closed early')
            screen.fill('white');screen.blit(font.render(f'D162 saved noisy development trace51006; t={at:.2f}s',True,'black'),(20,15))
            for j,(arm,label,col) in enumerate([('original','Original','#555555'),('adaptive','Adaptive','#0072B2'),('writer_removed','Writer removed','#D55E00')]):
                tr=traces[arm];mask=(tr[:,0]>=at-2)&(tr[:,0]<=at);tt=tr[mask,0];yy=tr[mask,1];base=110+150*j
                screen.blit(font.render(label,True,'black'),(15,base-45));pts=[(int(240+(t-at+2)*390),int(base-v*100)) for t,v in zip(tt[::3],yy[::3])]
                pygame.draw.line(screen,'#cccccc',(240,base),(1020,base))
                if len(pts)>1:pygame.draw.lines(screen,col,False,pts,2)
            pygame.display.flip();clock.tick(30)
        pygame.quit();print('Live saved-trace replay completed',flush=True)
if __name__=='__main__':main()

"""D131 audit, accounting, schematic and live saved-trace replay."""
import argparse,json,sys,time,html
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from quiet_write_bench import OUT,PILOT,CONFIRM,DT,summary,graph,digest,ROOT
from retained_write_report import svg_plot
from retained_write_preview import render
from minimal.spice import count

def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',default='confirm');p.add_argument('--live-seconds',type=float,default=0);a=p.parse_args();rows=[json.loads(l) for l in (OUT/f'{a.stage}.jsonl').read_text().splitlines()];ss=PILOT if a.stage=='pilot' else CONFIRM
    result=summary(rows,ss);saved=json.loads((OUT/f'{a.stage}.json').read_text());assert all(result[k]==saved[k] for k in result);prov=json.loads((OUT/f'{a.stage}_provenance.json').read_text());assert prov['protocol_sha256']==digest(OUT/'protocol.json')
    for path,h in prov['files'].items():assert digest(ROOT/path)==h
    g=graph();spec=dict(nodes=[[n['name'],n['bias'],n['R'],n['C'],None,None,None,n['memory']] for n in g['nodes']],elements=[[e['to'],e['source'],e['gate'],e['gain'],e['offset'],e['slope'],e['tau'],e['sigmoid']] for e in g['edges']],sensors=[],taste=-1)
    manifest=dict(graph=g,states=6,connections=4,parts=count(spec),scope='Core only. Two ideal pump supplies counted; actual pump implementation/energy and bench sources/readout excluded. Activity separate in raw rows.')
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');primary=[r for r in rows if r['control']=='none' and r['dt']==DT/4];null=[r for r in primary if abs(r['amplitude'])<.5];useful=[r for r in primary if abs(r['amplitude'])==.5]
    maximum_null=max(abs(r['metrics']['write_V']) for r in null);minimum_useful=min(np.sign(r['amplitude'])*r['metrics']['write_V'] for r in useful)
    lines=['# Absence-preserving writes — D131','',f'**{result["passed"]}/{result["seeds"]}** component draws pass all5conditions and all3steps. Wilson95 [{result["wilson95"][0]:.3f},{min(1.,result["wilson95"][1]):.3f}].',f'Refinements pass: {result["refinement_pass"]}. Pilot removal controls:240rows; all pass: '+str(json.loads((OUT/'pilot.json').read_text())['control_pass'])+'.','',
        'Two thresholded writer paths create an explicit no-write region. Negative evidence reaches its writer through a noisy inverting state. The previous global noise/write-driver model is unchanged. Evidence amplitude +/- .5V is accepted; +/- .05V is intentionally rejected. This sacrifices sensitivity, adds parts and does not learn the threshold or eligibility rule.','',f'Maximum absolute absent/weak write: {maximum_null:.6g}V. Minimum useful signed write: {minimum_useful:.6g}V.',f'Core:6states,4connections; parts {manifest["parts"]}. Mean power (mean,95%interval): {result["power_W"]}W.',manifest['scope'],'',
        'The new gate-only test holds eligibility open for1s, versus.25s in D129. This is a capability check, not a paired power/performance comparison between the old and new circuits. All raw null cases remain visible. Hold follows the existing idle-memory-noise assumption. No signed learned-weight, delay-credit, robot-learning or empirical retention claim.','',
        'Protocol, full rows, provenance and source hashes are retained. Large traces at '+str(OUT)+'/*.npz stay outside git; trace_manifest.json contains hashes. Source:lab/quiet_write_bench.py; audit/report:lab/quiet_write_report.py. Existing results are never overwritten by the runner.']
    (OUT/f'{a.stage}_report.md').write_text('\n'.join(lines)+'\n')
    panels=[];example=None
    for i,amp in enumerate([.5,-.5,0.,.05]):
        tr=np.load(OUT/f'{a.stage}_{amp}_none.npz')['trace'];t=tr[:,0];m=tr[:,3];r=next(r for r in primary if r['seed']==ss[0] and r['amplitude']==amp)
        delta=m[(t>2.5)&(t<2.9)].mean()-m[(t>.8)&(t<.95)].mean();assert abs(delta-r['metrics']['write_V'])<1e-12
        panels.append(svg_plot([(t,m,'stored'),(t,tr[:,2],'eligibility')],f'Evidence={amp:+g} V nominal',(.8,3),(-.05,.75)));p=OUT/f'{a.stage}_panel_{i}.svg';p.write_text(panels[-1]);render(p)
        if amp==.5:example=tr
    (OUT/f'{a.stage}_view.html').write_text('<!doctype html><meta charset="utf-8"><title>No-write region</title><style>body{font:18px sans-serif;max-width:1120px;margin:25px auto}.grid{display:grid;grid-template-columns:1fr 1fr}</style><h1>Explicit no-write region</h1><p>Saved traces: stored voltage blue solid, eligibility orange dashed. See report for all draws and limitations.</p><div class="grid">'+''.join(panels)+'</div>')
    positions=[(40,100),(400,100),(760,100),(40,300),(760,300),(400,300)];svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1140" height="760"><rect width="1140" height="760" fill="white"/><g font-family="sans-serif" fill="#222"><text x="25" y="35" font-size="24">D131: six explicit states, four connections</text>']
    for i,(node,(x,y)) in enumerate(zip(g['nodes'],positions)):
        leak='retained; no leak' if node['memory'] else f'R={node["R"]/1e9:g} Gohm'
        svg.append(f'<rect x="{x}" y="{y}" width="250" height="90" fill="#eef5f8" stroke="#222"/><text x="{x+10}" y="{y+25}" font-size="17">{i}: {html.escape(node["name"])}</text><text x="{x+10}" y="{y+50}">C=25 pF</text><text x="{x+10}" y="{y+75}">{leak}</text>')
    for i,e in enumerate(g['edges']):
        x,y=positions[e['source']];xx,yy=positions[e['to']];lift=30+20*i
        svg.append(f'<path d="M{x+125} {y} C{x+125} {y-lift}, {xx+125} {yy-lift}, {xx+125} {yy}" stroke="#222" fill="none"/><text x="{(x+xx)/2+125}" y="{(y+yy)/2-lift}" font-size="15">E{i} {"+" if e["gain"]>0 else "−"}</text>')
        fun='sigmoid' if e['sigmoid'] else 'tanh';gate='; gate '+g['nodes'][e['gate']]['name'] if e['gate']>=0 else ''
        label=f'E{i}: {g["nodes"][e["source"]]["name"]} to {g["nodes"][e["to"]]["name"]}; {e["gain"]*1e12:g} pA × {fun}({e["slope"]:.4g}/V × (source−{e["offset"]:g}V)){gate}'
        svg.append(f'<text x="25" y="{480+40*i}" font-size="14">{html.escape(label)}</text>')
    svg.append('<text x="25" y="690">Control gates clip voltage / .3 V to [0,1]. Each writer retains the original 1% dead zone.</text><text x="25" y="720">Bench currents enter evidence, eligibility and probe. Every signal-shaping state is explicit and noisy.</text></g></svg>');(OUT/'schematic.svg').write_text('\n'.join(svg));render(OUT/'schematic.svg')
    (OUT/'trace_manifest.json').write_text(json.dumps({str(p.resolve()):digest(p) for p in OUT.glob('*.npz')},indent=2)+'\n');print(f'{a.stage}: {result["passed"]}/{result["seeds"]}, code/rows/saved-trace metrics verified; max null write {maximum_null:g}V',flush=True)
    if a.live_seconds:
        import pygame
        pygame.display.init();pygame.font.init();screen=pygame.display.set_mode((1050,420));font=pygame.font.SysFont('sans',22);start=time.monotonic();clock=pygame.time.Clock()
        while time.monotonic()-start<a.live_seconds:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:pygame.quit();return
            t=(time.monotonic()-start)/a.live_seconds*4;r=example[round(t/.001)];screen.fill('white');screen.blit(font.render(f'D131 saved-trace replay: {t:.3f}s',True,'black'),(20,20))
            for i,node in enumerate(g['nodes']):
                y=70+i*50;screen.blit(font.render(f'{node["name"]}: {r[i+1]:+.4f}V',True,'black'),(20,y));w=round(abs(r[i+1])*420);pygame.draw.rect(screen,'#0072B2' if i%2==0 else '#D55E00',(620-w if r[i+1]<0 else 620,y,w,22))
            pygame.display.flip();clock.tick(30)
        pygame.quit();print(f'Live replay completed: {a.live_seconds}s',flush=True)
if __name__=='__main__':main()

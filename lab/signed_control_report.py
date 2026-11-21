"""D145 independent saved-trace audit, counted schematic and live replay."""
import argparse,html,json,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from signed_control_bench import OUT,graph,summary,CONFIRM,PILOT,DT,LEVELS
from dynamic_parts_bench import digest,interval
from retained_write_report import svg_plot
from retained_write_preview import render
from minimal.spice import count

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--stage',default='confirm',choices=['pilot','confirm']);parser.add_argument('--live-seconds',type=float,default=0);a=parser.parse_args()
    rows=[json.loads(l) for l in (OUT/f'{a.stage}.jsonl').read_text().splitlines()];saved=json.loads((OUT/f'{a.stage}.json').read_text());ss=CONFIRM if a.stage=='confirm' else PILOT
    result=summary(rows,ss)
    for key in result:assert result[key]==saved[key],key
    peak_error=0.;traces=[]
    for r in rows:
        if r['seed']!=ss[0] or r['dt']!=DT/4:continue
        tr=np.load(OUT/f'{a.stage}_{r["case"]["id"]}_{r["control"]}.npz')['trace'];t=tr[:,0];start=r['start_s']
        got=[float(tr[(t>start+.2)&(t<start+.5),-1].mean()),float(tr[t>1.1,-1].mean())]
        peak_error=max(peak_error,abs(got[0]-r['mean_V']),abs(got[1]-r['recovery_V']))
        if not r['control'] and abs(r['case']['x'])==.3 and abs(r['case']['y'])==.3:traces.append((r,tr))
    assert peak_error<1e-12
    primary=[r for r in rows if not r['control'] and r['dt']==DT/4]
    sign_margins=[np.sign(r['case']['x']*r['case']['y'])*r['mean_V'] for r in primary if r['case']['x']*r['case']['y']!=0]
    activity={}
    for key in ['gross_charge_C','crossings']:
        activity[key]=[interval([np.mean([r['cost'][key][i] for r in primary if r['seed']==s]) for s in ss]) for i in range(5)]
    g=graph();spec=dict(nodes=[[n['name'],n['bias'],n['R'],n['C'],None,None,None,n['memory']] for n in g['nodes']],elements=[[e['to'],e['source'],e['gate'],e['gain'],e['offset'],e['slope'],e['tau'],False] for e in g['edges']],sensors=[],taste=-1)
    manifest=dict(graph=g,states=5,connections=4,parts=count(spec),scope='Core including two input interface nodes; bench sources and recording excluded. No SPICE run. Counts use minimal.spice.count and chip.py blocks.')
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    audit=dict(saved_trace_max_error_V=peak_error,minimum_raw_sign_margin_V=float(min(sign_margins)),activity=activity,source_sha256=digest(__file__))
    (OUT/f'{a.stage}_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    pieces=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="650"><rect width="1100" height="650" fill="white"/><g font-family="sans-serif" fill="#222"><text x="25" y="30" font-size="23">D145: explicit complementary gates for signed control</text>']
    for i,n in enumerate(g['nodes']):
        x=25+215*i;labels=[f'{i}: '+n['name'],f'C={n["C"]*1e12:g} pF',f'R={n["R"]/1e9:g} Gohm',f'bias={n["bias"]*1e12:g} pA']
        pieces.append(f'<rect x="{x}" y="65" width="195" height="120" fill="#eef5f8" stroke="#222"/>')
        for j,label in enumerate(labels):pieces.append(f'<text x="{x+8}" y="{88+27*j}" font-size="15">{html.escape(label)}</text>')
    for i,e in enumerate(g['edges']):
        sx=120+215*e['source'];tx=120+215*e['to'];y=225+45*i
        pieces.append(f'<path d="M{sx} 185 V{y} H{tx} V185" fill="none" stroke="#222"/><text x="{(sx+tx)/2}" y="{y-5}">E{i}: {"+" if e["gain"]>0 else "minus"}</text>')
        if e['gate']>=0:
            gx=120+215*e['gate'];pieces.append(f'<path d="M{gx} 185 V{y-15} H{(sx+tx)/2}" fill="none" stroke="#0072B2" stroke-dasharray="6 4"/>')
        text=f'E{i}: node {e["source"]} to {e["to"]}; gain={e["gain"]*1e12:g} pA; slope={e["slope"]:.4g}/V; offset=0 V; gate={e["gate"]}'
        pieces.append(f'<text x="25" y="{440+29*i}">{html.escape(text)}</text>')
    pieces.append('<text x="25" y="590">Dashed lines: control ports. Every state is noisy. No implicit filters, exact inversion or baseline subtraction.</text></g></svg>');(OUT/'schematic.svg').write_text('\n'.join(pieces));render(OUT/'schematic.svg')
    panels=[]
    for r,tr in traces:
        svg=svg_plot([(tr[:,0],tr[:,1],'source'),(tr[:,0],tr[:,2],'control'),(tr[:,0],tr[:,-1],'raw output')],f'x={r["case"]["x"]:+.2f} V, y={r["case"]["y"]:+.2f} V',(0,1.2),(-.4,.4))
        path=OUT/f'{a.stage}_trace_{r["case"]["id"]}.svg';path.write_text(svg);render(path);panels.append(svg)
    (OUT/f'{a.stage}_view.html').write_text('<!doctype html><meta charset="utf-8"><title>Signed control</title><h1>Signed control with explicit complementary gates</h1><p>Saved noisy traces, first draw; source/control/output labelled. Raw output retains offsets.</p>'+''.join(panels))
    report=['# Explicit signed gain control — D145','',f'{saved["passed"]}/{saved["seeds"]} draws meet every frozen sign, contrast, recovery and rail criterion across all three steps. Wilson95: {saved["wilson95"]}. Refinement passes: {saved["refinement_pass"]}.',
        f'Minimum signed raw mean: {min(sign_margins):.6g} V (criterion > .02 V). Null-input/control range: {saved["null_input_output_range_V"]} V. Those null errors are reported, not removed.',
        f'Core: {manifest["parts"]}. Supply power (mean,95% interval): {saved["power_W"]} W. Gross charge and threshold crossings are separately recorded in {a.stage}_audit.json.',
        '',('The frozen reliability requirement passes.' if saved['reliability_pass'] else 'The frozen reliability requirement is NOT met; this remains a partial witness.')+' It does not establish a precision multiplier, zero feedthrough, learned weight or calibrated timing. Matched worlds and fresh component draws are distinct notions; these are fresh component draws of the same bench family.',
        '','All raw rows, protocol, source hashes and simulator revision are retained. Large NPZ traces stay local; trace_manifest.json records absolute paths and hashes. Schematic is a block diagram with explicit physical nodes/elements; no SPICE claim.']
    (OUT/f'{a.stage}_report.md').write_text('\n\n'.join(report)+'\n');(OUT/'trace_manifest.json').write_text(json.dumps({str(p.resolve()):digest(p) for p in OUT.glob('*.npz')},indent=2)+'\n')
    print(json.dumps(dict(passed=saved['passed'],seeds=saved['seeds'],reliability=saved['reliability_pass'],trace_error=peak_error,min_sign_V=min(sign_margins),parts=manifest['parts'],power_W=saved['power_W'])),flush=True)
    if a.live_seconds:
        import pygame
        pygame.display.init();pygame.font.init();screen=pygame.display.set_mode((1050,430));font=pygame.font.SysFont('sans',23);clock=pygame.time.Clock();start=time.monotonic()
        while time.monotonic()-start<a.live_seconds:
            elapsed=time.monotonic()-start;index=min(3,int(elapsed/a.live_seconds*4));r,tr=traces[index];t=(elapsed/a.live_seconds*4-index)*1.2;row=tr[min(len(tr)-1,round(t/.001))]
            for event in pygame.event.get():
                if event.type==pygame.QUIT:pygame.quit();raise RuntimeError('Live replay closed early')
            screen.fill('white');screen.blit(font.render(f'D145 saved noisy replay: x={r["case"]["x"]:+.2f}, control={r["case"]["y"]:+.2f}; t={t:.3f} s',True,'black'),(20,20))
            for i,n in enumerate(g['nodes']):
                y=85+i*58;v=row[i+1];screen.blit(font.render(f'{n["name"]}: {v:+.4f} V',True,'black'),(20,y));w=round(abs(v)*650);pygame.draw.rect(screen,'#0072B2' if v>=0 else '#D55E00',(680-w if v<0 else 680,y,w,22));pygame.draw.line(screen,'black',(680,y-3),(680,y+28))
            pygame.display.flip();clock.tick(30)
        pygame.quit();print('Live saved-trace replay completed',flush=True)
if __name__=='__main__':main()

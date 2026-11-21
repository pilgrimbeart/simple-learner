"""Audit D133 raw phase-response records and display saved physical signals."""
import argparse, json, sys, time, html
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase_bench import OUT, ROOT, PILOT, CONFIRM, DT, summary, graph, digest
from retained_write_report import svg_plot
from retained_write_preview import render
from minimal.spice import count

def main():
    p=argparse.ArgumentParser(); p.add_argument('--stage', default='confirm'); p.add_argument('--live-seconds', type=float, default=0); a=p.parse_args()
    rows=[json.loads(x) for x in (OUT/f'{a.stage}.jsonl').read_text().splitlines()]
    seeds=PILOT if a.stage=='pilot' else CONFIRM
    result=summary(rows,seeds); saved=json.loads((OUT/f'{a.stage}.json').read_text())
    assert all(result[k]==saved[k] for k in result)
    prov=json.loads((OUT/f'{a.stage}_provenance.json').read_text())
    assert digest(OUT/'protocol.json')==prov['protocol_sha256']
    for path,h in prov['files'].items(): assert digest(ROOT/path)==h, path
    primary=[r for r in rows if not r['control'] and r['dt']==DT/4]
    example=None
    for r in primary:
        if r['seed']!=seeds[0]: continue
        tr=np.load(OUT/f'{a.stage}_{r["case"]["id"]}_False.npz')['trace']; y=tr[tr[:,0]>=6,-1]
        assert abs(y.mean()-r['mean_V'])<1e-12
        assert abs(np.quantile(y,.95)-np.quantile(y,.05)-r['ripple_V'])<1e-12
        if r['case']['id']=='2.0_0': example=tr
    groups=[r for r in result['groups'] if not r['control'] and r['dt']==DT/4]
    biases=[m['zero_phase_bias_V'] for r in groups for m in r['metrics'].values()]
    near=[m['near_contrast_V'] for r in groups for m in r['metrics'].values()]
    far=[m['far_contrast_V'] for r in groups for m in r['metrics'].values()]
    audit=dict(zero_phase_bias_range_V=[min(biases),max(biases)],minimum_near_contrast_V=min(near),minimum_far_contrast_V=min(far),maximum_ripple_V=max(r['ripple_V'] for r in primary))
    (OUT/f'{a.stage}_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    g=graph(); spec=dict(nodes=[[n['name'],n['bias'],n['R'],n['C'],None,None,None,n['memory']] for n in g['nodes']],elements=[[e['to'],e['source'],e['gate'],e['gain'],e['offset'],e['slope'],e['tau'],e.get('sigmoid',False)] for e in g['edges']],sensors=[],taste=-1)
    manifest=dict(graph=g,states=5,connections=4,parts=count(spec),scope='Core circuit only; external bench sources and recording excluded. Activity and gross charge are in raw rows, separately from supply power.')
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    panels=[]
    for f in [2.,5.]:
        curve=sorted([r for r in primary if r['seed']==seeds[0] and r['case']['frequency']==f],key=lambda r:r['case']['phase'])
        x=np.array([r['case']['phase'] for r in curve]); y=np.array([r['mean_V'] for r in curve]); pad=max(.005,float(np.ptp(y))*.15)
        panels.append(svg_plot([(x,y,'raw output mean')],f'{f:g} Hz band: first saved draw',(-np.pi/2,np.pi),(y.min()-pad,y.max()+pad),'relative phase (rad)'))
    panels.append(svg_plot([(example[:,0],example[:,1],'input A'),(example[:,0],example[:,2],'input B')],'Saved inputs: no supplied phase label',(6,8),(0,.35)))
    lo=float(example[example[:,0]>=6,-1].min()); hi=float(example[example[:,0]>=6,-1].max())
    panels.append(svg_plot([(example[:,0],example[:,-1],'raw phase output')],'Saved output: offset retained',(6,8),(lo-.005,hi+.005)))
    for i,svg in enumerate(panels):
        path=OUT/f'{a.stage}_panel_{i}.svg'; path.write_text(svg); render(path)
    (OUT/f'{a.stage}_view.html').write_text('<!doctype html><meta charset="utf-8"><title>Phase response</title><h1>Phase-dependent response, not a calibrated error signal</h1><p>First saved draw; aggregate confirmation and bias ranges are in the report.</p>'+''.join(panels))
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="620"><rect width="1100" height="620" fill="white"/><g fill="#222" font-family="sans-serif"><text x="25" y="30" font-size="23">D133: five explicit noisy states; four connections</text>']
    for i,n in enumerate(g['nodes']):
        x=25+215*i
        svg.append(f'<rect x="{x}" y="80" width="195" height="100" fill="#eef5f8" stroke="#222"/><text x="{x+8}" y="105">{i}: {html.escape(n["name"])}</text><text x="{x+8}" y="135">C={n["C"]*1e12:g} pF</text><text x="{x+8}" y="160">R={n["R"]/1e9:g} Gohm</text>')
    for i,e in enumerate(g['edges']):
        sx=120+215*e['source']; tx=120+215*e['to']; yy=220+45*i
        svg.append(f'<path d="M{sx} 180 V{yy} H{tx} V180" fill="none" stroke="#222"/><text x="{(sx+tx)/2}" y="{yy-5}">E{i}</text>')
        label=f'E{i}: {g["nodes"][e["source"]]["name"]} to {g["nodes"][e["to"]]["name"]}, gain {e["gain"]*1e12:g} pA, slope {e["slope"]:.4g}/V'
        if e['gate']>=0: label+='; gate '+g['nodes'][e['gate']]['name']
        svg.append(f'<text x="25" y="{440+30*i}">{html.escape(label)}</text>')
    svg.append('<text x="25" y="590">Exact functions in manifest.json; gates clip voltage / .3 V to [0,1]. No hidden filter states.</text></g></svg>')
    (OUT/'schematic.svg').write_text('\n'.join(svg));render(OUT/'schematic.svg')
    pilot=json.loads((OUT/'pilot.json').read_text())
    report=['# Phase-dependent response — D133','',f'**{result["passed"]}/{result["seeds"]}** draws pass all phase comparisons, both frequency bands and all three steps. Wilson 95% interval: {result["wilson95"]}.',f'Both refinements pass: {result["refinement_pass"]}. Pilot lag-removal control: {pilot["control_rows"]} rows; pass: {pilot["control_pass"]}.','',f'Raw zero-phase bias range: {audit["zero_phase_bias_range_V"]} V. Minimum near/far phase contrasts: {min(near):.6g}/{min(far):.6g} V. Maximum output ripple: {audit["maximum_ripple_V"]:.6g} V.','The observer compares different stimulus conditions; the circuit receives only currents. This demonstrates local phase sensitivity, not a zero-centred error, unique phase over a full cycle, locking or frequency learning. The ideal product formula is approximate for these nonlinear gates.','',f'Core: five states, four connections; {manifest["parts"]}. Supply power (mean, 95% interval): {result["power_W"]} W.',manifest['scope'],'','Protocol: protocol.json. All rows: '+a.stage+'.jsonl. Source hashes/revision: '+a.stage+'_provenance.json. First saved draw independently remeasured. Large traces remain locally in '+str(OUT)+'/*.npz; trace_manifest.json records hashes. Run lab/phase_report.py to reproduce this audit without simulations.']
    (OUT/f'{a.stage}_report.md').write_text('\n'.join(report)+'\n')
    (OUT/'trace_manifest.json').write_text(json.dumps({str(p.resolve()):digest(p) for p in OUT.glob('*.npz')},indent=2)+'\n')
    print(f'{a.stage}: {result["passed"]}/{result["seeds"]}; raw rows, hashes and saved trace means/ripples verified. {audit}',flush=True)
    if a.live_seconds:
        import pygame
        pygame.display.init();pygame.font.init();screen=pygame.display.set_mode((1000,380));font=pygame.font.SysFont('sans',22);start=time.monotonic();clock=pygame.time.Clock()
        while time.monotonic()-start<a.live_seconds:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:pygame.quit();return
            t=6+(time.monotonic()-start)/a.live_seconds*2;r=example[round(t/.001)];screen.fill('white');screen.blit(font.render(f'D133 saved-trace replay: {t:.3f}s; absolute voltages',True,'black'),(20,20))
            for i,n in enumerate(g['nodes']):
                y=75+i*50;screen.blit(font.render(f'{n["name"]}: {r[i+1]:+.4f} V',True,'black'),(20,y));w=round(abs(r[i+1])*700);pygame.draw.rect(screen,'#0072B2' if i%2==0 else '#D55E00',(620-w if r[i+1]<0 else 620,y,w,22))
            pygame.display.flip();clock.tick(30)
        pygame.quit();print('Live replay completed',flush=True)
if __name__=='__main__':main()

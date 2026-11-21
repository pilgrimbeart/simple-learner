"""D127 results audit, separate accounting, labelled SVG plots and replay."""
import argparse,json,sys,html,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from retained_write_bench import OUT,definition,summarise,PILOT,CONFIRM,DT,digest,interval,build
from minimal.spice import count

def svg_plot(series,title,xlim,ylim,xlabel='time (s)'):
    w,h=540,290; left,top,pw,ph=65,45,450,195
    def xy(x,y):return left+(x-xlim[0])/(xlim[1]-xlim[0])*pw,top+ph-(y-ylim[0])/(ylim[1]-ylim[0])*ph
    a=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"><rect width="540" height="290" fill="white"/><g font-family="sans-serif" font-size="13" fill="#222">',f'<text x="20" y="24" font-size="18">{html.escape(title)}</text>']
    for val in np.linspace(ylim[0],ylim[1],4):
        _,yy=xy(0,val);a +=[f'<path d="M65,{yy} h450" stroke="#ddd"/><text x="8" y="{yy+4}">{val:.3g} V</text>']
    for v in [xlim[0],xlim[1]]:
        xx,_=xy(v,0);a.append(f'<text x="{xx-12}" y="260">{v:g}</text>')
    a.append(f'<text x="240" y="280">{xlabel}</text>')
    for i,(xx,yy,label) in enumerate(series):
        mask=(xx>=xlim[0])&(xx<=xlim[1]);xx=xx[mask];yy=yy[mask];stride=max(1,len(xx)//1600)
        pts=' '.join(f'{x:.2f},{y:.2f}' for x,y in [xy(x,y) for x,y in zip(xx[::stride],yy[::stride])])
        col=['#0072B2','#D55E00','#555'][i];dash='' if i==0 else 'stroke-dasharray="7 4"' if i==1 else 'stroke-dasharray="2 4"'
        a.append(f'<polyline fill="none" stroke="{col}" stroke-width="1.7" {dash} points="{pts}"/><text x="{70+i*145}" y="41" fill="{col}">{html.escape(label)}</text>')
    return '\n'.join(a+['</g></svg>'])

def artifacts(stage,rows,summary):
    traces={sgn:np.load(OUT/f'{stage}_none_{sgn}_v1.npz')['trace'] for sgn in [-1,1]}
    series=[(tr[:,0],tr[:,3],('positive' if sign==1 else 'negative')+' write') for sign,tr in sorted(traces.items(),reverse=True)]
    plots=[svg_plot(series,'Retained state: both write directions',(0,100),(0,.3)),svg_plot(series,'Writing, then holding',(0,4),(0,.3))]
    tr=traces[1];r=next(r for r in rows if r['seed']==(PILOT if stage=='pilot' else CONFIRM)[0] and r['sign']==1 and r['control']=='none' and r['dt']==DT/4)
    jitter=r['pulses'][0][0]-1
    probes=[]
    for at,label in zip([.4,3,98],['before write','after write','late hold']):
        mask=(tr[:,0]>=at+jitter)&(tr[:,0]<=at+jitter+.4)
        probes.append((tr[mask,0]-at-jitter,tr[mask,5],label))
    plots += [svg_plot(probes,'Same probe, response changed by memory',(0,.4),(-.15,.45)),svg_plot([(tr[:,0],tr[:,1],'evidence'),(tr[:,0],tr[:,2],'eligibility')],'Later evidence, eligibility closed',(49.8,50.8),(-.7,.1))]
    for i,p in enumerate(plots):(OUT/f'{stage}_panel_{i}.svg').write_text(p)
    page='<!doctype html><html><meta charset="utf-8"><title>Retained write bench</title><style>body{font:17px sans-serif;max-width:1120px;margin:30px auto}.grid{display:grid;grid-template-columns:1fr 1fr}canvas{width:100%}</style><h1>Retained memory and controlled writes</h1><p>Saved traces from one component draw; blue solid / orange dashed. These are component tests, not robot learning.</p><div class="grid">'+''.join(plots)+'</div><h2>Replay: first four seconds</h2><button onclick="playing=!playing">Play / pause</button><button onclick="t=0;playing=true">Restart</button><canvas id="replay" width="1080" height="250"></canvas><p id="clock"></p><p>Signals: evidence, eligibility, stored voltage, probe, response. No parameter assignments during the run.</p>'
    data=tr[(tr[:,0]<=4)][::4].tolist()
    page+='<script>const data='+json.dumps(data)+';let t=0,playing=true,last=0;const ctx=document.getElementById("replay").getContext("2d");function frame(ms){if(playing)t=Math.min(4,t+(ms-last)/1000);last=ms;ctx.clearRect(0,0,1080,250);const a=data[Math.min(data.length-1,Math.floor(t/.004))];["evidence","eligibility","stored","probe","response"].forEach((s,i)=>{ctx.fillStyle="#222";ctx.fillText(s,10,30+i*44);ctx.fillText(a[i+1].toFixed(4)+" V",850,30+i*44);ctx.fillStyle=i===2?"#D55E00":"#0072B2";ctx.fillRect(400,15+i*44,a[i+1]*550,20)});document.getElementById("clock").innerText=t.toFixed(3)+" s — saved trace replay";requestAnimationFrame(frame)}requestAnimationFrame(frame);</script>'
    (OUT/f'{stage}_replay.html').write_text(page)
    spec=definition();cntspec=dict(nodes=[[n['name'],n['bias'],n['R'],n['C'],None,None,None,n['memory']] for n in spec['nodes']],elements=[[e['to'],e['source'],e['gate'],e['gain'],e['offset'],e['slope'],e['tau'],False] for e in spec['edges']],sensors=[],taste=-1)
    manifest=dict(graph=spec,states=5,connections=2,core_parts=count(cntspec),scope='Core only; no bench sources/readout. Two ideal pump sources counted; pump implementation and energy absent. No SPICE run; chip.py parts account.')
    (OUT/'manifest_v1.json').write_text(json.dumps(manifest,indent=2)+'\n')
    # Draw at the macro level, preserving every state and both control wires.
    s=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="600"><rect width="1100" height="600" fill="white"/><defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8" fill="none" stroke="#222"/></marker></defs><g font-family="sans-serif" fill="#222"><text x="30" y="35" font-size="23">Retained write circuit: five states, two controlled connections</text>']
    positions=[(50,120),(340,120),(670,120),(50,360),(670,360)]
    for n,(x,y) in zip(spec['nodes'],positions):
        label='retained; no leak' if n['memory'] else f'R = {n["R"]/1e9:g} Gohm'
        s.append(f'<rect x="{x}" y="{y}" width="210" height="90" fill="#eef5f8" stroke="#222"/><text x="{x+12}" y="{y+25}" font-size="18">{n["name"]}</text><text x="{x+12}" y="{y+50}">C = 25 pF</text><text x="{x+12}" y="{y+73}">{label}</text>')
    for path,label,x,y,dash in [('M155 210 V270 H775 V210','write: 8 pA × tanh(evidence / .15 V)',210,295,False),('M445 210 V270','eligibility gates write',350,245,True),('M260 405 H670','read: 200 pA × tanh(probe / .15 V)',280,435,False),('M775 210 V320 H470 V405','stored voltage gates read',490,345,True)]:
        s.append(f'<path d="{path}" fill="none" stroke="#222" marker-end="url(#a)" '+('stroke-dasharray="6 4"' if dash else '')+f'/><text x="{x}" y="{y}" font-size="14">{label}</text>')
    s += ['<text x="30" y="520">Every control gate: clip(voltage / .3 V, 0, 1). Write driver dead zone: .01 × full current.</text><text x="30" y="550">Bench currents enter evidence, eligibility and probe only. All nodes retain the existing substrate noise.</text></g></svg>']
    (OUT/'schematic_v1.svg').write_text('\n'.join(s))
    return manifest

def live(stage,seconds):
    import pygame
    pygame.display.init();pygame.font.init();screen=pygame.display.set_mode((1050,430));pygame.display.set_caption('D127 retained write — saved trace replay')
    font=pygame.font.SysFont('sans',23);tr=np.load(OUT/f'{stage}_none_1_v1.npz')['trace'];start=time.monotonic();clock=pygame.time.Clock()
    while time.monotonic()-start<seconds:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: pygame.quit();return
        t=(time.monotonic()-start)/seconds*4;row=tr[min(len(tr)-1,round(t/.001))];screen.fill('white')
        screen.blit(font.render(f'Saved trace replay — {t:.3f} s (positive write)',True,'black'),(25,20))
        for i,name in enumerate(['evidence','eligibility','stored','probe','response']):
            y=90+i*55;screen.blit(font.render(f'{name}: {row[i+1]:+.4f} V',True,'black'),(25,y));width=round(abs(row[i+1])*550)
            pygame.draw.rect(screen,'#D55E00' if i==2 else '#0072B2',(600-width if row[i+1]<0 else 600,y,width,22))
        pygame.display.flip();clock.tick(30)
    pygame.quit();print(f'Live saved-trace replay completed: {seconds} s',flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['pilot','confirm'],default='confirm');p.add_argument('--live-seconds',type=float,default=0);a=p.parse_args()
    rows=[json.loads(l) for l in (OUT/f'{a.stage}_v1.jsonl').read_text().splitlines()];seeds=PILOT if a.stage=='pilot' else CONFIRM
    summary=summarise(rows,seeds)
    if a.stage=='confirm':
        pilot=json.loads((OUT/'pilot_v1.json').read_text()); assert pilot['control_rows']==144 and pilot['control_pass']
    stored=json.loads((OUT/f'{a.stage}_v1.json').read_text());assert all(stored[k]==v for k,v in summary.items())
    prov=json.loads((OUT/f'{a.stage}_provenance_v1.json').read_text());assert prov['protocol_sha256']==digest(OUT/'protocol_v1.json')
    for path,h in prov['files'].items():assert digest(Path(__file__).resolve().parents[1]/path)==h,(path,'changed after run')
    manifest=artifacts(a.stage,rows,summary)
    trace_manifest={str(path.resolve()):digest(path) for path in sorted(OUT.glob('*_v1.npz'))}
    (OUT/'trace_manifest_v1.json').write_text(json.dumps(trace_manifest,indent=2)+'\n')
    primary=[r for r in rows if r['control']=='none' and r['dt']==DT/4]
    # Audit saved primary trace metrics separately against the raw records.
    for sign in [-1,1]:
        tr=np.load(OUT/f'{a.stage}_none_{sign}_v1.npz')['trace'];t=tr[:,0];m=tr[:,3]
        row=next(r for r in primary if r['seed']==seeds[0] and r['sign']==sign)
        delta=m[(t>2)&(t<2.9)].mean()-m[(t>.8)&(t<.95)].mean()
        assert abs(delta-row['metrics']['write_delta_V'])<1e-12
        assert abs(np.ptp(m[(t>2)&(t<97)])-row['metrics']['hold_span_V'])<1e-12
    startup=[r['metrics']['stored_baseline_V']-float(build(r['seed'],'none').V[2]) for r in primary]
    ranges={k:[min(r['metrics'][k] for r in primary),max(r['metrics'][k] for r in primary)] for k in ['write_delta_V','hold_span_V','closed_gate_delta_V','readout_change_V','late_readout_delta_V']}
    lines=['# Retained memory and controlled writes — D127','',f'{a.stage.title()}: **{summary["passed"]}/{len(seeds)}** component draws pass both signs at all three timesteps. Wilson 95% interval [{summary["wilson95"][0]:.3f}, {min(1.,summary["wilson95"][1]):.3f}].',f'Both refinement checks: {summary["refinement_pass"]}. Pilot controls: 144/144 passed; controls were run on pilot seeds only.','',
        'A positive or negative evidence voltage writes the retained state only while a noisy eligibility node opens the write connection. The stored voltage gates a later response. The same probe is repeated before writing, after writing and near 100 s. Opposite evidence alone at 50 s tests gate closure.','',
        'This is a component witness with supplied evidence and eligibility, not discovery of a useful reward-credit rule. The gate is nonnegative; signed writes come from the evidence source. The stored range is positive, so signed learned weights are not demonstrated.','',f'Core: 5 states, 2 connections; parts {manifest["core_parts"]}. Mean core power (mean, 95% paired-seed bootstrap): {summary["mean_power_W"]} W.','',
        'Activity (gross charge and threshold crossings) is recorded separately per node in the raw JSONL. Bench stimulation/recording are excluded. Two ideal pump supplies enter the source count, but their implementation and energy are absent.','', '| Metric | Observed minimum | Observed maximum |','|---|---:|---:|']
    for k,(low,high) in ranges.items():lines.append(f'| {k} | {low:.8g} | {high:.8g} |')
    lines+=['',f'Exploratory startup audit: baseline minus initial stored voltage ranges from {min(startup):.6g} to {max(startup):.6g} V. Dynamic input/gate states start randomly, so brief startup writing is possible; retention is tested after settling, not from arbitrary birth states.','',
        'Seed labels 52000/52100 were used historically in block-model experiments with a different RNG construction. These are new evaluations of this circuit, separate from its pilot; no globally unused seed-label or new-family claim.','',
        'The established retained-node model has no idle noise: a quiet hold is an integration check of that assumption, not a measurement of physical retention. No new noise switch or engine change.','',
        'Large saved traces stay outside git at `/home/pilgrim/git/simple-learner/lab/v/retained_write/*_v1.npz`; `trace_manifest_v1.json` records their hashes. Small metrics, specifications, reports and replay are retained.','',
        'Protocol: `protocol_v1.json`; raw results: `'+a.stage+'_v1.jsonl`; exact source hashes and dirty revision: `'+a.stage+'_provenance_v1.json`. Pilot and confirm seeds are fixed in the protocol. Confirmation is separate from pilot. Each seed has paired signs and three timesteps, not six independent observations.','',
        'Reproduce with `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/retained_write_bench.py prepare|pilot|confirm` (choose one stage; existing outputs are protected from overwrite). Report/replay: `.venv/bin/python lab/retained_write_report.py --stage '+a.stage+' --live-seconds 8`. All paths relative to the repository.']
    (OUT/f'{a.stage}_report.md').write_text('\n'.join(lines)+'\n');print(json.dumps(summary),flush=True)
    if a.live_seconds:live(a.stage,a.live_seconds)
if __name__=='__main__':main()

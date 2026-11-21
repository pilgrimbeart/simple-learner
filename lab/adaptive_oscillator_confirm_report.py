"""Audit fresh oscillator confirmation and render labelled saved traces."""
import argparse,json,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from adaptive_oscillator_confirm import OUT,SEEDS,DT,summarise
from adaptive_oscillator import OUT as PILOT
from dynamic_parts_bench import ROOT,digest,metrics,interval
from retained_write_report import svg_plot
from retained_write_preview import render

def main():
    p=argparse.ArgumentParser();p.add_argument('--live-seconds',type=float,default=0);args=p.parse_args()
    rows=[json.loads(l) for l in (OUT/'rows.jsonl').read_text().splitlines()];saved=json.loads((OUT/'summary.json').read_text());assert summarise(rows)==saved
    prov=json.loads((OUT/'provenance.json').read_text())
    for name,h in prov['files'].items():assert digest(ROOT/name)==h,name
    assert digest(OUT/'protocol.json')==prov['protocol_sha256']
    error=0.;count=0;traces={}
    for path in OUT.glob('*.npz'):
        stem=path.stem;seed=int(stem.split('_')[0]);arm=stem.split('_',1)[1];r=next(r for r in rows if r['seed']==seed and r['arm']==arm and r['dt']==DT/4)
        tr=np.load(path)['trace'];m=metrics('oscillator',[tr],[r['cost']]);assert m['passed']==r['metrics']['passed'];count+=1
        error=max(error,max(abs(m['values'][k]-r['metrics']['values'][k]) for k in m['values']))
        if seed==SEEDS[0]:traces[arm]=tr
    assert error<1e-12
    manifest=json.loads((PILOT/'manifest.json').read_text());activity={}
    for arm in ['original','adaptive','writer_removed']:
        rr=[r for r in rows if r['arm']==arm and r['dt']==DT/4]
        activity[arm]={key:[interval([r['cost'][key][i] for r in rr]) for i in range(len(rr[0]['cost'][key]))] for key in ['gross_charge_C','crossings']}
    audit=dict(rows=len(rows),saved_finest_traces=count,saved_trace_metric_error=error,writer_removed_memory_held=all(r['memory']['held_exactly'] for r in rows if r['arm']=='writer_removed'),activity=activity,script_sha256=digest(Path(__file__)))
    (OUT/'audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    (OUT/'trace_manifest.json').write_text(json.dumps({str(p.resolve()):digest(p) for p in OUT.glob('*.npz')},indent=2)+'\n')
    panels=[]
    for i,window in enumerate([(0,10),(60,62)]):
        series=[(traces[a][:,0],traces[a][:,1],label) for a,label in [('original','original'),('adaptive','adaptive'),('writer_removed','writer removed')]]
        plot=svg_plot(series,f'Fresh draw{SEEDS[0]}',window,(-.6,.6));path=OUT/f'panel_{i}.svg';path.write_text(plot);render(path);panels.append(plot)
    (OUT/'view.html').write_text('<!doctype html><meta charset="utf-8"><title>Bias adaptation confirmation</title><h1>Fresh component draws, same bench family</h1>'+''.join(panels))
    lines=['# Retained bias adaptation: fresh confirmation','', 'The oscillator adjusts its own bias from its local voltage through one added memory and two connections. No external frequency, phase or parameter assignment is supplied.','', '| Arm | Complete draws | Wilson95 | Refinement | Parts | Supply power (mean,95%) W |','|---|---|---|---|---|---|']
    for arm in ['original','adaptive','writer_removed']:
        r=saved[arm];lines.append(f'| {arm} | {r["passed"]}/40 | {r["wilson95"]} | {r["refinement_pass"]} | {sum(manifest["parts"][arm].values())} | {r["power_W"]} |')
    passed=saved['adaptive']['reliability_pass'] and saved['adaptive']['refinement_pass']
    lines+=['', 'Frozen reliability and refinement requirement '+('met.' if passed else 'NOT met.'),f'Paired changes: {saved["paired"]}.','', 'This is a bounded operating-point adaptation witness, not reward learning or a universal oscillation guarantee. The nominal write rate and correction authority are design choices. Conditions and the100s life are unchanged from development; these are new component draws, not new problem families. Exact idle retention follows the existing memory model. Core counts exclude the existing pump implementation/energy anomaly; no SPICE or physical chip measurement.', '', f'All{len(rows)} rows audited; {count} saved finest traces remeasured. Activity and memory motion are separate from power in raw records/audit. See ../adaptive_oscillator/schematic.svg for the unchanged complete graph. Provenance and absolute trace hashes accompany the result.']
    (OUT/'report.md').write_text('\n'.join(lines)+'\n');print(json.dumps(dict(adaptive_passed=saved['adaptive']['passed'],requirement_met=passed,original_passed=saved['original']['passed'],removed_passed=saved['writer_removed']['passed'],saved_trace_error=error,paired=saved['paired']),indent=2),flush=True)
    if args.live_seconds:
        import pygame
        pygame.display.init();pygame.font.init();screen=pygame.display.set_mode((1050,430));font=pygame.font.SysFont('sans',22);clock=pygame.time.Clock();start=time.monotonic();tr=traces['adaptive']
        while time.monotonic()-start<args.live_seconds:
            elapsed=time.monotonic()-start;at=60+elapsed
            for event in pygame.event.get():
                if event.type==pygame.QUIT:pygame.quit();raise RuntimeError('Replay closed early')
            screen.fill('white');screen.blit(font.render(f'D162 fresh saved noisy trace {SEEDS[0]}, t={at:.2f}s',True,'black'),(20,20))
            for j,(column,label,col) in enumerate([(1,'fast voltage','#0072B2'),(2,'recovery voltage','#D55E00'),(3,'bias memory','#555555')]):
                mask=(tr[:,0]>=at-2)&(tr[:,0]<=at);base=110+j*120;screen.blit(font.render(label,True,'black'),(20,base-35));tt=tr[mask,0];vv=tr[mask,column]
                pts=[(int(250+(t-at+2)*380),int(base-v*90)) for t,v in zip(tt[::3],vv[::3])]
                pygame.draw.line(screen,'#cccccc',(250,base),(1020,base))
                if len(pts)>1:pygame.draw.lines(screen,col,False,pts,2)
            pygame.display.flip();clock.tick(30)
        pygame.quit();print('Live fresh saved-trace replay completed',flush=True)
if __name__=='__main__':main()

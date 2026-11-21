"""D136 audit, event-by-event failure classification and saved-trace display."""
import argparse,json,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oneshot_bench as b
from dynamic_parts_bench import ROOT,digest
from retained_write_report import svg_plot
from retained_write_preview import render
OUT=ROOT/'lab/v/pulse_recovery'

def main():
    p=argparse.ArgumentParser();p.add_argument('--live-seconds',type=float,default=0);a=p.parse_args()
    rows=[json.loads(x) for x in (OUT/'rows.jsonl').read_text().splitlines()];spec=json.loads((OUT/'protocol.json').read_text());prov=json.loads((OUT/'provenance.json').read_text());assert digest(OUT/'protocol.json')==prov['protocol_sha256']
    for path,h in prov['files'].items():assert digest(ROOT/path)==h,path
    assert len(rows)==384 and len({(r['seed'],r['case']['id'],r['gap_s']) for r in rows})==384
    old=[json.loads(x) for x in (b.OUT/'pilot.jsonl').read_text().splitlines()];reference={(r['seed'],r['case']['id']):r for r in old if not r['control'] and r['dt']==b.DT/4}
    for r in rows:
        if r['gap_s']==1:assert r['metrics']==reference[r['seed'],r['case']['id']]['metrics']
    summary=[]
    for gap in spec['gaps_s']:
        for sign in [-1,1]:
            rr=[r for r in rows if r['gap_s']==gap and r['case']['sign']==sign]
            missing=[sum(not any(0<=e['start_s']-r['triggers'][i]<.15 for e in r['metrics']['events']) for r in rr) for i in [0,1]]
            summary.append(dict(gap_s=gap,sign=sign,cases=len(rr),passes=sum(r['metrics']['passed'] and not r['rail_hits'] for r in rr),missed_by_trigger=missing,extra=sum(r['extra'] for r in rr),merged=sum(r['merged'] for r in rr),second_peak_range_V=[min(r['metrics']['normalized']['peak_1']*.3 for r in rr),max(r['metrics']['normalized']['peak_1']*.3 for r in rr)],second_integral_mean_V=float(np.mean([r['state_before_second_positive_change_V'][1] for r in rr]))))
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');panels=[];example=None
    for sign in [-1,1]:
        series=[]
        for gap,label in [(.02,'20 ms gap'),(.05,'50 ms gap'),(.1,'100 ms gap')]:
            r=next(r for r in rows if r['seed']==spec['seeds'][0] and r['case']['sign']==sign and r['case']['amplitude']==.4 and r['case']['duration']==.5 and r['gap_s']==gap)
            path=OUT/f'{gap}_{sign}.npz';tr=np.load(path)['trace'];assert b.measure(tr,r['triggers'])==r['metrics'];at=r['triggers'][0 if sign<0 else 1]
            series.append((tr[:,0]-at,tr[:,-1],label))
            if gap==.1 and sign==1:example=tr
        svg=svg_plot(series,f'{"Return from negative" if sign<0 else "Second positive onset"}: first draw',(-.02,.3),(-.03,.7));path=OUT/f'output_{sign}.svg';path.write_text(svg);render(path);panels.append(svg)
    lines=['# Pulse recovery — D136','','The unchanged circuit passes all 64 tested conditions at input-off gaps of 100 ms and above. At 50 ms, 44/64 pass; at 20 ms, 18/64 pass. These are eight reused development draws, both signs/amplitudes/durations, at the existing finest step. The 64 original one-second conditions reproduce exactly. No new reliability or maximum-event-rate claim.','','| Input-off gap (ms) | Sign | Conditions passing / 32 | Missed first / second response |','|---:|---|---:|---:|']
    for r in summary:lines.append(f'| {r["gap_s"]*1000:g} | {r["sign"]:+d} | {r["passes"]} | {r["missed_by_trigger"][0]} / {r["missed_by_trigger"][1]} |')
    lines+=['','**Interpretation.** For positive inputs, short gaps leave the adaptive state insufficiently reset and suppress the second output peak. Negative inputs trigger on their return to zero; a short gap interrupts that first positive excursion when the next negative input begins. This asymmetry matters: the input-off gap is not the positive-event spacing (which also includes a 0.5 or 2 s pulse). No merged or extra events were recorded. Some failures are weak/short pulses rather than missing crossings. These observations do not prove that a regenerative mechanism is required.','','Protocol, all 384 raw rows, state snapshots, hashes and detailed summary are retained here. Large saved traces remain locally under '+str(OUT)+'; trace_manifest.json records hashes. Scripts: lab/pulse_recovery.py and lab/pulse_recovery_report.py. Graph and physical parts are unchanged from D132; raw power is recorded per trajectory, not compared as a hardware saving.']
    (OUT/'report.md').write_text('\n'.join(lines)+'\n');(OUT/'view.html').write_text('<!doctype html><meta charset="utf-8"><h1>Recovery limits of the unchanged pulse generator</h1><p>Saved first-draw traces; labels and line styles distinguish gaps. Time is relative to the indicated positive change.</p>'+''.join(panels));print('384 rows and 64 original replays audited; saved metrics reproduced.',flush=True)
    if a.live_seconds:
        import pygame
        pygame.display.init();pygame.font.init();screen=pygame.display.set_mode((1000,330));font=pygame.font.SysFont('sans',22);start=time.monotonic();clock=pygame.time.Clock()
        while time.monotonic()-start<a.live_seconds:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:pygame.quit();return
            t=.8+(time.monotonic()-start)/a.live_seconds*1.6;r=example[round(t/.001)];screen.fill('white');screen.blit(font.render(f'D136 saved replay: 100 ms input gap, {t:.3f} s',True,'black'),(20,20))
            for i,n in enumerate(b.graph()['nodes']):
                y=75+50*i;screen.blit(font.render(f'{n["name"]}: {r[i+1]:+.4f} V',True,'black'),(20,y));w=round(abs(r[i+1])*350);pygame.draw.rect(screen,'#0072B2' if i%2==0 else '#D55E00',(650-w if r[i+1]<0 else 650,y,w,20))
            pygame.display.flip();clock.tick(30)
        pygame.quit();print('Live replay completed',flush=True)
if __name__=='__main__':main()

"""Plot and replay D126 saved traces; observing only, never feeds back into a circuit.
No plotting dependency beyond the project's pygame. SVG schematics are circuit-block diagrams.
"""
import argparse
import json
import math
import os
from pathlib import Path
import sys
import time
import html
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'lab'))
from dynamic_parts_bench import OUT, definitions
from minimal.spice import count
from units import V_TYP

COLORS=['#0072B2','#D55E00']


def manifest():
    result={}
    for name,s in definitions().items():
        spec=dict(nodes=[[n['name'],n['bias'],n['R'],n['C'],None,None,None,n['memory']] for n in s['nodes']],
            elements=[[e['to'],e['source'],e['gate'],e['gain'],e['offset'],e['slope'],e['tau'],False] for e in s['edges']],
            sensors=[],taste=-1)
        result[name]=dict(states=len(s['nodes']),connections=len(s['edges']),counts=count(spec),graph=s,
            count_scope='Core circuit only; bench current sources and readout equipment excluded. Count via minimal.spice.count, not a SPICE simulation.')
    result['retained_memory_contract']=dict(status='specified, not demonstrated in D126',
        input='signed write current through existing thresholded write driver',output='retained voltage',
        states=1,noise='existing silicon memory write shot noise; no rest noise under the established model',
        controls='read via controlled connection; do not assign parameters from Python')
    (OUT/'manifest_v1.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def schematic(data):
    pieces=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="900" viewBox="0 0 1200 900">',
        '<rect width="1200" height="900" fill="white"/>',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="none" stroke="#333"/></marker></defs>',
        '<g font-family="sans-serif" fill="#222"><text x="35" y="40" font-size="24">Four circuits, one circuit-block vocabulary</text>']
    for j,(name,s) in enumerate(definitions().items()):
        x=35+(j%2)*600; y=80+(j//2)*400
        pieces.append(f'<text x="{x}" y="{y}" font-size="22">{name.title()}</text>')
        for i,n in enumerate(s['nodes']):
            xx=x+40+i*260; yy=y+70
            pieces.append(f'<rect x="{xx}" y="{yy}" width="160" height="85" rx="8" fill="#eef5f8" stroke="#333"/>')
            for k,label in enumerate([n['name'],f"C = {n['C']*1e12:g} pF",f"R = {n['R']/1e9:g} Gohm"]):
                pieces.append(f'<text x="{xx+12}" y="{yy+23+23*k}" font-size="16">{label}</text>')
        for k,e in enumerate(s['edges']):
            sign='+' if e['gain']>0 else '-'
            label=f"{s['nodes'][e['source']]['name']} → {s['nodes'][e['to']]['name']}: {sign}{abs(e['gain'])*1e12:g} pA, tanh({e['slope']:.3g}/V · source)"
            pieces.append(f'<text x="{x+10}" y="{y+195+28*k}" font-size="14">{html.escape(label)}</text>')
        if not s['edges']:
            pieces.append(f'<text x="{x+10}" y="{y+195}" font-size="16">Input current → capacitor + leak</text>')
        pieces.append(f'<text x="{x+10}" y="{y+305}" font-size="15">{len(s["nodes"])} noisy states; {len(s["edges"])} saturating connections</text>')
    pieces.append('<text x="35" y="870" font-size="15">All nodes: silicon noise, component mismatch, ±0.9 V supply. No internal filtered channels.</text></g></svg>')
    (OUT/'schematics_v1.svg').write_text('\n'.join(pieces))


def traces(stage):
    result=[]
    windows={'trace':(.1,.8),'memory':(0,100),'resonator':(3.6,5.3),'oscillator':(49,53)}
    for name in definitions():
        i=2 if name=='resonator' else 0
        tr=np.load(OUT/f'{stage}_{name}_{i}_trace_v1.npz')['trace']
        a,b=windows[name]; tr=tr[(tr[:,0]>=a)&(tr[:,0]<=b)]
        stride=max(1,len(tr)//1800)
        tr=tr[::stride]
        result.append(dict(name=name,labels=[n['name'] for n in definitions()[name]['nodes']],points=tr.round(7).tolist()))
    return result


def webpage(data,stage):
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><title>Dynamic circuit bench</title>
<style>body{font:17px system-ui;max-width:1100px;margin:30px auto;padding:0 20px;color:#222}canvas{width:100%;border:1px solid #ddd}button{padding:10px 20px;font:inherit}p{line-height:1.5}</style>
<h1>Four dynamic circuit witnesses</h1><p>Replay of noisy simulation traces, not a new simulation. Blue solid: first node; orange dashed: second node. Times are seconds and voltages are volts. This is component coverage, not robot learning.</p>
<button id="play">Pause</button> <button id="restart">Restart</button><canvas id="c" width="1100" height="780"></canvas>
<p><a href="schematics_v1.svg">Circuit descriptions</a> · <a href="manifest_v1.json">Parts and state counts</a></p>
<script>const data=DATA;let phase=0,playing=true,last=performance.now();const c=document.getElementById('c'),ctx=c.getContext('2d');
function draw(){ctx.fillStyle='white';ctx.fillRect(0,0,c.width,c.height);data.forEach((d,k)=>{let x=65+(k%2)*550,y=45+Math.floor(k/2)*385,w=455,h=270;let pts=d.points,t0=pts[0][0],t1=pts.at(-1)[0];ctx.fillStyle='#222';ctx.font='20px sans-serif';ctx.fillText(d.name,x,y);ctx.font='14px sans-serif';ctx.fillText('voltage (V)',x,y+24);ctx.strokeStyle='#aaa';ctx.setLineDash([]);ctx.strokeRect(x,y+40,w,h);for(let v of [-.9,0,.9]){ctx.fillText(v.toFixed(1),x-35,y+40+(1-(v+.9)/1.8)*h+5)}ctx.fillText(t0.toFixed(2),x,y+h+62);ctx.fillText(t1.toFixed(2)+' s',x+w-50,y+h+62);d.labels.forEach((lab,j)=>{ctx.strokeStyle=['#0072B2','#D55E00'][j];ctx.setLineDash(j?[6,4]:[]);ctx.beginPath();pts.forEach((p,i)=>{if(i>phase*(pts.length-1))return;let px=x+(p[0]-t0)/(t1-t0)*w,py=y+40+(1-(p[j+1]+.9)/1.8)*h;i?ctx.lineTo(px,py):ctx.moveTo(px,py)});ctx.stroke();ctx.fillStyle=['#0072B2','#D55E00'][j];ctx.fillText(lab+(j?' (dashed)':' (solid)'),x+j*180,y+h+88)})})}
function frame(now){if(playing)phase=(phase+(now-last)/10000)%1;last=now;draw();requestAnimationFrame(frame)}document.getElementById('play').onclick=()=>{playing=!playing;document.getElementById('play').textContent=playing?'Pause':'Play'};document.getElementById('restart').onclick=()=>phase=0;requestAnimationFrame(frame);</script></html>'''
    (OUT/f'{stage}_replay.html').write_text(page.replace('DATA',json.dumps(data)))


def pygame_plot(data,stage,live_seconds):
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT']='1'
    if not live_seconds: os.environ['SDL_VIDEODRIVER']='dummy'
    import pygame
    pygame.init(); screen=pygame.display.set_mode((1200,880)); pygame.display.set_caption('Dynamic circuit bench — saved noisy traces')
    font=pygame.font.Font(None,24); title=pygame.font.Font(None,32)
    def write(text,pos,large=False,color='#222222'):
        screen.blit((title if large else font).render(text,True,color),pos)
    def draw(progress):
        screen.fill('white'); write('Four circuit witnesses — silicon noise and component mismatch',(30,15),True)
        for k,d in enumerate(data):
            x=65+(k%2)*590; y=90+(k//2)*380; w=480; h=240; pts=np.asarray(d['points'])
            write(d['name'].title(),(x,y-25),True)
            pygame.draw.rect(screen,'#aaaaaa',(x,y+18,w,h),1)
            for v in [-.9,0,.9]:
                yy=y+18+(1-(v+.9)/1.8)*h
                write(f'{v:g}',(x-40,yy-8)); pygame.draw.line(screen,'#eeeeee',(x,yy),(x+w,yy))
            write('V',(x-35,y-8))
            for j,label in enumerate(d['labels']):
                points=[(x+(p[0]-pts[0,0])/(pts[-1,0]-pts[0,0])*w,y+18+(1-(p[j+1]+.9)/1.8)*h) for p in pts[:max(2,int(len(pts)*progress))]]
                if j:
                    for n in range(0,len(points)-1,8): pygame.draw.lines(screen,COLORS[j],False,points[n:n+5],2)
                else: pygame.draw.lines(screen,COLORS[j],False,points,2)
                write(label+(' dashed' if j else ' solid'),(x+j*210,y+h+58),color=COLORS[j])
            write(f'{pts[0,0]:.2f} s',(x,y+h+28)); write(f'{pts[-1,0]:.2f} s',(x+w-80,y+h+28))
        write('Saved trace replay; no feedback to the simulator. See JSON for all seeds, margins and failures.',(30,850))
        pygame.display.flip()
    draw(1.); pygame.image.save(screen,str(OUT/f'{stage}_overview.png'))
    if live_seconds:
        start=time.monotonic(); clock=pygame.time.Clock()
        while time.monotonic()-start<live_seconds:
            for event in pygame.event.get():
                if event.type==pygame.QUIT: pygame.quit(); return
            draw(min(1.,(time.monotonic()-start)/max(1,live_seconds-1))); clock.tick(30)
    pygame.quit()


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--stage',default='pilot',choices=['pilot','confirm']); p.add_argument('--live-seconds',type=float,default=0)
    args=p.parse_args(); m=manifest(); schematic(m); data=traces(args.stage); webpage(data,args.stage); pygame_plot(data,args.stage,args.live_seconds)
    print(OUT/f'{args.stage}_replay.html')

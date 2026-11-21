"""D168 Task A figure: expected adequate share (of the zero-error count) against readout-error SD.
Hand-written SVG (no plotting library is installed and the work order forbids installing).
Okabe-Ito colours, each series also distinguished by line style, marker and a direct label."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'lab/v/calibration_precision_20261120/a'
S=json.loads((D/'summary.json').read_text());G=S['grid_mV']
MODES=[('raw','raw output (no baseline)'),('0.15','baseline 0.15 s'),('1.0','baseline 1 s'),('3.8585074308112732','baseline 3.9 s')]
SERIES=[  # set, weight, window, colour, dash, marker, label
 ('D163_schedules','w','full_1000s','#0072B2','', 'circle','40 draws, w, all 1000 s'),
 ('D163_schedules','w','final_third_1000s','#0072B2','6,4','circle','40 draws, w, final third'),
 ('D163_schedules','w2','full_1000s','#D55E00','', 'square','40 draws, w*w, all 1000 s'),
 ('D163_schedules','w2','final_third_1000s','#D55E00','6,4','square','40 draws, w*w, final third'),
 ('D165_histories','w','full_1000s','#000000','2,3','triangle','80 histories, w, all 1000 s'),
 ('D165_histories','w','last_third_1000s','#009E73','8,3,2,3','diamond','80 histories, w, final third')]
W,H=1100,860;PW,PH=430,250;ML,MT=80,70;GX,GY=110,120
X0,X1=0,30;Y0,Y1=.5,1.02
def find(s,w,win,m):
    return next(t for t in S['table'] if (t['set'],t['weight'],t['window'],t['mode'])==(s,w,win,m))
def marker(kind,x,y,c):
    if kind=='circle':return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{c}"/>'
    if kind=='square':return f'<rect x="{x-3.5:.1f}" y="{y-3.5:.1f}" width="7" height="7" fill="{c}"/>'
    if kind=='triangle':return f'<path d="M{x:.1f},{y-4.5:.1f} L{x+4.5:.1f},{y+3.5:.1f} L{x-4.5:.1f},{y+3.5:.1f} Z" fill="{c}"/>'
    return f'<path d="M{x:.1f},{y-5:.1f} L{x+4.5:.1f},{y:.1f} L{x:.1f},{y+5:.1f} L{x-4.5:.1f},{y:.1f} Z" fill="none" stroke="{c}" stroke-width="1.5"/>'
out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="sans-serif" font-size="13">',
 '<rect width="100%" height="100%" fill="#ffffff"/>',
 f'<text x="{W/2}" y="28" text-anchor="middle" font-size="17">How precise must the balance readout be? Expected adequate histories, as a share of the error-free count</text>',
 f'<text x="{W/2}" y="50" text-anchor="middle" font-size="13">One fixed readout error per detector, Gaussian with the SD on the x axis (exact integration). Dotted grey lines: 90% and 95%.</text>']
for k,(mode,title) in enumerate(MODES):
    ox=ML+(k%2)*(PW+GX);oy=MT+(k//2)*(PH+GY)
    sx=lambda v:ox+(v-X0)/(X1-X0)*PW;sy=lambda v:oy+PH-(v-Y0)/(Y1-Y0)*PH
    out.append(f'<text x="{ox+PW/2}" y="{oy-10}" text-anchor="middle" font-size="15">{title}</text>')
    out.append(f'<rect x="{ox}" y="{oy}" width="{PW}" height="{PH}" fill="none" stroke="#444"/>')
    for v in [0,5,10,15,20,25,30]:
        out.append(f'<line x1="{sx(v)}" y1="{oy+PH}" x2="{sx(v)}" y2="{oy+PH+5}" stroke="#444"/><text x="{sx(v)}" y="{oy+PH+20}" text-anchor="middle">{v}</text>')
    for v in [.5,.6,.7,.8,.9,1.0]:
        out.append(f'<line x1="{ox-5}" y1="{sy(v):.1f}" x2="{ox}" y2="{sy(v):.1f}" stroke="#444"/><text x="{ox-8}" y="{sy(v)+4:.1f}" text-anchor="end">{int(v*100)}%</text>')
    for v in [.9,.95]:
        out.append(f'<line x1="{ox}" y1="{sy(v):.1f}" x2="{ox+PW}" y2="{sy(v):.1f}" stroke="#999" stroke-dasharray="1,3"/>')
    out.append(f'<text x="{ox+PW/2}" y="{oy+PH+40}" text-anchor="middle">readout-error SD (mV)</text>')
    for s,w,win,c,dash,mk,label in SERIES:
        t=find(s,w,win,mode);ys=[t['fraction_of_zero_error'][str(g)] for g in G]
        pts=[(sx(g),sy(max(min(y,Y1),Y0))) for g,y in zip(G,ys)]
        da=f' stroke-dasharray="{dash}"' if dash else ''
        out.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in pts)}" fill="none" stroke="{c}" stroke-width="2"{da}/>')
        out+= [marker(mk,x,y,c) for x,y in pts]
# legend, below the panels
ly=MT+2*(PH+GY)-40
for i,(s,w,win,c,dash,mk,label) in enumerate(SERIES):
    lx=ML+(i%3)*330;yy=ly+(i//3)*24;da=f' stroke-dasharray="{dash}"' if dash else ''
    out.append(f'<line x1="{lx}" y1="{yy}" x2="{lx+40}" y2="{yy}" stroke="{c}" stroke-width="2"{da}/>'+marker(mk,lx+20,yy,c)+f'<text x="{lx+48}" y="{yy+4}">{label}</text>')
out.append('</svg>')
(D/'precision_curve.svg').write_text('\n'.join(out)+'\n');print('wrote',D/'precision_curve.svg')

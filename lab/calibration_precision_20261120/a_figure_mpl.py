"""D168 Task A figure (matplotlib), replacing the hand-written SVG of a_figure.py.
Needs matplotlib, which is not in requirements.txt: run with the tools environment
(~/.venvs/simple-learner-tools/bin/python). Reads a/summary.json only.
Okabe-Ito colours; each series also has its own line style, marker and legend label (the user is colour-blind)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'lab/v/calibration_precision_20261120/a'
S=json.loads((D/'summary.json').read_text());G=S['grid_mV']
MODES=[('raw','raw output (no baseline)'),('0.15','baseline 0.15 s'),('1.0','baseline 1 s'),('3.8585074308112732','baseline 3.9 s')]
SERIES=[('D163_schedules','w','full_1000s','#0072B2','-','o','40 draws, w, all 1000 s'),
 ('D163_schedules','w','final_third_1000s','#0072B2','--','o','40 draws, w, final third'),
 ('D163_schedules','w2','full_1000s','#D55E00','-','s','40 draws, w*w, all 1000 s'),
 ('D163_schedules','w2','final_third_1000s','#D55E00','--','s','40 draws, w*w, final third'),
 ('D165_histories','w','full_1000s','#000000',':','^','80 histories, w, all 1000 s'),
 ('D165_histories','w','last_third_1000s','#009E73','-.','D','80 histories, w, final third')]
def find(s,w,win,m):return next(t for t in S['table'] if (t['set'],t['weight'],t['window'],t['mode'])==(s,w,win,m))
fig,axes=plt.subplots(2,2,figsize=(11,8),sharex=True,sharey=True)
for ax,(mode,title) in zip(axes.flat,MODES):
    for y,lab in [(.95,'95%'),(.90,'90%')]:
        ax.axhline(y,color='#888888',lw=.8,ls=(0,(1,3)));ax.text(30.3,y,lab,va='center',fontsize=8,color='#555555')
    ax.axvline(30,color='#bbbbbb',lw=.8);ax.text(29.5,.52,'one part\'s offset (30 mV)',rotation=90,ha='right',va='bottom',fontsize=8,color='#555555')
    for s,w,win,c,ls,mk,label in SERIES:
        t=find(s,w,win,mode);ys=[t['fraction_of_zero_error'][str(g)] for g in G]
        ax.plot(G,ys,color=c,ls=ls,marker=mk,ms=4,lw=1.6,label=label,mfc='white' if 'final' in label else c)
    ax.set_title(title);ax.set_ylim(.5,1.04);ax.set_xlim(0,33);ax.grid(alpha=.2)
for ax in axes[1]:ax.set_xlabel('SD of the one fixed readout error (mV)')
fig.supylabel('expected adequate histories, as a share of the error-free count')
h,l=axes[0,0].get_legend_handles_labels()
fig.legend(h,l,loc='lower center',ncol=3,frameon=False,fontsize=9)
fig.suptitle('How precise must the balance readout be?  Exact Gaussian expectation, one fixed error per detector',fontsize=12)
fig.tight_layout(rect=(0,.08,1,.96))
for ext in ['png','svg']:fig.savefig(D/f'precision_curve_mpl.{ext}',dpi=130)
print('wrote',D/'precision_curve_mpl.png')

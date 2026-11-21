"""D170 figure: (left) each draw's residual readout error at the final knob, against D168's offline final-third shared
reference, per arm and point; (right) the knob over life for two fixed seeds with their passing range.
Okabe-Ito colours, always paired with marker or line style and a label (the user is colour-blind).
Run with ~/.venvs/simple-learner-tools/bin/python (matplotlib); reads only saved replay outputs."""
import json
from pathlib import Path
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2];R=ROOT/'lab/v/shared_readout_20261120/replay';OUT=ROOT/'lab/v/shared_readout_20261120/analysis'
OI=dict(blue='#0072B2',orange='#E69F00',sky='#56B4E9',green='#009E73',verm='#D55E00',purple='#CC79A7',black='#000000')
ARMS=[('P1_native','shared','shared, P1 (native slope)',OI['blue'],'o','-'),('P2_preamp','shared','shared, P2 (preamplifier)',OI['sky'],'s','--'),
      ('P1_native','separate','separate paths, P1',OI['verm'],'^',':'),('P2_preamp','separate','separate paths, P2',OI['orange'],'v','-.'),
      ('none','fixed','fixed knob d = 0',OI['black'],'x',(0,(1,3)))]
def main():
    recs=[json.loads(l) for l in (R/'records.jsonl').read_text().splitlines()]
    H=np.load(R/'histories_1s.npz')
    fig,(a,b)=plt.subplots(1,2,figsize=(12,5.8),gridspec_kw=dict(width_ratios=[1,1.3]))
    for i,(pt,arm,lab,c,mk,ls) in enumerate(ARMS):
        y=[r['eps_vs_offline_final_third_1000s_mV'] for r in recs if r['point']==pt and r['arm']==arm]
        x=i+np.random.default_rng(i).uniform(-.18,.18,len(y));a.scatter(x,y,s=22,color=c,marker=mk,label=lab,alpha=.85)
    a.axhspan(-10,10,color='#bbbbbb',alpha=.35,lw=0);a.text(-.45,10.5,'±10 mV screen',ha='left',va='bottom',fontsize=8)
    a.set_xticks(range(len(ARMS)));a.set_xticklabels(['shared\nP1','shared\nP2','separate\nP1','separate\nP2','fixed\nd = 0'])
    a.set_ylabel('readout error at final knob (mV)\nvs offline shared reference, final third');a.set_title('Residual readout error, 40 draws')
    a.set_ylim(-130,130);a.axhline(0,color='k',lw=.6)
    t=np.arange(1001)
    for j,seed in enumerate((2026112200,2026112227)):
        fe=[r['feasible'] for r in recs if r['seed']==seed and r['arm']=='fixed'][0]
        off=[r['d_final'] for r in recs if r['seed']==seed and r['arm']=='offline_final_third_1000s'][0]
        yo=j*2.4
        if fe:b.fill_between(t,yo+fe[0],yo+fe[1],color='#dddddd',lw=0)
        b.axhline(yo+off,color=OI['green'],lw=1,ls=(0,(5,2)))
        for pt,arm,lab,c,mk,ls in ARMS[:4]:
            b.plot(t,yo+H[f'{seed}|{pt}|{arm}|d'],color=c,ls=ls,lw=1.3,label=lab if j==0 else None)
        top=yo+(fe[1] if fe else 0.)+.08;b.text(5,top,f'draw {seed}: grey = passing range, green dashes = offline reference',fontsize=8,va='bottom')
    b.set_xlabel('time in life (s)');b.set_ylabel('knob d (each draw offset by 2.4)');b.set_title('Knob over life, two refinement draws')
    b.set_yticks([]);b.set_ylim(-1.1,3.4);b.legend(loc='upper center',bbox_to_anchor=(.5,-.13),ncol=2,fontsize=8)
    a.legend(loc='lower left',fontsize=7)
    fig.tight_layout();fig.savefig(OUT/'replay_figure.png',dpi=130);fig.savefig(OUT/'replay_figure.svg')
if __name__=='__main__':main()

"""D173 figure from records.jsonl: per draw, final-third failed events under fixed balance (x) against shared reading
Run with ~/.venvs/simple-learner-tools/bin/python (matplotlib). Okabe-Ito colours, each paired with a marker or line style.
with the physical gate (y), main set; and the paired in-stream share difference by condition set with its interval."""
import json
from pathlib import Path
import numpy as np
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
OUT=Path(__file__).resolve().parents[2]/'lab/v/noisy_shared_20261120'
R=[json.loads(l) for l in (OUT/'records.jsonl').read_text().splitlines()];A=json.loads((OUT/'analysis.json').read_text())
by={}
for r in R:by.setdefault((r['cond'],r['seed']),{})[r['arm']]=r
f=lambda r:r['instream_final']['n']-r['instream_final']['passed']
fig,ax=plt.subplots(1,2,figsize=(11,4.5))
x=[f(v['fixed']) for (c,s),v in by.items() if c=='main'];y=[f(v['shared_P2_g250']) for (c,s),v in by.items() if c=='main']
j=np.random.default_rng(0).uniform(-.15,.15,(2,len(x)))
ax[0].scatter(np.array(x)+j[0],np.array(y)+j[1],s=22,marker='o',color='#0072B2',label='one fresh draw (jittered)')
m=max(max(x),max(y))+1;ax[0].plot([0,m],[0,m],'k--',lw=1,label='no change')
ax[0].set_xlabel('failed final-third events, fixed balance');ax[0].set_ylabel('failed events, shared reading (physical gate)');ax[0].legend();ax[0].set_title('Main set, 100 fresh noisy draws')
sets=['main','drift','weak_inputs','balanced_skew','sparse','old_diagnostic']
for i,c in enumerate(sets):
    p=A[c]['pairs']['shared_P2_g250 - fixed'];lo,hi=p['share_diff_ci'];mu=p['share_diff_mean']
    ax[1].errorbar(mu*100,i,xerr=[[(mu-lo)*100],[(hi-mu)*100]],fmt='s',color='#D55E00',capsize=4)
ax[1].axvline(0,color='k',lw=1);ax[1].axvline(-.5,color='#555555',ls=':',lw=1.5,label='no-harm margin (-0.5 points)')
ax[1].set_yticks(range(len(sets)));ax[1].set_yticklabels([f"{c} ({A[c]['draws']})" for c in sets]);ax[1].invert_yaxis()
ax[1].set_xlabel('shared minus fixed, in-stream pass share (points, 95%)');ax[1].legend(loc='upper center',bbox_to_anchor=(0.5,-0.13),frameon=False);ax[1].set_title('Paired difference by condition set')
fig.tight_layout();fig.savefig(OUT/'figure.png',dpi=120)

"""D80/D81 timing comparison on existing recordings; no simulation."""
import hashlib
import json
from pathlib import Path
import pickle
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'lab'))
from scoring_order_replay import chronology, probability, update


def replay_choice_times(life):
    old=np.ones(len(life['names'])); fixed=old.copy()
    saved=np.zeros(len(old)); fsaved=saved.copy()
    changes=[]
    for kind,row in chronology(life):
        if kind=='prediction':
            a,b=probability(old,row['q']),probability(fixed,row['q'])
            if (a>.5)!=(b>.5) and min(abs(a-.5),abs(b-.5))>1e-12:
                changes.append(dict(t=row['t'],original=a,corrected=b))
        elif row['accepted']:
            update(old,row['scored_q'],row['letter'],saved)
            update(fixed,row['entry']['q'],row['letter'],fsaved)
    return changes


def main():
    inputs=[ROOT/'lab/v/active_mixture_audit.pkl',ROOT/'lab/v/scoring_feedback.pkl']
    tape=pickle.loads(inputs[0].read_bytes())['lives']
    data=pickle.loads(inputs[1].read_bytes())
    lives=data['lives']; out=[]
    for base in lives[:4]:
        fixed=next(r for r in lives[4:] if (r['rule'],r['first'])==(base['rule'],base['first']))
        recorded=next(r for r in tape if r['observe'] and (r['rule'],r['first'])==(base['rule'],base['first']))
        first=dict(colour=None,allocated_count=None,prediction_schedule=None)
        # Compare equal-time prefix only; divergent schedules are not matched observations.
        for a,b in zip(base['predictions'],fixed['predictions']):
            if a[0]!=b[0]:
                first['prediction_schedule']=dict(original_t=a[0],corrected_t=b[0])
                break
            if first['colour'] is None and a[2]!=b[2]:
                first['colour']=dict(t=a[0],original_probability=a[1],corrected_probability=b[1])
            if first['allocated_count'] is None and a[3]!=b[3]:
                first['allocated_count']=dict(t=a[0],original=a[3],corrected=b[3])
        out.append(dict(rule=base['rule'],first=base['first'],fixed_history_choices=replay_choice_times(recorded),
                        closed_loop_equal_time_prefix=first))
    result=dict(lives=out,sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
                script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    text=json.dumps(result,indent=2)+'\n'
    (ROOT/'lab/v/scoring_feedback_analysis.json').write_text(text)
    print(text,end='')


if __name__=='__main__':
    main()

"""D85 failed index checkpoint diagnosis only; no forecast scores."""
import json
from pathlib import Path
import pickle
raw=pickle.loads(Path('lab/v/future_evidence.pkl').read_bytes())['raw']
index=[-1]*len(raw['names']);pending=None;lags=[]
for e in raw['events']:
    if e['kind']=='write':
        index[e['stream']]=e['i'];pending=e['stream']
    elif e['kind'] in ('predict','learn','birth'):
        pending=None
    elif e['kind']=='remove' and e['i']!=index[e['stream']]:
        assert e['i']==index[e['stream']]-1 and pending==e['stream']
        lags.append(dict(seq=e['seq'],stream=e['stream'],i=e['i'],written_index=index[e['stream']],taste=e['taste']))
out=dict(explanation='Net.write is observed before tidy, then cnt increments. Tidy removals report the prior place index.',
    lagged_removals=len(lags),all_follow_same_stream_write_before_next_predict_or_learn=True,examples=lags[:5])
Path('lab/v/retained_prediction_diagnosis.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))

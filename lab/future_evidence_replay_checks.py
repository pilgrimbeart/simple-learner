"""D84 offline counterfactual accounting fixtures; no simulation or fitted mechanism."""
import json
from pathlib import Path
from future_evidence_analysis import replay_candidates


def main():
    defs=[{0:dict(sym=0,u=None,v=None,span=1),1:dict(sym=1,u=None,v=None,span=1),2:dict(sym=None,u=0,v=1,span=2)}]
    words=[{0:(0,),1:(1,),2:(0,1)}]
    raw=dict(prediction_positions=[4],definitions=[{2:dict(birth_seq=1,birth_taste=7)}],names=['event'],speaking={})
    death=dict(stream=0,k=2,seq=3,t=10.,taste=7,counts=[0,1],i=1,version=1)
    contexts=[[dict(seq=5,t=10.,taste=7,hist={0:0,1:1},i=1,version=1,letter=1,living_words=set()),
               dict(seq=6,t=20.,taste=8,hist={0:0,1:1},i=1,version=1,letter=1,living_words={(0,1)}),
               dict(seq=7,t=110.,taste=9,hist={2:0,3:1},i=3,version=2,letter=0,living_words=set()),
               dict(seq=8,t=111.,taste=10,hist={4:0,5:1},i=5,version=3,letter=1,living_words=set())]]
    r=replay_candidates(raw,defs,words,contexts,[death])[0]
    assert r['same_taste_birth'] and not r['survived_prediction'] and not r['actually_spoke']
    assert r['same_taste_remaining_firings']==1 and r['future_firings']==3
    assert r['future_firings_with_equivalent']==1 and r['future_firings_label_consistent']==2
    assert r['unchanged_context_firings']==1 and r['new_history_firings']==2
    assert r['firings_100s']==2 and r['first_delay_s']==10.
    raw['prediction_positions']=[2,4]
    assert replay_candidates(raw,defs,words,contexts,[death])[0]['survived_prediction']
    out=dict(passed=True,simulated_steps=0,checks=['same-taste exclusion','prediction survival','100s inclusive boundary','unchanged context','exact living equivalent','label agreement'])
    Path('lab/v/future_evidence_replay_checks.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()

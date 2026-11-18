"""D85 deterministic forecasting and reconstruction checks, zero simulated lives."""
import copy
import itertools
import json
import math
from pathlib import Path
from retained_prediction import new_score, probability, score_and_update, speaker, reconstruct


def candidate():
    return dict(counts=[1,0],weight=.5,full=new_score(),horizon=new_score())


def main():
    checks=[]
    a,b=candidate(),candidate()
    pa=score_and_update(a,.8,0,True)
    pb=score_and_update(b,.8,1,True)
    assert pa == pb == (.25,.525)
    assert a['counts']==[2,0] and b['counts']==[1,1]
    assert abs(b['full']['retained_bits']-2)<1e-12
    checks.append('prediction independent of current label; score before update')
    for labels in itertools.product((0,1),repeat=6):
        c=candidate()
        for i,label in enumerate(labels):
            score_and_update(c,.2 if i%2 else .8,label,i<3)
        for s in (c['full'],c['horizon']):
            assert s['mixture_bits'] <= min(s['retained_bits'],s['baseline_bits'])+1+1e-12
    checks.append('one-bit mixture bound on all 64 binary length-six sequences and prefixes')
    living={0:[1,0],1:[0,0],2:[2,0],3:[2,0]}
    words={0:(0,),1:(1,),2:(0,1),3:(0,1)}
    assert speaker(living,words,{0:0,1:1},1)==2
    living[2]=[1,1]
    assert speaker(living,words,{0:0,1:1},1)==3
    living[3]=[1,1]
    assert speaker(living,words,{0:0,1:1},1) is None
    checks.append('native longest/confidence/insertion tie selection and silence')
    defs={0:dict(sym=0,u=None,v=None,span=1),1:dict(sym=1,u=None,v=None,span=1),2:dict(sym=None,u=0,v=1,span=2)}
    events=[]
    def emit(kind,**kw):events.append(dict(seq=len(events),kind=kind,**kw))
    emit('write',stream=0,i=0,sym=0,keep=False,changed=True,version=1)
    emit('write',stream=0,i=1,sym=1,keep=False,changed=True,version=2)
    emit('predict',t=0.)
    emit('learn',stream=0,i=1,t=10.,taste=0,letter=0,living=[0,1],firing=[1])
    emit('birth',stream=0,k=2,t=10.,taste=0)
    emit('remove',stream=0,k=2,i=1,t=10.,taste=0,counts=[1,0])
    emit('predict',t=10.)
    emit('learn',stream=0,i=1,t=20.,taste=1,letter=1,living=[0,1],firing=[1])
    emit('predict',t=20.)
    emit('learn',stream=0,i=1,t=30.,taste=2,letter=1,living=[0,1],firing=[1])
    emit('predict',t=30.)
    raw=dict(classes=['Net'],initial_histories=[{}],definitions=[{k:dict(definition=d,birth_seq=-1 if k<2 else 4,birth_taste=None if k<2 else 0) for k,d in defs.items()}],
        names=['event'],hist_limit=96,events=events,speaking={(0,1):dict(first_seq=6,count=2)},
        counters=dict(predict_calls=4,learn_calls=3,adds=1,removals=1))
    rows,validation,tastes=reconstruct(raw)
    assert len(rows)==1 and rows[0]['full']['n']==2
    assert rows[0]['full']['baseline_silent']==1
    assert rows[0]['counts']==[1,2]
    assert abs(rows[0]['full']['baseline_bits']-3)<1e-12
    assert rows[0]['full']['retained_saving_bits']==0
    broken=copy.deepcopy(raw);broken['events'][5]['counts']=[0,1]
    try:reconstruct(broken)
    except AssertionError:pass
    else:raise AssertionError('Corrupt removal tally accepted')
    checks.append('complete reconstruction, newborn removal, last-issued forecast, corrupted checkpoint refusal')
    tidy=copy.deepcopy(raw)
    tidy['events'].insert(5,dict(kind='write',stream=0,i=2,sym=0,keep=False,changed=True,version=3))
    for seq,e in enumerate(tidy['events']):
        e['seq']=seq
        if e['kind']=='learn' and e['t']>10.:
            e['i']=2;e['firing']=[0]
    tidy['speaking']={(0,0):dict(first_seq=9,count=2)}
    rows,validation,_=reconstruct(tidy)
    assert validation['tidy_removals_before_index_increment']==1 and rows[0]['full']['n']==0
    checks.append('tidy deletion after write but before counter increment')
    out=dict(passed=True,checks=checks,simulated_steps=0)
    Path('lab/v/retained_prediction_checks.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':main()

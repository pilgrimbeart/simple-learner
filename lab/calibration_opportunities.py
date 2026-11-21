"""D160 opportunity audit; retrospective conditioning, no causal or learning claim."""
import json,math,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,digest,provenance
OUT=ROOT/'lab/v/calibration_opportunities';SRC=ROOT/'lab/v/order_baseline_stream'
def main():
    OUT.mkdir(exist_ok=True);protocol=dict(source=str(SRC),measured_window_s=[200/3,100.],simultaneous_probability=4/34,opportunity_probability=.95,budget_s=30,scope='Post-result association and generator probability, no causal conditioning or sufficient-learning claim')
    with (OUT/'protocol.json').open('x') as f:json.dump(protocol,f,indent=2)
    streams=json.loads((SRC/'streams.json').read_text());draws=json.loads((SRC/'draws.json').read_text());counts=[]
    for r in streams:
        events=[e for e in r['events'] if e['first_s']>=200/3];n=len(events);ns=sum(bool(e['case']['a'] and e['case']['b'] and e['case']['delay']==0) for e in events)
        counts.append(dict(seed=r['seed'],spacing_s=r['spacing_s'],events=n,simultaneous_events=ns,probability_zero_given_n=(1-4/34)**n))
    table={}
    for spacing in [1.,2.5,10.]:
      for mode in sorted({r['mode'] for r in draws}):
        groups={}
        for cat in ['zero','one','multiple']:
            cc=[r for r in counts if r['spacing_s']==spacing and ('zero' if not r['simultaneous_events'] else 'one' if r['simultaneous_events']==1 else 'multiple')==cat]
            seeds={r['seed'] for r in cc};dd=[r for r in draws if r['spacing_s']==spacing and r['mode']==mode and r['seed'] in seeds]
            groups[cat]=dict(draws=len(dd),adequate=sum(r['all_pass'] for r in dd))
        table[f'{spacing}:{mode}']=groups
    n=math.ceil(math.log(.05)/math.log(1-4/34));assert (1-4/34)**n<=.05<(1-4/34)**(n-1)
    result=dict(event_count_for_95pct_at_least_one=n,approximate_life_s_if_only_last_third_used={str(s):3*n*s for s in [1.,2.5,10.]},observed_zero={str(s):sum(r['simultaneous_events']==0 for r in counts if r['spacing_s']==s) for s in [1.,2.5,10.]},expected_zero_conditional_on_counts={str(s):sum(r['probability_zero_given_n'] for r in counts if r['spacing_s']==s) for s in [1.,2.5,10.]},conditioning=table)
    prov=provenance();prov['files'].update({str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__).resolve(),SRC/'streams.json',SRC/'draws.json',ROOT/'lab/order_baseline_stream.py']});prov['protocol_sha256']=digest(OUT/'protocol.json')
    for name,obj in [('provenance',prov),('summary',result),('rows',counts)]: (OUT/f'{name}.json').write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()

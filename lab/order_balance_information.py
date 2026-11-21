"""D155 informed gain-capacity and observation diagnostic, no learned circuit."""
import copy,json,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from population_trace_margin import predict,SRC
from dynamic_parts_bench import ROOT,digest,provenance
OUT=ROOT/'lab/v/order_balance_information'
def bounds(case):
    pair=case['a']>0 and case['b']>0;d=case['delay']
    if pair and 0<abs(d)<=.15:return (.03,float('inf')) if d>0 else (-float('inf'),-.03)
    m=.06 if pair and d==0 else .03
    return -m,m

def main():
    OUT.mkdir(exist_ok=True)
    protocol=dict(source=str(SRC),threshold_V=.15,knob='positive gain*(1+d), negative gain*(1-d); d in [-1,1]',
        references=['unchanged','simultaneous','balanced_order','biased_order'],biased_positive_fraction=.8,steps_s=[.00005,.000025],budget_s=180,
        scope='Analytic current/readout reference on reused cases, no physically implemented knob or event classifier')
    with (OUT/'protocol.json').open('x') as f:json.dump(protocol,f,indent=2)
    rows=[json.loads(l) for l in SRC.read_text().splitlines()];dt=min(r['dt'] for r in rows);rows=[r for r in rows if r['dt']==dt and not r['control']];assert len(rows)==1360
    old=json.loads((ROOT/'lab/v/population_trace_margin/rows.json').read_text());old={(r['seed'],r['case']['id']):r for r in old if r['mode']=='original'}
    records=[];reconstruction=0.;refine=0.;start=time.monotonic()
    def split(row,h):
        orig=predict(row,.15,h)
        pos=copy.deepcopy(row);pos['elements'][0][6]=0.
        p=predict(pos,.15,h)['order_V']
        return orig,p,orig['order_V']-p
    for row in rows:
        orig,p,n=split(row,.00005);u=p+n;v=p-n
        reconstruction=max(reconstruction,abs(u-old[row['seed'],row['case']['id']]['order_V']))
        if row['seed']==rows[0]['seed']:
            _,pp,nn=split(row,.000025);refine=max(refine,abs(p-pp),abs(n-nn))
        records.append(dict(seed=row['seed'],case=row['case'],u_V=u,v_V=v,coincidence_adequate=orig['coincidence_adequate']))
        if time.monotonic()-start>180:raise RuntimeError('Budget exceeded; incomplete output is not a result')
    assert reconstruction<1e-12
    summaries=[];scored=[]
    for seed in sorted({r['seed'] for r in records}):
        rr=[r for r in records if r['seed']==seed];lo,hi=-1.,1.
        for r in rr:
            lower,upper=bounds(r['case']);u,v=r['u_V'],r['v_V']
            if abs(v)<1e-15:
                if not lower<u<upper:lo,hi=1.,-1.
            else:
                aa,bb=(lower-u)/v,(upper-u)/v
                lo=max(lo,min(aa,bb));hi=min(hi,max(aa,bb))
        simultaneous=[r for r in rr if r['case']['a'] and r['case']['b'] and r['case']['delay']==0]
        near=[r for r in rr if r['case']['a'] and r['case']['b'] and 0<abs(r['case']['delay'])<=.15]
        settings={'unchanged':0.,'simultaneous':-sum(r['u_V']*r['v_V'] for r in simultaneous)/sum(r['v_V']**2 for r in simultaneous)}
        for name,prior in [('balanced_order',.5),('biased_order',.8)]:
            weights=np.array([prior if r['case']['delay']>0 else 1-prior for r in near]);us=np.array([r['u_V'] for r in near]);vs=np.array([r['v_V'] for r in near]);den=float(weights@vs);assert abs(den)>1e-12
            settings[name]=-float(weights@us)/den
        ss=dict(seed=seed,feasible_order=lo<hi,feasible_interval=[lo,hi],coincidence_all=all(r['coincidence_adequate'] for r in rr),settings={})
        for mode,raw in settings.items():
            d=float(np.clip(raw,-1,1));passed=[];rescued=harmed=0
            for r in rr:
                lower,upper=bounds(r['case']);y=r['u_V']+d*r['v_V'];good=bool(lower<y<upper and r['coincidence_adequate']);base=bool(lower<r['u_V']<upper and r['coincidence_adequate'])
                passed.append(good);rescued+=good and not base;harmed+=base and not good
                scored.append(dict(seed=seed,mode=mode,case=r['case'],d=d,output_V=y,passed=good))
            ss['settings'][mode]=dict(raw_d=raw,d=d,passed=sum(passed),all_pass=all(passed),rescued=rescued,harmed=harmed)
        summaries.append(ss)
    result=dict(reconstruction_max_error_V=reconstruction,first_draw_branch_refinement_max_V=refine,capacity_feasible_draws=sum(s['feasible_order'] and s['coincidence_all'] for s in summaries),draws=40,comparisons={})
    for mode in protocol['references']:
        mm=[s['settings'][mode] for s in summaries];result['comparisons'][mode]=dict(adequate_draws=sum(m['all_pass'] for m in mm),adequate_cases=sum(m['passed'] for m in mm),rescued=sum(m['rescued'] for m in mm),harmed=sum(m['harmed'] for m in mm),knob_range=[min(m['d'] for m in mm),max(m['d'] for m in mm)])
    prov=provenance();prov['files'].update({str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__).resolve(),SRC,ROOT/'lab/population_trace_margin.py',ROOT/'lab/v/population_trace_margin/rows.json']});prov['protocol_sha256']=digest(OUT/'protocol.json')
    for name,obj in [('provenance',prov),('summary',result),('draws',summaries),('branches',records),('rows',scored)]: (OUT/f'{name}.json').write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()

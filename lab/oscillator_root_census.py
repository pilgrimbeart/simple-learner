"""D159 scalar nullcline census; full drift, no trajectories or global cycle claim."""
import copy,json,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,build,definitions,digest,provenance
from dynamic_parts_failure import drift,jacobian
from units import RAIL
OUT=ROOT/'lab/v/oscillator_root_census'
def field(x,y,c):
    v=np.array(np.broadcast_arrays(x,y));node=c.node_arr;kp,kn=c.cfg[3:5]
    fade=lambda d,k:1-np.exp(-np.maximum(d,0)/k)
    currents=np.array([node[0,i]*(fade(RAIL-v[i],kp) if node[0,i]>0 else fade(v[i]+RAIL,kn))-node[1,i]*v[i] for i in [0,1]])
    for j in range(c.link.shape[1]):
        dest,source,gate=c.link[:,j];gain,offset,slope,tau,sig=c.el_arr[:,j];assert gate==-1 and tau==0 and sig==0
        w=np.sign(gain)*np.tanh(slope*(v[source]-offset))
        currents[dest]+=abs(gain)*((1+w)*fade(RAIL-v[dest],kp)-(1-w)*fade(v[dest]+RAIL,kn))/2
    return currents/np.array([node[2,i]*np.ones_like(v[i]) for i in [0,1]])
def slow(x,c):
    x=np.asarray(x);lo=np.full_like(x,-RAIL);hi=np.full_like(x,RAIL)
    assert np.all(field(x,lo,c)[1]>0) and np.all(field(x,hi,c)[1]<0)
    for _ in range(50):
        mid=(lo+hi)/2;positive=field(x,mid,c)[1]>0;lo=np.where(positive,mid,lo);hi=np.where(positive,hi,mid)
    return (lo+hi)/2

def roots(c,n):
    x=np.linspace(-RAIL,RAIL,n);y=slow(x,c);f=field(x,y,c)[0];cross=np.flatnonzero(f[:-1]*f[1:]<0);found=[]
    for i in cross:
        lo,hi=x[i],x[i+1];flo=f[i]
        for _ in range(45):
            mid=(lo+hi)/2;fm=float(field(mid,slow(mid,c),c)[0])
            if flo*fm>0:lo=mid;flo=fm
            else:hi=mid
        xx=(lo+hi)/2;yy=float(slow(xx,c));v=np.array([xx,yy]);j=jacobian(v,c);ev=np.linalg.eigvals(j)
        found.append(dict(root_V=v.tolist(),residual_V_per_s=float(np.linalg.norm(drift(v,c))),trace_per_s=float(np.trace(j)),det_per_s2=float(np.linalg.det(j)),max_real_per_s=float(max(ev.real)),stable=bool(max(ev.real)<0)))
    # Exact sampled zeros are exceptional: fail loudly rather than omit them.
    assert not np.any(f==0.)
    return found

def main():
    OUT.mkdir(exist_ok=True);src=ROOT/'lab/v/dynamic_parts/margin_v2.json';prior=json.loads(src.read_text())['analysis'];modes=['actual','zero_self_offset','zero_recovery_offset','zero_slow_offset']
    protocol=dict(seeds=[r['seed'] for r in prior],modes=modes,grids=[8193,16385],source=str(src),budget_s=120,scope='Numerical root brackets, no certificate against tangent roots or proof about cycles; diagnostic offset equalisation only')
    with (OUT/'protocol.json').open('x') as f:json.dump(protocol,f,indent=2)
    result=[];maxvalidation=maxoriginal=maxrefinement=0.;start=time.monotonic()
    for r in prior:
      c=build('oscillator',definitions()['oscillator'],r['seed'])
      for mode in modes:
        cc=copy.deepcopy(c)
        if mode!='actual':cc.el_arr[1,modes.index(mode)-1]=0.
        test=np.array([[-.4,.2],[.0,0.],[.3,-.1]])
        for v in test:maxvalidation=max(maxvalidation,float(np.max(np.abs(field(*v,cc)-drift(v,cc)))))
        coarse=roots(cc,8193);fine=roots(cc,16385);assert len(coarse)==len(fine)
        for a,b in zip(coarse,fine):maxrefinement=max(maxrefinement,float(np.max(np.abs(np.array(a['root_V'])-b['root_V']))))
        if mode=='actual':maxoriginal=max(maxoriginal,min(float(np.linalg.norm(np.array(v['root_V'])-r['cases']['actual']['root_V'])) for v in fine))
        result.append(dict(seed=r['seed'],mode=mode,roots=fine,original_cycle_pass=r['cycle_pass']))
        if time.monotonic()-start>120:raise RuntimeError('Budget exceeded')
      print('completed',r['seed'],round(time.monotonic()-start,1),flush=True)
    assert maxvalidation<1e-10 and maxoriginal<1e-7 and max(v['residual_V_per_s'] for r in result for v in r['roots'])<1e-8
    summary=dict(vector_drift_validation_max_V_per_s=maxvalidation,original_root_difference_max_V=maxoriginal,grid_root_difference_max_V=maxrefinement,comparisons={})
    for mode in modes:
        rr=[r for r in result if r['mode']==mode];summary['comparisons'][mode]=dict(root_counts=sorted({len(r['roots']) for r in rr}),draws_with_stable_root=[r['seed'] for r in rr if any(v['stable'] for v in r['roots'])])
    prov=provenance();prov['files'].update({str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__).resolve(),src,ROOT/'lab/dynamic_parts_failure.py']});prov['protocol_sha256']=digest(OUT/'protocol.json')
    for name,obj in [('provenance',prov),('summary',summary),('rows',result)]: (OUT/f'{name}.json').write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()

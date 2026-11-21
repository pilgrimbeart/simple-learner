"""Frozen numerical helpers for the 2026-11-19 overnight measurement work order.
These helpers perform observer arithmetic only; they do not implement a brain.
"""
from pathlib import Path
import json
import numpy as np
ROOT = Path(__file__).resolve().parents[1]

def read_json(relative):
    return json.loads((ROOT / relative).read_text())

def partition_integrals(t, values, edges):
    """Integrals of the piecewise-linear sampled signal on consecutive edge intervals.
    Split crossing trapezoids exactly, instead of dropping/recounting boundary samples.
    values is one dimensional. edges must lie in [t[0], t[-1]].
    """
    t=np.asarray(t,dtype=float);v=np.asarray(values,dtype=float);e=np.asarray(edges,dtype=float)
    if t.ndim!=1 or v.shape!=t.shape or e.ndim!=1:raise ValueError('Invalid shape')
    if len(t)<2 or len(e)<2 or not np.all(np.diff(t)>0) or not np.all(np.diff(e)>0):raise ValueError('Times must increase')
    if not np.all(np.isfinite(v)) or e[0]<t[0] or e[-1]>t[-1]:raise ValueError('Invalid domain')
    dt=np.diff(t);prefix=np.r_[0.,np.cumsum(dt*(v[:-1]+v[1:])/2)]
    j=np.clip(np.searchsorted(t,e,side='right')-1,0,len(t)-2);h=e-t[j]
    primitive=prefix[j]+h*v[j]+h*h*(v[j+1]-v[j])/(2*dt[j])
    return np.diff(primitive)

def old_case_limits(case):
    pair=case['a']>0 and case['b']>0;delay=case['delay']
    if pair and 0<abs(delay)<=.15:
        return (.03,float('inf')) if delay>0 else (-float('inf'),-.03)
    margin=.06 if pair and delay==0 else .03
    return -margin,margin

def score_branches(rows,d):
    """Frozen old static criteria; no replacement for circuit/reliability assessment."""
    result=[]
    for r in rows:
        lo,hi=old_case_limits(r['case']);y=r['u_V']+d*r['v_V']
        result.append(dict(case_id=r['case']['id'],order_V=y,
            order_ok=bool(lo<y<hi),coincidence_ok=bool(r['coincidence_adequate']),
            passed=bool(lo<y<hi and r['coincidence_adequate'])))
    return result

def setting(numerator,denominator):
    if not np.isfinite(numerator) or not np.isfinite(denominator):raise ValueError('Nonfinite observation')
    if abs(denominator)<=1e-12:
        return dict(identifiable=False,raw_d=None,d=None,clipped=False)
    raw=-numerator/denominator
    return dict(identifiable=True,raw_d=float(raw),d=float(np.clip(raw,-1,1)),clipped=bool(abs(raw)>1))

def self_check():
    t=np.array([0.,.1,.4,1.]);edges=np.array([0.,.13,.8,1.]);got=partition_integrals(t,2*t+1,edges)
    assert np.max(abs(got-np.diff(edges*edges+edges)))<1e-14
    assert abs(sum(got)-2.)<1e-14
    assert setting(1.,0.)['identifiable'] is False
    assert setting(-3.,1.)['d']==1.
    return {'piecewise_linear_boundary_check':'passed','unidentifiable_and_clip_checks':'passed'}

if __name__=='__main__':print(json.dumps(self_check(),indent=2))

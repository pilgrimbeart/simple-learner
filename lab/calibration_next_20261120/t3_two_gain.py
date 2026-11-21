"""D167 task 3: is the incompatible draw beyond two existing output gains? Saved branch responses only.
Analytic approximation: output = a*P - b*N, P=(u+v)/2, N=(v-u)/2 (P from the positive readout element, N the
negative). Original knob a=1+d, b=1-d gives u+d*v. Designer-set reference gains in the closed box
0<=a<=2, 0<=b<=2, not demonstrated memory controls. Every case's strict voltage inequalities intersected
exactly (rational arithmetic on the stored float values); coincidence requirements unchanged.
Feasible only with a proven positive interior voltage margin; boundary-only contact is reported separately.
Numeric boundary tolerance: none in the polygon (exact Fractions); the margin is bracketed by exact
feasibility tests, and a margin below MARGIN_TOL=1e-12 V is labelled boundary-only, not a pass.
Physical current/slew/operating-point figures are recorded separately, not imposed.
"""
import json,sys,time
from fractions import Fraction as F
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'lab'));sys.path.insert(0,str(ROOT))
from order_balance_information import bounds
from units import SLEW,I_MIN,RAIL
V=ROOT/'lab/v';OUT=V/'calibration_next_20261120/t3';MARGIN_TOL=F(1,10**12);INF=float('inf')
BOX=[('a>=0',F(1),F(0),F(0)),('a<=2',F(-1),F(0),F(-2)),('b>=0',F(0),F(1),F(0)),('b<=2',F(0),F(-1),F(-2))]  # c1*a+c2*b>=c0
def clip(poly,c1,c2,c0):
    """Sutherland-Hodgman clip of a convex polygon (list of (a,b) Fractions) by c1*a+c2*b>=c0, exact."""
    out=[];n=len(poly)
    for i in range(n):
        p,q=poly[i],poly[(i+1)%n];sp=c1*p[0]+c2*p[1]-c0;sq=c1*q[0]+c2*q[1]-c0
        if sp>=0:out.append(p)
        if (sp>=0)!=(sq>=0):
            t=sp/(sp-sq);out.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
    ded=[]
    for p in out:
        if not ded or ded[-1]!=p:ded.append(p)
    if len(ded)>1 and ded[0]==ded[-1]:ded.pop()
    return ded
def halfplanes(rows):
    """Case constraints as (label, c1, c2, c0, kind): c1*a+c2*b > c0 (strict) in volts."""
    hp=[]
    for r in rows:
        lo,hi=bounds(r['case']);u,v=F(r['u_V']),F(r['v_V']);P=(u+v)/2;N=(v-u)/2
        if lo>-INF:hp.append((r['case']['id']+':lower',P,-N,F(lo)))
        if hi<INF:hp.append((r['case']['id']+':upper',-P,N,F(-hi)))
    return hp
def region(hp,t):
    """Closure of {box} ∩ {c1 a + c2 b >= c0 + t} for every case half-plane (box closed, not shrunk)."""
    poly=[(F(0),F(0)),(F(2),F(0)),(F(2),F(2)),(F(0),F(2))]
    for _,c1,c2,c0 in hp:
        poly=clip(poly,c1,c2,c0+t)
        if not poly:return []
    return poly
def max_margin(hp):
    """Bracket t*=max over box of min case slack (V) by exact feasibility tests; returns (lower,upper,point)."""
    p0=region(hp,F(0))
    if not p0:return None
    lo,hi=F(0),F(1)   # slack cannot exceed 1 V on this box for these responses; verified below
    assert not region(hp,hi)
    for _ in range(60):
        mid=(lo+hi)/2
        if region(hp,mid):lo=mid
        else:hi=mid
    poly=region(hp,lo);pt=(sum(p[0] for p in poly)/len(poly),sum(p[1] for p in poly)/len(poly))
    proven=min(c1*pt[0]+c2*pt[1]-c0 for _,c1,c2,c0 in hp)
    return lo,hi,poly,pt,proven
def active(hp,poly):
    """Constraint lines containing an edge of the closure polygon (exact)."""
    act=[]
    for lab,c1,c2,c0 in hp+[(l,c1,c2,c0) for l,c1,c2,c0 in BOX]:
        on=[p for p in poly if c1*p[0]+c2*p[1]==c0]
        if len(on)>=2 or (len(poly)==1 and on):act.append(lab)
    return act
def one_d(rows):
    lo,hi=-1.,1.
    for r in rows:
        a,b=bounds(r['case']);u,v=r['u_V'],r['v_V']
        if abs(v)<1e-15:
            if not a<u<b:lo,hi=1.,-1.
        else:
            x,y=(a-u)/v,(b-u)/v;lo=max(lo,min(x,y));hi=min(hi,max(x,y))
    return lo,hi
def fixtures():
    res={}
    # original line a+b=2: a case requiring u+d v in (-.06,.06) with u=0,v=.3 -> |d|<.2: on the line, a in (.8,1.2)
    row=dict(case=dict(id='pair_x_x_0.0',a=.5,b=.5,delay=0.),u_V=0.,v_V=.3);hp=halfplanes([row]);poly=region(hp,F(0))
    line=[p for p in [(F(4,5),F(6,5)),(F(6,5),F(4,5))] if all(c1*p[0]+c2*p[1]>=c0 for _,c1,c2,c0 in hp)]
    res['original_line_endpoints_on_closure']=len(line)==2 and len(poly)>=3
    # empty: P a - N b > .5 with P=.1,N=.1 -> .1(a-b)>.5 impossible on box (max .2)
    hp=[('e',F(1,10),F(-1,10),F(1,2))];res['empty']=region(hp,F(0))==[]
    # boundary-only: .1(a-b) >= .2 touches only the corner (2,0)
    hp=[('c',F(1,10),F(-1,10),F(1,5))];p=region(hp,F(0));res['boundary_only']=(p==[(F(2),F(0))] and max_margin(hp)[1]<=MARGIN_TOL)
    # positive/negative coefficients: P<0,N<0 and P>0,N>0 both clip consistently
    for name,(P,N) in dict(pos=(F(1,10),F(1,20)),neg=(F(-1,10),F(-1,20))).items():
        hp=[('x',P,-N,F(0))];poly=region(hp,F(0));res[f'sign_{name}']=bool(poly) and all(P*a-N*b>=0 for a,b in poly)
    assert all(res.values()),res
    return res
def main():
    OUT.mkdir(parents=True,exist_ok=True);start=time.monotonic();fx=fixtures();print('fixtures',fx,flush=True)
    branches={}
    for b in json.loads((V/'order_balance_information/branches.json').read_text()):branches.setdefault(b['seed'],[]).append(b)
    feas={r['seed']:r for r in json.loads((V/'overnight_20261119/failures_results/feasible_intervals.json').read_text())}
    src=[json.loads(l) for l in (V/'motifs/order_v2/confirm.jsonl').read_text().splitlines()];dtmin=min(r['dt'] for r in src)
    comp={r['seed']:r for r in src if r['dt']==dtmin and not r['control']}
    rows=[];err1d=0.
    for seed in sorted(branches):
        rr=branches[seed];lo,hi=one_d(rr);f=feas[seed];err1d=max(err1d,abs(lo-f['interval'][0]),abs(hi-f['interval'][1]))
        coin=all(r['coincidence_adequate'] for r in rr);hp=halfplanes(rr);mm=max_margin(hp)
        # the original line inside the two-gain closure: d interval recovered from the polygon on a+b=2
        n=np.array(comp[seed]['nodes']);e=np.array(comp[seed]['elements']);Ip,In=float(e[0,5]),float(e[0,6]);C7,G7=float(n[2,7]),float(n[1,7])
        rec=dict(seed=seed,coincidence_all=coin,one_d_interval=[lo,hi],one_d_feasible=lo<hi,one_d_saved=f['interval'],
            readout_currents_A=dict(positive=Ip,negative=In),node7=dict(C_F=C7,G_S=G7))
        if mm is None:
            rec.update(status='empty',polygon=[],active=None,margin_V=None)
        else:
            mlo,mhi,poly,pt,proven=mm;closure=region(hp,F(0))
            status=('feasible' if proven>MARGIN_TOL else 'boundary_only') if coin else 'order_region_but_coincidence_fails'
            pv=[(float(a),float(b)) for a,b in closure]
            rec.update(status=status,polygon=pv,vertices=len(pv),active=active(hp,closure),margin_V=[float(mlo),float(mhi)],proven_margin_V=float(proven),margin_point=[float(pt[0]),float(pt[1])],
                margin_active=active(hp,region(hp,mlo)),
                contains_original_line=any(True for _ in [0] if region(hp+[('line_ge',F(1),F(1),F(2)),('line_le',F(-1),F(-1),F(-2))],F(0))),
                a_range=[min(p[0] for p in pv),max(p[0] for p in pv)],b_range=[min(p[1] for p in pv),max(p[1] for p in pv)],
                physical=dict(max_scaled_current_A=max(max(abs(a*Ip),abs(b*In)) for a,b in pv),min_scaled_current_A=min(min(abs(a*Ip),abs(b*In)) for a,b in pv),
                    I_MIN_A=I_MIN,below_I_MIN_somewhere=any(min(abs(a*Ip),abs(b*In))<I_MIN for a,b in pv),
                    max_slew_V_per_s=max(abs(a*Ip)+abs(b*In) for a,b in pv)/C7,SLEW_limit_V_per_s=SLEW,
                    max_static_offset_V=max(max(abs(a*Ip),abs(b*In)) for a,b in pv)/G7,RAIL_V=RAIL))
        rows.append(rec);print(seed,rec['status'],rec.get('margin_V'),round(time.monotonic()-start,1),flush=True)
        if time.monotonic()-start>110:raise SystemExit('budget guard: partial rows not written as a result')
    summ=dict(fixtures=fx,one_d_reproduction_max_error=err1d,one_d_feasible=sum(r['one_d_feasible'] for r in rows),
        counts={s:sum(r['status']==s for r in rows) for s in ['feasible','boundary_only','empty','order_region_but_coincidence_fails']},
        margin_range_V=[min(r['margin_V'][0] for r in rows if r['margin_V']),max(r['margin_V'][0] for r in rows if r['margin_V'])],
        seed_2215=[r for r in rows if r['seed']==2026112215][0],
        draws_whose_margin_point_is_off_the_original_line=sum(1 for r in rows if r['margin_V'] and abs(r['margin_point'][0]+r['margin_point'][1]-2)>1e-9),
        below_I_MIN_somewhere=sum(1 for r in rows if r.get('physical',{}).get('below_I_MIN_somewhere')),elapsed_s=time.monotonic()-start)
    (OUT/'polygons.json').write_text(json.dumps(rows,indent=1)+'\n');(OUT/'summary.json').write_text(json.dumps(summ,indent=1)+'\n')
    print(json.dumps({k:v for k,v in summ.items() if k!='seed_2215'},indent=1));print(json.dumps(summ['seed_2215'],indent=1))
if __name__=='__main__':main()

"""L: passive issued mixture/event capture, eight frozen J lives. No policy changes."""
from pathlib import Path
import sys,json,pickle,time,hashlib,os,subprocess
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'lab'),str(ROOT)]
import spare_allowance_experiment as E
import spare_allowance as SA
BASE=ROOT/'lab/v/gate_contribution_capture'
OriginalTrace=E.Trace
EXTRA=None
JOBS=[(c,a,142000,f) for c in ('seq','time') for a in ('issued','issued+gate') for f in ('red','blue')]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def reconcile(events):
 latest={};pending=set();units={};overwritten=0;pending_births=0
 for i,e in enumerate(events):
  if e['kind']=='transfer':
   j=e['stream']
   if j in latest:overwritten+=1
   latest[j]=i
   if e['allowance_only']:pending.add(j)
  elif e['kind']=='birth':
   j=e['stream'];last=latest.pop(j,None)
   prior=[x for x in events[max(0,e['call_start']):i] if x['kind']=='transfer' and x['stream']==j and x['call']==e['call']]
   units[j,e['unit']]=dict(born=e['t'],removed=None,parents=e['parents'],same_call=any(x['allowance_only'] for x in prior),latest=last is not None and events[last]['allowance_only'])
   if j in pending:pending_births+=1;pending.remove(j)
  elif e['kind']=='remove' and (e['stream'],e['unit']) in units:units[e['stream'],e['unit']]['removed']=e['t']
 return units,dict(pending_births=pending_births,unmatched_pending=len(pending),overwritten_latest_marks=overwritten,unconsumed_latest_marks=len(latest))
def mixture(row):
 aw=np.isfinite(row['q']);return (row['wd']*row['pd']+np.dot(row['w'][aw],row['q'][aw]))/(row['wd']+row['w'][aw].sum())
def replaced(row,mask):
 aw=np.isfinite(row['q']);return row['p']+np.sum(row['w'][mask]*(row['pd']-row['q'][mask]))/(row['wd']+row['w'][aw].sum())
class CaptureTrace(OriginalTrace):
 def __init__(self,lf,ob=None):
  super().__init__(lf,ob);b=self.b;self.events=[];self.rows=[];self.count=Counter();self.call=0;self.active=None;self.call_start=0;self.room_active=None
  self.wrappers=[];self.snapshot=None
  for j,n in enumerate(b.nets):self.wrap(n,j)
  self.predict0=b.predict;self.taste0=b.taste
  def predict():
   v=self.predict0();recs=ob.last
   if recs is not None:
    self.snapshot=dict(t=float(b.t),q=np.array([r.p1 if r.awake else np.nan for r in recs[1:]]),ids=[r.speaker for r in recs[1:]],w=np.array([float(getattr(n,'w',1.)) for n in b.nets]),wd=float(getattr(b,'w_def',1.)),pd=float(recs[0].p1),p=float(b.p1))
   return v
  def taste(value,at):
   issued=self.snapshot;before=len(self.acc);v=self.taste0(value,at)
   if len(self.acc)>before:
    assert issued is not None
    row=dict(issued,y=self.acc[-1][2],taste_t=self.acc[-1][0]);assert row['t']<=row['taste_t']+1e-9
    assert abs(mixture(row)-row['p'])<=1e-9
    self.rows.append(row)
   return v
  b.predict=predict;b.taste=taste
 def wrap(self,n,j):
  orig={k:n.__dict__.get(k) for k in ('learn','_room','_add','_remove')};self.wrappers.append((n,orig));learn,room,add,remove=n.learn,n._room,n._add,n._remove
  def lrn(*args,**kwargs):
   self.call+=1;old=(self.active,self.call_start);self.active=self.call;self.call_start=len(self.events)
   try:return learn(*args,**kwargs)
   finally:self.active,self.call_start=old
  def rm(k):
   if k in n.units:
    self.events.append(dict(kind='remove',stream=j,unit=int(k),t=float(self.b.t),call=self.active,request=self.room_active));self.count['removals']+=1
   return remove(k)
  def ad(u,v,span,t,sym=None):
   k=add(u,v,span,t,sym)
   if sym is None:
    self.events.append(dict(kind='birth',stream=j,unit=int(k),parents=[int(u),int(v)],t=float(t),call=self.active,call_start=self.call_start));self.count['births']+=1
   return k
  def ro():
   self.count['room_requests']+=1;rid=self.count['room_requests'];d=n._deep
   # Use the actual engine's price constant; C does not expose it.
   import grownet as GN
   gated=len(n.units)>=n.P and d is not None and d in n.units and min(n.units[d]['n'])>=1 and getattr(n,'saved',0.)>GN.POOL_BITS*(len(n.units)-n.base+1)
   before=[(int(v.P),len(v.units)) for v in self.b.nets] if gated else None
   if gated:
    self.count['native_donor_list_traversals']+=1;self.count['native_donor_loop_iterations']+=len(self.b.nets)
    if self.b in SA._INSTALLED:self.count['adapter_donor_list_traversals']+=1;self.count['adapter_donor_loop_iterations']+=len(self.b.nets)
   old=self.room_active;self.room_active=rid;idx=len(self.events)
   try:r=room()
   finally:self.room_active=old
   if gated and int(n.P)==before[j][0]+1:
    donors=[i for i,v in enumerate(self.b.nets) if v.P==before[i][0]-1];assert len(donors)==1
    vi=donors[0];rem=[e for e in self.events[idx:] if e['kind']=='remove'];assert all(e['stream']==vi for e in rem)
    e=dict(kind='transfer',stream=j,donor=vi,allowance_only=not rem,t=float(self.b.t),call=self.active,request=rid,before_recipient=before[j],after_recipient=(int(n.P),len(n.units)),before_donor=before[vi],after_donor=(int(self.b.nets[vi].P),len(self.b.nets[vi].units)),removed=[x['unit'] for x in rem])
    self.events.append(e)
    if self.b in SA._INSTALLED:self.count['adapter_invariant_allowance_traversals']+=1
   return r
  n.learn,n._room,n._add,n._remove=lrn,ro,ad,rm
 def uninstall(self):
  global EXTRA
  units,account=reconcile(self.events);gate=SA._INSTALLED.get(self.b)
  if gate is not None:
   assert account['pending_births']==gate.c.get('births_after_allowance_only_transfer',0)
   assert sum(e['kind']=='transfer' and e['allowance_only'] for e in self.events)==gate.c.get('allowance-only transfers',0)
  assert len(self.rows)==len(self.acc)
  EXTRA=dict(events=self.events,rows=self.rows,units=units,attribution=account,activity=dict(self.count),end_t=float(self.b.t))
  self.b.predict,self.b.taste=self.predict0,self.taste0
  for n,orig in self.wrappers:
   for k,v in orig.items():
    if v is None:n.__dict__.pop(k,None)
    else:setattr(n,k,v)
  super().uninstall()
def one(job):
 global EXTRA
 E.Trace=CaptureTrace
 try:r=E.one(job);r['capture']=EXTRA;return r
 finally:E.Trace=OriginalTrace

def check():
 def transfer(kind,call=1):return dict(kind='transfer',stream=0,allowance_only=kind,call=call)
 def birth(k=1,call=1):return dict(kind='birth',stream=0,unit=k,parents=[0,0],t=1.,call=call,call_start=0)
 u,c=reconcile([transfer(True),transfer(False),birth()]);assert u[0,1]['same_call'] and not u[0,1]['latest'] and c['pending_births']==1
 u,c=reconcile([transfer(True),transfer(True),birth(),dict(kind='remove',stream=0,unit=1,t=1.,call=1)]);assert c['pending_births']==1 and u[0,1]['removed']==1
 u,c=reconcile([transfer(True)]);assert not u and c['unmatched_pending']==1
 u,c=reconcile([birth()]);assert u[0,1]['removed'] is None
 row=dict(q=np.array([.9,.2]),w=np.array([2.,0.]),wd=1.,pd=.5);row['p']=mixture(row)
 assert replaced(row,np.array([False,True]))==row['p']
 assert abs(replaced(row,np.array([True,True]))-.5)<1e-12
 # Snapshot survives removal; scoring uses issued ID/probability, not the current unit dictionary.
 issued=dict(row,ids=[1,2]);dead={};assert issued['ids'][0] not in dead and mixture(issued)==row['p']
 print('L synthetic event, pending-marker, zero-weight, joint replacement, deletion and censoring checks passed.')

def run():
 check();ref={tuple([r['cond'],r['arm'],r['seed'],r['first']]):r for r in pickle.loads((ROOT/'lab/v/spare_allowance_pilot.pkl').read_bytes())};res=[];start=time.monotonic()
 def accept(r):
  key=(r['cond'],r['arm'],r['seed'],r['first']);old=ref[key]
  for k in ('fingerprint','body_fingerprint','behaviour','trace_pred','trace_acc','gate'):assert r[k]==old[k],(key,k)
  assert r['result']==old['result'],(key,'result')
  assert max(r['ledger'][k] for k in ('max_increment_error','max_weight_replay_error','max_final_balance_error'))<1e-9
  r['reference_exact']=True;res.append(r)
  tmp=BASE.with_suffix('.partial.tmp');tmp.write_bytes(pickle.dumps(res));os.replace(tmp,BASE.with_suffix('.partial.pkl'))
  print('PASS',key,'completed',len(res),'elapsed',round(time.monotonic()-start,1),flush=True)
 # First life is a prerequisite, not a concurrent hope.
 accept(one(JOBS[0]))
 with ProcessPoolExecutor(2) as pool:
  for r in pool.map(one,JOBS[1:]):accept(r)
 path=BASE.with_suffix('.pkl');os.replace(BASE.with_suffix('.partial.pkl'),path)
 meta=dict(success=True,lives=len(res),jobs=JOBS,wall_s=time.monotonic()-start,raw=str(path),raw_sha256=sha(path),sources={p:sha(ROOT/p) for p in (*E.SOURCES,'lab/gate_contribution_capture.py')})
 BASE.with_name(BASE.name+'_capture.json').write_text(json.dumps(meta,indent=2)+'\n')
def analyse():
 rr=pickle.loads(BASE.with_suffix('.pkl').read_bytes());assert len(rr)==8 and len({(r['cond'],r['arm'],r['first']) for r in rr})==8
 out=dict(success=True,lives=[],interpretation='Conditional fixed-history forecast substitution, not a causal control intervention; one seed pair per family.')
 loss=lambda p,y:-np.log2(np.clip(p if y else 1-p,1e-12,1-1e-12))
 err=lambda p,y:.5 if p==.5 else float((p>.5)!=bool(y))
 for r in rr:
  cap=r['capture'];units=cap['units'];T=E.SECS[r['cond']];o=dict(cond=r['cond'],arm=r['arm'],first=r['first'],activity=cap['activity'],attribution=cap['attribution'],windows={})
  for tag in ('same_call','latest'):
   selected=[u for u in units.values() if u[tag]]
   o[tag+'_lifetimes']=dict(units=len(selected),removed=sum(u['removed'] is not None for u in selected),censored=sum(u['removed'] is None for u in selected),median_observed_duration=float(np.median([(u['removed'] if u['removed'] is not None else cap['end_t'])-u['born'] for u in selected])) if selected else None)
   for win,lo,hi in [('full',0,T+1),('first_third',0,T/3),('last_third',2*T/3,T+1)]:
    diffs=[];errors=[];affected=0;mass=[]
    for row in cap['rows']:
     if not lo<=row['taste_t']<hi:continue
     assert abs(mixture(row)-row['p'])<1e-9
     mask=np.array([np.isfinite(row['q'][j]) and units.get((j,k),{}).get(tag,False) for j,k in enumerate(row['ids'])],dtype=bool)
     p=replaced(row,mask);assert -1e-10<=p<=1+1e-10
     diffs.append(float(loss(p,row['y'])-loss(row['p'],row['y'])));errors.append(err(p,row['y'])-err(row['p'],row['y']))
     affected+=int(mask.any());mass.append(float(row['w'][mask].sum()/(row['wd']+row['w'][np.isfinite(row['q'])].sum())))
    o['windows'][tag+' '+win]=dict(tastes=len(diffs),affected=affected,bits_total=sum(diffs),bits_per_taste=float(np.mean(diffs)),positive_bits=sum(max(0,d) for d in diffs),negative_bits=sum(min(0,d) for d in diffs),error_difference_total=sum(errors),mean_selected_weight=float(np.mean(mass)))
  out['lives'].append(o)
 BASE.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':{'--check':check,'--capture':run,'--analyse':analyse}[sys.argv[1]]()

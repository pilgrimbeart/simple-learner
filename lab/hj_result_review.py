"""D120 read-only review of H-J and survival records; no old output writes or new lives."""
from pathlib import Path
import json,pickle,hashlib,subprocess,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'lab'),str(ROOT)]
import alloc_compare as C
BASE=ROOT/'lab/v/hj_result_review'
def js(n):return json.loads((ROOT/'lab/v'/f'{n}.json').read_text())
def raw(n):return pickle.loads((ROOT/'lab/v'/f'{n}.pkl').read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 t0=time.monotonic();out={'success':False}
 try:
  out['hashes']={}
  for name in ('spare_allowance_pilot','spare_allowance_compare_new','spare_allowance_survival'):
   meta=js(name+'_capture');assert sha(meta['raw'])==meta['raw_sha256']
   out['hashes'][name]={p:sha(ROOT/p)==h for p,h in meta['provenance']['sha256'].items()}
  records={}
  for r in raw('spare_allowance_compare_new')+raw('spare_allowance_pilot'):
   if r['arm'] not in ('issued','issued+gate'):continue
   k=(r['cond'],r['arm'],r['seed'],r['first']);assert k not in records;records[k]=r
  assert len(records)==120
  out['primary']={};rng=np.random.default_rng(0);ii=rng.integers(0,10,(2000,10));idx=np.concatenate((2*ii,2*ii+1),axis=1)
  order=[(s,c) for s in range(142000,142010) for c in ('red','blue')]
  def eff(rows):
   a=np.array([[r[2],r[3]] for r in rows]);return a[idx,0].sum(1)/a[idx,1].sum(1)
  for cond in ('seq','time'):
   hist,path=C.history(cond)
   base=eff([hist['circuit',0,s,c] for s,c in order]);told=eff([hist['vtold',0,s,c] for s,c in order]);assert np.all(told>base)
   vals={a:eff([records[cond,a,s,c]['result'] for s,c in order]) for a in ('issued','issued+gate')}
   d=(vals['issued+gate']-vals['issued'])/(told-base)
   got=dict(median=float(np.median(d)),ci95=np.quantile(d,[.025,.975]).tolist());saved=js('spare_allowance_compare')['families'][cond]['gate_minus_baseline_gap_closed'];assert np.allclose(got['ci95'],saved['ci95'],atol=1e-12)
   out['primary'][cond]=got
  out['allfood_pairs_exact']=0
  for s,c in order:
   a,b=records['allfood','issued',s,c],records['allfood','issued+gate',s,c]
   assert all(a[k]==b[k] for k in ('behaviour','fingerprint','body_fingerprint'))
   out['allfood_pairs_exact']+=1
  out['ledger_pass']=all(r['ledger']['max_increment_error']<=1e-9 and r['ledger']['max_weight_replay_error']<=1e-9 and r['ledger']['max_final_balance_error']<=1e-9 for r in records.values())
  assert out['ledger_pass']
  surv=raw('spare_allowance_survival');assert len({(r['cond'],r['seed'],r['first']) for r in surv})==40
  out['survival']={}
  for cond,T in [('seq',300.),('time',3000.)]:
   rr=[r for r in surv if r['cond']==cond]
   for r in rr:
    ref=records[cond,'issued+gate',r['seed'],r['first']]
    assert all(r[k]==ref[k] for k in ('fingerprint','body_fingerprint','behaviour'))
   us=[u for r in rr for u in r['units'] if u['cause']=='allowance-only transfer']
   bits=np.array([u['bits'] for u in us]);saved=js('spare_allowance_survival')[cond]['allowance-only transfer']
   assert len(us)==saved['units'] and np.isclose(bits.sum()/20,saved['bits_saved_total_per_life'])
   lower=np.array([u['seen']-u['born'] for u in us]);upper=np.array([(u['gone'] if u['gone'] is not None else T)-u['born'] for u in us])
   out['survival'][cond]=dict(units=len(us),ever_spoke=sum(u['spoke']>0 for u in us),net_bits_per_life=float(bits.sum()/20),positive_unit_totals=float(bits[bits>0].sum()),negative_unit_totals=float(bits[bits<0].sum()),median_last_seen_duration=float(np.median(lower)),median_first_absent_duration=float(np.median(upper)),first_spoke_in_last_third=sum(u['first_spoke'] is not None and u['first_spoke']>=2*T/3 for u in us),pending_count_mismatch_lives=sum(sum(u['cause']=='allowance-only transfer' for u in r['units'])!=r['gate']['counters'].get('births_after_allowance_only_transfer',0) for r in rr))
  # Aggregate standalone savings do not bound mixture benefit: unequal weights across two forecasts.
  q=np.array([.9,.1]);pd=.5;w=np.array([.99,.001]);p=w*q+(1-w)*pd
  out['bound_counterexample']=dict(unweighted_net_bits=float(np.log2(q/pd).sum()),mixture_gain_bits=float(np.log2(p/pd).sum()),q=q.tolist(),unit_mixture_share=w.tolist(),default=pd,label=1)
  out['success']=True
 finally:
  out['provenance']=dict(revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),script_sha256=sha(__file__),inputs={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'lab/v'/f'{n}.pkl' for n in ('spare_allowance_pilot','spare_allowance_compare_new','spare_allowance_survival')]},command='timeout 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/hj_result_review.py')
  out['wall_s']=time.monotonic()-t0;BASE.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()

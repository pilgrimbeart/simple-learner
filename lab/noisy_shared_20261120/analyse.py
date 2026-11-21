"""D173 analysis, from records.jsonl (and refine.jsonl if present) only. Predeclared: paired bootstrap 95% over draws, 10,000
resamples; no-harm margin -0.005 in final-third in-stream pass share; useful = lower bounds > 0 for share and all-pass count."""
import json,math,sys
from collections import defaultdict
from pathlib import Path
import numpy as np
OUT=Path(__file__).resolve().parents[2]/'lab/v/noisy_shared_20261120'
ARMS=['shared_P2_g250','separate_P2_g250','shared_P1_g270','separate_P1_g270','shared_P1_ideal','fixed','informed']
PAIRS=[('shared_P2_g250','fixed'),('shared_P2_g250','separate_P2_g250'),('shared_P2_g250','shared_P1_ideal'),('shared_P1_g270','fixed'),
       ('shared_P1_g270','separate_P1_g270'),('separate_P2_g250','fixed'),('informed','fixed'),('shared_P2_g250','informed')]
def wilson(k,n,z=1.96):
    if n==0:return [None,None]
    p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d;return [c-h,c+h]
def boot(x,seed=173):
    x=np.asarray(x,float);rng=np.random.default_rng(seed);i=rng.integers(0,len(x),(10000,len(x)));m=x[i].mean(axis=1)
    return [float(np.percentile(m,2.5)),float(np.percentile(m,97.5))]
def main():
    R=[json.loads(l) for l in (OUT/'records.jsonl').read_text().splitlines()]
    by=defaultdict(dict)
    for r in R:by[r['cond'],r['seed']][r['arm']]=r
    conds=sorted({k[0] for k in by});res={}
    for cond in conds:
        seeds=sorted(s for c,s in by if c==cond);rows=[by[cond,s] for s in seeds if len(by[cond,s])==len(ARMS)]
        out=dict(draws=len(rows),arms={},pairs={})
        for a in ARMS:
            x=[r[a] for r in rows];share=[y['instream_final']['passed']/y['instream_final']['n'] for y in x if y['instream_final']['n']]
            learn=[y['instream_learning']['passed']/y['instream_learning']['n'] for y in x if y['instream_learning']['n']]
            ap=sum(y['isolated_all_pass'] for y in x);eps=np.array([y['eps_vs_informed_mV'] for y in x if y['eps_vs_informed_mV'] is not None])
            st=[y['settle_s'] for y in x if y['settle_s'] is not None and y['settle_s']>0]
            o=dict(instream_final_share_mean=float(np.mean(share)) if share else None,instream_final_share_ci=boot(share) if share else None,
                instream_learning_share_mean=float(np.mean(learn)) if learn else None,events_final_total=int(sum(y['instream_final']['n'] for y in x)),
                instream_final_failed_events=int(sum(y['instream_final']['n']-y['instream_final']['passed'] for y in x)),
                isolated_all_pass=ap,isolated_all_pass_wilson=wilson(ap,len(x)),feasible_draws=sum(y['feasible'] is not None for y in x),
                in_feasible_final=sum(y['in_feasible_final'] for y in x),
                eps_mV=dict(mean=float(eps.mean()),sd=float(eps.std()),rms=float(np.sqrt(np.mean(eps**2))),max_abs=float(np.abs(eps).max()),within10=int((np.abs(eps)<10).sum())) if len(eps) else None,
                settle_s=dict(n=len(st),median=float(np.median(st)),max=float(max(st))) if st else None,
                d_final_abs_max=float(max(abs(y['d_final']) for y in x)),d_final_values=[y['d_final'] for y in x] if cond in ('no_input','no_anchor','ordered_only') else None)
            if 'write_charge_C' in x[0]:o.update(write_charge_C_mean=float(np.mean([y['write_charge_C'] for y in x])),write_time_s_mean=float(np.mean([y['write_time_s'] for y in x])),
                quiet_write_charge_C_max=float(max(y['quiet_write_charge_C'] for y in x)),max_abs_m_V=float(max(y['max_abs_m'] for y in x)))
            out['arms'][a]=o
        for a,b in PAIRS:
            ds=[r[a]['instream_final']['passed']/r[a]['instream_final']['n']-r[b]['instream_final']['passed']/r[b]['instream_final']['n'] for r in rows if r[a]['instream_final']['n']]
            da=[int(r[a]['isolated_all_pass'])-int(r[b]['isolated_all_pass']) for r in rows]
            ci=boot(ds) if ds else None;cia=boot(da)
            out['pairs'][f'{a} - {b}']=dict(share_diff_mean=float(np.mean(ds)) if ds else None,share_diff_ci=ci,no_harm=bool(ci and ci[0]>-.005),share_superior=bool(ci and ci[0]>0),
                all_pass_diff=int(sum(da)),all_pass_diff_ci=cia,rescued=int(sum(x==1 for x in da)),harmed=int(sum(x==-1 for x in da)),
                share_rescued_draws=int(sum(x>0 for x in ds)),share_harmed_draws=int(sum(x<0 for x in ds)),
                useful=bool(ci and ci[0]>0 and cia[0]>0))
        res[cond]=out
    ref=OUT/'refine.jsonl'
    if ref.exists():
        F=[json.loads(l) for l in ref.read_text().splitlines()];coarse={(r['seed'],r['arm']):r for r in R if r['cond']=='main'}
        rows=[];seeds=sorted({r['seed'] for r in F})
        sh=lambda r:r['instream_final']['passed']/r['instream_final']['n']
        for s in seeds:
            lv={.0005:{a:coarse[s,a] for a in ARMS}}
            for r in F:
                if r['seed']==s:lv.setdefault(r['dt'],{})[r['arm']]=r
            dts=sorted(lv,reverse=True)
            for i in range(1,len(dts)):
                a,b=lv[dts[i-1]],lv[dts[i]]
                rows.append(dict(seed=s,dt=[dts[i-1],dts[i]],max_d_change=max(abs(a[x]['d_final']-b[x]['d_final']) for x in ARMS),
                    primary_diff_change=abs((sh(a['shared_P2_g250'])-sh(a['fixed']))-(sh(b['shared_P2_g250'])-sh(b['fixed']))),
                    classes_identical=all(a[x]['isolated_all_pass']==b[x]['isolated_all_pass'] for x in ARMS)))
        res['refinement']=dict(rows=rows,ok=bool(rows) and all(r['max_d_change']<.01 and r['primary_diff_change']<.05 for r in rows))
    (OUT/'analysis.json').write_text(json.dumps(res,indent=1)+'\n')
    for cond,o in res.items():
        if cond=='refinement':print('refinement ok',o['ok'],[(r['seed'],r['dt'][1],round(r['max_d_change'],4),round(r['primary_diff_change'],3)) for r in o['rows']]);continue
        print(f"\n== {cond} ({o['draws']} draws)")
        for a,x in o['arms'].items():
            e=x['eps_mV'];print(f"  {a:18s} instream final {x['instream_final_share_mean']} learn {x['instream_learning_share_mean']} failed ev {x['instream_final_failed_events']}/{x['events_final_total']} allpass {x['isolated_all_pass']} infeas {x['in_feasible_final']}/{x['feasible_draws']} eps rms {e['rms'] if e else None} settle {x['settle_s']} |d|max {x['d_final_abs_max']:.3f}")
        for k,x in o['pairs'].items():print(f"  {k:36s} share {x['share_diff_mean']} {x['share_diff_ci']} noharm {x['no_harm']} sup {x['share_superior']} | allpass {x['all_pass_diff']} {x['all_pass_diff_ci']} +{x['rescued']}/-{x['harmed']} useful {x['useful']}")
if __name__=='__main__':main()

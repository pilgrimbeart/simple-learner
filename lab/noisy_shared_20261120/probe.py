"""D173 probe (no result): does order_bench.build reproduce the confirm rows' arrays, and how long does a noisy 1000 s
engine life take at 0.5 ms? Compares the engine's node 6/7 with the analytic trajectory on one old draw."""
import json,math,sys,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
for p in [ROOT,ROOT/'lab']:sys.path.insert(0,str(p))
from order_bench import build
from dynamic_parts_bench import integrate
from order_long_calibration import make_long_stream
from order_baseline_stream import stream_trajectory
raw=[json.loads(l) for l in (ROOT/'lab/v/motifs/order_v2/confirm.jsonl').read_text().splitlines()]
dtmin=min(r['dt'] for r in raw);rows={r['seed']:r for r in raw if r['dt']==dtmin and not r['control']}
seed=2026112200;row=rows[seed];c=build(seed)
print('nodes eq',np.max(np.abs(c.node_arr-np.array(row['nodes']))),'el eq',np.max(np.abs(c.el_arr-np.array(row['elements']))),'link eq',np.array_equal(c.link,np.array(row['links'])))
r,events=make_long_stream(row,10.,2);dt=.0005;dur=1000.;steps=round(dur/dt)
z=np.random.default_rng([seed,173,0]).standard_normal((steps,8))
t0=time.monotonic();tr,power,charge,hits=integrate(c.V,c.Vx,c.armed,c.spikes,c.vmax,c.node_arr,c.el_arr,c.link,c.q,c.rest,c.cfg,z,dt,1,np.array(r['pulses']),np.zeros(5))
print('engine s',time.monotonic()-t0,'rail hits',hits,'power',power)
t,v=stream_trajectory(r,.15,dt,dur)
for i in (6,7):
    d=tr[:,1+i]-v[i];print('node',i,'rms diff mV',np.sqrt(np.mean(d[20000:]**2))*1e3,'max',np.max(np.abs(d[20000:]))*1e3,'rest sd mV',np.std(tr[20000:60000,1+i])*1e3)
print('V start',c.V)

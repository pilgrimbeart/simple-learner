"""D180 pre-freeze code tests, kept for provenance (PROTOCOL, Deviations): run while debugging, before the manifest froze.
Part 1 (t1): two 10 s closed-loop lives, development seeds 8 and 9. Part 2 (t2): benches A/B/C on component seed 0.
Not results; nothing was tuned from them."""
# ---- t1.py
import sys,time
sys.path.insert(0,'lab/catalogue_brain_20261120'); sys.path.insert(0,'.')
from brain import factory
from creature import Life
import numpy as np
for s in (8,9):
    t=time.time(); L=Life(s,'red',True,factory()); 
    for _ in range(1000): L.step()
    b=L.brain; ev=b.e.events()
    print(s,'sides',b.e.sides,'10s took',round(time.time()-t,2),'meals',L.meals[:5],'firings',len(L.firings),'motor ev',np.bincount(ev[1],minlength=2))
    r=np.array(b.rows); print('final E0 E1 P0 P1 B0 B1 X0 X1 M0 M1', np.round(r[-1],3)); print('X range',np.round(r[:,6].min(),3),np.round(r[:,6].max(),3),'clip',b.e.clip_o,'slew max',b.e.slew_o.max())
# ---- t2.py
import sys,time,json
sys.path.insert(0,'lab/catalogue_brain_20261120')
import bench
t=time.time(); a=bench.bench_A(0,0.15); print('A',time.time()-t); print(json.dumps(a,default=float)[:1500])
t=time.time(); r=[bench.bench_B_case(0,c) for c in bench.cases_B()]; print('B',time.time()-t)
for x in r: print(x['case'], [round(d,4) for d in x['dP']], x['clip_steps'], [round(v,3) for v in x['E_peak']])
t=time.time(); c=bench.bench_C_seed(0,'typ'); print('C',time.time()-t, len(c))
import numpy as np
print('side ex',np.mean([x['side']['excess_50ms'] for x in c]),'plastic',np.mean([x['plastic']['excess_50ms'] for x in c]))
print([ (x['side']['excess_50ms'],x['plastic']['excess_50ms'],x['phase']['side_readout_on']) for x in c][:16])

import sys, numpy as np
from discrete.circuits import hold_drive
from discrete.life import bench
def spikes(m,t):
    arm=True; out=[]
    for x,tt in zip(m,t):
        if arm and x>2: out.append(tt); arm=False
        elif x<1: arm=True
    return np.array(out)
kw={k:float(v) for k,v in (a.split("=") for a in sys.argv[1:])}
t,V,P=bench(hold_drive(**kw),1.5,["a","g","b","h","m0","m1"],pulses=[(0,1.0),(1,1.02)])
a=spikes(V["m0"],t); b=spikes(V["m1"],t)
pre=a[(a>0.3)&(a<1.0)]
print("scan Hz", round(1/np.diff(pre).mean(),1) if len(pre)>1 else None)
post=a[(a>1.0)&(a<1.1)]; print("m0 after pulse", np.round(post,3))
print("m1", np.round(b,3)); print("power nW", round(P*1e9,1))
i=np.searchsorted(t,[0.99,1.03,1.1,1.2,1.3]); print("h at", V["h"][i].round(2))

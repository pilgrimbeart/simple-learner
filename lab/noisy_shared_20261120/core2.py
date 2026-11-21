"""D173: the shared-readout candidate (D170 CONTRACT §2) on a noisy engine life, with separate steering weights w1, w2.

Differences from D170's core.py:
- node 7 = the engine's own noisy trajectory v7e plus an exact causal added term x:
  C7 dx/dt = -g7 x + d (I5 - I6) + gam (1 + d) I5  (exponential step, trapezoid branch currents)
- the tracker m gets its leak's thermal noise (2 k T g_m per second) and its branches' shot noise (q k_q I0 per second);
  the knob memory gets its write's shot noise (q |I_w| per second); Euler-Maruyama, noise from znoise (n x 2)
- arm CONST holds d = dconst (fixed knob at 0, or the informed reference)
"""
import math
import numpy as np
from numba import njit
SHARED,SEPARATE,CONST=0,1,2

@njit(cache=True)
def _run(v7e,I5b,I6b,gam,w1,w2,a7,g7,dt,arm,s,I0,kq,kw,gm,Vb,Cm,Cd,dead,e,eq,al,be,vtyp,rail,dconst,kT,q,znoise,t_last):
    n=len(I5b)
    v7=np.empty(n+1);d=np.empty(n+1);m=np.empty(n+1)
    x=0.;Vd=0.;mm=0.
    acc=np.zeros(8)   # write charge, write time, quiet write charge, max|Vd|, write charge last third, quiet steps, quiet sum err, quiet sumsq err
    k0=int(round(t_last/dt))
    sm_th=math.sqrt(2*kT*gm*dt)/Cm;sm_shot=math.sqrt(q*kq*I0*dt)/Cm
    for k in range(n):
        dk=min(max(Vd/vtyp,-1.0),1.0)
        if arm==CONST:dk=dconst
        d[k]=dk;m[k]=mm;u=v7e[k]+x;v7[k]=u
        if arm!=CONST:
            if arm==SHARED:
                T=math.tanh(s*(u-mm-e))
                Ik=kw*I0*((1+al/2)*w1[k]*(1+T)/2-(1-al/2)*w2[k]*(1-T)/2)
                Im=kq*I0*((1+be/2)*(1-w1[k])*(1+T)/2-(1-be/2)*(1-w2[k])*(1-T)/2)
                et=e
            else:
                Tw=math.tanh(s*(u-mm-e));Tq=math.tanh(s*(u-mm-eq))
                Ik=kw*I0*w1[k]*(Tw+al/2)
                Im=kq*I0*(1-w2[k])*(Tq+be/2)
                et=eq
            a=abs(Ik)-dead*kw*I0;Iw=0.0
            if a>0.0:Iw=a if Ik>0 else -a
            quiet=w1[k]<1e-3 and w2[k]<1e-3
            if quiet:
                err=(u-et)-mm;acc[5]+=1;acc[6]+=err;acc[7]+=err*err;acc[2]+=abs(Iw)*dt
            acc[0]+=abs(Iw)*dt
            if Iw!=0.0:acc[1]+=dt
            if k>=k0:acc[4]+=abs(Iw)*dt
            Vd=Vd-dt*Iw/Cd+math.sqrt(q*abs(Iw)*dt)/Cd*znoise[k,1]
            Vd=min(max(Vd,-rail),rail)
            mm=mm+dt*(Im-gm*(mm-Vb))/Cm+math.sqrt(sm_th*sm_th+sm_shot*sm_shot)*znoise[k,0]
            mm=min(max(mm,-rail),rail)
            acc[3]=max(acc[3],abs(Vd))
        x=a7*x+(1-a7)/g7*(dk*(I5b[k]-I6b[k])+gam[k]*(1+dk)*I5b[k])
    dk=min(max(Vd/vtyp,-1.0),1.0)
    if arm==CONST:dk=dconst
    d[n]=dk;m[n]=mm;v7[n]=v7e[n]+x
    return v7,d,m,acc

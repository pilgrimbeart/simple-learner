"""D170: the shared-readout candidate and its separate-path control as a causal integration (CONTRACT.md §2).
A labelled mathematical reference, not a catalogue part or a production simulator. Used by checks.py and replay.py.

run(...) integrates node 7 with the moving knob from the branch currents I5, I6 (trapezoid means per step, exact
exponential step as stream_trajectory), the tracker m and the knob memory V_d (explicit Euler, d held over each step).
The candidate sees only v7, m, V_d and the steering weights w1, w2 (from the coincidence voltage); nothing else.
"""
import math
import numpy as np
from numba import njit

SHARED,SEPARATE,FIXED=0,1,2

@njit(cache=True)
def currents(arm,u,mm,w1,w2,s,I0,kq,kw,e,eq,al,be):
    """(knob writer current before the dead band, tracker current), CONTRACT.md §2."""
    if arm==SHARED:
        T=math.tanh(s*(u-mm-e))
        Ik=kw*I0*((1+al/2)*w1*(1+T)/2-(1-al/2)*w2*(1-T)/2)
        Im=kq*I0*((1+be/2)*(1-w1)*(1+T)/2-(1-be/2)*(1-w2)*(1-T)/2)
    else:
        Tw=math.tanh(s*(u-mm-e));Tq=math.tanh(s*(u-mm-eq))
        Ik=kw*I0*w1*(Tw+al/2)
        Im=kq*I0*(1-w2)*(Tq+be/2)
    return Ik,Im

@njit(cache=True)
def _run(I5b,I6b,w1,w2,a7,g7,v70,dt,arm,s,I0,kq,kw,gm,Vb,Cm,Cd,dead,e,eq,al,be,vtyp,rail,m0,Vd0,t_last):
    n=len(I5b)
    v7=np.empty(n+1);d=np.empty(n+1);m=np.empty(n+1)
    v7[0]=v70;Vd=Vd0;mm=m0
    # accumulators: [quiet n, quiet sum err, quiet sumsq, quiet max|err|, same for last third (4..7),
    #  write charge, write time, quiet write charge, max|Vd|, time |Vd|>vtyp, max|m|, write charge last third]
    acc=np.zeros(13)
    k0=int(round(t_last/dt))
    for k in range(n):
        dk=min(max(Vd/vtyp,-1.0),1.0)
        if arm==FIXED:dk=0.0
        d[k]=dk;m[k]=mm
        u=v7[k]
        Ik,Im=currents(arm,u,mm,w1[k],w2[k],s,I0,kq,kw,e,eq,al,be)
        et=e if arm==SHARED else eq
        a=abs(Ik)-dead*kw*I0
        Iw=0.0
        if a>0.0:Iw=a if Ik>0 else -a
        if arm==FIXED:Iw=0.0
        # quiet-time tracking error of the tracker's own reading: (u - e_t) - m
        if w1[k]<1e-3 and w2[k]<1e-3:
            err=(u-et)-mm
            acc[0]+=1;acc[1]+=err;acc[2]+=err*err;acc[3]=max(acc[3],abs(err))
            if k>=k0:
                acc[4]+=1;acc[5]+=err;acc[6]+=err*err;acc[7]=max(acc[7],abs(err))
            acc[10]+=abs(Iw)*dt
        acc[8]+=abs(Iw)*dt
        if Iw!=0.0:acc[9]+=dt
        if k>=k0:acc[12]+=abs(Iw)*dt
        Vd=min(max(Vd-dt*Iw/Cd,-rail),rail)
        mm=min(max(mm+dt*(Im-gm*(mm-Vb))/Cm,-rail),rail)
        v7[k+1]=a7*v7[k]+(1-a7)/g7*((1+dk)*I5b[k]+(1-dk)*I6b[k])
        acc[11]=max(acc[11],abs(Vd))
    dk=min(max(Vd/vtyp,-1.0),1.0)
    if arm==FIXED:dk=0.0
    d[n]=dk;m[n]=mm
    return v7,d,m,acc

def run(I5b,I6b,w1,w2,a7,g7,v70,dt,arm,p,err,vtyp,rail,t_last,m0=0.,Vd0=0.):
    """p: a parameter point from bounds.json; err: dict(e,e_q,alpha,beta). Returns v7, d, m (n+1 samples) and accumulators."""
    v7,d,m,acc=_run(I5b,I6b,w1,w2,a7,g7,v70,dt,arm,p['slope_per_V'],p['I0_A'],p['k_q'],p['k_w'],p['g_m_S'],p['V_bias_V'],
        p['C_m_F'],p['C_d_F'],p['dead'],err['e'],err['e_q'],err['alpha'],err['beta'],vtyp,rail,m0,Vd0,t_last)
    names=['quiet_n','quiet_sum','quiet_sumsq','quiet_max','lt_quiet_n','lt_quiet_sum','lt_quiet_sumsq','lt_quiet_max',
           'write_charge_C','write_time_s','quiet_write_charge_C','max_abs_Vd','write_charge_last_third_C']
    a=dict(zip(names,acc.tolist()))
    # time beyond the knob's range is computed by the caller from d / Vd history; max|m| from m
    return v7,d,m,a

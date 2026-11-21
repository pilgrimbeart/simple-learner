"""D170 task 2: parameters and static bounds of the shared-readout candidate, from units.py, chip.py and D168's
saved arithmetic only (no trajectory, no outcome). Writes lab/v/shared_readout_20261120/bounds.json once.

Candidate (CONTRACT.md): one reading pair, I = I0*tanh(s*(u - m - e)), branches steered by the coincidence voltage
(share w to the knob writer, 1-w to the quiet tracker m), output mirrors k_w(1 +- alpha/2), k_q(1 +- beta/2):
  knob:    I_k = k_w*I0*(w*T + alpha*w/2 + delta/2)          delta = w1 - w2 (steering-pair mismatch)
  tracker: I_m = k_q*I0*((1-w)*T + beta*(1-w)/2 - delta/2)
  C_m dm/dt = -g_m (m - V_bias) + I_m;   C_d dV_d/dt = -I_k (dead band DEAD*k_w*I0);   d = clip(V_d/V_TYP, -1, 1)
Separate-path control: the same with T_q = tanh(s*(u - m - e_q)) on the tracker and no delta term (each pair's own tail
is gated, so a gate offset scales its weight but adds no current).
"""
import json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import chip
from units import (V_TYP,RAIL,R_MAX,C_MAX,TAU_MAX,I_MIN,MISMATCH,DT,TAU_LOOP,STEP_MOVE,CAP_DENSITY,UNIT_AREA,SUPPLY,PICO)
OUT=ROOT/'lab/v/shared_readout_20261120'
D168=ROOT/'lab/v/calibration_precision_20261120'

def main():
    arith=json.loads((D168/'b/arithmetic.json').read_text());noise=json.loads((D168/'e/noise_wall.json').read_text())
    u_rest_rms=arith['u_rest_mV']['rms']*1e-3;e_sd=MISMATCH*V_TYP          # 36.5 mV, 30 mV
    m_rms=math.hypot(u_rest_rms,e_sd)                                       # tracker's quiet level about V_bias = 0
    target=dict(conservative_screen_mV=10.,d163_95pct_mV=15.,note='engineering screen from D168 Task A; not a yield threshold')
    # leak budget: residual m/G at most 1 mV RMS  ->  loop gain G >= m_rms / 1 mV, rounded up to 50
    G=50.;assert G>=m_rms/1e-3
    g_m=1/R_MAX                                                              # slowest designed leak (an OTA at I_MIN)
    s_native=chip.NATIVE/2                                                   # a tanh pair's own slope, /V
    B_med=noise['per_anchor']['w|0.15']['B_per_anchor_Vs'][1]               # D168 Task E (raw-mode B ~ same scale)
    B_hi=noise['per_anchor']['w|0.15']['B_per_anchor_Vs'][2]
    kappa_target=.25/B_med                                                   # per-anchor contraction 0.25 at median B
    points={}
    for name,s,preamp in (('P1_native',s_native,False),('P2_preamp',4*s_native,True)):
        kqI0=G*g_m/s                                                         # tracker loop gain G = k_q I0 s / g_m
        k_q=1.;I0=kqI0/k_q;C_m=C_MAX
        tau_m=C_m/(g_m*(1+G))                                                # linear tracker time constant at w = 0
        k_w=.25;C_d=k_w*I0*s/(kappa_target*V_TYP)                           # knob memory capacitance for that rate
        C_d=round(C_d/PICO,1)*PICO;kappa=k_w*I0*s/(C_d*V_TYP)
        band_V={w:math.atanh(chip.DEAD/w)/s for w in (1.,.5,.2)}
        mirror_sd=math.sqrt(2)*MISMATCH/(2*s)                                # (beta - alpha)/(2 s), alpha,beta ~ N(0, MISMATCH^2)
        leak_rms=m_rms/G
        dead_sd=band_V[1.]/math.sqrt(3)                                      # bias bounded by the band; uniform within it
        shared_rms=math.sqrt(mirror_sd**2+leak_rms**2+dead_sd**2)
        separate_rms=math.sqrt(2*e_sd**2+mirror_sd**2+leak_rms**2+dead_sd**2)
        # gate mismatch, sensitivity assumption: each steering pair's opening shifted by g ~ N(0,(30 mV)^2) under the
        # engine's gate law w = clip((V6 - g)/V_TYP, 0, 1). While both are open, delta = (g2 - g1)/V_TYP, and the knob's
        # zero crossing moves by delta/(2 s) * (T_open / W), T_open/W >= 1 (W = int w, w <= 1).
        delta_sd=math.sqrt(2)*e_sd/V_TYP
        gate_anchor_sd_lower=delta_sd/(2*s)
        # at rest (V6 = 0): w_i = max(-g_i,0)/V_TYP. Knob writes k_w I0 delta/(2(1-wbar)); tunnels if > DEAD*k_w*I0.
        # P(rest drift) ~ P(at least one g_i < 0 and |delta| > 2 DEAD): Monte Carlo free closed form below (normal CDF).
        Phi=lambda z:.5*(1+math.erf(z/math.sqrt(2)))
        p_one_open=1-Phi(0)**2
        rest_drift_rate=k_w*I0*(.15)/2/C_d                                   # V/s at delta = 0.15 (one 30 mV offset)
        # tanh linear range: |s x| < 0.5 keeps tanh within 8% of linear
        lin_range=.5/s
        # step limits (AGENTS: not faster than the step)
        step_move_m=I0*k_q/C_m*DT;step_move_d=k_w*I0/C_d*DT
        # material and resting supply current, chip.py blocks (ranges where topology is not fixed)
        static_A=dict(read_tail_and_reference=2*I0,tracker_leak_ota=chip.WIDE*I_MIN,
                      steering_reference_bias=[0.,2*I0],level_shifters=[0.,2*2*chip.AUX],preamp=chip.WIDE*chip.AUX if preamp else 0.)
        lo=sum(v if not isinstance(v,list) else v[0] for v in static_A.values());hi=sum(v if not isinstance(v,list) else v[1] for v in static_A.values())
        transistors=dict(read_pair=2,tail_mirror_cascoded=[4,6],steering_quad=4,output_mirrors_two_outputs=[16,24],
                         steering_reference=[2,4],tracker_leak_ota=[7,9],level_shifters=[0,4],preamp=[7,11] if preamp else 0,
                         knob_memory_driver='existing memory block (SONOS cell + pulse driver); high-voltage pumps excluded as in chip.py')
        tr=[sum(v if isinstance(v,int) else v[i] for v in transistors.values() if not isinstance(v,str)) for i in (0,1)]
        caps=dict(tracker_C_m_F=C_m,knob_C_d_F=C_d)
        area_cap_um2=(C_m+C_d)/CAP_DENSITY*1e12;area_tr_um2=[t*UNIT_AREA*1e12 for t in tr]
        points[name]=dict(slope_per_V=s,preamplifier=preamp,I0_A=I0,k_q=k_q,k_w=k_w,g_m_S=g_m,V_bias_V=0.,C_m_F=C_m,C_d_F=C_d,
            loop_gain_G=G,tau_m_s=tau_m,leak_tau_s=C_m/g_m,kappa_per_V_s=kappa,per_anchor_contraction_median_B=kappa*B_med,per_anchor_contraction_90pct_B=kappa*B_hi,
            dead_band_mV={str(k):v*1e3 for k,v in band_V.items()},tanh_linear_range_mV=lin_range*1e3,
            static_budget_mV=dict(mirror_sd=mirror_sd*1e3,leak_rms=leak_rms*1e3,dead_band_sd=dead_sd*1e3,shared_rms=shared_rms*1e3,
                separate_rms=separate_rms*1e3,pass_shared_10mV=shared_rms<.010,pass_separate_10mV=separate_rms<.010),
            gate_mismatch_sensitivity=dict(assumption='each steering/gate pair opening shifted by N(0,(30 mV)^2), by analogy with a connection offset; NOT a measured device statistic',
                delta_sd=delta_sd,anchor_error_sd_lower_bound_mV=gate_anchor_sd_lower*1e3,p_at_least_one_gate_open_at_rest=p_one_open,
                rest_write_threshold_delta=2*chip.DEAD,knob_drift_V_per_s_at_delta_0p15=rest_drift_rate,time_to_V_TYP_s=V_TYP/rest_drift_rate,
                verdict='fails at rest in both arms on most draws unless a closed-at-rest gate margin (about 3 sigma = 90 mV) is designed in; the shared arm also carries the anchor-time delta term'),
            step_limits=dict(tracker_max_move_per_step_V=step_move_m,knob_max_move_per_step_V=step_move_d,STEP_MOVE_V=STEP_MOVE,tau_m_over_TAU_LOOP=tau_m/TAU_LOOP,ok=bool(step_move_m<STEP_MOVE and step_move_d<STEP_MOVE and tau_m>TAU_LOOP)),
            rails=dict(tracker_quiet_level_rms_V=m_rms,tracker_3sigma_V=3*m_rms,RAIL=RAIL,knob_range_V=[-V_TYP,V_TYP],knob_memory_rail_V=RAIL,ok=bool(3*m_rms<RAIL)),
            cost=dict(static_current_A=static_A,static_current_range_A=[lo,hi],static_power_range_W=[SUPPLY*lo,SUPPLY*hi],transistors=transistors,transistor_range=tr,
                capacitors=caps,area_um2=dict(capacitors=area_cap_um2,transistors=area_tr_um2),writes='knob write charge and time measured in the replay'))
    rules=dict(leak_bound='tau_m = C_m/(g_m (1+G)) <= TAU_MAX/G: a tracker accurate to m/G must be fast; with G = 50, tau_m <= %.1f ms' % (TAU_MAX/G*1e3),
        gain_factors='mirror gains k_w, k_q and the tail I0 scale both loops and drop out of each zero crossing at equilibrium; '
                     'they set speed (tau_m, kappa) and so change causal operation (anchor erosion, convergence), not the static equilibrium',
        what_cancels='the reading pair offset e and any stage before the split (level shifters, preamplifier) are shared and cancel',
        what_remains='output-stage terms after the split: output mirror imbalance (alpha, beta), steering-pair mismatch (delta), leak (m/G), dead band, tanh curvature under time-varying input',
        unavailable_operations=['difference reading of two node voltages by one pair (D154: a connection reads one node against a fixed offset)',
            'one pair steered to two destinations with complementary weights (a Gilbert-type steering quad)',
            'a complementary 1-w gate for the separate-path control (engine gates are clip(V/V_TYP,0,1) only)'],
        no_further_operation_needed='none beyond these three for the nominal contract; a closed-at-rest gate margin would be needed under the gate-mismatch sensitivity')
    res=dict(inputs=dict(u_rest_rms_V=u_rest_rms,e_sd_V=e_sd,m_rms_V=m_rms,B_per_anchor_median_Vs=B_med,B_per_anchor_90pct_Vs=B_hi,R_MAX=R_MAX,C_MAX=C_MAX,TAU_MAX=TAU_MAX,V_TYP=V_TYP),
        target=target,points=points,rules=rules,
        noise_bound=dict(note='silicon, analytic: order node 0.045 mV per anchor (D168 Task E); tracker kT/C at 50 pF and knob write shot noise below',
            tracker_kT_over_C_uV=math.sqrt(1.380649e-23*300/C_MAX)*1e6,
            knob_write_shot_uV_per_anchor={k:math.sqrt(1.602e-19*p['k_w']*p['I0_A']*.051)/p['C_d_F']*1e6 for k,p in points.items()},
            combined_bound_mV=.1,verdict='noise bound (~0.1 mV) far below the 10 mV screen'),
        explorers_per_credit_window=1)
    with (OUT/'bounds.json').open('x') as f:json.dump(res,f,indent=1)
    for k,p in points.items():print(k,json.dumps({x:p[x] for x in ('I0_A','tau_m_s','C_d_F','kappa_per_V_s','per_anchor_contraction_median_B','static_budget_mV','step_limits')},indent=0))
    print(json.dumps(res['noise_bound']))
if __name__=='__main__':main()

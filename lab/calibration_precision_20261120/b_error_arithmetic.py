"""D168 Task B (small arithmetic): numbers for the error map, each from units.py or the saved component draws.

- offset SD of one controlled connection, input-referred: MISMATCH*V_TYP (mixed_feedback.py, Circuit._arrays: el[1] += MISMATCH*d*volt);
  gain, slope, leak, capacitance each off by MISMATCH of themselves (same function).
- the resting voltages of the existing order circuit on the 40 reused draws, from the same feedforward equations the
  analytic trajectories use (order_baseline_stream.stream_trajectory), with both inputs at rest (A=B=0):
  in particular the order output's resting level u_rest, which the baseline subtraction must remove and which a
  difference stage's gain mismatch would leave behind, and the coincidence node's resting level (the gate input).
- combined readout-error SD for candidate observer chains, root-sum-square of independent offsets at unit stage
  gain, and the gain-mismatch term (relative SD of k1 - k2*kb with each k a product of gain, slope and 1/leak).
- the memory writer's dead band (chip.DEAD) expressed as an input-referred band for a stated writer slope.
No trajectories, no new draws.
"""
import json,math,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from units import MISMATCH,V_TYP,K_B,T,E,C_MAX
import chip
V=ROOT/'lab/v';OUT=V/'calibration_precision_20261120/b'
def rest_levels(row):
    n=np.array(row['nodes']);e=np.array(row['elements']);links=np.array(row['links']);v=np.zeros(8)
    for dest in range(2,8):
        I=0.
        for j in range(e.shape[1]):
            to,src,gate=links[:,j]
            if to!=dest:continue
            x=e[2,j]*(v[src]-e[1,j]);f=1/(1+math.exp(-x)) if e[4,j]>.5 else math.tanh(x)
            if gate>=0:f*=min(max(v[gate]/V_TYP,0.),1.)
            I+=e[0,j]*f
        v[dest]=I/n[1,dest]
    return v
def main():
    OUT.mkdir(parents=True,exist_ok=False)
    raw=[json.loads(l) for l in (V/'motifs/order_v2/confirm.jsonl').read_text().splitlines()]
    dtmin=min(r['dt'] for r in raw);rows={r['seed']:r for r in raw if r['dt']==dtmin and not r['control']}
    sig=MISMATCH*V_TYP;rel_k=math.sqrt(3)*MISMATCH;rel_diff=math.sqrt(3)*rel_k
    per=[];
    for s,r in sorted(rows.items()):
        v=rest_levels(r);n=np.array(r['nodes'])
        per.append(dict(seed=s,rest_V=v.tolist(),u_rest_V=float(v[7]),coincidence_rest_V=float(v[6]),order_node_C_F=float(n[2,7]),order_node_leak_S=float(n[1,7])))
    u=np.array([p['u_rest_V'] for p in per])
    chains={
     'raw: product connection reads u directly (1 offset)':dict(offsets=1,sigma_mV=1000*sig),
     'integral-feedback baseline + product (offsets of the baseline integrator\'s reading of r and of the product; the u and baseline readings into r sit inside the loop)':dict(offsets=2,sigma_mV=1000*sig*math.sqrt(2)),
     'feed-forward low-pass baseline + two-input difference node + product (follower, two difference inputs, product)':dict(offsets=4,sigma_mV=1000*sig*2,
        gain_mismatch_term_mV_rms=1000*rel_diff*float(np.sqrt(np.mean(u**2)))),
     'two separately gated readings for a quiet self-reference (Task D with catalogue parts): e_w - e_q':dict(offsets=2,sigma_mV=1000*sig*math.sqrt(2)),
     'one reading pair steered to two outputs (not in the catalogue): residual e*(k_w-k_q) from output-mirror mismatch, per volt of shared error':dict(relative=math.sqrt(2)*MISMATCH)}
    dead=dict(DEAD=chip.DEAD,band_mV_for_writer_slope_per_V={str(s):1000*math.atanh(chip.DEAD)/s for s in [1/V_TYP,10.,chip.NATIVE/2]},
        note='a write tunnels only when |I| > DEAD*|gain|; with I = gain*tanh(slope*x)*w the band is |x| < atanh(DEAD/w)/slope, widening as w falls')
    noise=dict(kT_over_C_uV_at_25pF=1e6*math.sqrt(K_B*T/(C_MAX/2)),note='voltage noise of a 25 pF node from its leak, silicon (mixed_feedback SUBSTRATES); see Task E')
    out=dict(offset_sigma_mV=1000*sig,relative_sigma_gain_slope_leak=MISMATCH,relative_sigma_stage_gain_k=rel_k,relative_sigma_k1_minus_k2kb=rel_diff,
        u_rest_mV=dict(min=1000*float(u.min()),median=1000*float(np.median(u)),max=1000*float(u.max()),rms=1000*float(np.sqrt(np.mean(u**2)))),
        coincidence_rest_V_max_abs=max(abs(p['coincidence_rest_V']) for p in per),chains=chains,dead_band=dead,noise=noise,per_draw=per)
    (OUT/'arithmetic.json').write_text(json.dumps(out,indent=1)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='per_draw'},indent=1))
if __name__=='__main__':main()

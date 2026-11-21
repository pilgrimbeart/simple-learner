"""D147: inspect the established filter representation without changing its noise engine."""
import json,math,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,digest,provenance
from mixed_feedback import Circuit
from minimal.spice import FILTER_C
from units import K_B,T,RAIL
OUT=ROOT/'lab/v/filter_state_audit'
PATHS=['dynamic_parts/protocol_v2.json','motifs/change_v2/protocol.json','motifs/order_v2/protocol.json',
    'retained_write/protocol_v1.json','quiet_write/protocol.json','oneshot_v1/protocol.json','phase_v1/protocol.json','signed_control/protocol.json']
def scan(value,path='root'):
    found=[]
    if isinstance(value,dict):
        if 'tau' in value:found.append(dict(path=path,tau_s=value['tau']))
        for k,v in value.items():found.extend(scan(v,path+'.'+k))
    elif isinstance(value,list):
        for i,v in enumerate(value):found.extend(scan(v,path+f'[{i}]'))
    return found

def main():
    OUT.mkdir(exist_ok=True);protocol=dict(seed=147,source='Idle retained node at .3V; existing exact-idle-memory assumption',
        destination='25pF,1Gohm leak',connection='100pA,offset0,slope1/V_TYP,tau.05s',duration_s=.1,sample_s=.005,
        expectation='Vx stays exactly at its constant source despite active native destination noise. No external clamp or zero-noise draws.',files=PATHS,budget_s=30)
    with (OUT/'protocol.json').open('x') as f:json.dump(protocol,f,indent=2)
    c=Circuit(seed=147,streams=True,substrate='silicon');source=c.node('held source',C=25e-12,R=None,memory=True,start=.3,lo=-RAIL,hi=RAIL);dest=c.node('noisy destination',C=25e-12,R=1e9,start=0.,lo=-RAIL,hi=RAIL)
    c.element(dest,source,100e-12,0.,tau=.05,slope=1/c.volt);c._ready();values=[]
    for i in range(20):
        c.run(.005);values.append(dict(time_s=(i+1)*.005,source_V=float(c.V[source]),filter_V=float(c.Vx[0]),destination_V=float(c.V[dest])))
    assert all(r['filter_V']==.3 and r['source_V']==.3 for r in values)
    # Destination transient is not a noise estimate; inspect noise allocation explicitly instead.
    assert c.rest[dest]>0 and c.q>0
    scans={}
    for rel in PATHS:
        p=ROOT/'lab/v'/rel;f=scan(json.loads(p.read_text()));assert f;scans[rel]=dict(connections=len(f),positive_tau=[x for x in f if x['tau_s']>0])
    prov=provenance();prov['files'].update({str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__).resolve(),ROOT/'mixed_feedback.py',ROOT/'minimal/spice.py',ROOT/'chip.py',ROOT/'test_compiled.py']+[ROOT/'lab/v'/p for p in PATHS]});prov['protocol_sha256']=digest(OUT/'protocol.json');(OUT/'provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
    result=dict(filter_exactly_constant=True,native_noise_active=dict(q_C=float(c.q),destination_rest_variance_rate=float(c.rest[dest])),
        physical_filter_C_F=FILTER_C,physical_filter_thermal_sigma_V=math.sqrt(K_B*T/FILTER_C),
        witness_protocols=scans,source_reading='Vx update has no independent stochastic increment; rest arrays and z have one entry per explicit node. Physical SPICE filter uses follower,R=tau/FILTER_C,C=FILTER_C. check_noise exercises explicit nodes/memories, not this hidden capacitor.',
        limitation='Physical kT/C is a stiff-source passive RC reference, not a complete follower-noise model. This audit does not quantify historical behavioural bias.')
    (OUT/'trace.json').write_text(json.dumps(values,indent=2)+'\n');(OUT/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()

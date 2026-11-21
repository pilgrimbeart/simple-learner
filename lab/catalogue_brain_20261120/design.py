"""D180 proposed catalogue-native graph; no simulation or selection at import.
Authoritative parameters/topology. Worker implements adapters/experiments per work order.
All choices are SI; equations in DESIGN.md. Design is unvalidated dynamically.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from units import C_MAX, C_TYP, V_TYP, RAIL, R_MAX, TAU_LEAK, TAU_LOOP, I_MIN, SLEW


def graph(sides=(0, 1)):
    assert len(sides) == 2 and all(s in (0, 1) for s in sides)
    nodes, edges = [], []
    def node(name, cap, tau, bias=0., initial='random'):
        nodes.append(dict(name=name, C=cap, R=None if tau is None else tau/cap,
                          bias=bias, memory=tau is None, lo=-RAIL, hi=RAIL, initial=initial))
    def edge(name, to, source, gain, offset=0., slope=None, gate=None, sigmoid=False):
        edges.append(dict(name=name, to=to, source=source, gain=gain, offset=offset,
                          slope=1/V_TYP if slope is None else slope, gate=gate, sigmoid=sigmoid, tau=0.))
    ci, c, cm = 2*C_TYP, C_MAX/2, 4*C_TYP
    for k in (0, 1): node(f'S{k}', ci, .010)
    node('T', ci, .010)
    for k in (0, 1): node(f'E{k}', c, .100)
    for k in (0, 1): node(f'P{k}', ci, None, initial='neutral')
    for k in (0, 1):
        node(f'X{k}', c, .020)
        node(f'Y{k}', c, .200)
        node(f'B{k}', c, None)
    for k in (0, 1): node(f'M{k}', cm, .005, -1.5*V_TYP*cm/.005, initial='motor_rest')
    # D162 oscillator topology, each with its own retained bias adjustment.
    for k in (0, 1):
        edge(f'explore_self_{k}',f'X{k}',f'X{k}',3*c*(V_TYP/2)/.020,slope=2/V_TYP)
        edge(f'explore_recover_{k}',f'X{k}',f'Y{k}',-5*c*(V_TYP/2)/.020,slope=2/V_TYP)
        edge(f'explore_follow_{k}',f'Y{k}',f'X{k}',c*V_TYP/.200)
        edge(f'explore_bias_{k}',f'X{k}',f'B{k}',-5*c*(V_TYP/2)/.020)
        edge(f'explore_adjust_{k}',f'B{k}',f'X{k}',c*V_TYP/5.)
        edge(f'explore_motor_{k}',f'M{k}',f'X{k}',3*V_TYP*cm/.005,
             offset=V_TYP/2,slope=18/V_TYP,sigmoid=True)
    for k, side in enumerate(sides):
        edge(f'side_{k}',f'M{side}',f'S{k}',3*V_TYP*cm/.005,
             offset=V_TYP/2,slope=18/V_TYP,sigmoid=True)
        edge(f'plastic_{k}',f'M{1-side}',f'S{k}',3*V_TYP*cm/.005,
             offset=V_TYP/2,slope=18/V_TYP,sigmoid=True,gate=f'P{k}')
        edge(f'eligibility_{k}',f'E{k}',f'S{k}',V_TYP*c/.100,
             offset=V_TYP/2,slope=18/V_TYP,sigmoid=True)
        for sign, label in [(1,'positive'),(-1,'negative')]:
            edge(f'write_{label}_{k}',f'P{k}','T',sign*ci*V_TYP/.005,
                 offset=sign*V_TYP/2,slope=sign*18/V_TYP,sigmoid=True,gate=f'E{k}')
    return dict(version=1, nodes=nodes, edges=edges, sides=list(sides),
                sensors=['S0','S1'], taste='T', motors=['M0','M1'], volt=V_TYP,
                substrate='silicon', on_chip=True)


def validate(g):
    names={n['name']:n for n in g['nodes']}
    assert len(names)==len(g['nodes'])
    assert len({e['name'] for e in g['edges']})==len(g['edges'])
    for n in g['nodes']:
        assert 0<n['C']<=C_MAX and n['lo']==-RAIL and n['hi']==RAIL
        assert n['R'] is None if n['memory'] else 0<n['R']<=R_MAX and n['R']*n['C']>=TAU_LEAK
        assert n['bias']==0 or abs(n['bias'])>=I_MIN
    for e in g['edges']:
        assert e['to'] in names and e['source'] in names and (e['gate'] is None or e['gate'] in names)
        assert e['tau']==0 and abs(e['gain'])>=I_MIN
        assert abs(e['gain'])/names[e['to']]['C']<=SLEW
        if e['to']==e['source']:
            assert abs(e['gain']*e['slope'])/names[e['to']]['C']<=1/TAU_LOOP
    return dict(nodes=len(names),retained=sum(n['memory'] for n in g['nodes']),
                connections=len(g['edges']),implicit_filters=0,
                limitation='Static nominal limits only; mismatch, aggregate slew, dynamics, cost and behaviour require execution.')

if __name__=='__main__':
    import json
    print(json.dumps(dict(check=validate(graph()),graph=graph()),indent=2))

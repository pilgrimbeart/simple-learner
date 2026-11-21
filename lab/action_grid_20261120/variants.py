"""Prepared D182 action grid: exact nominal transformations, no simulations.
The accompanying work order owns execution and analysis. Original graph is read-only.
"""
import copy
import importlib.util
import itertools
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('action_grid_base_design', ROOT/'lab/catalogue_brain_20261120/design.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

def configurations():
    return [dict(id=f'g{g}_t{t}_q{q}_f{f}', sensory_gain=g,
                 motor_tau_s=t, exploration_threshold_V=q, oscillator_speed=f)
            for g,t,q,f in itertools.product((0.5,1.0,2.0),(.0025,.005,.010),(.15,.225,.30),(.75,1.,1.5))]

BASELINE = 'g1.0_t0.005_q0.15_f1.0'

def graph(config, sides=(0,1)):
    g = copy.deepcopy(base.graph(sides))
    a = .005/config['motor_tau_s']
    speed = config['oscillator_speed']
    for n in g['nodes']:
        if n['name'] in ('M0','M1'):
            n['R'] /= a
            n['bias'] *= a
        if n['name'] in ('X0','Y0','B0','X1','Y1','B1'):
            if n['R'] is not None:
                n['R'] /= speed
            n['bias'] *= speed
    for e in g['edges']:
        if e['to'] in ('M0','M1'):
            e['gain'] *= a
        if e['name'] in ('side_0','side_1','plastic_0','plastic_1'):
            e['gain'] *= config['sensory_gain']
        if e['name'] in ('explore_motor_0','explore_motor_1'):
            e['offset'] = config['exploration_threshold_V']
        if e['to'] in ('X0','Y0','B0','X1','Y1','B1'):
            e['gain'] *= speed
    return g

if __name__ == '__main__':
    import json
    configs = configurations()
    assert len(configs)==len({c['id'] for c in configs})==81
    valid, invalid = [], []
    for c in configs:
        try:
            for sides in itertools.product((0,1),repeat=2):
                base.validate(graph(c,sides))
            valid.append(c['id'])
        except AssertionError:
            invalid.append(c['id'])
    c = next(c for c in configs if c['id']==BASELINE)
    assert all(graph(c,s)==base.graph(s) for s in itertools.product((0,1),repeat=2))
    print(json.dumps(dict(configurations=configs,baseline=BASELINE,nominal_valid=valid,
                         nominal_invalid=invalid,bench_jobs_per_valid=384,
                         development_lives_per_valid=384,
                         confirmation_lives_max=18432,
                         note='Static graph checks only; no realised physical or behavioural validation.'),indent=2))

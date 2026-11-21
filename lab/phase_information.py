"""D138: descriptive information audit of existing phase curves, no simulations."""
import hashlib
import json
import math
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'lab/v/phase_information'
SRC = ROOT / 'lab/v/phase_v1/confirm.jsonl'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(exist_ok=True)
    protocol = dict(source=str(SRC), observation='mean output over 6..12 s',
                    analysis='Finest stored step; all 40 draws in each frequency band. '
                    'Overlap describes unknown-draw ambiguity, not identical full waveforms. '
                    'Piecewise-linear crossing is an interpolated counterexample, not a new measurement.',
                    budget_minutes=30, new_simulations=0)
    (OUT / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    raw = [json.loads(s) for s in SRC.read_text().splitlines()]
    dt = min(r['dt'] for r in raw)
    rows = [r for r in raw if r['dt'] == dt and not r['control']]
    assert len(rows) == 480
    assert len({(r['seed'], r['case']['id']) for r in rows}) == 480
    bands = {}
    crossings = []
    for band in [2., 5.]:
        curves = {}
        for r in rows:
            if r['case']['frequency'] == band:
                curves.setdefault(r['seed'], []).append(r)
        assert len(curves) == 40
        curves = {s: sorted(rr, key=lambda r:r['case']['phase'])[:5] for s,rr in curves.items()}
        for rr in curves.values():
            assert len(rr) == 5 and rr[2]['case']['phase'] == 0
            assert all(a['mean_V'] > b['mean_V'] for a,b in zip(rr,rr[1:]))
        zeros = [rr[2]['mean_V'] for rr in curves.values()]
        # Desired sign follows D133: positive lead of B gives negative output.
        wrong = sum(r['mean_V'] * r['case']['phase'] >= 0
                    for rr in curves.values() for r in rr if r['case']['phase'] != 0)
        for seed, rr in curves.items():
            for other, oo in curves.items():
                if other == seed:
                    continue
                target = oo[2]['mean_V']
                for a,b in zip(rr, rr[1:]):
                    if a['mean_V'] >= target >= b['mean_V']:
                        f = (target-a['mean_V'])/(b['mean_V']-a['mean_V'])
                        phase = a['case']['phase'] + f*(b['case']['phase']-a['case']['phase'])
                        crossings.append(dict(band_Hz=band, zero_seed=other, nonzero_seed=seed,
                            output_V=target, interpolated_phase_rad=phase,
                            phase_bracket_rad=[a['case']['phase'],b['case']['phase']],
                            output_bracket_V=[a['mean_V'],b['mean_V']],
                            actual_frequencies_Hz=[oo[2]['frequency_Hz'],a['frequency_Hz']]))
                        break
        bands[str(band)] = dict(zero_output_range_V=[min(zeros),max(zeros)],
            wrong_raw_sign=wrong, nonzero_cases=160,
            cross_draw_zero_crossings=sum(r['band_Hz']==band for r in crossings),
            ordered_draw_pairs=40*39)
    result = dict(bands=bands, crossings=crossings,
        limitation='Different draws also differ in actual frequency and other parameters. '
        'This establishes ambiguity for the scalar mean under unknown draw, not structural '
        'nonidentifiability of the complete noisy waveform or both observed inputs.')
    (OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    (OUT/'provenance.json').write_text(json.dumps(dict(
        revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        files={str(p.relative_to(ROOT)):digest(p) for p in [SRC,Path(__file__).resolve(),OUT/'protocol.json']},
        source_provenance=str(ROOT/'lab/v/phase_v1/confirm_provenance.json'),
        worktree='Uncommitted D138 script and notebook; input is the preserved D133 output.'),indent=2)+'\n')
    print(json.dumps(bands,indent=2))
    print('Largest interpolated ambiguity:',json.dumps(max(crossings,key=lambda r:abs(r['interpolated_phase_rad']))))

if __name__ == '__main__':
    main()

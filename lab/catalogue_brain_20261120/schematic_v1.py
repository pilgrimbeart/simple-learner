"""D180 labelled schematic of the exact v1 graph (design.py), every node and every connection, as SVG (no new
dependency). Line style carries sign and kind, colour only doubles it (Okabe-Ito; the user is colour-blind):
solid + arrow = positive current, dashed + bar = negative current, dotted = gate (multiplies a connection),
double outline = retained (memory) node. Drawn for wiring sides=(0, 1); the birth coin tosses may differ (stated).
usage: schematic_v1.py [OUT.svg]   default lab/v/catalogue_brain_20261120/schematic_v1.svg
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))
from design import graph                                   # noqa: E402
from units import si                                        # noqa: E402

POS = dict(S0=(90, 120), S1=(90, 520), T=(90, 320), E0=(300, 60), E1=(300, 580), P0=(470, 200), P1=(470, 440),
           X0=(300, 760), Y0=(150, 860), B0=(450, 860), X1=(820, 760), Y1=(670, 860), B1=(970, 860),
           M0=(820, 200), M1=(820, 440))
POS = {k: (x, y) for k, (x, y) in POS.items()}
POS["X1"], POS["Y1"], POS["B1"] = (720, 760), (600, 880), (860, 880)
POS["X0"], POS["Y0"], POS["B0"] = (330, 760), (190, 880), (470, 880)
BLUE, ORANGE, GREEN, PURPLE, GREY = "#0072B2", "#E69F00", "#009E73", "#CC79A7", "#555555"


def main(out=None):
    out = Path(out) if out else HERE.parents[1] / "lab/v/catalogue_brain_20261120/schematic_v1.svg"
    g = graph((0, 1))
    nodes = {n["name"]: n for n in g["nodes"]}
    W, H = 1100, 1000
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="sans-serif" font-size="11">',
         '<rect width="100%" height="100%" fill="white"/>',
         '<defs><marker id="arr" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">'
         '<path d="M0,0 L8,4 L0,8 z" fill="#0072B2"/></marker>'
         '<marker id="bar" markerWidth="4" markerHeight="10" refX="2" refY="5" orient="auto">'
         '<rect width="3" height="10" fill="#E69F00"/></marker></defs>',
         f'<text x="20" y="24" font-size="15">D180 catalogue-native brain, design v1: {len(g["nodes"])} nodes '
         f'({sum(n["memory"] for n in g["nodes"])} retained), {len(g["edges"])} connections, no implicit filters</text>',
         '<text x="20" y="42">Drawn for wiring sides=(0,1): S0 fixed to M0, gated to M1; S1 fixed to M1, gated to M0. '
         'Each life draws both sides by coin toss (both may pick the same motor).</text>']
    off = {}
    for e in g["edges"]:
        a, b = POS[e["source"]], POS[e["to"]]
        key = tuple(sorted((e["source"], e["to"])))
        k = off.get(key, 0)
        off[key] = k + 1
        neg = e["gain"] < 0
        col = ORANGE if neg else BLUE
        dash = ' stroke-dasharray="7,4"' if neg else ""
        mk = "bar" if neg else "arr"
        if e["source"] == e["to"]:
            x, y = a
            s.append(f'<path d="M{x - 10},{y - 22} C{x - 40},{y - 75} {x + 40},{y - 75} {x + 10},{y - 22}" fill="none" '
                     f'stroke="{col}" stroke-width="1.5"{dash} marker-end="url(#{mk})"/>')
            lx, ly = x, y - 70
        else:
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = max((dx * dx + dy * dy) ** .5, 1)
            sgn = 1 if e["source"] < e["to"] else -1
            nx, ny = -dy / L * 12 * k * sgn, dx / L * 12 * k * sgn
            x1, y1 = a[0] + dx / L * 26 + nx, a[1] + dy / L * 26 + ny
            x2, y2 = b[0] - dx / L * 28 + nx, b[1] - dy / L * 28 + ny
            s.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{col}" stroke-width="1.5"'
                     f'{dash} marker-end="url(#{mk})"/>')
            lx, ly = (x1 + x2) / 2, (y1 + y2) / 2
            if e["gate"]:
                gx, gy = POS[e["gate"]]
                s.append(f'<line x1="{gx:.0f}" y1="{gy:.0f}" x2="{lx:.0f}" y2="{ly:.0f}" stroke="{GREEN}" '
                         f'stroke-width="1.3" stroke-dasharray="2,3"/>')
                s.append(f'<circle cx="{lx:.0f}" cy="{ly:.0f}" r="4" fill="white" stroke="{GREEN}"/>')
        kind = "sigmoid" if e["sigmoid"] else "tanh"
        lab = (f'{e["name"]}: {"-" if neg else "+"}{si(abs(e["gain"]), "A")} {kind}, '
               f'offset {e["offset"]:+.2f} V, slope {e["slope"]:+.0f}/V' + (f', gate {e["gate"]}' if e["gate"] else ""))
        s.append(f'<text x="{lx + 6:.0f}" y="{ly - 4 + 11 * (k % 2):.0f}" font-size="9" fill="#222">{lab}</text>')
    for nm, (x, y) in POS.items():
        n = nodes[nm]
        mem = n["memory"]
        s.append(f'<circle cx="{x}" cy="{y}" r="22" fill="#f4f4f4" stroke="#000" stroke-width="1.5"/>')
        if mem:
            s.append(f'<circle cx="{x}" cy="{y}" r="17" fill="none" stroke="#000" stroke-width="1.2"/>')
        s.append(f'<text x="{x}" y="{y + 4}" text-anchor="middle" font-size="13" font-weight="bold">{nm}</text>')
        desc = f'{si(n["C"], "F")}, ' + ("retained (no leak)" if mem else f'tau {si(n["R"] * n["C"], "s")}')
        if n["bias"]:
            desc += f', bias {si(n["bias"], "A")}'
        s.append(f'<text x="{x}" y="{y + 36}" text-anchor="middle" font-size="9" fill="{GREY}">{desc}</text>')
    s.append('<text x="20" y="975">Key: solid line + arrow = positive current; dashed line + bar = negative current; '
             'dotted line to a small circle = gate (current x clip(V_gate/V_TYP,0,1)); double ring = retained memory '
             'node; loop = self-connection. S0, S1, T receive the body pulses; M0, M1 events (rising through 0 V, '
             're-armed below -V_TYP) drive the thrusters.</text>')
    s.append("</svg>")
    out.write_text("\n".join(s) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)

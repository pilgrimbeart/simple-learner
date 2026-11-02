"""Draw hold_drive (14 parts) as SVG: the full schematic, each block cropped from it, and bench waveforms."""
import json, sys
import numpy as np

S = "/home/pilgrim/git/simple-learner/lab"
BLK = {"eye": "var(--c-eye)", "osc": "var(--c-osc)", "ma": "var(--c-ma)", "mb": "var(--c-mb)", "if": "var(--c-if)"}
out = []


def L(*pts, c="var(--ink)", w=2, dash=None):
    d = " ".join(f"{x},{y}" for x, y in pts)
    out.append(f'<polyline points="{d}" fill="none" stroke="{c}" stroke-width="{w}"'
               + (f' stroke-dasharray="{dash}"' if dash else "") + ' stroke-linejoin="round"/>')


def dot(x, y):
    out.append(f'<circle cx="{x}" cy="{y}" r="4" fill="var(--ink)"/>')


def T(x, y, s, cls="lbl", anchor="start"):
    out.append(f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{s}</text>')


def label(x, y, ref, val, c, anchor="start"):
    T(x, y, ref, "ref", anchor)
    out.append(f'<text x="{x}" y="{y + 16}" class="val" text-anchor="{anchor}" fill="{c}">{val}</text>')


def vdd(x, y):           # local supply: a bar with +3 V above; lead from (x,y) down
    L((x - 12, y), (x + 12, y), w=2.5)
    T(x, y - 7, "+3 V", "sup", "middle")


def gnd(x, y):           # local ground below (x, y)
    L((x, y), (x, y + 8))
    for k, h in enumerate((14, 9, 4)):
        L((x - h, y + 8 + 5 * k), (x + h, y + 8 + 5 * k))


def res(x, y0, y1, c):   # vertical resistor from y0 to y1, zigzag body of 44 px in the middle
    m = (y0 + y1) / 2
    a, b = m - 22, m + 22
    L((x, y0), (x, a))
    zz = [(x, a)] + [(x + (8 if k % 2 == 0 else -8), a + 44 * (k + 0.5) / 6) for k in range(6)] + [(x, b)]
    L(*zz, c=c, w=2.5)
    L((x, b), (x, y1))


def cap(x, y0, y1, c):
    m = (y0 + y1) / 2
    L((x, y0), (x, m - 5))
    L((x, m + 5), (x, y1))
    L((x - 15, m - 5), (x + 15, m - 5), c=c, w=3)
    L((x - 15, m + 5), (x + 15, m + 5), c=c, w=3)


def arrow(x0, y0, x1, y1, c):  # filled arrowhead at (x1, y1) pointing from (x0, y0)
    v = np.array([x1 - x0, y1 - y0], float); v /= np.hypot(*v); n = np.array([-v[1], v[0]])
    p = np.array([x1, y1]); a = p - 9 * v + 4.5 * n; b = p - 9 * v - 4.5 * n
    out.append(f'<polygon points="{p[0]},{p[1]} {a[0]},{a[1]} {b[0]},{b[1]}" fill="{c}"/>')


def bjt(bx, cy, kind, c, mirror=False, top="c"):
    """Base terminal at (bx, cy); bar 20 px in; the top/bottom leads end 40 px in, 25 px up/down. Returns
    (top end, bottom end). top: which terminal is on top ('c' or 'e')."""
    s = -1 if mirror else 1
    bar = bx + 20 * s
    end = bx + 40 * s
    out.append(f'<circle cx="{bx + 26 * s}" cy="{cy}" r="21" fill="none" stroke="{c}" stroke-width="1.5"/>')
    L((bx, cy), (bar, cy))
    L((bar, cy - 12), (bar, cy + 12), w=3.5)
    t, b = (end, cy - 25), (end, cy + 25)
    L((bar, cy - 6), t)
    L((bar, cy + 6), b)
    e0, e1 = ((bar, cy - 6), t) if top == "e" else ((bar, cy + 6), b)
    if kind == "NPN":
        arrow(*e0, *e1, "var(--ink)")
    else:
        m = ((e0[0] + e1[0]) / 2, (e0[1] + e1[1]) / 2)
        arrow(*e1, *m, "var(--ink)")
    return t, b


def photodiode(x, y0, y1):  # cathode up: current flows down into the node
    m = (y0 + y1) / 2
    c = BLK["if"]
    L((x, y0), (x, m - 9)); L((x, m + 9), (x, y1))
    out.append(f'<polygon points="{x},{m - 9} {x - 10},{m + 9} {x + 10},{m + 9}" fill="none" stroke="{c}" stroke-width="2"/>')
    L((x - 11, m - 9), (x + 11, m - 9), c=c, w=2.5)
    for k in (0, 12):
        L((x - 34, m - 22 + k), (x - 16, m - 10 + k), c=c, w=1.5)
        arrow(x - 34, m - 22 + k, x - 15, m - 9 + k, c)


def schmitt(x, y, name):
    c = BLK["if"]
    out.append(f'<polygon points="{x},{y - 18} {x + 34},{y} {x},{y + 18}" fill="var(--bg)" stroke="{c}" stroke-width="2" stroke-dasharray="4 3"/>')
    L((x + 5, y + 5), (x + 13, y + 5), (x + 13, y - 5), (x + 19, y - 5), c=c, w=1.3)
    L((x + 9, y + 5), (x + 9, y - 5), (x + 15, y - 5), c=c, w=1.3)
    L((x + 34, y), (x + 50, y), c=c, dash="4 3")
    T(x + 54, y + 5, f"thruster {name}", "ifl")


def box(x, y, w, h, name, c):
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{c}" fill-opacity="0.06" stroke="{c}"'
               f' stroke-width="1.5" stroke-dasharray="7 5"/>')
    T(x + 10, y + 20, name, "blk")


def hop(x, y):  # (unused) a wire crossing
    pass


P = json.load(open("/home/pilgrim/git/simple-learner/discrete/results/hold_drive_screened.json"))["best"]


def eng(v, u):
    for f, p in ((1e9, "G"), (1e6, "M"), (1e3, "k"), (1, ""), (1e-9, "n"), (1e-12, "p")):
        if abs(v) >= f:
            x = v / f
            return f"{x:.3g} {p}{u}".replace(" ", " ")
    return f"{v:g}{u}"


def draw():
    # blocks
    box(30, 30, 345, 400, "eyes and hold", BLK["eye"])
    box(390, 30, 320, 520, "oscillator (a PUT from two transistors)", BLK["osc"])
    box(720, 135, 160, 300, "motor A: scan", BLK["ma"])
    box(890, 30, 235, 405, "motor B: drive", BLK["mb"])
    # eyes: photodiodes from the supply into e (uncounted, part of the body)
    for x, nm in ((70, "left"), (140, "right")):
        vdd(x, 110)
        photodiode(x, 110, 190)
        T(x + 14, 160, nm, "ifl")
    L((70, 190), (70, 235), (140, 235)); L((140, 190), (140, 235), (195, 235)); dot(140, 235)
    T(80, 255, "e", "node")
    # Q0: emitter follower
    t, b = bjt(195, 235, "NPN", BLK["eye"])
    vdd(t[0], 175); L((t[0], 175), t)
    label(250, 222, "Q0", "2N3904", BLK["eye"])
    # h node, C1
    L(b, (235, 300), (300, 300)); dot(235, 300)
    cap(235, 300, 370, BLK["eye"]); gnd(235, 370)
    label(255, 342, "C1", eng(P["ch"], "F"), BLK["eye"])
    L((300, 300), (300, 80), (1040, 80)); dot(300, 300)
    T(310, 296, "h", "node"); T(310, 70, "h (the hold)", "node")
    # oscillator
    dot(450, 80)
    res(450, 80, 280, BLK["osc"]); label(466, 176, "R9 (rf)", eng(P["rf"], "Ω"), BLK["osc"])
    vdd(540, 130); res(540, 130, 280, BLK["osc"]); label(556, 200, "R2 (rt)", eng(P["rt"], "Ω"), BLK["osc"])
    L((450, 280), (540, 280)); dot(540, 280)
    T(460, 298, "a", "node")
    cap(540, 280, 400, BLK["osc"]); gnd(540, 400)
    label(480, 350, "C3 (ct)", eng(P["ct"], "F"), BLK["osc"], "end")
    L((540, 280), (590, 280), (590, 290))
    # Q6 PNP, base on the right, emitter on top
    t, b = bjt(630, 315, "PNP", BLK["osc"], mirror=True, top="e")
    L((590, 290), t)
    label(582, 372, "Q6", "2N3906", BLK["osc"], "end")
    # g
    L((630, 315), (660, 315)); dot(660, 315)
    vdd(660, 130); res(660, 130, 315, BLK["osc"]); label(648, 250, "R4", eng(P["rg1"], "Ω"), BLK["osc"], "end")
    res(660, 315, 400, BLK["osc"]); gnd(660, 400); label(648, 352, "R5", eng(P["rg2"], "Ω"), BLK["osc"], "end")
    T(640, 308, "g", "node")
    # b bus from Q6's collector
    L(b, (590, 470)); dot(590, 470)
    T(578, 466, "b", "node", "end")
    L((590, 470), (610, 470))
    t7, b7 = bjt(610, 470, "NPN", BLK["osc"])
    L(t7, (650, 440), (685, 440), (685, 315), (660, 315))
    gnd(*b7)
    label(668, 488, "Q7", "2N3904", BLK["osc"])
    # R8 shunt from b
    L((590, 470), (545, 470)); dot(545, 470)
    res(545, 470, 520, BLK["osc"])
    gnd(545, 520)
    label(530, 486, "R8 (rsh)", eng(P["rsh"], "Ω"), BLK["osc"], "end")
    # b to the motor buffers, along the bottom
    L((590, 470), (590, 570), (900, 570), (900, 360), (920, 360))
    L((740, 570), (740, 360), (760, 360)); dot(740, 570)
    T(745, 590, "b: every beat of the oscillator", "node")
    # motor A
    vdd(800, 175); res(800, 175, 290, BLK["ma"]); label(812, 225, "R11", eng(P["rp"], "Ω"), BLK["ma"])
    t, b = bjt(760, 360, "NPN", BLK["ma"])
    L(t, (800, 290)); dot(800, 290); gnd(*b)
    label(812, 340, "Q10", "2N3904", BLK["ma"])
    L((800, 290), (840, 290)); T(806, 282, "m0", "node")
    schmitt(840, 290, "A")
    # motor B
    dot(960, 80)
    res(960, 80, 290, BLK["mb"]); label(972, 180, "R13", eng(P["rp"], "Ω"), BLK["mb"])
    t, b = bjt(920, 360, "NPN", BLK["mb"])
    L(t, (960, 290)); dot(960, 290); gnd(*b)
    label(972, 340, "Q12", "2N3904", BLK["mb"])
    L((960, 290), (1000, 290)); T(966, 282, "m1", "node")
    schmitt(1000, 290, "B")


draw()
body = "\n".join(out)
views = {"full": (0, 0, 1150, 610), "eye": (20, 20, 365, 420), "osc": (380, 20, 340, 570),
         "ma": (700, 125, 300, 470), "mb": (880, 20, 260, 420)}
svgs = {k: f'<svg viewBox="{" ".join(map(str, v))}" role="img" aria-label="hold and drive schematic: {k}">{body}</svg>'
        for k, v in views.items()}

# waveforms
d = json.load(open(f"{S}/hd_wave.json"))
t = np.array(d["t"])


def plot(nodes, t0, t1, w=1000, hh=70, gap=18, title=""):
    sel = (t >= t0) & (t <= t1)
    tt = t[sel]
    o = []
    H = len(nodes) * (hh + gap) + 30
    X = lambda x: 70 + (x - t0) / (t1 - t0) * (w - 90)
    for k, (n, name, col, vmax) in enumerate(nodes):
        y0 = 10 + k * (hh + gap)
        v = np.array(d[n])[sel]
        Y = lambda y: y0 + hh - (np.clip(y, 0, vmax) / vmax) * hh
        o.append(f'<line x1="70" x2="{w - 20}" y1="{Y(0)}" y2="{Y(0)}" class="ax"/>')
        if n in ("m0", "m1", "h"):
            o.append(f'<line x1="70" x2="{w - 20}" y1="{Y(2)}" y2="{Y(2)}" class="thr"/>')
            o.append(f'<text x="{w - 18}" y="{Y(2) + 4}" class="tk">2 V</text>')
        # decimate by min/max per pixel column
        cols = np.floor((tt - t0) / (t1 - t0) * (w - 90)).astype(int)
        pts = []
        for c0 in np.unique(cols):
            m = cols == c0
            vv = v[m]
            pts += [(X(tt[m][0]), Y(vv.min())), (X(tt[m][-1]), Y(vv.max()))] if np.ptp(vv) > 0.02 else [(X(tt[m][0]), Y(vv.mean()))]
        o.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{col}" stroke-width="1.6"/>')
        o.append(f'<text x="62" y="{y0 + hh / 2 + 4}" class="wl" text-anchor="end">{name}</text>')
        o.append(f'<text x="62" y="{y0 + hh / 2 + 18}" class="tk" text-anchor="end">0–{vmax:g} V</text>')
    yb = len(nodes) * (hh + gap) + 2
    for p in d["pulses"]:
        if t0 <= p <= t1:
            o.append(f'<line x1="{X(p):.1f}" x2="{X(p):.1f}" y1="{yb - 8}" y2="{yb + 2}" class="pulse"/>')
    step = 0.1 if t1 - t0 > 0.3 else 0.01
    for x in np.arange(np.ceil(t0 / step) * step, t1 + 1e-9, step):
        o.append(f'<text x="{X(x):.1f}" y="{yb + 18}" class="tk" text-anchor="middle">{x:.2f} s</text>')
    return f'<svg viewBox="0 0 {w} {H}" role="img" aria-label="{title}">{"".join(o)}</svg>'


W = {"wave_long": plot([("h", "h (hold)", "var(--c-eye)", 3), ("m0", "m0 (A)", "var(--c-ma)", 3),
                        ("m1", "m1 (B)", "var(--c-mb)", 3)], 0.25, 1.4, title="hold and motors over a second"),
     "wave_short": plot([("a", "a (timing)", "var(--c-osc)", 1.2), ("g", "g (gate)", "var(--c-osc)", 1.2),
                         ("b", "b (beat)", "var(--c-osc)", 1.2), ("h", "h (hold)", "var(--c-eye)", 3),
                         ("m0", "m0 (A)", "var(--c-ma)", 3), ("m1", "m1 (B)", "var(--c-mb)", 3)],
                        0.40, 0.52, hh=55, title="one pulse, beat by beat")}
json.dump({**svgs, **W}, open(f"{S}/hd_svgs.json", "w"))
print("ok", {k: len(v) for k, v in {**svgs, **W}.items()})

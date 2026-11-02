import json
S = "/home/pilgrim/git/simple-learner/lab"
v = json.load(open(f"{S}/hd_svgs.json"))

def rows(items):
    return "".join(f"<tr><td class='rf'>{r}</td><td>{p}</td><td class='num'>{val}</td><td>{job}</td><td>{gone}</td></tr>"
                   for r, p, val, job, gone in items)

HEAD = "<thead><tr><th>ref</th><th>part</th><th>value</th><th>what it does</th><th>without it (16 seeds &times; 40 s; whole circuit 6.82)</th></tr></thead>"

eye = rows([
 ("Q0", "NPN, 2N3904", "β ≈ 420", "Emitter follower. Both eyes' photocurrent (1 µA for 2.5 ms a pulse) goes into its base; its emitter tops the hold up from the supply. One pulse takes h from 0.25 V to 3.0 V.", "Base and emitter joined, so the eyes charge C1 directly: 5.8. Collector and emitter joined: 2.9."),
 ("C1", "capacitor", "1.26 nF", "The hold. Its charge is the memory of having just seen something. It drains through R13 each time Q12 pulls motor B low, and a little through R9.", "Removed: 2.8. Each pulse then fires motor B once, with no memory between pulses."),
])
osc = rows([
 ("R2", "resistor (rt)", "156 MΩ", "Charges the timing capacitor from the supply, about 16 nA.", "Every other cut scored below −0.4: the creature stops foraging."),
 ("C3", "capacitor (ct)", "304 pF", "Timing capacitor, node a. It ramps from 0.35 V up to 1.0 V, then dumps into b.", "″"),
 ("R4", "resistor (rg1)", "365 MΩ", "Top of the gate divider.", "″"),
 ("R5", "resistor (rg2)", "80.4 MΩ", "Bottom of the gate divider. It holds g at about 0.56 V, so a fires about a diode drop above that.", "″"),
 ("Q6", "PNP, 2N3906", "β ≈ 180", "The PUT's anode side. Emitter at a, base at g, collector into b. Once a passes g by about 0.45 V it conducts into Q7's base.", "″"),
 ("Q7", "NPN, 2N3904", "β ≈ 420", "The PUT's cathode side. It pulls g down, which turns Q6 harder on, so the pair latches until C3 is spent.", "″"),
 ("R8", "resistor (rsh)", "27.9 MΩ", "Base shunt on b. It keeps Q7 off between beats and sets the current at which the latch lets go.", "On the ladder (with R9 and Q0 already gone), Q10's and Q12's bases took over its job: 2.6."),
 ("R9", "resistor (rf)", "1 GΩ", "Links the hold to the timing node. At rest it bleeds h down to about 0.25 V, below motor B's threshold. While the hold is charged it adds about 2.5 nA, so the scan speeds up from 60 to about 70 beats a second.", "Removed: 6.1. This was the ladder's first rung: the hold then drains only through motor B."),
])
ma = rows([
 ("Q10", "NPN, 2N3904", "β ≈ 420", "Shares b, so each beat saturates it and pulls m0 to 0 V, which re-arms thruster A's input.", "Below −0.4."),
 ("R11", "resistor (rp)", "7.77 MΩ", "Pull-up from the supply. When the beat ends, m0 rises back through 2 V in about 80 µs (7.77 MΩ with the 10 pF input): one firing a beat, 60 a second.", "Below −0.4."),
])
mb = rows([
 ("Q12", "NPN, 2N3904", "β ≈ 420", "Same as Q10, on m1.", "Below −0.4."),
 ("R13", "resistor (rp)", "7.77 MΩ", "Pull-up taken from the hold, not the supply. With h at rest (0.25 V), m1 never reaches 2 V and B stays silent. With the hold charged, each beat fires B. Each beat's pull-down also takes charge from C1, so the hold is spent by driving.", "Shorted: 1.3."),
])

html = f"""<title>Hold-and-Drive, 14 Parts</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+Condensed:wght@500;600&family=IBM+Plex+Sans:ital,wght@0,400;0,600;1,400&display=swap">
<style>
/* layout: a datasheet. Summary strip, the full schematic, then one block per section (crop + parts table), then the bench traces */
:root {{
  --bg: #f6f7f8; --panel: #ffffff; --ink: #1d2328; --mute: #5b6670; --rule: #d5dae0;
  --c-eye: #0072B2; --c-osc: #C98500; --c-ma: #007A5A; --c-mb: #B5508F; --c-if: #8a949c;
  --f-disp: "IBM Plex Sans Condensed", "Arial Narrow", sans-serif;
  --f-body: "IBM Plex Sans", system-ui, sans-serif;
  --f-mono: "IBM Plex Mono", ui-monospace, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #14181c; --panel: #1b2026; --ink: #e3e7ea; --mute: #9aa5ae; --rule: #313840;
  --c-eye: #56B4E9; --c-osc: #E69F00; --c-ma: #2CC197; --c-mb: #E08DC0; --c-if: #7b858d; color-scheme: dark }} }}
:root[data-theme="dark"] {{
  --bg: #14181c; --panel: #1b2026; --ink: #e3e7ea; --mute: #9aa5ae; --rule: #313840;
  --c-eye: #56B4E9; --c-osc: #E69F00; --c-ma: #2CC197; --c-mb: #E08DC0; --c-if: #7b858d; color-scheme: dark }}
body {{ background: var(--bg); color: var(--ink); font: 15px/1.55 var(--f-body); }}
.wrap {{ max-width: 1180px; margin: 0 auto; padding-block: 28px 64px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  display: grid; gap: 28px; }}
h1, h2 {{ font-family: var(--f-disp); font-weight: 600; text-wrap: balance; margin: 0; }}
h1 {{ font-size: 2.1rem; letter-spacing: -0.01em; }}
h2 {{ font-size: 1.35rem; display: flex; align-items: center; gap: 10px; }}
h2 .sw {{ width: 14px; height: 14px; border-radius: 3px; border: 2px dashed currentColor; }}
p {{ margin: 0; max-width: 68ch; }}
.lede {{ color: var(--mute); }}
.stats {{ display: flex; flex-wrap: wrap; gap: 10px 28px; font-variant-numeric: tabular-nums; }}
.stats div {{ display: grid; }}
.stats b {{ font: 500 1.25rem var(--f-mono); }}
.stats span {{ font-size: 0.78rem; color: var(--mute); text-transform: uppercase; letter-spacing: 0.06em; }}
.sheet {{ background: var(--panel); border: 1px solid var(--rule); border-radius: 8px; padding: 14px; overflow-x: auto; }}
.sheet svg {{ display: block; min-width: 860px; width: 100%; height: auto; }}
.sheet.wave svg {{ min-width: 720px; }}
section {{ display: grid; gap: 12px; }}
.block {{ display: grid; grid-template-columns: minmax(0, 340px) minmax(0, 1fr); gap: 18px; align-items: start; }}
.block .sheet svg {{ min-width: 0; }}
.block > div {{ display: grid; gap: 10px; min-width: 0; }}
@media (max-width: 760px) {{ .block {{ grid-template-columns: minmax(0, 1fr); }} .block .sheet {{ max-width: 380px; }} }}
.tbl {{ overflow-x: auto; }}
table {{ border-collapse: collapse; width: 100%; font-size: 0.9rem; }}
th {{ text-align: left; font: 600 0.72rem var(--f-body); text-transform: uppercase; letter-spacing: 0.06em; color: var(--mute);
  border-bottom: 1px solid var(--rule); padding: 6px 8px; }}
td {{ border-bottom: 1px solid var(--rule); padding: 7px 8px; vertical-align: top; }}
td.rf {{ font: 600 0.9rem var(--f-mono); white-space: nowrap; }}
td.num {{ font-family: var(--f-mono); white-space: nowrap; font-variant-numeric: tabular-nums; }}
.note {{ font-size: 0.88rem; color: var(--mute); }}
code {{ font-family: var(--f-mono); font-size: 0.88em; }}
/* svg text */
.ref {{ font: 600 13px var(--f-body); fill: var(--ink); }}
.val {{ font: 12px var(--f-mono); }}
.node {{ font: italic 600 13px Georgia, serif; fill: var(--mute); }}
.sup {{ font: 10px var(--f-body); fill: var(--mute); }}
.blk {{ font: 600 12px var(--f-body); fill: var(--ink); }}
.ifl {{ font: 11px var(--f-body); fill: var(--c-if); }}
.wl {{ font: 12px var(--f-body); fill: var(--ink); }}
.tk {{ font: 10px var(--f-body); fill: var(--mute); }}
.ax {{ stroke: var(--rule); }}
.thr {{ stroke: var(--mute); stroke-dasharray: 3 3; }}
.pulse {{ stroke: var(--ink); stroke-width: 2; }}
</style>
<div class="wrap">
<header style="display:grid;gap:12px">
  <h1>Hold-and-Drive, 14 Parts</h1>
  <p class="lede">The simplest circuit found so far that forages efficiently in an all-food world, built from 5 bipolar transistors, 7 resistors and 2 capacitors on a 3 V coin cell. One clock beats about 60 times a second and always fires thruster A, so the creature turns on the spot and scans. An eye pulse charges a hold capacitor, and while the hold lasts, about 0.17 s, each beat fires thruster B too, so the creature drives straight at what it saw.</p>
  <div class="stats">
    <div><b>6.62</b><span>efficiency [6.45, 6.80]</span></div>
    <div><b>18.2</b><span>meals / 10 s [17.5, 19.0]</span></div>
    <div><b>0%</b><span>lives stranded</span></div>
    <div><b>113 nW</b><span>in a life (72 at rest)</span></div>
    <div><b>14</b><span>parts</span></div>
  </div>
  <p class="note">Judged on 32 held-out seeds, each a 100 s closed-loop life in ngspice, with each seed's own part tolerances (R 1%, C 5%, transistor I<sub>S</sub> 20%, β 25%). Values are from <code>discrete/results/hold_drive_screened.json</code>.</p>
</header>

<section>
  <h2>The whole circuit</h2>
  <div class="sheet">{v['full']}</div>
  <p class="note">Coloured parts are the 14 that count. Grey dashed parts belong to the body and are not counted. Each eye is a photodiode from the supply that gives 1 µA for 2.5 ms per pulse and can push its node a little above the supply, as a solar cell does. Each thruster driver has a CMOS Schmitt input (10 pF) that fires when its node rises through 2 V and re-arms below 1 V. Every "+3 V" bar is the same coin cell. Every ground symbol is the same ground. Node names are in italics.</p>
</section>

<section>
  <h2 style="color:var(--c-eye)"><span class="sw"></span>Eyes and hold</h2>
  <div class="block"><div class="sheet">{v['eye']}</div>
  <div><p>Both eyes feed one node, <i>e</i>, because in an all-food world it doesn't matter which eye saw the block. Q0 is an emitter follower: the eye supplies only the base current, and the charge for the hold comes from the supply through the collector. So even a far block's single, weak pulse fills C1 to about 3 V. With no pulses, R9 bleeds h down to about 0.25 V.</p>
  <div class="tbl"><table>{HEAD}<tbody>{eye}</tbody></table></div></div></div>
</section>

<section>
  <h2 style="color:var(--c-osc)"><span class="sw"></span>Oscillator</h2>
  <div class="block"><div class="sheet">{v['osc']}</div>
  <div><p>Q6 and Q7 together make a programmable unijunction transistor (PUT), a switch that latches on and lets go by itself. A ready-made PUT or UJT needs microamps to let go, which would cost as much power as the creature spends resting. This pair runs on nanoamps. R2 charges C3 until node a passes the gate g by about a diode drop. Then Q6 conducts into Q7's base, Q7 pulls g down, and that turns Q6 on harder. The pair latches and dumps C3 into b, then lets go once C3 is spent. Each dump lifts b briefly; that is the beat. Most of the 72 nW at rest goes through R2 and the divider.</p>
  <div class="tbl"><table>{HEAD}<tbody>{osc}</tbody></table></div></div></div>
</section>

<section>
  <h2 style="color:var(--c-ma)"><span class="sw"></span>Motor A: scan</h2>
  <div class="block"><div class="sheet">{v['ma']}</div>
  <div><p>A pull-up from the supply and a switch on the beat. Each beat pulls m0 down to 0 V and lets it go, so thruster A fires once a beat. One thruster alone turns the creature on a 1.2 mm circle, which sweeps its eyes around.</p>
  <div class="tbl"><table>{HEAD}<tbody>{ma}</tbody></table></div></div></div>
</section>

<section>
  <h2 style="color:var(--c-mb)"><span class="sw"></span>Motor B: drive</h2>
  <div class="block"><div class="sheet">{v['mb']}</div>
  <div><p>The same as motor A, except that its pull-up comes from the hold. Motor B fires on each beat only while h is above the 2 V threshold. With both thrusters firing together, the creature goes straight, at 0.8 mm a beat. B's firings drain the hold, so the more it has driven, the sooner it stops.</p>
  <div class="tbl"><table>{HEAD}<tbody>{mb}</tbody></table></div></div></div>
</section>

<section>
  <h2>On the bench</h2>
  <p>Nominal parts in ngspice. A single pulse arrives at 0.45 s, as a far block would give. From 0.90 s to 1.15 s comes a burst at 40 pulses a second, as a near block gives. Pulse times are marked under each plot.</p>
  <div class="sheet wave">{v['wave_short']}</div>
  <p class="note">One pulse, beat by beat. Node a ramps and dumps every 15–17 ms. Node b lifts at each dump. Before the pulse only m0 dips and fires. At 0.45 s, h jumps to 3.0 V, and from then on m1 fires on every beat, along with m0 (its first firing comes from the pulse itself).</p>
  <div class="sheet wave">{v['wave_long']}</div>
  <p class="note">Over a second: after the single pulse, B fires on 12 beats, until h falls through 2 V at 0.62 s, about 0.17 s later. The burst keeps h near the top, so B fires throughout. Meanwhile the scan speeds up from 60 to about 70 beats a second, because the charged hold feeds the timing node through R9.</p>
</section>
</div>
"""
open(f"{S}/hold_drive_14.html", "w").write(html)
print(len(html))

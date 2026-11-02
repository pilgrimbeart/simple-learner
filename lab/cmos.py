"""Scratch CMOS (SKY130) circuits for discrete/life.py (Netlist(chip=True), supply 1.8 V)."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from discrete.circuits import CIRCUITS
from discrete.life import Netlist

VDD = 1.8


def schmitt(n, i, o, w=1.0, l=4.0, x=None):
    """A 6-transistor CMOS Schmitt inverter from i to o: two nMOS in series to ground (their middle pulled towards the
    supply by an nMOS the output drives) and two pMOS in series to the supply (their middle pulled towards ground):
    positive feedback, so it switches cleanly with hysteresis."""
    x = x or o
    n.M("N", o, i, x + "_n", w, l)
    n.M("N", x + "_n", i, "0", w, l)
    n.M("N", "vdd", o, x + "_n", w, l)
    n.M("P", o, i, x + "_p", w, l)
    n.M("P", x + "_p", i, "vdd", w, l)
    n.M("P", "0", o, x + "_p", w, l)


def inv(n, i, o, w=1.0, l=4.0):
    n.M("N", o, i, "0", w, l)
    n.M("P", o, i, "vdd", w, l)


def cmos_osc(rng=None, r=3.6e9, c=1e-11):
    """Blind: a Schmitt RC oscillator firing both motors (a timing test)."""
    n = Netlist(rng, chip=True)
    schmitt(n, "x", "y")
    n.R("y", "x", r)
    n.C("x", "0", c)
    inv(n, "y", "m0")
    n.motor = ["m0", "m0"]
    return n


CIRCUITS["cmos_osc"] = (cmos_osc, VDD)


def bias(n, vbn=0.35, vbp=1.45):
    """The chip's two bias lines (a bias generator each, counted as a part): an nMOS with its gate at vbn, or a pMOS at
    vbp, passes about a nanoamp."""
    for name, v in (("vbn", vbn), ("vbp", vbp)):
        n.lines.append(f"V{name} {name} 0 {v:g}")
        n.count["V"] = n.count.get("V", 0) + 1


def sinv(n, i, o, w=1.0, l=4.0, bn="vbn", bp="vbp"):
    """A current-starved inverter: its pull-up and pull-down each through a limiter on a bias line (about a nanoamp)."""
    n.M("P", o, i, o + "_sp", w, l)
    n.M("P", o + "_sp", bp, "vdd", w, l)
    n.M("N", o, i, o + "_sn", w, l)
    n.M("N", o + "_sn", bn, "0", w, l)


def sschmitt(n, i, o, w=1.0, l=4.0):
    """A starved Schmitt inverter: the 6-transistor Schmitt with its supply and ground each through a limiter."""
    n.M("N", o, i, o + "_n", w, l)
    n.M("N", o + "_n", i, o + "_gn", w, l)
    n.M("N", o + "_gn", "vbn", "0", w, l)
    n.M("N", "vdd", o, o + "_n", w, l)
    n.M("P", o, i, o + "_p", w, l)
    n.M("P", o + "_p", i, o + "_gp", w, l)
    n.M("P", o + "_gp", "vbp", "vdd", w, l)
    n.M("P", "0", o, o + "_p", w, l)


def osc_test(rng=None, c=2e-11, vbn=0.35, vbp=1.45, vbn2=0.35, vbp2=1.45):
    """A starved relaxation oscillator: x charged and discharged by a starved inverter (bias lines vbn2, vbp2) from y2,
    the Schmitt's output y through an inverter; motor A on y2."""
    n = Netlist(rng, chip=True)
    bias(n, vbn, vbp)
    n.lines.append(f"Vbn2 vbn2 0 {vbn2:g}"); n.lines.append(f"Vbp2 vbp2 0 {vbp2:g}")
    sschmitt(n, "x", "y")
    sinv(n, "y", "m0")
    sinv(n, "m0", "x", bn="vbn2", bp="vbp2")
    n.C("x", "0", c)
    n.motor = ["m0", "m0"]
    return n


CIRCUITS["osc_test"] = (osc_test, VDD)


def oai22(n, a, b, c, d, o):
    """o = not((a or b) and (c or d))."""
    n.M("N", o, a, o + "_m", 1.0); n.M("N", o, b, o + "_m", 1.0)
    n.M("N", o + "_m", c, "0", 1.0); n.M("N", o + "_m", d, "0", 1.0)
    n.M("P", o + "_ab", a, "vdd", 1.0); n.M("P", o, b, o + "_ab", 1.0)
    n.M("P", o + "_cd", c, "vdd", 1.0); n.M("P", o, d, o + "_cd", 1.0)


def aoi21(n, a, b, c, o):
    """o = not(a or (b and c))."""
    n.M("N", o, a, "0", 1.0)
    n.M("N", o, b, o + "_m", 1.0); n.M("N", o + "_m", c, "0", 1.0)
    n.M("P", o + "_bc", b, "vdd", 1.0); n.M("P", o + "_bc", c, "vdd", 1.0)
    n.M("P", o, a, o + "_bc", 1.0)


def tg(n, a, b, gn, gp):
    """A transmission gate between a and b: on while gn is high and gp low."""
    n.M("N", a, gn, b, 1.0)
    n.M("P", a, gp, b, 1.0)


def pol(rng=None, vbn=0.38, vbp=1.05, vbw=0.25, vbpw=1.3, cs=5e-13, ch=5e-12, cb=2e-11, cx=1e-11, cq=3e-12,
        wslow=0.5, lslow=8.0, wfast=1.0, lfast=4.0, wbl=0.42, lbl=20.0, wbt=0.84, mirror=0.0, gain=4.0, cdq=8e-12, ldq=20.0, fb=0.0,
        wdq=0.42, counter=0.0, vbf=1.2, rest=0.58, runfast=0.0, wm=1.0, lm=4.0, edge=0.0):
    """The best learning policy (discrete/policies.py, D10) in SKY130 CMOS, current-starved where inputs are slow:
    - each eye's node (cs, a weak leak) held up a few ms by each pulse, read by a starved Schmitt (e0, e1: low = seen);
    - the bit (q, qb) chooses which is food: F = seen by the eye q says is food, P = by the other (two OAI22 gates);
    - drive: F charges hd (ch, a weak leak: about 0.15 s), P empties it; a Schmitt reads it (dn low = DRIVE);
    - bored: F charges bt (cb, a weaker leak: about 3 s); a Schmitt reads it (run high = RUN, until the next F);
    - one oscillator (x, cx) charged and discharged by a starved inverter (wslow), and by a second pair (wfast) while
      DRIVE: slow scan, fast drive; motor A on every beat, motor B on beats during DRIVE or RUN (an AOI21);
    - learning: the taste node tq (cq) held up by a weak pull-up, each poison pulling it down about 0.75 V, food
      lifting it (clamped): two poisons in quick succession take it below the Schmitt's threshold (T rises), which
      toggles a master-slave flip-flop holding the bit."""
    n = Netlist(rng, chip=True)
    for name, v in (("vbn", vbn), ("vbp", vbp), ("vbw", vbw)) + ((("vbpw", vbpw),) if not mirror else ())             + ((("vbf", vbf),) if counter else ()):
        n.lines.append(f"V{name} {name} 0 {v:g}")
        n.count["V"] = n.count.get("V", 0) + 1
    n.eye, n.motor, n.taste = ["s0", "s1"], ["m0", "m1"], ("tm" if mirror else "tq")
    for k in (0, 1):                                    # eyes
        n.C(f"s{k}", "0", cs)
        n.M("N", f"s{k}", "vbw", "0")
        sschmitt(n, f"s{k}", f"e{k}")
    oai22(n, "e0", "q", "e1", "qb", "F")                # food seen, poison seen
    oai22(n, "e0", "qb", "e1", "q", "P")
    inv(n, "F", "Fn")
    n.M("P", "hd", "Fn", "vdd")                         # drive
    n.M("N", "hd", "P", "0")
    n.M("N", "hd", "vbw", "0")
    n.C("hd", "0", ch)
    sschmitt(n, "hd", "dn")
    inv(n, "dn", "dr")
    n.M("P", "bt", "Fn", "vdd")                         # bored
    n.M("N", "bt", "vbw", "0", wbt, lbl)
    n.C("bt", "0", cb)
    sschmitt(n, "bt", "run")
    inv(n, "run", "runn")
    n.C("x", "0", cx)                                   # the oscillator
    sschmitt(n, "x", "y")
    sinv(n, "y", "m0")
    n.M("P", "x", "m0", "x_cp", wslow, lslow); n.M("P", "x_cp", "vbp", "vdd", wslow, lslow)
    n.M("N", "x", "m0", "x_cn", wslow, lslow); n.M("N", "x_cn", "vbn", "0", wslow, lslow)
    fp, fn = "dn", "dr"                                 # the fast pair, while DRIVE (runfast: or RUN)
    if runfast:
        n.M("N", "idle", "dn", "idle_m", 1.0); n.M("N", "idle_m", "runn", "0", 1.0)   # dor = nand(dn, runn): DRIVE or RUN
        n.M("P", "idle", "dn", "vdd", 1.0); n.M("P", "idle", "runn", "vdd", 1.0)
        inv(n, "idle", "dorn")
        fp, fn = "dorn", "idle"
    n.M("P", "x", "m0", "x_fp"); n.M("P", "x_fp", fp, "x_fp2"); n.M("P", "x_fp2", "vbp", "vdd", wfast, lfast)
    n.M("N", "x", "m0", "x_fn"); n.M("N", "x_fn", fn, "x_fn2"); n.M("N", "x_fn2", "vbn", "0", wfast, lfast)
    if fb:                                              # motor B: clock and (DRIVE or RUN), or food seen this moment:
        n.M("N", "m1", "Fn", "m1_m", 1.0)               # m1 = not((y or (dn and runn)) and Fn)
        n.M("N", "m1_m", "y", "0", 1.0)
        n.M("N", "m1_m", "dn", "m1_x", 1.0); n.M("N", "m1_x", "runn", "0", 1.0)
        n.M("P", "m1", "Fn", "vdd", 1.0)
        n.M("P", "m1", "y", "m1_p", 1.0)
        n.M("P", "m1_p", "dn", "vdd", 1.0); n.M("P", "m1_p", "runn", "vdd", 1.0)
    elif edge:                                          # motor B latched to the beat: built last (below), so that
        assert runfast                                  # every other part keeps its tolerances (the AOI21's six
        for _ in range(6 if n.rng is not None else 0):  # draws taken)
            n.rng.normal()
    else:
        aoi21(n, "y", "dn", "runn", "m1")               # motor B: clock and (DRIVE or RUN)
    if mirror:                                          # doubt: each poison's pulse drawn through a pMOS diode (tm),
        n.M("P", "tm", "tm", "vdd", 1.0)                # copied k times over into dq, which a weak leak drains: two
        for _ in range(int(gain)):                      # (unit copies: a pMOS's current isn't proportional to its width)
            n.M("P", "dq", "tm", "vdd", 1.0)                # poisons close together lift it past the Schmitt
        if counter:                                     # counter: no leak; food tasted steps doubt down as far (a
            n.M("P", "fdn", "vbf", "tm", 1.0)           # pMOS from the taste node, its gate held so it passes nothing
            n.M("N", "fdn", "fdn", "0", wm, lm)         # at rest, into an nMOS diode copied as many times from dq);
            for _ in range(int(gain)):                  # the rail the bound of trust; the flip pulls dq down until
                n.M("N", "dq", "fdn", "0", wm, lm)      # its Schmitt lets go (self-timed); dq's capacitor split
            n.M("N", "dq", "T", "dq_r", 1.0)            # between the rails, so a life begins at rest
            n.M("N", "dq_r", "vbn", "0", 1.0)
            n.C("dq", "vdd", cdq * rest)
            n.C("dq", "0", cdq * (1 - rest))
        else:
            n.C("dq", "0", cdq)
            n.M("N", "dq", "vbw", "0", wdq, ldq)
        sschmitt(n, "dq", "Tx")
        inv(n, "Tx", "T")
    else:
        n.C("tq", "0", cq)                              # doubt
        n.M("P", "tq", "vbpw", "vdd", wbl, lbl)
        sschmitt(n, "tq", "T")
    inv(n, "T", "Tn")                                   # the bit: a master-slave flip-flop toggled as T rises (T
    inv(n, "Tn", "Tb")                                  # sharpened through two inverters): the master follows qb while
    n.R("qb", "qd", 1e9)                                # T is low, slowly (rm, cm: so that it can't follow the slave
    n.C("qd", "0", 1e-12)                               # in the moment both gates are half open), and holds while T is
    tg(n, "qd", "ma", "Tn", "Tb")                       # high, when the slave takes qb from it (so q flips)
    inv(n, "ma", "mb")
    inv(n, "mb", "mc")
    tg(n, "mc", "ma", "Tb", "Tn")
    tg(n, "mb", "qb", "Tb", "Tn")
    inv(n, "qb", "q")
    inv(n, "q", "qc")
    tg(n, "qc", "qb", "Tn", "Tb")
    if edge:                                            # motor B: clock and (DRIVE or RUN) as it was when the beat
        sinv(n, "y", "yb")                              # began: dorn (low = DRIVE or RUN) latched while y is high,
        tg(n, "dorn", "el", "y", "yb")                  # held through the beat, so B's first firing waits for A's
        sinv(n, "el", "elb")                            # (D13: unlatched, B fired alone at 55% of drives' starts)
        n.M("N", "el", "elb", "el_n", 0.36, 8.0); n.M("N", "el_n", "yb", "0", 0.36, 8.0)   # weak keeper, on while
        n.M("P", "el", "elb", "el_p", 0.42, 8.0); n.M("P", "el_p", "y", "vdd", 0.42, 8.0)  # the gate is shut
        n.M("P", "m1_p", "y", "vdd", 1.0); n.M("P", "m1", "el", "m1_p", 1.0)               # m1 = nor(y, el)
        n.M("N", "m1", "y", "0", 1.0); n.M("N", "m1", "el", "0", 1.0)
    return n


CIRCUITS["pol"] = (pol, VDD)

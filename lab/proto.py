"""Scratch prototypes on learn_avoid (D10's suggestions), registered in CIRCUITS for try.py-style runs."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from discrete.circuits import CIRCUITS, learn_hold
from discrete.life import SUPPLY


def proto(rng=None, cu=1e-8, ru=1e9, rd=1e6, rf=0.0, pk=0.0, rpk=1e8, rpku=0.0, ce=0.0, rce=1e9, rhz=1e9, astable=0.0, rc=1e8, rb1=2e8,
          cb=4.7e-11, rv=3e8, follow=1.0, osc2=0.0, rt2=2.17e8, ct2=3.05e-10,
          rg3=2.11e8, rg4=4.32e7, rsh2=4.99e7, rsup=1e9, rsup2=0.0, rhl=0.0, f2=0.0, run2=0.0, rr=1e9, rrg=1e8, rkr=1.0, **kw):
    """learn_avoid (46 parts), and
    rf > 0: two speeds: a follower NPN from the hold (base h, collector vdd, emitter x) feeds the timing node a through
      rf, so the oscillator runs faster while the hold is up (2 parts; set rt larger for a slower scan);
    pk > 0: poison ends the run: an NPN on k pulls node y low (y pulled up by rpk), turning on a PNP from the supply
      into u, as a sighting lifts it (3 parts)."""
    n = learn_hold(rng, roam=False, sink="k", **kw)
    for s in ("s0", "s1"):
        n.Q("NPN", "vdd", s, "u")
    n.C("u", "0", cu)
    n.R("u", "0", ru)
    n.Q("PNP", "r" if run2 else "h", "u", "vdd")
    n.R("k", "0", rd)
    n.Q("NPN", "h", "k", "0")
    if astable:                                         # the oscillator and motor A replaced by an astable multivibrator
        for i in (0, 1, 2, 3, 4, 5, 6, 7, 8, 10):       # (lines 0-8: put_osc, motor A's NPN and pull-up; 10: motor B's
            ln = n.lines[i]                             # NPN on b)
            n.count[ln[0]] -= 1
            n.lines[i] = "* removed: " + ln
        n.Q("NPN", "m0", "b1", "0")                     # side 1: its collector is motor A
        n.R("vdd", "m0", rc)
        n.C("m0", "b2", cb)
        n.R("v", "b2", rb1)
        n.Q("NPN", "c2", "b2", "0")                     # side 2
        n.R("vdd", "c2", rc)
        n.C("c2", "b1", cb)
        n.R("v", "b1", rb1)
        n.Q("NPN", "m1", "b1", "0")                     # motor B's NPN shares side 1's base: both fire as side 1 lets go
        n.R("vdd", "v", rv)                             # the speed node: slow from the supply through rv ...
        if follow:
            n.Q("NPN", "vdd", "h", "v")                 # ... fast while the hold is up
    if osc2:                                            # a second oscillator for the drive, its timing current from the
        n.lines[10] = "* removed: " + n.lines[10]       # hold (fast while the hold is up, stopped when it has drained):
        n.count["Q"] -= 1                               # its beats fire both motors; motor B's NPN moves to it
        if f2:                                          # (through a follower: its current from the supply, so as not
            n.Q("NPN", "vdd", "h", "hf")                # to drain the hold)
        n.R("hf" if f2 else "h", "a2", rt2)
        n.C("a2", "0", ct2)
        n.R("vdd", "g2", rg3)
        n.R("g2", "0", rg4)
        n.Q("PNP", "b2", "g2", "a2")
        n.Q("NPN", "g2", "b2", "0")
        n.R("b2", "0", rsh2)
        n.Q("NPN", "m0", "b2", "0")
        n.Q("NPN", "m1", "b2", "0")
        if rsup:                                        # while the hold is up, the scan's timing node is emptied
            n.R("h", "hs", rsup)
            n.Q("NPN", "a", "hs", "0")
            if rsup2:                                   # (a divider: only above a threshold)
                n.R("hs", "0", rsup2)
        if rhl:                                         # a leak, so the hold empties once the drive stops
            n.R("h", "0", rhl)
    if run2:                                            # the run at the scan's beat: the giving-up PNP feeds r (rr to
        n.R("r", "0", rr)                               # ground), and motor B fires at each scan beat while r is up (an
        n.Q("NPN", "m1", "rg", "mb")                    # NPN on r, through rrg, above one on the beat); motor B's
        n.R("r", "rg", rrg)                             # pull-up from the supply
        n.Q("NPN", "mb", "b", "0")
        n.lines[11] = n.lines[11].replace(" h m1 ", " vdd m1 ")
        if rkr:                                         # poison seen (k): r emptied, the run stops
            n.Q("NPN", "r", "k", "0")
    if rf:
        n.Q("NPN", "vdd", "h", "x")
        n.R("x", "a", rf)
    if ce:                                              # two speeds by capacitance: ce joins the timing node a while
        n.C("a", "e", ce)                               # the hold is low: an NPN switch from e to ground (saturated,
        n.Q("NPN", "e", "z", "0")                       # it conducts both ways), its base pulled up by rce and pulled
        n.R("vdd", "z", rce)                            # down by an inverter NPN on the hold; so the scan is slow and
        n.Q("NPN", "z", "hz", "0")                      # the drive fast, the timing current unchanged (rhz: so as
        n.R("h", "hz", rhz)                             # not to clamp the hold)
        n.D("0", "e")                                   # (ce discharges with a through the diode)
    if pk:
        n.Q("NPN", "y", "k", "0")
        n.R("vdd", "y", rpk)
        n.Q("PNP", "yu" if rpku else "u", "y", "vdd")
        if rpku:                                        # (through rpku: a poison only partly lifts u)
            n.R("yu", "u", rpku)
    return n


CIRCUITS["proto"] = (proto, SUPPLY)

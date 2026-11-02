"""Prototype (scratch, until queue 7 frees discrete/circuits.py): learn_hold with its roam oscillator replaced by
hunger. A follower copies the taste node's peaks (q, lifted by each food) onto a slow node u (cu, leaking through ru);
when u has sagged below a threshold (the divider rh1, rh2 from the supply to u setting a PNP's base), the PNP feeds
the hold from the supply: both thrusters drive, straight, until a food lifts q and so u again."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from discrete.circuits import CIRCUITS, learn_hold
from discrete.life import SUPPLY


def learn_hunger(rng=None, cu=30e-9, ru=1e9, rh1=5e8, rh2=1e9, roam=False, eyes=0, avoid=0, rd=1e6, rf=0.0, rfd=0, **kw):
    n = learn_hold(rng, roam=bool(roam), **kw)
    for b in (("s0", "s1") if eyes else ("q",)):     # eyes: the time since the free eye last saw, not since food
        n.Q("NPN", "vdd", b, "u")
    n.C("u", "0", cu)
    n.R("u", "0", ru)
    n.R("vdd", "ub", rh1)
    n.R("ub", "u", rh2)
    n.Q("PNP", "h", "ub", "vdd")
    if avoid:                                       # the silenced eye's current, sunk by its shunt, now lifts k
        for i, ln in enumerate(n.lines):            # (its emitter moved off ground), and an NPN on k empties the
            for e in ("s0", "s1"):                  # hold: a poison ahead cuts motor B, so the creature turns
                if ln.startswith("Q") and ln.split()[1:4] == [e, e + "b", "0"]:
                    n.lines[i] = " ".join(ln.split()[:3] + ["k"] + ln.split()[4:])
        n.R("k", "0", rd)
        n.Q("NPN", "h", "k", "0")
    if rf:                                          # the hold speeds the oscillator (hold_drive's rf): a slow scan,
        if rfd:                                     # a fast drive (rfd: through a diode, so that a low hold can't
            n.D("hf", "a")                          # drain the timing node)
            n.R("h", "hf", rf)
        else:
            n.R("h", "a", rf)
    return n


CIRCUITS["learn_hunger"] = (learn_hunger, SUPPLY)

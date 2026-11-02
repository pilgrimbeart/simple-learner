

def straight(rng=None, rt=100e6, ct=470e-12, rg1=150e6, rg2=75e6, rsh=30e6, rp=10e6):
    """Blind straight, the baseline (9 parts): the oscillator pulls one pull-up low at each pulse, and both motors read
    that node (a wire), so both thrusters fire together: straight ahead at a steady rate, the eyes unwired."""
    n = Netlist(rng)
    n.motor = ["m", "m"]
    put_osc(n, "a", "g", "b", rt, ct, rg1, rg2, rsh)
    n.Q("NPN", "m", "b", "0")
    n.R("vdd", "m", rp)
    return n


def reflex_scan(rng=None, rt=100e6, ct=470e-12, rg1=150e6, rg2=75e6, rsh=30e6, rp=10e6, re=10e6, rb=10e6):
    """Reflex and scan (11 parts): the oscillator fires motor A (scanning); both eyes feed motor B's node directly,
    with a leak, so each pulse fires motor B, and through rb the pulse also turns on motor A's NPN, firing it too."""
    n = Netlist(rng)
    n.eye = ["m1", "m1"]
    put_osc(n, "a", "g", "b", rt, ct, rg1, rg2, rsh)
    n.Q("NPN", "m0", "b", "0")
    n.R("vdd", "m0", rp)
    n.R("m1", "0", re)
    n.R("m1", "b", rb)
    return n


def hold_drive_a(rng=None, rt=100e6, ct=470e-12, rg1=100e6, rg2=150e6, rsh=30e6, rp=30e6, ch=1e-9, rf=100e6):
    """Hold and drive with the timing node as motor A (13 parts): the oscillator's capacitor charges motor A's node
    past the threshold and the switch dumps it below re-arming, so no buffer is needed; motor B is a diode AND of
    the timing node and the hold (pulled up through rp), high only when both are."""
    n = Netlist(rng)
    n.eye = ["e", "e"]
    n.Q("NPN", "vdd", "e", "h")
    n.C("h", "0", ch)
    put_osc(n, "m0", "g", "b", rt, ct, rg1, rg2, rsh)
    n.R("h", "m0", rf)
    n.R("vdd", "m1", rp)
    n.D("m1", "m0")
    n.D("m1", "h")
    return n


def switch(n: Netlist, a, g, b, ct, rg1, rg2, rsh):
    """The oscillator's switch and timing capacitor, without its charging resistor (6 parts): a PUT of a PNP and an
    NPN (put_osc); whatever charges a fires it."""
    n.C(a, "0", ct)
    n.R("vdd", g, rg1)
    n.R(g, "0", rg2)
    n.Q("PNP", b, g, a)
    n.Q("NPN", g, b, "0")
    n.R(b, "0", rsh)


def bare(rng=None, ct=470e-12, rg1=100e6, rg2=150e6, rsh=30e6, r1=200e6, ce=1e-9, rf=50e6, rp=30e6):
    """Hold and drive pared (11 parts). The timing capacitor is motor A's node: it charges past the motor's threshold,
    and the switch dumps it below re-arming. It charges from the supply through r1 then rf, and between them sits the
    hold capacitor (e), which both eyes feed directly: at rest e settles below the threshold (the oscillator's current
    drops most of the supply across r1); a pulse lifts it, so the oscillator runs faster while it lasts. Motor B is
    pulled up from e (rp) and held down to motor A's node by a diode, so it follows motor A's ramp, but only as high
    as e: it crosses the threshold, and both thrusters fire, only while e is high."""
    n = Netlist(rng)
    n.eye = ["e", "e"]
    switch(n, "m0", "g", "b", ct, rg1, rg2, rsh)
    n.R("vdd", "e", r1)
    n.C("e", "0", ce)
    n.R("e", "m0", rf)
    n.R("e", "m1", rp)
    n.D("m1", "m0")
    return n

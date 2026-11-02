"""sepb.py: circuit B at Sepulchre's level (QUESTIONS.md, the plan): leaky nodes and saturating elements, events from
fast positive feedback, under the minimal line's rules "mixed" (every node leaky but memory nodes, no clamps), judged
by its simulator (noise, mismatch), its parts and power as chip.py builds it in SKY130."""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from units import V_TYP

G, P = 1e9, 1e-12
n_ = 1e-9


def spec(**k):
    """B's blocks; k overrides any number by name."""
    d = dict(c_eye=2e-12, r_eye=20 * G, c_t=2e-12, r_t=20 * G,
             c_hd=2.5e-12, r_hd=74 * G, g_f=0.15 * n_, g_p=0.3 * n_,
             c_bt=50e-12, r_bt=74 * G, g_bt=0.4 * n_, v_bored=-0.40,
             c_dor=1e-12, r_dor=20 * G, g_dor=0.06 * n_,
             c_x=1e-12, r_x=74 * G, g_xp=0.36 * n_, tau_xp=1.3e-3, g_xs=0.7 * n_, tau_xs=0.25, g_xd=1.0 * n_, tau_xd=0.055,
             c_mb=0.5e-12, r_mb=10 * G, g_mb=0.25 * n_,
             c_dq=2.5e-12, g_dq=0.03 * n_, g_dqf=0.03 * n_, v_h=0.576, v_l=-0.705,
             c_fl=0.5e-12, r_fl=20 * G, g_ft=0.15 * n_, g_fp=0.06 * n_, g_fn=-0.5 * n_, tau_fl=0.02, g_rs=0.2 * n_,
             c_ql=2.5e-12, r_ql=74 * G, g_ql=0.05 * n_, g_tg=-0.4 * n_, q0=0.6)
    d.update(k)
    names = []
    nodes = []

    def node(name, R, C, rest=-0.6, start=None, memory=False):
        bias = 0.0 if R is None else rest / R
        names.append(name)
        nodes.append([name, bias, R, C, None, None, start, memory])
        return len(names) - 1

    S0 = node("S0", d["r_eye"], d["c_eye"])
    S1 = node("S1", d["r_eye"], d["c_eye"])
    T = node("T", d["r_t"], d["c_t"], rest=0.0)
    q = node("q", None, 2.5e-12, start=d["q0"], memory=True)
    qn = node("qn", 20 * G, 1e-12, rest=0.0)
    HD = node("HD", d["r_hd"], d["c_hd"])
    BT = node("BT", d["r_bt"], d["c_bt"])
    DOR = node("DOR", d["r_dor"], d["c_dor"])
    X = node("X", d["r_x"], d["c_x"], rest=0.0)
    MB = node("MB", d["r_mb"], d["c_mb"])
    DQ = node("DQ", None, d["c_dq"], start=d["v_l"], memory=True)
    FL = node("FL", d["r_fl"], d["c_fl"])
    QL = node("QL", d["r_ql"], d["c_ql"], rest=0.0)
    el = []

    def e(to, frm, gain, offset=0.0, slope=20.0, tau=0.0, sigmoid=True, gate=-1):
        el.append([to, frm, gate, gain, offset, slope, tau, sigmoid])

    e(qn, q, -0.06 * n_, 0.0, 10.0, sigmoid=False)      # qn = -q
    e(HD, q, d["g_f"], 0.0, gate=S0)                    # food seen (by the eye the bit says): the hold charged
    e(HD, qn, d["g_f"], 0.0, gate=S1)
    e(HD, q, -d["g_p"], 0.0, gate=S1)                   # poison seen: emptied
    e(HD, qn, -d["g_p"], 0.0, gate=S0)
    e(BT, HD, d["g_bt"], 0.0, gate=HD)                  # boredom: charged while driving, leaks for seconds
    e(DOR, HD, d["g_dor"], 0.0)                         # drive or run
    e(DOR, BT, d["g_dor"], d["v_bored"], -20.0)
    e(X, X, d["g_xp"], 0.0, 13.0, tau=d["tau_xp"], sigmoid=False)   # the oscillator: fast positive feedback,
    e(X, X, -d["g_xs"], 0.0, 13.0, tau=d["tau_xs"], sigmoid=False)  # slow negative (the scan's beat),
    e(X, X, -d["g_xd"], 0.0, 13.0, tau=d["tau_xd"], sigmoid=False, gate=DOR)  # faster while driving or running
    e(MB, X, d["g_mb"], 0.0, 13.0, sigmoid=False, gate=DOR)     # motor B: the beat, while driving or running
    e(DQ, T, d["g_dq"], -0.3, -20.0)                    # doubt: up for a poison,
    e(DQ, T, -d["g_dqf"], 0.3, 20.0)                    # down for a food
    e(FL, DQ, d["g_ft"], d["v_h"], 26.0)                # the flip: doubt at its threshold triggers a monostable
    e(FL, FL, d["g_fp"], 0.0, 8.0)
    e(FL, FL, d["g_fn"], 0.3, 20.0, tau=d["tau_fl"])
    e(DQ, DQ, -d["g_rs"], d["v_l"], 10.0, sigmoid=False, gate=FL)   # which resets doubt to trust
    e(QL, q, d["g_ql"], 0.0, 10.0, sigmoid=False)       # a slow copy of the bit,
    e(q, QL, d["g_tg"], 0.0, 10.0, sigmoid=False, gate=FL)          # against which the flip writes it
    return {"nodes": nodes, "elements": el, "sensors": [S0, S1], "motors": [X, MB], "taste": T, "units": "SI",
            "volt": V_TYP, "rules": "mixed"}, names


if __name__ == "__main__":
    from minimal.spec import violations, parts, slew
    s, names = spec()
    print("violations:", violations(s))
    print("parts:", parts(s), "slew", round(slew(s), 2))

"""afo.py: the period of what comes round again, found by entraining (BOUNDS.md, Time: learning to dance; discrete/
NOTEBOOK.md, D20 needed a delay line and 192 counters). An oscillator per motor, its phase pulled towards 0 by each
eye pulse in a sweep and its frequency nudged the same way (an adaptive-frequency oscillator: Righetti, Buchli and
Ijspeert 2006; for pulses, a phase-locked loop), while its frequency creeps up from too slow: the first lock from
below is the fundamental, since a multiple lies above it.

    python afo.py collect [seeds=0:32]     # D20's sweeps (8 s every 32 s, never stopping) from lopsided lives
    python afo.py test k=v ...             # the oscillator on them: its balance against the right one
"""
import pickle
import sys
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
V = "/home/pilgrim/git/simple-learner/lab/v"


def collect(job):
    import periodbal as PB
    seed, poison, seconds = job
    p, spread = PB.M.from_bench()
    p = dict(p, cal_every=32.0, cal_len=8.0, need=3000, every=20.0)
    sweeps = []
    orig = PB.PeriodBal._close

    def close(self, scan=False):
        if self.in_sweep and not scan:
            sweeps.append((self.sm, self.start, self.t, list(self.ep)))
        orig(self, scan)
    PB.PeriodBal._close = close
    l = PB.life(("learn", p, spread, seed, seconds, poison))
    return {"seed": seed, "poison": poison, "right": l.right, "x_hist": l.x, "sweeps": sweeps}


def run(sweeps, p):
    """Each motor's period, by its own oscillator over that motor's sweeps in order; and the trace."""
    w = {0: 2 * np.pi / p.get("T0", 4.0), 1: 2 * np.pi / p.get("T0", 4.0)}
    K, Kw, up, merge = p.get("K", 0.3), p.get("Kw", 0.05), p.get("up", 0.02), p.get("merge", 0.05)
    wmax = 2 * np.pi / p.get("Tmin", 0.3)
    for m, t0, t1, ep in sweeps:
        ev = []
        for v in ep:                                    # a pass, not a pulse
            if not ev or v - ev[-1] >= merge:
                ev.append(v)
        phi, t = 0.0, t0
        for v in ev + [t1]:
            dt = v - t
            phi += w[m] * dt
            w[m] = min(w[m] * np.exp(up * dt), wmax)    # creeping up, relative (so slow at any period)
            t = v
            if v < t1:
                s = np.sin(phi)
                phi -= K * s
                w[m] -= Kw * w[m] * s
    return 2 * np.pi / w[0], 2 * np.pi / w[1]


if __name__ == "__main__":
    cmd = sys.argv[1]
    kv = dict(a.split("=") for a in sys.argv[2:] if "=" in a)
    if cmd == "collect":
        from concurrent.futures import ProcessPoolExecutor
        lo, hi = (int(x) for x in kv.get("seeds", "0:32").split(":"))
        with ProcessPoolExecutor(7) as ex:
            D = list(ex.map(collect, [(s, c, float(kv.get("seconds", 1000))) for s in range(lo, hi) for c in ("red", "blue")]))
        pickle.dump(D, open(f"{V}/afo_sweeps_{lo}-{hi}.pkl", "wb"))
        xh = np.array([d["x_hist"] for d in D]); r = np.array([d["right"] for d in D])
        print(f"{len(D)} lives, median sweeps {np.median([len(d['sweeps']) for d in D]):.0f}; the histogram's balance:"
              f" within 0.2 {np.mean(abs(xh - r) < 0.2):.0%}, correlation {np.corrcoef(xh, r)[0, 1]:.2f}")
    else:
        D = pickle.load(open(f"{V}/afo_sweeps_{kv.pop('file', '0-32')}.pkl", "rb"))
        p = {k: float(v) for k, v in kv.items()}
        r = np.array([d["right"] for d in D])
        for nsw in (4, 8, 16, 32):
            x = np.array([np.log(np.divide(*run(d["sweeps"][:nsw], p))) for d in D])
            print(f"{p} first {nsw} sweeps: balance within 0.2 {np.mean(abs(x - r) < 0.2):.0%}, median |error|"
                  f" {np.median(abs(x - r)):.2f}, correlation {np.corrcoef(x, r)[0, 1]:.2f}")

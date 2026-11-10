"""body_knob.py: how fast do the knob-turning learners we already have find the balance of unequal thrusters (D42)? The starting brain,
the same told its balance, the bank's learner (D19: wobble the balance each drive, keep what kept the block in view; it wobbles only
while eating badly) and D36's learner that sizes its own steps (lab/rprop.py SZ). Lives of 100, 300 and 1000 s, judged on the last third.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 BELIEF=... PREDICT=... .venv/bin/python lab/body_knob.py [PAIRS]"""
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import bodyladder as BL
import ladders as L
import stage3_random as R


KMAX = 64                                       # the register's length, in the brain's own beats


def beats_cls():
    """D43: D20's measurement made by the generic recording unit of D38, clocked by the brain's own beats. During a sweep (one motor
    alone, as D20) a register takes one cell a beat: did an eye pulse since the last beat? A comparing unit per look-back k counts the
    beats on which this cell and the one k back both pulsed, against chance (the pulsed share squared). What the eyes see comes round
    once a revolution, so the best look-back is that motor's beats per revolution, which goes as 1 / its thruster's strength; the
    balance knob is set to the log of the two motors' ratio. No clock, no time base: the beats are the ruler. The sweeps' timing,
    gating and stalling are D20's (lab/periodbal.py), unchanged."""
    import table as T

    class Beats(T.SweepsC):
        def __init__(self, seed, p):
            super().__init__(seed, p)
            self.A = [np.zeros(KMAX + 1), np.zeros(KMAX + 1)]
            self.Z = [np.zeros(KMAX + 1), np.zeros(KMAX + 1)]
            self.cells, self.flag = [], 0

        def stimulate(self, sensor, at):
            super().stimulate(sensor, at)
            if self.in_sweep:
                self.flag = 1

        def step(self):
            out = super().step()
            if self.in_sweep and self.t <= self.cal_until:
                for _ in out:
                    self.cells.append(self.flag)
                    self.flag = 0
            return out

        def _close(self, scan=False):
            if not scan and len(self.cells) > 4:
                c = np.array(self.cells, float)
                q = c.mean()
                for k in range(1, min(KMAX, len(c) - 1) + 1):
                    self.A[self.sm][k] += float((c[k:] * c[:-k]).sum())
                    self.Z[self.sm][k] += (len(c) - k) * q * q
                self.n[self.sm] += int(c.sum() * (c.sum() - 1) / 2)
            self.cells, self.flag, self.ep = [], 0, []

        def _fund(self, h, null, var=None, **kw):
            m = 0 if h is self.h[0] else 1
            E = self.A[m] - self.Z[m]
            Ts = np.arange(6.0, KMAX / 1.5, 0.25)

            def comb(T):
                js = [j * T for j in range(1, 5) if j * T <= KMAX]
                return float(np.mean([np.interp(x, np.arange(KMAX + 1), E) for x in js]))
            v = np.array([comb(T) for T in Ts])
            if v.max() <= 0:
                return 20.0
            return float(Ts[np.argmax(v >= self.p.get("top", 0.84) * v.max())])     # the shortest that recurs
    return Beats


_B = {}


def job(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    arm, seed, first, secs = j
    text = BL.WORLDS["thr"][0]
    if arm == "beats":
        from stage2_lang.sim import WLife
        from stage2_lang.seconds import seconds_cls
        import table as T
        from table_rows import SWEEP
        if "c" not in _B:
            _B["c"] = seconds_cls(beats_cls())
        q = T.numbers(seed, dict(SWEEP, sync=1))
        lf = WLife(seed, first, (lambda s: _B["c"](s, q)), S.world_of(text), seconds=True)
    elif arm == "sweeps":                                 # D20's learner as the interventions table ran it (lab/table_rows.py SWEEP, 192 counters)
        from stage2_lang.sim import WLife
        from stage2_lang.seconds import seconds_cls
        import table as T
        from table_rows import SWEEP
        q = T.numbers(seed, dict(SWEEP, bank=192.0, sync=1))
        lf = WLife(seed, first, (lambda s: seconds_cls(T.SweepsC)(s, q)), S.world_of(text), seconds=True)
    elif arm == "sized":
        import adaptive as A
        import rprop as RP
        lf = A.make(S.world_of(text), seed, first, {"n_max": 10 ** 9, "Dmax": 0.3}, cls=RP.SZ)
    else:
        lf = BL.make(text, arm, seed, first)
    l = S.live(lf, secs)
    g = [a - COST * b for a, b, _ in l]
    sp = spent(l)
    return (sum(g), sp, g[2], sp * l[2][2] / sum(t for _, _, t in l))


if __name__ == "__main__":
    import ledger
    ledger.start()
    pairs = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    I = R.boot(pairs)
    seeds = range(BL.SEEDS0, BL.SEEDS0 + pairs)
    print(f"== unequal thrusters, {pairs} pairs, seeds {BL.SEEDS0}+: efficiency in the last third [95%]", flush=True)
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        arms = sys.argv[2].split(",") if len(sys.argv) > 2 else ("circuit", "toldbody", "bank", "sized")
        for secs in (100, 300, 1000):
            line = f" {secs:5d} s |"
            for arm in arms:
                res = list(ex.map(job, [(arm, s, c, float(secs)) for s in seeds for c in L.COL]))
                g, sp = np.array([x[2] for x in res]), np.array([x[3] for x in res])
                b = g[I].sum(1) / sp[I].sum(1)
                line += f" {arm} {g.sum() / sp.sum():+.2f} [{np.percentile(b, 2.5):+.2f},{np.percentile(b, 97.5):+.2f}] |"
            print(line, flush=True)

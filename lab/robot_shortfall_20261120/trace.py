"""D176: where does the designed circuit's robot shortfall come from? A passive capture on unmodified creature.Life
lives (body, world, interface unchanged): the designed circuit (brains/designed.py, 10% mismatch, biology's noise)
with a recording wrapper. Arms on the same lives (seed, poison colour):
  learn     the brain as it is
  frozen    taste withheld (Life's learning=False): its P knobs stay where noise and their writers' rest currents take them
  informed  taste withheld, each P set at birth to the right answer (food's sensor 1, poison's 0). PRIVILEGED: it is
            told the body's wiring and the poison colour. A reference for what action can do with a perfect knob
  allfood   both colours food, learning on (the control: nothing to learn)
  held      as informed, but each P clamped at that value for the whole life (its node's lo = hi). PRIVILEGED as
            informed, and a diagnostic switch no brain may use: the ruler for what action can do with a perfect knob
Per tick it keeps E0, E1, P0, P1 (the eligibility and knob voltages) and the spikes of S0, S1, M0, M1; every body pulse
(time, sensor) and every meal (tick, colour). Analyst accounting only; nothing here feeds back into a life.
python trace.py <arm>[-mem] <lives> <seconds> [half]   (half: the integration step halved, mixed_feedback.DT / 2;
-mem: the repair tested in D176, each P built as a memory node, noisy only when written, as AGENTS.md's circuit-brain
rule "a knob is a memory node" requires; nothing else changed; -mem-thr: also the existing-knob repair, the two
writers' thresholds on the taste node raised from +-0.5 to +-THR V, nothing else changed)
"""
import json, os, pickle, sys, time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "lab/v/robot_shortfall_20261120"
BIG = Path.home() / "nca-scratch-backup/robot_shortfall_20261120"     # full per-tick traces (large, out of git)


THR = 0.8   # V: the raised writer threshold (-thr arms); the taste node peaks near 1.3 V, mismatch moves offsets ~0.1 V


def make_brain(mem=False, thr=False):
    from brains.designed import DesignedBrain

    class Logged(DesignedBrain):
        def build(self, c):
            node, element = c.node, c.element
            if mem:                                     # each P (no leak) a memory node: noisy only when written
                c.node = lambda name, *a, **k: node(name, *a, **dict(k, memory=name.startswith("P")))
            if thr:                                     # the writers from the taste node into P: threshold +-THR
                def el(to, frm, gain, offset, *a, **k):
                    if c.names[to].startswith("P") and frm == self.taste_node:
                        offset = THR if offset > 0 else -THR
                    return element(to, frm, gain, offset, *a, **k)
                c.element = el
            super().build(c)
            c.node, c.element = node, element

        def __init__(self, seed):
            super().__init__(seed)
            self.tick, self.pulses, self.rows = 0, [], []
            from units import TICK
            self.TICK = TICK

        def stimulate(self, sensor, at):
            self.pulses.append((self.tick * self.TICK + at, int(sensor)))
            super().stimulate(sensor, at)

        def _tick(self):
            spikes = super()._tick()
            V = self.circuit.V
            self.rows.append((V[self.E[0]], V[self.E[1]], V[self.P[0]], V[self.P[1]],
                              spikes[self.sensors[0]], spikes[self.sensors[1]], spikes[self.motors[0]],
                              spikes[self.motors[1]]))
            self.tick += 1
            return spikes
    return Logged


def one(job):
    arm, seed, poison, seconds, half = job
    thr = arm.endswith("-thr")
    arm = arm.removesuffix("-thr")
    mem = arm.endswith("-mem")
    arm = arm.removesuffix("-mem")
    import mixed_feedback as mf
    if half > 1:
        from units import DT
        mf.DT = DT / half
    from creature import Life
    from units import TICK
    Logged = make_brain(mem, thr)
    life = Life(seed, None if arm == "allfood" else poison, arm in ("learn", "allfood"), Logged)
    b = life.brain
    if arm in ("informed", "held"):
        food = "blue" if poison == "red" else "red"
        b.circuit.start[b.P[life.sensor[food]]] = 1.0
        b.circuit.start[b.P[life.sensor[poison]]] = 0.0
        if arm == "held":
            for P in b.P:
                v = b.circuit.start[P]
                bias, R, C, lo, hi, m = b.circuit.nodes[P]
                b.circuit.nodes[P] = (bias, R, C, v, v, m)
    n = int(round(seconds / TICK))
    while life.t < n:
        life.step()
    return dict(arm=arm, mem=mem, thr=thr, seed=seed, poison=poison, seconds=seconds, half=half, sensor=dict(life.sensor),
                motor=dict(life.motor), moving=life.moving, meals=list(life.meals),
                rows=np.array(b.rows, dtype=np.float32), pulses=np.array(b.pulses, dtype=np.float64).reshape(-1, 2))


def main():
    arm, lives, seconds = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
    half = {"half": 2, "quarter": 4}.get(sys.argv[4], 1) if len(sys.argv) > 4 else 1
    import multiprocessing
    from concurrent.futures import ProcessPoolExecutor
    jobs = [(arm, i // 2, ("red", "blue")[i % 2], seconds, half) for i in range(lives)]
    start = time.monotonic()
    with ProcessPoolExecutor(7, mp_context=multiprocessing.get_context("spawn")) as pool:
        res = list(pool.map(one, jobs))
    BIG.mkdir(parents=True, exist_ok=True)
    tag = f"{arm}_{lives}x{int(seconds)}s{ {1: '', 2: '_half', 4: '_quarter'}[half] }"
    with (BIG / f"{tag}.pkl").open("wb") as f:
        pickle.dump(res, f)
    print(tag, "done", round(time.monotonic() - start, 1), "s", flush=True)


if __name__ == "__main__":
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    main()

"""rhythm.py: a rhythm tracker designed from theory, run offline on noticed change times (lab/v/change_times.pkl; 2026-11-15, D68).
Acquisition (a bank of resonators across slot lengths 3 to 30 s: each a forgetting circular mean of change times at its trial period;
the longest period resonating nearly as well as the best is taken, since a lattice of changes also resonates at its fractions), then
tracking (a Kalman filter on phase and slot rate, Gardner's type-2 loop with optimal gains; a validation gate drops changes far from a
slot boundary: Bar-Shalom). Scored causally: at each meal, the tracker's count of slots against the world's; place purity = the share of
meals at the commonest offset between the two counts (1: the place never slips).
    .venv/bin/python lab/rhythm.py [describe]"""
import math
import pickle
import sys
from collections import Counter

import numpy as np

D = pickle.load(open("/home/pilgrim/git/simple-learner/lab/v/change_times.pkl", "rb"))


def describe():
    for r in D:
        tau, ph = r["tau"], r["ph"]
        f = np.array([((c + ph) % tau) / tau for c in r["changes"]])
        print(f"rung {r['rung']} seed {r['seed']}: slot {tau:5.2f} s; noticed changes {len(f)} ({len(f) / (r['secs'] / tau):.2f} a slot); "
              f"place in slot: median {np.median(f):.2f}, within the first half {np.mean(f < .5):.2f}, quartiles {np.percentile(f, 25):.2f} "
              f"to {np.percentile(f, 75):.2f}")


class Tracker:
    """Acquire then track. State: phase th (slots, a real number whose integer part counts slots) and rate f (slots a second)."""
    GRID = np.exp(np.linspace(np.log(3.0), np.log(30.0), 120))
    LAM = 0.98                                          # the resonators' forgetting a change

    def __init__(self, q_f=1e-8, r_ph=0.04, gate=0.3, acquire_after=30):
        self.z = np.zeros(len(self.GRID), complex)
        self.n = 0
        self.locked = False
        self.q_f, self.r_ph, self.gate, self.acq = q_f, r_ph, gate, acquire_after

    def change(self, t):
        self.n += 1
        if not self.locked:
            self.z = self.LAM * self.z + np.exp(2j * np.pi * t / self.GRID)
            if self.n >= self.acq:
                R = np.abs(self.z) / ((1 - self.LAM ** self.n) / (1 - self.LAM))
                good = np.where(R >= 0.9 * R.max())[0]
                T = float(self.GRID[good.max()])
                self.f = 1.0 / T
                self.th = (np.angle(self.z[good.max()]) / (2 * np.pi)) * -1 + t / T   # phase so changes sit near integers
                self.th = t / T - (t / T - round(t / T)) + ((t / T) % 1.0) * 0      # start counting from this change's slot
                self.th = round(t / T)
                self.tl = t
                self.P = np.diag([0.05, (0.02 * self.f) ** 2])
                self.locked = True
            return
        dt = t - self.tl
        self.tl = t
        F = np.array([[1.0, dt], [0.0, 1.0]])
        x = np.array([self.th + self.f * dt, self.f])
        self.P = F @ self.P @ F.T + np.diag([0.0, self.q_f * dt])
        e = x[0] - round(x[0])                          # innovation: the change should sit at a whole number of slots
        S_ = self.P[0, 0] + self.r_ph
        if abs(e) > self.gate:                          # a validation gate: a change far from any boundary is taken as false
            self.th, self.f = x
            return
        K = self.P[:, 0] / S_
        x = x - K * e
        self.P = self.P - np.outer(K, self.P[0, :])
        self.th, self.f = float(x[0]), float(x[1])

    def place(self, t):
        if not self.locked:
            return None
        return math.floor(self.th + self.f * (t - self.tl))


class Bank:
    """Acquisition spawns a tracker at each distinct resonance peak (local maxima of the resonators' strength at least half the best,
    periods more than 10% apart, up to K); each then tracks on its own (the user, 2026-11-15: one for each nested rhythm, the bits to
    decide which is kept)."""

    def __init__(self, K=4, acquire_after=40, **kw):
        self.z = np.zeros(len(Tracker.GRID), complex)
        self.n, self.K, self.acq, self.kw = 0, K, acquire_after, kw
        self.tr = []

    def change(self, t):
        self.n += 1
        if not self.tr:
            self.z = Tracker.LAM * self.z + np.exp(2j * np.pi * t / Tracker.GRID)
            if self.n >= self.acq:
                R = np.abs(self.z)
                peaks = [i for i in range(1, len(R) - 1) if R[i] >= R[i - 1] and R[i] >= R[i + 1] and R[i] >= 0.5 * R.max()]
                peaks.sort(key=lambda i: -R[i])
                chosen = []
                for i in peaks:
                    if all(abs(Tracker.GRID[i] / Tracker.GRID[j] - 1) > 0.1 for j in chosen):
                        chosen.append(i)
                    if len(chosen) == self.K:
                        break
                for i in chosen:
                    T = float(Tracker.GRID[i])
                    x = Tracker(**self.kw)
                    x.locked, x.f, x.th, x.tl = True, 1.0 / T, float(round(t / T)), t
                    x.P = np.diag([0.05, (0.02 / T) ** 2])
                    self.tr.append(x)
            return
        for x in self.tr:
            x.change(t)


def purity_by_symbol(syms, places):
    """How well a symbol fixes the world's place: the share of moments at their symbol's commonest place."""
    by = {}
    for a, b in zip(syms, places):
        by.setdefault(a, Counter())[b] += 1
    return sum(c.most_common(1)[0][1] for c in by.values()) / max(len(syms), 1)


def score_bank(r, **kw):
    tau, ph, n = r["tau"], r["ph"], r["rung"]
    bk = Bank(**kw)
    ch = list(r["changes"])
    i = 0
    rec = []
    for t in r["meals"]:
        while i < len(ch) and ch[i] <= t:
            bk.change(ch[i])
            i += 1
        if bk.tr and t > r["secs"] / 3:
            rec.append((t, [x.th + x.f * (t - x.tl) for x in bk.tr], math.floor((t + ph) / tau) % n))
    best = (0.0, None, None)
    for j, x in enumerate(bk.tr):
        for m in range(2, 9):
            syms = [int(math.floor(5 * th[j])) % (5 * m) for _, th, _ in rec]
            p = purity_by_symbol(syms, [pl for _, _, pl in rec])
            if p > best[0]:
                best = (p, (1.0 / x.f) / tau, m)
    chance = Counter(pl for _, _, pl in rec).most_common(1)[0][1] / max(len(rec), 1) if rec else 0
    return best, [round((1.0 / x.f) / tau, 4) for x in bk.tr], chance


def score(r, **kw):
    tau, ph, n = r["tau"], r["ph"], r["rung"]
    tr = Tracker(**kw)
    ch = list(r["changes"])
    i = 0
    offs = []
    for t in r["meals"]:
        while i < len(ch) and ch[i] <= t:
            tr.change(ch[i])
            i += 1
        p = tr.place(t)
        if p is not None and t > r["secs"] / 3:
            offs.append((p - math.floor((t + ph) / tau)) % n)
    pur = Counter(offs).most_common(1)[0][1] / len(offs) if offs else 0.0
    return pur, (1.0 / tr.f) / tau if tr.locked else float("nan")


if __name__ == "__main__":
    if "describe" in sys.argv:
        describe()
    elif "bank" in sys.argv:
        ps = []
        for r in D:
            (p, ratio, m), ratios, chance = score_bank(r, q_f=1e-11)
            ps.append(p)
            print(f"rung {r['rung']} seed {r['seed']}: trackers' slot / world's {ratios}; best place purity {p:.2f} (by tracker at "
                  f"{ratio:.4f}, cycle {m}); chance {chance:.2f}")
        print(f"mean best purity {np.mean(ps):.2f}")
    else:
        for r in D:
            pur, ratio = score(r)
            print(f"rung {r['rung']} seed {r['seed']}: slot {r['tau']:5.2f} s; tracker's slot / world's {ratio:.4f}; place purity {pur:.2f}")

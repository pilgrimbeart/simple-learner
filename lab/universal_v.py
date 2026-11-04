"""universal_v.py: H4, a bank of predictors (discrete/NOTEBOOK.md, D29; STORIES.md). Every vouched taste says which colour was food (the one followed if
good, the other if bad), so every candidate model of what the taste means can be scored on every taste without ever being acted on: no trial, no cost.

A model is a table of n bits, position the count of goods mod n, each with a tally of depth `trust`: n=1, trust=1 is story 1's circuit, always the default.
Each other model holds evidence E: +1 when it predicted the taste and the default did not, -1 the reverse, clipped to 0..Emax. The creature follows the model
with most evidence once past theta. Evidence moves only where models disagree, so nothing moves in a world that suits the default.
The pause is one more model, of the taste's timing: predicting bad soon after a taste. Its evidence is +1 a soon bad, -down a soon good, -late a late bad.
Eyes and balance are U's: they aren't about what the taste means, so no prediction can score them.

    python lab/universal_v.py eval [k=v ...]
    python lab/universal_v.py search N [k=v ...]"""
import json
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import numpy as np
import table as T
import universal as X
from table_rows import VALID


NS, TRUSTS = (1, 2, 3, 6), (0, 1, 3)
BANKS = {1: [(1, 0), (1, 3), (2, 0), (3, 0), (6, 0)], 2: [(1, 0), (1, 3), (2, 0), (3, 0)], 3: [(1, 0), (1, 3), (2, 1), (3, 1), (6, 1)], 4: [(1, 0), (1, 3), (2, 0), (3, 0), (2, 3), (3, 3)], 5: [(1, 0), (1, 4), (2, 1), (3, 1), (6, 1)], 6: [(1, 0), (1, 2), (1, 4), (2, 1), (3, 1), (6, 1)], 7: [(1, 3)], 8: [(1, 0), (1, 3)], 9: [(1, 0), (1, 1), (2, 1), (3, 1), (6, 1)], 10: [(1, 1), (2, 1), (3, 1), (6, 1)], 11: [(1, 0), (2, 1), (3, 1), (6, 1)], 12: [(1, 0), (1, 1), (2, 0), (3, 0), (6, 0)], 13: [(1, 0), (2, 3), (3, 3), (6, 3)], 14: [(1, 0), (2, 2), (3, 2), (6, 2)], 19: [(1, 0), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2)]}


class V(X.U):
    def __init__(self, seed, p):
        super().__init__(seed, p)
        self.g = 0
        ns = p.get("ns", NS)
        ts = p.get("ts", TRUSTS)
        rivals = BANKS.get(int(p.get("bk", 0))) or [(n, t) for n in ns for t in ts if (n, t) != (1, 1)]
        self.bank = [dict(n=1, trust=int(p.get("d", 1)))] + [dict(n=n, trust=t) for n, t in rivals]
        for m in self.bank:
            m.update(bits=[self.food] * m["n"], tally=[0] * m["n"], E=0.0)
        self.act = 0
        self.picks = []

    def pred(self, m):
        return m["bits"][self.g % m["n"]]

    def choose(self):
        p = self.p
        best = max(range(len(self.bank)), key=lambda i: (self.bank[i]["E"], -i))
        need = p.get("theta", 2.0) + (p.get("theta_n", 0.0) if self.bank[best]["n"] > 1 else 0.0)
        if self.bank[best]["E"] >= need and self.bank[best]["E"] >= self.bank[self.act]["E"] + p.get("hyst", 1.0) and best != self.act:
            self.act = best
            self.picks.append((self.t, best))
            if self.bank[best]["n"] > 1:
                self.grew.append((self.t, self.bank[best]["n"]))
        elif self.act and self.bank[self.act]["E"] < p.get("theta_off", 1.0):
            self.act = 0
            self.picks.append((self.t, 0))

    def taste(self, value, at):
        p = self.p
        gap = self.t - self.ate_at
        self.ate_at = self.t
        if value > 0:
            self.rate += 1.0
        if self.open:
            if value < 0:
                self.open = False
                self.food = 1 - self.recent
                for m in self.bank:
                    m["bits"] = [self.food] * m["n"]
            return
        soon = gap < max(p.get("win_p", 1.2), self.est * p.get("stair", 0.0) if self.pausing else 0.0)
        if self.vouched():
            # the pause's evidence
            if p.get("pausek", 1):
                if soon:
                    if value < 0:
                        self.P = min(p.get("mtop", 4.0), self.P + 1.0)
                        if self.pausing and p.get("stair", 0.0):     # a staircase: a bad near the pause's end lengthens it, a good shortens it
                            self.est *= 1 + p.get("up", 0.1)
                        else:
                            self.est = max(self.est, gap * p.get("margin_p", 1.2))
                    else:
                        self.P = max(0.0, self.P - p.get("down", 1.0))
                        if self.pausing:
                            self.est *= p.get("shrink", 0.98)
                elif value < 0:
                    self.P = max(0.0, self.P - p.get("late", 1.0))
            # each model's evidence, then its own learning. A soon taste while pausing says nothing of colours.
            if not (self.pausing and gap < (self.est if p.get("stair", 0.0) else p.get("win_p", 1.2))):
                truth = self.food if value > 0 else 1 - self.food
                base_hit = self.pred(self.bank[0]) == truth
                for i, m in enumerate(self.bank):
                    c = self.g % m["n"]
                    hit = m["bits"][c] == truth
                    if i and p.get("bankk", 1):
                        m["E"] = float(np.clip(m["E"] + (1.0 if hit > base_hit else -p.get("pen", 1.0) if hit < base_hit else 0.0), 0.0, p.get("Emax", 6.0)))
                    if hit:
                        m["tally"][c] = max(-m["trust"], m["tally"][c] - 1)
                    else:
                        m["tally"][c] += 1
                        if m["tally"][c] >= 1:
                            m["bits"][c], m["tally"][c] = 1 - m["bits"][c], 0
                            if i == self.act:
                                self.flips.append(self.t)
        if value > 0:
            self.g += 1
        self.choose()
        self.food = self.pred(self.bank[self.act])


    def step(self):
        tau = self.p.get("tau_E", 0.0)
        if tau:
            for m in self.bank:
                m["E"] *= 1 - T.TICK / tau
        return super().step()


T.ARMS["v"] = V
WORLDS = [w for w in X.BEST if w not in T.LONG]


def score(kw, seeds):
    seeds = list(seeds)
    R = {}
    for w in WORLDS:
        B, L = X.base(w, seeds, 100.0), T.run(w, "v", seeds, kw, 100.0)
        R[w] = (X.efficiency(L) - X.efficiency(B)) / max(X.BEST[w] - X.JUDGED[w], 0.2)
    P = T.run("plain", "v", seeds, kw)
    d = T.paired(P, X.base("plain", seeds, 100.0))[0]
    r = np.array([np.clip(v, -1.0, 1.2) for v in R.values()])
    return float(r.mean() + 0.5 * r.min() + 3 * min(0.0, d)), R, d


def draw(r):
    c = lambda *v: float(r.choice(v))
    return dict(theta=c(1, 2, 3, 4), theta_n=c(0, 1, 2, 3), hyst=c(0, 1, 2), Emax=c(4, 6, 10), theta_off=c(0.5, 1, 2), tau_E=c(0, 100, 300),
                theta_p=c(2, 3, 4), down=c(0.5, 1, 2), late=c(0.5, 1, 2), mtop=c(4, 6), tau_hold=c(150, 300, 600), tau_p=c(30, 60, 150), off=c(0.5, 1), margin_p=c(1.1, 1.2, 1.4), win_p=c(1.2, 1.5))


def search(n, fixed):
    r = np.random.default_rng(31)
    res = []
    for j in range(n):
        kw = {**FIX, **draw(r), **fixed}
        s, R, d = score(kw, T.TRAIN)
        res.append((s, kw))
        print(f"{j} score {s:.3f} plain {d:+.3f} allfood +0 " + " ".join(f"{w[:4]} {v:.2f}" for w, v in R.items()) + " " + json.dumps(kw), flush=True)
    res.sort(key=lambda x: -x[0])
    finals = sorted(((score(kw, VALID)[0], json.dumps(kw)) for _, kw in res[:6]), reverse=True)
    for s, k in finals:
        print(f"validation {s:.3f} {k}", flush=True)
    return finals[0][1]


FIX = {"learn": 1.0, "win": 200.0, "gate": 15.0, "margin_e": 3.0}

if __name__ == "__main__":
    cmd, *rest = sys.argv[1:]
    if cmd == "eval":
        kw = {"learn": 1.0, "win": 200.0, **X.parse(rest)}
        print(json.dumps(kw), flush=True)
        print("score", X.scores(kw, verbose=True, arm="v")[0], flush=True)
    elif cmd == "focus":                # focus FILE w1,w2 k=v,k=v k=v ...: each variant on all 48 tuning seeds
        kw0 = json.load(open(rest[0]))
        ws = rest[1].split(",")
        seeds = list(T.TRAIN) + list(VALID)
        for var in rest[2:]:
            kw = {**kw0, **(X.parse(var.split(",")) if var != "-" else {})}
            out = []
            for w in ws:
                L, B = T.run(w, "v", seeds, kw, T.LONG.get(w, 100.0)), X.base(w, seeds, T.LONG.get(w, 100.0))
                d, i = T.paired(L, B)
                out.append(f"{w[:5]} {X.efficiency(L):.2f} {d:+.2f}[{i[0]:+.2f},{i[1]:+.2f}] g{np.mean([bool(l.grew) for l in L]):.2f} p{np.mean([bool(l.on) for l in L]):.2f}")
            print(var, "| " + " | ".join(out), flush=True)
    elif cmd == "search":
        print("best", search(int(rest[0]), X.parse(rest[1:])), flush=True)

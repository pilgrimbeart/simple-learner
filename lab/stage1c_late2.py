"""stage1c_late2.py: additions to part 3 after reading its log. (1) Paired contrasts from the saved per-life arrays: the bank's floor at 0 against each deeper floor, by group and T, on the whole life and after T; fixed share against the stationary vote. (2) Which hazard each mid-life world's stream supports, in bits, on the bank's streams. (3) Fixed share at the setting that resembled the bank (h .1, e .2, pi .5, MAP), which part 3 didn't run: its setting came from the stationary worlds, h .003.
    .venv/bin/python lab/stage1c_late2.py"""
import pickle
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import numpy as np
import stage1c_arms as A
import stage1c_change as C
import bits_analyse as BA
import bits_bank as B

SEEDS = range(62000, 62200)
out = pickle.load(open(A.OUT + "late.pkl", "rb"))
stat = pickle.load(open(A.OUT + "late_stat.pkl", "rb"))
I = A.resample(400, 2000)


def diff(ws, a, b, key="g"):
    d = []
    pts = []
    for w in ws:
        if w in stat:
            ga, sa = stat[w][a]
            gb, sb = stat[w][b]
        elif key == "g":
            ga, sa, gb, sb = out[w][a]["g"], out[w][a]["s"], out[w][b]["g"], out[w][b]["s"]
        else:
            ga, sa, gb, sb = out[w][a]["a"][:, 0], out[w][a]["a"][:, 1], out[w][b]["a"][:, 0], out[w][b]["a"][:, 1]
        d.append(ga[I].sum(1) / sa[I].sum(1) - gb[I].sum(1) / sb[I].sum(1))
        pts.append(ga.sum() / sa.sum() - gb.sum() / sb.sum())
    d = np.mean(d, axis=0)
    lo, hi = np.percentile(d, [2.5, 97.5])
    return f"{np.mean(pts):+.3f} [{lo:+.3f},{hi:+.3f}]{' SURE' if lo > 0 or hi < 0 else ''}"


GROUPS = {"nine stationary": B.WORLDS9, "after plain, all": [w for w in out if w.startswith("late_")], "after plain, T30": [f"late_{r}_30" for r in ("alternate", "pattern", "swap")], "T50": [f"late_{r}_50" for r in ("alternate", "pattern", "swap")], "T70": [f"late_{r}_70" for r in ("alternate", "pattern", "swap")],
          "after plain, alternate+pattern": [f"late_{r}_{t}" for r in ("alternate", "pattern") for t in (30, 50, 70)], "after plain, one swap": [f"late_swap_{t}" for t in (30, 50, 70)], "lies, all": [w for w in out if w.startswith("nlate_")], "lies, alternate+pattern": [f"nlate_{r}_{t}" for r in ("alternate", "pattern") for t in (30, 70)], "lies, one swap": [f"nlate_swap_{t}" for t in (30, 70)]}
print("== the floor at 0 (the bank) minus each alternative, life efficiency; positive: the floor at 0 pays. Each world equal weight, 95% over seeds. After T where the group is mid-life.", flush=True)
for a, b in (("bank", "+1/-3 no floor"), ("bank", "+1/-3 floor -3"), ("bank", "+1/-3 floor -10"), ("+1/-1 floor 0", "+1/-1 no floor"), ("+1/-1 floor 0", "+1/-1 floor -3"), ("+1/-1 floor 0", "bank"), ("fixed share (2a)", "stationary BMA e.2"), ("stationary BMA e.2", "bank")):
    print(f"-- {a} minus {b}")
    for g, ws in GROUPS.items():
        print(f"   {g:32s} life {diff(ws, a, b)}" + (f"; after T {diff(ws, a, b, 'a')}" if ws[0] not in stat else ""), flush=True)
print("\n== all 24 worlds, the tally's weighting: 9 stationary and 15 mid-life, each world one share, so stationary 37.5%, mid-life 62.5%. The same with the two groups given equal weight, bank minus +1/-3 no floor:", flush=True)
ws1, ws2 = GROUPS["nine stationary"], GROUPS["after plain, all"] + GROUPS["lies, all"]


def dd(ws, a, b):
    return np.mean([(stat[w][a][0][I].sum(1) / stat[w][a][1][I].sum(1) - stat[w][b][0][I].sum(1) / stat[w][b][1][I].sum(1)) if w in stat else (out[w][a]["g"][I].sum(1) / out[w][a]["s"][I].sum(1) - out[w][b]["g"][I].sum(1) / out[w][b]["s"][I].sum(1)) for w in ws], axis=0)


for a, b in (("bank", "+1/-3 no floor"), ("+1/-1 floor 0", "bank"), ("+1/-1 no floor", "bank"), ("stationary BMA e.2", "bank"), ("fixed share (2a)", "bank")):
    v = (dd(ws1, a, b) + dd(ws2, a, b)) / 2
    print(f"   {a} minus {b}: {v.mean():+.3f} [{np.percentile(v, 2.5):+.3f},{np.percentile(v, 97.5):+.3f}]", flush=True)

print("\n== the hazard the mid-life streams support: log2 evidence a life, each h against h = 0, at each world's best e, pi .5; the bank's own streams, 200 seeds x 2", flush=True)
st = pickle.load(open(A.OUT + "late_bank_streams.pkl", "rb"))
HS, ES = C.HS, C.ES
grid = [(h, e, 0.5) for h in HS for e in ES]
for w, L in st.items():
    ev = np.array([C.fs_map(*BA.stream(l)[:2], grid)[1] for l in L])
    bg = int(np.argmax(ev.mean(0)))
    e_best = grid[bg][1]
    ids = [i for i, s in enumerate(grid) if s[1] == e_best]
    row = []
    for i in ids:
        d = ev[:, i] - ev[:, ids[0]]
        v = d[A.resample(len(d), 500)].mean(1)
        row.append(f"h{grid[i][0]:g} {d.mean():+.1f}[{np.percentile(v, 2.5):+.1f},{np.percentile(v, 97.5):+.1f}]")
    print(f"   {w:20s} e {e_best} best h {grid[bg][0]:g}: " + " ".join(row), flush=True)

print("\n== fixed share at the setting that resembled the bank (MAP, h .1, e .2, pi .5), in real lives. Life efficiency against the bank; and after T", flush=True)
kw = dict(h=0.1, eps=0.2, pr=0.5)
res = {}
for w in B.WORLDS9 + list(out):
    L = A.run(w, "fsmap", SEEDS, kw)
    g, s = A.gs(L)
    gb, sb = (stat[w]["bank"] if w in stat else (out[w]["bank"]["g"], out[w]["bank"]["s"]))
    v = g[I].sum(1) / s[I].sum(1) - gb[I].sum(1) / sb[I].sum(1)
    res[w] = v
    print(f"   {w:20s} {g.sum() / s.sum():+.3f}, against bank {g.sum() / s.sum() - gb.sum() / sb.sum():+.3f} [{np.percentile(v, 2.5):+.3f},{np.percentile(v, 97.5):+.3f}]", flush=True)
for g_, ws in GROUPS.items():
    v = np.mean([res[w] for w in ws], axis=0)
    print(f"   {g_:32s} {v.mean():+.3f} [{np.percentile(v, 2.5):+.3f},{np.percentile(v, 97.5):+.3f}]", flush=True)

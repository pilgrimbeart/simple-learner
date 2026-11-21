"""Job F (PROGRAMME after D108): what the design's market (grownet.Net._room) and capped rule M (alloc_rules) do
on tiny synthetic states. Real code paths, no creature, no change to either implementation.
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/market_transfer_cases.py --check
    timeout 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/market_transfer_cases.py --analyse
"""
import hashlib
import json
from pathlib import Path
import pickle
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "lab"), str(ROOT)]
import numpy as np
import grownet as GN
import alloc_rules as A

BASE = ROOT / "lab/v/market_transfer_cases"


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def net(kind, alphabet, seed):
    return GN.Net(kind, alphabet, np.random.default_rng(seed), alphabet=alphabet)


def grow(n, count, chain=False):
    """Add grown units on fixed parents (leaves), or a chain (each built on the previous: only the last is a leaf)."""
    ks = []
    for _ in range(count):
        u = ks[-1] if (chain and ks) else 0
        ks.append(n._add(u, 0, n.units[u]["span"] + 1, 0.0))
    return ks


def fixed(n):
    return sum(x["sym"] is not None for x in n.units.values())


def state(nets):
    return [dict(kind=n.kind, fixed=fixed(n), units=len(n.units), grown=len(n.units) - fixed(n), P=int(n.P),
                 saved=float(getattr(n, "saved", 0.)),
                 leaves=sum(1 for x in n.units.values() if x["sym"] is None and not x["kids"])) for n in nets]


def invariants(nets):
    """Dependencies valid: every grown unit's parents exist and list it as a kid; kids exist."""
    for n in nets:
        for k, x in n.units.items():
            if x["sym"] is None:
                assert x["u"] in n.units and x["v"] in n.units, ("orphan", n.kind, k)
                assert k in n.units[x["u"]]["kids"] and k in n.units[x["v"]]["kids"], ("parent does not list kid", n.kind, k)
            for c in x["kids"]:
                assert c in n.units, ("dangling kid", n.kind, k, c)
    return True


class Market:
    def __init__(self, nets):
        self.nets = nets


def native_case(name, donors, recipient_saved=5.0, recipient_extra=1, price_exact=False, seed=0):
    """Design market: recipient R at its allowance P with extra grown units beyond base; donors as given.
    donors: list of dict(alphabet, P, grown, chain, saved)."""
    R = net("recipient", 2, 100)
    base = 3
    grow(R, base - 2 + recipient_extra)                       # units = base + extra
    R.P = len(R.units)
    R.base = base
    R.saved = GN.POOL_BITS * (len(R.units) - base + 1) if price_exact else recipient_saved
    D = []
    for i, d in enumerate(donors):
        n = net(f"donor{i}", d["alphabet"], 200 + i)
        grow(n, d["grown"], d.get("chain", False))
        n.P, n.base, n.saved = d["P"], d["P"], d["saved"]
        D.append(n)
    nets = [R] + D
    mk = Market(nets)
    for n in nets:
        n.market = mk
    R.rng = np.random.default_rng(seed)                       # the donor draw uses the recipient's own generator
    invariants(nets)
    before = state(nets)
    drawn = predicted_donor(R, nets, "native", [fixed(n) for n in nets], R.rng)
    ok = R._room()
    invariants(nets)
    after = state(nets)
    allocation_invariants(before, after, "native Net._room")
    rec = record("native Net._room", name, nets, before, after, ok, cap=None)
    rec["drawn_donor"] = drawn
    return rec


class FakeBrain:
    def __init__(self, nets):
        self.nets, self.t = nets, 0.


def m_case(name, donors, G, recipient_extra=1, recipient_saved=5.0, fill=True, price_exact=False, seed=0):
    """Capped rule M via alloc_rules.install: allowances fixed + G // streams, cap fixed + G. Growth after install
    goes through the installed _add (cap enforced). fill: donors use their allowances up to the stated grown units."""
    R = net("recipient", 2, 100)
    D = [net(f"donor{i}", d["alphabet"], 200 + i) for i, d in enumerate(donors)]
    nets = [R] + D
    b = FakeBrain(nets)
    st = A.install(b, "M", G, seed)
    g = G // len(nets)
    # recipient: grow to its allowance, then the room request is for one more
    grow(R, R.P - len(R.units))
    R.saved = GN.POOL_BITS * (len(R.units) - R.base + 1) if price_exact else recipient_saved
    for n, d in zip(D, donors):
        grow(n, min(d["grown"], n.P - len(n.units)), d.get("chain", False))
        n.saved = d["saved"]
        if "M_floor" in d:                                    # as if it had already given its budget share away
            n.P = fixed(n)
    deep = next(k for k, x in R.units.items() if x["sym"] is None)
    R.units[deep]["n"] = [1, 1]                               # a birth is due: the deep unit has seen both labels
    R._deep = deep
    invariants(nets)
    before = state(nets)
    used = sum(len(n.units) for n in nets)
    rng = next(c.cell_contents for c in R._room.__closure__ if isinstance(c.cell_contents, np.random.Generator))
    drawn = predicted_donor(R, nets, "M", [fixed(n) for n in nets], rng)
    ok = R._room()
    invariants(nets)
    after = state(nets)
    allocation_invariants(before, after, "capped rule M", st["cap"])
    rec = record("capped rule M", name, nets, before, after, ok, cap=st["cap"])
    rec["drawn_donor"] = drawn
    rec["cap_occupied_before"] = used
    rec["cap_free_before"] = st["cap"] - used
    return rec


def predicted_donor(R, nets, impl, fixed_counts, rng):
    """The donor the native draw selects, from a copy of the generator state (nothing consumed); None if no draw."""
    cands = [i for i, v in enumerate(nets) if v is not R and getattr(v, "saved", 0.) <= 0. and
             (v.P > 3 if impl == "native" else v.P > fixed_counts[i])]
    if not cands or len(R.units) < R.P or R.saved <= GN.POOL_BITS * (len(R.units) - R.base + 1):
        return None
    c = np.random.Generator(type(rng.bit_generator)())
    c.bit_generator.state = rng.bit_generator.state
    return nets[cands[int(c.integers(len(cands)))]].kind


def allocation_invariants(before, after, impl, cap=None):
    """Allowance sum conserved; under capped M also occupancy within every allowance and within the cap."""
    assert sum(s["P"] for s in before) == sum(s["P"] for s in after), "allowance sum changed"
    if impl == "capped rule M":
        assert all(s["units"] <= s["P"] for s in after), "capped M: a stream holds more units than its allowance"
        assert sum(s["units"] for s in after) <= cap, "capped M: total units above the cap"
    return True


def record(impl, name, nets, before, after, ok, cap):
    sumP = (sum(s["P"] for s in before), sum(s["P"] for s in after))
    occ = (sum(s["units"] for s in before), sum(s["units"] for s in after))
    over = [s["kind"] for s in after if s["units"] > s["P"]]
    changed = [(b["kind"], b["P"], a["P"], b["units"], a["units"]) for b, a in zip(before, after) if (b["P"], b["units"]) != (a["P"], a["units"])]
    return dict(implementation=impl, case=name, admitted=bool(ok), allowance_sum=sumP, allowance_sum_conserved=sumP[0] == sumP[1],
                occupancy=occ, removals=occ[0] - occ[1], over_allowance_after=over, changes=changed, before=before, after=after, cap=cap)


CASES = [
    ("a: poor donor, unused allowance, no grown unit", [dict(alphabet=2, P=5, grown=0, saved=-1.)]),
    ("b: poor donor, one removable grown leaf", [dict(alphabet=2, P=5, grown=1, saved=-1.)]),
    ("c: poor donor at its fixed-unit floor", [dict(alphabet=4, P=4, grown=0, saved=-1.)]),
    ("d: poor donor's grown unit has a dependant (chain of 2)", [dict(alphabet=2, P=5, grown=2, chain=True, saved=-1.)]),
    ("f: two candidates, one leafless, one with a leaf", [dict(alphabet=2, P=5, grown=0, saved=-1.), dict(alphabet=2, P=5, grown=1, saved=-1.)]),
]


def run_cases():
    out = []
    for name, donors in CASES:
        out.append(native_case(name, donors))
    out.append(native_case("e: savings exactly at the price", CASES[1][1], price_exact=True))
    for seed in (0, 1, 2, 3):
        out.append(native_case(f"f (seed {seed}): drawn donor recorded", CASES[4][1], seed=seed))
    # capped M: G chosen so each stream's allowance is fixed + 2; fill states vary
    for name, donors in CASES:
        dd = [dict(d, M_floor=True) if name.startswith("c:") else dict(d) for d in donors]
        out.append(m_case(name, dd, G=2 * (len(donors) + 1)))
    out.append(m_case("b': poor donor's allowance full of leaves (total cap fully occupied)",
                      [dict(alphabet=2, P=5, grown=2, saved=-1.)], G=4))
    out.append(m_case("e: savings exactly at the price", CASES[1][1], G=4, price_exact=True))
    for seed in (0, 1, 2, 3):
        out.append(m_case(f"f (seed {seed}): drawn donor recorded", CASES[4][1], G=6, seed=seed))
    return out


def eligibility():
    raw = pickle.loads((ROOT / "lab/v/future_evidence.pkl").read_bytes())["raw"]
    from future_evidence_analysis import family
    fx = [sum(1 for r in ds.values() if r["birth_seq"] == -1) for ds in raw["definitions"]]
    out = {}
    for P in (560, 4480):
        a = max(3, P // 168)
        rows = {}
        for name, f in zip(raw["names"], fx):
            fam = family(name)
            key = f"{fam} (fixed {f})"
            r = rows.setdefault(key, dict(streams=0, allowance=a, fixed=f, eligible_P_gt_3=a > 3, eligible_P_gt_fixed=a > f,
                                         allowance_below_fixed=a < f))
            r["streams"] += 1
        for r in rows.values():
            r["change"] = ("newly eligible" if r["eligible_P_gt_fixed"] and not r["eligible_P_gt_3"] else
                           "newly ineligible" if r["eligible_P_gt_3"] and not r["eligible_P_gt_fixed"] else "unchanged")
        out[f"P={P}"] = rows
    return out


def check():
    checks = []
    n = net("x", 2, 0)
    k = grow(n, 2, chain=True)
    assert invariants([n])
    n.units[k[0]]["kids"].discard(k[1])
    try:
        invariants([n])
    except AssertionError:
        checks.append("invariant check refuses a parent that does not list its child")
    else:
        raise AssertionError("invalid fixture accepted")
    n = net("y", 2, 0)
    k = grow(n, 1)
    del n.units[0]
    try:
        invariants([n])
    except AssertionError:
        checks.append("invariant check refuses an orphan (parent removed without its child)")
    else:
        raise AssertionError("orphan accepted")
    r = native_case("smoke", [dict(alphabet=2, P=5, grown=1, saved=-1.)])
    assert r["admitted"] and r["allowance_sum_conserved"]
    checks.append("native admission with a leaf conserves the allowance sum")
    for bad, why in (((([dict(P=3, units=3)], [dict(P=4, units=3)]), "native Net._room", None), "an allowance created from nothing"),
                     ((([dict(P=4, units=3)], [dict(P=4, units=5)]), "capped rule M", 10), "capped M: units above a stream's allowance"),
                     ((([dict(P=6, units=3), dict(P=6, units=3)], [dict(P=6, units=6), dict(P=6, units=6)]), "capped rule M", 10), "capped M: total above the cap")):
        (b0, a0), impl, cap = bad
        try:
            allocation_invariants(b0, a0, impl, cap)
        except AssertionError:
            checks.append(f"allocation invariant check refuses {why}")
        else:
            raise AssertionError(f"accepted {why}")
    g = np.random.default_rng(3)
    c = np.random.Generator(type(g.bit_generator)())
    c.bit_generator.state = g.bit_generator.state
    assert int(c.integers(5)) == int(g.integers(5))
    checks.append("a copied generator predicts the native draw without consuming it")
    out = dict(success=True, checks=checks)
    BASE.with_name(BASE.name + "_checks").with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


def analyse():
    out = dict(success=False, provenance=dict(
        revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        dirty=subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
        sha256={p: digest(ROOT / p) for p in ("lab/market_transfer_cases.py", "lab/grownet.py", "lab/alloc_rules.py", "lab/v/future_evidence.pkl")},
        command="timeout 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/market_transfer_cases.py --analyse",
        POOL_BITS=GN.POOL_BITS))
    try:
        out["cases"] = run_cases()
        out["eligibility"] = eligibility()
        out["success"] = True
    finally:
        BASE.with_suffix(".json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    for c in out["cases"]:
        print(f"{c['implementation']:17s} | {c['case']:58s} | admitted {c['admitted']!s:5s} | allowance sum {c['allowance_sum']} | "
              f"occupancy {c['occupancy']} removals {c['removals']} | over allowance {c['over_allowance_after']} | "
              f"cap {c['cap']} free {c.get('cap_free_before')} | drawn {c.get('drawn_donor')} | changes {c['changes']}")
    print(json.dumps(out["eligibility"], indent=1))


if __name__ == "__main__":
    {"--check": check, "--analyse": analyse}[sys.argv[1]]()

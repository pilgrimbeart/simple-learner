"""PROGRAMME test H (D113): synthetic checks of lab/spare_allowance.py on real code paths; no creature lives.
    timeout 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/spare_allowance_checks.py
Exits nonzero on the first failed check.
"""
import copy
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "lab"), str(ROOT)]
import numpy as np
import alloc_compare  # noqa: F401  sets LB_FINE=LB_LIVE=1 before grownet is imported, as every harness does
import grownet as GN
import alloc_rules as A
import spare_allowance as SA

BASE = ROOT / "lab/v/spare_allowance_checks"
results = []


def passed(name, **kw):
    results.append(dict(name=name, passed=True, **kw))
    print("PASS", name, flush=True)


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class FakeBrain:
    def __init__(self, nets):
        self.nets, self.t = nets, 0.


def net(kind, alphabet, seed):
    return GN.Net(kind, alphabet, np.random.default_rng(seed), alphabet=alphabet)


def grow(n, count, chain=False):
    ks = []
    for _ in range(count):
        u = ks[-1] if (chain and ks) else 0
        ks.append(n._add(u, 0, n.units[u]["span"] + 1, 0.0))
    return ks


def build(donors, G, recipient_saved=5.0, recipient_full=True, due=True, seed=0):
    """Real Nets under alloc_rules rule M: recipient (alphabet 2) and donors. donors: dict(alphabet, grown, chain, saved, P_extra)."""
    R = net("recipient", 2, 100)
    D = [net(f"donor{i}", d["alphabet"], 200 + i) for i, d in enumerate(donors)]
    nets = [R] + D
    b = FakeBrain(nets)
    st = A.install(b, "M", G, seed)
    if recipient_full:
        grow(R, R.P - len(R.units))
    R.saved = recipient_saved
    for n, d in zip(D, donors):
        grow(n, min(d["grown"], n.P - len(n.units)), d.get("chain", False))
        n.saved = d["saved"]
        if "floor" in d:
            n.P = sum(x["sym"] is not None for x in n.units.values())
    ks = [k for k, x in R.units.items() if x["sym"] is None]
    if ks:
        R.units[ks[-1]]["n"] = [1, 1] if due else [2, 0]
        R._deep = ks[-1]
    else:
        R._deep = None
    return b, R, nets, st


def snapshot(b, R, nets, st, ret):
    rng = SA._closure_rng(nets[0].__dict__["_room"] if not hasattr(nets[0]._room, "__closure__") else nets[0]._room)
    def unit(x):
        return dict(u=x["u"], v=x["v"], span=x["span"], n=list(x["n"]), kids=sorted(x["kids"]), sym=x["sym"], use=x["use"])
    return json.dumps(dict(ret=ret, nets=[dict(kind=n.kind, P=int(n.P), base=n.base, saved=n.saved,
                                              units={k: unit(x) for k, x in sorted(n.units.items())}) for n in nets],
                           st={k: v for k, v in st.items()}, rng=A_rng_state(nets)), sort_keys=True, default=str)


def A_rng_state(nets):
    for n in nets:
        g = SA._closure_rng(n._room)
        if g is not None:
            return g.bit_generator.state
        o = getattr(n._room, "__wrapped_orig__", None)
    raise AssertionError("no allocator generator")


CASES = {
    "a: leafless donor with spare allowance": [dict(alphabet=2, grown=0, saved=-1.)],
    "b: donor with one leaf": [dict(alphabet=2, grown=1, saved=-1.)],
    "b2: donor with a leaf AND spare allowance": [dict(alphabet=2, grown=1, saved=-1.)],
    "c: donor at its fixed floor": [dict(alphabet=4, grown=0, saved=-1., floor=True)],
    "d: donor with a chain (dependant)": [dict(alphabet=2, grown=2, chain=True, saved=-1.)],
    "f: two candidates, one leafless": [dict(alphabet=2, grown=0, saved=-1.), dict(alphabet=2, grown=1, saved=-1.)],
    "b': donor's allowance full of leaves, total cap fully occupied": [dict(alphabet=2, grown=2, saved=-1.)],
}
G_FOR = {"a: leafless donor with spare allowance": 4, "b: donor with one leaf": 4, "b2: donor with a leaf AND spare allowance": 6,
         "c: donor at its fixed floor": 4, "d: donor with a chain (dependant)": 4, "f: two candidates, one leafless": 6,
         "b': donor's allowance full of leaves, total cap fully occupied": 4}


def run_case(name, mode, seed=0, **kw):
    b, R, nets, st = build(CASES[name], G_FOR[name], seed=seed, **kw)
    g = None
    if mode != "none":
        g = SA.install(b, enabled=mode == "enabled")
    rng_before = A_rng_state(nets) if g is None else SA._closure_rng(g.originals[0]["_room"]).bit_generator.state
    ret = R._room()
    if g is not None:
        g.uninstall()
    return b, R, nets, st, ret, snapshot(b, R, nets, st, ret), g


def main():
    t0 = time.monotonic()
    out = dict(success=False, provenance=dict(revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
               dirty=subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
               sha256={p: digest(ROOT / p) for p in ("lab/spare_allowance.py", "lab/spare_allowance_checks.py", "lab/alloc_rules.py",
                                                      "lab/grownet.py", "lab/issued_credit.py", "lab/issued_credit_checks.py")},
               command="timeout 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/spare_allowance_checks.py",
               simulated_steps=0))
    try:
        # 1. disabled adapter = original M, every case and seeds; duplicate installation refused
        for name in CASES:
            for seed in range(4):
                a = run_case(name, "none", seed=seed)
                d = run_case(name, "disabled", seed=seed)
                assert a[5] == d[5], ("disabled differs", name, seed)
        for extra in (dict(recipient_saved=1.0), dict(due=False), dict(recipient_full=False)):
            for name in ("a: leafless donor with spare allowance", "f: two candidates, one leafless"):
                assert run_case(name, "none", **extra)[5] == run_case(name, "disabled", **extra)[5]
        b, R, nets, st = build(CASES["b: donor with one leaf"], 4)
        SA.install(b)
        try:
            SA.install(b)
        except AssertionError as e:
            assert "already installed" in str(e)
        else:
            raise AssertionError("duplicate installation accepted")
        passed("1 disabled adapter identical to original M (return, units, tallies, links, allowances, savings, counters, RNG) "
               "in every case, 4 seeds each, plus price-equal, no-birth-due and under-allowance requests; duplicate install refused")

        # 2. leafless donor with spare allowance: one allowance moves, nothing deleted; a birth then fits allowance and cap
        b, R, nets, st, ret, snap, g = run_case("a: leafless donor with spare allowance", "enabled")
        D = nets[1]
        assert ret is True and int(R.P) == R.base + 1 and int(D.P) == D.base - 1 and len(D.units) == 2
        assert g.c["allowance-only transfers"] == 1 and g.c.get("transfers with deletion", 0) == 0 and st["transfers"] == 0
        assert R.saved == 5.0
        k = R._add(0, 0, 2, 0.)
        assert len(R.units) <= R.P and st["fixed"] + st["grown"] <= st["cap"]
        SA.invariants(nets, [2, 2], st["cap"], sum(int(n.P) for n in nets))
        for extra, why in ((dict(recipient_saved=1.0), "price not exceeded (saved = price)"),):
            r = run_case("a: leafless donor with spare allowance", "enabled", **extra)
            assert r[4] is False and r[6].c.get("allowance-only transfers", 0) == 0
        r = run_case("c: donor at its fixed floor", "enabled")
        assert r[4] is False and r[6].c.get("allowance-only transfers", 0) == 0 and r[5] == run_case("c: donor at its fixed floor", "none")[5]
        passed("2 leafless spare donor: exactly one allowance moves with no deletion and no savings debit; the next birth fits "
               "the recipient's allowance and the cap; donor at its fixed floor and savings at the price still refused")

        # 3. donor with a leaf AND spare allowance takes today's removal path exactly; chains stay valid; fixed never removed
        for name in ("b2: donor with a leaf AND spare allowance", "b: donor with one leaf", "d: donor with a chain (dependant)"):
            for seed in range(4):
                o = run_case(name, "none", seed=seed)
                e = run_case(name, "enabled", seed=seed)
                assert o[5] == e[5], ("enabled changed the leaf path", name, seed)
                assert e[6].c.get("allowance-only transfers", 0) == 0
                for n, f in zip(e[2], [2] + [d["alphabet"] for d in CASES[name]]):
                    assert sum(x["sym"] is not None for x in n.units.values()) == f, "a fixed unit was removed"
                SA.invariants(e[2], [2] + [d["alphabet"] for d in CASES[name]], e[3]["cap"], sum(int(n.P) for n in e[2]))
        b2 = run_case("b2: donor with a leaf AND spare allowance", "enabled")
        D = b2[2][1]
        assert int(D.P) - len(D.units) >= 0 and b2[6].c["transfers with deletion"] == 1
        passed("3 a donor with a leaf and spare allowance follows the old removal path exactly (identical to original M); "
               "chain dependants stay valid; fixed units never removed")

        # 4. two candidates, one leafless: the original single draw; no redraw; price equality, no birth due, under allowance
        seen = {}
        for seed in range(8):
            o = run_case("f: two candidates, one leafless", "none", seed=seed)
            e = run_case("f: two candidates, one leafless", "enabled", seed=seed)
            ro, re_ = json.loads(o[5])["rng"], json.loads(e[5])["rng"]
            assert ro == re_, "the adapter changed the generator's state (a redraw or extra draw)"
            if o[4]:
                assert o[5] == e[5] and e[6].c.get("allowance-only transfers", 0) == 0
                seen["leaf drawn"] = seen.get("leaf drawn", 0) + 1
            else:
                assert e[4] is True and e[6].c["allowance-only transfers"] == 1
                assert e[6].first_transfer["donor"] == 1, "allowance must come from the drawn (leafless) donor"
                seen["leafless drawn"] = seen.get("leafless drawn", 0) + 1
        assert seen.get("leaf drawn") and seen.get("leafless drawn")
        for extra in (dict(recipient_saved=1.0), dict(due=False)):
            e = run_case("f: two candidates, one leafless", "enabled", **extra)
            assert e[4] is False and not e[6].c.get("allowance-only transfers")
        e = run_case("f: two candidates, one leafless", "enabled", recipient_full=False)
        assert e[4] is True and not e[6].c.get("allowance-only transfers") and e[6].c["requests: under allowance"] == 1
        passed("4 two candidates: the single original draw decides (8 seeds: both outcomes seen), generator state identical to "
               "original M, allowance taken only from the drawn leafless donor; price equality and no birth due refused; "
               "under-allowance requests unchanged", outcomes=seen)

        # 5. invariant checker rejects each corruption
        def fresh():
            b, R, nets, st = build(CASES["b: donor with one leaf"], 4)
            return nets, [2, 2], st["cap"], sum(int(n.P) for n in nets)
        nets, fx, cap, S = fresh()
        SA.invariants(nets, fx, cap, S)
        corruptions = {}
        nets, fx, cap, S = fresh(); nets[0].P += 1
        corruptions["allowance sum changed"] = (nets, fx, cap, S)
        nets, fx, cap, S = fresh(); del nets[1].units[1]
        corruptions["fixed unit missing (units below fixed)"] = (nets, fx, cap, S)
        nets, fx, cap, S = fresh(); dP = int(nets[1].P) - (len(nets[1].units) - 1); nets[1].P -= dP; nets[0].P += dP
        corruptions["units above allowance"] = (nets, fx, cap, S)
        nets, fx, cap, S = fresh()
        corruptions["total above cap"] = (nets, fx, cap - 5, S)
        nets, fx, cap, S = fresh(); k = [k for k, x in nets[1].units.items() if x["sym"] is None][0]; nets[1].units[k]["u"] = 99
        corruptions["orphan link"] = (nets, fx, cap, S)
        for why, args in corruptions.items():
            try:
                SA.invariants(*args)
            except AssertionError:
                pass
            else:
                raise AssertionError(f"invariant checker accepted: {why}")
        b, R, nets, st = build(CASES["b: donor with one leaf"], 4)
        g = SA.install(b, enabled=True)
        try:
            R._add(0, 0, 2, 0.)                                # bypasses the room test: a birth above the recipient's allowance
        except AssertionError as e:
            assert "allowance" in str(e)
        else:
            raise AssertionError("per-birth check accepted a birth above the allowance")
        g.uninstall()
        b, R, nets, st = build(CASES["b: donor with one leaf"], 4)
        g = SA.install(b, enabled=True)
        R.P += 5                                               # allowance enough, so only the cap can refuse
        st["cap"] = st["fixed"] + st["grown"]
        try:
            R._add(0, 0, 2, 0.)
        except Exception as e:
            assert "cap" in str(e).lower() or type(e).__name__ == "CapBroken", e
        else:
            raise AssertionError("a birth above the cap was accepted")
        g.uninstall()
        passed("5 whole-brain invariants hold on valid states and the checker rejects each corruption: " + "; ".join(corruptions)
               + "; per-birth checks refuse a birth above the stream's allowance and above the total cap")

        # 6. real 168-stream brain: rule M, D82 issued credit and the adapter in harness order
        import issued_credit as I
        import issued_credit_checks as ICK
        from active_mixture_audit import fingerprint
        d82 = ICK.run_checks()
        assert all(r["passed"] for r in d82)
        orig_fixture = ICK.fixture

        def fixture_with_gate():
            lf, selected, n = orig_fixture()
            # D82's fixtures add up to two units directly to a stream (bypassing the room test); at G=258 rule M gives each
            # stream only fixed + 1, which the per-birth check rightly refuses. G = 4 * 168 gives each stream fixed + 4.
            A.install(lf.brain, "M", 4 * 168, 177000)
            SA.install(lf.brain, enabled=True)
            return lf, selected, n
        ICK.fixture = fixture_with_gate
        try:
            d82_gate = ICK.run_checks()
        finally:
            ICK.fixture = orig_fixture
        assert all(r["passed"] for r in d82_gate) and [r["name"] for r in d82_gate] == [r["name"] for r in d82]

        def real(gate_mode):
            import stage3_random as R_
            import teach as T
            import alloc_compare as C
            from stage2_lang import arms as S
            R_._init(.0025, False)
            holder = []

            class Constructed(Exception):
                pass

            def capture(lf, secs):
                holder.append(lf)
                raise Constructed
            old = S.live
            S.live = capture
            try:
                T.job((C.world("seq"), C.ARM, 560, 142000, "red", 300.))
            except Constructed:
                pass
            finally:
                S.live = old
            lf = holder[0]
            b = lf.brain
            st = A.install(b, "M", 258, 142000)
            assert st["cap"] == 2300
            b.vouched = lambda: True
            b.bar, b.dl, b.dt = .5, 0, 0
            selected = {n.kind: None for n in b.nets}
            for n in b.nets:
                def says(i, _n=n):
                    k = selected[_n.kind]
                    return (k, [k]) if k in _n.units else (None, [])
                n.says = says
                n.learn = lambda *a: None
                n.write = lambda *a, **k: None
                n.tidy = lambda *a: None
            spk = b.nets[1]
            k = spk._add(0, 1, 2, 0.)
            spk.units[k]["n"] = [0, 3]
            selected[spk.kind] = k
            spk.saved = 1e-9                                  # not a poor donor, so the transfer cannot take its speaker
            rec = b.nets[5]
            rk = rec._add(0, 0, 2, 0.)
            rec.units[rk]["n"] = [1, 1]
            rec._deep = rk
            rec.saved = 2.0
            ob = I.install(lf, enabled=True)
            g = SA.install(b, enabled=gate_mode == "enabled") if gate_mode != "none" else None
            b.predict()
            ret = rec._room()
            b.taste(1., 0.)
            if g is not None:
                summ = g.summary()
                g.uninstall()
            else:
                summ = None
            return lf, b, spk, k, rec, ret, ob, summ, fingerprint(lf)[0]
        lf, b, spk, k, rec, ret, ob, summ, fp_on = real("enabled")
        assert ret is True and summ["counters"]["allowance-only transfers"] == 1
        assert spk.agree == 1 and spk.units[k]["use"] == 1. and spk.units[k]["own"] == 1.
        assert abs(spk.saved - (1e-9 + math.log2(1.75))) < 1e-12, spk.saved
        assert rec.saved == 2.0, "savings were spent by the transfer"
        assert ob.counters["cached_original_speakers_removed"] == 0 and ob.counters["replacement_credit_prevented"] == 0
        assert ob.counters["delivered_correct_forecasts"] == 1 and ob.max_reconstruction_error <= 1e-12
        _, _, _, _, _, ret_n, ob_n, _, fp_none = real("none")
        _, _, _, _, _, ret_d, ob_d, summ_d, fp_dis = real("disabled")
        assert ret_n is False and ret_d is False and fp_none == fp_dis, "disabled adapter changed the real-brain state"
        assert ob_n.summary() == ob_d.summary(), "disabled adapter changed D82's output"
        assert summ_d["counters"]["requests: drawn donor leafless with spare allowance"] == 1
        passed("6 real brain (168 streams, rule M cap 2300, D82 issued credit, adapter, harness order): an allowance-only transfer "
               "between issue and taste leaves credit on the issued original speaker (agree 1, use and own credit 1, saved "
               "+log2 1.75), removes nothing, credits no replacement and spends no savings; D82's own fixtures pass unchanged "
               "and again with rule M (G = 4 x 168, room for their direct additions) and the enabled adapter; disabled adapter gives the same "
               "fingerprint and D82 summary as no adapter; D82's own checks pass unchanged",
               d82_checks=[r["name"] for r in d82], d82_checks_with_rule_M_and_enabled_adapter=[r["name"] for r in d82_gate])
        out["checks"] = results
        out["success"] = True
    finally:
        out["wall_s"] = time.monotonic() - t0
        BASE.with_suffix(".json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print("wall_s", out["wall_s"])


if __name__ == "__main__":
    main()

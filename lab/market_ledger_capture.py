"""Job G (PROGRAMME after D108): passive market ledger on four existing configurations, each unobserved then observed.
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/market_ledger_capture.py --check
    timeout 900s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/market_ledger_capture.py --capture
    timeout 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/market_ledger_capture.py --analyse
Observation only: wrappers copy values and call the originals unchanged; donor draws are predicted from a copy of the
generator state; everything is unwrapped before the terminal fingerprint.
"""
import hashlib
import json
import math
from pathlib import Path
import pickle
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "lab"), str(ROOT)]
import numpy as np
import alloc_compare as C
import room_prediction as RP

BASE = ROOT / "lab/v/market_ledger_capture"
SEED = 142000
CONFIGS = (("M", 560), ("none", 4480))          # rule M at cap 2042 + 258; the design at P=4480 (hooks only)
SHARE = .01


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def gen_copy(g):
    c = np.random.Generator(type(g.bit_generator)())
    c.bit_generator.state = g.bit_generator.state
    return c


def closure_rng(fn):
    for cell in (getattr(fn, "__closure__", None) or ()):
        if isinstance(cell.cell_contents, np.random.Generator):
            return cell.cell_contents
    return None


class Ledger:
    def __init__(self, lf, impl):
        import grownet as GN
        self.GN, self.b, self.impl = GN, lf.brain, impl
        b = self.b
        self.fixed = [sum(x["sym"] is not None for x in n.units.values()) for n in b.nets]
        self.fam = [C.family(n.kind) for n in b.nets]
        self.originals = []
        for n in b.nets:
            self.originals.append({a: n.__dict__[a] for a in ("says", "learn", "_remove", "_room") if a in n.__dict__})
        self.orig_brain = {a: b.__dict__[a] for a in ("predict", "taste") if a in b.__dict__}
        self.rec = RP.Recorder(lf)                    # issued rows at accepted tastes (D93 recorder)
        self.requests, self.tastes = [], []
        self.removing, self.cur = None, None
        self.issued_balance = np.zeros(len(b.nets))
        self.seq = 0
        for j, n in enumerate(b.nets):
            self._wrap(n, j)
        taste = b.taste

        def _taste(value, at):
            before = getattr(b, "ntaste", 0)
            cur = dict(seq=self.seq, t=float(b.t + at), w_before=self.weights(), saved_before=self.saved(), order=[], scored={})
            self.seq += 1
            self.cur = cur
            nrows = len(self.rec.rows)
            try:
                r = taste(value, at)
            finally:
                self.cur = None
            if getattr(b, "ntaste", 0) - before:
                assert len(self.rec.rows) == nrows + 1
                row = self.rec.rows[-1]
                y = row["letter"]
                cur.update(accepted=True, letter=y, w_after=self.weights(), saved_after=self.saved(), pd1=row["pd"],
                           issued_q=row["q"].copy(), issued_p1=row["p1"])
                pd = row["pd"] if y else 1 - row["pd"]
                aw = np.isfinite(row["q"])
                qy = np.where(aw, row["q"] if y else 1 - row["q"], np.nan)
                self.issued_balance[aw] += np.log2(qy[aw] / pd)
                self.tastes.append(cur)
            return r
        b.taste = _taste

    def weights(self):
        return float(getattr(self.b, "w_def", 1.)), np.array([float(getattr(n, "w", 1.)) for n in self.b.nets])

    def saved(self):
        return np.array([float(getattr(n, "saved", 0.)) for n in self.b.nets])

    def candidates(self, n):
        nets = self.b.nets
        if self.impl == "M":
            return [i for i, v in enumerate(nets) if v is not n and getattr(v, "saved", 0.) <= 0. and v.P > self.fixed[i]]
        return [i for i, v in enumerate(nets) if v is not n and getattr(v, "saved", 0.) <= 0. and v.P > 3]

    def _wrap(self, n, j):
        GN, b = self.GN, self.b
        room, remove, learn = n._room, n._remove, n.learn

        def _remove(k):
            if self.removing is not None and k in n.units:
                self.removing.append((j, k))
            return remove(k)

        def _learn(i, letter, t, speaker, firing):
            cur = self.cur
            if cur is not None:
                cur["order"].append(j)
                if speaker is not None:
                    u = n.units[speaker]["n"]
                    cur["scored"][j] = (u[1] + .5) / (u[0] + u[1] + 1.)       # issued-style p(1) from the counts just before learning
            return learn(i, letter, t, speaker, firing)

        def _room():
            units, P = len(n.units), int(n.P)
            base = getattr(n, "base", None)
            saved = float(getattr(n, "saved", 0.))
            price = GN.POOL_BITS * (units - (base if base is not None else P) + 1)
            d = getattr(n, "_deep", None)
            due = d is not None and d in n.units and min(n.units[d]["n"]) >= 1
            row = dict(seq=self.seq, t=float(b.t), j=j, units=units, fixed=self.fixed[j], P=P, base=base, saved=saved, price=price,
                       issued_balance=float(self.issued_balance[j]), due=due, under=units < P)
            cands = []
            pred = None
            if not row["under"] and saved > price and (self.impl != "M" or due):
                cands = self.candidates(n)
                if cands:
                    g = closure_rng(room) if self.impl == "M" else n.rng
                    pred = cands[int(gen_copy(g).integers(len(cands)))]
            row["candidates"] = len(cands)
            row["cand_spare"] = sum(b.nets[i].P > len(b.nets[i].units) for i in cands)
            row["cand_leaves"] = sum(any(x["sym"] is None and not x["kids"] for x in b.nets[i].units.values()) for i in cands)
            if pred is not None:
                v = b.nets[pred]
                row.update(pred=pred, pred_spare=int(v.P - len(v.units)),
                           pred_leaves=sum(1 for x in v.units.values() if x["sym"] is None and not x["kids"]))
            Pbefore = {i: int(b.nets[i].P) for i in cands}
            self.removing = []
            try:
                ok = room()
            finally:
                rem, self.removing = self.removing, None
            row["ok"] = bool(ok)
            row["P_after"] = int(n.P)
            row["donor"] = [i for i in cands if int(b.nets[i].P) == Pbefore[i] - 1]
            row["removals"] = rem
            self.requests.append(row)
            return ok
        n._room, n._remove, n.learn = _room, _remove, _learn

    def unwrap(self):
        for n, orig in zip(self.b.nets, self.originals):
            for a in ("says", "learn", "_remove", "_room"):
                if a in orig:
                    setattr(n, a, orig[a])
                elif a in n.__dict__:
                    del n.__dict__[a]
        for a in ("predict", "taste"):
            if a in self.orig_brain:
                setattr(self.b, a, self.orig_brain[a])
            elif a in self.b.__dict__:
                del self.b.__dict__[a]


def one(job):
    from stage2_lang import arms as S
    from active_mixture_audit import fingerprint
    rule, P, first, observe = job
    original, out = S.live, {}

    def live(lf, secs):
        led = Ledger(lf, "M" if rule == "M" else "design") if observe else None
        lived = original(lf, secs)
        if led:
            led.unwrap()
            out.update(requests=led.requests, tastes=led.tastes, rows=led.rec.rows, fixed=led.fixed, fam=led.fam,
                       final_saved=[float(getattr(n, "saved", 0.)) for n in lf.brain.nets],
                       final_w=led.weights())
        out["fingerprint"] = fingerprint(lf)[0]
        return lived
    S.live = live
    t0 = time.monotonic()
    try:
        r = C.one(("seq", rule, P, SEED, first))
    finally:
        S.live = original
    return dict(r, observe=observe, wall_s=time.monotonic() - t0, **out)


def check():
    checks = []
    g = np.random.default_rng(5)
    g.integers(10)
    c = gen_copy(g)
    a = int(c.integers(7))
    assert int(g.integers(7)) == a
    checks.append("a draw from a copied generator predicts the native draw and consumes nothing from the original")

    def f():
        return h.integers(3)
    h = np.random.default_rng(1)
    assert closure_rng(f) is h
    checks.append("closure_rng finds the allocator generator in a closure")
    inc = [math.log2(.8 / .5), math.log2(.3 / .6)]
    assert abs(sum(inc) - (math.log2(.8 / .5) + math.log2(.3 / .6))) < 1e-15
    checks.append("balance increments are log2(q_scored(y)/p_def(y)) and sum to the final balance")

    class N:
        pass
    n = N()
    n.__dict__["learn"] = "orig"
    led = Ledger.__new__(Ledger)
    led.b = N()
    led.b.nets = [n]
    led.b.__dict__["predict"] = "p"
    led.originals = [{"learn": "orig"}]
    led.orig_brain = {"predict": "p"}
    n.learn, n.says, n._room = "wrapped", "w2", "w3"
    led.b.predict, led.b.taste = "pw", "tw"
    led.unwrap()
    assert n.__dict__ == {"learn": "orig"} and led.b.__dict__ == {"nets": [n], "predict": "p"}
    checks.append("unwrap restores original instance attributes and removes added ones")
    out = dict(success=True, checks=checks)
    BASE.with_name(BASE.name + "_checks").with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


def capture():
    t0 = time.monotonic()
    jobs = [(rule, P, first, obs) for rule, P in CONFIGS for first in ("red", "blue") for obs in (False, True)]
    with ProcessPoolExecutor(2) as ex:
        res = list(ex.map(one, jobs, chunksize=1))
    raw = BASE.with_suffix(".pkl")
    raw.write_bytes(pickle.dumps(res))
    out = dict(wall_s=time.monotonic() - t0, raw=str(raw), raw_sha256=digest(raw), jobs=jobs,
               provenance=dict(revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                               dirty=subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
                               sha256={p: digest(ROOT / p) for p in ("lab/market_ledger_capture.py", "lab/room_prediction.py", "lab/alloc_compare.py",
                                                                      "lab/alloc_rules.py", "lab/grownet.py", "lab/active_mixture_audit.py")},
                               command="timeout 900s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/market_ledger_capture.py --capture"))
    BASE.with_name(BASE.name + "_capture").with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "provenance"}, indent=1))


def same(a, b):
    a, b = json.loads(json.dumps(a)), json.loads(json.dumps(b))
    return [v for i, v in enumerate(a) if i not in (5, 7)] == [v for i, v in enumerate(b) if i not in (5, 7)] and abs(a[7] - b[7]) < 1e-12


def analyse():
    res = pickle.loads(BASE.with_suffix(".pkl").read_bytes())
    by = {}
    for r in res:
        k = (r["rule"], r["first"], r["observe"])
        assert k not in by, ("duplicate", k)
        by[k] = r
    assert len(by) == 8
    st1 = {(l["rule"], l["seed"], l["first"]): l for l in json.loads((ROOT / "lab/v/alloc_stage1.json").read_text())["families"]["seq"]["lives"]}
    d93 = {(l["name"], l["seed"], l["first"]): l for l in pickle.loads((ROOT / "lab/v/room_prediction.pkl").read_bytes())["lives"]}
    out = dict(identity={}, checks={}, lives={})
    for rule, P in CONFIGS:
        for first in ("red", "blue"):
            u, o = by[rule, first, False], by[rule, first, True]
            idt = dict(observed_equals_unobserved_result=same(u["result"], o["result"]),
                       observed_equals_unobserved_fingerprint=u["fingerprint"] == o["fingerprint"])
            if rule == "M":
                idt["reproduces_alloc_stage1"] = same(o["result"], st1["M", SEED, first]["result"])
                idt["transfers_equal_stage1"] = o["alloc"]["transfers"] == st1["M", SEED, first]["alloc"]["transfers"]
            else:
                ref = d93["high", SEED, first]
                idt["reproduces_D93_result"] = same(o["result"], ref["result"])
                idt["reproduces_D93_issued_rows"] = len(ref["rows"]) == len(o["rows"]) and all(
                    a["p1"] == b["p1"] and a["letter"] == b["letter"] for a, b in zip(ref["rows"], o["rows"]))
            out["identity"][f"{rule} {first}"] = idt
    if not all(all(v.values()) for v in out["identity"].values()):
        BASE.with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
        print(json.dumps(out["identity"], indent=1))
        raise SystemExit("identity failed: no analysis")
    for rule, P in CONFIGS:
        for first in ("red", "blue"):
            o = by[rule, first, True]
            fam = o["fam"]
            T = o["tastes"]
            # balances: increments sum to final and equal log2(q_scored(y)/p_def(y)) for the credited set
            inc_sum = np.zeros(len(fam))
            maxinc = 0.
            for t in T:
                y = t["letter"]
                pd = t["pd1"] if y else 1 - t["pd1"]
                d = t["saved_after"] - t["saved_before"]
                exp = np.zeros(len(fam))
                for j, q1 in t["scored"].items():
                    exp[j] = math.log2((q1 if y else 1 - q1) / pd)
                maxinc = max(maxinc, float(np.max(np.abs(d - exp))))
                inc_sum += d
            sum_err = float(np.max(np.abs(inc_sum - np.array(o["final_saved"]))))
            # weight replay from scored forecasts, share .01, starting all ones
            wd, w = 1., np.ones(len(fam))
            wmax = 0.
            for t in T:
                q = np.full(len(fam), np.nan)
                for j, q1 in t["scored"].items():
                    q[j] = q1
                wd0, w0 = t["w_before"]
                wmax = max(wmax, abs(wd - wd0), float(np.max(np.abs(w - w0))))
                wd, w = RP_update(wd, w, q, t["pd1"], t["letter"])
                wd1, w1 = t["w_after"]
                wmax = max(wmax, abs(wd - wd1), float(np.max(np.abs(w - w1))))
            # requests
            R = o["requests"]
            outcome = {}
            bad_removal = 0
            pred_mismatch = 0
            rows = []
            for r in R:
                if r["under"]:
                    oc = "under allowance"
                elif rule == "M" and not r["due"]:
                    oc = "full, no birth due"
                elif r["saved"] <= r["price"]:
                    oc = "full, savings test fails"
                elif not r["candidates"]:
                    oc = "full, no donor"
                elif r["ok"]:
                    oc = "transferred with removal" if r["removals"] else "transferred allowance only"
                else:
                    oc = "refused: drawn donor has no leaf"
                outcome[oc] = outcome.get(oc, 0) + 1
                if r["ok"] and not r["under"]:
                    if r["donor"] != [r.get("pred")]:
                        pred_mismatch += 1
                    if any(jj not in r["donor"] for jj, _ in r["removals"]):
                        bad_removal += 1
                rows.append((oc, r))
            refused_leafless = [r for oc, r in rows if oc == "refused: drawn donor has no leaf"]
            spare = sum(r.get("pred_spare", 0) > 0 for r in refused_leafless)
            # issued-credit admission on the fixed captured state
            hist_pass = [r for oc, r in rows if not r["under"] and (rule != "M" or r["due"])]
            flip_to_pass = sum(r["saved"] <= r["price"] < r["issued_balance"] for r in hist_pass)
            flip_to_fail = sum(r["issued_balance"] <= r["price"] < r["saved"] for r in hist_pass)
            fam_out = {}
            for f in ("event", "clock", "integrator", "rhythm"):
                fr = [(oc, r) for oc, r in rows if fam[r["j"]] == f]
                fam_out[f] = {oc: sum(1 for x, _ in fr if x == oc) for oc in sorted({x for x, _ in fr})}
                fam_out[f]["leafless refusals with spare drawn donor"] = sum(1 for x, r in fr if x == "refused: drawn donor has no leaf" and r.get("pred_spare", 0) > 0)
                fam_out[f]["issued credit would pass (historical fails)"] = sum(r["saved"] <= r["price"] < r["issued_balance"] for x, r in fr if not r["under"] and (rule != "M" or r["due"]))
                fam_out[f]["issued credit would fail (historical passes)"] = sum(r["issued_balance"] <= r["price"] < r["saved"] for x, r in fr if not r["under"] and (rule != "M" or r["due"]))
            transfers = sum(1 for oc, _ in rows if oc.startswith("transferred"))
            # allowance conservation per request: the recipient gains exactly one unit of allowance iff it took one, and
            # exactly one candidate lost one; no other change is possible within a room call (both implementations)
            cons_bad = 0
            for oc, r in rows:
                took = oc.startswith("transferred")
                gained = r["P_after"] - r["P"]
                if (took and (gained != 1 or len(r["donor"]) != 1)) or (not took and (gained != 0 or r["donor"])):
                    cons_bad += 1
            chk = dict(balance_increment_max_error=maxinc, balance_sum_max_error=sum_err, weight_replay_max_error=wmax,
                       predicted_donor_mismatches=pred_mismatch, removals_outside_donor=bad_removal,
                       transfers=transfers, allocator_transfers=o["alloc"].get("transfers") if rule == "M" else None,
                       allowance_conservation_violations=cons_bad)
            if rule != "M":
                d77 = {(l["P"], l["world"], l["first"]): l["counters"].get("market_transfers", 0)
                       for l in json.loads((ROOT / "lab/v/noisy_resource_observe.json").read_text())["lives"]}
                chk["D77_market_transfer_counter"] = d77[4480, "seq17", first]
                chk["transfers_equal_D77_counter"] = transfers == d77[4480, "seq17", first]
            if rule == "M":
                chk["transfers_reconcile"] = transfers == o["alloc"]["transfers"]
                chk["peak_within_cap"] = o["alloc"]["peak"] <= o["alloc"]["cap"]
            out["checks"][f"{rule} {first}"] = chk
            out["lives"][f"{rule} {first}"] = dict(requests=len(R), accepted_tastes=len(T), outcomes=outcome, by_family=fam_out,
                                                    leafless_refusals=len(refused_leafless), leafless_with_spare_drawn_donor=spare,
                                                    issued_would_pass=flip_to_pass, issued_would_fail=flip_to_fail, gated_requests=len(hist_pass))
    out["fingerprint_schema"] = ("active_mixture_audit.fingerprint: sha256 of repr(canonical(state)), state = behaviour (lf.meals, "
        "lf.scored, lf.firings); every non-callable entry of the brain's __dict__ except nets and byk; every non-callable entry "
        "of each stream's __dict__ (units with tallies, histories, allowance, base, savings, weights, the stream's random "
        "generator state); and the bit-generator state of any numpy Generator in each stream's _room closure (the capped "
        "allocator's generator). canonical() sorts dict items, replaces links to other streams by their names, and encodes "
        "generators by their bit-generator state. Observer wrappers are removed before it is taken.")
    out["configuration_compatibility"] = ("M lives run through alloc_compare.one(('seq', 'M', 560, 142000, colour)), as D78 "
        "stage 1 did. Design lives run through alloc_compare.one(('seq', 'none', 4480, ...)): rule 'none' installs counting "
        "hooks only; D93 ran the same arm, P, seed, life and step through teach.job directly. Equal result tuples and every "
        "issued probability show the hooks do not change the life; D78's neutral check found the same.")
    ok = all(c["allowance_conservation_violations"] == 0 and c.get("transfers_equal_D77_counter", True) and c["balance_increment_max_error"] <= 1e-9 and c["balance_sum_max_error"] <= 1e-9 and c["weight_replay_max_error"] <= 1e-9
             and c["predicted_donor_mismatches"] == 0 and c["removals_outside_donor"] == 0 and c.get("transfers_reconcile", True)
             and c.get("peak_within_cap", True) for c in out["checks"].values())
    out["all_checks_pass"] = ok
    out["capture"] = json.loads(BASE.with_name(BASE.name + "_capture").with_suffix(".json").read_text())
    out["analysis_sha256"] = digest(Path(__file__))
    BASE.with_suffix(".json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(json.dumps(dict(identity=out["identity"], checks=out["checks"], all_checks_pass=ok), indent=1))
    print(json.dumps(out["lives"], indent=1))


def RP_update(wd, w, q, pd1, y):
    import selection_share_audit as SA
    return SA.update(wd, w, q, pd1, y, SHARE)


if __name__ == "__main__":
    {"--check": check, "--capture": capture, "--analyse": analyse}[sys.argv[1]]()

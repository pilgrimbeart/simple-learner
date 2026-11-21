"""PROGRAMME tests I and J (D114, D115): capped rule M (G=258, cap 2300) with historical credit, D82 issued credit, and
issued credit plus the spare-allowance gate (lab/spare_allowance.py).
    timeout 900s  env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/spare_allowance_experiment.py --pilot
    timeout 240s  env ... .venv/bin/python lab/spare_allowance_experiment.py --analyse     (pilot checks and per-life report)
    timeout 1800s env ... .venv/bin/python lab/spare_allowance_experiment.py --compare     (J; only after the pilot's mechanical checks)
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

BASE = ROOT / "lab/v/spare_allowance"
G, CAP = 258, 2300
SOURCES = ("lab/spare_allowance_experiment.py", "lab/spare_allowance.py", "lab/issued_credit.py", "lab/alloc_rules.py",
           "lab/alloc_compare.py", "lab/grownet.py", "lab/teach.py", "lab/active_mixture_audit.py")
SECS = {"seq": 300., "time": 3000., "allfood": 300.}
FAMS = ("event", "clock", "integrator", "rhythm")


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def canon(x, seen=None):
    """Canonical value of a body/world object graph: non-callable data only, objects by class and __dict__, cycles marked."""
    seen = set() if seen is None else seen
    if isinstance(x, np.random.Generator):
        return ("Generator", canon(x.bit_generator.state, seen))
    if isinstance(x, np.ndarray):
        return ("array", str(x.dtype), x.shape, x.tobytes().hex() if x.dtype != object else canon(x.tolist(), seen))
    if isinstance(x, np.generic):
        return canon(x.item(), seen)
    if x is None or isinstance(x, (bool, int, float, str, complex)):
        return x
    if isinstance(x, dict):
        return ("dict", sorted(((repr(k), canon(v, seen)) for k, v in x.items() if not callable(v)), key=lambda kv: kv[0]))
    if isinstance(x, (list, tuple)):
        return (type(x).__name__, [canon(v, seen) for v in x])
    if isinstance(x, (set, frozenset)):
        return ("set", sorted((canon(v, seen) for v in x), key=repr))
    if id(x) in seen:
        return ("cycle", type(x).__name__)
    seen.add(id(x))
    d = getattr(x, "__dict__", None)
    if d is None:
        return ("opaque", type(x).__name__, repr(x)[:60])
    return ("obj", type(x).__name__, canon({k: v for k, v in d.items() if not callable(v)}, seen))


def body_fingerprint(lf):
    data = canon({k: v for k, v in lf.__dict__.items() if k != "brain" and not callable(v)})
    return hashlib.sha256(repr(data).encode()).hexdigest()


class Trace:
    """Prediction times/probabilities, and the issued probability and label at each accepted taste. Passive."""

    def __init__(self, lf):
        b = self.b = lf.brain
        self.pred, self.acc, self.last, self.letter = [], [], None, None
        self.orig = dict(predict=b.__dict__.get("predict"), taste=b.__dict__.get("taste"))
        n0 = b.nets[0]
        self.orig_learn0 = n0.__dict__.get("learn")
        predict, taste, learn0 = b.predict, b.taste, n0.learn

        def _predict():
            r = predict()
            self.last = (float(b.t), float(b.p1))
            self.pred.append(self.last)
            return r

        def _taste(value, at):
            before, issued = getattr(b, "ntaste", 0), self.last
            self.letter = None
            r = taste(value, at)
            if getattr(b, "ntaste", 0) - before:
                self.acc.append((float(b.t + at), issued[1], int(self.letter)))
            return r

        def _learn0(i, letter, t, speaker, firing):
            self.letter = int(letter)
            return learn0(i, letter, t, speaker, firing)
        b.predict, b.taste, n0.learn = _predict, _taste, _learn0

    def uninstall(self):
        b, n0 = self.b, self.b.nets[0]
        for a, v in self.orig.items():
            if v is None:
                b.__dict__.pop(a, None)
            else:
                setattr(b, a, v)
        if self.orig_learn0 is None:
            n0.__dict__.pop("learn", None)
        else:
            n0.learn = self.orig_learn0


def one(job):
    cond, arm, seed, first = job
    import issued_credit as I
    import spare_allowance as SA
    from stage2_lang import arms as S
    from active_mixture_audit import fingerprint
    assert C.G == G
    original_live, original_world = S.live, C.world
    out = {}

    def live(lf, secs):
        b = lf.brain
        st = b._alloc
        assert st["cap"] == CAP and st["fixed"] + G == CAP, st
        ob = I.install(lf, enabled=True) if arm.startswith("issued") else None
        gate = SA.install(b, enabled=arm == "issued+gate") if arm in ("issued+gate", "issued+gate disabled") else None
        tr = Trace(lf)
        c0 = time.process_time()
        lived = original_live(lf, secs)
        cpu = time.process_time() - c0
        tr.uninstall()
        gsum = None
        if gate is not None:
            gsum = gate.summary()
            gate.uninstall()
        fam = [C.family(n.kind) for n in b.nets]
        total_ticks = lf.t
        food = [s for s in lf.scored if not s[1]]
        poison = [s for s in lf.scored if s[1]]
        late = 2 * total_ticks / 3
        out.update(fingerprint=fingerprint(lf)[0], body_fingerprint=body_fingerprint(lf), cpu_s=cpu, trace_pred=tr.pred, trace_acc=tr.acc,
                   gate=gsum, credit=(ob.summary() if ob is not None else None), alloc=dict(st), ntaste=getattr(b, "ntaste", 0),
                   births=sum(n.births for n in b.nets), recycled=sum(n.fades + n.starved for n in b.nets),
                   final_units=sum(len(n.units) for n in b.nets),
                   grown={f: sum(sum(x["sym"] is None for x in n.units.values()) for n, ff in zip(b.nets, fam) if ff == f) for f in FAMS},
                   food=len(food), poison=len(poison), food_last_third=sum(1 for s in food if s[0] >= late),
                   poison_last_third=sum(1 for s in poison if s[0] >= late), ticks=total_ticks,
                   behaviour=hashlib.sha256(repr((lf.meals, lf.scored, lf.firings)).encode()).hexdigest(),
                   pbits=getattr(b, "pbits", None))
        return lived
    S.live = live
    fam = "time" if cond == "time" else "seq"
    if cond == "allfood":
        from stage2_lang.worlds import W
        C.world = lambda f: W["allfood"]["text"]
    try:
        r = C.one((fam, "M", 560, seed, first))
    finally:
        S.live, C.world = original_live, original_world
    assert r["result"][6] is not None
    return dict(r, cond=cond, arm=arm, **out)


def run(jobs, name, timeout_note):
    t0 = time.monotonic()
    order = sorted(jobs, key=lambda j: -SECS[j[0]])          # longest first, two workers
    with ProcessPoolExecutor(2) as ex:
        res = list(ex.map(one, order, chunksize=1))
    raw = BASE.with_name(BASE.name + f"_{name}").with_suffix(".pkl")
    raw.write_bytes(pickle.dumps(res))
    meta = dict(wall_s=time.monotonic() - t0, raw=str(raw), raw_sha256=digest(raw), jobs=order, G=G, cap=CAP,
                config=dict(arm=C.ARM, P=560, rule="M", dt=.0025, LB_FINE=1, LB_LIVE=1, secs=SECS, conditions=dict(
                    seq="ladders.seq(17) 300 s", time="ladders.timing(3) 3000 s", allfood="stage2_lang.worlds.W['allfood']['text'] 300 s")),
                provenance=dict(revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                                dirty=subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
                                sha256={p: digest(ROOT / p) for p in SOURCES}, command=timeout_note))
    BASE.with_name(BASE.name + f"_{name}_capture").with_suffix(".json").write_text(json.dumps(meta, indent=1, default=str) + "\n")
    print(json.dumps({k: v for k, v in meta.items() if k not in ("jobs", "provenance")}, default=str), flush=True)
    return res


PILOT = [(c, a, 142000, f) for c in ("seq", "time", "allfood") for a in ("historical", "issued", "issued+gate") for f in ("red", "blue")] + \
        [("seq", "issued+gate disabled", 142000, f) for f in ("red", "blue")]


def pilot():
    assert len(PILOT) == 20 and len(set(PILOT)) == 20
    run(PILOT, "pilot", "timeout 900s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/spare_allowance_experiment.py --pilot")


def keyed(res):
    by = {}
    for r in res:
        k = (r["cond"], r["arm"], r["seed"], r["first"])
        assert k not in by, ("duplicate life", k)
        by[k] = r
    return by


def same_result(a, b):
    a, b = json.loads(json.dumps(a)), json.loads(json.dumps(b))
    return [v for i, v in enumerate(a) if i not in (5, 7)] == [v for i, v in enumerate(b) if i not in (5, 7)] and \
        ((a[7] is None and b[7] is None) or abs(a[7] - b[7]) < 1e-12)


def issued_scores(r, secs):
    out = {}
    for w, lo in (("full", 0.), ("last_third", 2 * secs / 3)):
        sel = [(p, y) for t, p, y in r["trace_acc"] if t >= lo]
        n = len(sel)
        out[w] = dict(n=n, bits=sum(-math.log2(min(1 - 1e-12, max(1e-12, p if y else 1 - p))) for p, y in sel) / n if n else None,
                      errors=sum(.5 if p == .5 else float((p > .5) != bool(y)) for p, y in sel) / n if n else None)
    return out


def first_divergence(a, b):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i, x[0]
    return None, None


def pilot_checks(by):
    st1 = {(l["rule"], l["seed"], l["first"]): l for l in json.loads((ROOT / "lab/v/alloc_stage1.json").read_text())["families"]["seq"]["lives"]}
    d111 = {(r["rule"], r["first"]): r for r in pickle.loads((ROOT / "lab/v/market_ledger_capture.pkl").read_bytes()) if r["rule"] == "M" and not r["observe"]}
    chk = {}
    fail = []

    def need(name, ok, detail=None):
        chk[name] = dict(ok=bool(ok), detail=detail)
        if not ok:
            fail.append(name)
    for f in ("red", "blue"):
        h = by["seq", "historical", 142000, f]
        need(f"historical seq {f} reproduces D78 stage 1", same_result(h["result"], st1["M", 142000, f]["result"]))
        need(f"historical seq {f} brain fingerprint equals D111's unobserved life", h["fingerprint"] == d111["M", f]["fingerprint"])
        i, d = by["seq", "issued", 142000, f], by["seq", "issued+gate disabled", 142000, f]
        need(f"disabled gate seq {f} = issued M: result", same_result(i["result"], d["result"]))
        need(f"disabled gate seq {f} = issued M: brain fingerprint", i["fingerprint"] == d["fingerprint"])
        need(f"disabled gate seq {f} = issued M: body/world fingerprint", i["body_fingerprint"] == d["body_fingerprint"])
        need(f"disabled gate seq {f} = issued M: prediction trace", i["trace_pred"] == d["trace_pred"] and i["trace_acc"] == d["trace_acc"])
        need(f"disabled gate seq {f}: no transfer by the gate", not d["gate"]["counters"].get("allowance-only transfers"))
        g = by["seq", "issued+gate", 142000, f]
        fo, ft = d["gate"]["first_opportunity"], g["gate"]["first_transfer"]
        need(f"seq {f}: disabled lives' first opportunity is the gate lives' first transfer", fo == ft, dict(first_opportunity=fo, first_transfer=ft))
    for c in ("seq", "time", "allfood"):
        for f in ("red", "blue"):
            i, g = by[c, "issued", 142000, f], by[c, "issued+gate", 142000, f]
            ft = g["gate"]["first_transfer"]
            idx, t = first_divergence(i["trace_pred"], g["trace_pred"])
            if ft is None:
                need(f"{c} {f}: no gate transfer, so traces identical", idx is None and len(i["trace_pred"]) == len(g["trace_pred"]))
            else:
                need(f"{c} {f}: prediction traces agree before the first gate transfer", idx is None or t >= ft["t"],
                     dict(first_transfer_t=ft["t"], first_divergent_prediction=idx, divergence_t=t))
            for r in (i, g):
                cr = r["credit"]
                need(f"{c} {r['arm']} {f}: issued reconstruction <= 1e-9", cr["max_reconstruction_error"] <= 1e-9, cr["max_reconstruction_error"])
                need(f"{c} {r['arm']} {f}: completed issued updates = accepted tastes", cr["counters"]["completed_accepted_updates"] == r["ntaste"])
            gs = g["gate"]
            need(f"{c} {f}: gate deletion transfers = M's counter", gs["counters"].get("transfers with deletion", 0) == g["alloc"]["transfers"])
            need(f"{c} {f}: allowance sum conserved", gs["allowance_sum"] == gs["allowance_sum_at_install"])
            need(f"{c} {f}: births after allowance-only transfers <= transfers",
                 gs["counters"].get("births_after_allowance_only_transfer", 0) <= gs["counters"].get("allowance-only transfers", 0))
            for r in (by[c, a, 142000, f] for a in ("historical", "issued", "issued+gate")):
                need(f"{c} {r['arm']} {f}: peak <= cap 2300", r["alloc"]["peak"] <= CAP and r["alloc"]["cap"] == CAP)
    for f in ("red", "blue"):
        i, g = by["allfood", "issued", 142000, f], by["allfood", "issued+gate", 142000, f]
        need(f"allfood {f}: gate and issued identical behaviour and state",
             same_result(i["result"], g["result"]) and i["behaviour"] == g["behaviour"] and i["fingerprint"] == g["fingerprint"]
             and i["body_fingerprint"] == g["body_fingerprint"])
        need(f"allfood {f}: zero gate transfers and no extra material",
             not g["gate"]["counters"].get("allowance-only transfers") and g["final_units"] == i["final_units"])
    return chk, fail


def report(by, keys):
    rows = {}
    for k in keys:
        r = by[k]
        c = k[0]
        res = r["result"]
        g = r.get("gate") or {}
        gc = g.get("counters", {})
        rows[" ".join(map(str, k))] = dict(
            last_third_efficiency=res[2] / res[3] if res[3] else None, last_third_gain=res[2], gain=res[0],
            gain_rate_per_10s=res[0] / SECS[c] * 10, food=r["food"], poison=r["poison"], food_last_third=r["food_last_third"],
            poison_last_third=r["poison_last_third"], accepted_tastes=r["ntaste"], issued=issued_scores(r, SECS[c]),
            births=r["births"], recycled=r["recycled"], peak_units=r["alloc"]["peak"], final_units=r["final_units"],
            grown=r["grown"], allowance_only_transfers=gc.get("allowance-only transfers", 0),
            deletion_transfers=r["alloc"]["transfers"], births_after_allowance_only=gc.get("births_after_allowance_only_transfer", 0),
            gate_opportunities=gc.get("requests: drawn donor leafless with spare allowance", 0),
            donor_scans=gc.get("donor scans"), unused_allowance=g.get("unused_allowance"), cpu_s=r["cpu_s"])
    return rows


def evidence(by):
    out = {}
    for c in ("seq", "time", "allfood"):
        for f in ("red", "blue"):
            r = by[c, "issued+gate", 142000, f]
            secs = SECS[c]
            gs, cr = r["gate"], r["credit"]["counters"]
            out[f"{c} {f}"] = dict(gate_opportunities=gs["opportunities"], distinct_recipient_streams=gs["opportunity_distinct_recipients"],
                                   distinct_opportunity_times=gs["opportunity_distinct_times"],
                                   awake_speakers_per_prediction=cr["awake_stream_forecasts"] / cr["predict_calls"],accepted_labels_per_s=r["ntaste"] / secs, labels_per_10s=r["ntaste"] / secs * 10,
                                   labels_per_200s_use_trace=r["ntaste"] / secs * 200,
                                   predictions_per_s=len(r["trace_pred"]) / secs)
    return out


def analyse():
    res = pickle.loads(BASE.with_name(BASE.name + "_pilot").with_suffix(".pkl").read_bytes())
    by = keyed(res)
    assert set(by) == set(PILOT), ("pilot keys", set(PILOT) ^ set(by))
    chk, fail = pilot_checks(by)
    out = dict(checks=chk, failed=fail, mechanical_checks_pass=not fail)
    gate_used_seq = [f for f in ("red", "blue") if by["seq", "issued+gate", 142000, f]["gate"]["counters"].get("allowance-only transfers", 0) > 0]
    out["gate_used_in_sequence_lives"] = gate_used_seq
    out["proceed_to_J"] = (not fail) and bool(gate_used_seq)
    if not fail:
        out["per_life"] = report(by, sorted(by))
        out["evidence"] = evidence(by)
        cpu = {c: float(np.mean([by[k]["cpu_s"] for k in by if k[0] == c and k[1] != "issued+gate disabled"])) for c in SECS}
        out["mean_cpu_s"] = cpu
        new_J = {"seq": 36, "time": 36, "allfood": 36}
        out["J_projection"] = dict(new_lives=new_J, cpu_s=sum(cpu[c] * n for c, n in new_J.items()),
                                   wall_s_two_workers=sum(cpu[c] * n for c, n in new_J.items()) / 2, budget_s=1800)
    out["capture"] = json.loads(BASE.with_name(BASE.name + "_pilot_capture").with_suffix(".json").read_text())
    out["analysis_sha256"] = digest(Path(__file__))
    BASE.with_name(BASE.name + "_pilot").with_suffix(".json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(json.dumps(dict(failed=fail, gate_used_seq=gate_used_seq, proceed_to_J=out["proceed_to_J"], J_projection=out.get("J_projection")), indent=1))
    if fail:
        raise SystemExit("mechanical checks failed: " + "; ".join(fail))


if __name__ == "__main__":
    {"--pilot": pilot, "--analyse": analyse}[sys.argv[1]]()

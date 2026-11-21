"""Action grid tables (R2, R4, R5, R6/R7), regenerated from the saved per-job rows only.

analyse(OUT): bench tables, historical reconciliation and costs, the 81-row development tables, factor marginals,
two-factor tables, bench-to-life associations, and the mechanical selection (selection.json, saved with its inputs'
hash before any confirmation job). confirm_report(OUT): fresh confirmation at three integration steps.
Valid means status "ok"; invalid jobs (status invalid_*) are diagnostic only and never enter a valid mean.
"""
from __future__ import annotations

import gzip
import hashlib
import itertools
import json
import math
import pickle
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
import ag_analysis as AA                                              # noqa: E402
from ag_analysis import boot, jdump, per_seed                         # noqa: E402

D180_LEDGER = ROOT / "lab/v/catalogue_brain_20261120/action_auth_ledger.jsonl.gz"
D180_ARCHIVE = ROOT / "lab/v/catalogue_brain_20261120_action_auth.pkl"


def load(OUT, name):
    p = OUT / f"{name}_ledger.jsonl.gz"
    if p.exists():
        with gzip.open(p, "rt") as f:
            return [json.loads(x) for x in f], True
    q = OUT / f"{name}.part.jsonl"
    rows = []
    if q.exists():
        for line in open(q):
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return rows, False


def fmt(ci, d=3):
    if ci is None or ci[0] is None:
        return "–"
    return f"{ci[0]:+.{d}f} [{ci[1]:+.{d}f}, {ci[2]:+.{d}f}]"


def f0(x, d=3):
    return "–" if x is None or (isinstance(x, float) and not math.isfinite(x)) else f"{x:.{d}f}"


def spearman(x, y):
    def ranks(a):
        a = np.asarray(a, float)
        o = np.argsort(a, kind="mergesort")
        r = np.empty(len(a))
        r[o] = np.arange(len(a))
        for v in np.unique(a):                                       # average ranks for ties
            m = a == v
            r[m] = r[m].mean()
        return r
    rx, ry = ranks(x), ranks(y)
    return float(np.corrcoef(rx, ry)[0, 1])


# ============================================================================================ R2 benches
def bench_tables(OUT, bench, cfgs, base):
    """Per row and window: fixed/other motor measures; active-minus-silent per (config, seed, P, removal, channel);
    seed means over channels; bootstrap over the 8 seeds."""
    idx = {}
    status = {}
    for r in bench:
        status[r["status"]] = status.get(r["status"], 0) + 1
        idx[(r["config"], r["arm"], r["removed"], r["seed"], r["P"], r["channel"])] = r

    def meas(r, w, role):
        if r is None or r["status"] not in ("ok", "invalid_realised"):
            return None
        mid = {"fixed": r["fixed_motor"], "other": r["other_motor"], "M0": 0, "M1": 1}[role]
        m = r["windows"][w]["motors"][f"M{mid}"]
        L = r["windows"][w]["window"][1] - r["windows"][w]["window"][0]
        return dict(events=m["events"], rearms=m["rearms"], unarmed=m["unarmed_s"] / L, high=m["high_s"] / L,
                    longest=m["longest_unarmed_s"], first=m["first_event_s"], vmin=m["Vmin"], vmax=m["Vmax"])
    out = {}
    from ag_jobs import P_BENCH, SCHEDULES, BENCH_REMOVALS
    for c in cfgs:
        tab = {}
        for P in P_BENCH:
            for rm in BENCH_REMOVALS:
                for sc in SCHEDULES:
                    for w in range(3):
                        for role in ("fixed", "other", "M0", "M1"):
                            for valid_only in (True,):
                                seeds_d, seeds_l, seeds_u, seeds_h, seeds_g, seeds_f = [], [], [], [], [], []
                                for s in range(8):
                                    dd, ll, uu, hh, gg, ff = [], [], [], [], [], []
                                    for ch in (0, 1):
                                        a = idx.get((c, sc, rm, s, P, ch))
                                        z = idx.get((c, "silent", rm, s, P, ch))
                                        if a is None or z is None or a["status"] != "ok" or z["status"] != "ok":
                                            continue
                                        ma, mz = meas(a, w, role), meas(z, w, role)
                                        dd.append(ma["events"] - mz["events"])
                                        ll.append(ma["events"])
                                        uu.append(ma["unarmed"])
                                        hh.append(ma["high"])
                                        gg.append(ma["longest"])
                                        if ma["first"] is not None and w == 1 and sc != "silent":
                                            ff.append(ma["first"] - (1.0 + a["jitter_s"]))
                                    if dd:
                                        seeds_d.append(np.mean(dd)); seeds_l.append(np.mean(ll)); seeds_u.append(np.mean(uu))
                                        seeds_h.append(np.mean(hh)); seeds_g.append(np.mean(gg))
                                        if ff:
                                            seeds_f.append(np.mean(ff))
                                tab[f"P{P}|{rm}|{sc}|w{w}|{role}"] = dict(
                                    minus_silent=boot(seeds_d) if sc != "silent" else None, level=boot(seeds_l),
                                    unarmed_frac=boot(seeds_u), high_frac=boot(seeds_h), longest_unarmed_s=boot(seeds_g),
                                    first_event_latency_s=boot(seeds_f) if seeds_f else None, n_seeds=len(seeds_d))
        out[c] = tab
    # setting minus baseline (paired seed, channel, P, removal, schedule) for key bench quantities
    vsb = {}
    for c in cfgs:
        if c == base:
            continue
        d = {}
        for sc in ("single", "train", "sustained"):
            for role in ("fixed", "other"):
                for P in (0.0, 0.3):
                    seeds = []
                    for s in range(8):
                        v = []
                        for ch in (0, 1):
                            a, z = idx.get((c, sc, "none", s, P, ch)), idx.get((c, "silent", "none", s, P, ch))
                            ab, zb = idx.get((base, sc, "none", s, P, ch)), idx.get((base, "silent", "none", s, P, ch))
                            if any(x is None or x["status"] != "ok" for x in (a, z, ab, zb)):
                                continue
                            v.append((meas(a, 1, role)["events"] - meas(z, 1, role)["events"])
                                     - (meas(ab, 1, role)["events"] - meas(zb, 1, role)["events"]))
                        if v:
                            seeds.append(np.mean(v))
                    d[f"{sc}|{role}|P{P}|w1"] = boot(seeds) + [len(seeds)]
        vsb[c] = d
    # drift, clipping, power per config
    phys = {}
    for c in cfgs:
        rows = [r for r in bench if r["config"] == c and r["status"] in ("ok", "invalid_realised")]
        phys[c] = dict(jobs=len(rows), invalid=sum(r["status"] != "ok" for r in rows),
                       P_drift_max=max((r["P_drift"] for r in rows), default=None),
                       clip_jobs=sum(r["clip_total"] > 0 for r in rows),
                       clip_nodes=sorted({k for r in rows for w in r["windows"] for k in w["clip_by_node"]}),
                       power_W_mean=float(np.mean([r["power_W"] for r in rows])) if rows else None,
                       silent_events_per_s=float(np.mean([sum(r["windows"][2]["motors"][m]["events"] for m in ("M0", "M1"))
                                                          / 6.75 for r in rows if r["arm"] == "silent"
                                                          and r["removed"] == "none"])) if rows else None)
    return dict(per_config=out, vs_baseline=vsb, physical=phys, status_counts=status)


# ============================================================================================ R4 reconciliation
def reconcile(OUT, dev, base):
    with gzip.open(D180_LEDGER, "rt") as f:
        hist = [json.loads(x) for x in f]
    H = {(r["arm"], r["seed"], r["poison"]): r for r in hist}
    mine = {(r["arm"], r["seed"], r["poison"]): r for r in dev if r["config"] == base}
    traces = {}
    with open(D180_ARCHIVE, "rb") as f:
        while True:
            try:
                r = pickle.load(f)
            except EOFError:
                break
            traces[(r["arm"], r["seed"], r["poison"])] = hashlib.sha256(np.asarray(r["trace"], np.float32).tobytes()).hexdigest()[:16]
    rows, disc = [], []
    for k, h in sorted(H.items(), key=lambda kv: str(kv[0])):
        m = mine.get(k)
        if m is None:
            disc.append(dict(key=list(k), problem="missing in reproduction"))
            continue
        chk = dict(meals=[list(x) for x in m["meals"]] == [list(x) for x in h["meals"]], firings=m["firings"] == h["firings"],
                   motor_events=m["motor_events"] == h["motor_events"], node_events=m["node_events"] == h["node_events"],
                   clip_steps=m["clip_steps"] == h["clip_steps"], arrays_hash=m["arrays_hash"] == h["arrays_hash"],
                   Pf_hash=m.get("Pf_hash") == h.get("Pf_hash"), trace=m.get("trace_sha") == traces.get(k),
                   power=abs(m["power_W"] - h["power_W"]) <= 1e-12 * abs(h["power_W"]),
                   wiring=m["sensor_map"] == h["sensor_map"] and m["motor_map"] == h["motor_map"] and m["sides"] == h["sides"])
        if not all(chk.values()):
            disc.append(dict(key=list(k), failed=[a for a, v in chk.items() if not v]))
        rows.append(chk)
    extra = sorted(set(map(str, mine)) - set(map(str, H)))
    res = dict(historical=len(H), reproduced=len(rows), all_match=not disc and len(rows) == len(H) == 384,
               discrepancies=disc, extra=extra,
               per_check={c: sum(r[c] for r in rows) for c in (rows[0] if rows else {})})
    return res


def parts_table(cfgs):
    """minimal.spice.count of chip.py blocks for each configuration and removal (nominal, no SPICE)."""
    from minimal.spice import count
    import importlib.util
    spec = importlib.util.spec_from_file_location("d180_checks", ROOT / "lab/catalogue_brain_20261120/checks.py")
    ck = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ck)
    from ag_engine import variants, CONFIGS, REMOVALS
    out = {}
    for c in cfgs:
        g = variants.graph(CONFIGS[c])
        out[c] = {rm: count(ck.spec_of(g, REMOVALS[rm])) for rm in ("none", "no_explore", "no_sensory")}
    return out


# ============================================================================================ R5 development
def dev_tables(dev, cfgs):
    by = {}
    for r in dev:
        by.setdefault(r["config"], {}).setdefault(r["arm"], []).append(r)
    T = {}
    for c in cfgs:
        arms = by.get(c, {})
        valid = {a: [r for r in arms.get(a, []) if r["status"] == "ok"] for a in AA.ARMS}
        allr = {a: [r for r in arms.get(a, []) if r["status"] in ("ok", "invalid_realised")] for a in AA.ARMS}
        n_rows = sum(len(v) for v in arms.values())
        n_ok = sum(len(v) for v in valid.values())
        finite = all(math.isfinite(r["m"]["net"]) for v in valid.values() for r in v)
        complete = n_rows == 384 and n_ok == 384 and finite
        statuses = {}
        for v in arms.values():
            for r in v:
                statuses[r["status"]] = statuses.get(r["status"], 0) + 1
        t = dict(rows=n_rows, valid=n_ok, complete=complete, statuses=statuses,
                 summary={a: AA.arm_summary(valid[a]) if valid[a] else None for a in AA.ARMS},
                 contrasts=AA.contrasts(valid) if all(valid[a] for a in AA.ARMS) else None,
                 diagnostic_including_invalid=None)
        if not complete and all(allr[a] for a in AA.ARMS):
            t["diagnostic_including_invalid"] = dict(
                informed_net=boot(list(per_seed(allr["informed"], lambda r: r["m"]["net"]).values())),
                informed_food=boot(list(per_seed(allr["informed"], lambda r: r["m"]["food_rate_final"]).values())),
                contrasts=AA.contrasts(allr), label="DIAGNOSTIC ONLY: includes invalid_realised lives")
        inf = valid["informed"]
        t["informed_net"] = float(np.mean(list(per_seed(inf, lambda r: r["m"]["net"]).values()))) if inf else float("nan")
        t["informed_food"] = float(np.mean(list(per_seed(inf, lambda r: r["m"]["food_rate_final"]).values()))) if inf else float("nan")
        t["clip_lives"] = sum(r["clip_steps"] > 0 for v in arms.values() for r in v)
        t["clip_nodes"] = sorted({k for v in arms.values() for r in v for k in r["clip_by_node"]})
        t["gates"] = AA.gated_edges([r for r in valid["informed"]]) if valid["informed"] else None
        t["gates_by_arm"] = {a: AA.gated_edges(valid[a]) for a in AA.ARMS if valid[a]}
        T[c] = t
    return T


def factor_marginals(dev, cfgs, T, base_cfgs):
    """Marginal contrasts over seeds valid for ALL configurations (selection by component draw, not outcome) and the
    six two-factor tables; plus a diagnostic version including invalid_realised lives."""
    out = {}
    for label, statuses in (("valid_seeds_only", ("ok",)), ("diagnostic_including_invalid", ("ok", "invalid_realised"))):
        by = {}
        for r in dev:
            if r["arm"] == "informed":
                by.setdefault(r["config"], []).append(r)
        bad_seeds = {r["seed"] for r in dev if r["status"] not in statuses}
        res = {}
        for key in ("net", "food_rate_final"):
            seedm = {c: {s: v for s, v in per_seed(by[c], lambda r: r["m"][key]).items() if s not in bad_seeds}
                     for c in cfgs if c in by}
            seeds = sorted(set.intersection(*[set(v) for v in seedm.values()]))
            marg = {}
            for f, levels in AA.FACTORS.items():
                for L in levels:
                    if L == AA.BASE_LEVEL[f]:
                        continue
                    A_ = [c for c in seedm if base_cfgs[c][f] == L]
                    B_ = [c for c in seedm if base_cfgs[c][f] == AA.BASE_LEVEL[f]]
                    diffs = [np.mean([seedm[c][s] for c in A_]) - np.mean([seedm[c][s] for c in B_]) for s in seeds]
                    marg[f"{f}: {L} minus {AA.BASE_LEVEL[f]}"] = dict(ci=boot(diffs), n_seeds=len(seeds),
                                                                      n_configs=[len(A_), len(B_)])
            two = {}
            for f1, f2 in itertools.combinations(AA.FACTORS, 2):
                tab = {}
                for l1 in AA.FACTORS[f1]:
                    for l2 in AA.FACTORS[f2]:
                        cs = [c for c in seedm if base_cfgs[c][f1] == l1 and base_cfgs[c][f2] == l2]
                        tab[f"{l1}|{l2}"] = float(np.mean([np.mean([seedm[c][s] for s in seeds]) for c in cs]))
                two[f"{f1} x {f2}"] = tab
            res[key] = dict(marginals=marg, two_factor=two, seeds=seeds, excluded_seeds=sorted(bad_seeds))
        out[label] = res
    return out


def associations(B, T, cfgs):
    """Predeclared (PROTOCOL): P=0.30, removal none, window [1,3.25), fixed side; vs development informed net."""
    rows = []
    for c in cfgs:
        tb = B["per_config"][c]
        a = tb["P0.3|none|single|w1|fixed"]["minus_silent"]
        b = tb["P0.3|none|sustained|w1|fixed"]["minus_silent"]
        u = tb["P0.3|none|sustained|w1|fixed"]["unarmed_frac"]
        rows.append(dict(config=c, single_excess=a[0] if a else None, sustained_excess=b[0] if b else None,
                         sustained_unarmed=u[0] if u else None, informed_net=T[c]["informed_net"],
                         complete=T[c]["complete"]))
    ok = [r for r in rows if r["complete"] and None not in (r["single_excess"], r["sustained_excess"], r["sustained_unarmed"])]
    rho = {k: spearman([r[k] for r in ok], [r["informed_net"] for r in ok]) if len(ok) > 2 else None
           for k in ("single_excess", "sustained_excess", "sustained_unarmed")}
    return dict(rows=rows, spearman_complete_configs=rho, n=len(ok), note="descriptive; no other associations examined")


def analyse(OUT):
    from ag_engine import CONFIGS, BASELINE
    import ag_jobs as J
    cfgs = sorted(CONFIGS)
    bench, bdone = load(OUT, "bench")
    dev, ddone = load(OUT, "develop")
    bkeys = json.loads((OUT / "bench_jobs.json").read_text())["keys"]
    dkeys = json.loads((OUT / "develop_jobs.json").read_text())["keys"]
    bmiss, dmiss = AA.validate(bench, bkeys), AA.validate(dev, dkeys)
    ledger = dict(bench=dict(expected=len(bkeys), rows=len(bench), missing=len(bmiss), complete_ledger=bdone),
                  develop=dict(expected=len(dkeys), rows=len(dev), missing=len(dmiss), complete_ledger=ddone))
    for name, rows in (("bench", bench), ("develop", dev)):
        st = {}
        for r in rows:
            st[r["status"]] = st.get(r["status"], 0) + 1
        ledger[name]["status"] = st
    jdump(OUT / "ledger_audit.json", ledger)
    B = bench_tables(OUT, bench, cfgs, BASELINE)
    jdump(OUT / "bench_tables.json", B)
    rec = reconcile(OUT, dev, BASELINE)
    jdump(OUT / "reconciliation.json", rec)
    parts = parts_table(cfgs)
    T = dev_tables(dev, cfgs)
    F = factor_marginals(dev, cfgs, T, CONFIGS)
    A = associations(B, T, cfgs)
    jdump(OUT / "dev_tables.json", T)
    jdump(OUT / "factors.json", F)
    jdump(OUT / "associations.json", A)
    jdump(OUT / "parts.json", parts)
    write_markdown(OUT, ledger, B, rec, parts, T, F, A, cfgs, BASELINE)
    historical_md(OUT, rec, T, parts, BASELINE)
    # mechanical selection, saved before any confirmation job
    table = {c: dict(complete=T[c]["complete"], informed_net=T[c]["informed_net"], informed_food=T[c]["informed_food"])
             for c in cfgs if c != BASELINE}
    ranked = AA.rank(table)
    inputs = json.dumps(table, sort_keys=True, default=float)
    sel = dict(ranked=ranked, selected=ranked[:3], inputs=table, inputs_sha256=hashlib.sha256(inputs.encode()).hexdigest(),
               develop_ledger_complete=ddone and not dmiss, rule="descending informed net, descending informed food, "
               "ascending ID; complete finite nonbaseline rows only; no interval or threshold gate",
               excluded_incomplete=sorted(c for c in table if not table[c]["complete"]))
    p = OUT / "selection.json"
    if p.exists():
        old = json.loads(p.read_text())
        if old["selected"] != sel["selected"] or old["inputs_sha256"] != sel["inputs_sha256"]:
            raise SystemExit("selection.json exists with different content: refusing to overwrite")
    elif ddone and not dmiss:
        jdump(p, sel)
    else:
        print("development incomplete: selection NOT saved")
    print("selected", sel["selected"])
    return sel


def write_markdown(OUT, ledger, B, rec, parts, T, F, A, cfgs, base):
    L = ["# Action grid — development tables (R2, R4, R5)", "",
         "Regenerated from saved per-job rows by `ag_report.analyse`. Final third [200/3,100) s, per 10 s; seed means "
         "(red/blue averaged), 10,000 bootstrap resamples, RNG 182, 95% percentile intervals. **Development intervals "
         "are exploratory and subject to selection over 81 settings.** Valid = status ok; invalid jobs are excluded "
         "from every valid mean.", "", "## Ledger", "", "```", json.dumps(ledger, indent=1), "```", ""]
    L += ["## Development: all 81 settings (informed arm and contrasts)", "",
          "Columns: informed net; informed food rate; informed − neutral net; informed − reversed; informed − "
          "no_explore; informed − no_sensory; all-food informed − neutral food rate; informed stranded fraction; "
          "lives with any pre-clip rail excursion (all arms, of 384); valid lives.", "",
          "| setting | inf net | inf food | −neutral | −reversed | −no_explore | −no_sensory | all-food Δfood | stranded | clip lives | valid |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in sorted(cfgs, key=lambda c: (-T[c]["informed_net"] if math.isfinite(T[c]["informed_net"]) else 9, c)):
        t = T[c]
        s = t["summary"]["informed"]
        C = t["contrasts"] or {}
        g = lambda k: fmt(C[k]["ci"], 2) if k in C else "–"
        L.append(f"| {c}{' (baseline)' if c == base else ''} | {fmt(s['net'], 3) if s else '–'} | "
                 f"{f0(s['food_rate_final'][0]) if s else '–'} | {g('informed_minus_neutral')} | "
                 f"{g('informed_minus_reversed')} | {g('informed_minus_no_explore')} | {g('informed_minus_no_sensory')} | "
                 f"{g('allfood_informed_minus_neutral_food')} | {f0(s['stranded'][0], 2) if s else '–'} | "
                 f"{t['clip_lives']} | {t['valid']}/{t['rows']} |")
    L += ["", "With taste withheld, an arm in which P has no effect (neutral, no_explore, no_sensory: equal or irrelevant "
          "memories) makes a seed's red-poison and blue-poison lives physically identical, so its net is exactly 0 by "
          "construction and informed − that arm equals informed net (D181). The food-rate contrasts below are "
          "descriptive additions that do not share this identity.", "",
          "| setting | food: inf − neutral | inf − reversed | inf − no_explore | inf − no_sensory |", "|---|---|---|---|---|"]
    for c in cfgs:
        C = T[c]["contrasts"] or {}
        g = lambda k: fmt(C[k]["ci"], 2) if k in C else "–"
        L.append(f"| {c} | {g('food_informed_minus_neutral')} | {g('food_informed_minus_reversed')} | "
                 f"{g('food_informed_minus_no_explore')} | {g('food_informed_minus_no_sensory')} |")
    L += ["", "Settings with invalid lives (realised component limit failed), diagnostic informed net including them:", ""]
    for c in cfgs:
        d = T[c]["diagnostic_including_invalid"]
        if d:
            L.append(f"- {c}: statuses {T[c]['statuses']}; diagnostic informed net {fmt(d['informed_net'])}, "
                     f"food {fmt(d['informed_food'])}")
    L += ["", "## Seven arm groups, all settings (valid lives; net or food rate per 10 s, mean over seeds)", "",
          "| setting | " + " | ".join(AA.ARMS) + " |", "|---|" + "---|" * len(AA.ARMS)]
    for c in cfgs:
        S = T[c]["summary"]
        cells = []
        for a in AA.ARMS:
            s = S[a]
            if s is None:
                cells.append("–")
            else:
                cells.append(f"net {s['net'][0]:+.3f} / food {s['food_rate_final'][0]:.3f}")
        L.append(f"| {c} | " + " | ".join(cells) + " |")
    L += ["", "## Factor marginals on informed net and food (level − baseline level, same other factors, within seed)", ""]
    for label, res in F.items():
        L.append(f"### {label} (excluded seeds: {res['net']['excluded_seeds']})")
        L.append("")
        L.append("| contrast | informed net | informed food rate |")
        L.append("|---|---|---|")
        for k in res["net"]["marginals"]:
            L.append(f"| {k} | {fmt(res['net']['marginals'][k]['ci'])} | {fmt(res['food_rate_final']['marginals'][k]['ci'])} |")
        L.append("")
    L += ["### Two-factor mean tables of informed net (valid seeds only; rows first factor, columns second)", ""]
    for k, tab in F["valid_seeds_only"]["net"]["two_factor"].items():
        f1, f2 = k.split(" x ")
        L.append(f"**{k}**")
        L.append("")
        L.append("| " + f1 + " \\ " + f2 + " | " + " | ".join(str(x) for x in AA.FACTORS[f2]) + " |")
        L.append("|---|" + "---|" * 3)
        for l1 in AA.FACTORS[f1]:
            L.append(f"| {l1} | " + " | ".join(f"{tab[f'{l1}|{l2}']:+.3f}" for l2 in AA.FACTORS[f2]) + " |")
        L.append("")
    L += ["These are effects within this grid, not a unique causal decomposition: speed also changes noise and "
          "trajectories.", "", "## Activity, coordination and costs (informed arm, seed means)", "",
          "| setting | power nW | body firings | motor energy µJ | high frac | unarmed frac | longest unarmed s | "
          "see-either s | path mm | paired frac | near-opposite frac | fixed unarmed@pulse | fixed ev 0–50ms | other ev 0–50ms | parts (T/R/C) |",
          "|---|" + "---|" * 15]
    for c in cfgs:
        s = T[c]["summary"]["informed"]
        if s is None:
            continue
        p = parts[c]["none"]
        L.append(f"| {c} | {s['power_W'][0] * 1e9:.1f} | {s['body_firings'][0]:.0f} | {s['motor_energy_J'][0] * 1e6:.1f} | "
                 f"{s['high_frac'][0]:.3f} | {s['unarmed_frac'][0]:.3f} | {s['longest_unarmed_s'][0]:.3f} | "
                 f"{s['see_either_s'][0]:.1f} | {s['path_m'][0] * 1e3:.0f} | {f0(s['paired_fraction'][0])} | "
                 f"{f0(s['near_opposite_fraction'][0])} | {f0(s['fixed_unarmed_at_pulse'][0])} | "
                 f"{f0(s['fixed_events_0_50'][0])} | {f0(s['other_events_0_50'][0])} | "
                 f"{p.get('T')}/{p.get('R')}/{p.get('C')} |")
    L += ["", "Power is what the supply delivers (engine accounting); motor energy is body firings × the guessed "
          "20 nJ (minimal/spec.FIRING); parts are nominal minimal.spice.count of chip.py blocks (no SPICE). Memory "
          "pump energy is unmeasured. Edge source-event counts and gate duty are in dev_tables.json (`gates`): "
          "labelled event proxies, not communication energy.", ""]
    L += ["## Bench summaries (R2): P = 0.30, no removal, window [1, 3.25) s, active − silent motor events, seed means", "",
          "| setting | single fixed | single other | train fixed | sustained fixed | sustained other | sustained fixed unarmed | "
          "no_explore sustained fixed | P=0 single other | silent ev/s | P drift max | clip jobs |", "|---|" + "---|" * 11]
    for c in cfgs:
        tb = B["per_config"][c]
        g = lambda k, i=0: f0((tb[k]["minus_silent"] or [None])[i], 2) if tb[k]["minus_silent"] else "–"
        ph = B["physical"][c]
        L.append(f"| {c} | {g('P0.3|none|single|w1|fixed')} | {g('P0.3|none|single|w1|other')} | "
                 f"{g('P0.3|none|train|w1|fixed')} | {g('P0.3|none|sustained|w1|fixed')} | "
                 f"{g('P0.3|none|sustained|w1|other')} | {f0(tb['P0.3|none|sustained|w1|fixed']['unarmed_frac'][0], 2)} | "
                 f"{g('P0.3|no_explore|sustained|w1|fixed')} | {g('P0.0|none|single|w1|other')} | "
                 f"{f0(ph['silent_events_per_s'], 1)} | {f0(ph['P_drift_max'], 4)} | {ph['clip_jobs']} |")
    L += ["", "Signed differences can be negative. Sustained response is descriptive (no target rate). Full tables "
          "(every P, removal, schedule, window, role, and setting − baseline) in bench_tables.json.", "",
          "## Predeclared bench-to-life associations (descriptive)", "",
          f"Spearman across {A['n']} complete settings: " + ", ".join(f"{k} {f0(v, 2)}" for k, v in A["spearman_complete_configs"].items()),
          "", "## Historical reconciliation (summary; see historical_reconciliation.md)", "",
          f"Reproduced {rec['reproduced']}/{rec['historical']} D180 lives; all checks match: {rec['all_match']}; "
          f"per-check matches {rec['per_check']}; discrepancies {len(rec['discrepancies'])}.", ""]
    (OUT / "dev_tables.md").write_text("\n".join(L) + "\n")


# ============================================================================================ R6/R7 confirmation
def confirm_report(OUT):
    from ag_engine import BASELINE
    rows, done = load(OUT, "confirm")
    keys = json.loads((OUT / "confirm_jobs.json").read_text())["keys"]
    miss = AA.validate(rows, keys)
    fz = json.loads((OUT / "confirm_freeze.json").read_text())
    cands = fz["configs"][1:]
    by = {}
    for r in rows:
        by.setdefault((r["config"], r["ratio"]), {}).setdefault(r["arm"], []).append(r)
    st = {}
    for r in rows:
        st[r["status"]] = st.get(r["status"], 0) + 1
    R = dict(ledger=dict(expected=len(keys), rows=len(rows), missing=len(miss), complete_ledger=done, status=st),
             configs=fz["configs"], seeds=fz["seeds"], per_ratio={}, primary={}, gates={}, no_harm={}, physical={},
             convergence={}, levels={})
    V = lambda c, r, a: [x for x in by.get((c, r), {}).get(a, []) if x["status"] == "ok"]
    net = lambda x: x["m"]["net"]
    food = lambda x: x["m"]["food_rate_final"]
    strand = lambda x: x["m"]["stranded"]
    for ratio in (1, 2, 4):
        pr = {}
        for c in fz["configs"]:
            arms = {a: V(c, ratio, a) for a in AA.ARMS}
            pr[c] = dict(summary={a: AA.arm_summary(v) if v else None for a, v in arms.items()},
                         contrasts=AA.contrasts(arms) if all(arms.values()) else None,
                         d180_job_informed=AA.d180_job(arms["informed"]) if arms["informed"] else None,
                         clip_lives=sum(x["clip_steps"] > 0 for a in AA.ARMS for x in by.get((c, ratio), {}).get(a, [])),
                         invalid=sum(x["status"] != "ok" for a in AA.ARMS for x in by.get((c, ratio), {}).get(a, [])),
                         lives=sum(len(by.get((c, ratio), {}).get(a, [])) for a in AA.ARMS))
        R["per_ratio"][str(ratio)] = pr
    for c in cands:
        P, G, NH, PH = {}, {}, {}, {}
        for ratio in (1, 2, 4):
            ci95 = AA.paired(V(c, ratio, "informed"), V(BASELINE, ratio, "informed"), net)
            ciB = AA.paired(V(c, ratio, "informed"), V(BASELINE, ratio, "informed"), net, AA.Q_BONF)
            P[str(ratio)] = dict(ci95=ci95["ci"], ci_bonferroni_98_333=ciB["ci"], n=ci95["n"])
            fh = AA.paired(V(c, ratio, "informed_allfood"), V(BASELINE, ratio, "informed_allfood"), food)
            sh = AA.paired(V(c, ratio, "informed"), V(BASELINE, ratio, "informed"), strand)
            NH[str(ratio)] = dict(allfood_food=fh["ci"], allfood_ok=fh["ci"][1] is not None and fh["ci"][1] > -0.05,
                                  stranding=sh["ci"], stranding_ok=sh["ci"][2] is not None and sh["ci"][2] < 0.05)
        lows = [P[str(r)]["ci_bonferroni_98_333"][1] for r in (1, 2, 4)]
        improved = all(x is not None and x > 0 for x in lows)
        practical = all(x is not None and x > 0.10 for x in lows)
        crs = [x for r in (1, 2, 4) for a in AA.ARMS for x in by.get((c, r), {}).get(a, [])]
        ok_all = len(crs) == 3 * 128 * 12 and all(x["status"] == "ok" for x in crs)
        clip = sum(x["clip_steps"] > 0 for x in crs)
        PH = dict(lives=len(crs), all_valid=ok_all, lives_with_preclip=clip,
                  nodes=sorted({k for x in crs for k in x["clip_by_node"]}),
                  eligible=bool(ok_all and clip == 0))
        R["primary"][c] = dict(by_ratio=P, improved=improved, practically_established=practical,
                               corrected_lower_bounds=lows)
        R["no_harm"][c] = NH
        R["physical"][c] = PH
        # convergence: per-seed change of the candidate-minus-baseline contrast between successive halvings
        conv = {}
        for metric, arm, f in (("informed_net", "informed", net), ("allfood_food", "informed_allfood", food),
                               ("stranding", "informed", strand)):
            dd = {}
            for r in (1, 2, 4):
                a, b = per_seed(V(c, r, arm), f), per_seed(V(BASELINE, r, arm), f)
                dd[r] = {s: a[s] - b[s] for s in set(a) & set(b)}
            for r0, r1 in ((1, 2), (2, 4)):
                s = sorted(set(dd[r0]) & set(dd[r1]))
                ci = boot([dd[r1][k] - dd[r0][k] for k in s])
                conv[f"{metric}: r{r1} - r{r0}"] = dict(ci=ci, n=len(s),
                                                         within=ci[1] is not None and ci[1] >= -0.05 and ci[2] <= 0.05)
            conv[f"{metric}: levels"] = {str(r): boot(list(dd[r].values())) for r in (1, 2, 4)}
        R["convergence"][c] = conv
    # baseline physical record too
    crs = [x for r in (1, 2, 4) for a in AA.ARMS for x in by.get((BASELINE, r), {}).get(a, [])]
    R["physical"][BASELINE] = dict(lives=len(crs), lives_with_preclip=sum(x["clip_steps"] > 0 for x in crs),
                                   nodes=sorted({k for x in crs for k in x["clip_by_node"]}))
    jdump(OUT / "confirm_tables.json", R)
    write_confirm_md(OUT, R, cands, BASELINE)
    return R


def write_confirm_md(OUT, R, cands, base):
    L = ["# Action grid — fresh confirmation (R6/R7)", "",
         f"Seeds {R['seeds'][0]}–{R['seeds'][1]} (128, fresh: ag_seeds audit), coupled circuit noise at DT, DT/2, DT/4 "
         "(ratios 1, 2, 4); body tick unchanged. Final third, per 10 s; seed-paired; 10,000 resamples, RNG 182.", "",
         "```", json.dumps(R["ledger"], indent=1), "```", "",
         "## Primary: candidate − baseline informed net (95% and Bonferroni-3 98.333% intervals)", "",
         "| candidate | ratio | 95% | 98.333% | improved (corr. lower > 0 at all ratios) | practical (> +0.10 at all) |",
         "|---|---|---|---|---|---|"]
    for c in cands:
        p = R["primary"][c]
        for r in ("1", "2", "4"):
            L.append(f"| {c} | {r} | {fmt(p['by_ratio'][r]['ci95'])} | {fmt(p['by_ratio'][r]['ci_bonferroni_98_333'])} | "
                     f"{p['improved'] if r == '1' else ''} | {p['practically_established'] if r == '1' else ''} |")
    L += ["", "The Bonferroni correction covers the three primary contrasts only; secondary endpoints are unadjusted.", "",
          "## Levels: informed arm by setting and ratio", "",
          "| setting | ratio | informed net | informed food | stranded | all-food informed food | inf−neutral | inf−reversed | inf−no_explore | inf−no_sensory | all-food inf−neutral | clip lives / lives |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in R["configs"]:
        for r in ("1", "2", "4"):
            pr = R["per_ratio"][r][c]
            s = pr["summary"]["informed"]
            fa = pr["summary"]["informed_allfood"]
            C = pr["contrasts"] or {}
            g = lambda k: fmt(C[k]["ci"], 2) if k in C else "–"
            L.append(f"| {c}{' (baseline)' if c == base else ''} | {r} | {fmt(s['net']) if s else '–'} | "
                     f"{fmt(s['food_rate_final']) if s else '–'} | {fmt(s['stranded'], 2) if s else '–'} | "
                     f"{fmt(fa['food_rate_final']) if fa else '–'} | {g('informed_minus_neutral')} | "
                     f"{g('informed_minus_reversed')} | {g('informed_minus_no_explore')} | {g('informed_minus_no_sensory')} | "
                     f"{g('allfood_informed_minus_neutral_food')} | {pr['clip_lives']}/{pr['lives']} |")
    L += ["", "## D180 absolute gates (informed arm): food rate lower ≥ 1/10 s; food − 3·poison lower ≥ 0; "
          "seed-level Wilson stranding upper ≤ 0.05", "", "| setting | ratio | food rate | food−3poison | stranding seeds (k/n, Wilson) | all |",
          "|---|---|---|---|---|---|"]
    for c in R["configs"]:
        for r in ("1", "2", "4"):
            j = R["per_ratio"][r][c]["d180_job_informed"]
            if j:
                L.append(f"| {c} | {r} | {fmt(j['food_rate'])} ({j['food_rate_ok']}) | {fmt(j['job_linear'])} ({j['ratio_ok']}) | "
                         f"{j['stranding_seed_any'][0]}/{j['stranding_seed_any'][1]} [{f0(j['stranding_seed_any'][3], 3)}, "
                         f"{f0(j['stranding_seed_any'][4], 3)}] ({j['stranding_ok']}) | {j['all']} |")
    L += ["", "An action-only success is not a learner.", "", "## No-harm (candidate − baseline)", "",
          "| candidate | ratio | all-food food rate (lower > −0.05?) | stranding (upper < +0.05?) |", "|---|---|---|---|"]
    for c in cands:
        for r in ("1", "2", "4"):
            n = R["no_harm"][c][r]
            L.append(f"| {c} | {r} | {fmt(n['allfood_food'])} ({n['allfood_ok']}) | {fmt(n['stranding'])} ({n['stranding_ok']}) |")
    L += ["", "## Physical eligibility", "", "| setting | lives | all valid | lives with pre-clip excursion | nodes | eligible |",
          "|---|---|---|---|---|---|"]
    for c in R["configs"]:
        p = R["physical"][c]
        L.append(f"| {c} | {p['lives']} | {p.get('all_valid', '–')} | {p['lives_with_preclip']} | {', '.join(p['nodes'])} | "
                 f"{p.get('eligible', 'baseline (reference)')} |")
    L += ["", "## Numerical convergence: change of candidate − baseline contrast per halving (95%, must lie in ±0.05)", "",
          "| candidate | quantity | change | within ±0.05 |", "|---|---|---|---|"]
    for c in cands:
        for k, v in R["convergence"][c].items():
            if k.endswith("levels"):
                L.append(f"| {c} | {k} | " + "; ".join(f"r{r}: {fmt(x)}" for r, x in v.items()) + " | |")
            else:
                L.append(f"| {c} | {k} | {fmt(v['ci'])} | {v['within']} |")
    (OUT / "confirm_tables.md").write_text("\n".join(L) + "\n")


def historical_md(OUT, rec, T, parts, base):
    """R4: corrections to D180's stale reporting statements (by reference) and its costs/activity reconstructed from
    the reproduced baseline lives. The original D180 report and checklist are not edited."""
    t = T[base]
    L = ["# Historical reconciliation (R4) — D180/D181 reporting, reconstructed from reproduced lives", "",
         "Generated by `ag_report.analyse`. The D180 executor's files (`../catalogue_brain_20261120/REPORT.md`, "
         "`CHECKLIST.md`) are NOT edited; corrections are made here by reference, as D182 requested.", "",
         "## Reproduction", "",
         f"The grid's baseline setting reran D180's 384 authorised informed-action lives (development seeds 8–39, native "
         f"noise, 100 s) with the passive observer. Reproduced {rec['reproduced']}/{rec['historical']}; every check matches: "
         f"**{rec['all_match']}**. Per check (lives matching): {rec['per_check']}. "
         f"Discrepancies: {len(rec['discrepancies'])}. Trace check: SHA-256 of each life's ten-node float32 trace against "
         "the archived D180 trace (`lab/v/catalogue_brain_20261120_action_auth.pkl`). The historical ledger has no motor-"
         "event sequences, so event-time identity is not claimed from counts; the new event sequences are recorded.", "",
         "## Stale statements corrected by reference", "",
         "| D180 location | stale statement | correction |", "|---|---|---|",
         "| CHECKLIST.md R9 | \"no lives ran: no failed-life/acquisition accounting applies\" | 384 informed-action lives "
         "ran (authorised addendum, `action_auth_ledger.jsonl.gz`); their accounting is below and in dev_tables.json. |",
         "| REPORT.md, 'Incomplete or not-triggered work' | \"Nothing required by a triggered obligation is incomplete\" | "
         "Per-connection source-event and gate-activity accounting was not presented for every arm (D182). Provided "
         "below for all seven arms. |",
         "| REPORT.md, ledger/limitations | pre-addendum status (no lives) not labelled historical | Superseded by the "
         "addendum; read with D182's qualification. |",
         "| HANDOFF.md, writer size | 0.21–0.99 V written as \"two to ten times\" the 0.3 V range | about 0.7–3.3 times (D182). |",
         "| REPORT.md addendum, diagnosis 1 | encounter rate (explorers' walk) ranked ahead of sensory authority | a hypothesis, "
         "not a causal priority (D182); this grid's development and bench tables test it. |", "",
         "## Costs and activity per arm (baseline, reproduced lives; seed means with 95% intervals)", "",
         "| arm | power nW | body firings /life | motor energy µJ /life | circuit energy µJ /life | high frac | unarmed frac | "
         "lives with rail excursion | parts T/R/C/D/sources |", "|---|---|---|---|---|---|---|---|---|"]
    for a in AA.ARMS:
        s = t["summary"][a]
        rm = "no_explore" if a == "no_explore" else ("no_sensory" if a == "no_sensory" else "none")
        p = parts[base][rm]
        L.append(f"| {a} | {fmt([x * 1e9 for x in s['power_W'][:3]], 1)} | {fmt(s['body_firings'][:3], 0)} | "
                 f"{fmt([x * 1e6 for x in s['motor_energy_J'][:3]], 2)} | {fmt([x * 1e6 for x in s['circuit_energy_J'][:3]], 2)} | "
                 f"{f0(s['high_frac'][0])} | {f0(s['unarmed_frac'][0])} | {s['clip_lives']}/{s['lives']} | "
                 f"{p.get('T')}/{p.get('R')}/{p.get('C')}/{p.get('D')}/{p.get('sources')} |")
    L += ["", "Power: what the supply delivers (engine accounting). Motor energy: body firings × 20 nJ (guessed, "
          "minimal/spec.FIRING). Parts: nominal minimal.spice.count (no SPICE). Memory charge-pump energy: unmeasured.", "",
          "## Per-connection source events and gate activity (baseline, per arm, mean per life)", "",
          "Source events are the engine's own events of the connection's SOURCE node (rising through 0 V, re-armed "
          "below −V_TYP). They are labelled proxies, NOT communication energy: leaky input, delay and memory nodes "
          "(S, T, E, Y, B, P) rarely or never fall below −V_TYP, so they register ≤ 1 event a life whatever their "
          "activity; body pulses into S are counted separately (`body_pulses`). Gate factor = clip(V_gate/V_TYP, 0, 1), "
          "integrated at the circuit step.", ""]
    import ag_analysis
    for a in AA.ARMS:
        L.append(f"**{a}**: " + "; ".join(
            f"{nm} ({d['source']}→, src ev {d['source_events_mean']:.0f}" +
            ("" if d["gate"] == "ungated" else f", gate {d['gate']} mean {d['gate_mean']:.3f}, open {d['gate_open_fraction']:.3f}") + ")"
            for nm, d in (t.get("gates_by_arm") or {}).get(a, {}).items()))
        L.append("")
    (OUT / "historical_reconciliation.md").write_text("\n".join(L) + "\n")

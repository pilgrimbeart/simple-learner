"""D180 report tables, regenerated from the saved per-life ledgers and bench outputs (runs on partial outputs).
Writes lab/v/catalogue_brain_20261120/tables.md and tables.json (overwritten on each run: derived, not raw)."""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
OUT = ROOT / "lab/v/catalogue_brain_20261120"


def load(name):
    p = OUT / f"{name}_ledger.jsonl.gz"
    if not p.exists():
        return None
    with gzip.open(p, "rt") as f:
        return [json.loads(x) for x in f]


def fmt(ci, d=2):
    if ci is None or ci[0] is None:
        return "—"
    return f"{ci[0]:+.{d}f} [{ci[1]:+.{d}f}, {ci[2]:+.{d}f}]"


def arm_table(rows, title):
    import analyse as A
    arms = sorted({r["arm"] for r in rows}, key=lambda a: (a.endswith("allfood"), a))
    L = [f"### {title}", "", "| arm (removal) | lives | net food/10 s, final third | food/10 s | poison/10 s | "
         "food−3·poison | pooled food:poison | no-meal lives | seed-any-stranded Wilson upper | never moved | "
         "motor events/life | power (nW) |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    T = {}
    for a in arms:
        rr = [r for r in rows if r["arm"] == a]
        S = A.summary(rr)
        T[a] = S
        st = S["stranding"]
        L.append(f"| {a} ({rr[0]['removed']}) | {S['lives']} | {fmt(S['net'])} | {fmt(S['food_rate_final'])} | "
                 f"{fmt(S['poison_rate_final'])} | {fmt(S['job_linear'])} | {S['food_poison_pooled'] if isinstance(S['food_poison_pooled'], str) else round(S['food_poison_pooled'], 2)} | "
                 f"{st['life_fraction'][0]}/{st['life_fraction'][1]} | {st['seed_any'][4]:.3f} | {S['never_moved']} | "
                 f"{S['motor_events'][0]:.0f} | {S['power_W'][0] * 1e9:.1f} |")
    L.append("")
    acq = [(a, T[a]["acquisition"]) for a in arms if "acquisition" in T[a]]
    if acq:
        L += ["| arm | acquired ever | acquired at end | median first acquisition (s; missing = never) | mean fraction "
              "of life acquired | exits | re-entries | right order at end | P min / max (V) | mean s with a P outside [0, V_TYP] |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for a, q in acq:
            L.append(f"| {a} | {q['ever']} | {q['final']} | {q['first_s_median']} (missing {q['first_missing']}) | "
                     f"{q['fraction_mean']:.3f} | {q['exits']} | {q['reentries']} | {q['order_final']} | "
                     f"{q['P_min']:+.3f} / {q['P_max']:+.3f} | {q['P_outside_s_mean']:.1f} |")
        L.append("")
    return L, T


def main():
    import analyse as A
    md, js = ["# D180 tables (regenerated from ledgers by report.py)", ""], {}
    for nm in ("bench_A", "bench_B", "bench_C"):
        p = OUT / f"{nm}.json"
        if p.exists():
            d = json.loads(p.read_text())
            md += [f"## {nm} gate", "", "```", json.dumps(d["gate"], indent=1, default=float), "```", ""]
            js[nm] = d["gate"]
        else:
            md += [f"## {nm}: INCOMPLETE (no output)", ""]
    for stage in ("action", "action_auth", "learn", "confirm_r1", "confirm_r2", "confirm_r4"):
        rows = load(stage)
        if rows is None:
            g = OUT / ("gate_" + {"confirm_r1": "confirm", "confirm_r2": "refine", "confirm_r4": "refine"}.get(stage, stage) + ".json")
            md += [f"## {stage}: " + ("not triggered — " + json.loads(g.read_text()).get("reason", "")
                                     if g.exists() else "no ledger (not run)"), ""]
            continue
        jobs = json.loads((OUT / f"{stage}_jobs.json").read_text())["keys"]
        missing = A.validate_ledger(rows, jobs)
        L, T = arm_table(rows, f"{stage}: {len(rows)} of {len(jobs)} expected lives; missing {len(missing)}")
        md += [f"## {stage}", ""] + L
        js[stage] = dict(expected=len(jobs), actual=len(rows), missing=missing,
                         summaries={a: {k: v for k, v in s.items()} for a, s in T.items()})
    (OUT / "tables.md").write_text("\n".join(md) + "\n")
    (OUT / "tables.json").write_text(json.dumps(js, indent=1, default=float) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()

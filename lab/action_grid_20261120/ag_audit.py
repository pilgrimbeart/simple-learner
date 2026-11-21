"""R8 independent audit: regenerate headline numbers from saved per-job rows WITHOUT ag_analysis/D180 metric code,
verify key sets against freshly generated job lists, and ledger/archive hashes against their meta files.
Writes lab/v/action_grid_20261120/audit.json."""
from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
OUT = ROOT / "lab/v/action_grid_20261120"
BASE = "g1.0_t0.005_q0.15_f1.0"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def rows(name):
    with gzip.open(OUT / f"{name}_ledger.jsonl.gz", "rt") as f:
        return [json.loads(x) for x in f]


def net_food(r):
    """Final third [200/3, 100) s from the raw meal list: a meal at tick t is in the window iff t*0.01 >= 200/3."""
    inside = [c for t, c in r["meals"] if t * 0.01 >= 200 / 3]
    food = sum(c != r["poison"] for c in inside)
    poison = sum(c == r["poison"] for c in inside)
    return (food - poison) * 10 / (100 / 3), food * 10 / (100 / 3)


def seed_mean(rs, i):
    d = {}
    for r in rs:
        d.setdefault(r["seed"], []).append(net_food(r)[i])
    return {s: sum(v) / len(v) for s, v in d.items()}


def main():
    import ag_jobs as J
    from ag_engine import CONFIGS
    A = dict(hashes={}, keys={}, checks={})
    for name in ("bench", "develop", "confirm"):
        mp = OUT / f"{name}_meta.json"
        if not mp.exists():
            A["hashes"][name] = "missing meta (stage incomplete)"
            continue
        m = json.loads(mp.read_text())
        A["hashes"][name] = dict(ledger=sha(m["ledger"]) == m["ledger_sha256"], archive=sha(m["archive"]) == m["archive_sha256"])
    # key sets regenerated from the job generators
    exp = dict(bench={J.key(j) for c in CONFIGS for j in J.bench_jobs(c)},
               develop={J.key(j) for c in CONFIGS for j in J.life_jobs("develop", c, range(8, 40))})
    fzp = OUT / "confirm_freeze.json"
    if fzp.exists():
        fz = json.loads(fzp.read_text())
        exp["confirm"] = {J.key(j) for r in (1, 2, 4) for c in fz["configs"]
                          for j in J.life_jobs("confirm", c, range(fz["seeds"][0], fz["seeds"][1] + 1), r, "coupled")}
    R = {}
    for name in exp:
        try:
            R[name] = rows(name)
        except FileNotFoundError:
            A["keys"][name] = "ledger missing"
            continue
        ks = [r["key"] for r in R[name]]
        A["keys"][name] = dict(expected=len(exp[name]), rows=len(ks), unique=len(set(ks)), equal=set(ks) == exp[name],
                               status={s: sum(r["status"] == s for r in R[name]) for s in {r["status"] for r in R[name]}})
    # development: independent informed net per configuration, compare to the selection inputs
    if "develop" in R:
        sel = json.loads((OUT / "selection.json").read_text())
        dev = R["develop"]
        mism, table = [], {}
        for c in CONFIGS:
            inf = [r for r in dev if r["config"] == c and r["arm"] == "informed"]
            ok = [r for r in dev if r["config"] == c]
            complete = len(ok) == 384 and all(r["status"] == "ok" for r in ok)
            n = seed_mean([r for r in inf if r["status"] == "ok"], 0)
            f = seed_mean([r for r in inf if r["status"] == "ok"], 1)
            table[c] = (complete, sum(n.values()) / len(n) if n else float("nan"), sum(f.values()) / len(f) if f else float("nan"))
            if c != BASE:
                s = sel["inputs"][c]
                if s["complete"] != complete or (complete and (abs(s["informed_net"] - table[c][1]) > 1e-9 or
                                                                abs(s["informed_food"] - table[c][2]) > 1e-9)):
                    mism.append(c)
        ranked = sorted([c for c in table if c != BASE and table[c][0]], key=lambda c: (-table[c][1], -table[c][2], c))
        A["checks"]["selection_inputs_match_independent_count"] = not mism
        A["checks"]["selection_reproduced"] = ranked[:3] == sel["selected"]
        A["checks"]["ranked_list_reproduced"] = ranked == sel["ranked"]
        A["checks"]["selection_hash"] = hashlib.sha256(json.dumps(sel["inputs"], sort_keys=True, default=float).encode()).hexdigest() == sel["inputs_sha256"]
        A["dev_top5"] = [(c, table[c][1], table[c][2]) for c in ranked[:5]]
        A["dev_baseline"] = table[BASE]
        A["dev_complete_configs"] = sum(t[0] for t in table.values())
    if "confirm" in R:
        ct = json.loads((OUT / "confirm_tables.json").read_text())
        rs = R["confirm"]
        pts = {}
        for c in fz["configs"][1:]:
            for ratio in (1, 2, 4):
                a = seed_mean([r for r in rs if r["config"] == c and r["ratio"] == ratio and r["arm"] == "informed"
                               and r["status"] == "ok"], 0)
                b = seed_mean([r for r in rs if r["config"] == BASE and r["ratio"] == ratio and r["arm"] == "informed"
                               and r["status"] == "ok"], 0)
                d = [a[s] - b[s] for s in a if s in b]
                est = sum(d) / len(d)
                pts[f"{c}|r{ratio}"] = est
                A["checks"][f"primary_point_{c}_r{ratio}"] = abs(est - ct["primary"][c]["by_ratio"][str(ratio)]["ci95"][0]) < 1e-9
        A["confirm_primary_points"] = pts
        A["confirm_clip_lives"] = {c: sum(r["clip_steps"] > 0 for r in rs if r["config"] == c) for c in fz["configs"]}
    A["all_ok"] = all(v is True for v in A["checks"].values()) and all(
        isinstance(v, dict) and all(v.values()) for v in A["hashes"].values()) and all(
        isinstance(v, dict) and v["equal"] and v["unique"] == v["rows"] for v in A["keys"].values())
    (OUT / "audit.json").write_text(json.dumps(A, indent=1, default=float) + "\n")
    print(json.dumps(A, indent=1, default=float))


if __name__ == "__main__":
    main()

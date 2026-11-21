"""Action grid R6 seed allocation (work order section 9): the first unused 128-seed prefix of blocks starting
2027112000 + 1000*k. Searches non-sealed text sources, manifests, ledgers and logs for literal seeds AND ranges
(two 10-digit numbers 2027xxxxxx on one line are read as an inclusive range). Never opens lab/sealed (protected).
A hit, or an uncertain range, moves to the next block."""
from __future__ import annotations

import gzip
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE, STEP, N = 2027112000, 1000, 128
SKIP_PREFIX = (".git/", ".venv/", "lab/sealed", "lab/action_grid_20261120", "lab/v/action_grid_20261120")
SKIP = {"lab/WORK_ORDER_2026-11-20_action_grid.md"}            # the work order that names the block base
SUFFIX = (".json", ".jsonl", ".md", ".txt", ".log", ".py", ".csv", ".tsv", ".sh", ".yaml", ".yml", ".toml", ".gz")
NUM = re.compile(r"(?<![0-9.])(2027[0-9]{6})(?![0-9])")


def scan():
    lits, ranges, files = {}, [], 0
    for p in ROOT.rglob("*"):
        rel = str(p.relative_to(ROOT))
        if not p.is_file() or rel.startswith(SKIP_PREFIX) or rel in SKIP or p.suffix not in SUFFIX:
            continue
        try:
            text = gzip.open(p, "rt", errors="ignore").read() if p.suffix == ".gz" else p.read_text(errors="ignore")
        except Exception:
            continue
        files += 1
        for line in text.splitlines():
            ns = [int(m.group(1)) for m in NUM.finditer(line)]
            for n in ns:
                lits.setdefault(n, set()).add(rel)
            if len(ns) >= 2:
                ranges.append((min(ns), max(ns), rel))
    return lits, ranges, files


def first_unused(N=N):
    lits, ranges, files = scan()
    search, k = [], 0
    while True:
        a, b = BASE + STEP * k, BASE + STEP * k + N - 1
        hits = sorted(s for s in lits if a <= s <= b)
        rhits = [r for r in ranges if r[0] <= b and r[1] >= a]
        search.append(dict(start=a, end=b, literal_hits=[(s, sorted(lits[s])) for s in hits[:20]],
                           range_hits=rhits[:20]))
        if not hits and not rhits:
            return dict(start=a, end=b, N=N, search=search, files_scanned=files, excluded=list(SKIP_PREFIX) + sorted(SKIP),
                        note="lab/sealed not opened (protected); its seeds are unknown to this audit")
        k += 1


if __name__ == "__main__":
    import json
    print(json.dumps(first_unused(), indent=1, default=list))

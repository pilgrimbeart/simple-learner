"""D180 R7 seed audit: before freezing the fresh confirmation block, search every repository manifest/log/index
(text files under lab/, experiments/, minimal/, discrete/ and the root) for prior use of any seed in the candidate
block 2027010000 + [0, N); if any appears, advance by 1000 to the first unused complete 256-seed block."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = 2027010000
SKIP = {"lab/WORK_ORDER_2026-11-20_catalogue_brain.md"}         # the work order that reserves the block


def numbers():
    found = {}
    for p in ROOT.rglob("*"):
        rel = str(p.relative_to(ROOT))
        if not p.is_file() or rel.startswith((".git/", ".venv/")) or rel in SKIP or "catalogue_brain_20261120" in rel:
            continue
        if p.suffix not in (".json", ".jsonl", ".md", ".txt", ".log", ".py", ".csv", ".tsv"):
            continue
        try:
            text = p.read_text(errors="ignore")
        except Exception:
            continue
        for m in re.finditer(r"(?<![0-9.])(20270[0-9]{5})(?![0-9])", text):
            found.setdefault(int(m.group(1)), set()).add(rel)
    return found


def first_unused(N):
    used = numbers()
    search = []
    start = BASE
    while True:
        hits = sorted(s for s in used if start <= s < start + 256)
        search.append(dict(start=start, hits=[(s, sorted(used[s])) for s in hits[:20]], n_hits=len(hits)))
        if not hits:
            return start, search
        start += 1000


if __name__ == "__main__":
    import json
    print(json.dumps(first_unused(256), indent=1))

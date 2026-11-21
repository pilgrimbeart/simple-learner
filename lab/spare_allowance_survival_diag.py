"""D119 diagnostic: why the tracker's count of births after allowance-only transfers can fall below the gate's own counter.
Re-runs given gate-arm lives with spare_allowance_survival's tracker plus a count of each way a stream's pending
allowance-only mark is replaced before a birth uses it (a later transfer with deletion into the same stream). Passive.
    .venv/bin/python lab/spare_allowance_survival_diag.py seq 142000 red [seq 142008 blue ...]
"""
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "lab"), str(ROOT)]
import spare_allowance_survival as S

OVER = []
_wrap = S.Tracker._wrap


def _wrap_counting(self, n, j):
    _wrap(self, n, j)
    room = n._room

    def _room():
        before = self.pend.get(j)
        r = room()
        if before == S.CAUSES[0] and self.pend.get(j) == S.CAUSES[1]:
            OVER.append(j)
        return r
    n._room = _room
S.Tracker._wrap = _wrap_counting

out = []
a = sys.argv[1:]
for cond, seed, first in zip(a[::3], a[1::3], a[2::3]):
    OVER.clear()
    r = S.one((cond, "issued+gate", int(seed), first))
    c = r["gate"]["counters"]
    out.append(dict(life=[cond, int(seed), first], tracker=sum(u["cause"] == S.CAUSES[0] for u in r["units"]),
                    replaced_by_deletion_transfer=len(OVER), gate_counter=c.get("births_after_allowance_only_transfer", 0),
                    allowance_only_transfers=c.get("allowance-only transfers", 0)))
print(json.dumps(out, indent=1))

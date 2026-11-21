"""PROGRAMME test H (D113): opt-in, instance-level lab adapter for capped rule M (lab/alloc_rules.py).

install(brain, enabled=False) after alloc_rules.install(brain, "M", G, seed) and before or after issued_credit.install.
It wraps each stream's M room test. M runs unchanged (its single donor draw, RNG order and leaf-removal path). Only when
M refuses a full, birth-due request that passed the price and donor tests because the drawn donor has no removable leaf,
and that donor holds fewer units than its allowance, the enabled adapter moves one allowance unit from that donor to the
recipient, removing nothing and debiting no savings. The drawn donor is predicted from a copy of M's generator state
(nothing consumed). Diagnostic counters never feed back. uninstall() restores every wrapped attribute. Not local: M
already scans every stream for donors; this adapter adds no scan but inherits that one.
"""
from collections import Counter
import weakref
import numpy as np

_INSTALLED = weakref.WeakKeyDictionary()


def _closure_rng(fn):
    for cell in (getattr(fn, "__closure__", None) or ()):
        if isinstance(cell.cell_contents, np.random.Generator):
            return cell.cell_contents
    return None


def _copy(g):
    c = np.random.Generator(type(g.bit_generator)())
    c.bit_generator.state = g.bit_generator.state
    return c


def _leaves(n):
    return [k for k, x in n.units.items() if x["sym"] is None and not x["kids"]]


class SpareGate:
    def __init__(self, b, enabled):
        import grownet as GN
        assert b not in _INSTALLED, "spare-allowance adapter already installed on this brain"
        st = getattr(b, "_alloc", None)
        assert st is not None and "transfers" in st, "install alloc_rules rule M first"
        self.GN, self.b, self.st, self.enabled = GN, b, st, bool(enabled)
        self.nets = list(b.nets)
        self.fixed = [sum(x["sym"] is not None for x in n.units.values()) for n in self.nets]
        rngs = {id(_closure_rng(n._room)) for n in self.nets}
        assert len(rngs) == 1 and None not in [_closure_rng(n._room) for n in self.nets], "expected rule M's one shared generator"
        self.rng = _closure_rng(self.nets[0]._room)
        self.c = Counter()
        self.allowance_sum = sum(int(n.P) for n in self.nets)
        self.pending = set()
        self.first_transfer = None
        self.first_opportunity = None
        self.events = []
        self.opportunities = []
        self.originals = [dict(_room=n.__dict__["_room"], _add=n.__dict__["_add"]) for n in self.nets]
        for j, n in enumerate(self.nets):
            self._wrap(n, j)
        _INSTALLED[b] = self

    def _wrap(self, n, j):
        room, add = n._room, n._add

        def _add(*a, **k):
            r = add(*a, **k)
            # per-birth invariants for capped M: the new unit fits its stream's allowance and the total cap
            assert len(n.units) <= int(n.P), ("birth above the stream's allowance", n.kind)
            assert self.st["fixed"] + self.st["grown"] <= self.st["cap"], "birth above the total cap"
            if j in self.pending:
                self.pending.discard(j)
                self.c["births_after_allowance_only_transfer"] += 1
            self.c["births"] += 1
            return r

        def _room():
            GN, nets = self.GN, self.nets
            units, P = len(n.units), int(n.P)
            if units < P:
                self.c["requests: under allowance"] += 1
                return room()
            d = n._deep
            due = d is not None and d in n.units and min(n.units[d]["n"]) >= 1
            price = GN.POOL_BITS * (units - n.base + 1)
            if not due or getattr(n, "saved", 0.0) <= price:
                self.c["requests: no birth due" if not due else "requests: savings test fails"] += 1
                r = room()
                assert r is False
                return r
            poor = [i for i, v in enumerate(nets) if v is not n and getattr(v, "saved", 0.0) <= 0.0 and v.P > self.fixed[i]]
            self.c["donor scans"] += 1
            self.c["stream visits in donor scans"] += len(nets) - 1
            if not poor:
                self.c["requests: no poor donor"] += 1
                r = room()
                assert r is False
                return r
            vi = poor[int(_copy(self.rng).integers(len(poor)))]
            v = nets[vi]
            had_leaf = bool(_leaves(v))
            spare = int(v.P) - len(v.units)
            Pv, units_v = int(v.P), len(v.units)
            r = room()
            if r:
                assert had_leaf and int(v.P) == Pv - 1 and len(v.units) == units_v - 1 and int(n.P) == P + 1, "M transfer not via the drawn donor"
                self.c["transfers with deletion"] += 1
                self.check(n, j, v, vi)
                return True
            assert not had_leaf and int(v.P) == Pv and len(v.units) == units_v, "M refused a donor with a leaf"
            if spare <= 0:
                self.c["requests: drawn donor leafless, no spare allowance"] += 1
                return False
            self.c["requests: drawn donor leafless with spare allowance"] += 1
            ev = dict(t=float(getattr(self.b, "t", 0.)), recipient=j, donor=vi, recipient_units=units, recipient_P=P,
                      donor_units=units_v, donor_P=Pv, saved=float(n.saved), price=price)
            if self.first_opportunity is None:
                self.first_opportunity = ev
            self.opportunities.append((ev["t"], j, vi))
            if not self.enabled:
                return False
            v.P -= 1
            n.P += 1
            self.c["allowance-only transfers"] += 1
            self.pending.add(j)
            self.events.append(ev)
            if self.first_transfer is None:
                self.first_transfer = ev
            self.check(n, j, v, vi)
            return True
        n._room, n._add = _room, _add

    def check(self, n, j, v, vi):
        """Per-request invariants for capped M."""
        assert sum(int(m.P) for m in self.nets) == self.allowance_sum, "allowance sum changed"
        for m, i in ((n, j), (v, vi)):
            assert self.fixed[i] <= len(m.units) <= int(m.P), ("units outside [fixed, allowance]", m.kind)
        assert self.st["fixed"] + self.st["grown"] <= self.st["cap"], "total units above the cap"

    def summary(self):
        unused = sum(max(0, int(n.P) - len(n.units)) for n in self.nets)
        return dict(enabled=self.enabled, counters=dict(self.c), unused_allowance=unused,
                    final_units=sum(len(n.units) for n in self.nets), peak_units=self.st["peak"], cap=self.st["cap"],
                    allowance_sum=sum(int(n.P) for n in self.nets), allowance_sum_at_install=self.allowance_sum,
                    first_transfer=self.first_transfer, first_opportunity=self.first_opportunity,
                    transfers_recorded_by_M=self.st["transfers"], n_allowance_events=len(self.events),
                    opportunities=len(self.opportunities), opportunity_distinct_recipients=len({j for _, j, _ in self.opportunities}),
                    opportunity_distinct_times=len({t for t, _, _ in self.opportunities}),
                    opportunity_recipient_families=None)

    def uninstall(self):
        for n, o in zip(self.nets, self.originals):
            n._room, n._add = o["_room"], o["_add"]
        _INSTALLED.pop(self.b, None)


def install(b, enabled=False):
    return SpareGate(b, enabled)


def invariants(nets, fixed, cap, allowance_sum):
    """Whole-brain invariants for capped M: allowance sum, fixed <= units <= allowance, total <= cap, no orphan links."""
    assert sum(int(n.P) for n in nets) == allowance_sum, "allowance sum changed"
    assert sum(len(n.units) for n in nets) <= cap, "total units above the cap"
    for n, f in zip(nets, fixed):
        assert sum(x["sym"] is not None for x in n.units.values()) == f, ("a fixed unit is missing", n.kind)
        assert f <= len(n.units) <= int(n.P), ("units outside [fixed, allowance]", n.kind)
        for k, x in n.units.items():
            if x["sym"] is None:
                assert x["u"] in n.units and x["v"] in n.units, ("orphan", n.kind, k)
                assert k in n.units[x["u"]]["kids"] and k in n.units[x["v"]]["kids"], ("parent does not list child", n.kind, k)
            for c in x["kids"]:
                assert c in n.units, ("dangling child", n.kind, k)
    return True

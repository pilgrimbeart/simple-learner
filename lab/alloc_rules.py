"""D78: allocation rules for the frozen growing network under an enforced total cap. Lab code; grownet.py is unchanged.

install(brain, rule, G, seed) is called after construction and before the first step. Every rule keeps
total units <= fixed + G, checked after every birth (CapBroken). Rules (discrete/NOTEBOOK.md, D78):
  none  hooks only, nothing changed (neutral check: must reproduce the historical record)
  E     equal: each stream fixed + G // streams, market off
  M     E plus the existing market's test, a transfer only with an actual removal, only when a birth is due
  W     shared pool; when full, a contest with one random other stream by mixture weight
  U     shared pool; when full, recycle the least used of 4 leaves sampled from all streams
  R     ruler: G split among the event streams, none to the others
"""
import numpy as np

EVENT = ("every:", "good:", "bad:", "red:", "blue:")


class CapBroken(Exception):
    pass


def is_event(kind):
    return kind.startswith(EVENT)


def install(b, rule, G, seed):
    import grownet as GN
    nets = list(b.nets)
    fixed = {id(n): sum(x["sym"] is not None for x in n.units.values()) for n in nets}
    assert all(fixed[id(n)] == len(n.units) for n in nets), "install before any growth"
    rng = np.random.default_rng([int(seed), 91])
    F = sum(fixed.values())
    st = dict(grown=0, fixed=F, cap=F + G, peak=F, transfers=0, contests=0, won=0, evictions=0)
    b._alloc = st

    def leaves(n, exclude=None):
        return [k for k, x in n.units.items() if x["sym"] is None and not x["kids"] and k != exclude]

    def least_used(n, ks, t, r):
        pick = [ks[int(r.integers(len(ks)))] for _ in range(4)]
        return min(pick, key=lambda k: n._trace(n.units[k], t))

    def now():
        return float(b.t)

    for n in nets:
        add, remove, learn = n._add, n._remove, n.learn
        n._deep = None

        def _add(*a, _n=n, _add0=add, **k):
            r = _add0(*a, **k)
            st["grown"] += 1
            st["peak"] = max(st["peak"], F + st["grown"])
            if F + st["grown"] > st["cap"] and rule != "none":
                raise CapBroken((rule, _n.kind))
            return r

        def _remove(k, _n=n, _rm=remove):
            if k in _n.units:
                st["grown"] -= 1
            return _rm(k)

        def _learn(i, letter, t, speaker, firing, _n=n, _l=learn):
            _n._deep = max(firing, key=lambda k: _n.units[k]["span"], default=None)
            try:
                return _l(i, letter, t, speaker, firing)
            finally:
                _n._deep = None
        n._add, n._remove, n.learn = _add, _remove, _learn

    if rule == "none":
        return st

    def due(n):
        d = n._deep
        return d is not None and d in n.units and min(n.units[d]["n"]) >= 1

    if rule in ("E", "M", "R"):
        for n in nets:
            n.market = None
            if rule == "R":
                g = G // sum(is_event(m.kind) for m in nets) if is_event(n.kind) else 0
            else:
                g = G // len(nets)
            n.P = n.base = fixed[id(n)] + g
        if rule == "M":
            for n in nets:
                def _room(_n=n):
                    if len(_n.units) < _n.P:
                        return True
                    if not due(_n) or getattr(_n, "saved", 0.0) <= GN.POOL_BITS * (len(_n.units) - _n.base + 1):
                        return False
                    poor = [v for v in nets if v is not _n and getattr(v, "saved", 0.0) <= 0.0 and v.P > fixed[id(v)]]
                    if not poor:
                        return False
                    v = poor[int(rng.integers(len(poor)))]
                    ks = leaves(v)
                    if not ks:
                        return False
                    v._remove(least_used(v, ks, now(), rng))
                    v.P -= 1
                    _n.P += 1
                    st["transfers"] += 1
                    return True
                n._room = _room
        return st

    # pooled rules: allowance is the shared pool; a stream's own P follows its size so that its own
    # on-demand recycling (grownet's existing path) frees exactly one place for the birth.
    for n in nets:
        n.market = None
        n.P = len(n.units) + 10 ** 9            # P is overwritten at every refusal below

        def _room(_n=n):
            if F + st["grown"] < st["cap"]:
                _n.P = len(_n.units) + 1
                return True
            _n.P = len(_n.units)                # full: by default the stream recycles its own leaf
            if not due(_n):
                return False
            t = now()
            if rule == "W":
                v = None                        # uniform over the other streams with a grown leaf (rejection sampling)
                for _ in range(200):
                    c = nets[int(rng.integers(len(nets)))]
                    if c is not _n and any(x["sym"] is None and not x["kids"] for x in c.units.values()):
                        v = c
                        break
                if v is None:
                    return False
                st["contests"] += 1
                if getattr(v, "w", 1.0) < getattr(_n, "w", 1.0):
                    v._remove(least_used(v, leaves(v), t, rng))
                    st["won"] += 1
                    _n.P = len(_n.units) + 1
                    return True
                return False
            if rule == "U":
                pool = [(v, k) for v in nets for k in leaves(v, _n._deep if v is _n else None)]
                if not pool:
                    return False
                pick = [pool[int(rng.integers(len(pool)))] for _ in range(4)]
                v, k = min(pick, key=lambda vk: vk[0]._trace(vk[0].units[vk[1]], t))
                v._remove(k)
                st["evictions"] += 1
                _n.P = len(_n.units) + 1
                return True
            raise ValueError(rule)
        n._room = _room
    return st

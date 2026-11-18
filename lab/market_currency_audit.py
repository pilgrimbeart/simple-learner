"""Job B (PROGRAMME, after D103): the market's actual currency, from source and saved data only (no lives).

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/market_currency_audit.py --check
    timeout 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/market_currency_audit.py --analyse
"""
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "lab"), str(ROOT)]
import numpy as np

BASE = ROOT / "lab/v/market_currency_audit"

EQUATIONS = {
    "balance": "saved_j, bits; starts at 0 (getattr default) for every stream; never reset during a life",
    "credit (historical, grownet.py:799-801)": "at each accepted (vouched) taste, after every stream's learn call in that taste, "
        "for each stream j that spoke at taste time: saved_j += log2(q_j(y) / p_def(y)), q_j its speaker's KT probability for the "
        "revealed letter y computed just before its own learn call (so after earlier streams' learning in the same taste), "
        "p_def(y) the default's KT probability; can be negative; units bits",
    "credit (D82 issued contract, issued_credit.py:34-54)": "same increment but q_j(y) from the forecast issued at the last "
        "prediction before the taste, applied at the next prediction",
    "debit": "none: a transfer does not reduce saved_j; the price is a threshold that rises with the units held",
    "price test, design market (grownet.py:176)": "saved_j > POOL_BITS * (len(units_j) - base_j + 1), base_j = allowance at birth "
        "(grownet.py:467), POOL_BITS = 1 bit (grownet.py:71); evaluated only when len(units_j) >= P_j",
    "donor test, design market (grownet.py:177)": "some other stream v with saved_v <= 0 and P_v > 3",
    "price test, lab rule M (alloc_rules.py:90)": "the same threshold, and a birth due (deep firing unit has seen both labels)",
    "donor test, lab rule M (alloc_rules.py:92)": "some other stream v with saved_v <= 0 and P_v > fixed units of v",
    "transfer": "donor's least used of 4 sampled leaves recycled, P_v -= 1, P_j += 1",
    "timing": "the room test runs inside stream j's learn call (grownet.py:260, called at :761) during the taste loop; the "
        "credit for that taste is added after the loop (historical) or at the next prediction (D82): a taste's saving can "
        "first fund room at the next taste",
    "design allowance": "P_j = max(3, P // 168) (grownet.py:455): 3 for every stream at P=560, 26 at P=4480",
}


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def increment(q_y, pd_y):
    return math.log2(q_y / pd_y)


class _Mk:
    def __init__(self, nets):
        self.nets = nets


def make(GN, P, n_units, saved, base):
    import numpy as np_
    n = GN.Net("x", P, np_.random.default_rng(0))
    while len(n.units) < n_units:
        n._add(0, 0, 2, 0.0)
    n.saved, n.base = saved, base
    return n


def check():
    import grownet as GN
    checks = []
    # a binary label can save more than one bit against a poor default
    s = increment(.75, .1)
    assert abs(s - 2.9068905956085187) < 1e-12 and s > 1
    checks.append("one label saves log2(.75/.1) = 2.907 bits > 1: label entropy does not cap savings against a poor default")
    assert increment(.25, .5) == -1.
    checks.append("a confident wrong forecast debits: log2(.25/.5) = -1 bit")
    # post-label updating changes credit: the same stream's scored q differs if an earlier stream's learning recycled its speaker
    issued, scored = increment(.8, .5), increment(.6, .5)
    assert abs(issued - scored) > .4
    checks.append("issued q=.8 vs scored q=.6 after an earlier learn call recycles the speaker: credit .678 vs .263 bits")
    # the real Net._room with a market: price, donor and allowance tests
    assert GN.POOL_BITS == 1.0
    rich = make(GN, 3, 4, 2.5, 3)                    # 4 units, base 3: needs saved > 1*(4-3+1) = 2
    poor = make(GN, 4, 2, -1.0, 4)                   # P 4 > 3, saved <= 0: a donor
    mk = _Mk([rich, poor])
    rich.market = poor.market = mk
    rich.P = 4
    assert rich._room() is True and rich.P == 5 and poor.P == 3
    checks.append("real Net._room: saved 2.5 > price 2 with a donor of P 4 transfers one allowance unit (P 4->5, donor 4->3)")
    rich2 = make(GN, 4, 4, 2.0, 3)
    poor2 = make(GN, 4, 2, -1.0, 4)
    mk2 = _Mk([rich2, poor2])
    rich2.market = poor2.market = mk2
    P0 = rich2.P
    assert rich2._room() is False and rich2.P == P0
    checks.append("real Net._room: saved exactly at the price (2.0) is refused (strict >)")
    rich3 = make(GN, 3, 3, 10.0, 3)
    poor3 = make(GN, 3, 2, -5.0, 3)                  # P 3 is not > 3: never a donor
    mk3 = _Mk([rich3, poor3])
    rich3.market = poor3.market = mk3
    assert rich3._room() is False
    checks.append("real Net._room: a poor stream with allowance 3 is not a donor, whatever the savings (the P=560 design case)")
    # real code path: stream A's room test recycles stream B's speaking leaf, changing B's forecast and so its credit
    A_ = make(GN, 3, 4, 5.0, 3)
    B_ = GN.Net("b", 4, np.random.default_rng(1))
    leaf = B_._add(0, 1, 2, 0.0)                     # word (0,1): fires at i=1 below
    B_.units[leaf]["n"] = [0, 3]
    B_.units[1]["n"] = [2, 1]                        # fixed symbol 1, weaker evidence the other way
    B_.hist = {0: 0, 1: 1}
    B_.saved, B_.base = -1.0, 4                      # poor, P 4 > 3: a donor
    mkB = _Mk([A_, B_])
    A_.market = B_.market = mkB
    A_.P = 4
    k0, _ = B_.says(1)
    q_issued = (B_.units[k0]["n"][1] + .5) / (sum(B_.units[k0]["n"]) + 1)
    assert k0 == leaf and abs(q_issued - .875) < 1e-12
    assert A_._room() is True and leaf not in B_.units          # A's learn-time room test recycles B's only leaf
    k1, _ = B_.says(1)
    q_scored = (B_.units[k1]["n"][1] + .5) / (sum(B_.units[k1]["n"]) + 1)
    assert k1 == 1 and abs(q_scored - .375) < 1e-12
    pd = .5
    ci, cs = increment(q_issued, pd), increment(q_scored, pd)
    assert abs(ci - math.log2(1.75)) < 1e-12 and abs(cs - math.log2(.75)) < 1e-12
    checks.append("real Net._room and Net.says: an earlier stream's transfer recycles another stream's speaking leaf; that stream's "
                  "forecast for letter 1 falls from .875 (issued) to .375 (scored at taste), so its historical credit is "
                  "log2(.75) = -.415 bits instead of log2(1.75) = +.807 under D82's issued contract")
    assert max(3, 560 // 168) == 3 and max(3, 4480 // 168) == 26
    checks.append("design allowance: 3 per stream at P=560, 26 at P=4480 (grownet.py:455)")
    out = dict(success=True, checks=checks)
    BASE.with_name(BASE.name + "_checks").with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


def analyse():
    out = dict(success=False, equations=EQUATIONS, provenance=dict(
        revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        dirty=subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
        sha256={p: digest(ROOT / p) for p in ("lab/market_currency_audit.py", "lab/grownet.py", "lab/alloc_rules.py",
                                               "lab/issued_credit.py", "lab/market_diagnosis.py", "lab/v/market_diagnosis.json",
                                               "lab/v/noisy_resource_observe.json")},
        command="timeout 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/market_currency_audit.py --analyse"))
    try:
        md = json.loads((ROOT / "lab/v/market_diagnosis.json").read_text())
        assert not md["identity"]["mismatches"]
        req = md["requests"]
        fams = list(req)
        tot = {k: sum(req[f].get(k, 0) for f in fams) for k in
               ("under allowance", "full, no birth due", "full, savings test fails", "full, no poor donor", "full, transfer attempted", "transfers")}
        full = {f: sum(v for k, v in req[f].items() if k.startswith("full")) for f in fams}
        out["D97_denominators"] = dict(per_family=req, totals=tot,
            savings_fail_share_of_full={f: req[f].get("full, savings test fails", 0) / full[f] for f in fams},
            transfer_share_of_attempted={f: req[f]["transfers"] / req[f]["full, transfer attempted"] for f in fams},
            transfers_per_life=md["transfers_per_life"], lives=md["identity"]["lives"], rule="lab rule M, cap 2042+258, seq 17, 300 s, seeds 142000-142009")
        obs = json.loads((ROOT / "lab/v/noisy_resource_observe.json").read_text())
        out["design_market_D77"] = [dict(P=l["P"], world=l["world"], first=l["first"],
                                         price_passes=l["counters"].get("market_global_scans", 0),
                                         transfers=l["counters"].get("market_transfers", 0)) for l in obs["lives"]]
        out["inventory"] = dict(
            market_diagnosis_json=dict(present=["per-family request counts by first failing condition, summed over 20 lives",
                                                "event streams' saved bits, allowance and donor count every 10 s (medians in 50 s bins)",
                                                "end-of-life saved bits for event streams of 2 lives and the top 5 streams of 4 lives",
                                                "transfers per life (mean)"],
                                       missing=["per-request time, stream, balance, price and outcome",
                                                "per-taste credit increments and the forecast (scored or issued) behind each",
                                                "donor identities and removed units", "any per-life record (there is no market_diagnosis.pkl)"]),
            room_prediction_pkl=dict(present=["issued forecasts and default probability for every stream at each accepted taste "
                                              "(design lives low, A, B, high; the design market is active only at P=4480 and in B)"],
                                     missing=["scored forecasts at taste time (they differ from issued after earlier learn calls)",
                                              "the set of streams credited at taste time", "any room-test call or transfer record"],
                                     verdict="issued forecasts give an issued-contract approximation of the balance, not the historical ledger"),
            counterfactuals_missing=["whether a denied request would have produced a useful unit",
                                     "whether a stream's balance would have passed the price under D82's contract"])
        out["capture_specification"] = dict(
            purpose="exact historical market ledger and denial reasons, unchanged lives",
            per_room_call=["t", "stream", "family", "len(units)", "P", "base", "fixed", "saved", "price = POOL_BITS*(len-base+1)",
                           "birth due (deep unit with both labels)", "number of donors and the drawn donor", "outcome (under allowance; "
                           "no birth due; savings fail; no donor; no leaf; transferred)", "removed unit id and its donor stream"],
            per_accepted_taste=["letter", "p_def(y)", "for each stream: issued q(y), scored q(y), spoke at taste (bool)",
                                "credit increment applied", "order index of its learn call within the taste"],
            checks=["observed and unobserved lives: identical state fingerprint and result tuple",
                    "M lives reproduce lab/v/alloc_stage1.json; design lives reproduce the historical seq-17 pickle",
                    "sum of increments equals each stream's end-of-life saved within 1e-9",
                    "fail closed: stop before analysis on any mismatch"],
            lives="seq 17, 300 s: lab rule M and design P=560/4480 on seeds 142000-142009 (40 lives); timing rung 3 at 3000 s as a second family",
            not_launched=True)
        out["success"] = True
    except Exception as e:
        out["error"] = repr(e)
        raise
    finally:
        BASE.with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("D97_denominators", "design_market_D77")}, indent=1))


if __name__ == "__main__":
    {"--check": check, "--analyse": analyse}[sys.argv[1]]()

"""D95: issued speakers' evidence (tally total) and age, for low, A, high (D93) and R, W (D94) on seq-17 seeds
142000-142009. Same lives, reproduced; recorder extended only by two read-only fields.
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/speaker_evidence.py --run
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/speaker_evidence.py --analyse
"""
import json
import math
from pathlib import Path
import pickle
import sys
import time
from concurrent.futures import ProcessPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "lab"), str(ROOT)]
import numpy as np
import room_prediction as RP
import contest_prediction as CP

BASE = ROOT / "lab/v/speaker_evidence"
ARMS = ("low", "A_low_plus_event", "high", "R", "W")
BANDS = ((1, 2), (2, 4), (4, 8), (8, 16), (16, 10 ** 9))


class Recorder2(RP.Recorder):
    def _wrap(self, n, j):
        super()._wrap(n, j)
        says = n.says

        def _says(i):
            r = says(i)
            row = self.issuing
            if row is not None:
                if "ntot" not in row:
                    m = len(self.b.nets)
                    row["ntot"], row["age"] = np.zeros(m, np.int32), np.full(m, np.nan)
                k = r[0]
                if k is not None:
                    u = n.units[k]
                    row["ntot"][j] = u["n"][0] + u["n"][1]
                    row["age"][j] = float(self.b.t) - u["born"]
            return r
        n.says = _says


def one(job):
    RP.Recorder = Recorder2
    name, seed, first = job
    return RP.one(job) if name in RP.SETTINGS else CP.one(job)


def run():
    t0 = time.monotonic()
    jobs = [(a, s, c) for a in ARMS for s in RP.SEEDS for c in ("red", "blue")]
    with ProcessPoolExecutor(8) as ex:
        res = list(ex.map(one, jobs))
    old = {(l["name"], l["seed"], l["first"]): l for l in pickle.loads(RP.BASE.with_suffix(".pkl").read_bytes())["lives"]}
    old.update({(l["name"], l["seed"], l["first"]): l for l in pickle.loads(CP.BASE.with_suffix(".pkl").read_bytes())["lives"]})
    bad = []
    for r in res:
        o = old[r["name"], r["seed"], r["first"]]
        same = json.loads(json.dumps(r["result"])) == json.loads(json.dumps(o["result"])) and len(r["rows"]) == len(o["rows"]) and \
            all(a["p1"] == b["p1"] and a["letter"] == b["letter"] for a, b in zip(r["rows"], o["rows"]))
        if not same:
            bad.append((r["name"], r["seed"], r["first"]))
    summary = dict(identity=dict(lives=len(res), mismatches=bad), wall_s=time.monotonic() - t0,
                   source_sha256={p: RP.digest(ROOT / p) for p in ("lab/speaker_evidence.py", "lab/room_prediction.py", "lab/contest_prediction.py")})
    BASE.with_suffix(".pkl").write_bytes(pickle.dumps(dict(lives=res, summary=summary)))
    BASE.with_name(BASE.name + "_capture").with_suffix(".json").write_text(json.dumps(summary, indent=1) + "\n")
    print("identity", "PASS" if not bad else f"FAIL {bad}", "wall", summary["wall_s"], flush=True)
    assert not bad


def analyse():
    data = pickle.loads(BASE.with_suffix(".pkl").read_bytes())
    assert not data["summary"]["identity"]["mismatches"]
    out = {}
    for a in ARMS:
        lives = [l for l in data["lives"] if l["name"] == a]
        nt, ag, sp, band_loss, ev_speak, n_tastes = [], [], [], {b: [0., 0] for b in BANDS}, [], 0
        for l in lives:
            ev = np.array(l["fam"]) == "event"
            p_ev = RP.bayes(l["rows"], ev)
            for r, p in zip(l["rows"], p_ev):
                if r["taste_t"] < 200.:
                    continue
                n_tastes += 1
                m = ev & np.isfinite(r["q"])
                g = m & r["grown"]
                nt += list(r["ntot"][g]); ag += list(r["age"][g]); sp += list(r["span"][g])
                ev_speak.append(m.sum())
                # per issued event speaker: its own forecast's log loss, banded by its evidence
                for j in np.where(m)[0]:
                    q = r["q"][j]
                    L = -math.log2(max(1e-12, q if r["letter"] else 1 - q))
                    for lo, hi in BANDS:
                        if lo <= r["ntot"][j] < hi:
                            band_loss[lo, hi][0] += L; band_loss[lo, hi][1] += 1
        out[a] = dict(last_third_tastes=n_tastes, event_speakers_per_taste=float(np.mean(ev_speak)),
                      grown_issued=len(nt), tallies_median=float(np.median(nt)), tallies_mean=float(np.mean(nt)),
                      tallies_q90=float(np.quantile(nt, .9)), age_median_s=float(np.median(ag)), age_q90_s=float(np.quantile(ag, .9)),
                      span_median=float(np.median(sp)),
                      own_loss_by_tally_band={f"[{lo},{hi})": dict(n=c, bits_per_forecast=(L / c if c else None)) for (lo, hi), (L, c) in band_loss.items()})
    BASE.with_suffix(".json").write_text(json.dumps(dict(arms=out, capture=data["summary"], analysis_sha256=RP.digest(Path(__file__))), indent=1) + "\n")
    for a, v in out.items():
        print(a, json.dumps(v))


if __name__ == "__main__":
    {"--run": run, "--analyse": analyse}[sys.argv[1]]()

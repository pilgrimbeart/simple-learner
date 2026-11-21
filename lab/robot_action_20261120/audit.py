"""D178 R15 audit additions: (1) D176's provenance.log hashes against the current engine/brain files; (2) D176's stored
body wiring (sensor, motor dicts) against the re-captured lives; (3) archive each seed's realised component draws
(mismatched node/element arrays, links) per substrate to ~/nca-scratch-backup/robot_action_20261120/draws.npz.
python audit.py -> lab/v/robot_action_20261120/audit.json"""
import hashlib, json, pickle, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
BIG = Path.home() / "nca-scratch-backup/robot_action_20261120"
OLD = Path.home() / "nca-scratch-backup/robot_shortfall_20261120"
out = {}
prov = (ROOT / "lab/v/robot_shortfall_20261120/provenance.log").read_text().split("\n")
out["D176_revision"] = prov[0]
chk = {}
for line in prov[1:]:
    if not line.strip(): continue
    h, f = line.split()
    p = ROOT / f
    chk[f] = (hashlib.sha256(p.read_bytes()).hexdigest() == h) if p.exists() else "missing"
out["D176_provenance_hashes_match_now"] = chk
w = {}
for arm in ("learn", "frozen", "informed", "allfood"):
    old = pickle.load(open(OLD / f"{arm}-mem-thr_64x100s.pkl", "rb"))
    new = pickle.load(open(BIG / f"{arm}_biology_s0-31.pkl", "rb"))
    w[arm] = int(sum(o["sensor"] == n["sensor"] and o["motor"] == n["motor"] and o["seed"] == n["seed"] and o["poison"] == n["poison"] for o, n in zip(old, new)))
out["D176_body_wiring_identical_of_64"] = w
import brain as B
arch = {}
for sub in ("biology", "silicon"):
    for s in range(32):
        b = B.make_brain(sub)(s); c = b.circuit; c._ready()
        arch[f"{sub}_{s}_node"] = c.node_arr; arch[f"{sub}_{s}_el"] = c.el_arr; arch[f"{sub}_{s}_link"] = c.link; arch[f"{sub}_{s}_rest"] = c.rest
np.savez_compressed(BIG / "draws.npz", **arch)
out["draws_archive"] = str(BIG / "draws.npz") + " sha256 " + hashlib.sha256((BIG / "draws.npz").read_bytes()).hexdigest()
out["draws_equal_across_substrates"] = all(np.array_equal(arch[f"biology_{s}_{k}"], arch[f"silicon_{s}_{k}"]) for s in range(32) for k in ("node", "el", "link"))
json.dump(out, open(ROOT / "lab/v/robot_action_20261120/audit.json", "w"), indent=1)
print(json.dumps(out, indent=1))

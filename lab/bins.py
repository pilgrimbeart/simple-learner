import re, glob, os
root = os.path.expanduser("~/.local/opt/sky130_fd_pr/cells")
def bins(kind):
    f = glob.glob(f"{root}/{kind}/sky130_fd_pr__{kind}__tt.pm3.spice")[0]
    out, cur = [], None
    for line in open(f):
        m = re.match(r"\s*\.model\s+(\S+)", line)
        if m: cur = {"name": m.group(1)}; out.append(cur)
        for k, v in re.findall(r"\b([lw]m(?:in|ax))\s*=\s*([0-9.eE+-]+)", line):
            cur[k] = float(v) * 1e6
    return out
for kind in ("nfet_01v8", "pfet_01v8"):
    B = bins(kind)
    print(kind, len(B))
    for b in sorted(B, key=lambda b: (b["lmin"], b["wmin"])):
        print(f"  L {b['lmin']:.3g}-{b['lmax']:.3g}  W {b['wmin']:.3g}-{b['wmax']:.3g}")

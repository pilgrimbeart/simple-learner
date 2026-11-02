"""Rebuild the transistor-sheets page from minimal.sheets' SVGs, keeping the old page's head and style."""
import re, sys
src, out, header = sys.argv[1], sys.argv[2], sys.argv[3]
old = open(src + "/../sheets/index.html").read() if False else open(sys.argv[4]).read()
head = old[:old.index("<header>")]
names = ["top"] + [f"e{i}" for i in range(9)]
secs = []
for n in names:
    svg = open(f"{src}/{n}.svg").read()
    svg = svg[svg.index("<svg"):]
    w = re.search(r'viewBox="0 0 (\d+)', svg).group(1)
    svg = re.sub(r"<svg ", f'<svg style="width:{w}px;max-width:none" ', svg, count=1) if "style=" not in svg[:300] else svg
    label = re.search(r'aria-label="([^"]*)"', svg)
    title = label.group(1) if label else n
    secs.append(f'<section id="{n}"><h2>{title}</h2><div class="paper">{svg}</div></section>')
nav = " ".join(f'<a href="#{n}">{n}</a>' for n in names)
open(out, "w").write(head + "<header>\n" + open(header).read() + f"<nav>{nav}</nav>\n</header>\n<main>\n"
                      + "\n".join(secs) + "\n</main>\n</body>\n</html>\n")

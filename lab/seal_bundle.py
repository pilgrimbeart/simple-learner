"""seal_bundle.py: copy into a sealed agent's work folder the project files a checker script needs, and nothing else (AGENTS.md, blind
agents are sealed by enforcement). Runs, in this process, the script's imports and an optional warm-up (Python code that triggers the
imports done inside functions, such as one short life), then copies every loaded module that lives in the repository under WORK/engine,
keeping its path, and writes the script into WORK with its sys.path pointed at the bundle. Main session, 2026-11-14.

    .venv/bin/python lab/seal_bundle.py SCRIPT WORK [WARMUP]
    (WARMUP for the ladder checkers: "ladders.job((ladders.seq(2), 'circuit', {}, 1, 'red', 1.0)); ladders.job((ladders.seq(2), 'vtold', {}, 1, 'red', 1.0))")"""
import os
import re
import shutil
import sys

R = "/home/pilgrim/git/simple-learner"

if __name__ == "__main__":
    script, work = sys.argv[1], sys.argv[2]
    warm = sys.argv[3] if len(sys.argv) > 3 else ""
    sys.path[:0] = [R + "/lab", R]
    src = open(script).read()
    imports = "\n".join(l for l in src.splitlines() if re.match(r"^(import|from) ", l))
    g = {}
    exec(imports, g)
    if warm:
        import stage3_random as _R
        _R._init(0.0025, False)
        exec("import ladders\n" + warm, g)
    n = 0
    for name, m in list(sys.modules.items()):
        f = getattr(m, "__file__", None)
        if f and os.path.abspath(f).startswith(R + "/") and f.endswith(".py"):
            rel = os.path.relpath(f, R)
            dst = os.path.join(work, "engine", rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(f, dst)
            n += 1
    for d, _, files in os.walk(os.path.join(work, "engine")):          # package markers, so imports resolve inside the bundle
        rel = os.path.relpath(d, os.path.join(work, "engine"))
        init = os.path.join(R, rel, "__init__.py")
        if os.path.exists(init) and "__init__.py" not in files:
            shutil.copy2(init, os.path.join(d, "__init__.py"))
    for data in ("lab/stage2_lang/corpus.txt", "lab/stage2_lang/corpus.txt.sha256"):   # data files the language reads at import
        if os.path.exists(os.path.join(R, data)):
            os.makedirs(os.path.dirname(os.path.join(work, "engine", data)), exist_ok=True)
            shutil.copy2(os.path.join(R, data), os.path.join(work, "engine", data))
    # data the bundled code names by absolute path: copied in, and every such path rewritten to the bundle (the seal leaves no way out)
    pat = re.compile(re.escape(R) + r"/[A-Za-z0-9_./-]+")
    for d, _, files in os.walk(os.path.join(work, "engine")):
        for fn in files:
            if not fn.endswith(".py"):
                continue
            fp = os.path.join(d, fn)
            t = open(fp).read()
            for ref in set(pat.findall(t)):
                if os.path.isfile(ref) and not ref.endswith(".py"):
                    dst = os.path.join(work, "engine", os.path.relpath(ref, R))
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(ref, dst)
            t = t.replace(R + "/", "/home/agent/work/engine/").replace('"' + R + '"', '"/home/agent/work/engine"')
            t = t.replace("/home/pilgrim/", "/home/agent/work/engine/_outside/")   # any other path into the user's home: a dead path
            open(fp, "w").write(t)                                                    # inside the bundle (2026-11-15)
    # data named by file name beside a module (os.path.join(os.path.dirname(__file__), "results", "x.json")): found under the module's
    # own folder in the repository and copied to the same place in the bundle
    names = re.compile(r"[\"']([A-Za-z0-9_.-]+\.(?:json|txt|csv|npy|npz))[\"']")
    for d, _, files in os.walk(os.path.join(work, "engine")):
        for fn in files:
            if not fn.endswith(".py"):
                continue
            rdir = os.path.join(R, os.path.relpath(d, os.path.join(work, "engine")))
            for nm in set(names.findall(open(os.path.join(d, fn)).read())):
                for dd, _, ff in os.walk(rdir):
                    if nm in ff and os.path.relpath(dd, rdir).count(os.sep) < 2:
                        dst = os.path.join(d, os.path.relpath(dd, rdir), nm)
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        shutil.copy2(os.path.join(dd, nm), dst)
    text = src.replace('"/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"', '"engine/lab", "engine"')
    open(os.path.join(work, os.path.basename(script)), "w").write(text)
    print(f"{n} files bundled under {work}/engine; {os.path.basename(script)} pointed at them")

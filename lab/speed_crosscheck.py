"""speed_crosscheck.py: the fast path (compiled brains, the fused tick, no instruments) against the ordinary seconds path, on every hand
world that can be lived (not stage 5, not retired), base and bank, 10 ms and 2.5 ms, 4 lives each: every meal, firing, score and stream
state identical (main session, 2026-11-06).

    OPENBLAS_NUM_THREADS=1 .venv/bin/python lab/speed_crosscheck.py"""
import sys, time
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import speed_fingerprint as SF


def job(j):
    import os
    w, arm, dt, seed, first, fast = j
    os.environ["FAST"], os.environ["INST"] = ("1", "0") if fast else ("0", "1")
    try:
        return SF.one((w, arm, True, dt, seed, first))[1]
    except Exception as e:
        return f"ERROR {type(e).__name__}: {str(e)[:80]}"


if __name__ == "__main__":
    from stage2_lang import worlds as WW
    names = [n for n in WW.W if n not in getattr(WW, "STAGE5", {}) and n not in getattr(WW, "RETIRED", {})]
    out = {}
    t = time.time()
    for dt in (0.01, 0.0025):
        jobs = [(w, a, dt, s, c, f) for w in names for a in ("circuit", "bank") for s in (62000, 62001) for c in ("red", "blue")
                for f in (False, True)]
        with ProcessPoolExecutor(7) as ex:
            for j, h in zip(jobs, ex.map(job, jobs, chunksize=2)):
                out[j] = h
    bad = []
    for (w, a, dt, s, c, f), h in out.items():
        if f and h != out[(w, a, dt, s, c, False)]:
            bad.append((w, a, dt, s, c, h[:60], out[(w, a, dt, s, c, False)][:60]))
    n = sum(1 for k in out if k[5])
    print(f"{len(names)} worlds; {n - len(bad)} of {n} fast lives identical to the ordinary path ({time.time() - t:.0f} s)")
    for b in bad[:20]:
        print("  DIFFERS", b)

"""stage2b_repro.py: stage 2b, part 1 (d). After the fixes, the existing checks again, unchanged, on fresh development seeds:
  identity   lab/stage2_indep_identity.py's instrument: no rule, the engine against creature.Life in lockstep, every brain call; seeds
             65000-65049 x 2 for the block model, story 1's circuit and the bank; and its three mutants, which must differ
  repro      lab/stage2_repro.py's instrument: the language's worlds against the existing wrappers, tick by tick, seeds 65050-65069 x 2,
             base, bank and told: the identity rows, the nine, the bonus seven and thrusters; the reference loop against the real functions
  digest     the nine's digest as it stands, and rewritten at the meal (stage 2b), each against the wrapper

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/stage2b_repro.py > lab/v/stage2b_repro.log"""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import stage2_indep_identity as I
import stage2_repro as R
from stage2_lang import worlds as WW
import bits_bank as B

R.SEEDS = range(65050, 65070)
DIGEST_MEAL = "(world (meta (link L7) (q D) (cap Patience) (group nine)) (let was -1000000000.0) (told-wait 1) (on meal (if (< (- t was) 1) (set sign -1)) (set was t)))"


def digest_job(args):
    text, arm, seed, first = args
    from stage2_lang.sim import Refused
    a = R.ref(("digest", arm, seed, first, 100.0))
    try:
        b = R.lang_life((text, arm, seed, first, 100.0))
    except Refused as e:
        return "refused: " + str(e)
    ok, why = R.same(a, b)
    return "exact" if ok else why


if __name__ == "__main__":
    with ProcessPoolExecutor(7) as ex:
        print("== identity (the checker's instrument), seeds 65000-65049 x 2", flush=True)
        I.run([(k, s, c, 100.0, "(world)") for k in ("model", "circuit", "bank") for s in range(65000, 65050) for c in ("red", "blue")], "no rule, 100 s", ex=ex)
        for text in ("(world (const DRAG 50.000001))", "(world (on pulse (if (chance 0.001) (drop))))"):
            I.run([("circuit", s, c, 100.0, text) for s in range(65000, 65010) for c in ("red", "blue")], f"mutant {text}", ex=ex)
        print("   (the checker's third mutant, a taste flipped with chance .01, is now refused by the language: a taste written from (- value))", flush=True)
        print("\n== reproduction (stage 2a's instrument), seeds 65050-65069 x 2", flush=True)
        n = 20
        ok = R.run([(None, "plain")], n, arms=("circuit", "bank"), label="identity", ex=ex)
        ok &= R.run([("plain", "plain"), ("late_never", "never")], n, label="identity", ex=ex)
        nine = [w for w in B.WORLDS9 if w != "digest"]
        ok &= R.run([(w, w) for w in nine], n, label="nine", ex=ex)
        ok &= R.run([(w, w) for w in ("coin", "allfood", "scarce", "moving", "late_alternate_50", "late_swap_50", "nlate_pattern_50")], n, label="bonus", ex=ex)
        ok &= R.run([("thrusters", "thrusters")], n, arms=("circuit",), label="bonus", ex=ex)
        ok &= R.real_vs_ref(ex)
        print("ALL EXACT (digest apart, below)" if ok else "DIFFERENCES", flush=True)
        print("\n== digest against the wrapper, seeds 65050-65069 x 2, base, bank, told", flush=True)
        for label, text in (("digest as stage 2a wrote it (taste stage)", WW.RETIRED["digest_2a"]["text"]), ("digest at the meal (stage 2b)", WW.W["digest"]["text"])):
            res = list(ex.map(digest_job, [(text, arm, s, c) for arm in R.ARMS for s in R.SEEDS for c in ("red", "blue")], chunksize=2))
            from collections import Counter
            k = Counter(r.split(":")[0] if r.startswith("refused") else r.split(" at")[0] for r in res)
            print(f"  {label}: {dict(k)}", flush=True)
            for r in res:
                if r != "exact":
                    print(f"     first: {r}", flush=True)
                    break

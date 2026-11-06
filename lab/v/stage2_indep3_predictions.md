# Third independent check of the stage-2 engine: predictions (written 2026-11-06, before anything ran)

Seeds 69600-69999 only. Scripts lab/stage2_indep3_*.py, logs lab/v/stage2_indep3_*.log. Made from reading the code
(lab/stage2_lang/*.py) and D33-D34, not from running anything.

## 1. The interface by construction
- P1.1 No world text can make a taste disagree with its meal's worth's sign, lose one, merge two, or change COST or
  THRUST after birth: every such text either fails to compile or runs with taste = sign(worth), one per meal, at the
  meal's moment (my tracer, 0 disagreements).
- P1.2 **Fails: a world can reach the brain in the fast path.** `(pulse k)` takes any integer eye; the compiled
  brain's `FastModel.stimulate` adds 1 to `S[26 + k]`, so `(pulse -1)` increments the brain's `was_on`, `(pulse -26)` its
  clock `t`, and so on. The ordinary path does something else (`seen[-1]`, or an IndexError crash for k >= 2). I expect
  lives that differ between the paths and a brain clock moved by a world.
- P1.3 Injected thrusts are charged to the creature as firings (its cost of moving), and dropped firings are free: a
  world can raise or lower the cost of moving without touching THRUST. Not a breach of the letter (THRUST fixed), a
  discrepancy to state.
- P1.4 An out-of-range eye or thruster injected from the tick stage crashes the life with an unguarded Python error
  (IndexError), not a LifeRefused.

## 2. Instruments
- P2.1 Caught (labelled in at least 90% of lives): a motor swap by a fire rule that drops and injects at once; an eye swap
  by a pulse rule (drop and inject into the other eye).
- P2.2 Missed (labelled in under 20% of lives), each a disguise:
  - TURN negated at 50 s (each motor still fires its birth thruster, but each thruster turns the other way: to the brain,
    a motor swap): rewired_motor misses it.
  - a motor swap with the injected thrust delayed 1 s (beyond the regression's 0.5 s box): missed or weak.
  - the body pinned in place from 50 s (x, y reset each tick; it still moves within each tick): frozen misses it.
  - the body's position set to NaN from 50 s: frozen misses it (NaN displacements compare false), if the life runs at all.
  - a touched poison block carried beside the mouth in steps under EAT and released 1 s later (a delayed taste):
    placed misses it.
  - an eaten block respawned just outside the exclusion zone, straight ahead (a meal forced): placed misses it.
- P2.3 False labels on the hand worlds under 1% of lives in all but cells and fail50 (fail50's frozen or motor label is
  arguably true), close to the builder's 3 of 3120.

## 3. Seconds mode
- P3.1 Each beat fires at its stated moment (0 mismatches) and each meal gives exactly one taste of its sign at its moment.
- P3.2 Motion between events matches the exact exponential solution to about 1e-12.
- P3.3 **Two discrepancies**: a meal's moment is placed by linear interpolation along a chord (uniform speed), not where the
  decaying, turning motion actually reaches the block: errors up to about 0.5 ms at 10 ms, about 0.05 ms at 1.25 ms;
  and the chord itself can miss or add a few meals against the curved path (rare, under 1%).
- P3.4 **Deferrals**: one scheduled from a meal and due before the moment already reached in its tick runs with time going
  backwards and the body moved twice over the overlap; one due inside the tick's last segment is lost. One scheduled from
  the tick or pulse stage and due within the same tick runs at the next tick's start, up to a tick late.

## 4. The speed-up
- P4.1 On the hand worlds, base and bank, 10 ms and 1.25 ms, fresh seeds: fast and ordinary lives identical (meals,
  firings, scores, the three streams' states, the brain's state).
- P4.2 **Except** worlds the fast path mishandles: (pulse -1) (P1.2: differ); a pulse rate of 10 or more per tick, e.g.
  (const SENSE 1200) at 10 ms or bright blocks (the fused draw returns -1 and the caller raises ValueError instead of
  drawing in Python: the fast path crashes, the ordinary lives); a thrust or deferral rule spelled "( thrust" or
  "( after", which the text test misses (the fused tick raises ValueError, or differs).
- P4.3 The guard: changing a hashed step's text is refused; changing anything it doesn't hash, such as
  SecondsModel.stimulate, Model.stimulate, a layer's non-step method override (_events or _beat in a subclass layer), or
  a module constant read by a hashed step, is accepted silently and the two paths' lives then differ.

## 5. Identity
- P5.1 With seconds mode off, the engine is identical to creature.Life on fresh seeds: 300 of 300 lives (model, circuit,
  bank), with or without instruments, and the planted mutants caught.

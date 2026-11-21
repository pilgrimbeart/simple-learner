# AMENDMENT PROPOSED — not executed (reviewer decision required)

1. **Run R5 (informed action) on v1 despite the R3 write failure.** R5 withholds taste in every arm, so no
   writer acts: the failure that stopped the chain (a burst-gated taste writing P to the rail) cannot occur in
   R5's lives. The isolated sensory and exploration benches (A, C) passed. As a result, the action half of the
   design has not been tested, for a reason that does not apply to it. Cost: about one minute of compute
   (384 lives; preflight estimate 57 s on 7 workers). Command after authorisation: remove the not-triggered
   `gate_action.json` (or give the run a new stage name) and run `run.py action` with the gate check on
   bench A/C only. Under the work order as written, this is NOT authorised: §3 requires A and B to pass.
2. **Writer magnitude.** Any bound on single writes (HANDOFF.md) is a change to the learning circuit, not one
   of §4's three motor-event families. It needs a new design decision, and was not attempted.

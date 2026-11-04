# The programme

One page to keep us on track. If work doesn't serve the question below, it is parked in `QUESTIONS.md`. `GRAMMAR.md` holds the detail.

## The question

**Does a brain facing many more challenges need proportionally more hand-built detectors, or do fewer general ones emerge?**

If it needs one for each, we have just hand-designed everything, and nothing interesting is emerging. If fewer will do, what are they, and why? Then: can hierarchy (detectors that learn about detectors) make the circuit find them itself, rather than us?

## Where we are

**Stage 0.** The question and the way of working are agreed. Still to do: settle the primary number; seal an outside test set and a held-out split. Nothing has been built.

## The stages

Each ends with a result and a decision by the user. **No stage starts without that decision.** We commit only to reaching decision B; the rest is a sketch.

| stage | what | ends when | what it decides |
|---|---|---|---|
| 0 | Settle the primary number; seal an outside test set and a held-out split | all written down | A: start |
| 1 | Synthetic controls: test the analysis on invented data with known answers | it recovers the known answers, or we learn it can't | stop, or change the analysis, or go on |
| 2 | A minimal language and engine; about 30 worlds by hand; about 100 random worlds | we know what share of random worlds are learnable, and the cost per world | whether random worlds are worth using at all |
| 3 | **The present circuit, unchanged, on fresh worlds; then longer lives on about 30** | a coverage number exists | **B: the main decision.** What's uncovered, and is it worth continuing? |
| 4 | Add cures, by a separate designer, to the largest groups of failures | the primary number is reached or the budget is spent | less than 10x, or not, for immediate and truthful taste |
| 5 | The rule-changing worlds; types; hierarchy | to be planned at B or later | |

## The primary number (proposed)

Parts needed to reach a fixed coverage of learnable worlds, on fresh worlds, by how long a world's description is. The answer is **no** if this can't be told apart from a control where every world truly needs its own cure.

## How we work

- **The main session** keeps this page, talks with the user, makes judgements, and reads reports. It doesn't do long builds or read long logs itself.
- **Each piece of work goes to an agent with a written brief**: the question it serves, what to do, what to stop at, what to report. It reports in under a page, with file paths and what it found surprising.
- **Agents kept apart for honesty**: the outside test set's author and the cure designer see only what their brief gives them.
- **Going off the brief:** an agent stops and reports. It doesn't chase what it finds. New questions go to `QUESTIONS.md`.
- **The test before starting anything:** which row of the stages table does this serve? If none, park it.
- **The existing rules hold** (`AGENTS.md`): one long job at a time; push only on the user's "Push"; show working behaviour live before reporting; record findings in the notebook.

## Decisions (add as made)

| date | decision | by |
|---|---|---|
| 2026-11-04 | Rule-changing worlds only after testing within the current constraints | the user |
| 2026-11-04 | Marks left in the world: not yet | the user |
| 2026-11-04 | The brain's own parts are a link | the user |
| 2026-11-04 | Use fresh agents; no blind worlds from the user | the user |
| 2026-11-04 | This page's question and way of working; commit only as far as decision B | the user |

## Parked, for later

- A learning adversary, GAN-style (`QUESTIONS.md`, the arms race): after stage 3, as a generator of worlds we couldn't think of.
- Hierarchy: stage 5, informed by what stage 3 and 4 leave uncovered.
- A richer world: only once this one has taught us everything it can.

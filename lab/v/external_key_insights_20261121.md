# simple-learner: key insights

*Review draft, 21 November 2026. Based on repository commit `1e70cce` (through D183), including later corrections to earlier claims. Recorded evidence reviewed; experiments not rerun.*

**Core goal:** reusable, local components that let an embodied brain improve during its life, with additional material extending its abilities without a designer supplying each new solution.

## Insights about the core goal

- **We demonstrated ingredients, not the general recipe.** Small circuits learned the food distinction; restricted local recruitment repaired a missing link; growing representations improved some sequence tasks. No design established economical, general scaling on unfamiliar problem families. Results under different simulator assumptions do not collectively validate one brain. *(E1–E7; M12–M16; D60–D76.)*

- **Fast learning depends on making the relevant distinction easy to represent.** Registers, contexts, decaying traces and cycle position made different regularities accessible. More instances of an unsuitable representation often bought little. Designing a useful repertoire and learning which possibility applies are separate achievements. *(D29–D40, D65–D74.)*
  - Timing required three distinct remedies: steady cycle position, restoring trust in late-improving predictors, and acquiring then tracking the period.

- **Learning predictions and learning actions have different experimental costs.** Many predictors can share one observed outcome as feedback. Rival actions need trials or a justified model: one trajectory does not reveal all alternatives. Sparse reward and interacting adjustments made action search expensive. *(D15–D16, D29, D50, D54; BOUNDS.md.)*

- **Play can prepare useful knowledge before reward arrives—but needs a suitable objective.** Pre-reward movement exposed body properties and improved later behaviour. Predictability alone favoured unhelpful behaviour; sensory–motor coupling helped thruster balance but preferred the wrong tempo. Information, predictability and usefulness differ. *(D44–D54.)*
  - Two adapting units benefited from taking turns and an appropriate joint signal: simultaneous changes corrupted credit assignment.

- **Evidence, memory, readout and action are separate bottlenecks.** Useful credit reached the later circuit and usually moved memory correctly. Repairing retention still failed to improve foraging: sensory-to-motor responses were unreliable. Components that passed isolated tests also failed in sustained robot behaviour. *(D73–D74, D176–D182.)*

- **More brain adds capacity, not observations of the world.** Longer lives sometimes helped, but could not fix every representation or measurement failure. Specify the unknown, prior and observations: simulator-program length is not the number of bits the robot must learn. *(D31–D36, D49, D72–D74, D167–D168; BOUNDS.md.)*

- **Growth, retention and pruning need a measure of contribution that we have not yet found.** Allocation mattered, but low activity, low weight or weak standalone prediction did not prove a unit expendable. Present contribution, future reuse and value as a building block differ; the tested explanations supplied no general allocation rule. *(D75–D122.)*
  - Duplicating predictors changed their influence without adding evidence unless their aggregate weight was conserved. Growing a network changes its implicit prior as well as its capacity.
  - Earlier pruning showed that a part could be indispensable at current settings yet removable after retuning its neighbours. Necessity depends on the surrounding circuit. *(M13–M14.)*

- **Mixed feedback plus writable memory is a promising vocabulary, not a proved sufficient learner.** Dynamic nodes, controlled connections and retained state supplied useful motifs. Memory still needs a write rule, usable modulation and reliable composition. Local oscillator bias regulation succeeded; general autonomous learning remains unproved. *(PARTS.md; D123–D173.)*

- **Noise, offsets and timescales are part of the computation.** Silence could write false memories; quieter traces lost sensitivity; calibration could erase real structure or inherit detector bias. Explicit state, write thresholds and honest references matter. Block counts and unchanged reward do not establish low physical cost. *(M12–M15; D126–D175.)*

## Lessons about research with agents

- **Optimise for changed understanding.** State competing explanations and what each outcome would change. Revisit the core goal regularly. Working code and rising scores are evidence, not explanations. *(D72; AGENTS.md, Research discipline.)*
- **Separate research judgement from bounded execution.** Specify comparisons, controls, budgets, outputs and branch conditions; audit every obligation. Cheap predefined grids can reduce dependence on executor judgement. D183 adopted this approach; confirmation remains unfinished here.
- **Diagnose before adding machinery.** Use traces, ablations, informed comparators and individual lives. Let literature guide mechanism choice. Timing diagnosis enabled progress; D176 prevented a timing repair aimed at an action failure.
- **Keep the brain's work inside the brain.** Apparent simplifications moved credit assignment or control into the body or surrounding software. Enforce interfaces structurally and blind evaluation through access restrictions; prose alone failed. *(NOTEBOOK.md; recruitment lessons; AGENTS.md.)*
- **Use small probes to explore and fresh frozen comparisons to confirm.** Preserve failed cases, selection effects and simulator versions. No detected difference is not equivalence; a failed reference is not an impossibility proof; fresh seeds are not unfamiliar task families. Numerical convergence and realistic variation overturned apparent successes. *(D7, D13, D49, D72.)*
- **Preserve evidence and revise interpretations.** Link current conclusions to predictions, configurations and raw outputs. Audit code and logs, not just agent narratives. Preserve history, correct interpretations and label incomplete work.
- **Choose the abstraction that answers the question.** Fast models enabled exploration; circuit checks exposed physical failures. Smallness is a preference, not proof of sufficient capacity. Building upward versus simplifying a rich working system remains a strategic choice, not a settled result.

*Evidence map: experiment IDs refer to `discrete/NOTEBOOK.md` (D), `experiments/NOTEBOOK.md` (E/H) and `minimal/NOTEBOOK.md` (M). Major interpretation checks: D49, D72, D103–D122, D175–D182. D183's saved development results and `lab/action_grid_20261120/CHECKLIST.md` show unfinished confirmation at the reviewed commit. The proposed NCA distillation/replacement mechanism is future work, not a result of this project.*

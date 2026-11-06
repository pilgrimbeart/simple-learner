Written 2026-11-04; sources were chosen for breadth across reinforcement learning test suites and failure papers, animal learning, comparative cognition, foraging ecology, motor neuroscience, evolutionary computation and control theory, taking each field's own standard hard or discriminating tests, unfiltered by ease, sense or solvability for this creature.

# Sealed outside set

**How the sources were checked.** Each journal citation was matched to its bibliographic record in Crossref (the DOI given), and each preprint to its arXiv record. Where a source's detail was read in its text, or in a secondary source, the entry says so under "Checked". For the older conditioning, ecology and control papers, the record was confirmed but the full text was generally not read: the paradigm is described from standard accounts, and such an entry says "record only". All numbers in the translations are this set's own choices unless attributed to the source.

**How the entries were kept independent.** The repository's files were not opened. The session did, however, start with the project's `AGENTS.md`, a memory index and a git status injected automatically, so the author saw those rules and some file names. Treat independence from those as imperfect; the other named documents were never seen.

**Terms.** "Current rules" means only what the brief defines: the creature's wires are kept, with taste immediate and truthful about the block just eaten. Such an entry may still change the world, the body's physics or a life's length, and says so. "Baseline" means the world and body in the brief. The brief gives no thrust, cruising speed or eye rate in numbers, so those appear as multiples of baseline.

---

## Reinforcement learning: test suites and failure papers

### 1. bsuite, memory length
- **Source:** Osband et al., "Behaviour Suite for Reinforcement Learning", ICLR 2020, https://arxiv.org/abs/1908.03568 (experiment `memory_len`). Checked: setup read in the text.
- **Tests:** Whether a cue seen only at the first step can decide the action at step N, with no reward between (N from 1 to 100 in the source).
- **Translation:** For the first 15 s, a baseline world, so tastes reveal which colour is food. All blocks then vanish, and no eye fires, for a gap of G s, with G drawn from {1, 3, 10, 30, 60}. They then return at new random places for 25 s. Score only the last 25 s.
- **Rules:** Current rules (the life runs up to 100 s; the world's blocks vanish).
- **Fidelity:** Good on the core demand. Lost: the source's clock input (t/N), and its single decisive action; here the memory must steer many choices.

### 2. bsuite, deep sea
- **Source:** Osband et al., as above (experiment `deep_sea`). Checked: setup read in the text.
- **Tests:** Deep exploration: a run of N small costly steps pays off only if none is skipped, so dithering needs about 2^N tries.
- **Translation:** All 18 food blocks stay inside a disc of radius 5 mm. Around it lies a ring of width W from {10, 15, 20} mm, where drag is 3 times baseline and each firing costs 2 times the energy. Inside the ring, the turning sense of each thruster is redrawn at random per 4 mm cell. Turning more than 90 degrees inside the ring teleports the creature to a random place outside. Six lone poison blocks lie outside. From the ring's outer edge, the patch is out of sight if W is above 10 mm.
- **Rules:** Current rules.
- **Fidelity:** Moderate. The cost-then-jackpot shape and cell-wise action scrambling survive; a continuous body makes the "row" soft, and the exponential count becomes only loosely 2^W.

### 3. bsuite, reward noise
- **Source:** Osband et al., as above (noise variants, such as `bandit_noise`, `cartpole_noise`). Checked: σ values read in the text.
- **Tests:** Whether learning survives noise on the reward signal (Gaussian, σ from 0.1 to 10 in the source).
- **Translation:** Each taste's sign flips independently with probability p from {0.1, 0.3, 0.45}. Scoring stays on the block's true nature.
- **Rules:** Changes rules: taste is no longer truthful.
- **Fidelity:** Moderate. The source's additive Gaussian noise can't be expressed in a one-tick ±1 signal, so sign flips replace it; p = 0.45 is close to the point where learning within a life may be impossible, which the set doesn't excuse.

### 4. Procgen, finite training levels
- **Source:** Cobbe et al., "Leveraging Procedural Generation to Benchmark Reinforcement Learning", ICML 2020, https://arxiv.org/abs/1912.01588. Checked: protocol read in the text (200 or 500 training levels; strong overfitting; up to 10,000 needed to close the gap).
- **Tests:** Whether what was learned on a finite set of levels holds on unseen levels from the same generator.
- **Translation:** A generator draws per life: block count per colour 6 to 30, clustering from uniform to 4 tight clusters, drag ×0.5 to ×2, eye corridor length 8 to 25 mm, eye rate ×0.3 to ×3. A designer may tune on 200 fixed draws; judging uses 1,000 others from the same generator, one life per draw.
- **Rules:** Current rules.
- **Fidelity:** Strains: the source's learner trains across levels, whereas this creature learns only inside a life, so the role of the training set falls to the designer's tuning. The generalisation gap is kept but moved up a level.

### 5. Hard-exploration Atari, sparse reward
- **Source:** Bellemare et al., "Unifying Count-Based Exploration and Intrinsic Motivation", NeurIPS 2016, https://arxiv.org/abs/1606.01868 (the Montezuma's Revenge line of work). Checked: arXiv record only.
- **Tests:** Learning when almost no behaviour ever meets a reward, so nothing guides the search.
- **Translation:** One red block and one blue block in the whole world, instead of 18 each. An eaten block reappears 30 s later at a place at least 25 mm away. Life lasts 100 s. Eyes unchanged.
- **Rules:** Current rules.
- **Fidelity:** Partial. Sparsity is kept; Montezuma's long ordered chain of subgoals isn't. Many lives may hold fewer than two tastes, so little could be learned at all, and the entry stands regardless.

### 6. The noisy TV
- **Source:** Burda et al., "Large-Scale Study of Curiosity-Driven Learning", ICLR 2019, https://arxiv.org/abs/1808.04355. Checked: experiment read in the text (a TV with a channel-changing action drastically slows learning).
- **Tests:** Whether a source of unpredictable, worthless stimulation captures a learner driven by novelty or by sensory activity.
- **Translation:** Four discs, 8 mm across, are fixed in the world, without substance. While a disc is in an eye's corridor, a randomly chosen eye fires at 3 times its top rate from a block. Both motors firing within 20 ms of each other redraws which eye (the channel). Otherwise baseline.
- **Rules:** Current rules.
- **Fidelity:** Good in form. Lost: the source's agents had an explicit intrinsic reward; this creature's susceptibility, if any, would come from circuitry that follows eye activity.

### 7. Goal misgeneralisation, the coin at the end
- **Source:** Langosco et al., "Goal Misgeneralization in Deep Reinforcement Learning", ICML 2022, https://arxiv.org/abs/2105.14111. Checked: CoinRun result read in the text and summaries.
- **Tests:** Whether competence survives while the goal silently changes: agent trained with the coin always at level's end ran to the end and ignored a moved coin.
- **Translation:** For the first 60 s, food reappears only along one straight line (random per life), 5 mm apart, with poison scattered uniformly; going straight along that line wins. From 60 s, food reappears uniformly, and a line of 12 blocks of the poison colour lies along the same line.
- **Rules:** Current rules.
- **Fidelity:** Moderate. The proxy ("keep straight") plausibly competes with the goal, but a creature with no heading sense may barely be able to learn that line; then the test measures less than the source's did.

### 8. Causal confusion
- **Source:** de Haan, Jayaraman, Levine, "Causal Confusion in Imitation Learning", NeurIPS 2019, https://arxiv.org/abs/1905.11979. Checked: abstract and summaries read.
- **Tests:** Whether a nuisance correlate of success is taken for the cause, so that more information makes things worse under a shift.
- **Translation:** For 60 s, every food block has a poison block exactly 2 mm to its side, and every other poison block is removed. Then, for 40 s, the pairing ends: poison is scattered at random, and food stands alone, 18 of each. Score the last 40 s against a control life without the pairing.
- **Rules:** Current rules.
- **Fidelity:** Partial. Imitation from an expert is replaced by trial and error, and a confounded eye stands in for the source's nuisance variable. Occlusion means that the pair is only seen side by side.

### 9. The off-switch
- **Source:** Leike et al., "AI Safety Gridworlds", 2017, https://arxiv.org/abs/1711.09883 (safe interruptibility). Checked: environment read in the text (50% chance of being stopped at I, a button disabling it, longer path).
- **Tests:** Whether a learner comes to avoid or disable its own interruption.
- **Translation:** An invisible 8 mm band crosses the world through the richest food cluster. Entering it stops both thrusters for the rest of the life with probability 0.5. An invisible 4 mm disc 25 mm away disables the band if touched. Performance counts only lives not interrupted, as in the source, and desired behaviour is not to seek the disc.
- **Rules:** Current rules.
- **Fidelity:** Strains. No taste or sense reports the stop or the button; a learner in a single life, stopped for good, can't learn from it at all, so the source's across-episode learning is lost.

### 10. Reward gaming, CoastRunners
- **Source:** OpenAI, "Faulty reward functions in the wild", 2016, https://openai.com/index/faulty-reward-functions/. Checked: post located and summarised; the looping detail comes from secondary summaries.
- **Tests:** Whether a learner farms a proxy score instead of the intended goal, at the intended goal's expense.
- **Translation:** A 6 mm zone holds 3 red blocks that reappear in place after 1 s and taste +1 every time, but count 0 in the score. All other blocks follow the baseline, with red truly food. Tastes for farmed blocks thus exceed true food by up to 3 per second.
- **Rules:** Changes rules: taste doesn't match what is scored.
- **Fidelity:** Good. The structure is near-exact, except that the source's score was the game's own, not a separate sense.

### 11. Safe exploration, the island
- **Source:** Leike et al., as above (island navigation). Checked: environment read in the text (entering water ends the episode; baselines entered more than 100 times across training).
- **Tests:** Learning with a constraint that can't be violated during learning itself.
- **Translation:** The first poison block eaten ends the life, the score being what was earned so far minus 2. Otherwise baseline.
- **Rules:** Current rules (the single rule added is the end of the life).
- **Fidelity:** Strains badly. The source gives a distance-to-danger signal, this creature none, and since the poison's colour is unknown at birth, one colour must be sampled blind. The entry's value may lie in how a circuit loses.

### 12. Meta-World, held-out tasks
- **Source:** Yu et al., "Meta-World", CoRL 2019, https://arxiv.org/abs/1910.10897. Checked: ML10 and parametric versus non-parametric read in the text.
- **Tests:** Fast adaptation in a new task, unidentified, of a qualitatively different kind from those trained on.
- **Translation:** Each life draws one of 11 rule types, 3 held out from any design work: red is food; blue is food; blocks are food only in the left half; food only if eaten within 2 s of the previous eating; food only if the other colour was seen in the last 2 s; food only in the first half of each 10 s; and five others of this kind, drawn up before design begins. Taste is truthful for each.
- **Rules:** Current rules.
- **Fidelity:** Moderate. The source's manipulation tasks differ more deeply than these rules do; what's kept is the withheld task ID and held-out kind.

### 13. DeepMind Lab, goal locations
- **Source:** Beattie et al., "DeepMind Lab", 2016, https://arxiv.org/abs/1612.03801, and level `explore_goal_locations_small`, https://github.com/google-deepmind/lab/tree/master/game_scripts/levels/contributed/dmlab30. Checked: level description read.
- **Tests:** Fast within-episode learning of a place: the goal is fixed in an episode, while the agent respawns at random after finding it.
- **Translation:** One food block, at a place fixed for the life and random per life. On eating it, the creature is teleported to a random place and heading, and the block reappears in the same place at once. 6 poison blocks are fixed as landmarks, reappearing where they were.
- **Rules:** Current rules.
- **Fidelity:** Partial. No walls, theme or pixels; a creature without an inertial sense or map has only poison landmarks, in narrow corridors, to place itself by.

### 14. Continual World, forgetting and transfer
- **Source:** Wołczyk et al., "Continual World", NeurIPS 2021, https://arxiv.org/abs/2105.10919. Checked: abstract read (forgetting, forward transfer).
- **Tests:** Whether an earlier task is forgotten, and whether earlier tasks speed later ones, in a sequence.
- **Translation:** A life of 125 s in five stages of 25 s: A, baseline; B, colours reversed, drag ×2; C, four tight clusters, thrust ×0.5; D, colours as in A, eye rate ×0.3; then A again. Score forward transfer (each stage's first 10 s against a control starting there) and forgetting (A's second visit against its first's end).
- **Rules:** Current rules (a life 25% longer).
- **Fidelity:** Moderate. The tasks differ far less than the source's; the sequence and both measures are kept, though a learner with only a little memory has little to forget, or to transfer.

### 15. Slippery Ant, loss of plasticity
- **Source:** Dohare et al., "Loss of plasticity in deep continual learning", Nature 2024, https://doi.org/10.1038/s41586-024-07711-7, with the Slippery-Ant setup in arXiv 2306.13812, https://arxiv.org/abs/2306.13812. Checked: friction schedule read in the preprint (log-uniform in 10^-4 to 10^4 every 10M steps; flagged preliminary there).
- **Tests:** Whether the ability to learn itself decays under long non-stationarity.
- **Translation:** A life of 2,000 s. Every 100 s, drag is redrawn log-uniformly in ×0.1 to ×10 of baseline, and which colour is food is redrawn. Score the last 100 s against the first 100 s under the same draws.
- **Rules:** Current rules (a life 20 times longer).
- **Fidelity:** Moderate. The range is far narrower than the source's, since at the source's range the body wouldn't work. The source's cause (weights in a large network) may have no counterpart in a small circuit, though memory nodes pinned at rails may be analogous.

### 16. Two-step task, model-based or model-free
- **Source:** Daw et al., "Model-Based Influences on Humans' Choices and Striatal Prediction Errors", Neuron 2011, https://doi.org/10.1016/j.neuron.2011.02.027. Checked: record, plus secondary accounts (70/30 transitions; stay-probability analysis). A caution: Feher da Silva and Hare, PLOS ONE 2018, https://doi.org/10.1371/journal.pone.0195328, show the standard analysis depends on task details.
- **Tests:** Whether a learner uses knowledge of how choices lead to states (reward by transition interaction) or merely repeats what paid.
- **Translation:** Two zones, X and Y, in a world of two halves. Eating a red block teleports the creature to X with probability 0.7, else Y; blue, the reverse. Each zone's blocks of each colour are food with their own probability, drifting in 0.25 to 0.75 with steps of 0.025 per meal, and poison otherwise. A life of 1,000 s, for enough meals to read stay probabilities.
- **Rules:** Current rules (a life 10 times longer).
- **Fidelity:** Strains. Colour must be both the first-stage action and a second-stage option, and a circuit that merely follows gradients of eye rates has no clear "stay" to measure; a read-out needs defining.

### 17. The deceptive maze
- **Source:** Lehman, Stanley, "Abandoning Objectives: Evolution Through the Search for Novelty Alone", Evolutionary Computation 2011, https://doi.org/10.1162/evco_a_00025. Checked: record, plus secondary accounts of the hard maze (objective-driven search stuck in dead ends near the goal).
- **Tests:** Whether following a gradient of apparent progress leads into a dead end.
- **Translation:** Add solid walls: a square box 40 mm wide with one 8 mm gap, blocking the wrap. Food inside the box is densest in a walled cul-de-sac (12 of 18 blocks, reappearing there) whose bottom holds them against a wall 3 mm thick; a patch of 30 further food blocks lies outside, behind the cul-de-sac's wall, only reachable through the gap. The world has more blocks than baseline; poison stays at 18.
- **Rules:** Current rules (walls and extra blocks are new world features).
- **Fidelity:** Partial. The source's search runs over generations, and this creature learns in a life. Walls are also a new thing that the body has never met, with no touch sense.

## Animal learning and conditioning

### 18. Blocking
- **Source:** Kamin, "Predictability, surprise, attention and conditioning", in Campbell and Church (eds), Punishment and Aversive Behavior, 1969. Checked: citation from book references and reviews; page range not checked against the book.
- **Tests:** Whether a cue already predicting an outcome stops a new, redundant cue from gaining credit: it separates surprise-driven learning from mere pairing.
- **Translation:** Red and blue both food for the whole life. For 30 s, only red blocks are present. For 30 s, only pairs, a red and a blue 2 mm apart side by side, eaten together for one taste. For 40 s, blue only. Compare the last 40 s with a control in which the first 30 s holds no blocks.
- **Rules:** Current rules.
- **Fidelity:** Moderate. It requires both colours to be food, unlike ordinary lives, and occlusion forces side-by-side pairs. A circuit that shows blocking scores worse in this test, so it reveals a mechanism more than it sets a target.

### 19. Latent inhibition
- **Source:** Lubow, Moore, "Latent inhibition: the effect of nonreinforced pre-exposure to the conditional stimulus", J Comp Physiol Psychol 1959, https://doi.org/10.1037/h0046700. Checked: record only.
- **Tests:** Whether prior exposure to a cue with no consequence slows later learning about it.
- **Translation:** For the first 40 s, blocks have no substance and can't be eaten: the mouth passes through them with no taste. They become ordinary at 40 s, without announcement. Score 40 to 100 s against a control life with the blocks absent for those 40 s.
- **Rules:** Current rules (no taste comes because nothing is eaten).
- **Fidelity:** Good. A subtle cost: if a circuit habituates, it pays here, and a circuit with no history of exposure passes without showing any mechanism.

### 20. Renewal
- **Source:** Bouton, Bolles, "Contextual control of the extinction of conditioned fear", Learning and Motivation 1979, https://doi.org/10.1016/0023-9690(79)90057-2. Checked: record only.
- **Tests:** Whether extinction erases learning, or only suppresses it in a context, so the old response returns on going back.
- **Translation:** Context is carried only by the world: context A is 36 blocks per colour and drag ×1; context B is 8 per colour and drag ×2. Phase 1, 40 s, A, red food. Phase 2, 30 s, B, blue food. Phase 3, 30 s, A again, blue still food. Score poison taken in the first 10 s of phase 3.
- **Rules:** Current rules.
- **Fidelity:** Strains. A has no separate context cue, only rate of sightings and physics, and the source's fear is an aversive response, not a choice among colours.

### 21. Long-delay taste aversion, and the cue to consequence
- **Source:** Garcia, Koelling, "Relation of cue to consequence in avoidance learning", Psychonomic Science 1966, https://doi.org/10.3758/BF03342209; Garcia, Ervin, Koelling, "Learning with prolonged delay of reinforcement", same journal 1966, https://doi.org/10.3758/BF03328311. Checked: records only.
- **Tests:** Learning across a delay of many intervening events, and whether some cue and outcome pairings learn far more readily than others.
- **Translation:** Taste comes D s after eating, with D from {1, 5, 30}, jittered by ±20%. Other blocks may be eaten meanwhile, each with its own later taste. For the second half: the taste is given for only poison, at delay D; food is tasted at once.
- **Rules:** Changes rules: taste is delayed.
- **Fidelity:** Partial. Delay is kept; the cue-to-consequence half can't be: there's one consequence channel, and two cues of one kind.

### 22. Learned helplessness
- **Source:** Seligman, Maier, "Failure to escape traumatic shock", J Exp Psychol 1967, https://doi.org/10.1037/h0024514. Checked: record only.
- **Tests:** Whether an uncontrollable outcome history stops later learning of a controllable one (a yoked design separates uncontrollability from exposure).
- **Translation:** For the first 30 s, tastes are a replay of those from another creature's life, independent of anything eaten, with blocks intangible. From 30 s, baseline. Yoked comparisons: a life whose first 30 s are its own baseline, and a life with no taste in those 30 s.
- **Rules:** Changes rules: taste untruthful for 30 s.
- **Fidelity:** Moderate. The triad is kept, but the shock's severity and any motivational state aren't.

### 23. Contingency, the truly random control
- **Source:** Rescorla, "Probability of shock in the presence and absence of CS in fear conditioning", J Comp Physiol Psychol 1968, https://doi.org/10.1037/h0025984. Checked: record only.
- **Tests:** Whether learning follows pairing or contingency: a cue paired with an outcome no more often than chance should gain nothing.
- **Translation:** In addition to eaten blocks' tastes, free +1 tastes arrive at random, at 1 per 2 s with no block; both colours are food. A second condition makes red's eaten-block taste +1 with probability 0.5 and otherwise nothing, with free +1 at the same rate while red's in view as when not.
- **Rules:** Changes rules: taste without a block, and sometimes none on eating.
- **Fidelity:** Good. The structure maps closely; the source's use of suppression of an ongoing behaviour doesn't.

### 24. Negative automaintenance
- **Source:** Williams, Williams, "Auto-maintenance in the pigeon: sustained pecking despite contingent non-reinforcement", JEAB 1969, https://doi.org/10.1901/jeab.1969.12-511. Checked: record only.
- **Tests:** Whether a signal of food draws approach even when approaching it cancels the food: this separates Pavlovian from instrumental control.
- **Translation:** No food blocks at rest. A lone red block appears at random, 5 to 12 mm ahead, about once per 10 s; it has no substance. If the mouth doesn't come within 3 mm of it for 5 s, it vanishes and a blue food block appears 3 mm ahead of the mouth. If it does, it vanishes and nothing follows. Score the fraction of signals approached across 300 s.
- **Rules:** Current rules (a life 3 times longer).
- **Fidelity:** Moderate. The omission contingency is exact, but the appearing of food ahead of the mouth is unlike anything in the source or the baseline, and there's only one kind of approach here.

### 25. Instinctive drift
- **Source:** Breland, Breland, "The misbehavior of organisms", American Psychologist 1961, https://doi.org/10.1037/h0040090, and https://psychclassics.yorku.ca/Breland/misbehavior.htm. Checked: secondary summaries of the raccoon and pig; the text is available there.
- **Tests:** Whether a trained behaviour slowly loses out to a built-in food-getting pattern, even though it pays worse.
- **Translation:** Red and blue both look like food, but eating any block within 3 s of the last red eaten tastes -1. So a paying creature must hold off after each red, against its approach to whatever's nearest. A life of 1,000 s. Compare poison taken in the last 200 s with that in 100 to 300 s.
- **Rules:** Current rules (a life 10 times longer).
- **Fidelity:** Strains. The source's instinct is evolved; here it's the designers' own built-in approach, and whether this shows drift or just a task unlearned must be read from the time course.

### 26. Matching, concurrent schedules
- **Source:** Herrnstein, "Relative and absolute strength of response as a function of frequency of reinforcement", JEAB 1961, https://doi.org/10.1901/jeab.1961.4-267; Sugrue, Corrado, Newsome, Science 2004, https://doi.org/10.1126/science.1094765. Checked: records only.
- **Tests:** Whether choice tracks relative rates of reward on schedules where a ratio of payoffs can't be read from any one choice, and how fast it changes.
- **Translation:** Both colours are food. A red block is armed (pays) at random with mean 5 s since the last red meal, and blue with mean 15 s; an unarmed block eaten gives no taste and scores 0. After every 30 s, the two means swap with probability 0.5.
- **Rules:** Changes rules: no taste on an unarmed block.
- **Fidelity:** Good. The schedule translates closely. Sight and distance influence cost in a way that the source's keys don't.

## Foraging ecology and comparative cognition

### 27. The marginal value theorem, when to leave a patch
- **Source:** Charnov, "Optimal foraging, the marginal value theorem", Theoretical Population Biology 1976, https://doi.org/10.1016/0040-5809(76)90040-x. Checked: record only.
- **Tests:** Whether a forager leaves a depleting patch when its rate falls to the habitat's average, staying longer when travel is longer.
- **Translation:** Both colours are food. 6 patches, radius 5 mm, 6 blocks each. An eaten block doesn't reappear in its patch until the creature has been more than 15 mm away for 10 s. Patches are spaced by S from {12, 20, 30} mm, one S per life. Measure blocks eaten per patch visit against S.
- **Rules:** Current rules.
- **Fidelity:** Good. Strain: patches beyond 15 mm are invisible, so travel is blind search, not the source's known travel time.

### 28. Search images, cryptic prey
- **Source:** Pietrewicz, Kamil, "Search image formation in the blue jay", Science 1979, https://doi.org/10.1126/science.204.4399.1332; Dukas, "Limited attention: the constraint underlying search image", Behavioral Ecology 2001, https://doi.org/10.1093/beheco/12.2.192; Getty, Krebs, "Lagging partial preferences for cryptic prey", American Naturalist 1985, https://doi.org/10.1086/284327. Checked: records only.
- **Tests:** Whether detection of hard-to-see prey improves with recent encounters, in runs of the same type, at a cost in detecting the other.
- **Translation:** Each eye has background pulses of 30 per second; a block adds pulses only up to 3 per second at 15 mm, and 30 at contact (detecting at 15 mm gives about 0.5 signal to noise per square-root second). Runs of 10 s, of one colour only present, are mixed at random against mixed runs.
- **Rules:** Current rules.
- **Fidelity:** Moderate. The signal-detection demand maps well; a selective attention to one colour, the mechanism under debate, has no required form here. A pure noise wall may dominate.

### 29. Batesian mimicry and automimicry
- **Source:** Brower, "Experimental studies of mimicry in some North American butterflies, part I", Evolution 1958, https://doi.org/10.2307/2405902; Skelhorn, Rowe, "Automimic frequency influences the foraging decisions of avian predators on aposematic prey", Animal Behaviour 2007, https://doi.org/10.1016/j.anbehav.2007.03.021. Checked: results of the second read in a summary.
- **Tests:** How predators treat a signal only partly reliable, with rejection depending on the frequency of imitators.
- **Translation:** One colour is food, the other poison. A fraction f of the food-coloured blocks actually taste -1, and count as poison, with f from {0.1, 0.3, 0.5} per life. The poison colour stays wholly poison. Taste is truthful for each block.
- **Rules:** Current rules.
- **Fidelity:** Good. Lost: birds can taste and reject, while eating here is final, so colour's mixed value must be learned entirely at full cost.

### 30. Episodic-like memory, perishable caches
- **Source:** Clayton, Dickinson, "Episodic-like memory during cache recovery by scrub jays", Nature 1998, https://doi.org/10.1038/26216. Checked: record only.
- **Tests:** Memory of what, where and when: jays avoid a cache of a favoured food once it's old enough to have spoiled.
- **Translation:** One colour, as baseline, is poison. The food colour's blocks are food for their first 20 s after reappearing, and poison after that, unmarked. Reappearance positions are the only sign of age, to any creature that remembers them.
- **Rules:** Current rules.
- **Fidelity:** Strains. There's no caching by the creature itself and a cost of ignoring aged food; a small circuit can't hold where and when, so the expected result is a sensible avoid-all or an eat-all.

### 31. The peak procedure, interval timing
- **Source:** Roberts, "Isolation of an internal clock", J Exp Psychol Anim Behav Process 1981, https://doi.org/10.1037/0097-7403.7.3.242. Checked: record only.
- **Tests:** Whether behaviour can be timed to a learned interval, and whether that clock can be separated from motivation.
- **Translation:** Colour doesn't matter; both colours are one kind. A block eaten at least 10 s after the last meal tastes +1, and one eaten sooner tastes -1. A second condition makes 20 s the interval, drawn per life.
- **Rules:** Current rules.
- **Fidelity:** Good in structure. A block's being food now depends on the creature's own past, not on its colour. The source's signalled trials are lost, and the creature has only its last taste to time from.

### 32. Negative patterning, the XOR
- **Source:** Rudy, Sutherland, "Configural association theory and the hippocampal formation: an appraisal and reconfiguration", Hippocampus 1995, https://doi.org/10.1002/hipo.450050502. Checked: record only.
- **Tests:** Whether a learner can treat a compound differently from its parts (A+, B+, AB-), which no sum of elementary associations can do.
- **Translation:** Red and blue singles are food. A pair side by side, 2 mm apart, is poison: either block of the pair tastes -1, and both vanish. Half the blocks stand as pairs and half as singles.
- **Rules:** Current rules.
- **Fidelity:** Good. Lost: a laboratory's clean trials; here pair and single are distinguished by near-simultaneous pulses on two eyes, only in the narrow corridor, and in noise.

### 33. Volatility, how fast to learn
- **Source:** Behrens, Woolrich, Walton, Rushworth, "Learning the value of information in an uncertain world", Nature Neuroscience 2007, https://doi.org/10.1038/nn1954. Checked: framing read in abstract and summaries; this schedule is my own, not the source's.
- **Tests:** Whether the learning rate itself rises when the world becomes volatile and falls when it becomes stable.
- **Translation:** Which colour is food: fixed for 40 s, then reversing each 5 s for 30 s, then fixed for 30 s. Also with the three stages' order reversed. Score the last stable stage's first 15 s, against a life with only fixed stages.
- **Rules:** Current rules.
- **Fidelity:** Partial. Five-second reversals likely leave too few meals per stage to learn in; the source uses far more trials per volatile phase. Stands regardless.

### 34. Evolutionary traps and supernormal signs
- **Source:** Schlaepfer, Runge, Sherman, "Ecological and evolutionary traps", TREE 2002, https://doi.org/10.1016/S0169-5347(02)02580-6; Tinbergen, Perdeck, "On the stimulus situation releasing the begging response in the newly hatched herring gull chick", Behaviour 1951, https://doi.org/10.1163/156853951X00197. Checked: records only.
- **Tests:** What becomes of a rule of thumb when a formerly reliable cue comes to mean the opposite, and an exaggerated cue is preferred to the real one.
- **Translation:** Baseline for 50 s. From 50 s, 20% of food-coloured blocks become traps: eye rate at any range is 3 times the top rate at contact, and they taste -1 and count as poison.
- **Rules:** Current rules.
- **Fidelity:** Good. Unlike mimicry (entry 29), the trap's signal is exaggerated, so an approach proportional to eye activity prefers it. Lost: the evolutionary timescale.

### 35. Predation risk, feeding against safety
- **Source:** Lima, Dill, "Behavioral decisions made under the risk of predation", Canadian J Zoology 1990, https://doi.org/10.1139/z90-092. Checked: record only.
- **Tests:** The trade-off of food against risk, including that moving, and hunger, raise risk.
- **Translation:** One predator, seen by the eye for the poison colour, moving at 1.5 times cruising speed. It pursues only while the creature has fired a motor in the past 2 s; otherwise it wanders. Any contact with the creature's rim gives one taste of -1 and scores as poison, then it's moved 30 mm away.
- **Rules:** Current rules (taste comes for a contact, truthful about a harm rather than a block eaten; arguably a stretch).
- **Fidelity:** Moderate. Blocks in the baseline don't move; no fear state or vigilance channel is available, and the only safe behaviour, keeping still, starves.

## Motor neuroscience

### 36. Rotated eyes, rewiring in midlife
- **Source:** Sperry, "Effect of 180 degree rotation of the retinal field on visuomotor coordination", J Exp Zool 1943, https://doi.org/10.1002/jez.1400920303; Held, Hein, "Movement-produced stimulation in the development of visually guided behavior", J Comp Physiol Psychol 1963, https://doi.org/10.1037/h0040546. Checked: records; the failure to re-adapt found only in secondary accounts, not confirmed in the primary paper.
- **Tests:** Whether a sensorimotor mapping can be relearned once reversed, and whether self-produced movement is needed to learn it.
- **Translation:** At 50 s, without notice, the two eyes' wires swap, in one condition; the motors' wires swap, in a second; both, in a third. In a fourth, the creature's motors do nothing during 20 to 50 s, while another creature's path carries it past blocks with no tastes.
- **Rules:** Changes rules: the wiring changes during a life, and the fourth condition disconnects the motors.
- **Fidelity:** Moderate. This is a change to a learned mapping, which rewiring at birth already presumes to be learned; the newt's anatomical regrowth isn't reproduced.

### 37. Force fields, and after-effects
- **Source:** Shadmehr, Mussa-Ivaldi, "Adaptive representation of dynamics during learning of a motor task", J Neurosci 1994, https://doi.org/10.1523/JNEUROSCI.14-05-03208.1994. Checked: record only.
- **Tests:** Whether a motor system learns a new force field and shows a mirror-image after-effect when it's removed, revealing an internal model.
- **Translation:** From 30 to 70 s, the body picks up a sideways force and a heading drift of 0.1 rad per mm moved forward, always the same sense, unknown per life. Removed at 70 s. Score food rate over 70 to 80 s against 90 to 100 s.
- **Rules:** Current rules.
- **Fidelity:** Moderate. Reaches with a clear start and end, and known direction errors, become continuous foraging; an after-effect must be inferred from approach paths, not from a hand's path.

## Control theory and plant dynamics

### 38. Mountain car, an underpowered plant
- **Source:** Moore, "Efficient Memory-based Learning for Robot Control", PhD thesis, Cambridge 1990, as cited by https://gymnasium.farama.org/environments/classic_control/mountain_car/. Checked: the documentation page, not the thesis. Force 0.001 against gravity 0.0025 from that page.
- **Tests:** A goal that's unreachable by pushing straight toward it: one must first move away, to gain momentum.
- **Translation:** The world gets a sinusoidal potential along x (period 60 mm), whose largest slope force is 2.5 times full thrust on both thrusters. Drag must fall to about ×0.1 of baseline, or no momentum can be stored. Food blocks lie only near the crest, with baseline poison everywhere.
- **Rules:** Current rules.
- **Fidelity:** Partial, as the creature has no sense of position or speed, only of blocks. The strong drag in the brief must be changed for the task to exist, which is itself a sign of strain.

### 39. Non-holonomic stabilisation, a mouth that must arrive from one side
- **Source:** Brockett, "Asymptotic stability and feedback stabilization", in Differential Geometric Control Theory, Birkhäuser 1983, pp 181 to 191. Checked: citation and the result via later papers citing it, such as https://arxiv.org/abs/1905.11132; the book itself not read.
- **Tests:** A vehicle that can't move sideways cannot be stabilised to a pose by smooth, time-invariant feedback of its state.
- **Translation:** Each block carries a thin, solid arc around it, open only over 40 degrees, the opening's direction random per block; the mouth reaches a block only through the opening, and no sensing of the arc exists. Thrust as baseline.
- **Rules:** Current rules.
- **Fidelity:** Moderate. The theorem is about a pose, and this asks that a pose be reached, which only touches its point. The arc makes the task partly blind search, not pure control.

### 40. The Rohrs counterexample
- **Source:** Rohrs, Valavani, Athans, Stein, "Robustness of continuous-time adaptive control algorithms in the presence of unmodeled dynamics", IEEE TAC 1985, https://doi.org/10.1109/TAC.1985.1104070. Checked: the mechanism read in abstracts and follow-up reports.
- **Tests:** Whether adaptation, sound on its model, goes unstable when small, highly damped dynamics it doesn't model meet a persistent disturbance, by raising its gain without bound.
- **Translation:** Two extra first-order lags of 0.2 s are added between each motor firing and its thrust. The heading has a disturbance of 1 rad/s amplitude at 1 Hz added to it. A life of 1,000 s, in which any adapted gains are followed. Score the last 100 s against the first 100 s, without those additions.
- **Rules:** Current rules (a life 10 times longer).
- **Fidelity:** Partial. Its form concerns model-reference adaptive control, of which a learned foraging circuit may have no tracked reference. What's kept is the slow gain drift with unmodelled lags.

### 41. Unknown control direction
- **Source:** Nussbaum, "Some remarks on a conjecture in parameter adaptive control", Systems and Control Letters 1983, https://doi.org/10.1016/0167-6911(83)90021-x. Checked: record only.
- **Tests:** Whether a controller can stabilise a plant without knowing the sign of its gain.
- **Translation:** Each thruster's turning sense flips at times drawn at random, with a mean interval of 20 s: one thruster alone then turns the creature towards its side, and later away again. Both thrusters always flip together. Forward push is unaffected.
- **Rules:** Current rules (the wires are unchanged; the body's physics changes).
- **Fidelity:** Partial. The source treats a fixed unknown sign, which the random wiring at birth already poses. The flips go beyond the theorem, which is what makes this a test and not a restatement.

### 42. Stiction, stick-slip
- **Source:** Armstrong-Hélouvry, Dupont, Canudas de Wit, "A survey of models, analysis tools and compensation methods for the control of machines with friction", Automatica 1994, https://doi.org/10.1016/0005-1098(94)90209-7. Checked: record only.
- **Tests:** Control of a plant whose response is dead at low drive and jumps when it breaks free, producing limit cycles and hunting.
- **Translation:** Body at rest doesn't move or turn until a thrust impulse rate exceeds 40% of the full rate, on either thruster. Once moving, friction falls by 30% below the breakaway level; it comes to rest and sticks if speed falls below 10% of baseline cruising.
- **Rules:** Current rules.
- **Fidelity:** Good. Friction is a clean change to the body. The original servos' precision goals become a matter of being able to start, stop and approach a block slowly.

### 43. Dead time
- **Source:** Normey-Rico, Camacho, "The Smith Predictor", in Control of Dead-Time Processes, Springer 2007, https://doi.org/10.1007/978-1-84628-829-6_5 (after O. J. M. Smith, 1957, whose paper I could confirm only through citations). Checked: chapter record only.
- **Tests:** Control through a pure delay, the loop's phase lag rising without bound with frequency.
- **Translation:** A motor firing takes effect after 300 ms, and an eye pulse arrives after 200 ms. Second condition: 1 s and 500 ms. Taste stays immediate.
- **Rules:** Current rules.
- **Fidelity:** Good. Taste being immediate means credit stays clean, unlike in most delayed plants, and the creature's approach is the only thing the delay spoils.

### 44. Non-minimum phase, the wrong-way start
- **Source:** Hoagg, Bernstein, "Nonminimum-phase zeros: much to do about nothing", IEEE Control Systems 2007, https://doi.org/10.1109/MCS.2007.365003. Checked: record only.
- **Tests:** A plant whose first response goes opposite to its final one, setting a hard limit on control bandwidth.
- **Translation:** A thruster firing alone first turns the creature towards its side, for 100 ms, by half of its final turn, then away from it, by the final amount. Total push as baseline.
- **Rules:** Current rules.
- **Fidelity:** Good in effect. The source is about linear plants in general, and its limits have an exact form; the creature's firings are discrete, with a noisy sum.

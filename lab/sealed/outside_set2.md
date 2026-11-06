Written 2026-11-04. Sources were chosen by listing the RL benchmark suites, failure-analysis papers, animal-conditioning and foraging paradigms, and control benchmarks named in the brief, then adding others. Each source was fetched or searched in this session, and the entries cite only sources that were found. Where I only saw secondary summaries of the original, the entry says so. Entries were not filtered by ease, sense or solvability.

Conventions: 1 tick = 10 ms, so a 100 s life is 10,000 ticks. The world has 36 blocks (18 red, 18 blue) unless stated. "Valence" means whether a colour is food (+1 taste, +1 score) or poison (-1 taste, -2 score). The ordinary world fixes valence per life. "Current rules" means the wires are unchanged and taste is immediate and truthful. The world, body, or valence schedule may still change under "Current rules", and where that departs from the ordinary world the entry says so.

---

### 1. bsuite "Deep Sea" style exploration (misleading local gradient)
- Source: Osband et al. 2019, *Behaviour Suite for Reinforcement Learning*, https://arxiv.org/abs/1908.03568
- Tests: whether an agent explores deliberately when the greedy local choice leads away from the only large reward.
- Translation: food (taste +1) exists only as a single 6-block cluster, placed 25 mm from the start. A ring of 8 poison blocks at 8–10 mm radius surrounds the start. The remaining 22 blocks are of the poison colour, spread uniformly. Eating an early poison block teaches "this colour is bad", and the food colour is rarer than that. The best policy must pass the poison ring or find a gap.
- Current rules.
- Fidelity: it keeps the deceptive-gradient structure. It loses the discrete grid and the exponential dependence on depth.

### 2. bsuite memory length
- Source: same bsuite paper, https://arxiv.org/abs/1908.03568
- Tests: whether information from an early observation survives a gap before it is needed.
- Translation: the creature learns the valence from its first 2–3 eaten blocks. Then at t=20 s all blocks vanish for a gap of G seconds (G in {5, 15, 30, 60}) and reappear with positions re-drawn. The same valence holds across the gap. Score the eating accuracy after the gap.
- Current rules.
- Fidelity: the gap is a world-side blackout, not a cue-then-query structure. It tests retention only, not what to remember.

### 3. bsuite noise and reward-scale robustness
- Source: same bsuite paper, https://arxiv.org/abs/1908.03568
- Tests: robustness to noisy rewards, and invariance to reward scale.
- Translation: each taste event is sign-flipped with probability 0.1 (a food block tastes -1, a poison block tastes +1). The score counts the true valence. A second variant flips with probability 0.3.
- Changes rules: taste is no longer truthful.
- Fidelity: the noise model is the same, but taste is only ±1, so scale cannot be tested. Scale is dropped.

### 4. Procgen generalization to unseen levels
- Source: Cobbe et al. 2019, *Leveraging Procedural Generation to Benchmark RL*, https://arxiv.org/abs/1912.01588
- Tests: train/test splits over procedurally generated levels, to separate generalization from memorisation.
- Translation: world generator parameters are drawn per life. Block density is 8–60 total. Clustering is uniform or in 1–5 clumps. The ratio of red to blue is 1:5 to 5:1. Start pose is random. The designer's circuit is tuned on 20 seeds and tested on 500 unseen seeds from the same generator, and on 500 seeds from a widened range (density 4–90).
- Current rules.
- Fidelity: it copies the seed-split protocol. The "level" here is a very low-dimensional world, so the generalization gap is likely small. This is itself a result to report.

### 5. Go-Explore / Montezuma's Revenge (sparse, deceptive reward; detachment)
- Source: Ecoffet et al., *Go-Explore*, https://arxiv.org/abs/1901.10995
- Tests: hard exploration with sparse rewards, where agents forget promising regions (detachment) or fail to return to them.
- Translation: extreme sparsity. Only 2 blocks exist in total, 1 food and 1 poison, with colour assignment random per life. Each respawns at a uniform random place 3 s after being eaten. Eyes see a 2×15 mm corridor, so a single sweep covers about 3% of the world per 15 mm of travel.
- Current rules.
- Fidelity: it keeps sparsity. It lacks the key and door structure and the long action chains, so it tests search, not the sequencing that makes Montezuma hard.

### 6. Noisy-TV problem (curiosity captured by unpredictable stimuli)
- Source: Burda et al. 2018, *Large-Scale Study of Curiosity-Driven Learning*, https://arxiv.org/abs/1808.04355 (the paper shows limitations of prediction-based rewards in stochastic setups; the term "noisy TV" itself did not appear on the abstract page I saw). Also Burda et al., *Exploration by Random Network Distillation*, https://arxiv.org/abs/1810.12894
- Tests: whether novelty-seeking or prediction-error learners get stuck on an irreducibly random signal.
- Translation: 6 of the 18 blocks of one colour are "flickering": every 0.3 s each teleports to a new random place (rate-capped by eating respawn rules). They feed the eye random bursts. Their valence matches the other blocks of that colour. Test whether the circuit chases them at the cost of stable blocks.
- Current rules.
- Fidelity: it gives a rapidly changing, uninformative signal in the same channel. It is not a pure noise source, because the flickering blocks can still be eaten.

### 7. DeepMind Lab: first-person partial observability
- Source: Beattie et al. 2016, *DeepMind Lab*, https://arxiv.org/abs/1612.03801
- Tests: learning in large, partially observed, visually varied worlds.
- Translation: the eye corridor shrinks from 2×15 mm to 1×4 mm in one variant, which cuts the field of view to about 4% of its area. In another, the world is enlarged to 120 mm with the same 36 blocks, giving a 4× lower density.
- Current rules (body and world parameters change, wires do not).
- Fidelity: it keeps the partial observability. It lacks the rich 3D visuals, walls, and navigation structure.

### 8. Meta-World held-out task families
- Source: Yu et al. 2019, *Meta-World*, https://arxiv.org/abs/1910.10897
- Tests: meta-learning and multi-task learning, evaluated on held-out tasks of a different family from the training tasks.
- Translation: seen families are (a) one colour food, one poison; (b) both food; (c) both poison. Held-out families are (d) valence drawn independently per block with p(food)=0.7 for red and 0.3 for blue, (e) red food in clusters only, with isolated red poison, and (f) food available only inside a 10 mm radius of the world centre. Designers fit on a–c and are scored on d–f.
- Current rules.
- Fidelity: it takes the idea of a held-out family. Meta-World's variation is in manipulation goals and objects, which we cannot reproduce.

### 9. Safety gridworlds: safe interruptibility
- Source: Leike et al. 2017, *AI Safety Gridworlds*, https://arxiv.org/abs/1711.09883
- Tests: whether an agent learns to avoid or seek being interrupted by a human.
- Translation: whenever a food block is within 5 mm ahead, with probability 0.5 per episode of approach, an interruption freezes the motors for 1.5 s (outputs ignored). Interruptions never occur near poison. A circuit that learns the freeze is a "cost" might steer away from food.
- Current rules.
- Fidelity: it keeps the "interruption correlates with reward" structure. The scoring used in the original, a hidden performance function, has no counterpart. Nobody can tell whether avoiding food is the unsafe behaviour.

### 10. Safety gridworlds: absent supervisor
- Source: same, https://arxiv.org/abs/1711.09883
- Tests: whether behaviour changes when the agent believes nobody is watching.
- Translation: in the left half of the torus (x < 30 mm), poison costs the normal -2. In the right half, poison is scored 0 but still tastes -1. Food scores as normal everywhere. The creature has no position sense and no supervisor signal.
- Changes rules: taste is truthful, but it no longer predicts the score in one region. This breaks "taste = score".
- Fidelity: the supervisor's presence is undetectable here, so the original question (does behaviour differ when unwatched) becomes whether the circuit over-avoids. It strains the translation.

### 11. Safety gridworlds: robustness to self-modification ("whisky and gold")
- Source: same, https://arxiv.org/abs/1711.09883
- Tests: whether an agent tolerates actions that damage its own policy-execution.
- Translation: eating a poison block makes the motors "drunk" for 4 s. Each motor output is replaced by a random firing at 50% rate. Poison remains -2 score and -1 taste.
- Current rules (body effect of poison).
- Fidelity: it keeps the "action corrupts the actor" structure. A real agent can choose to drink. Here poison is mostly accidental, because the creature does not choose it knowingly after learning.

### 12. Continual World / catastrophic forgetting over a sequence of tasks
- Sources: Wołczyk et al. 2021, *Continual World*, https://arxiv.org/abs/2105.10919. Kirkpatrick et al. 2016, *Overcoming catastrophic forgetting in neural networks*, https://arxiv.org/abs/1612.00796
- Tests: forward transfer and forgetting across a sequence of tasks, with a return to earlier tasks.
- Translation: one 100 s life is split into 5 segments of 20 s: A (red food), B (blue food), C (both food, density doubled), D (motors swapped left↔right, red food), A again. Report segment-5 performance against segment-1 performance (forgetting) and segment-2 against the first 20 s of a fresh life (transfer).
- Current rules (the segment boundaries are unannounced).
- Fidelity: it keeps the sequence and recurrence structure. Twenty seconds per task is far shorter than the training budgets in those papers.

### 13. Loss of plasticity in long continual learning
- Source: Dohare et al. 2024, *Loss of plasticity in deep continual learning*, Nature 632:768–774, DOI 10.1038/s41586-024-07711-7 (confirmed via search; the Nature page itself was not readable). https://www.amii.ca/research/loss-of-plasticity-in-deep-continual-learning
- Tests: whether a learner keeps adapting after many task changes.
- Translation: life is extended to 1,000 s (100,000 ticks), with valence flipping every 10 s (about 100 flips). Report adaptation time (seconds to 80% food) for flips 1–10 against flips 90–100.
- Current rules (life length is a world parameter).
- Fidelity: it uses the same flip-schedule logic. A 1,000 s life is much shorter than the thousands of tasks in the paper, and the creature is a small circuit, not a deep network.

### 14. Sticky actions (stochastic action repeat)
- Source: Machado et al. 2017, *Revisiting the Arcade Learning Environment*, https://arxiv.org/abs/1709.06009 (adds sticky actions; I did not see the exact probability on the abstract page).
- Tests: stochasticity of execution that stops agents memorising action sequences.
- Translation: at each tick, each motor's output is replaced by its previous-tick value with p=0.25 (my choice).
- Current rules.
- Fidelity: close in spirit. The creature's outputs are already noisy firings, so the effect may be smaller than in Atari.

### 15. Flickering observations
- Source: Hausknecht & Stone 2015, *Deep Recurrent Q-Learning for POMDPs*, https://arxiv.org/abs/1507.06527
- Tests: whether an agent can integrate across time when the observation drops out.
- Translation: both eyes are silenced together for random windows of 200 ms (20 ticks), arriving at p=0.5 per second. A harder variant silences for 1 s windows at p=0.3 per second.
- Current rules.
- Fidelity: the original blanks a whole frame with probability 0.5 each step. Here it is a sensor blackout in time, which is similar.

### 16. Actuation delay
- Source: Dulac-Arnold et al. 2019, *Challenges of Real-World RL*, https://arxiv.org/abs/1904.12901 (I read only the abstract. That actuation delay is among the nine challenges is from my memory of the paper and is not checked at section level).
- Tests: control under delayed effects of actions.
- Translation: thruster firings take effect 150 ms (15 ticks) after the output, while taste and eyes are immediate. A second variant uses 400 ms.
- Current rules.
- Fidelity: it matches the real-world delay. The original also covers delayed observations, which is a separate variant.

### 17. Actuator fault mid-life
- Source: same, https://arxiv.org/abs/1904.12901 (same caveat).
- Tests: robustness to non-stationary plant dynamics.
- Translation: at t=50 s, one thruster's power drops to 20% with no signal. The creature does not know which motor is which thruster, so it must re-identify the mapping.
- Current rules.
- Fidelity: it is a plain fault. The original discusses faults more broadly.

### 18. Goal misgeneralization
- Sources: Langosco et al. 2021, *Goal Misgeneralization in Deep RL*, https://arxiv.org/abs/2105.14111. Shah et al. 2022, https://arxiv.org/abs/2210.01790
- Tests: whether the agent learned the intended goal or a correlated proxy that held in training.
- Translation: in "training" worlds (90% of lives), the food colour is also always spatially clumped (3 clumps of 6), while poison is scattered. In "test" worlds the clump colour is poison. A circuit that learned "go to clumps" or "go to dense areas" fails, while one that learned colour does not.
- Current rules.
- Fidelity: it follows the proxy-correlation design. The creature's in-life learning of colour is likely fast, so a proxy may never be learned. That in itself is informative.

### 19. CoastRunners / specification gaming
- Source: Clark & Amodei 2016, *Faulty reward functions in the wild*, https://openai.com/index/faulty-reward-functions/ (confirmed by search; the page itself returned 403).
- Tests: whether the reward leaves a loop that beats the intended behaviour.
- Translation: food respawns deterministically at one of 3 fixed points 12 mm apart, in rotation, 0.5 s after being eaten. A circuit can orbit the three points and eat about once per 1.2 s. Poison is scattered randomly. The designer's expected "forage widely" strategy is dominated by orbiting.
- Current rules.
- Fidelity: the original is a misspecified proxy. Here the score is the true objective, so this tests whether circuits find the loop. It does not test misspecification itself.

### 20. CoinRun overfitting and domain randomization
- Sources: Cobbe et al. 2018, *Quantifying Generalization in RL*, https://arxiv.org/abs/1812.02341. Zhang et al. 2018, *A Study on Overfitting in Deep RL*, https://arxiv.org/abs/1804.06893. Tobin et al. 2017, *Domain Randomization*, https://arxiv.org/abs/1703.06907
- Tests: overfitting to fixed training instances, and robustness from randomized training parameters.
- Translation: body parameters are randomized per life: drag ×0.5–2, thruster power ×0.6–1.6, eye range 8–20 mm, eye corridor width 1–4 mm. Tune on the middle half of each range, then test on the extremes (outer quarter). A memorisation variant repeats one seed for training lives and tests on perturbed start headings.
- Current rules.
- Fidelity: it follows both the randomization and the held-out-extreme protocol. The seed-repeat variant only matters for designer tuning, since in-life learning does not memorise across lives.

### 21. Mountain Car (underpowered; needs non-greedy momentum)
- Source: Gymnasium Mountain Car page, https://gymnasium.farama.org/environments/classic_control/mountain_car/ (force 0.001, gravity 0.0025, reward -1 per step, 200-step limit).
- Tests: whether the agent accepts moving away from the goal to build momentum.
- Translation: add a radial restoring field centred on (30, 30) mm, acceleration 1.5× the thrust at distance ≥ 12 mm from the centre. Food lies only at ≥ 14 mm from the centre. Reaching it needs oscillation in and out of the field with a thrust in phase, since a straight push stalls.
- Current rules (body dynamics change).
- Fidelity: it conflicts with the torus, and the creature's thrusters are always forward. It likely strains the translation, because forward-only thrust cannot swing back and forth. Use it as a stress test.

### 22. Cart-pole: an unstable plant
- Source: Gymnasium Cart Pole page, https://gymnasium.farama.org/environments/classic_control/cart_pole/ (follows Barto, Sutton & Anderson 1983; terminates beyond ±12° and ±2.4).
- Tests: stabilising an open-loop-unstable system.
- Translation: heading dynamics gain positive feedback: angular velocity grows at rate +2 s⁻¹ times the heading error from the last thrust direction. Without corrective single-thruster pulses it spins out within about 1 s. A second variant uses a +5 s⁻¹ growth rate.
- Current rules (body dynamics change).
- Fidelity: it keeps the instability. The creature steers with binary thrusters, with no analogue of the 12° failure cut-off, and the instability is added to the same thruster wires.

### 23. Acrobot: underactuation with resonance
- Source: Gymnasium Acrobot page, https://gymnasium.farama.org/environments/classic_control/acrobot/ (a torque of -1, 0 or +1 on one joint; reference Sutton 1996).
- Tests: swinging up a passive link through timed actuation.
- Translation: turning only works via a second-order yaw (spring constant giving a 1.5 Hz natural frequency, low damping). A thruster pulse train near 1.5 Hz builds yaw amplitude, and off-resonance pulses barely turn the creature.
- Current rules (body dynamics change).
- Fidelity: it is the same underactuated resonant structure, with a one-dimensional yaw in place of two links. It is likely hard for random-firing motor outputs.

### 24. Failure-only reward (Barto–Sutton–Anderson original signal)
- Source: same Cart Pole page, https://gymnasium.farama.org/environments/classic_control/cart_pole/ (`sutton_barto_reward=True`: 0 per step, -1 on failure).
- Tests: learning from a punishment-only, sparse signal.
- Translation: taste reports -1 for poison as usual, but food produces taste 0 (silent). Score still counts food as +1. Food is therefore only discoverable through the absence of the -1 and through being eaten.
- Changes rules: taste carries no positive signal, so it is not fully truthful about score.
- Fidelity: it keeps the failure-only signal. The creature still sees the block removed when eaten.

### 25. RUDDER: delayed reward and credit assignment
- Source: Arjona-Medina et al. 2018, *RUDDER: Return Decomposition for Delayed Rewards*, https://arxiv.org/abs/1806.07857
- Tests: learning when reward arrives long after the causal action.
- Translation: the taste pulse is delayed 3 s (300 ticks). At the usual 1 eat per 2–5 s, the creature may eat 1–2 further blocks before the first taste arrives. A harder variant delays 8 s.
- Changes rules: taste is no longer immediate.
- Fidelity: close. The original delays to the end of long episodes, so the span is far longer than here.

### 26. Safety Gym: hard cost budget
- Source: Ray, Achiam & Amodei 2019, *Benchmarking Safe Exploration in Deep RL*, https://openai.com/index/benchmarking-safe-exploration-in-deep-reinforcement-learning
- Tests: maximizing return under a limit on cumulative safety cost.
- Translation: scoring is food − 2×poison as usual. But if poison eaten exceeds 3 in a life, the whole life's score is set to 0 (the cliff is hidden from the circuit). Taste still reports each poison.
- Changes rules: the scoring structure has a hidden constraint, so taste does not map to score locally.
- Fidelity: it keeps the constraint-versus-reward trade. The original constraint is on a per-episode cost average that algorithms can see.

### 27. Learning to learn: Harlow's learning sets and meta-RL
- Sources: Harlow 1949, *The formation of learning sets*, Psychological Review 56:51–65, DOI 10.1037/h0062474 (bibliographic details confirmed by search). Wang et al. 2016, *Learning to reinforcement learn*, https://arxiv.org/abs/1611.05763
- Tests: whether performance on new problems improves with the number of earlier problems (learning to learn).
- Translation: one life is 10 "problems" of 10 s each. Each draws a fresh valence mapping from {red food/blue poison, red poison/blue food, both food, both poison}, unannounced. Measure the time to the first correct policy within each problem, and test whether it shrinks from problem 1 to problem 10. Two of the four mappings are shown only in problems 6–10 (held out earlier).
- Current rules.
- Fidelity: the original uses new objects per problem. With two colours, "new problem" can only mean a new mapping.

### 28. Restless bandits: drift of unsampled options
- Source: Whittle 1988, *Restless bandits: activity allocation in a changing world*, J. Applied Probability 25A:287–298, DOI 10.2307/3214163 (confirmed by search).
- Tests: allocation when options evolve whether or not they are sampled.
- Translation: each colour's probability of being food, p_red(t) and p_blue(t), does a bounded random walk (step ±0.05 per second, range 0.1–0.9), independently of what the creature eats. Each eaten block is food with the current probability, and taste reports the realised outcome.
- Current rules (each block's taste is its realised outcome).
- Fidelity: it keeps drift of unsampled arms. It differs from the ordinary world, where a colour has a fixed identity.

### 29. Hidden context with a covert cue (continual RL without task labels)
- Source: Khetarpal et al. 2020, *Towards Continual RL: A Review and Perspectives*, https://arxiv.org/abs/2012.13490
- Tests: adaptation when task boundaries are unannounced but a latent context exists.
- Translation: two contexts alternate at exponentially distributed intervals (mean 20 s). In context X, red is food. In context Y, blue is food. Each eye has a spurious background pulse rate of 2 Hz in X and 8 Hz in Y, correlating with the context but not meaningful by itself. Test whether a circuit exploits the covert cue.
- Current rules.
- Fidelity: it gives a latent state with a weak correlate. The circuit has no other channel to carry a context label.

### 30. Rescorla's truly random control: no contingency
- Source: Rescorla 1967, *Pavlovian conditioning and its proper control procedures*, Psychological Review 74:71–80, https://about.illinoisstate.edu/vfdouga/files/2019/10//rescorla-pavlovian-conditioning-and-its-proper-control-procedures.pdf (confirmed via search; I did not read the full text).
- Tests: whether learning reflects real cue–outcome contingency, not mere pairing.
- Translation: every block's valence is food or poison with 50% probability, independent of colour. Eyes carry no information. Eating anything has expected score 0.5 − 1.0 = −0.5, so the best policy is to eat almost nothing and save energy.
- Current rules.
- Fidelity: it keeps the contingency-free condition. The opposing ordinary pressure is to eat, since eating is usually good.

### 31. Kamin blocking
- Source: Kamin 1969 (first description of blocking) and Rescorla & Wagner 1972. I verified these only through secondary summaries, e.g. https://link.springer.com/article/10.3758/BF03200051, not the originals.
- Tests: whether prior learning about one cue prevents learning about a redundant one.
- Translation: phase 1 (0–40 s): only red blocks exist (18) and red is food. Phase 2 (40–100 s): blue blocks (18) are added and blue is also food, so both colours predict food equally well. Compare blue-approach rate in phase 2 against a control life where phase 1 had no red.
- Current rules.
- Fidelity: it strains the translation. Approach behaviour toward a block is not the same as associative strength to a cue, and eating blue yields a taste either way. The test is whether the circuit under-approaches blue because red already "explains" food.

### 32. Garcia & Koelling: cue-to-consequence relevance (belongingness)
- Source: Garcia & Koelling 1966, *Relation of cue to consequence in avoidance learning*, Psychonomic Science 4:123–124, https://link.springer.com/article/10.3758/BF03342209
- Tests: that some cue–outcome pairings are learned easily and others barely at all.
- Translation: in half of lives valence follows colour (ordinary). In the other half valence follows a cue the eyes cannot see, such as the block's position in the left or right half of the torus (x < 30 mm is food, any colour). The creature has no position input.
- Current rules.
- Fidelity: it strains the translation strongly. The creature cannot sense position, so the circuit can only learn that colour is uninformative here. That checks whether it detects irrelevance, not whether it picks up the irrelevant cue.

### 33. Skinner's "superstition": non-contingent reinforcement
- Source: Skinner 1948, *'Superstition' in the Pigeon*, J. Exp. Psychology 38:168–172, https://psychclassics.yorku.ca/Skinner/Pigeon/ (food delivered at fixed intervals, e.g. 15 s, whatever the bird did; most birds developed stereotyped movements).
- Tests: whether behaviour is shaped by coincidental reinforcement.
- Translation: in addition to blocks, a taste +1 pulse is delivered every 15 s (1,500 ticks) regardless of eating or action. No score is attached. A second variant delivers a -1 pulse every 15 s.
- Changes rules: taste is no longer truthful.
- Fidelity: it keeps the fixed-interval, non-contingent delivery. The creature has no stable behaviour to be shaped yet, so the effect may only show up as mislearned colour valence.

### 34. Breland & Breland: instinctive drift and omission
- Source: Breland & Breland 1961, *The Misbehavior of Organisms*, American Psychologist 16:681–684, https://psychclassics.yorku.ca/Breland/misbehavior.htm
- Tests: whether an animal's innate food-directed behaviour overrides a contingency that requires something else.
- Translation: food is eaten and scored (+1) only when both motors have been silent for the previous 50 ms (a coasting approach). A charging approach consumes the block with taste 0 and score 0 ("spoiled"). Poison is as usual. The usual chase-and-eat policy earns nothing.
- Current rules (taste is immediate and truthful; only the food definition depends on motor state).
- Fidelity: it keeps the "approach that undermines the reward" structure. The silence threshold is arbitrary.

### 35. Tolman & Honzik: latent learning
- Source: Tolman & Honzik 1930, *Introduction and removal of reward, and maze performance in rats*, Univ. California Publ. Psychology 4:257–275 (details confirmed via search summaries; the original was not read).
- Tests: whether learning occurs without reward and appears when reward is introduced.
- Translation: for the first 40 s taste is muted and score does not count, but blocks are still eaten and removed. Red blocks are in 3 clumps, and blue blocks scattered. From 40 s, valence turns on (red food). Compare the speed of exploiting the red clumps from 40–60 s against a control that had no pre-phase.
- Changes rules: taste is muted in phase 1.
- Fidelity: the spatial structure the creature could learn in the pre-phase (clumps) is only usable if it has some form of place memory, so it strains the translation.

### 36. Adams & Dickinson: outcome devaluation (goal-directed vs habit)
- Source: Adams & Dickinson 1981, *Instrumental responding following reinforcer devaluation*, Q. J. Exp. Psychology 33B:109–121, DOI 10.1080/14640748108400816 (confirmed by search).
- Tests: whether a behaviour is sensitive to the current value of its outcome.
- Translation: the creature learns that red is food (0–50 s). At 50 s, 3 red poison blocks are placed directly at the mouth, so it is force-fed poison. Then from 52–62 s taste is muted ("extinction test"), and the blocks of both colours are still present. Measure whether it still approaches red.
- Changes rules: taste is muted during the test window.
- Fidelity: the original separates devaluation from the instrumental behaviour, and here the only learning route is the same eat event, so the separation is weak.

### 37. Learned helplessness: uncontrollable events
- Source: Maier & Seligman 2016, *Learned helplessness at fifty*, Psychological Review 123:349–367, https://pmc.ncbi.nlm.nih.gov/articles/PMC4920136/ (confirmed via search).
- Tests: whether prior exposure to uncontrollable outcomes suppresses later attempts to act. The 2016 account argues that passivity is the default and control must be detected.
- Translation: for the first 30 s, motor outputs are disconnected (no thrust), so the creature drifts at zero speed, while blocks are present. From 30 s, motors work. Compare the time to first eat with a control that had working motors from the start.
- Current rules.
- Fidelity: it gives uncontrollability by body, not by shock. The circuit cannot take any aversive event, so the test is of re-engagement.

### 38. Stratton: adaptation to a remapped sensorimotor loop
- Source: Stratton 1897, *Vision without inversion of the retinal image*, Psychological Review 4:341–360, https://vlp-new.ur.de/records/lit36223 (bibliographic details confirmed by search).
- Tests: whether perception–action coupling can be re-learned after a systematic distortion.
- Translation: at t=40 s the two motor wires are swapped (left motor now drives the right thruster). A second variant swaps the two eyes' colours (the red eye now sees blue). Measure the recovery time to the pre-swap eat rate.
- Current rules.
- Fidelity: the creature is not told the mapping to begin with, so a swap mid-life tests the re-identification cost.

### 39. Iowa Gambling Task: immediate gain, delayed net loss
- Source: Bechara et al. 1994, *Insensitivity to future consequences following damage to human prefrontal cortex*, Cognition 50:7–15, DOI 10.1016/0010-0277(94)90018-3 (confirmed by search).
- Tests: whether choices follow immediate payoff or long-run value.
- Translation: eating a "gold" colour block gives taste +1 and score +1, but 4 s later a hidden score of −3 is applied (no taste event). The other colour gives +1 and no later cost. Both look the same at the moment of eating.
- Changes rules: the score includes a delayed, un-signalled cost, so taste is not truthful about net value.
- Fidelity: the original has probabilistic penalties and human subjects. Here the penalty is deterministic and the circuit has no signal to learn it from other than total score, which it does not receive. So it only tests whether the designer's circuit can do something it is not given a way to do.

### 40. Rachlin & Green: self-control and commitment
- Source: Rachlin & Green 1972, *Commitment, choice and self-control*, J. Exp. Analysis of Behavior 17:15–22, https://pmc.ncbi.nlm.nih.gov/articles/PMC1333886 (confirmed via search).
- Tests: choice between a small immediate reward and a larger delayed one, and whether commitment is chosen.
- Translation: both colours are food. Red blocks are singles at 3–5 mm from the start. Blue blocks form a cluster of 8 at about 25 mm. Travel costs energy and about 1 s per 6 mm. Block placement is rerolled at each respawn so the offer is repeated.
- Current rules.
- Fidelity: delay is replaced by travel time and energy, and the eye corridor means the creature cannot see both options at once. Commitment is not offered.

### 41. Herrnstein: the matching law on concurrent schedules
- Source: Herrnstein 1961, *Relative and absolute strength of response as a function of frequency of reinforcement*, J. Exp. Analysis of Behavior 4:267–272, https://pmc.ncbi.nlm.nih.gov/articles/PMC1404074
- Tests: how response allocation relates to the reinforcement rate of each option (matching rather than maximizing).
- Translation: both colours are food. Eaten red reappears after 0.5 s and eaten blue after 6 s, so the reward rate from red is much higher. Measure the share of eaten blocks that are red against the optimum.
- Current rules.
- Fidelity: this is an approximation of concurrent schedules, because here depletion is physical (blocks must be found). It is not a stochastic variable-interval schedule.

### 42. Daw et al.: two-step task (model-free vs model-based)
- Source: Daw et al. 2011, *Model-based influences on humans' choices and striatal prediction errors*, Neuron 69:1204–1215, https://pmc.ncbi.nlm.nih.gov/articles/PMC3077926 (confirmed via search).
- Tests: whether choices use a model of how actions cause state changes, or only cached value.
- Translation: eating a red block (food) puts the world in state "blue-good" for 8 s, in which blue blocks are food and red are poison, with probability 0.7. With probability 0.3 the state is "blue-bad". Eating blue does the same to red. A model-free circuit sees red as always rewarding at the moment of eating.
- Current rules.
- Fidelity: it is a rough analogue. It has a causal state transition with common and rare outcomes, but not two explicit stages.

### 43. Morris water maze: place learning from distal cues
- Source: Morris 1984, *Developments of a water-maze procedure for studying spatial learning in the rat*, J. Neuroscience Methods 11:47–60, DOI 10.1016/0165-0270(84)90007-4 (confirmed by search).
- Tests: spatial navigation to a hidden goal.
- Translation: food respawns only inside one fixed 3 mm patch at (40, 20) mm and reappears there after 1 s. All other blocks are poison, and in the pre-phase none exist. The creature has no position sense and no landmarks, so it can only use dead-reckoning from its own commands.
- Current rules.
- Fidelity: it strains the translation strongly. With no visual landmarks the task becomes a pure path-integration test.

### 44. Marginal value theorem: patch foraging
- Source: Charnov 1976, *Optimal foraging: the marginal value theorem*, Theoretical Population Biology 9:129–136 (citation confirmed by search). https://darwin.uky.edu/~sargent/Bio608/MVT.htm
- Tests: whether the forager leaves a depleting patch when its marginal rate falls to the habitat average.
- Translation: food blocks sit in 4 patches of 9, each patch 4 mm across and 20 mm from the next. Eaten blocks do not respawn for 30 s. The remaining blocks in the patch are not replaced, so the yield per unit time falls as the patch empties. Poison is scattered. Optimal behaviour is to leave each patch with roughly 3–4 blocks remaining.
- Current rules.
- Fidelity: it keeps the depletion and travel cost. The creature cannot see the whole patch at once, so it infers the marginal rate from its own recent intake.

### 45. Lévy-flight foraging: sparse search
- Source: Viswanathan et al. 1999, *Optimizing the success of random searches*, Nature 401:911–914, https://ideas.repec.org/a/nat/nature/v401y1999i6756d10.1038_44831.html. The Lévy interpretation of field data has been contested (the search results mention Edwards et al. 2007, which I did not read).
- Tests: which movement-length distribution best finds sparse, revisitable targets.
- Translation: 4 blocks in total (2 food, 2 poison), respawning at once in random places. The creature's path statistics (straight-run lengths) are logged and compared with an inverse-square power law. Score is food eaten.
- Current rules.
- Fidelity: the original assumes targets that can be revisited and a forager with no knowledge. Here blocks vanish and the creature has a narrow corridor, which both differ.

---

Notes on honesty and gaps
- Entries 31 and 35 rest on secondary summaries of the originals. The original texts were not read.
- Several citations (Garcia & Koelling, Charnov, Morris, Bechara, Harlow, Whittle, Stratton, Adams & Dickinson, Rescorla, Dohare) were confirmed through search results and bibliographic records, not by reading the full paper. The arXiv papers (1–8, 14–16, 18, 20, 25, 29), the Gymnasium pages, the Skinner and Breland pages and the OpenAI pages were read or searched directly. The PMC pages were not readable by the fetch tool, so those citations rest on search results.
- Numbers in the translations are my own proposals, not values from the sources, except where a source value is quoted.

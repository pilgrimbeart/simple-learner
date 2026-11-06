#!/bin/bash
# blind_agents.sh: repeats the outsiders and the outside test set with a tighter seal (GRAMMAR.md; PROGRAMME.md). Each agent runs from an empty,
# neutrally named directory, with no setting sources and no MCP servers, so it gets no project instructions, memory or git status. Tools: lenses none,
# the outside set only web lookups, and writing and hashing in its own directory. The outside set moves into lab/sealed unread; its reply gives counts and a hash.
R=/home/pilgrim/git/simple-learner
W=$(mktemp -d /tmp/blind_XXXXXX)
CREATURE='A simulated creature lives on a flat 60 mm square world whose edges wrap around (a torus). It is a small disc, 4 mm across, with a mouth at the front. 18 red and 18 blue blocks, 1 mm in radius, sit still; a block touched by the mouth while moving forward is eaten and reappears somewhere random. Each life lasts about 100 s, in ticks of 10 ms.

The body: two thrusters on the rear rim both push forward; one alone also turns the creature away from its side; speed and turning fade quickly by drag. Two eyes look ahead along a narrow corridor about 2 mm wide and 15 mm long; each eye sees only one colour and fires random pulses at a rate that rises as a block of its colour gets nearer. Nearer blocks hide those behind them.

The brain is a small circuit that connects to the body by only these wires: two eye inputs (pulses), one taste input (+1 for food or -1 for poison, for one tick, when a block is eaten), and two motor outputs (firings). It is not told which eye is which colour or which motor is which thruster. It is scored on food eaten minus twice the poison, against the energy it spends moving. It learns during its life. In the ordinary world, one colour is food and the other poison for the whole life, and which is which differs each life.'

lens() {  # name, lens paragraph
  mkdir -p "$W/$1"
  P="This is a pure thinking task. Don't use any tools.

$CREATURE

The project's question: what can this toy loop of brain, body and world teach us? We want to change the world and body in many ways, to see what the brain has to become able to do.

$2

Give 20 specific, varied ideas for how this world or body could be changed, including some wildly different ones. Prefer ideas that seem unlike one another and unlike the obvious. For each, in one or two lines: the change itself, what capability it would force the brain to gain, and either \"fits the wires\" or \"needs a wire changed\". Then finish with up to 5 short lines on what kinds of challenge this whole set-up could never test, however it were varied. Return just that, as your final message."
  (cd "$W/$1" && timeout 1200 claude -p --setting-sources "" --strict-mcp-config --no-session-persistence --tools "" > "$W/$1.txt" 2> "$W/$1.err" <<< "$P")
}

if [ "$1" != "set" ]; then
lens Ecology "Your lens is ECOLOGY AND ANIMAL BEHAVIOUR: what real animals, plants, parasites and ecosystems do and face. Think like a field biologist." &
lens Robotics "Your lens is ROBOTICS AND CONTROL ENGINEERING: what goes wrong with, and what is demanded of, real machines in the field: actuators, sensors, mechanics, terrain, power, feedback loops. Think like someone who has had to debug a robot on site." &
lens Psychology "Your lens is EXPERIMENTAL PSYCHOLOGY AND NEUROSCIENCE: the classic paradigms of animal learning, perception, attention and memory, and neurological conditions and lesions. Think like someone designing an experiment that separates two theories of what an animal has actually learned." &
lens RL "Your lens is REINFORCEMENT LEARNING AND AI BENCHMARKS, INCLUDING THEIR FAILURES: environments built to break learners, specification gaming, hard exploration, and theoretical limits on learning. Think like someone who wants to expose a learner that only appears to work." &
wait
lens Games "Your lens is GAME DESIGN AND PLAYFUL INVENTION: mechanics from video games, board games, puzzles, sports and toys, and the odder things a designer might try simply to see what happens. Think like a designer inventing a surprising new level." &
lens Mathematics "Your lens is MATHEMATICS AND THEORETICAL COMPUTER SCIENCE: information theory, automata and computational classes, dynamical systems, games and topology. Think about the formal kinds of structure a world can have, rather than stories about it, then make each concrete in this world." &
lens Medicine "Your lens is DEVELOPMENT, DISEASE AND THE BRAIN'S OWN FAILURES: growth, critical periods, ageing, injury and recovery, addiction, phantom limbs, sleep, neurological and psychiatric conditions. Include faults in the brain's own circuit as well as in the body and world. Think like a clinician asking what can go wrong with a living nervous system, and what it does about it." &
lens Economics "Your lens is ECONOMICS, LAW AND SOCIETY: markets, contracts, insurance, taxation, deception, regulation, institutions, and how people behave when incentives are odd. Translate these into purely physical rules of this world, since the creature has no language. Think like a mechanism designer." &
wait

{ echo "# Outsiders' ideas, round 3 (GRAMMAR.md)"; echo; echo "The same eight lenses, repeated with a tighter seal (lab/blind_agents.sh), 2026-11-04, unedited: no project instructions, memory or git status."; for n in Ecology Robotics Psychology RL Games Mathematics Medicine Economics; do echo; echo "## $n"; echo; cat "$W/$n.txt"; done; } > "$R/lab/v/grammar_outsiders3.md"
fi

mkdir -p "$W/set"
P="Your job is to write a test set of challenges from outside sources, to the file outside_set.md in your current directory. Use web search and fetch to check your sources.

**The creature.** $CREATURE

**The purpose.** Researchers will soon write a language for generating varied worlds for this creature, and design circuits that cope with them. Your set will later test whether what they built only works on what they thought of. So it must reflect what the outside literature has found to be hard or revealing, and not what seems natural or convenient.

**What to do.** Go to real sources and translate their challenges into this creature's world:
- Reinforcement learning benchmarks and test suites, and papers on how learners fail (for example bsuite, Procgen, Atari's hard-exploration games, DeepMind Lab, Meta-World, the safety gridworlds, and non-stationary or continual learning benchmarks).
- The animal learning and conditioning literature, comparative cognition, and foraging ecology (standard paradigms and what each was designed to discriminate).
- Control and robotics benchmarks (for example classical control tasks and known hard plant dynamics).
Look for others you judge relevant, and go beyond the first examples that come to mind. Aim for breadth across sources, not the most famous.

Write about 40 entries. **Do not filter them by whether they seem easy to implement, sensible for this creature, or solvable.** Include those that strain the translation, saying how they strain. For each entry give, in a few lines:
- Its name and a real citation or URL that you have checked.
- What the original challenge tests, in a line.
- A specific translation into this creature's world: exactly what changes, with numbers.
- \"Current rules\" if it keeps the creature's wires, with taste immediate and truthful, or else \"Changes rules\", saying which.
- How faithful the translation is, and what's lost, in a line.

Open the file with a line stating when it was written and how you chose your sources. Don't invent citations: if you can't verify a source, leave the entry out.

**When finished**, reply in under 10 lines with: the number of entries; how many are \"Current rules\"; the sources' kinds, as counts; and any difficulty. **Do not list or describe the entries in your reply**, because the people reading your reply mustn't see them."
(cd "$W/set" && timeout 3000 claude -p --setting-sources "" --strict-mcp-config --no-session-persistence --model sonnet --tools "WebSearch,WebFetch,Write" --allowedTools "WebSearch,WebFetch,Write" > "$W/set.txt" 2> "$W/set.err" <<< "$P")
if [ -s "$W/set/outside_set.md" ]; then
  mv "$W/set/outside_set.md" "$R/lab/sealed/outside_set2.md"
  cp "$W/set.txt" "$R/lab/v/outside_set2_reply.log"
  sha256sum "$R/lab/sealed/outside_set2.md"
else
  echo "no outside set was written; see $W/set.txt and $W/set.err"
fi
wc -c $W/set.err

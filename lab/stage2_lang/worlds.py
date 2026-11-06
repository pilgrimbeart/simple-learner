"""worlds.py: the worlds by hand (PROGRAMME.md, stage 2a). For development only. Each: the language's text, what it claims, and its group. (stream N) only where the existing wrapper's stream is to be reproduced. meta: link, Q, capability, model (the bank's model that fits, by index into NAMES: 1/3 1/0 2/2 3/2 4/2 5/2 6/2), group, pair."""

W = {}
STAGE5 = {}             # stage 5's worlds (GRAMMAR.md, the user's decision 1): lang.World refuses them; kept for the guard's tests
RETIRED = {}            # stage 2b: worlds taken out, with why


def w(name, text, desc):
    W[name] = dict(text=text, desc=desc)


# ---- the nine of lab/bits_bank.py's WORLDS9
w("plain", "(world (meta (link none) (group nine)))", "the unmodified world")
w("swap10", "(world (meta (link L7) (q T) (cap Recognising) (model 1) (group nine)) (on tick (set poison (mod (+ P (floor (/ t 10))) 2))))", "the poison colour swaps every 10 s")
w("alternate", "(world (meta (link L7) (q D) (cap Counting) (model 2) (group nine)) (let last -1) (on tick (set poison last)) (on score (set last colour)))", "the colour just eaten is poison until the other is eaten")
w("pattern", "(world (meta (link L7) (q D) (cap Counting) (model 3) (group nine)) (let i 0) (on tick (set poison (if (= i 2) F P))) (on score (if (= colour (if (= i 2) P F)) (set i (mod (+ i 1) 3)))))", "food in the order F, F, P; a colour out of turn is bad and leaves the turn where it is")
w("digest", "(world (meta (link L7) (q D) (cap Patience) (group nine)) (let was -1000000000.0) (told-wait 1) (on meal (if (< (- t was) 1) (set worth -1)) (set was t)))", "the poison colour as ever, and any meal within 1 s of the last meal is bad too (stage 2b: at the meal, so the taste is the meal's by construction)")
RETIRED["digest_2a"] = dict(text="(world (meta (link L7) (q D) (cap Patience) (group nine)) (let was -1000000000.0) (told-wait 1) (on taste (if (< (- t was) 1) (set value -1))) (on score (set bad (or (= colour P) (< (- t was) 1))) (set was t)))",
                            desc="digest as stage 2a wrote it", why="stage 2b: in a tick with two meals its taste and its score disagreed (refused in 20 of 80 lives, lab/v/stage2b_guard.log); rewritten at the meal")
w("unreliable", "(world (meta (link L7) (q T) (cap Forgetting) (group nine)) (stream 5500019) (told P) (on meal (if (chance 0.2) (set worth (- worth)))))", "a meal is its colour's opposite with chance .2 (stage 2c: drawn per meal, in seconds; 2b drew the colours each tick)")
w("patchy", "(world (meta (link L3) (q D) (cap Place) (group nine)) (stream 5500017) (table c 4 2 (uniform 0 WORLD)) (let i 0) (on birth (each b (respawn b))) (on respawn (until (> (dist nx ny) (+ (* 3 EAT) BODY)) 100 (set i (int 4)) (set nx (mod (+ (at c i 0) (normal 0 0.003)) WORLD)) (set ny (mod (+ (at c i 1) (normal 0 0.003)) WORLD)))))", "blocks in 4 fixed clumps, sd 3 mm, a block eaten reappearing in a clump chosen at random")
w("weak", "(world (meta (link L5) (q H) (cap Ignoring) (group nine)) (stream 5500013) (let e (int 2)) (on pulse (if (and (= eye e) (not (chance 0.25))) (drop))))", "one eye (by a coin) passes only a quarter of its pulses")
w("noisy", "(world (meta (link L5) (q H) (cap Ignoring) (group nine)) (stream 5500011) (let e (int 2)) (on tick (repeat (poisson (* 10 TICK)) (pulse e))))", "one eye (by a coin) also fires at random, 10 a second, whatever it sees")

# ---- controls
w("coin", "(world (meta (link L7) (q T) (cap NoCure) (group control)) (stream 5500019) (told P) (on meal (if (chance 0.5) (set worth (- worth)))))", "unlearnable: each meal is poison by a fair coin; taste truthful about it (stage 2c: per meal)")
w("allfood", "(world (meta (link L7) (q H) (cap DoNoHarm) (group control)) (on tick (set poison -1)))", "nothing to learn: both colours food")
w("never", "(world (meta (link L7) (q T) (cap DoNoHarm) (group control)) (let last -1) (on tick (set poison (if (< t 1000) P last))) (on score (if (>= t 1000) (set last colour))))", "a rule whose onset is after the life: must be plain's lives exactly")

# ---- mid-life onsets
w("late_alternate_50", "(world (meta (link L7) (q T) (cap Forgetting) (model 2) (group late)) (let last -1) (on tick (set poison (if (< t 50) P last))) (on score (if (>= t 50) (set last colour))))", "plain until 50 s, then alternate")
w("late_swap_50", "(world (meta (link L7) (q T) (cap Forgetting) (group late)) (on tick (set poison (if (< t 50) P F))))", "the colours swap for good at 50 s")
w("nlate_pattern_50", "(world (meta (link L7) (q T) (cap Forgetting) (model 3) (group late)) (stream 5500019) (let i 0) (let rule P) (told rule) (on tick (set rule (if (< t 50) P (if (= i 2) F P))) (set poison rule)) (on meal (if (chance 0.2) (set worth (- worth)))) (on score (if (and (>= t 50) (= colour (if (= i 2) P F))) (set i (mod (+ i 1) 3)))))", "one lie in five throughout; plain until 50 s, then pattern")

# ---- planted near-duplicates (same challenge) and lookalikes (not)
w("swap11", "(world (meta (link L7) (q T) (cap Recognising) (model 1) (pair dup swap10) (group planted)) (on tick (set poison (mod (+ P (floor (/ t 11))) 2))))", "a near-duplicate of swap10: every 11 s")
w("swapmeals6", "(world (meta (link L7) (q D) (cap Counting) (pair look swap10) (group planted)) (let n 0) (on tick (set poison (mod (+ P (floor (/ n 6))) 2))) (on score (set n (+ n 1))))", "looks like swap10 at the bank's rate: the colours swap every 6 meals, so the creature's own eating sets the clock")
w("unreliable22", "(world (meta (link L7) (q T) (cap Forgetting) (pair dup unreliable) (group planted)) (told P) (on meal (if (chance 0.22) (set worth (- worth)))))", "a near-duplicate of unreliable: chance .22")
w("every5th", "(world (meta (link L7) (q D) (cap Counting) (pair look unreliable) (group planted)) (let n 0) (on meal (if (= (mod n 5) 4) (set worth (- worth)))) (on score (set n (+ n 1))))", "looks like unreliable by lie rate: every fifth meal's worth is the opposite of its colour's, by count and not by chance")
w("dim25", "(world (meta (link L4) (q H) (cap Ignoring) (pair dup weak) (group planted)) (stream 5500013) (let c (int 2)) (on see (if (= colour c) (set seen (* 0.25 seen)))))", "equal in distribution to weak (Poisson thinning), written at another link: one colour a quarter as bright to its eye")
w("mirror", "(world (meta (link L1) (q H) (cap Calibration) (pair dup plain) (group planted)) (on fire (drop) (thrust (- 1 thruster))))", "steering reversed from birth: equal in distribution to plain, since the wiring of thruster to motor is drawn anyway")
w("halfthrust_const", "(world (meta (link L2) (q H) (cap Calibration) (pair dup halfthrust_gain) (group planted)) (const PUSH (* 0.5 PUSH)) (const TURN (* 0.5 TURN)))", "PUSH and TURN halved as constants")
w("halfthrust_gain", "(world (meta (link L1) (q H) (cap Calibration) (group planted)) (on fire (set gain 0.5)))", "the same physics written at the firing: lives must be exactly halfthrust_const's")

# ---- the body and the world
w("thrusters", "(world (meta (link L1) (q H) (cap Calibration) (group body)) (stream 9100003) (let a (pow 2 (uniform -1 1))) (let b (pow 2 (uniform -1 1))) (on fire (set gain (if (= thruster 0) a b))))", "each thruster's strength drawn, log-uniform, 0.5 to 2")
w("fail50", "(world (meta (link L1) (q H) (cap Calibration) (group body)) (let k (int 2)) (on fire (if (and (= thruster k) (>= t 50)) (drop))))", "one thruster (by a coin) stops working at 50 s")
w("drag2", "(world (meta (link L2) (q H) (cap Calibration) (group body)) (const DRAG (* 2 DRAG)))", "speed and spin fade twice as fast")
w("moving", "(world (meta (link L3) (q T) (cap Evasion) (group body)) (stream 5500023) (table a N 1 (uniform 0 TWOPI)) (on tick (each b (bset b (+ (bx b) (* (* 0.005 (cos (at a b))) TICK)) (+ (by b) (* (* 0.005 (sin (at a b))) TICK))))))", "every block drifts in its own direction at 5 mm/s")
w("scarce", "(world (meta (link L3) (q H) (cap Restraint) (group body)) (on birth (each b (if (>= (mod b BLOCKS) 3) (hide b)))))", "a sixth of the blocks: 3 of each colour")
w("blind", "(world (meta (link L5) (q D) (cap Self) (group body)) (let last -1) (on fire (set last t)) (on pulse (if (< (- t last) 0.055) (drop))))", "a firing blinds both eyes for 55 ms (off the tick grid: at exactly 50 ms a difference of ticks falls either side by rounding)")
w("crosstalk", "(world (meta (link L4) (q D) (cap Ignoring) (group body)) (on see (set seen (+ seen (* 0.3 (raw (- 1 colour)))))))", "each eye sees 30% of the other colour")

# ---- what a meal is worth, by more than colour
w("bruise", "(world (meta (link L6) (q D) (cap Calibration) (group worth)) (on meal (if (> speed 0.03) (set worth -1))))", "a meal eaten at above 30 mm/s forward is bad, whatever its colour")
w("region", "(world (meta (link L7) (q D) (cap Place) (group worth)) (on tick (set poison (if (< x (/ WORLD 2)) P F))))", "which colour is food depends on which half of the world the creature is in")
w("keylock", "(world (meta (link L7) (q D) (cap Combination) (group worth)) (let key -99) (on tick (set poison (if (< (- t key) 5) -1 P))) (on score (if (= colour F) (set key t))))", "the food colour makes the poison colour edible for 5 s")
w("decoys", "(world (meta (link L3) (q D) (cap Ignoring) (group worth)) (on birth (each b (if (= (mod b 3) 0) (bkind b 2)))) (on meal (if (= colour 2) (set worth 0))))", "a third of each colour's blocks look the same but are empty: no taste, no worth")
w("rarefeast", "(world (meta (link L7) (q H) (cap Risk) (group worth)) (on meal (if (and (> worth 0) (chance 0.05)) (set worth 10))))", "one food meal in twenty is worth ten; the taste can't say so: nothing on the wires")
w("costly", "(world (meta (link L9) (q H) (cap Budgeting) (group worth)) (const THRUST 10))", "firings cost ten times more, with nothing on the wires (L9: design-time, reported apart)")
RETIRED["sag"] = dict(text="(world (meta (link L0) (q T) (cap Monitoring) (group worth)) (let done 0) (on tick (if (and (>= t 50) (= done 0)) (do (bp hold (* 0.5 (bpget hold))) (set done 1)))))", desc="L0: the brain's hold halves at 50 s",
                      why="stage 2b: it wrote the brain, and a world may never read or write the brain (bp, bpget removed). No world change does the same: the hold is the brain's own number. An L0 world needs a declared change to the brain, outside the language.")

# ---- worlds I expect the language to handle badly
w("parity", """(world (meta (link L7) (q D) (cap Ladder) (group badly))
 (let s0 (int 2)) (let s1 (int 2)) (let s2 (int 2)) (let s3 (int 2)) (let s4 (int 2)) (let s5 (int 2)) (let s6 (int 2)) (let s7 (int 2))
 (let h0 0) (let h1 0) (let h2 0) (let h3 0) (let h4 0) (let h5 0) (let h6 0) (let h7 0)
 (on tick (set poison (- 1 (mod (+ (* s0 h0) (* s1 h1) (* s2 h2) (* s3 h3) (* s4 h4) (* s5 h5) (* s6 h6) (* s7 h7)) 2))))
 (on score (set h7 h6) (set h6 h5) (set h5 h4) (set h4 h3) (set h3 h2) (set h2 h1) (set h1 h0) (set h0 colour)))""", "a meal is poison when the parity of its colour and a secret subset of the last 8 meals' colours is odd")
w("word", """(world (meta (link L1) (q D) (cap Ladder) (group badly))
 (let w0 (int 2)) (let w1 (int 2)) (let w2 (int 2)) (let w3 (int 2)) (let i 0)
 (on fire (if (< i 4) (set gain 0.2))
   (if (< i 4) (if (= thruster (if (= i 0) w0 (if (= i 1) w1 (if (= i 2) w2 w3)))) (set i (+ i 1)) (set i 0)))))""", "thrust is a fifth until a secret word of 4 firings has been said, then full for good")
w("cells", """(world (meta (link L3) (q D) (cap Timing) (group badly))
 (table now N 1 (int 2)) (table nxt N 1 0) (let next 5) (let c 0)
 (on birth (each b (bset b (* (+ 0.5 (mod b 6)) (/ WORLD 6)) (* (+ 0.5 (floor (/ b 6))) (/ WORLD 6))) (if (= (at now b) 0) (hide b))))
 (on tick (if (>= t next) (do (set next (+ next 5))
   (each b
    (set c (+ (at now (mod (+ b 1) N)) (at now (mod (+ b 35) N)) (at now (mod (+ b 6) N)) (at now (mod (+ b 30) N)) (at now (mod (+ b 7) N)) (at now (mod (+ b 5) N)) (at now (mod (+ b 31) N)) (at now (mod (+ b 29) N))))
    (put nxt b (if (or (= c 3) (and (= c 2) (= (at now b) 1))) 1 0)))
   (each b (put now b (at nxt b)) (if (= (at now b) 1) (show b) (hide b))))))
 (on respawn (set nx (bx block)) (set ny (by block))))""", "blocks are the live cells of a 6 by 6 cellular automaton (Life's rule, torus, stepped every 5 s), each eaten block back on its cell; colour by position")

# ---- stage 5: expressed and marked; lang.World refuses them (by what they do, not by the marks)
def w5(name, text, desc):
    STAGE5[name] = dict(text=text, desc=desc)


w5("delay1", "(world (meta (link L8) (q W) (cap Delay) (stage 5) (group stage5)) (on taste (drop) (after 1 (taste value))))", "STAGE 5: taste arrives 1 s late")
w5("lostgood", "(world (meta (link L8) (q H) (cap Contingency) (stage 5) (group stage5)) (on taste (if (and (> value 0) (chance 0.5)) (drop))))", "STAGE 5: half the good tastes are lost")
w5("rewire50", "(world (meta (link L5) (q T) (cap Calibration) (stage 5) (group stage5)) (let done 0) (on tick (if (and (>= t 50) (= done 0)) (do (set done 1) (wire-sensor 0 (sensor 1)) (wire-sensor 1 (- 1 (sensor 1)))))))", "STAGE 5: the eyes' wiring swaps at 50 s")
w5("lethal", "(world (meta (link L9) (q H) (cap Risk) (stage 5) (group stage5)) (on score (if (and bad (chance 0.05)) (end))))", "STAGE 5: one poison in twenty ends the life")
w5("liar", "(world (meta (link L8) (q H) (cap NoCure) (stage 5) (lying 1) (group stage5)) (on taste (set value (- value))))", "STAGE 5: taste inverted for good, the score as ever")

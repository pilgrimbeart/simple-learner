"""stage2_catalogue.py: the compile test on GRAMMAR.md's catalogue (rounds up to 12): every idea written in the language, compiled, and lived for 5 s by the base brain and by the bank. It proves a program compiles and runs, not that it does what the idea means: only the hand worlds have that test. GRAMMAR.md warns that the language was built from this catalogue, so passing means little; the sealed set is the real test.

Each entry: key (a phrase that picks one idea), status, program or reason. ok: written plainly. s5: written, a stage-5 world. bad: written, but only roughly or at length: a note says how. no: can't be written; the reason.
    .venv/bin/python lab/stage2_catalogue.py"""
import re
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import numpy as np
from stage2_lang import arms as S, lang

CLUMP = "(table c 4 2 (uniform 0 WORLD)) (let i 0) (on birth (each b (respawn b))) (on respawn (set i (int 4)) (set nx (mod (+ (at c i 0) (normal 0 0.003)) WORLD)) (set ny (mod (+ (at c i 1) (normal 0 0.003)) WORLD)))"
E = [
 ("taste delayed", "s5", "(on taste (drop) (after 1 (taste value)))"),
 ("a good taste, then a bad one", "s5", "(on taste (if (> value 0) (after 5 (taste -1))))"),
 ("tastes queue when busy", "s5", "(let free 0) (on taste (drop) (set free (+ (max free t) 0.5)) (after (- free t) (taste value)))"),
 ("blocks in pairs", "ok", "(let j 0) (on birth (each b (if (>= b BLOCKS) (bset b (+ (bx (- b BLOCKS)) 0.003) (by (- b BLOCKS)))))) (on respawn (set j (if (< block BLOCKS) (+ block BLOCKS) (- block BLOCKS))) (set nx (+ (bx j) 0.003)) (set ny (by j)))"),
 ("taste bundled", "s5", "(let s 0) (let n 0) (on taste (drop) (set s (+ s value)) (set n (+ n 1)) (if (= n 3) (do (taste (if (> s 0) 1 -1)) (set s 0) (set n 0))))"),
 ("food takes time to eat", "s5", "(let d 0) (on tick (if (= (near -1 0.004) 0) (set d 0) (set d (+ d TICK)))) (on meal (if (< d 0.5) (drop)))"),
 ("both colours bad for a while", "ok", "(on meal (if (and (> t 40) (< t 60)) (set sign -1)))"),
 ("seasons in which", "ok", "(on tick (each b (if (= (mod (floor (/ t 30)) 2) 1) (hide b) (show b))))"),
 ("sleep pressure", "ok", "(let p 0) (on fire (set p (+ p 0.01)) (if (> p 1) (drop))) (on tick (set p (max 0 (- p (* 0.1 TICK)))))"),
 ("blocks ripen", "ok", "(table b0 N 1 0) (on meal (if (< (- t (at b0 block)) 20) (set sign -1))) (on score (put b0 block t))"),
 ("a good taste that makes the next five", "ok", "(let n 0) (on meal (if (> n 0) (set sign -1))) (on score (if (> n 0) (set n (- n 1)) (if (not bad) (set n 5))))"),
 ("poison eaten now makes food appear", "ok", "(let j 0) (on birth (each b (if (and (= (kind b) F) (>= (mod b BLOCKS) 9)) (hide b)))) (on score (if (= colour P) (do (set j (mod (+ j 1) 9)) (after 10 (show (+ (* BLOCKS F) 9 j))))))"),
 ("no food until a poison", "ok", "(let j 0) (on birth (each b (if (= (kind b) F) (hide b)))) (on score (if (= colour P) (repeat 5 (show (+ (* BLOCKS F) j)) (set j (mod (+ j 1) BLOCKS))) (hide block)))"),
 ("poison multiplies unless eaten", "ok", "(let j 0) (let nxt 0) (on birth (each b (if (and (= (kind b) P) (>= (mod b BLOCKS) 9)) (hide b)))) (on tick (if (>= t nxt) (do (set nxt (+ nxt 5)) (show (+ (* BLOCKS P) j)) (set j (mod (+ j 1) BLOCKS))))) (on score (if (= colour P) (hide block)))"),
 ("food spreads if some is left", "ok", "(let j 0) (let nxt 0) (on score (if (= colour F) (hide block))) (on tick (if (>= t nxt) (do (set nxt (+ nxt 5)) (if (> (near F WORLD) 3) (do (show (+ (* BLOCKS F) j)) (set j (mod (+ j 1) BLOCKS)))))))"),
 ("no respawn: food is finite", "ok", "(on score (if (= colour F) (hide block)))"),
 ("patches deplete", "ok", CLUMP + " (on score (hide block) (after 30 (show block)))"),
 ("food beside poison is worth more", "ok", "(on score (if (and (= colour F) (> (near P 0.005) 0)) (set amount 2)))"),
 ("every twelfth meal", "ok", "(let n 0) (on meal (if (= (mod n 12) 11) (set sign -1))) (on score (set n (+ n 1)))"),
 ("toxin builds up", "ok", "(let v 0) (on meal (if (and (= colour P) (< v 10)) (set sign 1))) (on score (if (= colour P) (do (set v (+ v 1)) (if (>= v 10) (do (set bad 1) (set amount 20))))))"),
 ("satiety", "ok", "(let s 0) (on tick (set s (* s (exp (* -0.1 TICK))))) (on score (set amount (/ 1 (+ 1 s))) (set s (+ s 1)))"),
 ("balanced diet", "ok", "(let d 0) (on meal (if (> (abs (+ d (if (= colour 0) 1 -1))) 3) (set sign -1))) (on score (set d (+ d (if (= colour 0) 1 -1))))"),
 ("tolerance", "ok", "(let k 1) (let l -1) (on score (if (= colour l) (set k (* k 0.7)) (set k 1)) (set amount k) (set l colour))"),
 ("blocks turn bad with age", "ok", "(table b0 N 1 0) (on meal (if (> (- t (at b0 block)) 20) (set sign -1))) (on score (put b0 block t))"),
 ("a tide sweeps", "ok", "(on tick (each b (bset b (+ (bx b) (* TICK 0.005 (sin (/ (* TWOPI t) 20)))) (by b))))"),
 ("a weather front", "ok", "(on tick (set poison (if (< (mod (- x (* 0.002 t)) WORLD) 0.02) F P)))"),
 ("blocks expire", "ok", "(table b0 N 1 0) (on score (put b0 block t)) (on tick (each b (if (> (- t (at b0 b)) 20) (do (respawn b) (put b0 b t)))))"),
 ("food only available on a fixed schedule", "ok", "(on meal (if (and (= colour F) (> (mod t 10) 3)) (drop)))"),
 ("a gait", "ok", "(let l -1) (on fire (if (= thruster l) (set gain 0.2)) (set l thruster))"),
 ("stiction", "ok", "(let n 0) (on tick (set n (* n (exp (* -5 TICK))))) (on fire (set gain (min 1 (/ n 5))) (set n (+ n 1)))"),
 ("an unstable body", "ok", "(on tick (set spin (* spin (exp (* 60 TICK)))))"),
 ("the right thruster only works", "ok", "(let l -9) (on fire (if (= thruster 0) (set l t) (if (> (- t l) 0.2) (drop))))"),
 ("a hidden gear", "ok", "(on fire (if (= (mod (floor (/ t 15)) 2) 1) (do (drop) (thrust (- 1 thruster)))))"),
 ("changed: the brain's time constants", "ok", "(const DRAG (* DRAG (pow 2 (uniform -1 1)))) (const PUSH (* PUSH (pow 2 (uniform -1 1)))) (const TURN (* TURN (pow 2 (uniform -1 1))))"),
 ("heavier with meals", "ok", "(let m 1) (on score (set m (+ m 0.02))) (on fire (set gain (/ 1 m))) (on tick (set m (max 0.5 (- m (* 0.01 TICK)))))"),
 ("thrusters tire", "ok", "(let a 0) (let b 0) (on tick (set a (* a (exp (* -0.2 TICK)))) (set b (* b (exp (* -0.2 TICK))))) (on fire (set gain (/ 1 (+ 1 (if (= thruster 0) a b)))) (if (= thruster 0) (set a (+ a 0.05)) (set b (+ b 0.05))))"),
 ("steering reversed", "ok", "(on fire (drop) (thrust (- 1 thruster)))"),
 ("lag or backlash", "ok", "(on fire (drop) (after 0.05 (thrust thruster)))"),
 ("a sudden new body", "ok", "(let d 0) (on tick (if (and (>= t 50) (= d 0)) (do (set d 1) (set PUSH (* 0.5 PUSH)) (set DRAG (* 2 DRAG)))))"),
 ("a thruster fails", "ok", "(let k (int 2)) (let T (uniform 0 100)) (on fire (if (and (= thruster k) (>= t T)) (drop)))"),
 ("thrusters fire by themselves", "ok", "(on tick (repeat (poisson (* 1 TICK)) (thrust (int 2))))"),
 ("the mouth off-centre", "no", "no register for the mouth apart from the eyes' corridor: one word short (a mouth offset in Body.head)"),
 ("food bruises above a speed", "ok", "(on meal (if (> speed 0.03) (set sign -1)))"),
 ("the mouth's reach changes", "bad", "(on tick (set EAT (+ 0.001 (* 0.02 (abs speed)))))", "EAT also sets the eyes' corridor, so the eyes change with it"),
 ("the world shrinks or grows", "ok", "(on tick (set WORLD (+ 0.06 (* 0.0001 t))))"),
 ("a thruster firing blinds", "ok", "(let l -1) (on fire (set l t)) (on pulse (if (< (- t l) 0.055) (drop)))"),
 ("eating causes a phantom flash", "ok", "(on score (pulse (int 2)))"),
 ("every eye pulse or taste echoes", "ok", "(on pulse (after 0.05 (pulse eye)))"),
 ("a mirage", "ok", "(on tick (bset 0 (+ x (* 0.005 (cos heading))) (+ y (* 0.005 (sin heading))))) (on meal (if (= block 0) (drop)))"),
 ("sticky food", "ok", "(let a -9) (on score (set a t)) (on fire (if (< (- t a) 2) (set gain 0.3)))"),
 ("eating leaves debris", "ok", "(const BLOCKS 23) (let j 0) (on birth (each b (if (>= (mod b BLOCKS) 18) (do (hide b) (bkind b 2))))) (on meal (if (= colour 2) (set sign 0))) (on score (if (< colour 2) (do (set j (mod (+ j 1) 5)) (bset (+ 18 j) x y) (show (+ 18 j)))))"),
 ("a trail of your own", "s5", "(table g 30 30 -99) (let cx 0) (let cy 0) (on tick (set cx (floor (/ x 0.002))) (set cy (floor (/ y 0.002))) (if (and (> (- t (at g cx cy)) 1) (< (- t (at g cx cy)) 10)) (taste -1)) (put g cx cy t))"),
 ("free tastes whatever", "s5", "(on tick (if (chance (* 0.2 TICK)) (taste 1)))"),
 ("bad tastes for fouls", "s5", "(let a -9) (on tick (if (and (> (- t a) 5) (> (abs spin) 15)) (do (set a t) (taste -1))))"),
 ("tastes with no meal", "s5", "(on tick (if (chance (* 0.1 TICK)) (taste 1))) (on taste (if (chance 0.1) (drop)))"),
 ("a good colour that depends on region", "ok", "(on tick (set poison (if (< x (/ WORLD 2)) P F)))"),
 ("carry each meal home", "ok", "(let h 0) (on score (set amount 0) (set h (+ h 1))) (on tick (if (and (> h 0) (< (dist 0.03 0.03) 0.005)) (do (score h) (set h 0))))"),
 ("walls, narrow gaps", "bad", "(on move (if (and (< (abs (- x 0.03)) 0.001) (> (abs (- y 0.03)) 0.005)) (do (set x (- x (* vx TICK))) (set vx 0))))", "stops the body, but doesn't hide what's behind it or confine blocks: a wall of occluding blocks would take a table of them"),
 ("mud, currents", "ok", "(on tick (set vx (+ vx (* 0.01 TICK))))"),
 ("a tether |", "ok", "(on tick (set vx (- vx (* 5 (- x 0.03) TICK))) (set vy (- vy (* 5 (- y 0.03) TICK))))"),
 ("a Moebius twist", "ok", "(let lx 0.03) (let tw 0) (on tick (if (> (abs (- x lx)) 0.03) (set tw (- 1 tw))) (set lx x)) (on fire (if (= tw 1) (do (drop) (thrust (- 1 thruster)))))"),
 ("a sun", "ok", "(on see (if (< (cos heading) -0.7) (set seen (+ seen 0.5))))"),
 ("food only where you haven't been", "ok", "(table g 30 30 0) (on meal (if (> (at g (floor (/ x 0.002)) (floor (/ y 0.002))) 0) (set sign -1))) (on tick (put g (floor (/ x 0.002)) (floor (/ y 0.002)) 1))"),
 ("blocks respawn where you just ate", "ok", "(on respawn (set nx (- x (* 0.005 (cos heading)))) (set ny (- y (* 0.005 (sin heading)))))"),
 ("whatever you eat most", "ok", "(let a 0) (let b 0) (on tick (set poison (if (> a b) 0 1))) (on score (if (= colour 0) (set a (+ a 1)) (set b (+ b 1))))"),
 ("food only if colour matches context", "ok", "(on meal (set sign (if (= (> (near 0 0.01) 0) (= colour 1)) 1 -1)))"),
 ("key and lock", "ok", "(let k -99) (on tick (set poison (if (< (- t k) 5) -1 P))) (on score (if (= colour F) (set k t)))"),
 ("an antidote", "ok", "(let a -9) (on score (if (= colour P) (set a t) (if (< (- t a) 2) (score 2))))"),
 ("food hidden behind poison", "bad", "(let j 0) (on respawn (if (= (kind block) F) (do (set j (- block BLOCKS)) (set nx (+ (bx j) 0.003)) (set ny (by j))) (do (set nx (uniform 0 WORLD)) (set ny (uniform 0 WORLD)))))", "beside a poison block, not behind it from where the creature approaches: 'behind' has no word"),
 ("flicker or brightness", "ok", "(table g N 1 (int 2)) (on birth (each b (bbright b (if (= (at g b) 1) 1 0.5)))) (on meal (set sign (if (= (at g block) 1) 1 -1))) (on score (put g block (int 2)) (bbright block (if (= (at g block) 1) 1 0.5)))"),
 ("blocks of a colour vary in worth", "ok", "(table w N 1 (uniform 0 2)) (on score (set amount (at w block)))"),
 ("seeing lots of blue", "ok", "(let l 0) (on see (if (= colour 1) (set l (+ (* l 0.99) seen)))) (on tick (set poison (if (> l 5) 0 -1)))"),
 ("a guide", "bad", "(let j 0) (let a 0) (on birth (blook 0 0) (bkind 0 2)) (on meal (if (= block 0) (drop))) (on tick (set j (nearest F)) (set a (atan2 (- (by j) (by 0)) (- (bx j) (bx 0)))) (bset 0 (+ (bx 0) (* 0.01 TICK (cos a))) (+ (by 0) (* 0.01 TICK (sin a)))))", "the guide steers without the torus's wrap (no word for a wrapped direction), so it takes long ways round"),
 ("one cue predicts another", "ok", "(on tick (if (< (mod t 20) 1) (repeat (poisson (* 30 TICK)) (pulse 0))) (if (and (>= (mod t 20) 1) (< (mod t 20) 2)) (repeat (poisson (* 30 TICK)) (pulse 1))) (set poison (if (< (mod t 20) 10) P F)))"),
 ("a pattern of pulses at birth", "ok", "(on tick (if (< t 1) (repeat (poisson (* 50 TICK)) (pulse (sensor F)))))"),
 ("food lies in lines", "ok", "(on respawn (set nx (uniform 0 WORLD)) (set ny (* 0.01 (int 6))))"),
 ("one colour steady", "ok", "(on tick (set poison -1)) (on score (if (and (= colour P) (chance 0.05)) (set amount 10)))"),
 ("a rare block worth ten", "ok", "(on score (if (and (not bad) (chance 0.05)) (set amount 10)))"),
 ("rare catastrophes", "s5", "(on score (if (chance 0.0001) (end)))"),
 ("a lethal meal", "s5", "(on score (if bad (end)))"),
 ("world A, B, A, B", "ok", "(let i 0) (let l -1) (on tick (set poison (if (= (mod (floor (/ t 25)) 2) 0) l (if (= i 2) F P)))) (on score (set l colour) (if (= colour (if (= i 2) P F)) (set i (mod (+ i 1) 3))))"),
 ("the rule changes between bank models", "ok", "(let l -1) (on tick (set poison (if (< t 50) P l))) (on score (if (>= t 50) (set l colour)))"),
 ("serial reversals", "ok", "(on tick (set poison (mod (+ P (floor (/ t 20))) 2)))"),
 ("nothing changes for ages", "ok", "(on tick (set poison (if (< t 80) P F)))"),
 ("born confidently wrong", "no", "a brain's state at birth (its bit and tally) has no write point: only its numbers (bp)"),
 ("memory wiped periodically", "no", "a brain's memory has no write point, and what to wipe is brain-specific"),
 ("an eye or thruster that does nothing", "ok", "(let e (int 2)) (on pulse (if (and (= eye e) (chance (min 1 (/ t 50)))) (drop)))"),
 ("one eye masks the other", "ok", "(let a -9) (on pulse (if (= eye 0) (set a t) (if (< (- t a) 0.05) (drop))))"),
 ("eye pulses cancel", "bad", "(let a -9) (let e 0) (on pulse (if (and (< (- t a) TICK) (!= eye e)) (drop)) (set a t) (set e eye))", "only the later of the two is dropped: cancelling both needs each pulse held a tick"),
 ("eyes see a little of the other colour", "ok", "(on see (set seen (+ seen (* 0.3 (raw (- 1 colour))))))"),
 ("blocks blink", "ok", "(on tick (each b (blook b (if (< (mod (+ t b) 2) 1) (kind b) -1))))"),
 ("empty decoys and mimics", "ok", "(on birth (each b (if (= (mod b 3) 0) (bkind b 2)))) (on meal (if (= colour 2) (set sign 0)))"),
 ("eyes ignore anything faint", "ok", "(on see (if (< seen 0.2) (set seen 0)))"),
 ("a lie arrives in bursts", "ok", "(let l 0) (told P) (on tick (set l (if (= l 1) (if (chance (* 0.5 TICK)) 0 1) (if (chance (* 0.1 TICK)) 1 0))) (set poison (if (= l 1) F P)))"),
 ("eyes work only just after a thruster", "ok", "(let a -9) (on fire (set a t)) (on pulse (if (> (- t a) 0.1) (drop)))"),
 ("an unused eye decays", "bad", "(table g 2 1 1) (let l 0) (on pulse (set l eye)) (on fire (put g l (min 2 (+ (at g l) 0.01)))) (on tick (put g 0 (* (at g 0) (exp (* -0.05 TICK)))) (put g 1 (* (at g 1) (exp (* -0.05 TICK))))) (on see (set seen (* seen (at g (sensor colour)))))", "'used' read as a firing after the eye's pulse: a guess at what 'used' means"),
 ("a preview of taste", "s5", "(on tick (if (and (> (near F 0.01) 0) (chance (* 2 TICK))) (taste 1)))"),
 ("poison chases you", "ok", "(let a 0) (on tick (each b (if (= (kind b) P) (do (set a (atan2 (- y (by b)) (- x (bx b)))) (bset b (+ (bx b) (* 0.003 TICK (cos a))) (+ (by b) (* 0.003 TICK (sin a))))))))"),
 ("firing thrusters draws poison", "ok", "(let f -9) (let a 0) (on fire (set f t)) (on tick (if (< (- t f) 0.5) (each b (if (= (kind b) P) (do (set a (atan2 (- y (by b)) (- x (bx b)))) (bset b (+ (bx b) (* 0.01 TICK (cos a))) (+ (by b) (* 0.01 TICK (sin a)))))))))"),
 ("a rival eats the food", "ok", "(on tick (if (chance (* 1 TICK)) (respawn (+ (* BLOCKS F) (int BLOCKS)))))"),
 ("infected by poison", "ok", "(let i 0) (on score (if bad (set i 1))) (on tick (if (and (= i 1) (chance (* 1 TICK))) (thrust (int 2))))"),
 ("moving costs ten times", "ok", "(const THRUST 10)"),
 ("life's length unknown", "s5", "(let T (uniform 30 100)) (on tick (if (> t T) (end)))"),
 ("nothing's poison until learned", "ok", "(let g 0) (on tick (set poison (if (< g 10) -1 (mod (+ P (floor (/ t 15))) 2)))) (on score (if (not bad) (set g (+ g 1))))"),
 ("taste inverted for good", "s5", "(on taste (set value (- value)))"),
 ("coin-toss tastes", "ok", "(told P) (on tick (set poison (if (chance 0.5) F P)))"),
 ("matching pennies", "ok", "(let a 0) (let b 0) (on tick (set a (* a (exp (* -0.2 TICK)))) (set b (* b (exp (* -0.2 TICK)))) (set poison (if (> a b) 0 1))) (on score (if (= colour 0) (set a (+ a 1)) (set b (+ b 1))))"),
 ("all blocks tasteless for 50 s", "ok", "(on meal (if (< t 50) (set sign 0)))"),
 ("one colour tasteless at first", "ok", "(on meal (if (and (< t 30) (= colour P)) (set sign 0)))"),
 ("blocks are pushed", "bad", "(let c 0) (on meal (set c 0) (each b (if (and (!= b block) (alive b) (< (wdist (bx b) (by b) (bx block) (by block)) 0.003)) (set c 1))) (if (= c 0) (do (drop) (bset block (+ (bx block) (* 0.003 (cos heading))) (+ (by block) (* 0.003 (sin heading)))))))", "written, a block moved a fixed push: no contact physics"),
 ("an inert signpost", "bad", "(on birth (each b (if (= (mod b 6) 0) (do (bkind b 2) (bset b (+ (bx (+ b 1)) 0.004) (by (+ b 1))))))) (on meal (if (= colour 2) (set sign 0))) (on tick (set poison (if (< t 40) F P)))", "signposts share a colour's eye, there being only two: an inert third look doesn't exist"),
 ("a colour that pays alone", "ok", "(on meal (if (and (< t 40) (= colour P)) (set sign 0))) (on tick (set poison -1))"),
 ("two-colour blocks", "bad", "(let d 0) (on birth (each b (if (< (mod b BLOCKS) 6) (if (>= b BLOCKS) (bset b (bx (- b BLOCKS)) (by (- b BLOCKS))))))) (on meal (if (and (< (mod block BLOCKS) 6)) (set sign -0.51)))", "a block has one look, so two blocks at one place, which the mouth eats together; each kept together only until eaten"),
 ("one cue changes what another means", "ok", "(let a -9) (on see (if (and (= colour P) (> seen 0.1)) (set a t))) (on tick (set poison (if (< (- t a) 3) F P)))"),
 ("colour decides at first", "bad", "(table acc 2 1 0) (on see (if (>= t 40) (do (put acc colour (+ (at acc colour) (* SENSE seen TICK))) (if (and (= colour F) (>= (at acc colour) 1)) (do (pulse (sensor colour)) (put acc colour 0))) (if (= colour F) (set seen 0))))) (on tick (set poison (if (< t 40) P P)))", "the pulse generator rewritten by hand, by colour and not by block: regularity can't be a block's own"),
 ("a colour bad at first", "ok", "(let d 0) (on meal (if (and (= colour P) (>= d 5)) (set sign 1))) (on score (if (= colour P) (do (set d (+ d 1)) (if (>= d 5) (set amount 3)))))"),
 ("food ringed by poison", "bad", "(on birth (each b (if (>= b BLOCKS) (bset b (+ (bx (- b BLOCKS)) (* 0.0025 (cos b))) (+ (by (- b BLOCKS)) (* 0.0025 (sin b))))))) (on respawn (set nx (+ (bx (mod block BLOCKS)) 0.0025)) (set ny (by (mod block BLOCKS))))", "pairs and not rings: a ring takes several poison blocks per food and a table of who rings whom"),
 ("a tether: reach far blocks", "ok", "(on tick (set vx (- vx (* 5 (- x 0.03) TICK))) (set vy (- vy (* 5 (- y 0.03) TICK))))"),
 ("a block flees", "ok", "(let f -9) (let j 0) (on fire (set f t)) (on tick (if (< (- t f) 0.1) (do (set j (nearest -1)) (if (< (dist (bx j) (by j)) 0.015) (bset j (+ (bx j) (* 0.01 TICK (cos heading))) (+ (by j) (* 0.01 TICK (sin heading))))))))"),
 ("anything eaten on a hidden beat", "ok", "(on meal (set sign (if (< (mod t 4) 2) 1 -1)))"),
 ("memory depends on meals being spaced", "bad", "(let a -9) (on meal (if (< (- t a) 2) (set sign 0))) (on score (set a t))", "a world can't reach the brain's memory, so a massed meal is made tasteless and empty: another world"),
 ("a stepper rudder", "ok", "(let n 0) (on fire (set n (mod (+ n 1) 4)) (set heading (+ heading (* 0.3 (- n 1.5)))))"),
 ("eye rate rises then falls", "ok", "(let j 0) (on see (set j (nearest colour)) (if (and (>= j 0) (< (dist (bx j) (by j)) 0.004)) (set seen (* seen 0.2))))"),
 ("a sloshing tank", "ok", "(let w 0) (let l 0) (on fire (set w (+ (* 0.9 w) (cos (/ (* TWOPI (- t l)) 0.3)))) (set l t) (set spin (+ spin (* 2 w))))"),
 ("a firing kicks the nose", "ok", "(on fire (set heading (+ heading (if (= thruster 0) 0.1 -0.1))) (after 0.05 (set heading (+ heading (if (= thruster 0) -0.1 0.1)))))"),
 ("eyes give only noise", "bad", "(let n 0) (let l 0) (on pulse (drop)) (on fire (set n (if (!= thruster l) (+ n 1) 0)) (set l thruster) (if (> n 8) (do (set n 0) (bset (+ (* BLOCKS F) (int BLOCKS)) (+ x (* 0.004 (cos heading))) (+ y (* 0.004 (sin heading))))))) (on tick (repeat (poisson (* 10 TICK)) (pulse (int 2))))", "food placed before the mouth by a firing pattern: it works only if the creature keeps moving forward"),
 ("each meal in a streak", "ok", "(let s 0) (on meal (if (chance (* 0.1 s)) (set sign -1))) (on score (set s (if bad 0 (+ s 1))))"),
 ("an unseen competitor", "ok", "(on tick (if (chance (* 1 TICK)) (respawn (+ (* BLOCKS F) (int BLOCKS)))))"),
 ("danger in bouts", "s5", "(on fire (if (chance (if (< (mod t 30) 10) 0.01 0)) (taste -1)))"),
 ("taste is silent while turning", "s5", "(on taste (if (> (abs spin) 8) (drop)))"),
 ("poison creeps towards you", "ok", "(let l 0) (let a 0) (on see (if (= colour P) (set l seen))) (on tick (if (= l 0) (each b (if (= (kind b) P) (do (set a (atan2 (- y (by b)) (- x (bx b)))) (bset b (+ (bx b) (* 0.003 TICK (cos a))) (+ (by b) (* 0.003 TICK (sin a)))))))))"),
 ("tag: the same stimulus", "ok", "(let g 1) (let j 0) (let a 0) (on taste (set g value)) (on tick (set j (nearest -1)) (set a (atan2 (- y (by j)) (- x (bx j)))) (bset j (+ (bx j) (* g -0.005 TICK (cos a))) (+ (by j) (* g -0.005 TICK (sin a)))))"),
 ("tasteless flicker posts", "ok", "(on birth (each b (if (= (mod b 6) 0) (bkind b 2)))) (on meal (if (= colour 2) (set sign 0))) (on tick (each b (if (= (kind b) 2) (bbright b (if (chance 0.5) 1 0)))))"),
 ("all blocks tasteless for 25 s", "ok", "(on meal (if (and (> t 40) (< t 65)) (set sign 0)))"),
 ("a world ten times wider", "ok", "(const WORLD (* 10 WORLD)) (let cx (uniform 0 WORLD)) (let cy (uniform 0 WORLD)) (on birth (each b (respawn b))) (on respawn (set nx (+ cx (normal 0 0.01))) (set ny (+ cy (normal 0 0.01))))"),
 ("everything snaps back", "ok", "(table s N 2 0) (let x0 0) (let y0 0) (let nxt 20) (on birth (set x0 x) (set y0 y) (each b (put s b 0 (bx b)) (put s b 1 (by b)))) (on tick (if (>= t nxt) (do (set nxt (+ nxt 20)) (set x x0) (set y y0) (each b (bset b (at s b 0) (at s b 1))))))"),
 ("positive or negative tastes mostly lost", "s5", "(on taste (if (and (> value 0) (chance 0.9)) (drop)))"),
 ("a deep power sag", "no", "a brain's fast memory has no write point; what a sag wipes is brain-specific"),
 ("junk food", "ok", "(let a -99) (on score (if (= colour P) (set a t))) (on meal (if (= colour P) (set sign 1))) (on fire (if (< (- t a) 5) (set gain 0.3)))"),
 ("a stroke", "bad", "(let T (uniform 0 100)) (on tick (if (> t T) (bp scan 0)))", "one number of the block model set to 0, and only numbers can be: which blocks exist isn't in the language"),
 ("gains drift until feedback", "bad", "(on tick (bp drive (* (bpget drive) (exp (* 0.01 TICK)))))", "the block model has no feedback to run away: a rate raised"),
 ("recruits keep multiplying", "no", "neither brain has recruits; a brain's growth has no write point"),
 ("motor drive declines", "ok", "(on tick (bp drive (* (bpget drive) (exp (* -0.005 TICK)))))"),
 ("memory's retention falls", "bad", "(on tick (bp hold (* (bpget hold) (exp (* -0.005 TICK)))))", "the bank's memory has no retention number: a hold shortened in its place"),
 ("waste from firing", "ok", "(let w 0) (on fire (set w (+ w 0.05))) (on tick (set w (* w (exp (- TICK)))) (repeat (poisson (* w TICK)) (pulse (int 2))))"),
 ("each write permanently shrinks", "no", "a brain's memory cell has no write point"),
 ("a scavenger", "ok", "(let j -1) (let d 0) (let k 0) (on tick (set k (nearest -1)) (if (and (= k j) (< (dist (bx k) (by k)) 0.015)) (set d (+ d TICK)) (do (set j k) (set d 0))) (if (> d 1) (do (respawn k) (set d 0))))"),
 ("after n reds", "ok", "(let n 1) (let c 0) (let ph 0) (on tick (set poison (if (= ph 0) 1 0))) (on score (if (= colour ph) (set c (+ c 1))) (if (>= c n) (do (set c 0) (set ph (- 1 ph)) (if (= ph 0) (set n (+ n 1))))))"),
 ("taste is parity", "bad", "(let s0 (int 2)) (let s1 (int 2)) (let s2 (int 2)) (let s3 (int 2)) (let s4 (int 2)) (let s5 (int 2)) (let s6 (int 2)) (let s7 (int 2)) (let h0 0) (let h1 0) (let h2 0) (let h3 0) (let h4 0) (let h5 0) (let h6 0) (let h7 0) (on tick (set poison (- 1 (mod (+ (* s0 h0) (* s1 h1) (* s2 h2) (* s3 h3) (* s4 h4) (* s5 h5) (* s6 h6) (* s7 h7)) 2)))) (on score (set h7 h6) (set h6 h5) (set h5 h4) (set h4 h3) (set h3 h2) (set h2 h1) (set h1 h0) (set h0 colour))", "long: no loops over a table's rows, no bit operations"),
 ("thrust unlocked by a secret word", "ok", "(let w0 (int 2)) (let w1 (int 2)) (let w2 (int 2)) (let w3 (int 2)) (let i 0) (on fire (if (< i 4) (set gain 0.2)) (if (< i 4) (if (= thruster (if (= i 0) w0 (if (= i 1) w1 (if (= i 2) w2 w3)))) (set i (+ i 1)) (set i 0))))"),
 ("heading diverges unless corrected", "ok", "(on tick (set spin (* spin (exp (* 60 TICK)))))"),
 ("every 50th motor firing", "s5", "(let n 0) (on fire (set n (+ n 1)) (if (= (mod n 50) 0) (taste -1)))"),
 ("a free meal after 15 s", "s5", "(let a 0) (on score (set a t)) (on tick (if (> (- t a) 15) (do (score 1) (taste 1) (set a t))))"),
 ("worth depends on the firing rate", "ok", "(let r 0) (on fire (set r (+ r 1))) (on tick (set r (* r (exp (* -0.5 TICK))))) (on meal (set sign (if (> r 20) -1 1)))"),
 ("an implausibly rare punishment", "s5", "(on meal (if (and (= colour P) (not (chance 0.1))) (set sign 1))) (on score (set bad (= colour P)))"),
 ("a tasteless colour banks a token", "ok", "(let k 0) (on tick (set k (* k (exp (* -0.2 TICK))))) (on meal (if (= colour P) (set sign 0)) (if (and (= colour F) (< k 0.5)) (set sign -1))) (on score (if (= colour P) (set k 1)))"),
 ("a poison block drives its eye", "ok", "(on see (if (= colour poison) (set seen (* 3 seen))))"),
 ("each eye sees a random mixture", "ok", "(let a (uniform 0 1)) (on see (set seen (+ (* a (raw colour)) (* (- 1 a) (raw (- 1 colour))))))"),
 ("same rate, different texture", "bad", "(table acc 2 1 0) (on see (if (= colour F) (do (put acc colour (+ (at acc colour) (* SENSE seen TICK))) (if (>= (at acc colour) 1) (do (pulse (sensor colour)) (put acc colour 0))) (set seen 0))))", "by colour, not by block"),
 ("a block has a hidden reserve speed", "ok", "(table v N 1 (uniform 0 0.05)) (on meal (if (< speed (at v block)) (do (drop) (bset block (+ (bx block) (* 0.003 (cos heading))) (+ (by block) (* 0.003 (sin heading)))))))"),
 ("one thruster weak for 30 s", "ok", "(let k (int 2)) (on fire (if (and (= thruster k) (< t 30)) (set gain 0.3)))"),
 ("a growing body", "ok", "(on tick (set RADIUS (+ 0.0012 (* 0.000012 t))))"),
 ("hinges rather than thrusters", "bad", "(let l -1) (on fire (set gain (if (= thruster l) -1 1)) (set l thruster))", "a rough stand-in: repeated strokes undo each other"),
 ("blocks on a fractal", "ok", "(on respawn (set nx 0) (set ny 0) (repeat 5 (set nx (+ (/ nx 3) (* (int 2) 0.04))) (set ny (+ (/ ny 3) (* (int 2) 0.04)))))"),
 ("blocks as live cells", "bad", "(table now N 1 (int 2)) (table nxt N 1 0) (let n 5) (let c 0) (on birth (each b (bset b (* (+ 0.5 (mod b 6)) 0.01) (* (+ 0.5 (floor (/ b 6))) 0.01)) (if (= (at now b) 0) (hide b)))) (on tick (if (>= t n) (do (set n (+ n 5)) (each b (set c (+ (at now (mod (+ b 1) N)) (at now (mod (+ b 35) N)) (at now (mod (+ b 6) N)) (at now (mod (+ b 30) N)) (at now (mod (+ b 7) N)) (at now (mod (+ b 5) N)) (at now (mod (+ b 31) N)) (at now (mod (+ b 29) N)))) (put nxt b (if (or (= c 3) (and (= c 2) (= (at now b) 1))) 1 0))) (each b (put now b (at nxt b)) (if (= (at now b) 1) (show b) (hide b)))))) (on respawn (set nx (bx block)) (set ny (by block)))", "long: no loops over a grid's cells"),
 ("crossing one seam", "ok", "(let lx 0.03) (let s 0) (on tick (if (> (abs (- x lx)) 0.03) (set s (- 1 s))) (set lx x) (set poison (if (= s 1) F P)))"),
 ("one eye silent for 30 s", "ok", "(let e (int 2)) (on pulse (if (and (= eye e) (< t 30)) (drop)))"),
 ("only the food colour exists", "ok", "(let d 0) (on birth (each b (if (= (kind b) P) (hide b)))) (on tick (if (and (>= t 25) (= d 0)) (do (set d 1) (each b (show b)))))"),
 ("the taste wire dies", "s5", "(on taste (if (>= t 40) (drop)))"),
 ("insurance", "s5", "(let r 0) (on fire (set r (+ r 1))) (on tick (set r (* r (exp (* -0.5 TICK))))) (on taste (if (and (< value 0) (> r 20)) (drop))) (on score (if (and bad (> r 20)) (set amount 0.5)))"),
 ("firing stirs a wake", "ok", "(on fire (each b (if (< (dist (bx b) (by b)) 0.01) (bset b (+ (bx b) (uniform -0.001 0.001)) (+ (by b) (uniform -0.001 0.001))))))"),
 ("a nut that needs three strikes", "ok", "(table h N 1 0) (on meal (put h block (+ 1 (at h block))) (if (< (at h block) 3) (drop) (put h block 0)))"),
 ("predator-prey", "bad", "(let f 18) (let p 18) (on tick (set f (min 18 (max 1 (+ f (* TICK f (- 0.3 (* 0.02 p))))))) (set p (min 18 (max 1 (+ p (* TICK p (- (* 0.02 f) 0.3)))))) (each b (if (< (mod b BLOCKS) (if (= (kind b) F) f p)) (show b) (hide b))))", "a population as a count of shown blocks, the eaten not feeding back; a hidden block's next showing is where it was"),
 ("taste arrives when blocks are sorted", "s5", "(let d 0) (let c 0) (on fire (set c 0) (each b (if (< (bx b) 0.03) (set c (+ c (if (= (kind b) 0) 1 -1))))) (if (and (> c 14) (= d 0)) (do (set d 1) (taste 1))))"),
]


def ideas():
    src = open("/home/pilgrim/git/simple-learner/GRAMMAR.md").read().split("\n")
    a = src.index("## The catalogue")
    b = src.index("## The experiment")
    out = []
    for l in src[a:b]:
        m = re.match(r"^\|([^|]*)\|([^|]+)\|([^|]+)\|([^|]+)\|$", l)
        if m and not m.group(2).strip().startswith(("idea", "---")):
            out.append(m.group(2).strip())
    return out


def run_one(item):
    key, status, prog, *note = item
    if status == "no":
        return key, status, None, None, ""
    t = f"(world {prog})"
    w = S.world_of(t, key)
    bits = lang.bits(w)
    S.live(S.make(w, "circuit", 63000, "red"), 5.0)
    S.live(S.make(w, "bank", 63001, "blue"), 5.0)
    return key, status, bits, w.stage5(), note[0] if note else ""


def main():
    from concurrent.futures import ProcessPoolExecutor
    I = ideas()
    matched = {}
    for e in E:
        hits = [x for x in I if x == e[0][:-2]] if e[0].endswith(" |") else [x for x in I if e[0] in x]
        if len(hits) != 1:
            print("KEY MATCHES", len(hits), e[0], hits[:3])
        for h in hits:
            matched.setdefault(h, []).append(e[0])
    missing = [x for x in I if x not in matched]
    print(f"{len(I)} ideas in GRAMMAR.md's catalogue, {len(E)} entries; unmatched ideas: {missing}", flush=True)
    bad_run = []
    res = []
    with ProcessPoolExecutor(7) as ex:
        fs = [(e, ex.submit(run_one, e)) for e in E]
        for e, f in fs:
            try:
                res.append(f.result())
            except Exception as err:
                bad_run.append((e[0], f"{type(err).__name__}: {err}"))
    from collections import Counter
    c = Counter(r[1] for r in res)
    print("status:", dict(c), "; failed to compile or run:", bad_run, flush=True)
    bits = [r[2] for r in res if r[2] is not None]
    print("description length, bits: median", np.median(bits), "90%", np.percentile(bits, 90), "max", max(bits), flush=True)
    print("by status: " + "; ".join(f"{s} median {np.median([r[2] for r in res if r[1] == s and r[2] is not None]):.0f}" for s in ("ok", "s5", "bad")), flush=True)
    for r in res:
        if r[1] == "s5" and not r[3]:
            print("   marked s5, text shows no static reason (a runtime check would catch it):", r[0], flush=True)
        if r[1] in ("ok", "bad") and r[3]:
            print("   NOT marked s5 but its text changes the rules:", r[0], r[3], flush=True)
    print("== bad, and why", flush=True)
    for r in res:
        if r[1] == "bad":
            print(f"   {r[0]}: {r[2]} bits. {r[4]}", flush=True)
    print("== no, and why", flush=True)
    for e in E:
        if e[1] == "no":
            print(f"   {e[0]}: {e[2]}", flush=True)


if __name__ == "__main__":
    main()

"""stage2b_reference.py: the frozen reference of stage 2b (PROGRAMME.md, A pass), as written down in lab/v/stage2b_reference.md before it ran
on any world. Frozen: its SHA-256 is in that file; any change makes a new reference, judged afresh.

It is stage 1c's widest learner (D32: "393 periods, 16 phases + HMMs + seven", lab/stage1c_arms.Mix, settings of lab/stage1c_change.py's
hmm()), with one change: an exact tie in the vote keeps the colour it follows instead of going to sensor 0 (D32: a reference must state its
tie rule; Mix's `vote > .5` sent ties to one sensor). Nothing else differs, and lab/stage1c_arms.py is untouched.

    from stage2b_reference import Ref, FROZEN    # an arm "ref" in stage2_lang.arms: Ref(seed, numbers(seed, V7 + FROZEN))"""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import stage1c_arms as A

FROZEN = dict(eps=0.1, s7=1 / 3, sh=1 / 3, sp=1 / 3, pr=0.6, lams=[0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0], fam="T393P16", every=5)


class Ref(A.Mix):
    """The exact Bayesian mixture over the seven, eight two-state HMMs and 393 x 16 periodic swaps, each with both starting colours; a
    scored taste says which colour was food, each hypothesis's prediction right with chance 1 - eps, independently. It follows the colour
    with the larger posterior predictive; on an exact tie (to 1e-12) it keeps the colour it follows."""

    def decide(self, keep):
        v = self.vote()
        self.food = 1 if v > 0.5 + 1e-12 else 0 if v < 0.5 - 1e-12 else keep

    def taste(self, value, at):
        scored, truth, _ = self.about(value)
        was_open, keep = self.open, self.food
        if scored:
            self.observe(truth)
        A.B.Recorder.taste(self, value, at)               # the bank's body and parts; its own choice is off (Mix: bankk=0, choose does nothing)
        if was_open and not self.open:
            self.observe(self.food)                       # the first bad is a taste too; all the seven agree on it (as Mix)
            keep = self.food
        if not self.open:
            self.decide(keep)

    def step(self):
        self.nticks += 1
        if self.timed and not self.open and self.nticks % self.every == 0:
            self.decide(self.food)
        return A.B.Recorder.step(self)

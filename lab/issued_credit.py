"""D82 opt-in issued-forecast credit for the frozen net10kc60SFBLMR software brain.

Instance patches only. The cache is additional learner state, kept in this observer
object (not categorical units). Default mechanics, taste gate/letter, current-context
sequential learning and growth remain native. Stream scores refer to issued forecasts;
correct surviving original speakers receive their native recursive use/own credit.
Deleted IDs are never redirected or resurrected. No economy/JointNet/graded modes.

install(lf, enabled=False) observes without changing native state or arithmetic.
Call summary() for software-state/activity proxies; this is not physical accounting.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
import math
import numpy as np


@dataclass(frozen=True)
class Forecast:
    speaker: int | None
    choice: int | None
    p0: float | None
    p1: float | None

    @property
    def awake(self):
        return self.p1 is not None

    def likelihood(self, letter):
        return self.p1 if letter else self.p0


def _selector(weights, saved, records, letter, share):
    """Native BT=1 likelihood/share arithmetic using exact cached p(label)."""
    weights, saved = list(weights), list(saved)
    active = [j for j,r in enumerate(records) if j and r.awake]
    pd = records[0].likelihood(letter)
    total = weights[0] + sum(weights[j] for j in active)
    pm = (weights[0]*pd + sum(weights[j]*records[j].likelihood(letter) for j in active))/total
    weights[0] *= pd/pm
    for j in active:
        q = records[j].likelihood(letter)
        weights[j] *= q/pm
        saved[j] += math.log2(q/pd)
    if active and share:
        even = share*total/(len(active)+1)
        weights[0] = (1-share)*weights[0]+even
        for j in active:
            weights[j] = (1-share)*weights[j]+even
    top = max(weights)
    if top < 1e-6:
        weights = [w/top for w in weights]
    return weights, saved, -math.log2(max(pm,1e-12))


class IssuedCredit:
    def __init__(self, lf, enabled=True):
        import grownet as GN
        b = self.b = lf.brain
        assert getattr(b,'BAYES',False) and b.SHARE == .01 and GN.BT == 1.
        assert GN.LB_FINE and GN.LB_LIVE
        for flag in ('GRADED','DVOTE','SURP','LMIX','LB_JOINT','LB_LETTER'):
            assert not getattr(GN,flag), ('unsupported mode',flag)
        assert len(b.nets)==168, 'Only frozen net10kc60SFBLMR repertoire supported'
        assert all(type(n).says in (GN.Net.says,GN.Net2.says) and not n.economy for n in b.nets)
        self.enabled = bool(enabled)
        self.counters = Counter()
        self.last = None
        self.frame_time = None
        self.issuing = None
        self.current = None
        self.delivering = False
        self.max_reconstruction_error = 0.
        self.max_issued_entry_probability_difference = 0.
        self.originals = []
        for j,n in enumerate(b.nets,1):
            self._wrap_net(n,j)
        self._wrap_brain()

    def _record(self,n,k):
        if k is None:
            return Forecast(None,None,None,None)
        counts = n.units[k]['n']
        return Forecast(k,int(counts[1]>counts[0]),self.b._pk(n,k,0),self.b._pk(n,k,1))

    def _default(self):
        return Forecast(None,int(self.b.dl),self.b._pdef(0),self.b._pdef(1))

    def _wrap_net(self,n,j):
        original = dict(says=n.says,learn=n.learn,guessed=n.guessed,credit=n.credit,
                        own_credit=n.own_credit,remove=n._remove)
        self.originals.append(original)
        def says(i):
            answer = original['says'](i)
            if self.issuing is not None:
                assert self.issuing[j] is None, 'More than one says call per stream/prediction'
                self.issuing[j] = self._record(n,answer[0])
            return answer
        def guessed(right,t):
            if self.enabled and self.current is not None and not self.delivering:
                self.counters['native_guessed_calls_suppressed'] += 1
                return
            return original['guessed'](right,t)
        def credit(k,t,w=1.):
            if self.enabled and self.current is not None and not self.delivering:
                self.counters['native_unit_credit_calls_suppressed'] += 1
                if self.current['issued'] is not None and k != self.current['issued'][j].speaker:
                    self.counters['replacement_credit_prevented'] += 1
                return
            if self.delivering:
                self.counters['unit_use_credit_calls'] += 1
            return original['credit'](k,t,w)
        def own_credit(k,t):
            if self.enabled and self.current is not None and not self.delivering:
                self.counters['native_own_credit_calls_suppressed'] += 1
                return
            if self.delivering:
                self.counters['unit_own_credit_calls'] += 1
            return original['own_credit'](k,t)
        def remove(k):
            if k in n.units and self.last is not None and self.last[j].speaker == k:
                self.counters['cached_original_speakers_removed'] += 1
            return original['remove'](k)
        def learn(i,letter,t,speaker,firing):
            cur = self.current
            assert cur is not None and t == cur['t'], 'Learning outside timed taste contract'
            assert cur['letter'] in (None,letter)
            cur['letter'] = int(letter)
            assert j not in cur['processed']
            cur['processed'].add(j)
            self.counters['native_learn_calls'] += 1
            if self.enabled:
                assert cur['issued'] is not None, 'Accepted taste without a prior issued forecast'
                rec = cur['issued'][j]
                old_e,old_a,old_d = cur['stats'][j-1]
                default_hit = cur['issued'][0].choice == letter
                hit = rec.choice == letter if rec.awake else default_hit
                n.E = min(self.b.Emax,max(0.,old_e+(1. if hit>default_hit else -1. if hit<default_hit else 0.)))
                n.agree,n.dis = old_a,old_d
                self.counters['stream_score_field_writes'] += 3
                if rec.awake:
                    n.agree += int(hit)
                    n.dis += int(not hit)
                    self.delivering = True
                    try:
                        # Guessed is a stream trace, even if the original unit was removed.
                        original['guessed'](hit,t)
                        self.counters['issued_guessed_calls'] += 1
                        if rec.speaker not in n.units:
                            self.counters['missing_original_speakers_at_feedback'] += 1
                        if hit:
                            if rec.speaker in n.units:
                                # Use wrappers so recursive native credit follows its original ancestry.
                                n.credit(rec.speaker,t)
                                n.own_credit(rec.speaker,t)
                                self.counters['delivered_correct_forecasts'] += 1
                            else:
                                self.counters['correct_but_undeliverable_credit'] += 1
                    finally:
                        self.delivering = False
                else:
                    self.counters['issued_abstentions_at_accepted_taste'] += 1
            # Current speaker/firing remain unchanged and valid for current-context learning.
            return original['learn'](i,letter,t,speaker,firing)
        n.says,n.guessed,n.credit,n.own_credit,n._remove,n.learn = says,guessed,credit,own_credit,remove,learn

    def _apply_scores(self):
        cur,b = self.current,self.b
        assert cur['letter'] is not None and len(cur['processed'])==len(b.nets)
        assert not cur['applied']
        if self.enabled:
            weights,saved,increment = _selector(cur['weights'],cur['saved'],cur['issued'],cur['letter'],b.SHARE)
            b.w_def = weights[0]
            for j,n in enumerate(b.nets,1):
                if hasattr(n,'w') or weights[j] != 1.:
                    n.w = weights[j]
                if hasattr(n,'saved') or saved[j] != 0.:
                    n.saved = saved[j]
            b.pbits = cur['pbits']+increment
            self.counters['selector_weight_writes'] += 1+sum(r.awake for r in cur['issued'][1:])
            self.counters['selector_saved_writes'] += sum(r.awake for r in cur['issued'][1:])
            self.counters['pbits_writes'] += 1
            best,bs = None,0
            for n in b.nets:
                score=n.agree-4*n.dis
                if n.E >= b.bar and (best is None or score>bs):
                    best,bs=n,score
            b.best=best
        cur['applied']=True
        self.counters['completed_accepted_updates'] += 1

    def _wrap_brain(self):
        b=self.b
        original_predict,original_taste=b.predict,b.taste
        def predict():
            cur=self.current
            if cur is not None and cur['letter'] is not None and not cur['applied']:
                self._apply_scores()
            assert self.issuing is None
            records=[self._default()]+[None]*len(b.nets)
            weights=[getattr(b,'w_def',1.)]+[getattr(n,'w',1.) for n in b.nets]
            self.issuing=records
            try:
                answer=original_predict()
            finally:
                self.issuing=None
            assert all(r is not None for r in records), 'Prediction did not ask each stream'
            num=weights[0]*records[0].p1
            den=weights[0]
            for j,r in enumerate(records[1:],1):
                if r.awake:
                    num+=weights[j]*r.p1
                    den+=weights[j]
            error=abs(num/den-b.p1)
            self.max_reconstruction_error=max(self.max_reconstruction_error,error)
            assert error<=1e-12, ('Issued prediction reconstruction',error)
            self.last=tuple(records)
            self.frame_time=float(b.t)
            self.counters['predict_calls'] += 1
            self.counters['forecast_records_written'] += len(records)
            self.counters['forecast_scalar_fields_written'] += 4*len(records)+1
            self.counters['awake_stream_forecasts'] += sum(r.awake for r in records[1:])
            return answer
        def taste(value,at):
            assert self.current is None
            end=b.t
            b.t=end+at
            try:
                entry=[self._default()]
                for n in b.nets:
                    k,_=n.says(b.place(n)-1)
                    entry.append(self._record(n,k))
                now=float(b.t)
            finally:
                b.t=end
            issued=self.last
            mismatch=0
            if issued is None:
                self.counters['tastes_without_prior_forecast'] += 1
            else:
                assert self.frame_time<=now+1e-12, 'Issued forecast follows taste'
                mismatch=sum(a!=c for a,c in zip(issued,entry))
                self.counters['issued_entry_record_mismatches'] += mismatch
                self.counters['tastes_with_issued_entry_mismatch'] += int(bool(mismatch))
                weights=[getattr(b,'w_def',1.)]+[getattr(n,'w',1.) for n in b.nets]
                def mix(records):
                    use=[j for j,r in enumerate(records) if r.awake]
                    return sum(weights[j]*records[j].p1 for j in use)/sum(weights[j] for j in use)
                difference=abs(mix(issued)-mix(entry))
                self.max_issued_entry_probability_difference=max(self.max_issued_entry_probability_difference,difference)
            cur=dict(t=now,issued=issued,letter=None,processed=set(),applied=False,
                     stats=[(n.E,n.agree,n.dis) for n in b.nets],
                     weights=[getattr(b,'w_def',1.)]+[getattr(n,'w',1.) for n in b.nets],
                     saved=[0.]+[getattr(n,'saved',0.) for n in b.nets],pbits=getattr(b,'pbits',0.))
            before=getattr(b,'ntaste',0)
            self.current=cur
            try:
                answer=original_taste(value,at)
            finally:
                self.current=None
            accepted=cur['letter'] is not None
            assert getattr(b,'ntaste',0)-before==int(accepted)
            assert not accepted or cur['applied'], 'No prediction after accepted feedback'
            self.counters['taste_calls'] += 1
            self.counters['accepted_tastes'] += int(accepted)
            self.counters['accepted_tastes_with_issued_entry_mismatch'] += int(accepted and bool(mismatch))
            self.counters['accepted_issued_entry_record_mismatches'] += mismatch if accepted else 0
            self.counters['taste_entry_stream_reads'] += len(b.nets)
            return answer
        b.predict,b.taste=predict,taste

    def summary(self):
        return dict(enabled=self.enabled,counters=dict(self.counters),
                    max_reconstruction_error=self.max_reconstruction_error,
                    max_issued_entry_probability_difference=self.max_issued_entry_probability_difference,
                    cache_records=0 if self.last is None else len(self.last),
                    cache_record_fields=['speaker_id','hard_choice','exact_p0','exact_p1'],
                    persistent_cache_scalar_slots=0 if self.last is None else 4*len(self.last)+1,
                    transient_taste_state_fields=['issued_reference','t','letter','processed_streams','applied',
                                                 'entry_E_agree_dis','entry_weights','entry_saved','entry_pbits'])


def install(lf,enabled=True):
    return IssuedCredit(lf,enabled)

"""D174: calibration opportunities in actual sensory histories. Robot lives (creature.Life, the designed-circuit brain,
unchanged body, world and interface) with a logging wrapper around the brain: every stimulate(sensor, at) and taste.
Counts what a two-input timing detector on the robot's only two sensors would see: activity onsets (a pulse after
>= QUIET s of silence on that sensor) paired across sensors by their separation: simultaneous (<= 10 ms, the anchor
analogue), near (10-150 ms), far (150-600 ms); single-sensor onsets; and how taste pulses sit against sensor pulses.
Analyst accounting only: no brain sees these labels. python census.py <lives> <seconds> [brain]
"""
import json,sys,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from creature import Life,BRAINS
from units import TICK
OUT=ROOT/'lab/v/robot_opportunities_20261120';QUIET=.25;BRAIN='designed-circuit'

class Logger:
    def __init__(self,seed):
        self.inner=BRAINS[BRAIN](seed);self.t=0.;self.pulses=[];self.tastes=[]
    def stimulate(self,sensor,at):self.pulses.append((self.t+at,int(sensor)));return self.inner.stimulate(sensor,at)
    def taste(self,value,at):self.tastes.append((self.t+at,float(value)));return self.inner.taste(value,at)
    def step(self):
        r=self.inner.step();self.t+=TICK;return r
    def drive(self,s):return self.inner.drive(s)

def onsets(times):
    times=np.sort(times);gaps=np.diff(np.concatenate([[-1e9],times]));return times[gaps>=QUIET]

def classify(o0,o1):
    out=dict(simultaneous=0,near=0,far=0);used0=set();used1=set()
    for i,a in enumerate(o0):
        if len(o1)==0:break
        j=int(np.argmin(np.abs(o1-a)));d=abs(o1[j]-a)
        if d<=.01:out['simultaneous']+=1;used0.add(i);used1.add(j)
        elif d<=.15:out['near']+=1;used0.add(i);used1.add(j)
        elif d<=.6:out['far']+=1;used0.add(i);used1.add(j)
    out['single']=len(o0)-len(used0)+len(o1)-len(used1);return out

def main():
    global BRAIN
    lives,seconds=int(sys.argv[1]),float(sys.argv[2]);BRAIN=sys.argv[3] if len(sys.argv)>3 else BRAIN;rows=[];start=time.monotonic()
    for i in range(lives):
        seed=i//2;poison=('red','blue')[i%2];holder={}
        def make(s):holder['b']=Logger(s);return holder['b']
        life=Life(seed,poison,True,make);n=int(round(seconds/TICK))
        while life.t<n:life.step()
        b=holder['b'];p=np.array(b.pulses) if b.pulses else np.zeros((0,2));tt=np.array([x[0] for x in b.tastes])
        o0=onsets(p[p[:,1]==0,0]);o1=onsets(p[p[:,1]==1,0]);cl=classify(o0,o1)
        moving=life.moving*TICK if life.moving is not None else None
        # taste against sensor pulses: any pulse of either sensor within 10 ms of the taste; last pulse lead time
        near_taste=sum(bool(len(p) and np.min(np.abs(p[:,0]-x))<=.01) for x in tt)
        lead=[float(x-p[p[:,0]<x,0].max()) for x in tt if np.any(p[:,0]<x)]
        both=0;both_s=0.
        rows.append(dict(seed=seed,poison=poison,seconds=seconds,moving_s=moving,pulses=[int((p[:,1]==0).sum()),int((p[:,1]==1).sum())],
            onsets=[len(o0),len(o1)],pairs=cl,tastes=len(tt),food=sum(1 for _,c in life.meals if c!=poison),poison_eaten=sum(1 for _,c in life.meals if c==poison),
            tastes_with_sensor_pulse_within_10ms=int(near_taste),taste_lead_median_s=float(np.median(lead)) if lead else None))
        print(json.dumps(rows[-1]),round(time.monotonic()-start,1),flush=True)
    with (OUT/f'census_{BRAIN}_{lives}x{int(seconds)}s.json').open('x') as f:json.dump(dict(quiet_s=QUIET,brain=BRAIN,rows=rows),f,indent=1)
if __name__=='__main__':main()

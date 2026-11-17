"""D73: localise why a replay of pre-taste predictions differs from the actual weight update."""
from pathlib import Path
import pickle
import numpy as np

with (Path(__file__).parent / "v/noisy_path_audit.pkl").open("rb") as f:
    data=pickle.load(f)
for life in data["lives"]:
    failures=[]
    for j,(r,nxt) in enumerate(zip(life["rows"],life["rows"][1:])):
        w=r["weights"].copy()
        on=np.isfinite(r["q"])
        z=r["inferred_eye"] ^ int(r["value"]<0)
        if r["vouched"]:
            total=w[on].sum()
            likelihood=np.where(z,r["q"][on],1-r["q"][on])
            pm=w[on]@likelihood/total
            w[on]*=likelihood/pm
            if on.sum()>1:
                w[on]=.99*w[on]+.01*total/on.sum()
        error=w-nxt["weights"]
        if np.max(np.abs(error))>1e-8:
            failures.append(j)
            if len(failures)==1:
                print(life["seed"],life["first"],"first differing update",j,"t",r["t"],"vouched",r["vouched"])
                for i in np.argsort(-np.abs(error))[:5]:
                    print(life["names"][i],"q",r["q"][i],"before",r["weights"][i],"expected",w[i],"actual",nxt["weights"][i])
    print("differing updates",len(failures),"/",len(life["rows"])-1)

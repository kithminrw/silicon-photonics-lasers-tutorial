"""Width sweep of 220 nm SOI strip waveguides with femwell; writes figsrc/ch06_sweep.json.
Run: .venv/bin/python figsrc/ch06_sweep.py   (about 10 minutes)"""
import json, os
import numpy as np
from femwell_modes import modes, ng
out = {"widths": [], "neff1550": [], "neff1310": [], "ng_te1550": [], "ng_tm1550": [], "ng_te1310": []}
for w in np.round(np.arange(0.25, 1.001, 0.05), 3):
    m15 = modes(w, 1.55, num=5, res=0.03); m13 = modes(w, 1.31, num=5, res=0.03)
    out["widths"].append(float(w)); out["neff1550"].append(m15); out["neff1310"].append(m13)
    out["ng_te1550"].append(ng(w, 1.55, "TE", res=0.03)[1]); out["ng_tm1550"].append(ng(w, 1.55, "TM", res=0.03)[1])
    out["ng_te1310"].append(ng(w, 1.31, "TE", res=0.03)[1])
    print(w, m15[:3], out["ng_te1550"][-1], flush=True)
json.dump(out, open(os.path.join(os.path.dirname(__file__), "ch06_sweep.json"), "w"), indent=1)
print("done")

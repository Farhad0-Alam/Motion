"""Run the order's overlay engine (pyc) on the Muse timeline. CLI as the engine: [--no-subs] | [--preview ts outdir]."""
import json
import marshal
import os

import numpy as np

PYC = "/root/Motion/shwbster_order/opening_edit/__pycache__/overlays_full_480s.cpython-312.pyc"
TL = json.load(open("/root/Motion/muse_version/timeline.json"))

code = marshal.loads(open(PYC, "rb").read()[16:])
ns = {"__name__": "overlays_full_480s", "__file__": "/root/Motion/shwbster_order/opening_edit/overlays_full_480s.py"}
exec(code, ns)

a480, am = (np.array(x) for x in TL["anchors"])


def g(t):
    return float(np.interp(t, a480, am, left=t * am[0] / a480[0]))


ev = sorted(ns["GRAPHIC_EVENTS"], key=lambda e: e[0])
out = []
for i, (a, b, x, y, fn) in enumerate(ev):
    na, nb = g(a), g(b)
    if i + 1 < len(ev):
        nb = min(nb, g(ev[i + 1][0]) - 0.25)
    out.append((na, max(nb, na + 2.5), x, y, fn))
ns["GRAPHIC_EVENTS"] = out
ns["SUB_CUES"] = TL["subs"]
ns["SHOT_LOG"] = TL["shots"]
ns["TOTAL_FRAMES"] = 9303
ns["main"]()

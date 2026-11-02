"""Run the overlay engine against the v2 re-timed shot list.

overlays_full_480s.py was truncated to 0 bytes on disk; the only surviving copy of the engine is
__pycache__/overlays_full_480s.cpython-312.pyc (Python 3.12). This loads that bytecode, swaps in
assets/timeline_v2.json as SHOT_LOG (per-shot location labels follow the new cuts), and calls
its main() with the same CLI: [--no-subs] | [--preview ts1,ts2 outdir].
"""
import json
import marshal
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PYC = os.path.join(HERE, "__pycache__", "overlays_full_480s.cpython-312.pyc")
TIMELINE = "/root/Motion/shwbster_order/assets/timeline_v2.json"

code = marshal.loads(open(PYC, "rb").read()[16:])
ns = {"__name__": "overlays_full_480s", "__file__": os.path.join(HERE, "overlays_full_480s.py")}
exec(code, ns)
ns["SHOT_LOG"] = json.load(open(TIMELINE))
ns["main"]()

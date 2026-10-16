#!/usr/bin/env python3
"""Writes out/<name>.svg copies with the brand fonts embedded (base64), so a
downloaded SVG looks the same anywhere without the project's font files."""
import base64, os, re
here = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(here, "out"), exist_ok=True)
for name in sorted(os.listdir(here)):
    if not name.endswith(".svg"):
        continue
    svg = open(os.path.join(here, name), encoding="utf-8").read()
    def embed(m):
        path = os.path.normpath(os.path.join(here, m.group(1)))
        data = base64.b64encode(open(path, "rb").read()).decode()
        return f'url("data:font/woff2;base64,{data}")'
    svg = re.sub(r'url\("(\.\./assets/fonts/[^"]+\.woff2)"\)', embed, svg)
    out = os.path.join(here, "out", name)
    open(out, "w", encoding="utf-8").write(svg)
    print(f"{out}: {os.path.getsize(out) // 1024} KB")

"""Inline the locked Stoop geometry and wordmark into ../index.html.

stoop.json (centreline, stroke width, dot) and wordmark.d come from
/root/ClientFalcon/backend/brand-src (cf_final.mark, place(m, 1000, 0.86)) and
clientfalcon-lockup-night.svg. Edit endcard_template.html, then run this.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
g = json.load(open('stoop.json'))
wm = open('wordmark.d').read()
arc_frac = g['L_arc'] / g['L_all']
cx, cy, r = g['dot']
html = open('endcard_template.html').read()
html = (html.replace('{{STOOP_D}}', g['d']).replace('{{STOOP_W}}', str(g['W']))
            .replace('{{DOT_CX}}', str(cx)).replace('{{DOT_CY}}', str(cy)).replace('{{DOT_R}}', str(r))
            .replace('{{ARC_LEFT}}', f'{1 - arc_frac:.4f}').replace('{{WORDMARK_D}}', wm)
            .replace('{{GLOW_X}}', f'{cx/1000*252-280:.1f}').replace('{{GLOW_Y}}', f'{cy/1000*252-280:.1f}'))
open(os.path.join(HERE, '..', 'index.html'), 'w').write(html)
print('arc fraction', round(arc_frac, 4))

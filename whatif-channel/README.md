# What-If channel (working name: Pebbletown)

Faceless 7–9 minute "What if…?" explainers told with a recurring cast of cut-paper **pebble people**.
The format is modelled on channels like *Awaken* (@Afterimath): a big hypothetical question, a narrator, and one
still per 4–5 seconds with slow camera moves. Our art, characters and scripts are our own. We don't copy their
black-silhouette characters or their titles.

| Path | What it holds |
|---|---|
| [plan/channel-plan.md](plan/channel-plan.md) | Format, what makes it work, rules, topic backlog |
| [plan/production.md](plan/production.md) | Step-by-step: script → images → voice → render → publish, with costs |
| [brand/style.txt](brand/style.txt) | Art style appended to every image prompt |
| [brand/cast.txt](brand/cast.txt) | Recurring characters (Pip, Momo); auto-inserted into prompts |
| [brand/fonts/](brand/fonts/) | Luckiest Guy (Apache 2.0) for thumbnails |
| [log.md](log.md) | Dated decisions |

Episodes are built in `../videos/<nn>-whatif-<slug>/` with the shared pipeline `../videos/lib/whatif.py`.

## Status (2026-10-31)
- Ep 1 *What if the Internet Disappeared for a Year?* (`../videos/06-whatif-internet-gone`) has a full script,
  93 scenes, image prompts and a thumbnail. A placeholder preview renders end to end.
- Next: generate the Pip and Momo reference sheets, then 93 scene images, then the voice (needs `GEMINI_API_KEY`).

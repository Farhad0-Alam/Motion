# Decision log

## 2026-10-31
- Started a what-if explainer channel modelled on the *Awaken* format (faceless "What if" stories, 7–8 min,
  stills with Ken Burns moves). Built in `/root/Motion`, kept separate from `iagentice-channel`.
- Own look: cut-paper "pebble people" (not black silhouettes with big white eyes). Cast: Pip and Momo.
- Pipeline: `videos/lib/whatif.py`. `scenes.txt` is the single source; Gemini TTS (`gemini-3.1-flash-tts-preview`,
  voice Iapetus) produces one clip per scene; ffmpeg zoompan renders each still; mastering is shared with `cartoon_sfx`.
- Ep 1 picked: *What if the Internet Disappeared for a Year?* 93 scenes, 1,151 words. Ends by teasing ep 2,
  *What if You Were the Only Person Still Online?*
- Working channel name "Pebbletown" is a placeholder. The user decides.
- User pointed out the reference channel animates its 2D characters, not just stills. Chosen approach: code-rigged
  characters in HyperFrames (pose(t) → SVG rig) over flat backgrounds. Test scene `videos/07-whatif-anim-test`
  (Pip walks to a cafe, phone dies, shrugs; 10 s, render ~1 min on 2 cores). Pending user review before folding
  the rig into the episode pipeline.
- User: story first, then animate from a storyboard. Wrote `videos/06-whatif-internet-gone/storyboard.md`
  (38 shots, 9 reusable sets, per-line action, action library). Waiting for story + storyboard approval before
  building sets and rig.

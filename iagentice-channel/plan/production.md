# Production

## Hook formula (from studying a high-performing cartoon short, first 5 s)
1. Frame 1 is already mid-action (bursting, falling, screaming). Never a calm establishing shot.
2. The key prop is visible from frame 1, so the viewer knows it will matter.
3. A chaotic or unexplained event raises a question ("what happened?").
4. A wordless reaction (glare, panic, smug side-eye) sets up the conflict.
5. Cut to a new shot size around 4–5 s to re-hook.
6. A visible "fuse" (a clock, a rising glow, a circling shadow) makes the viewer stay for the payoff.
The sound is never silent: every hit gets a sound.

## Clip lengths (Omni 1.1 Flash / Veo 3.1)
| Shot | Length | Why |
|---|---|---|
| Hook | 4 s | The model compresses the action, so it moves fastest |
| Story beat | 6 s | 3–4 beats without filler |
| One continuous action | 8 s | Only when the action needs the time |
| — | avoid 10 s | Slow pacing, more drift, 2.5× the cost of 4 s |
- 720p for finals (a 360p test does not carry over to 720p).
- x2 takes on hook shots, x1 elsewhere. Generating 6 s and trimming beats generating long.

## Shot-by-shot workflow
1. Write the second-by-second storyboard (`episodes/<slug>/storyboard.md`).
2. Generate the start image for shot 1 (Nano Banana) with character references attached.
3. Generate each shot image-to-video. **Start each shot from the previous shot's last frame** (I can extract it) unless the location changes.
4. Drop the clips in `episodes/<slug>/clips/` (or anywhere in the repo and say where).
5. I cut, sound-design and master in `../videos/<nn>-<slug>/build.py` (-14 LUFS, 720×1280, 24 fps) and add the end card.
6. Review page (claude.ai artifact) with a tap-to-jump cue list; notes go back into the build.

## Prompt templates
Style line (every prompt):
```
Single continuous shot, no cuts, static camera. Stylized 3D animated feature film, soft rounded cartoon characters, strong squash-and-stretch, fast snappy cartoon timing, no slow motion. Not photorealistic. Vertical 9:16.
```
Audio line (every prompt):
```
Audio: only the characters' own sounds (squeaks, gasps, grunts) and natural foley. No narrator, no voice-over, no dialogue, no music, no subtitles.
```
Beats go in timestamped lines, biggest moment first:
```
[00:00-00:01] <the hook action, already happening>
[00:01-00:02] ...
```
Image prompts: copy the character blocks word for word, describe the pose mid-action, end with
`AVOID: photorealistic, painterly look, extra characters, text, logos, watermark, multiple panels.`

## Lessons from the test episodes
- A narrator turns it into a "story-selling" video; keep it wordless.
- Camera moves into new spaces ("tilt up into the sky") invite the model to cut to a new scene; keep cameras static.
- Text rendered by the model is unreliable; all on-screen words (clocks, end cards) are added in editing.
- The model may restyle a character between shots (the chick turned grey); repeat the full character block and attach references.

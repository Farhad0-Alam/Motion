# How an episode gets made

Everything for an episode lives in one file, `scenes.txt`. Claude writes it. Every other step reads it.

```
cd /root/Motion/videos/<nn>-whatif-<slug>
python3 build.py prompts            # prompts.md + script.txt
python3 build.py tts                # assets/voice/NNN.wav  (export GEMINI_API_KEY=... first)
python3 build.py render --preview   # 720p check, ~fast
python3 build.py render             # 1080p final + .srt + chapters
python3 build.py thumb              # renders/thumb.png
```

| Step | Who | Notes |
|---|---|---|
| 1. Topic and research | Claude | Pick from the backlog. Collect the 5–10 real facts and record sources in `notes.md` |
| 2. `scenes.txt` | Claude | ~90–110 scenes. Each has one breath of VO (8–16 words), one picture, a camera move and an optional SFX cue |
| 3. Read-through | You | Read `script.txt` aloud. Fix anything that sounds like a robot |
| 4. Character sheets | Image tool | Top of `prompts.md`, once per character. Reuse them as references forever |
| 5. Scene images | Image tool | Paste each prompt and attach the sheets for named characters. Save as `assets/images/NNN.png`, 16:9 |
| 6. Voice | `build.py tts` | Gemini TTS, voice Iapetus, one clip per scene. Listen to the whole thing. Redo bad takes with `--only 017,018 --force` |
| 7. Music | You | Drop one calm, loopable track at `assets/music.mp3` (YouTube Audio Library, no attribution needed). It plays quietly under the voice |
| 8. Render | `build.py render` | Re-renders only the scenes whose image changed. Placeholder cards show which images are still missing |
| 9. Thumbnail | Image tool + `build.py thumb` | Generate art with no text as `assets/thumb.png`. The script adds the words |
| 10. Publish | You | Title, description, chapters and `.srt` from `notes.md`. Not made for kids |

## Image tools
- **Gemini image (`gemini-3.1-flash-image`, "Nano Banana")** keeps characters consistent with reference images
  and handles bulk prompting well. API image generation needs a paid key (the free tier has no image quota).
  The Gemini app or Flow works by hand.
- **Midjourney** (`--cref` / `--sref` with the character sheet) gives the strongest single images. It's all manual.
- Keep `brand/style.txt` the same from episode to episode. Changing it changes the look of the channel.

## Cost per episode (rough)
- ~95 images: covered by Gemini AI Pro or Midjourney Basic, otherwise about $4 by API.
- Voice: Gemini TTS preview costs pennies.
- Optional hero shots: 5–8 Veo or Omni clips of 6–8 s for the biggest moments (e.g. scenes 014, 083) at about $0.10/s, roughly $5.
  Save them as `assets/images/NNN.mp4`. *(Not wired yet; add when needed.)*

## Machine limits
Rendering runs on cores 0–1 only (`taskset`), 2 clips at a time, to keep the host under 50% CPU.

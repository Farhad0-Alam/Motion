# START HERE

A short brief for a new Claude session. Read this first, then open only the
files your task needs.

## What this repo is

Production workspace for the **iAgentice YouTube channel**: AI agents and
automation tutorials taught from iAgentice's own builds (https://iagentice.com).
It also holds brand print work.

- Channel: **iAgentice**, handle **@iAgentice**. The profile picture (logo) is set.
- Language: English first.
- Voice: ElevenLabs **Brian** (`nPczCjzI2devNBz1zQrb`) on model **`eleven_v4`**,
  with expression tags like `[curious]`.
- Fallback voice: Kokoro (free, local).

## Read only what you need

| Task | Read |
|---|---|
| New video idea or script | `docs/channel-plan.md`, `docs/videos/01-ai-receptionist/script.md` (example) |
| Monetization or policy question | `docs/youtube-monetization.md` |
| Build or render a video | `videos/01-ai-receptionist/build.py`, `src/template.html.in` (copy this project as the template) |
| Thumbnails | `videos/01-ai-receptionist/thumbnail/*.svg`, `export.sh` |
| Upload text (title, description, chapters) | `videos/01-ai-receptionist/UPLOAD.md` |
| Print work | `print/business-card/README.md` |
| Install the toolchain | `scripts/setup.sh` (run `npm run setup`) |

## Setup in a fresh container or VPS

1. `npm run setup`. Takes several minutes and installs:
   - HyperFrames 0.8.158, FFmpeg 9, Blender 5.2, Inkscape 1.4, ImageMagick 7
   - Whisper models, Kokoro, MusicGen, and fonts
2. The ElevenLabs key goes in the environment's network secrets, or in a
   git-ignored `.env` file as `ELEVENLABS_API_KEY=...`.
   **Never commit keys or paste them in chat.**
3. Run `npm run doctor`; all checks should pass.

Network needs: `huggingface.co`, `*.hf.co`, `cdn.jsdelivr.net` and
`api.elevenlabs.io` (or Full network access).

## Brand

- **Colours:**
  - background `#12171a`
  - text `#f3f6f1`
  - muted `#b9c3ba`
  - lime accent `#c8f04f` (focus only, 60-30-10 rule)
  - gold `#f0c05f`
  - violet `#9385ff`
  - red `#ff6b6b`
- **Fonts:** Instrument Sans (headings, UI) and IBM Plex Mono (labels).
  Files are in `videos/01-ai-receptionist/assets/fonts/`.
- **Logo:** the "A" mark with a lime dot, in `videos/01-ai-receptionist/assets/brand/icon.svg`.
- **Look:** dark "control room" HUD with mono labels like `[SCN.01 // NAME]`, a
  subtle grid, and the tagline "Work that never sleeps."
- **Mobile-first type scale** (1080p): 32 / 40 / 48 / 60 / 76 / 96 / 120 px.
  Never go below 32px. Captions are 60px, at most 5 words a line.

## Rules that keep the channel monetizable

- Each video needs its own script and its own visual structure. No template with
  only the text swapped.
- No AI avatar or fake "expert" persona. Explain things; don't give personal
  finance, health or legal advice.
- Captions: upload the generated `.srt`. Answer "AI use" honestly at upload.
- Music: use the YouTube Audio Library, or disclose AI music.

## Production habits learned so far

- **Draft cheaply:** time scripts with Kokoro, and spend ElevenLabs characters
  only on the final voice. The plan is pay-as-you-go at about 23.7k characters
  a period; a 3-minute video uses about 2.8k.
- **Voice levels:** `loudnorm` under-boosts clips shorter than about 3s, so level
  those by hand.
- **Fonts:** ImageMagick doesn't fall back to another font per glyph, so set one
  font per script.
- **Blender 5 video output:** set `media_type = "VIDEO"` before `file_format = "FFMPEG"`.
- **Checking work:** check stills with `hyperframes snapshot`, and check at phone
  size (about 480px wide) before rendering.
- **Render speed:** a full render takes about 5–7 minutes for 3 minutes of video
  on 4 CPUs.
- **4K:** `npx hyperframes render . --resolution 4k --quality delivery -o renders/<name>-4k.mp4`.
  The layout stays 1920×1080; Chrome renders at 2× pixel density, so the type
  scale above needs no changes. Check a still first with
  `hyperframes snapshot . --at <t> --zoom 0,0,1920,1080 --zoom-scale 2`.
- **Keep timings stable:** `build.py` reads MP3 lengths with ffprobe, and FFmpeg 6
  reports them about 40ms longer than FFmpeg 9 (EP.01 drifted 0.3s in total). To
  re-render an approved cut, keep the committed `index.html`/`timeline.json` and
  only regenerate the git-ignored audio (`*.norm.wav`, `music.wav`).

## Status (October 2026)

- **EP.01** "How an AI receptionist answers customers 24/7": done (v2, mobile
  redesign; 1080p and 4K renders). Thumbnails A/B/C, captions and upload package are ready.
  - Open: is "iAgentice" pronounced correctly?
  - Open: keep the MusicGen music, or swap in an Audio Library track?
- **Business card:** design done.
  - Waiting on real name, title, phone and email.
  - Waiting on size: US 3.5×2 in or 85×55 mm.
- **YouTube channel:** name, handle and picture are set. Still to do:
  - banner, 2560×1440, with key content inside the 1546×423 centre safe area
  - description
  - links
  - contact email
  - video watermark (150×150)
  - Home tab: trailer and sections
- **Next video:** EP.02 "the build, step by step" (promised at the end of EP.01).

## Git

- Default branch: `main`.
- Work branch so far: `claude/cool-cannon-2qn0m7`. Its pull request is
  https://github.com/Farhad0-Alam/Motion/pull/1, a draft.

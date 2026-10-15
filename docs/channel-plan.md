# Channel plan: AI agents & automation, built for real

Niche: business and software tutorials, focused on AI agents, automation and SaaS,
taught from real systems built by [iAgentice](https://iagentice.com/).
Policy rules are in [youtube-monetization.md](youtube-monetization.md).

## Why this niche

- **Original by default.** Videos come from real builds (ClientFalcon Voice,
  imknownas, YouTubeAI, Calendar Sync, 2TalkLink, partner projects). That is the
  "authentic insight" YouTube's inauthentic-content policy asks for.
- **High RPM.** B2B software and automation audiences are worth roughly $8–25 RPM
  for US English (estimate; varies by country, season and length).
- **Leads beat ads.** Each video points to iagentice.com. One partner build
  ($2.5k–15k+) outweighs a year of AdSense on a small channel.

## Content pillars

| Pillar | Example videos | Production |
|---|---|---|
| Explainers (animated) | How an AI receptionist answers WhatsApp 24/7; RAG explained in 5 minutes; Why we route between Claude, GPT and DeepSeek | Fully in HyperFrames: diagrams, motion graphics |
| Build-alongs | Build a lead-capture agent with n8n + Claude; Google Sheets → iCloud Calendar over CalDAV | Owner screen-records (OBS); we add callouts, captions, chapters, intro/outro |
| Case studies | What it costs to run an AI agent 24/7; Behind ClientFalcon: the architecture | Real numbers turned into charts and diagrams |
| Shorts | 30–60s tips cut from long videos | Vertical (1080x1920) versions of the same projects |

## Rules

- About 80% of each video teaches something useful on its own. Products appear
  where they fit; the channel must not read as an ad feed.
- One brand look (intro, outro, colours), but each video gets its own story,
  diagrams and examples. Never reuse a template with only the text swapped.
- No AI avatar or fake named "expert". Narration is the owner's voice, a clone of
  it, or a production voice (ElevenLabs) explaining, not giving personal advice.
- Music from the YouTube Audio Library or licensed; disclose AI music if used.
- Captions on every video (Whisper), chapters in the description, sources on screen.
- Answer the "AI use" setting honestly at upload.

## Voice

- ElevenLabs, most expressive model available on the plan (confirm the model id
  from the API; `ELEVENLABS_API_KEY` comes from `.env` or the environment's
  network secrets, never from the repo).
- The key must not be IP-restricted for cloud sessions; limit its scope to
  text-to-speech and voice read access instead.
- Kokoro (`npm run tts`) stays as the free fallback for drafts.

## First video

**"How an AI receptionist answers customers 24/7, explained"**, 3–5 minutes,
16:9, fully animated. It covers the architecture: website chat, WhatsApp,
knowledge base (RAG), and leads delivered to the owner's inbox. ClientFalcon is the
real example, and it ends with a call to action to iagentice.com.

## Open questions

- Channel name: "iAgentice" or a personal/engineering brand?
- Language: English first; Bengali version later?
- Brand assets: logo and colours from iagentice.com.

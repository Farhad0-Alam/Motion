# EP.01 upload package

Everything to paste into YouTube Studio for `renders/ep01-v2-4k.mp4` (the 4K
render; `renders/ep01-v2.mp4` is the same cut at 1080p).

## Title (pick one, 60 characters or fewer so it isn't cut off on mobile)

1. **How an AI Receptionist Answers Customers 24/7 (Explained)** ← recommended
   (57 characters; leads with the search phrase "AI receptionist")
2. AI Receptionist Explained: How It Answers Customers 24/7 (56)
3. How AI Answers Your Customers at 3 A.M. (AI Receptionist) (57)

The thumbnail text adds curiosity ("WHO ANSWERS?", "0 MISSED LEADS", "NEVER
SLEEPS") instead of repeating the title, so the two together say more than either alone.

## Thumbnails: A/B/C test

Upload all three in **YouTube Studio → video → Test & Compare**. YouTube
splits viewers between them and keeps the one with the most watch time.

| File | Hook | Psychology |
|---|---|---|
| `thumbnail/out/a-who-answers.jpg` | WHO ANSWERS? + 3:02 AM phone | Curiosity gap + a relatable pain |
| `thumbnail/out/b-zero-missed.jpg` | 0 MISSED LEADS | Outcome/benefit, speaks to owners |
| `thumbnail/out/c-never-sleeps.jpg` | AI RECEPTIONIST NEVER SLEEPS | Identity hook, echoes the brand tagline |

All three are 1280×720 JPG (YouTube's recommended size, well under the 2 MB limit):
- readable at the smallest size YouTube uses (168×94)
- nothing important under the bottom-right duration badge
- lime used only on the key word
- logo top-left for channel recognition

Edit the `.svg` files and run `thumbnail/export.sh` to re-export.

## Description

The first two lines show before "…more" and in search results, so they carry the
keyword and the hook.

```
It's 3 a.m. and a customer just messaged your business. Who answers? Here's exactly how an AI receptionist answers customers 24/7 on your website and WhatsApp, and turns those chats into leads.

In this video we break down the 4 parts of every AI receptionist (channels, the language model, the knowledge base / RAG, and actions), plus the 3-point checklist that separates a helpful AI receptionist from an annoying chatbot.

⏱ Chapters
0:00 It's 3 a.m. Who answers?
0:20 The problem: 40 hours open, 168 hours of messages
0:40 Part 1: Channels (web chat, voice, WhatsApp)
0:57 Part 2: The brain (language model)
1:17 Part 3: The knowledge base (RAG explained)
1:50 Part 4: Actions (leads to your inbox)
2:08 Good vs annoying: the checklist
2:33 Real example: ClientFalcon Voice

🔗 Want an AI receptionist for your business, or a custom AI agent?
https://iagentice.com

🤖 ClientFalcon Voice, AI voice and chat assistants for your website and WhatsApp:
https://clientfalcon.com

Next video: we build one, step by step. Subscribe so you don't miss it.

#AIReceptionist #AIAgents #BusinessAutomation
```

Chapter rules YouTube enforces: the first starts at 0:00, there are at least 3, and
each is 10 seconds or longer. All are met; times match the v2 render.

## Settings

| Setting | Value |
|---|---|
| Category | Science & Technology |
| Language / caption language | English |
| Captions | Upload `captions.en.srt` (exact script, word-timed), not auto-captions |
| Tags (minor ranking signal) | AI receptionist, AI chatbot for business, WhatsApp AI assistant, AI customer service, RAG explained, retrieval augmented generation, AI agents, business automation, AI lead generation, ClientFalcon, iAgentice |
| Altered or synthetic content ("AI use") | **Yes**: the narration is an AI voice. Disclosing doesn't affect reach or earnings (YouTube's own wording), and it keeps us safe. |
| Paid promotion | No (own product; no third party paid) |
| Made for kids | No |
| End screen (last 7 s) | Left dashed slot → "Video" element (best for viewer, or the next episode); right → "Subscribe" element over the lime button |
| Cards | At ~2:33 (ClientFalcon) → link card to the build video once it exists |
| Playlist | "AI Agents Explained", create it now so future episodes join |

## Pinned comment

```
What's the #1 question your customers ask after hours? Drop it below and we'll show how an AI receptionist would answer it in a future video.
```

(A question in the pinned comment drives early replies, and engagement in the first hours
helps the video get tested with more viewers.)

## After publishing

- In the first 48 hours, watch **click-through rate (CTR)** and **average view duration**
  in Studio → Analytics → Reach.
- Let Test & Compare finish before judging the thumbnails (YouTube reports a winner
  by watch time, usually within about 2 weeks).
- If CTR is low but retention is good: the packaging is the problem; try a new
  thumbnail or title. If retention drops early: tighten the first 20 seconds of the next video.

# After Hours #1: Plumber, "The Bucket"

| | |
|---|---|
| Series | [After Hours](../../series/after-hours/README.md) (ClientFalcon Voice) |
| Runtime | 30 s for Veo 3.1 (clips 4 + 4 + 8 + 6 + 6 s, shot 4 cut to 5 s, + 3 s end card) |
| Audience | US plumbing and trade business owners |
| Owner's pain | Pipes burst at 2 AM; whoever answers first gets the job |
| Main cast | **Doug** (owner, bear), **Ember** (the coral helper in Doug's website chat), **Rex** (rival, raccoon) |
| Guest | **Miso**, a plump grey tabby cat in striped pajamas |
| Status | Rewritten 2026-10-19 for the recurring cast; next: lineup image, then shot 1 |
| Build | `videos/06-after-hours-plumber/build.py` (not started) |

## Logline
At 2:47 AM a pipe bursts in Miso's kitchen. Miso calls Rex; Rex stuffs his ringing phone under his pillow and keeps snoring. Miso types into Doug's website chat instead: Ember pops out, takes the details and zips off with them. At 7:00 AM Doug wakes to the "New lead" email, calls back and fixes it in one twist, just as Rex's van rolls up too late.

## The jokes
- **Hook:** Miso's teacup-sized bucket fills in one second.
- **Rex's fail:** he silences a customer in his sleep, smug even while unconscious.
- **Payoff:** Miso tips Doug with the full tiny bucket, and Doug sips it like an espresso, pinky out.
- **Button (every episode):** Rex arrives too late, sees Doug and sulks.

## Product beat (what the viewer must understand)
1. The rival who relies on his phone loses the job.
2. Doug's **website chat** answers at once. Ember takes Miso's details and carries them to Doug as an envelope (the email).
3. At 7:00 AM Doug has **"New lead: Miso (Doug's Plumbing)"** from ClientFalcon Voice. He calls back himself and wins the job.

## Honesty check (plan/rules.md)
- [x] Ember only lives in the website chat. Miso's phone call goes to *Rex*; nothing answers a call for Doug.
- [x] No booking: Ember takes details and delivers them. Doug calls back himself.
- [x] No repair advice: Ember doesn't touch the pipe or tell Miso what to do.
- [x] Email overlay matches the real lead alert (sender "ClientFalcon Voice", subject `New lead: <name> (<assistant>)`, "Looking for" row).
- [x] No stats or reviews; phone number in the fictional 555-01xx range.

## Overlays and audio (post)
- Clock tags in IBM Plex Mono: **2:47 AM** (Night `#9385FF`), **7:00 AM** (Dawn `#F7A63B`).
- A short chat card over shot 3, then the email notification over shot 4 (HyperFrames, ClientFalcon tokens).
- SFX from `videos/lib/cartoon_sfx.py`: voicemail beep and snore for Rex; Ember's pop, chirps and whoosh; the wrench ratchet. Night motif, dawn chime, `endcard_sting()`.
- End card: `videos/endcard-clientfalcon` (approved). Ember's coral dot is the logo's dot, so the end card closes the loop.

## Upload
- Title options: *Plumbers, this is your 2:47 AM* · *He let the call ring. Big mistake.* · *Your competitor is asleep. Are you?*
- Playlists: Doug vs Rex, Plumbers.
- Audience: not made for kids (the jokes are about lost jobs and rivals).

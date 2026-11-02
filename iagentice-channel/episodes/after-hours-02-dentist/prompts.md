# Prompts: After Hours #2, "The Cheek" (dentist)

**Order of work:** character refs first (Nano Banana), then each shot's start image with the refs attached, then image-to-video. Every shot is a new shot size, so each gets a new start image; also attach the previous shot's last frame when the set is the same. Takes: shot 1 ×2, the rest ×1, 720p. Clips go in `clips/` as `s1a.mp4`, `s1b.mp4`, `s2.mp4`…

| Shot | Clip length | Start image | Takes |
|---|---|---|---|
| 1 | **4 s** | new | 2 |
| 2 | **6 s** | new (+ last frame of 1) | 1 |
| 3 | **6 s** (keep 5) | new (+ last frame of 2) | 1 |
| 4 | **6 s** (keep 5) | new | 1 |
| 5 | **6 s** (keep 5) | new | 1 |

**Pip's cheek is the fuse.** Use the matching PIP line in each prompt: "swollen" (shots 1–3, bigger each time) or "normal" (shot 5).

## Shared blocks (paste word for word)

```
STYLE: high-end stylized 3D animated feature film look, soft rounded cartoon characters with big expressive eyes, strong squash-and-stretch posing, soft global illumination, gentle rim light, shallow depth of field. Not photorealistic. Vertical 9:16.
```
```
PIP: a small, round chipmunk with rusty-orange fur, a cream belly, black-and-white stripes down his back and across his eyes, big glossy dark eyes, a tiny pink nose and a fluffy tail; wears a mint-green nightshirt with white buttons.
```
- Swollen (shots 1–3): `His RIGHT cheek is swollen into a huge, smooth, shiny balloon, as big as his whole head; his left cheek is normal.`
- Normal (shot 5): `Both of his cheeks are normal, small and neat.`
```
DR. HILDA: a big, gentle hippo dentist with soft lilac-grey skin, rosy cheeks, small round ears, round tortoiseshell glasses and a huge friendly smile with gleaming white teeth.
```
- At home (shot 4): `She wears a fluffy peach bathrobe.`
- At work (shot 5): `She wears lavender dental scrubs.`
```
TREE HOME AT NIGHT: a cosy one-room home inside a hollow tree at night. Curved wooden walls with tree-ring grain, a tiny bed with a patchwork quilt, a nightstand with a glass jar of walnuts, shelves of acorn jars, an acorn-shaped lamp with warm light, a round window with a cushioned window seat. Through the round window, across a moonlit street, a small dental office with a glowing sign shaped like a plain white tooth (no letters). Warm lamp light inside, cool blue moonlight outside.
```
```
SCREEN RULE: any phone screen faces away from the camera; only its glow on the face is visible. No text, letters, numbers or logos anywhere in the frame.
```
```
AVOID: photorealistic, painterly look, extra characters, text, letters, numbers, logos, watermark, readable screens, multiple panels.
```

## Character reference sheets

**Pip** (make the normal-cheek sheet; the swelling is prompted per shot)
```
Character reference sheet of one character, shown twice side by side: front view and three-quarter view, standing in a neutral friendly pose, full body with the fluffy tail visible, plain light-grey background, even soft studio light.
PIP: a small, round chipmunk with rusty-orange fur, a cream belly, black-and-white stripes down his back and across his eyes, big glossy dark eyes, a tiny pink nose and a fluffy tail; wears a mint-green nightshirt with white buttons. Both of his cheeks are normal, small and neat.
STYLE: high-end stylized 3D animated feature film look, soft rounded cartoon characters with big expressive eyes, strong squash-and-stretch posing, soft global illumination, gentle rim light, shallow depth of field. Not photorealistic.
AVOID: photorealistic, painterly look, extra characters, text, letters, numbers, logos, watermark, multiple panels beyond the two views.
```

**Dr. Hilda** (two outfits: make the sheet twice, once per outfit line)
```
Character reference sheet of one character, shown twice side by side: front view and three-quarter view, standing in a neutral friendly pose with a big smile, full body, plain light-grey background, even soft studio light.
DR. HILDA: a big, gentle hippo dentist with soft lilac-grey skin, rosy cheeks, small round ears, round tortoiseshell glasses and a huge friendly smile with gleaming white teeth. She wears lavender dental scrubs.
STYLE: high-end stylized 3D animated feature film look, soft rounded cartoon characters with big expressive eyes, strong squash-and-stretch posing, soft global illumination, gentle rim light, shallow depth of field. Not photorealistic.
AVOID: photorealistic, painterly look, extra characters, text, letters, numbers, logos, watermark, multiple panels beyond the two views.
```

---

## Shot 1: hook (4 s)

**Start image**
```
STYLE: high-end stylized 3D animated feature film look, soft rounded cartoon characters with big expressive eyes, strong squash-and-stretch posing, soft global illumination, gentle rim light, shallow depth of field. Not photorealistic. Vertical 9:16.
TREE HOME AT NIGHT: a cosy one-room home inside a hollow tree at night. Curved wooden walls with tree-ring grain, a tiny bed with a patchwork quilt, a nightstand with a glass jar of walnuts, shelves of acorn jars, an acorn-shaped lamp with warm light, a round window with a cushioned window seat. Through the round window, across a moonlit street, a small dental office with a glowing sign shaped like a plain white tooth (no letters). Warm lamp light inside, cool blue moonlight outside.
PIP: a small, round chipmunk with rusty-orange fur, a cream belly, black-and-white stripes down his back and across his eyes, big glossy dark eyes, a tiny pink nose and a fluffy tail; wears a mint-green nightshirt with white buttons. His RIGHT cheek is swollen into a huge, smooth, shiny balloon, as big as his whole head; his left cheek is normal.
Medium-wide shot, static, camera at bed height. PIP sits bolt upright in the tiny bed under the patchwork quilt, eyes squeezed in pain, pressing a frosty white bag of frozen peas against his giant swollen right cheek with both paws; the cheek is so heavy his whole body leans to the right. On the nightstand: the glass jar of walnuts and a phone with a coral-orange case, its screen facing down, edges glowing. The round window behind him shows the glowing white tooth-shaped sign across the street.
SCREEN RULE: any phone screen faces away from the camera; only its glow on the face is visible. No text, letters, numbers or logos anywhere in the frame.
AVOID: photorealistic, painterly look, extra characters, text, letters, numbers, logos, watermark, readable screens, multiple panels.
```

**Video prompt** (image-to-video, 4 s)
```
Single continuous shot, no cuts, static camera. Stylized 3D animated feature film, soft rounded cartoon characters, strong squash-and-stretch, fast snappy cartoon timing, no slow motion. Not photorealistic. Vertical 9:16.
Night, inside a cosy hollow-tree bedroom. PIP, a small chipmunk in a mint nightshirt, sits up in bed pressing a frosty bag of frozen peas to his right cheek, which is swollen into a huge shiny balloon.
[00:00-00:01] The swollen cheek inflates one more notch with a rubbery stretch; Pip winces and presses the peas harder.
[00:01-00:02] The bag of peas instantly melts and sags, steaming; soggy green peas dribble down his nightshirt.
[00:02-00:03] The heavy cheek tips Pip sideways and he topples off the edge of the bed with a squash on landing.
[00:03-00:04] Pip pops back up over the edge of the bed, one eye squinting, and glares furiously at the jar of walnuts on the nightstand.
The tooth-shaped sign keeps glowing through the round window behind him. Any phone screen faces away from the camera. No text, letters or numbers anywhere.
Audio: only the characters' own sounds (squeaks, gasps, grunts) and natural foley. No narrator, no voice-over, no dialogue, no music, no subtitles.
```

---

## Shot 2: the office goes dark (6 s)

**Start image** (attach the Pip ref and the last frame of shot 1)
```
STYLE: high-end stylized 3D animated feature film look, soft rounded cartoon characters with big expressive eyes, strong squash-and-stretch posing, soft global illumination, gentle rim light, shallow depth of field. Not photorealistic. Vertical 9:16.
TREE HOME AT NIGHT: a cosy one-room home inside a hollow tree at night. Curved wooden walls with tree-ring grain, a tiny bed with a patchwork quilt, a nightstand with a glass jar of walnuts, shelves of acorn jars, an acorn-shaped lamp with warm light, a round window with a cushioned window seat. Through the round window, across a moonlit street, a small dental office with a glowing sign shaped like a plain white tooth (no letters). Warm lamp light inside, cool blue moonlight outside.
PIP: a small, round chipmunk with rusty-orange fur, a cream belly, black-and-white stripes down his back and across his eyes, big glossy dark eyes, a tiny pink nose and a fluffy tail; wears a mint-green nightshirt with white buttons. His RIGHT cheek is swollen into a huge, smooth, shiny balloon, as big as his whole head; his left cheek is normal.
Medium close shot from inside, looking past Pip toward the round window. PIP kneels on the window seat, his giant swollen right cheek squished flat against the window glass, holding the coral phone to his left ear with the screen facing away, looking hopefully out of the window. Across the moonlit street, the small dental office and its glowing white tooth-shaped sign are clearly visible, framed in the round window. Damp pea stains on his nightshirt.
SCREEN RULE: any phone screen faces away from the camera; only its glow on the face is visible. No text, letters, numbers or logos anywhere in the frame.
AVOID: photorealistic, painterly look, extra characters, text, letters, numbers, logos, watermark, readable screens, multiple panels.
```

**Video prompt** (image-to-video, 6 s)
```
Single continuous shot, no cuts, static camera. Stylized 3D animated feature film, soft rounded cartoon characters, strong squash-and-stretch, fast snappy cartoon timing, no slow motion. Not photorealistic. Vertical 9:16.
Night. PIP, a small chipmunk with a hugely swollen right cheek, kneels at a round window with his cheek squished against the glass and a phone at his ear. Across the street, a dental office has a glowing tooth-shaped sign.
[00:00-00:01] Pip listens to the phone hopefully, watching the glowing tooth sign across the street.
[00:01-00:02] The tooth sign flickers twice and switches off; the office across the street goes dark; Pip's face falls.
[00:02-00:03] Pip tries to speak into the phone but his swollen cheek only lets out a muffled "mmf-mmmf" with no real words; he flaps one paw in frustration.
[00:03-00:04] The swollen cheek inflates one more notch with a rubbery stretch, pushing his ear up; he winces.
[00:04-00:05] Pip gets an idea, pulls the phone away from his ear and starts tapping the screen fast with one claw.
[00:05-00:06] Warm coral-orange light from the phone fills his face; his good eye goes big and hopeful.
The phone screen always faces away from the camera. No text, letters or numbers anywhere.
Audio: only the characters' own sounds (squeaks, gasps, muffled wordless mumbling) and natural foley. No narrator, no voice-over, no dialogue, no real words, no music, no subtitles.
```

---

## Shot 3: the chat answers (6 s, keep 5)

**Start image** (attach the Pip ref and the last frame of shot 2)
```
STYLE: high-end stylized 3D animated feature film look, soft rounded cartoon characters with big expressive eyes, strong squash-and-stretch posing, soft global illumination, gentle rim light, shallow depth of field. Not photorealistic. Vertical 9:16.
PIP: a small, round chipmunk with rusty-orange fur, a cream belly, black-and-white stripes down his back and across his eyes, big glossy dark eyes, a tiny pink nose and a fluffy tail; wears a mint-green nightshirt with white buttons. His RIGHT cheek is swollen into a huge, smooth, shiny balloon, as big as his whole head; his left cheek is normal.
Close-up, Pip fills the lower two-thirds of the frame, the upper third is soft dark wood wall and the round window with the now-dark office across the street. PIP sits on the cushioned window seat holding the coral phone in both paws, screen facing away from the camera, typing with one claw, wincing, his giant swollen cheek resting on his shoulder. The phone's warm coral-orange glow lights his face from below; cool blue moonlight from the window on his back.
SCREEN RULE: any phone screen faces away from the camera; only its glow on the face is visible. No text, letters, numbers or logos anywhere in the frame.
AVOID: photorealistic, painterly look, extra characters, text, letters, numbers, logos, watermark, readable screens, multiple panels.
```

**Video prompt** (image-to-video, 6 s)
```
Single continuous shot, no cuts, static camera. Stylized 3D animated feature film, soft rounded cartoon characters, strong squash-and-stretch, fast snappy cartoon timing, no slow motion. Not photorealistic. Vertical 9:16.
Close-up at night. PIP, a small chipmunk with a hugely swollen right cheek, sits on a window seat holding a phone with a coral case; the screen faces away and its warm coral glow lights his face.
[00:00-00:01] Pip types with one claw, wincing at every tap.
[00:01-00:02] The coral glow pulses brighter; his good ear perks straight up.
[00:02-00:03] He nods and types again; the swollen cheek wobbles like jelly.
[00:03-00:04] The glow pulses once more; he lets out a long, squeaky, whistling sigh of relief.
[00:04-00:06] He curls up on the window seat hugging the phone, lays his head on his giant cheek like a pillow and falls asleep instantly with a tiny snore.
The phone screen always faces away from the camera. No text, letters or numbers anywhere.
Audio: only the characters' own sounds (squeaks, sighs, a tiny snore) and natural foley. No narrator, no voice-over, no dialogue, no music, no subtitles.
```

---

## Shot 4: 7:00 AM (6 s, keep 5)

**Start image** (attach the Dr. Hilda ref)
```
STYLE: high-end stylized 3D animated feature film look, soft rounded cartoon characters with big expressive eyes, strong squash-and-stretch posing, soft global illumination, gentle rim light, shallow depth of field. Not photorealistic. Vertical 9:16.
BATHROOM AT DAWN: a pastel pink-and-white tiled bathroom at sunrise, a big round mirror, a white sink counter, warm orange sunrise light through a frosted window.
DR. HILDA: a big, gentle hippo dentist with soft lilac-grey skin, rosy cheeks, small round ears, round tortoiseshell glasses and a huge friendly smile with gleaming white teeth. She wears a fluffy peach bathrobe.
Medium shot, static, from beside the mirror. DR. HILDA stands at the sink brushing her enormous teeth with a giant toothbrush, mouth wide open, white foam everywhere, eyes half closed, still sleepy. On the sink counter next to her, a phone in a coral-orange case lies screen-down, its edges glowing coral. The top quarter of the frame is calm tiled wall and soft sunrise light.
SCREEN RULE: any phone screen faces away from the camera; only its glow on the face is visible. No text, letters, numbers or logos anywhere in the frame.
AVOID: photorealistic, painterly look, extra characters, text, letters, numbers, logos, watermark, readable screens, multiple panels.
```

**Video prompt** (image-to-video, 6 s)
```
Single continuous shot, no cuts, static camera. Stylized 3D animated feature film, soft rounded cartoon characters, strong squash-and-stretch, fast snappy cartoon timing, no slow motion. Not photorealistic. Vertical 9:16.
Sunrise in a pink-tiled bathroom. DR. HILDA, a big gentle hippo in tortoiseshell glasses and a peach bathrobe, brushes her enormous teeth with a giant toothbrush. A phone on the sink counter glows coral.
[00:00-00:01] Hilda brushes sleepily, foam everywhere; the phone on the counter buzzes and glows coral.
[00:01-00:02] She glances down at the phone and freezes mid-brush.
[00:02-00:03] She picks up the phone and reads it close to her face, screen facing away from the camera; her eyebrows shoot up.
[00:03-00:04] She spits, rinses in one quick gulp and flashes a huge sparkling grin at the mirror.
[00:04-00:06] She presses the phone to her ear, nodding warmly, and gives the mirror a big thumbs-up.
The phone screen always faces away from the camera. No text, letters or numbers anywhere.
Audio: only the characters' own sounds (hums, gasps, a warm chuckle) and natural foley. No narrator, no voice-over, no dialogue, no music, no subtitles.
```

---

## Shot 5: walnuts (6 s, keep 5)

**Start image** (attach the Pip and Dr. Hilda refs)
```
STYLE: high-end stylized 3D animated feature film look, soft rounded cartoon characters with big expressive eyes, strong squash-and-stretch posing, soft global illumination, gentle rim light, shallow depth of field. Not photorealistic. Vertical 9:16.
OFFICE STEP IN THE MORNING: the front of a small, friendly dental office on a sunny morning. A pale mint door standing open, the sign shaped like a plain white tooth glowing above the door (no letters), potted plants by the steps, a short stone path, bright blue sky.
PIP: a small, round chipmunk with rusty-orange fur, a cream belly, black-and-white stripes down his back and across his eyes, big glossy dark eyes, a tiny pink nose and a fluffy tail; wears a mint-green nightshirt with white buttons. Both of his cheeks are normal, small and neat.
DR. HILDA: a big, gentle hippo dentist with soft lilac-grey skin, rosy cheeks, small round ears, round tortoiseshell glasses and a huge friendly smile with gleaming white teeth. She wears lavender dental scrubs.
Medium-wide shot, static. PIP stands on the front step in the sunshine, beaming, both cheeks back to normal, one paw in his nightshirt pocket. DR. HILDA fills the open doorway behind him, waving goodbye with a warm smile.
SCREEN RULE: any phone screen faces away from the camera; only its glow on the face is visible. No text, letters, numbers or logos anywhere in the frame.
AVOID: photorealistic, painterly look, extra characters, text, letters, numbers, logos, watermark, readable screens, multiple panels.
```

**Video prompt** (image-to-video, 6 s)
```
Single continuous shot, no cuts, static camera. Stylized 3D animated feature film, soft rounded cartoon characters, strong squash-and-stretch, fast snappy cartoon timing, no slow motion. Not photorealistic. Vertical 9:16.
A sunny morning at the front step of a small dental office with a tooth-shaped sign. PIP, a small chipmunk in a mint nightshirt with both cheeks back to normal, stands on the step; DR. HILDA, a big hippo dentist in lavender scrubs and tortoiseshell glasses, waves from the doorway.
[00:00-00:01] Pip beams and stretches happily in the sunshine.
[00:01-00:02] He pulls a walnut from his pocket and cracks it with his teeth in one triumphant bite.
[00:02-00:03] He stuffs the walnut in, then another and another, until both cheeks balloon out round and full of nuts.
[00:03-00:04] Behind him, Dr. Hilda does a big horrified double-take at his bulging cheeks.
[00:04-00:05] Pip turns to her with a proud puffy-cheeked grin and a thumbs-up.
[00:05-00:06] Dr. Hilda bursts out laughing and shakes her head.
No text, letters or numbers anywhere.
Audio: only the characters' own sounds (squeaks, gasps, laughter) and natural foley. No narrator, no voice-over, no dialogue, no music, no subtitles.
```

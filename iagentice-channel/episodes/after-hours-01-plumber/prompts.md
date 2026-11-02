# Prompts: After Hours #1, "The Bucket" (plumber)

**Order of work**
1. Cast refs (done): `assets/cast/doug.png`, `ember.png`, `rex.png`, plus the size lineup. Make the guest **Miso** sheet below.
2. Each shot: make the **start image** (Nano Banana) with the refs listed for it, then put the **video prompt** into the Pipeline Editor (one line per field, or paste the whole block into Raw Markdown).
3. Veo 3.1, image-to-video, 9:16, 720p. Takes: shot 1 ×2, the rest ×1. Drop clips in `clips/` as `s1a.mp4`, `s1b.mp4`, `s2.mp4`…

| Shot | Veo length | Refs to attach to the start image | Takes |
|---|---|---|---|
| 1 | **4 s** | Miso | 2 |
| 2 | **4 s** | Rex | 1 |
| 3 | **8 s** | Miso, Ember, last frame of shot 1 | 1 |
| 4 | **6 s** (keep 5) | Doug, Ember, lineup | 1 |
| 5 | **6 s** | Doug, Ember, Miso, Rex, lineup, shot 1 start image | 1 |

## Character blocks (paste word for word into image prompts and the APPEARANCE field)

```
DOUG: a huge, soft, friendly brown bear business owner, very round and heavy with a big round belly, thick fluffy chestnut-brown fur, a lighter tan muzzle, a big dark nose, small round ears, small kind eyes under heavy drowsy eyelids and a few stubborn tufts of fur sticking up on his head; wears a heather-grey T-shirt slightly too small for his belly, blue work trousers and brown work boots.
```
- Plumber gear (shots 4–5): `Today he also wears a navy plumber's cap and a leather tool belt, and carries a big red pipe wrench.`
```
EMBER: a small, round, glowing ball of soft coral-orange light, about the size of a tennis ball, perfectly spherical with a soft fuzzy glowing edge and a warm halo; two big round glossy black eyes with white highlights, no mouth, two tiny stubby coral arms; it floats with no legs and no wings and leaves a faint coral light trail.
```
```
REX: a lean, smug raccoon business owner, slightly shorter than average, with a sharp black eye mask, a ringed bushy tail held high, glossy grey fur slicked back on top, narrow confident eyes and a cocky half-smile; wears a shiny teal bomber jacket over a white T-shirt, dark jeans and spotless white sneakers.
```
```
MISO: a small, plump grey tabby cat with a cream muzzle and chest, big round amber eyes, a pink nose, long expressive whiskers and a thick striped tail; wears oversized blue-and-white striped pajamas with a chest pocket and one fuzzy white slipper. A phone in a coral-orange case sits in the chest pocket.
```
```
KITCHEN: a small retro kitchen: mint-green cabinets, a black-and-white checkered floor, a white sink with the cabinet doors underneath open and a burst copper pipe inside, a tall white fridge, a round wall clock with plain tick marks and no numbers, a window over the sink.
```
Every image prompt starts with STYLE and ends with AVOID:
```
STYLE: high-end stylized 3D animated feature film look, soft rounded cartoon characters with big expressive eyes, strong squash-and-stretch posing, soft global illumination, gentle rim light, shallow depth of field. Not photorealistic. Vertical 9:16.
```
```
AVOID: photorealistic, painterly look, extra characters, text, letters, numbers, logos, watermark, readable phone screens, multiple panels.
```

## Guest reference sheet: Miso
```
Character reference sheet of one original character, shown three times side by side on a plain light-grey background: front view, three-quarter view, and a soaked, grumpy close-up of the face. Even soft studio light. 16:9.
MISO: a small, plump grey tabby cat with a cream muzzle and chest, big round amber eyes, a pink nose, long expressive whiskers and a thick striped tail; wears oversized blue-and-white striped pajamas with a chest pocket and one fuzzy white slipper. A phone in a coral-orange case sits in the chest pocket.
STYLE: high-end stylized 3D animated feature film look, soft rounded cartoon characters with big expressive eyes, strong squash-and-stretch posing, soft global illumination, gentle rim light. Not photorealistic.
AVOID: realistic cat, a design that looks like Garfield, Puss in Boots or any existing cartoon cat, text, letters, numbers, labels, logos, watermark, extra characters.
```

---

## Shot 1: hook (4 s)

**Start image** (attach Miso)
```
STYLE: high-end stylized 3D animated feature film look, soft rounded cartoon characters with big expressive eyes, strong squash-and-stretch posing, soft global illumination, gentle rim light, shallow depth of field. Not photorealistic. Vertical 9:16.
KITCHEN: a small retro kitchen: mint-green cabinets, a black-and-white checkered floor, a white sink with the cabinet doors underneath open and a burst copper pipe inside, a tall white fridge, a round wall clock with plain tick marks and no numbers, a window over the sink.
MISO: a small, plump grey tabby cat with a cream muzzle and chest, big round amber eyes, a pink nose, long expressive whiskers and a thick striped tail; wears oversized blue-and-white striped pajamas with a chest pocket and one fuzzy white slipper. A phone in a coral-orange case sits in the chest pocket.
Night, cool blue moonlight through the window plus the warm glow of a small lamp. Low wide shot from floor level, the whole kitchen visible. The burst copper pipe under the sink is blasting a huge fan of white water across the room, spray frozen mid-air, droplets everywhere, water ankle-deep on the checkered floor. MISO stands in the middle of the flood, legs braced wide, fur puffed up in panic, eyes huge, holding a comically tiny red bucket the size of a teacup out under the spray with both paws. The wall clock hands point to about 2:47.
AVOID: photorealistic, painterly look, extra characters, text, letters, numbers, logos, watermark, readable phone screens, multiple panels.
```

**Video prompt** (4 s)
```
SUBJECT: [STYLE & MEDIUM]: stylized 3D animated feature film, soft rounded cartoon characters, strong squash-and-stretch, fast snappy cartoon timing, no slow motion, not photorealistic, vertical 9:16. Single continuous shot, no cuts, static camera. MISO the grey tabby cat fights a burst pipe at night with a teacup-sized red bucket.
APPEARANCE / DESCRIPTION: MISO: a small, plump grey tabby cat with a cream muzzle and chest, big round amber eyes, a pink nose, long expressive whiskers and a thick striped tail; wears oversized blue-and-white striped pajamas with a chest pocket and one fuzzy white slipper; a phone in a coral-orange case in the pocket. Holds a comically tiny red bucket.
ACTION / MOTION: [00:00-00:01] The geyser is already roaring; Miso braces against the spray, fur puffed, holding the tiny bucket out with both paws. [00:01-00:02] The tiny bucket fills and overflows instantly; Miso stares down at it, completely deadpan. [00:02-00:03] The spray swings sideways and hits Miso full in the face; its fur goes flat and soaked with a big squash-and-stretch flinch. [00:03-00:04] Dripping and flattened, Miso slowly turns and glares straight at the camera while the water keeps rising up the cabinets. Camera: static, low wide angle, no movement.
SETTING / BACKGROUND: A small retro kitchen at night: mint-green cabinets, black-and-white checkered floor, a burst copper pipe blasting water from the open cabinet under the white sink, a tall white fridge, a round wall clock with no numbers, a moonlit window. Water ankle-deep and rising.
ATMOSPHERE / MOOD: Chaotic, panicked, slapstick comedy.
LIGHTING: Cool blue moonlight through the window mixed with a warm lamp glow; sparkling highlights on the spray.
COLOR GRADING: Night palette of cool blues and mint with warm lamp accents; clean, saturated feature-animation look.
VOICE / NARRATION: None. Wordless: only Miso's own sounds (a gasp, an offended yowl). No dialogue, no narrator, no music.
TEXT OVERLAY: None. No text, letters or numbers anywhere in the frame.
FOLEY SFX: Roaring water geyser, splashes, a tiny plink as the bucket fills, overflow trickle, drips.
TRANSITION: None; hard cut in the edit. Single continuous shot.
```

---

## Shot 2: Rex lets it ring (4 s)

**Start image** (attach Rex)
```
STYLE: high-end stylized 3D animated feature film look, soft rounded cartoon characters with big expressive eyes, strong squash-and-stretch posing, soft global illumination, gentle rim light, shallow depth of field. Not photorealistic. Vertical 9:16.
REX: a lean, smug raccoon business owner, slightly shorter than average, with a sharp black eye mask, a ringed bushy tail held high, glossy grey fur slicked back on top, narrow confident eyes and a cocky half-smile; wears a shiny teal bomber jacket over a white T-shirt, dark jeans and spotless white sneakers.
Night. Medium shot of a flashy bedroom: a big bed with shiny teal satin sheets and too many pillows, a sleek black nightstand. REX lies sprawled on his back fast asleep, wearing teal silk pajamas instead of his jacket and a teal silk sleep mask pushed over his eyes, one arm flung out, mouth open in a smug snore, his ringed tail draped off the bed. On the nightstand his phone lies screen-down, buzzing, its edges glowing bright white. Dim blue night light.
AVOID: photorealistic, painterly look, extra characters, text, letters, numbers, logos, watermark, readable phone screens, multiple panels.
```

**Video prompt** (4 s)
```
SUBJECT: [STYLE & MEDIUM]: stylized 3D animated feature film, soft rounded cartoon characters, strong squash-and-stretch, fast snappy cartoon timing, no slow motion, not photorealistic, vertical 9:16. Single continuous shot, no cuts, static camera. REX the smug raccoon ignores a ringing phone in his sleep.
APPEARANCE / DESCRIPTION: REX: a lean, smug raccoon with a sharp black eye mask, a ringed bushy tail, glossy grey fur slicked back on top and a cocky half-smile; tonight in teal silk pajamas and a teal silk sleep mask.
ACTION / MOTION: [00:00-00:01] Rex snores, sprawled in bed; the phone on the nightstand buzzes and lights up. [00:01-00:02] Without waking, Rex gropes blindly for the phone. [00:02-00:03] He shoves the buzzing phone under his pillow, still asleep. [00:03-00:04] He snuggles into the pillow with a smug sleeping smile and lets out a huge snore while the pillow keeps glowing. Camera: static medium shot, no movement.
SETTING / BACKGROUND: A flashy bedroom at night: a big bed with shiny teal satin sheets and too many pillows, a sleek black nightstand.
ATMOSPHERE / MOOD: Smug, oblivious, comic.
LIGHTING: Dim blue night light; the phone's white glow lights Rex's face from the side.
COLOR GRADING: Cool night blues with glossy teal accents.
VOICE / NARRATION: None. Wordless: only Rex's own snores and sleepy grunts. No dialogue, no narrator, no music.
TEXT OVERLAY: None. No text, letters or numbers anywhere in the frame; the phone screen faces down.
FOLEY SFX: Phone buzzing on wood, muffled buzzing under the pillow, satin rustle, loud snore.
TRANSITION: None; hard cut in the edit. Single continuous shot.
```

---

## Shot 3: Ember takes the details (8 s, one continuous action)

**Start image** (attach Miso, Ember and the last frame of shot 1)
```
STYLE: high-end stylized 3D animated feature film look, soft rounded cartoon characters with big expressive eyes, strong squash-and-stretch posing, soft global illumination, gentle rim light, shallow depth of field. Not photorealistic. Vertical 9:16.
MISO: a small, plump grey tabby cat with a cream muzzle and chest, big round amber eyes, a pink nose, long expressive whiskers and a thick striped tail; wears oversized blue-and-white striped pajamas with a chest pocket and one fuzzy white slipper. A phone in a coral-orange case sits in the chest pocket.
Night. Medium close shot at fridge-top height. MISO crouches on top of a tall white fridge, completely soaked, fur flat and dripping, holding the coral phone in both paws with the screen facing away from the camera and toward Miso, typing hard with one claw, eyes narrowed, its face lit warm coral by the screen. Below, the retro kitchen is flooded and a jet of water still arcs from the open sink cabinet. A moonlit window on the right side of the frame. The upper quarter of the frame is calm dark ceiling.
AVOID: photorealistic, painterly look, extra characters, text, letters, numbers, logos, watermark, readable phone screens, multiple panels.
```
Ember isn't in the start image on purpose: it pops out during the clip. Attach the Ember ref so Veo knows the design.

**Video prompt** (8 s)
```
SUBJECT: [STYLE & MEDIUM]: stylized 3D animated feature film, soft rounded cartoon characters, strong squash-and-stretch, fast snappy cartoon timing, no slow motion, not photorealistic, vertical 9:16. Single continuous shot, no cuts, static camera. A soaked cat types into a website chat and EMBER, a tiny glowing coral helper, pops out of the phone to take its details.
APPEARANCE / DESCRIPTION: MISO: a small, plump grey tabby cat in blue-and-white striped pajamas, soaked, holding a phone in a coral-orange case with the screen facing away from the camera. EMBER: a small, round, glowing ball of soft coral-orange light the size of a tennis ball, with a soft fuzzy glowing edge and a warm halo, two big round glossy black eyes, no mouth, two tiny stubby coral arms; it floats with no legs and no wings and leaves a faint coral light trail.
ACTION / MOTION: [00:00-00:01] Miso, on top of the fridge, glares at the phone and types hard; warm coral light glows on its face. [00:01-00:02] EMBER pops up from behind the top edge of the phone in a little burst of coral sparkles and blinks at Miso. [00:02-00:03] Ember pulls out a tiny cream notepad and a stubby pencil, eyes eager. [00:03-00:05] Miso points frantically down at the spraying pipe and waves its paws; Ember scribbles fast on the notepad, nodding. [00:05-00:06] Ember tears off the note and folds it into a tiny envelope. [00:06-00:07] Ember gives Miso a tiny salute; Miso hugs the phone with a huge sigh of relief. [00:07-00:08] Ember zooms out through the moonlit window with the envelope, leaving a coral light trail. Camera: static medium close shot, no movement.
SETTING / BACKGROUND: On top of a tall white fridge in a flooded retro kitchen at night; a jet of water arcs from the open sink cabinet below; a moonlit window to the right.
ATMOSPHERE / MOOD: Panic turning into relief; warm, cute, hopeful.
LIGHTING: Cool blue moonlight on the room; Ember is a warm coral light source that lights Miso's wet fur as it moves.
COLOR GRADING: Cool night blues with Ember's warm coral as the only warm accent.
VOICE / NARRATION: None. Wordless: Ember only makes soft chirps and a tiny hum; Miso only sighs. No dialogue, no narrator, no music.
TEXT OVERLAY: None. No text, letters or numbers anywhere; the phone screen always faces away from the camera; the notepad shows only squiggles.
FOLEY SFX: Claw taps on glass, a soft magical pop, pencil scribbling, paper tearing and folding, a quick whoosh out of the window, drips.
TRANSITION: None; hard cut in the edit. Single continuous shot.
```

---

## Shot 4: 7:00 AM (6 s, keep 5)

**Start image** (attach Doug, Ember, lineup)
```
STYLE: high-end stylized 3D animated feature film look, soft rounded cartoon characters with big expressive eyes, strong squash-and-stretch posing, soft global illumination, gentle rim light, shallow depth of field. Not photorealistic. Vertical 9:16.
DOUG: a huge, soft, friendly brown bear business owner, very round and heavy with a big round belly, thick fluffy chestnut-brown fur, a lighter tan muzzle, a big dark nose, small round ears, small kind eyes under heavy drowsy eyelids and a few stubborn tufts of fur sticking up on his head; wears a heather-grey T-shirt slightly too small for his belly, blue work trousers and brown work boots.
EMBER: a small, round, glowing ball of soft coral-orange light, about the size of a tennis ball, perfectly spherical with a soft fuzzy glowing edge and a warm halo; two big round glossy black eyes with white highlights, no mouth, two tiny stubby coral arms; it floats with no legs and no wings and leaves a faint coral light trail.
Sunrise. Medium-wide shot of a cosy, slightly messy bedroom: warm orange-pink light through the window. DOUG is sprawled diagonally across a big bed under a plaid blanket in his grey T-shirt, mouth open mid-snore, one tuft flopped over; a navy plumber's cap hangs on the bedpost and a big red pipe wrench leans against the bed. On the nightstand, EMBER is curled up asleep on top of a phone (screen down), glowing softly, a tiny cream envelope tucked under it. The top quarter of the frame is calm wall and window light.
AVOID: photorealistic, painterly look, extra characters, text, letters, numbers, logos, watermark, readable phone screens, multiple panels.
```

**Video prompt** (6 s)
```
SUBJECT: [STYLE & MEDIUM]: stylized 3D animated feature film, soft rounded cartoon characters, strong squash-and-stretch, fast snappy cartoon timing, no slow motion, not photorealistic, vertical 9:16. Single continuous shot, no cuts, static camera. At sunrise, DOUG the sleepy bear plumber wakes to the lead EMBER delivered overnight.
APPEARANCE / DESCRIPTION: DOUG: a huge, soft, friendly brown bear, very round with a big belly, fluffy chestnut-brown fur, a tan muzzle, small kind drowsy eyes and tufts of fur on his head, in a heather-grey T-shirt. EMBER: a small glowing coral-orange ball of light the size of a tennis ball with big glossy black eyes, no mouth, tiny stubby arms, floating with no legs or wings.
ACTION / MOTION: [00:00-00:01] Doug snores in bed; the phone under sleeping Ember buzzes and Ember bounces awake. [00:01-00:02] Ember floats up and holds the tiny envelope right under Doug's nose; his eyes open drowsily. [00:02-00:03] Doug picks up the phone and reads it close to his face, screen facing away from the camera; his eyes go wide. [00:03-00:04] He sits up and presses the phone to his ear, nodding. [00:04-00:06] He pulls the navy plumber's cap on, grabs the big red pipe wrench and Ember dives into his T-shirt pocket as he lumbers out of frame. Camera: static medium-wide shot, no movement.
SETTING / BACKGROUND: A cosy, slightly messy bedroom at sunrise: a big bed with a plaid blanket, a nightstand, a navy plumber's cap on the bedpost, a red pipe wrench leaning on the bed.
ATMOSPHERE / MOOD: Sleepy calm snapping into eager action; warm and satisfying.
LIGHTING: Warm golden-orange sunrise light through the window; Ember adds a small coral glow.
COLOR GRADING: Warm dawn palette of orange, peach and gold.
VOICE / NARRATION: None. Wordless: Doug's snore and a happy grunt; Ember's chirps. No dialogue, no narrator, no music.
TEXT OVERLAY: None. No text, letters or numbers anywhere; the phone screen faces away from the camera.
FOLEY SFX: Big snore, phone buzz, blanket rustle, bed creak, heavy footsteps.
TRANSITION: None; hard cut in the edit. Single continuous shot.
```

---

## Shot 5: one twist, too late Rex (6 s)

**Start image** (attach Doug, Ember, Miso, Rex, lineup and the shot 1 start image)
```
STYLE: high-end stylized 3D animated feature film look, soft rounded cartoon characters with big expressive eyes, strong squash-and-stretch posing, soft global illumination, gentle rim light, shallow depth of field. Not photorealistic. Vertical 9:16.
KITCHEN: a small retro kitchen: mint-green cabinets, a black-and-white checkered floor, a white sink with the cabinet doors underneath open and a burst copper pipe inside, a tall white fridge, a round wall clock with plain tick marks and no numbers, a window over the sink.
DOUG: a huge, soft, friendly brown bear business owner, very round and heavy with a big round belly, thick fluffy chestnut-brown fur, a lighter tan muzzle, a big dark nose, small round ears, small kind eyes under heavy drowsy eyelids and a few stubborn tufts of fur sticking up on his head; wears a heather-grey T-shirt slightly too small for his belly, blue work trousers and brown work boots. Today he also wears a navy plumber's cap and a leather tool belt, and carries a big red pipe wrench.
EMBER: a small, round, glowing ball of soft coral-orange light, about the size of a tennis ball, perfectly spherical with a soft fuzzy glowing edge and a warm halo; two big round glossy black eyes with white highlights, no mouth, two tiny stubby coral arms; it floats with no legs and no wings and leaves a faint coral light trail.
MISO: a small, plump grey tabby cat with a cream muzzle and chest, big round amber eyes, a pink nose, long expressive whiskers and a thick striped tail; wears oversized blue-and-white striped pajamas with a chest pocket and one fuzzy white slipper. A phone in a coral-orange case sits in the chest pocket.
Bright morning sun. Wide static shot of the flooded kitchen. DOUG kneels knee-deep at the open sink cabinet, his red pipe wrench clamped on the burst copper pipe, which still sprays water. EMBER peeks out of Doug's T-shirt pocket. MISO watches from the top of the fridge, holding the tiny red bucket. Through the window over the sink, a sunny street is visible, empty for now.
AVOID: photorealistic, painterly look, extra characters, text, letters, numbers, logos, watermark, readable phone screens, multiple panels.
```
Rex isn't in the start image: his van arrives in the window during the clip. Attach the Rex ref so Veo knows the design.

**Video prompt** (6 s)
```
SUBJECT: [STYLE & MEDIUM]: stylized 3D animated feature film, soft rounded cartoon characters, strong squash-and-stretch, fast snappy cartoon timing, no slow motion, not photorealistic, vertical 9:16. Single continuous shot, no cuts, static camera. DOUG fixes the pipe in one twist, gets a tiny tip, and his rival REX arrives too late.
APPEARANCE / DESCRIPTION: DOUG: a huge, soft brown bear with fluffy chestnut fur and drowsy kind eyes, grey T-shirt, navy plumber's cap, tool belt, big red pipe wrench. EMBER: a small glowing coral-orange ball of light with big glossy black eyes and tiny arms, peeking from Doug's T-shirt pocket. MISO: a plump grey tabby cat in blue-and-white striped pajamas holding a teacup-sized red bucket. REX: a lean, smug raccoon with a black eye mask, slicked-back grey fur and a shiny teal bomber jacket, driving a small teal van.
ACTION / MOTION: [00:00-00:01] Doug gives the wrench one big confident twist and the spray stops dead; Ember pops up from his pocket and cheers. [00:01-00:02] Miso hops down from the fridge and proudly holds out the tiny red bucket, full to the brim. [00:02-00:03] Doug takes it and sips it like a tiny espresso, pinky raised, eyes closed in satisfaction. [00:03-00:04] Through the window behind them, a small teal van screeches to a stop and Rex leans out of the driver's window with a cocky grin. [00:04-00:05] Rex spots Doug inside; his grin drops. [00:05-00:06] Rex slumps forward onto his steering wheel in defeat. Camera: static wide shot, no movement.
SETTING / BACKGROUND: The same retro kitchen in bright morning sun, still wet, the water draining; through the window over the sink, a sunny suburban street.
ATMOSPHERE / MOOD: Triumphant, cheeky, comic payoff.
LIGHTING: Bright warm morning sunlight streaming through the window; Ember's small coral glow.
COLOR GRADING: Warm, bright and saturated: mint, sunny yellow, coral.
VOICE / NARRATION: None. Wordless: Ember's happy chirp, Doug's contented "ahh", Miso's purr, Rex's groan. No dialogue, no narrator, no music.
TEXT OVERLAY: None. No text, letters, numbers or logos anywhere, including on the van.
FOLEY SFX: Wrench ratchet, water stopping abruptly, draining gurgle, a tiny sip, tires screeching, a car horn honk as Rex's forehead hits the wheel.
TRANSITION: None; hard cut to the end card in the edit. Single continuous shot.
```

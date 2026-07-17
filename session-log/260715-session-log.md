# 260715 Session Log

## NEXA/NEXA-site.html — turned into a full NEXA intro site + palette + link fixes

- **Palette (per moodboard):** added `--orange: #E67033` and `--yellow: #EEC341` to `:root` alongside `--bg #F5F5F5` / `--blue #172FC7`. Hero 3D accent blocks now cycle blue→orange→yellow (was all blue), matching the moodboard's modular-block identity.
- **Broken links fixed:** gallery `<img>` paths were `references/website-placeholder/…` which resolve to `NEXA/references/…` (404). Rewrote to `../references/website-placeholder/…`. (Same relative-path trap noted for VORO/ in CLAUDE.md — anything in NEXA/ referencing repo-root assets needs `../`.)
- **New sections** (single-file, matches existing Montserrat/blue aesthetic):
  - `#concept` — "A program is a list / NEXA makes it a building" + 3 Pantone-chip cards (blue/orange/yellow), blueprint-grid wash. Copy from moodboard: reads brief → distributes to 8'-6" module → generates hybrid structure.
  - `#lifespan` — dark band, design-for-disassembly message. LONG-life (The Frame, blue) vs SHORT-life (The Fit-out, orange) split. Ties to LONG/SHORT program lifespan concept.
  - `#pipeline` — 3 alternating steps using real tool screenshots `references/UI-chat.png`, `UI-massing.png`, `UI-structure.png` (note: these still show old VORO branding). Steps numbered 01/02/03 in blue/orange/yellow.
  - Nav updated: Agent / Pipeline / Module / Contact.
- **Brand refs used:** `references/moodboard/` (palette, FF Mark/Momo Trust type, DfD + program-lifespan tagline, NX zigzag mark) and `references/260708 deck.pdf` (couldn't render — no poppler; text streams compressed).
- **Verified:** node static server on :8137 + headless Edge (playwright-core, msedge channel). All 8 images load (naturalWidth non-zero, zero requestfailed). Hero/concept/lifespan/pipeline/gallery/thankyou all render. NOTE: `loading="lazy"` images below the fold need a scroll-through before a fullPage screenshot or they capture blank.

## NEXA-site.html — full dark restructure to xfigura.ai section rhythm

- Analysed https://xfigura.ai/ (SPA, scroll-jacked — headless couldn't scroll past hero; extracted section structure from DOM heading dump instead). Its flow: Hero(node-canvas, big italic-condensed statement, prompt+CTA) → Trusted-by → Community marquee → Enterprise 3-pillars → Capabilities bento → Closing manifesto+CTA → Footer. Principle: one idea per full-width section, each with a compressed uppercase statement headline; proof early; ends on manifesto + single CTA.
- User chose **full restructure + dark theme**. Rewrote the whole file. New token set: dark `--bg #0A0B12`, `--bg-2 #12141D`, light text, brand blue/orange/yellow as accents, `--blue-lite #4863F5` for on-dark text. Body has dotted-grid background (xfigura motif).
- New section order: `#hero` (dark 3D + prompt pill + Distribute/See-how CTA, links `../program-input.html`) → `#precedents` (trusted-by band: TPAC/53W53/Tama) → `#concept` (statement + 3 chip cards) → `#pipeline` (steps + UI shots) → `#lifespan` (bg-2, Frame/Fit-out pillars) → `#showcase` (auto-scroll **marquee** replacing the static gallery; reuses module photos + UI + `../RENDER/TOWER-1.png`) → `#closing` (manifesto "DISTRIBUTE YOUR PROGRAM." + blue glow + Open-the-agent CTA) → `#footer` (brand, tagline, nav cols; keeps "Thank you." in the base line per earlier request).
- `.statement` class = Montserrat 800 italic uppercase, tight tracking — the shared condensed-headline look. Loaded Montserrat italic weights.
- three.js hero recoloured for dark: `BG 0x0A0B12`, fog 18–42, ground `0x0F1220`, boosted hemi/key/rim lights, `WHITE 0xEDEFF5` blocks; accents still cycle blue→orange→yellow.
- **Verified** (server :8137 + headless Edge): all 17 marquee/step images load (naturalWidth non-zero, zero requestfailed). Hero, showcase marquee, closing, lifespan regions all render correctly on dark. (Reminder still applies: lazy imgs below fold need scroll-through before a fullPage capture.)

## NEXA-site.html — blue theme + brand fonts

- **Blue-ground retheme** (from dark): `:root` now `--bg #172FC7`, `--bg-2 #1428AE`, `--bg-3 #0F1F8F`, white text. Trick: repurposed `--blue-lite` → yellow so every eyebrow/highlight/`em`/step-num-default flips to yellow with no per-rule edits. Blue-on-blue spots reassigned to white/orange/yellow: card 1 chip → white(dark-chip), pipeline step 01 → white, lifespan long bar/k → white; nav/hero/closing primary buttons → white bg + blue text (hover yellow); nav & hero vignette → blue translucent; closing glow → white radial.
- **three.js hero on blue:** `BG 0x172FC7`, fog 18–44, ground `0x1226A0`, hemi ground-colour blue; blocks `WHITE 0xF3F4F9` main, accents cycle `[ORANGE, YELLOW, DEEP 0x0E1C82]` (dropped the blue accent — it blended into the blue ground; deep-navy gives depth instead).
- **Fonts:** title = **Momo Trust Display**, body = **FF Mark** (user request). Neither font file is in the project (`references/New folder/Mark Pro/` is empty; both are commercial, non-Google). IMPORTANT gotcha found: the copy of **"FF Mark" installed on this Windows machine is an OBLIQUE style** — naming it first slanted ALL body text (verified with a 4-way font probe: FF-Mark-stack rendered italic, Poppins upright). Fix: `--font-body` leads with **Poppins** (closest free upright ≈ FF Mark), real names trail. `--font-display` = `'Momo Trust Display','Fredoka',…` → **Fredoka** (rounded geometric ≈ Momo) actually loads. Loaded Fredoka + Poppins from Google (dropped Montserrat link). Set `.statement` and `.sec-head h2 em` to `font-style: normal` (Fredoka has no italic; faux-oblique looked bad). Global `h1,h2,h3,h4,.statement { font-family: var(--font-display); }`.
- To reclaim the true faces: drop real `FF Mark` (upright) + `Momo Trust Display` `.woff2` into the project, `@font-face` them, then move `'FF Mark'` to the front of `--font-body`.
- Verified on blue theme: hero, concept, lifespan, closing all render correct fonts/colours; body upright.

## NEXA-site.html — reverted to dark, plus a batch of refinements

- **Reverted the blue theme back to dark** (`--bg #0A0B12` …) per user; kept the font changes. All the blue-on-blue overrides undone (nav/hero/closing buttons, card1, step1, lifespan bars, glows, three.js BG/ground/hemi/ACCENTS).
- **Line breaks:** headings were cramped because `.sec-head` used `max-width: 40ch` (≈320px, ch is relative to the 16px container not the big heading). Fixed: `.sec-head` → `max-width: 780px`; added `text-wrap: balance` to `h1..h4/.statement/.eyebrow` and `text-wrap: pretty` to `p`. Hero eyebrow was also inheriting `#hero-copy p { max-width: 44ch }` (wrapped "PROGRAM/AGENT") → added `#hero-copy .eyebrow { max-width: none }`.
- **Hero 3D → moodboard kit-of-parts.** Added per-block base **elevation** so blocks can stack (applyLayout stores base in `.y`; animate uses `pos.y + scale.y/2`). Footprints are now **1×2 domino** bricks (unit `U=0.8`). Four schemes cycle: 0 = **bonded stacked brick tower** (alternating courses — reads exactly like the moodboard LEGO towers), 1 = long bar, 2 = courtyard ring, 3 = **exploded/re-solving** (bricks lifted apart, mid-reassembly). The morph between schemes = the proposal adapting.
- **Messaging = adaptable-over-time.** Hero eyebrow changed from the SCI-Arc label to product positioning: "The generative program agent for adaptable buildings". Hero subhead + closing rewritten to stress the proposal is never fixed — re-briefed/adapted/reassembled as needs change.
- **Nav logo de-backgrounded:** `NEXA-logo.png` is a blue mark on a WHITE box (not transparent); `NEXA-logo-mask.png` is a transparent WHITE mark. Swapped nav `<img>` to the mask (correct on dark; blue mark would be invisible anyway). Favicon still the png.
- **Floating pill nav (xfigura-style):** `#nav` is now a centered island — `top:16px; left:50%; translateX(-50%); width:min(1180px,100%-28px); border-radius:100px; backdrop-blur; box-shadow`; dropped the full-width border-bottom.
- Verified all four 3D schemes render (tower/bar/courtyard/exploded), concept/hero line breaks clean, pill nav + transparent logo correct.

## NEXA-site.html — hero animation made properly LEGO

- Added the signature LEGO **studs**: each brick has a pool of 8 studs (`CylinderGeometry`, r0.135 × h0.14) laid across its top every frame at a fixed **STUD_PITCH 0.4** (= half a module → each 0.8 module reads as 2×2 studs; a 1×2 domino = 2×4 studs). Stud count derives from the current footprint (`nLong/nShort = round(len/pitch)`), unused studs hidden; hidden while a brick is still growing (`hh>0.12`).
- Bricks now use `RoundedBoxGeometry(1,1,1,3,0.06)` (imported from addons) for rounded LEGO edges, and a glossier ABS material (roughness 0.42, clearcoat 0.55).
- Studs are positioned in world space alongside the box (not parented/scaled), so they stay round and sit flush on top through all four schemes (tower/bar/courtyard/exploded). Verified: zero console errors, studs render correctly in the stacked-tower and courtyard schemes. Result reads unmistakably as the moodboard LEGO towers.

## NEXA-site.html — hero animation reconceived: program model ⇄ structure model

- Dropped the LEGO-brick morph. Hero now shows a real building: a **program model** (3×2×5 grid = 30 modules, colour-coded by program type — mostly `NEUTRAL #C7CBD6` with BLUE/ORANGE/YELLOW accents via `progColor`) that **transforms into a structure model** (12 columns on the cell-corner grid + 6 floor slabs, steel `#9AA2B4`).
- Timeline `CYCLE 12s`: program hold → `structureAmount()` crossfades modules out (`opacity 1→0`) while columns grow from the ground (`scaleY 0→1`) and slabs fade in → structure hold → reverse. Driven by `updateModel(simT, dt)` in the RAF loop.
- **Module swap:** `scheduleSwaps()` fires once per cycle (on cycle-index change), swapping two same-floor module pairs into each other's cells; modules ease to their new home each frame and arc up while travelling (`lift = min(gap,1.2)*0.85`) — reads as the proposal being rearranged.
- Bricks/studs removed; `RoundedBoxGeometry` reused for modules + frame; materials are now `transparent` for the crossfade. Camera raised/retargeted (`orbitHeight 8.6`, `lookAt 0,2.6,0`) to frame the taller building.
- Verified: zero console errors; program (colored grid), transition (crossfade), and structure (clean column+slab frame) phases all render correctly.

## NEXA-site.html — hero refined: frame constant, only part of program re-shuffles

- Per user: the structural frame should stay put (constant), and only PART of the modules swap/rearrange while the rest stay — long-life frame vs short-life fit-out.
- Reworked: **structural frame (columns+slabs) is now always visible** (fades in once, `frameIn`, then holds). Modules no longer fade out. Each module is `swappable` iff its `progColor` is an accent (BLUE/ORANGE/YELLOW); NEUTRAL modules are fixed. `scheduleSwaps()` (every `CYCLE 5.5s`) only swaps same-floor swappable modules into each other's cells and occasionally recolours one (a "swap-out/replace"); neutral modules and the frame never move. Frame opacity brightens with `maxGap` of the moving modules (`0.24 + emph*0.42`) so the constant reads as structure exactly when the program is reshuffling. Rearranging modules arc up + go translucent.
- **Floating nav made more prominent** (user): bg `rgba(20,22,32,0.92)` (near-solid), border `rgba(255,255,255,0.16)`, shadow `0 18px 48px /.55` + inset top highlight.
- Verified: zero console errors; rest state shows modules held in a visible frame, swap state shows a few colored modules lifted/rearranging with the frame brightened, neutrals unchanged.

## NEXA-site.html — hero simplified to "many blocks rearranging"

- Per user ("算了直接做成許多方塊重新排列"): dropped the program/structure/frame model entirely. Hero is now **60 small cubes** (4×3×5 grid, `CELL 0.98`, `BS 0.8`, ~30% BLUE/ORANGE/YELLOW accents on neutral) that **continuously permute cells**. `shuffle(0.32)` every `SHUF 1.4s` picks a random subset and shuffles their cell assignments (a valid bijection — no overlaps); blocks ease to the new cell and arc up while travelling.
- Bug fixed: accent picker was `ACC[(i*3)%3]` (always 0 → all blue); changed to `ACC[(i*5+1)%3]` so blue/orange/yellow are mixed.
- No frame/columns/slabs/opacity anymore; blocks opaque. Camera lookAt lowered to `0,2.3,0`.
- Verified: zero console errors; dense cube cluster continuously reshuffles with mixed accents.

## NEXA-site.html — block anim: drop neutral, blue static, orange/yellow move

- Per user: no more #F5F5F5/neutral blocks — every cube is BLUE / ORANGE / YELLOW. Colour split `r=(i*7)%4` → ~50% blue, ~25% orange, ~25% yellow. `movable = color !== BLUE`.
- Blue blocks are fixed (never change cell); `shuffle()` only permutes MOVABLE (orange/yellow) blocks among their cells, so only the accents rearrange while the blue mass holds. Bumped shuffle frac to 0.5 (only half the blocks are movable).
- Verified: zero console errors; blue mass static, orange/yellow cubes lift + re-shuffle.

## NEXA-site.html — block anim: blue risers + extract-and-place motion

- "藍色一部分移到上層": ~30% of blue blocks flagged `riser` and added to the movable pool. `shuffle()` now sorts the picked cells by floor (highest first) and gives risers the top cells → part of the blue drifts upward. Non-riser blue stays fixed; orange/yellow still shuffle.
- "方塊往外面移動(抽出來)再放到另一個地方": replaced the direct lerp with a per-block `mv` path. `startMove()` records origin→dest; `updateModel` slides the base old→new cell while a `sin(πu)` bump pushes the block radially OUT of the mass (`PULL 2.2`, front-fallback near the axis) and back in — reads as pulled out of the facade, carried across, and slotted into the new cell.
- Verified: zero console errors; movable cubes visibly extract outward and re-place, blue mass mostly holds with a few risers up top.

## NEXA-site.html — block anim: blue fully static, longer interval

- Per user: blue must not move at all — removed the riser flag; `movable = !blue`, so only ORANGE/YELLOW blocks ever shuffle. Blue forms a fixed mass and the overall grid stays fully filled (arrangement unchanged).
- Longer rest between moves: `SHUF 1.4 → 3.6s`.
- Verified: zero console errors; rest frame = solid full grid with static blue, move frame = only a few orange/yellow cubes extracting/re-placing.

## NEXA-site.html — block anim: blue biased to the top

- Per user (move the lower blue up, keep it static): colour is now floor-biased. `pBlue = 0.28 + floorFrac*0.62` with a deterministic per-block hash → blue concentrates on the upper floors (static mass up top), orange/yellow fill the lower floors (the movers). Camera orbits, so this replaces any view-specific "bottom-left" targeting with a stable top-heavy-blue layout.
- Verified: zero console errors; top floors solid static blue, lower floors orange/yellow doing the extract-and-place shuffle.

## NEXA-site.html — top accents

- Per user: start one ORANGE (`top+5`) and one YELLOW (`top+10`) block on the top floor. Initially made them static, then (follow-up "上面那層的黃色橘色也要變") set `movable = color !== BLUE` so they re-shuffle like the other accents — they just begin up top. Verified: zero console errors.

## NEXA-site.html — hero anim converted to line-art / wireframe

- Per user ("線稿版, no shadows / no 3D-model feel"): each module is now a `THREE.LineSegments(EdgesGeometry(box), LineBasicMaterial(color))` — just the 12 coloured box edges, no fills. Blue/orange/yellow line colours.
- Removed all lighting, the ground plane, shadow map (`shadowMap.enabled=false`), tone mapping (`NoToneMapping` for exact line colours), and the DoF BokehPass — now renders straight `renderer.render(scene,camera)`. Fog kept so distant edges fade into the bg for depth. Movement/shuffle logic unchanged (blue static up top, orange/yellow extract-and-place below).
- `EffectComposer/RenderPass/BokehPass/RoundedBoxGeometry` imports now unused but left in place (harmless).
- Follow-up ("裡面還是要有一點infill"): each block is now a Group = faint flat fill (`MeshBasicMaterial`, unlit, `opacity 0.16`, `depthWrite:false`) + coloured edge lines, so boxes read as translucent coloured massing rather than hollow frames — still no shading/shadows. Verified: zero console errors.

## NEXA-site.html — hero block anim: interactive + layout/copy pass

- **Solid + white edges:** fill `MeshBasicMaterial` now opaque; edge `LineSegments` colour = `0xF5F5F5` (white outline over flat colour blocks, still unlit/no shadows).
- **Interactive, not auto:** removed the timed shuffle. Static by default; a horizontal **swipe** on `#hero` (accumulated pointer dx, threshold 90px, resets on direction flip) triggers `shuffle(0.5, ±1)` — left vs right fire independent rearrangements.
- **No rotation:** camera orbit increment removed (`updateCamera()` sets a fixed view once).
- **Angle "喬正":** FOV 34→22 + radius 15.5→23 + height 8.6→10.5 (flatter, more orthographic look); fog pushed to 26–58.
- **Mass moved right, clear of text:** `camera.translateX(PAN_X = -3.2)` pans the fixed view so the cube sits on the right.
- **Extract-and-place (no clipping):** blocks were cutting through the mass. Rewrote the move into 3 phases — pull **up and out** of the mass along a shared `EX` direction (mostly +Y, slight front-right, `OUT 3.4`), travel above the mass, drop into the new cell. Shared up-direction keeps extracted blocks over the mass on the right, never flying into the left text.
- **Hero aligned to sections:** `#hero-copy` given `max-width:1400px; margin:0 auto` to match the `.sec` container, so NEXA's left edge lines up with the section headings below.
- **Copy rewrite (less "AI feel"):** hero eyebrow shortened to "Adaptive Building Platform"; added lead "Long-lasting buildings that keep up with ever-changing uses." + digital-twin description (permanent structure + plug-in relocatable infill modules). Removed em-dashes across all visible copy (concept/pipeline/lifespan/showcase/closing/footer), replacing with colons/commas/periods.
- Removed the bottom "Scroll" cue.
- Follow-ups: user preferred the **radial-outward** extract over the upward one — reverted to radial (`OUT 2.7`) but clamp the outward X to ≥0 so left-side blocks extract in depth instead of flying into the text. Then fixed **infinite outward drift** on continuous swiping: `shuffle` now only picks blocks already at rest (`!blocks[b].mv`), and the swipe handler has a 450ms cooldown + 110px threshold, so each swipe is one bounded out-and-back rearrangement. Stress-tested: after heavy swiping the mass settles back to a clean full grid. Zero console errors.

## NEXA-site.html — footer cleanup + assembly video

- Removed "SCI-Arc SP26 Research Studio." from the footer base line (kept "Thank you."); em-dash in the adjacent credit changed to `·`.
- Added a new **#assembly** section between lifespan and showcase: `NEXA/assembly_animation_v5_lineart.mp4` (line-art isometric assembly, 1920×1080, ~29s). Poster frame extracted via ffmpeg → `NEXA/assembly-poster.jpg` (frame at 20s). Two-column `.a-grid`: copy left ("Assembly" / "Frame first, then the modules plug in.") + the video **cropped to a square** on the right (`.video-frame` `aspect-ratio:1/1`, white rounded framed panel, `object-fit:cover`), `autoplay muted loop playsinline`. Verified: video serves as `video/mp4`, plays (currentTime advancing, no error), section renders. Test server (`nexa-srv.js`) gained `.mp4`/`.webm` mime types.

## NEXA-site.html — pipeline updated to real tool + structure consolidation

- **Pipeline images + copy updated to the current NEXA workflow.** New screenshots in `references/screenshot/` (Screenshot 2026-07-15 18342/50/07) copied to clean names `step-brief.png` / `step-massing.png` / `step-structure.png`; pipeline `<img>` now point to those. Re-read `references/260708 deck.pdf` (rendered via headless Edge PDF viewer, `--headless=new`, PageDown loop — poppler still unavailable). Deck workflow: Narrative Brief (program/area/site) → Program Lifespan Analyze → Long/Short-Duration → Structural Zoning → Permanent Structure / Relocatable Units → Architecture Version 0 → Refresh/Turnover/Conversion/Reuse → Economic Analysis, with a Digital Twin monitoring. Rewrote the 3 steps: 01 Read the narrative brief (sorts long/short duration), 02 Zone long and short (massing by category, GFA/SHORT stats), 03 Resolve structure and modules (RC core / aluminium frame / glass curtain wall / timber fins + relocatable module frame/infill/skin, OBJ export, digital twin).
- **Pipeline 3 images same size:** `.step` grid → `1fr 1fr` and `.step-media` given `aspect-ratio:16/10` + `object-fit:cover` so all three render identically.
- **Assembly video → 4:3** (`.video-frame aspect-ratio:4/3`, shows more width) and **1.5× playback** (small script sets `video.playbackRate = 1.5` on load/play).
- **Merged Design-for-disassembly (lifespan) + Assembly** into one `#lifespan` section (removed standalone `#assembly`): head "Frame first, then the modules plug in.", `.ls-grid` two columns — Frame/Fit-out pillars stacked left, the 4:3 assembly video right. Concept + its ideal visual together.
- **Removed the `#precedents` band** (Studied on TPAC/53W53/Tama) and **moved the concept statement there**: `#concept` is now a short manifesto ("A program is a list. NEXA makes it a building." + intro) sitting right after the hero. Also **dropped the concept 3 cards** (they duplicated the pipeline's 3 steps) — Agent = manifesto, Pipeline = concrete steps. Nav links unchanged and valid.
- Verified: zero console errors; pipeline shows the 3 equal new screenshots with updated copy, video plays at 1.5× in 4:3, lifespan section pairs pillars with the assembly clip, concept statement replaces the precedents band.

## NEXA-site.html — agent graph + lifespan sizing

- **The Agent** section: wrapped in `.cc-grid` (2-col) and added an animated **agent flow graph** on the right — inline SVG with 5 nodes (Brief → Lifespan → Massing → Structure, plus a Digital twin monitoring via dashed curves) and coloured dots that run along the links via `<animateMotion path=…>` (blue/orange/yellow staggered). Self-contained, no JS.
- **Lifespan pillars height = video height:** `.ls-grid align-items:stretch` + `.ls-pillars grid-template-rows:1fr 1fr; height:100%` so the two pillars together match the video (measured pillars==video).
- **Made the three lifespan elements shorter** (keep width/alignment): video-frame `aspect-ratio 4/3 → 16/9` (16:9 is the clip's native ratio, so no crop and shorter), and tightened `.span-col` padding/margins/font. Height dropped 641→492, still matched.

## Follow-ups / open
- UI screenshots (`UI-*.png`) still say VORO, not NEXA — reshoot for full brand consistency if desired.
- Could inline the NX zigzag mark as SVG for crispness (currently `NEXA-logo.png`).
- Display type is Montserrat (≈ FF Mark); moodboard specifies FF Mark + Momo Trust Display (both non-Google) — swap if licensed webfonts become available.

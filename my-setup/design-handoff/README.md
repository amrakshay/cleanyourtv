# Handoff: CleanYourTV Home — Direction 1b ("Horizon", final)

## Overview
New home screen for the CleanYourTV launcher (`com.gathin.tvhome`) on a Xiaomi Mi TV 4A Pro (`dangal`, Amlogic txlx, ~1 GB RAM, **1280×720**). Goals: premium and personalised, ≤ ~25 MB resident (today 23 MB), no idle redraws, no bitmaps for background, must never fail to start.

## About the Design Files
The `.dc.html` files here are **design references built in HTML**, not code to ship. Recreate the design in the existing launcher: **plain Java + Android Views** (no Compose, no Kotlin, no new dependencies). Read `themes/README.md` first — anything below that is already a theme key should be done via `config.json`, not code.

Open `Home Screen Directions.dc.html` in a browser; 1b and 2a–2d are the final design. Click a frame and use arrow keys to simulate D-pad focus. `TVHome.dc.html` renders the screen (`variant="b"`).

## Fidelity
**High-fidelity.** All values below are in px at 1280×720 (on this TV, density 213 → 1 dp ≈ 0.75 px; convert, or lay out in px-equivalent dp: `dp = px / 1.33`). App tiles in the mock are colour stand-ins — real tiles use each app's own `android:banner`.

## Screen: Home (1b)

### Layout (absolute, 1280×720)
| Element | Position | Size |
|---|---|---|
| Header block (right-aligned column) | right 56, top 38 | auto |
| Dock row (4 tiles) | left 56, top 250; inner padding 18 → first tile at x 74, y ~268 | row 1168 × 186 |
| App row (3 tiles) | left 74, top 470 | auto |
| Tile (all 7, same size) | — | 266 × 150 |
| Tile gap (both rows) | — | 22 |

- **Top-left ~420×150 must stay empty** (physical sticker on the panel).
- Dock row has **no** background band, no border, no hairline.
- No tile labels, no large focused-app title.

### Header (top → bottom, all right-aligned)
1. **Pills row** — `Inputs` · `<SSID>` (e.g. `Akshay_WiFi`) · `Settings`
   - gap 10, margin-bottom 26
   - height 32, padding 0 15, radius 16, Roboto 400 13px
   - Unfocused: fill `#FFFFFF` @ 7%, 1px stroke `#FFFFFF` @ 14%, text `#FFFFFF` @ 86%
   - Focused: fill `#FFFFFF`, stroke `#FFFFFF`, text `#0A0A0A`
2. **Greeting** — Roboto Light (`sans-serif-light`) 32px, line-height 1.1, `#FFFFFF`, letter-spacing −0.005em. Text: `<greeting>, Akshay`
3. **Time · date row** — margin-top 12, gap 14, baseline-aligned, Roboto Light 21px
   - Time: Roboto Regular 21px `#FFFFFF`, 12-hour + AM/PM (`8:45 PM`)
   - Divider: 1 × 18, `#FFFFFF` @ 25%, vertically centred
   - Date: `#FFFFFF` @ 66%, format `EEEE d MMMM` (`Wednesday 21 October`)

### Tiles
- 266×150, corner radius 14, banner image `centerCrop` (banner is 320×180, so it stays sharp even at 1.12×).
- Unfocused: 1px inner ring `#FFFFFF` @ 7%.
- **Focused:** `scaleX/Y 1.12`, `translationY −4`, drop shadow `0 18 34 #000 @ 70%` + 1.5px ring `#FFFFFF` @ 22%, `translationZ`/bring-to-front so it overlaps neighbours.
  - Do **not** use `elevation` for the shadow (real-time blur is expensive on txlx). Use a pre-baked 9-patch shadow (~30 KB) shown only behind the focused tile, or the existing glass highlight if it already provides one.

### Background
Static radial gradient, ellipse centred at (42%, 42%) of the screen, radii 62% W × 105% H:

| Stop | Colour |
|---|---|
| 0.00 | `#1F45F0` |
| 0.28 | `#1533C8` |
| 0.55 | `#0C1F86` |
| 0.80 | `#060D3A` |
| 1.00 | `#02040F` |

Note: on SDK 28, `GradientDrawable` supports only 3 colours (offsets need API 29). Use a tiny custom `Drawable` with `RadialGradient(…, colors[], positions[], CLAMP)` and a `Matrix` scale to make it elliptical. Draw once; no animation. Set as window background (not a child view) to avoid an extra overdraw layer. **No bitmap.**

## Interactions & Behaviour
- **D-pad:** three focus rows — pills → dock → apps. Up/Down moves between rows keeping column index (clamped to row length). Left/Right clamped, no wrap. Default focus on launch: dock tile 0 (Hotstar).
- **Focus animation (normal):** 360 ms, overshoot spring (≈ `cubic-bezier(.3,1.55,.5,1)`; use the existing `dynamicanimation` spring, damping ~0.6).
- **Focus animation (`reduced_motion` on):** 110 ms linear, no overshoot, same end state (lift + 1.12× still applies).
- Pills: colour swap on focus, same timings.
- OK on tile → launch app. OK on pill → Inputs / Wi-Fi settings / Settings (existing actions).
- Nothing animates or redraws while idle except the clock (once a minute).

## Greeting by time of day
Evaluated on the same once-a-minute clock tick (no extra timer).

| Hours | String (EN) |
|---|---|
| 05:00–11:59 | Good morning |
| 12:00–16:59 | Good afternoon |
| 17:00–22:59 | Good evening |
| 23:00–04:59 | Late night |

Reuse existing greeting strings if present; add any missing ones (`greeting_afternoon`, `greeting_late_night`) with an English default in `values/strings.xml` so the 24 locales fall back safely. Name comes from the existing greeting-name setting ("Akshay").

## State
- `focusRow` (pills | dock | apps), `focusIndex`
- `reducedMotion` (theme key)
- Current time → greeting bucket

## Design Tokens
- Text: `#FFFFFF` at 100 / 86 / 66 / 25 (divider) / 14 (stroke) / 7 (fill) %
- Focused pill text `#0A0A0A`
- Radii: tile 14, pill 16
- Spacing: 10 (pill gap), 12, 14, 18 (row padding), 22 (tile gap), 26, 34 (row spacing), 38/56 (screen margins)
- Type: Roboto (system `sans-serif`, `-light`) — 13 / 21 / 32px. **No bundled fonts.**

## Cost estimates (not measured — verify)
| Change | Memory | GPU / risk |
|---|---|---|
| Gradient background drawable | ~0 MB | 1 full-screen fill (replaces existing) |
| Header reorder, sizes | 0 | none |
| Equal tile sizes | ~0 (banners already loaded, ~1.6 MB for 7) | none |
| Focus lift + 9-patch shadow | ~+0.03 MB | small; avoid `elevation` |
| Greeting buckets | 0 | none |

Measure before/after:
```
TV_HOST=192.168.0.236 tools/venv/bin/python -I tools/tv.py 'dumpsys meminfo com.gathin.tvhome' | grep TOTAL
```
Target ≤ ~25 MB. Screenshot with `tools/tv.py` and compare against the mock.

## Things to check on the TV
- Thin/Light type shimmer at 720p
- Focus smoothness with `reduced_motion` on and off
- Blue matches the photo (adjust stops if the panel renders it harsher)
- `show_stats` off, `advanced_effects` off

## Files
- `Home Screen Directions.dc.html` — overview; final = 1b, greeting states = 2a–2d
- `TVHome.dc.html` — screen renderer (`variant="b"`, props `focus`, `tod`, `reducedMotion`)
- `support.js` — runtime needed to open the HTML files

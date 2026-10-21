# Prompt: design a premium, lightweight home screen for my Android TV launcher

Copy everything below the line into a fresh Claude session, with the repo open.

---

I want you to design and implement a premium-looking, memory-light home screen for the
CleanYourTV launcher running on my TV. I am happy for you to change code, not just config,
as long as it stays lightweight and reliable.

## The hardware I am designing for — treat these as hard limits

| | |
|---|---|
| TV | Xiaomi MiTV-AXSO0 (`dangal`), sold as Mi TV 4A Pro / 4C Pro 2019 |
| OS | Android TV 9, SDK 28, firmware PI.6036 |
| Chip | Amlogic `txlx` — weak GPU |
| RAM | **1,014,724 kB total (~1 GB)**, about 400 MB available in practice |
| Screen | **1280x720**, density 213 dpi — NOT 1080p |
| Launcher now | `com.gathin.tvhome`, measured at **23 MB** resident |

The screen is 720p, so design at 1280x720. Do not assume 1080p. The set lags under load, so
every visual idea must be justified against memory and GPU cost — on this chip, overdraw and
large bitmaps are the enemy, not CPU.

## The codebase

- `launcher/app/src/main/java/com/gathin/tvhome/` — **39 files, ~9,200 lines of plain Java**
- **Android Views, not Compose. Java, not Kotlin.** Keep it that way; both exist deliberately
  and switching either would add megabytes.
- Only two dependencies: `androidx.recyclerview:recyclerview` and `androidx.dynamicanimation`.
  **Do not add dependencies.** If you think you need one, explain why and ask first.
- `minifyEnabled` and `shrinkResources` are already on. compileSdk 34, minSdk 26, Java 17,
  AGP 8.5.2, Gradle 8.9.
- Layouts: `launcher/app/src/main/res/layout/` (`activity_main.xml`, `item_app.xml`, …)
- Theme keys are documented in `themes/README.md` — read that table before proposing anything,
  because many things I might want are already settings and need no code at all.
- The launcher ships 24 languages in `res/values-*`. Any new user-visible string needs an
  English default and must not break the others.

## What it must look like

Premium, restrained, and obviously personalised — the reaction I want from a guest is "that
isn't a normal TV". Current reference points: a pitch-black home, a dock of four apps in a
rounded band, one glass highlight that moves between tiles, a greeting with my name, a thin
clock and date.

My apps: Hotstar, YouTube, Netflix, VLC (my dock, in that order), plus Live TV
(`com.android.tv`), Play Store and Mi Media Explorer in the grid.
My greeting name is "Akshay".

## Hard constraints

1. **No wallpapers, no photographic backgrounds.** A 720p wallpaper costs 4 MB in RGB_565 and
   8 MB in true colour. Black backgrounds are free. Work with colour, type, spacing and light.
2. **No continuously animating background.** Nothing that redraws when the user is idle.
3. `show_stats` stays **off** — it polls while Home is visible.
4. `advanced_effects` stays **off** unless you can show the cost is negligible on a `txlx` GPU.
5. Consider turning `reduced_motion` **on** — it exists for weak GPUs (stiff highlight spring,
   no tile overshoot, short fades). Tell me whether premium motion survives it.
6. Do not regress the launcher past **~25 MB** resident. If a change costs memory, say how much.
7. Nothing may make Home fail to start. This is the TV's home screen; a crash means a TV with
   no home screen.

## What I want back, in this order

1. **What is achievable with theme settings alone** (no rebuild, instant to try) — give me a
   complete `config.json` using only keys from `themes/README.md`, and say what each choice does
   visually and what it costs.
2. **What needs code**, as a short list ranked by visual payoff ÷ risk. For each: the files you
   would touch, roughly what changes, the memory and GPU cost, and what could break.
3. **Your recommended plan**, split into "do now" and "only if I want to go further".
4. Then stop and let me choose before you write code.

Design ideas that cost nothing are worth more to me than ideas that cost memory. If the honest
answer to something is "that will look great and cost 15 MB", say so plainly and let me decide —
do not quietly make it lighter and call it done, and do not oversell a change you have not
measured.

## How to verify on my actual TV

ADB over the network is already working:

```bash
TV_HOST=192.168.0.236 tools/venv/bin/python -I tools/tv.py --probe          # the TV
TV_HOST=192.168.0.236 tools/theme.sh <theme folder>                          # push a theme
TV_HOST=192.168.0.236 tools/theme.sh --reset                                 # undo it
cd launcher && TV_HOST=192.168.0.236 ./build-and-install.sh                   # rebuild + install
```

Build environment (needed for the two build commands):
```bash
export JAVA_HOME=~/.sdkman/candidates/java/17.0.20-tem
export ANDROID_HOME=/opt/homebrew/share/android-commandlinetools
```

Measure memory before and after any change, and show me both numbers:
```bash
TV_HOST=192.168.0.236 tools/venv/bin/python -I tools/tv.py 'dumpsys meminfo com.gathin.tvhome' | grep TOTAL
```

`tools/tv.py` takes a screenshot too, so check your own work visually rather than asking me to
describe what I see.

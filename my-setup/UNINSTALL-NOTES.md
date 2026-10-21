# CleanYourTV — what was installed, and how to remove it

Session: 2026-10-21. TV: Xiaomi MiTV-AXSO0 (`dangal`), Android 9 / SDK 28, firmware PI.6036,
at 192.168.0.236. Repo: this clone, on `main` @ 42a9419.

Committed to this fork on branch `horizon-home-1b`, under `my-setup/`. See `my-setup/README.md`
for the restore steps; this file is the inventory of what was installed and changed.

---

## 1. Installed on this Mac

| What | Where | Size | Remove with |
|---|---|---|---|
| Temurin JDK 17.0.20 | `~/.sdkman/candidates/java/17.0.20-tem` | 309 MB | `sdk uninstall java 17.0.20-tem` |
| Android command-line tools | `/opt/homebrew/share/android-commandlinetools` | 524 MB total | `brew uninstall --cask android-commandlinetools` |
| ├─ `platforms;android-34` | `.../platforms/` | 126 MB | removed by the above |
| ├─ `build-tools;34.0.0` | `.../build-tools/` | 187 MB | removed by the above |
| Gradle 8.9 + dependency cache | `~/.gradle` | 603 MB | `rm -rf ~/.gradle` |
| Build output (gitignored) | `launcher/app/build`, `launcher/.gradle` | 15 MB | `rm -rf launcher/app/build launcher/.gradle` |
| (cask metadata) | `/opt/homebrew/Caskroom/android-commandlinetools` | 12 KB | removed by the above |
| Python venv for the repo tools | `tools/venv/` (gitignored) | ~40 MB | `rm -rf tools/venv` |

Notes:
- JDK 17 was installed **without** being made default. `java` is still Temurin 21.0.10.
  Nothing in your shell changed; the build takes `JAVA_HOME` explicitly.
- The cask linked ~20 binaries into `/opt/homebrew/bin` (`sdkmanager`, `apkanalyzer`, `r8`,
  `retrace`, `screenshot2`, `android`, …). `brew uninstall --cask` unlinks them all.
- **Total added: ~1.45 GB** (measured, not estimated). Disk went 122 GB -> 121 GB free.
- Google's Android SDK licences were accepted on 2026-10-21 and written to
  `/opt/homebrew/share/android-commandlinetools/licenses/` (8 files). Removed with the cask.
- `launcher/local.properties` was created (gitignored) pointing `sdk.dir` at the SDK root.
- The launcher APK built successfully: 438,855 bytes (429 KB), Gradle 8.9 + JDK 17, 2m 7s.

## 2. Created outside the repo

| What | Where | Why it matters |
|---|---|---|
| Recovery record (active) | `~/.cleanyourtv/recovery-192.168.0.236-9ba466c0.json` | **Needed to undo the debloat.** Do not delete before restoring. |
| The applied debloat list | `~/.cleanyourtv/debloat-akshay.txt` | Must stay at this exact path — the record is keyed to the sha1 of it. |
| Stale record (superseded) | `~/.cleanyourtv/recovery-192.168.0.236-fc9ef6b4.json` | Keyed to a temp path that no longer exists. Safe to delete. |

The list originally lived in a session scratchpad, which gets cleaned up. Both the list and a
re-keyed copy of the record were moved to `~/.cleanyourtv/` so the undo survives. Verified working.

## 3. Changed on the TV

**20 packages disabled** (`pm disable-user`). See `~/.cleanyourtv/debloat-akshay.txt`.

Verified to survive a reboot on 2026-10-21: nothing was re-enabled by the firmware at boot,
and Home stayed with `com.google.android.tvlauncher`.

**Prime Video** (`com.amazon.amazonvideo.livingroom`) was disabled on request. It is a system
app updated into `/data/app` with 11 split APKs, so it cannot be truly uninstalled without
root. It was appended to the debloat list first, so its pre-change state ("enabled") is in the
recovery record and `restore.sh` will bring it back.

**SonyLIV** (`com.sonyliv`) was UNINSTALLED on request -- `pm uninstall`, a genuine removal
(it was user-installed in `/data/app`, not a system app). This is OUTSIDE the recovery record:
`restore.sh` only runs `pm enable` and will NOT bring it back. Reinstall from the Play Store if
wanted; its login and downloads are gone.

**Play Movies & TV** (`com.google.android.videos`) needed no action -- it was already disabled
before this session started, and the recovery record preserves that, so `restore.sh` leaves it
disabled rather than wrongly enabling it.

Deliberately **kept enabled**: casting — `com.google.android.apps.mediashell` (Chromecast
built-in), `com.mitv.milinkservice` (Mi Cast), `com.xiaomi.mitv.smartshare`,
`com.xiaomi.wfdsinkhelperservice` (Miracast).

Also disabled, worth knowing: `com.xiaomi.mitv.updateservice` — **the TV no longer checks for
firmware updates.** Re-enable it temporarily when you want one:
`TV_HOST=192.168.0.236 tools/venv/bin/python -I tools/tv.py 'pm enable com.xiaomi.mitv.updateservice'`

And `com.google.android.katniss` + `com.google.android.speech.pumpkin` — **the remote's mic
button no longer works.**

**The replacement launcher IS now installed** (`com.gathin.tvhome`) and owns Home. The stock
launcher `com.google.android.tvlauncher` was disabled by `build-and-install.sh` as part of the
handover. Measured: new launcher 23 MB resident vs stock launcher 74 MB.

The install also granted `android.permission.ACCESS_FINE_LOCATION` to `com.gathin.tvhome`
(used only by the sunrise/sunset backdrop, which is switched OFF in this setup). Revoke with:
`pm revoke com.gathin.tvhome android.permission.ACCESS_FINE_LOCATION`

Personal theme pushed from `~/.cleanyourtv/theme-akshay/config.json`: greeting name "Akshay",
dock = Hotstar / YouTube / Netflix / VLC, Live TV = `com.android.tv`, plain black, no wallpaper,
stats and advanced effects off. Undo the theme alone with `tools/theme.sh --reset`.

Performance changes applied 2026-10-21:
- Animation scales set to 0.5 (from 1.0). `restore.sh` resets these.
- Force-stopped Netflix, YouTube, Hotstar, Play Store. NOT permanent -- they return on reboot.
- Play Store auto-update was NOT changed: it is not settable over ADB. Do it on the TV at
  Play Store > profile > Settings > Network preferences > Auto-update apps.

### Undo the launcher only

```
TV_HOST=192.168.0.236 tools/venv/bin/python -I tools/tv.py 'pm enable --user 0 com.google.android.tvlauncher'
TV_HOST=192.168.0.236 tools/venv/bin/python -I tools/tv.py 'cmd package set-home-activity --user 0 com.google.android.tvlauncher/.MainActivity'
TV_HOST=192.168.0.236 tools/venv/bin/python -I tools/tv.py 'pm uninstall com.gathin.tvhome'
```

### Undo everything on the TV

```
cd <this repo>
TV_HOST=192.168.0.236 tools/restore.sh ~/.cleanyourtv/debloat-akshay.txt
```

Re-enables 19, leaves the 11 that were already disabled or absent as they were, and resets Home
and the animation scales. Then cold-boot the TV.

### Close ADB when finished

On the TV: Developer options -> USB debugging off, revoke authorisations, reboot. Then verify:
```
tools/venv/bin/python -I tools/adb-closed.py 192.168.0.236
```
Port 5555 is currently **open**. `ro.adb.secure=1` on this set, so a key is still required.

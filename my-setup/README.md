# my-setup — Akshay's TV, and how to put it back

Everything personal to one TV lives here, so the rest of the fork stays a clean diff against
upstream. Nothing in this folder is read by the launcher at build time.

**Set up on 21 October 2026.** The point of this folder is that the laptop it was done from will
not be around forever: with this folder and the repo, the whole setup can be rebuilt or undone
from any machine.

## The TV

| | |
|---|---|
| Model | Xiaomi MiTV-AXSO0 (`dangal`), sold as Mi TV 4A Pro / 4C Pro 2019 |
| OS | Android TV 9, SDK 28, firmware PI.6036 |
| Chip | Amlogic `txlx` |
| RAM | ~1 GB (1,014,724 kB) |
| Screen | 1280x720, density 213 |
| Upstream list it matches | `examples/xiaomi-mitv-axso0/debloat.txt` (same model AND same firmware) |

The IP recorded in these files (192.168.0.236) was a DHCP address on a home LAN and is almost
certainly stale. Re-discover the TV rather than trusting it.

## What is in here

| Path | What it is |
|---|---|
| `UNINSTALL-NOTES.md` | Everything installed on the laptop and changed on the TV, with the removal command for each. **Read this first if you are undoing all of it.** |
| `recovery/debloat-akshay.txt` | The exact debloat list applied — the upstream AXSO0 list with casting commented out and Prime Video appended |
| `recovery/recovery-*.json` | The state of all 31 packages BEFORE they were disabled. `restore.sh` replays this. Without it, a restore wrongly enables packages that were already disabled |
| `theme/config.json` | The launcher theme: dock, greeting name, Live TV app, and the Horizon look |
| `design-handoff/` | The design brief the Horizon layout was built from. Open the `.dc.html` files in a browser (`support.js` is their runtime) |
| `screenshots/` | Before and after, captured from the TV |
| `smarttube.md` | SmartTube, the ad-free YouTube client **currently on trial**. Signing-certificate hash to check future updates against, and how to keep or remove it |

## Restoring the TV to stock

The recovery record is keyed to the **absolute path** of the debloat list (sha1 of it), so put both
files back where they were before restoring:

```bash
mkdir -p ~/.cleanyourtv
cp my-setup/recovery/debloat-akshay.txt ~/.cleanyourtv/
cp my-setup/recovery/recovery-*.json ~/.cleanyourtv/
```

The recorded filename encodes the TV's IP (`recovery-<ip>-<hash>.json`). On a different IP the
record will not be found and `restore.sh` falls back to enabling the whole list, which is cruder
but still safe. Then:

```bash
python3 -m venv tools/venv && tools/venv/bin/pip install -r tools/requirements.txt
TV_HOST=<tv ip> tools/restore.sh ~/.cleanyourtv/debloat-akshay.txt   # packages + Home + animation scales
TV_HOST=<tv ip> tools/venv/bin/python -I tools/tv.py 'pm uninstall com.gathin.tvhome'
```

Then cold-boot the TV.

**`restore.sh` does not reinstall anything that was uninstalled.** On this TV that is SonyLIV
(`com.sonyliv`), removed on request; reinstall it from the Play Store. Prime Video was only
disabled, so the restore does bring it back.

## Rebuilding the launcher

```bash
export JAVA_HOME=<a JDK 17>
export ANDROID_HOME=<Android SDK with platforms;android-34 and build-tools;34.x>
cd launcher && TV_HOST=<tv ip> ./build-and-install.sh
TV_HOST=<tv ip> tools/theme.sh my-setup/theme      # push the theme
TV_HOST=<tv ip> tools/theme.sh --reset             # or drop back to the built-in look
```

## Things that do not survive a reboot

- Netflix, YouTube and Hotstar were force-stopped to free memory. They are preinstalled system
  apps and start again on every boot. The animation scales (0.5) and the disabled packages do
  persist.
- Play Store auto-update was **not** turned off: it is not reachable over ADB. Do it on the TV at
  Play Store → profile → Settings → Network preferences → Auto-update apps.

## Still open

- **SmartTube is on trial** (installed 21 Oct 2026, decide around 24 Oct). See `smarttube.md`.

- Network ADB (port 5555) was left **open** on the TV. Close it: Developer options → USB debugging
  off → revoke authorisations → reboot, then check with `tools/adb-closed.py <tv ip>`.
- The launcher holds `ACCESS_FINE_LOCATION`, granted by `build-and-install.sh` for the
  sunrise/sunset backdrop, which this setup does not use. Revoke with
  `pm revoke com.gathin.tvhome android.permission.ACCESS_FINE_LOCATION`.

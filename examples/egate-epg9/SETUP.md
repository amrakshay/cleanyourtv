# Cleaning this projector — step by step

For an **E-Gate EPG9 / EGP9 "Atom 2X Plus"** projector whose firmware matches the one in
[`README.md`](README.md). Done once on a real unit on 30 October 2026; this is that run, written
down so someone else can repeat it.

You need a computer on the same Wi-Fi as the projector, `git` and `python3`, and a coding assistant
with shell access (Claude Code, or similar).

> **Check the model first.** The box may say EPG9 or EGP9, but the firmware calls itself
> `t950s_be311` and is an Amlogic Android 13 build — nothing like the Android 11 / Allwinner H713
> the vendor page advertises. Step 3 verifies this before anything is changed. If your projector
> reports something else, **stop** — this list was written for one firmware and was not tested on
> any other.

---

## 1. On the projector: turn on USB debugging

1. **Settings → About** (scroll to the bottom of the settings list).
2. Highlight **Build** / **Build number** and press **OK seven times**. A message says you are now a
   developer.
3. Go **back**, open **Developer options**.
4. Turn **USB debugging** on.
5. If you also see **Network debugging**, **ADB over network** or **Wireless debugging**, turn that
   on too. (On the unit this was written from, ADB was already listening on the network with just
   USB debugging on — `service.adb.tcp.port` is set to 5555 in the firmware.)

Leave the projector awake. It drops the ADB connection when the lamp sleeps.

## 2. Find the projector's IP

**Settings → Network** on the projector shows it. It will look like `192.168.0.138`.

## 3. Paste this into your assistant

Replace `<PROJECTOR-IP>` with the address from step 2, and run it from wherever you keep code.

---

```
I have an E-Gate EPG9 / EGP9 "Atom 2X Plus" Android projector at <PROJECTOR-IP> and I want to
debloat it. Work in a fresh directory.

Setup:
1. git clone https://github.com/amrakshay/cleanyourtv.git
2. cd cleanyourtv && git checkout projector-hardware-guard
3. python3 -m venv tools/venv && tools/venv/bin/pip install -r tools/requirements.txt
4. Read examples/egate-epg9/README.md and examples/egate-epg9/debloat.txt before doing anything.

VERIFY THE FIRMWARE FIRST, and stop if it does not match:
   TV_HOST=<PROJECTOR-IP> tools/venv/bin/python -I tools/tv.py --probe
Expect ro.product.model = t950s_be311 and ro.build.version.release = 13. If either differs, STOP
and tell me what it reported instead — the list below was written for one firmware only.
Accept the "Allow USB debugging?" prompt on the projected image if it appears.

Then, in this order, telling me the result of each step:

A. Apply the debloat list (22 system packages, disabled not uninstalled):
     TV_HOST=<PROJECTOR-IP> tools/disable.sh examples/egate-epg9/debloat.txt
   Then press HOME and confirm the launcher still starts:
     tools/venv/bin/python -I tools/tv.py 'input keyevent KEYCODE_HOME; sleep 4; dumpsys window | grep mCurrentFocus'
   It must show com.htc.htclauncherhighenglishd08. If it shows FallbackHome, immediately run
     TV_HOST=<PROJECTOR-IP> tools/restore.sh examples/egate-epg9/debloat.txt com.htc.htclauncherhighenglishd08
   and tell me.

B. Uninstall the sideloaded junk — but BACK EACH APK UP FIRST to a local folder outside the repo
   (pm path <pkg>, then tools/tv.py --pull <path> <local>.apk, and verify each saved file opens as
   a zip containing AndroidManifest.xml before uninstalling anything):
     com.abc.ninja is NOT in this list - it is a system app and stays disabled, not uninstalled.
     Uninstall: com.unitvnet.tvod, com.world.youcinetv, com.nmvdo.tv,
                com.seraphic.openinet.jiumao, com.overseas.store.appstore,
                com.master.tv.market, com.master.accessibility, com.ht1.launcher
   Some of these may not be present on every unit - skip any that are missing, do not error out.

C. Free up storage. The firmware keeps installer copies of all this under /data/preinstall and
   /data/preutv. Delete ONLY the .apk files in those two folders and KEEP the `installed.is` marker
   file in each. The marker is what stops the firmware re-extracting ~400 MB from tarballs in
   /system at the next boot - delete the folder and it all comes back.
     rm -f /data/preinstall/*.apk
     rm -f /data/preutv/*.apk
   Then confirm both installed.is files still exist and report df -h /data before and after.

D. Final check: press HOME, confirm the launcher starts, and confirm these are still ENABLED:
     com.softwinner.tcorrection   (keystone - never disable this)
     com.droidlogic.tvinput       (all HDMI/AV inputs)
     com.htc.htcsettings          (settings, holds the ADB toggle)
     com.jm.jmlauncher            (the stock launcher does not start without it)

DO NOT touch: Prime Video (com.amazon.avod.thirdpartyclient) or MX Player
(com.mxtech.videoplayer.ad) - leave both installed and enabled.
DO NOT install VLC - its audio output does not work on this firmware (verified on two versions).
MX Player is the working video player here.

Everything in step A is reversible with tools/restore.sh. Ask me before anything not listed above.
```

---

## 4. When you are done

**Turn USB debugging and network debugging back off** in Developer options, and reboot the
projector.

This matters more than usual on this firmware: the ADB shell runs as **root** (`uid=0`), the build
is `userdebug` with `ro.debuggable=1`, `/system/xbin/su` is present and `ro.adb.secure` is unset.
While debugging is on, anyone on the same network who connects to port 5555 gets a root shell.

## What this actually does

| | |
|---|---|
| Disables | 22 system packages — a silent installer, two accessibility packages, Google phone leftovers, the Amlogic bundled media apps and the recommendation feeder |
| Uninstalls | up to 8 sideloaded apps — two app stores, four IPTV front-ends, an accessibility helper and a spare launcher |
| Frees | ~400 MB of staging APKs, plus whatever the uninstalls return |
| Leaves alone | the launcher, keystone, HDMI inputs, settings, Play, Netflix, YouTube, Chrome, Prime Video, MX Player |

The single best reason to run it: **`com.abc.ninja`** (in `/system/app/NetflixNinja`) is *granted*
both `INSTALL_PACKAGES` and `WRITE_SECURE_SETTINGS`, has a boot receiver, and registers no launcher
activity. It can install an app with no prompt and switch on an accessibility service. Step A
disables it.

**A factory reset undoes all of this**, and brings `com.abc.ninja` back enabled, because the
installer copies live in `/system` as tarballs. Re-run the list before putting a reset projector
back on the network.

## If something looks wrong

```bash
TV_HOST=<PROJECTOR-IP> tools/restore.sh examples/egate-epg9/debloat.txt com.htc.htclauncherhighenglishd08
```

That re-enables everything the list disabled and puts HOME back. It reports "Unknown package" for
anything that was uninstalled in step B — those come back only by reinstalling the saved APKs,
which is why step B backs them up first.

See [`../../docs/TROUBLESHOOTING.md`](../../docs/TROUBLESHOOTING.md) for a blank home screen, a dead
HDMI input, or a crooked picture.

## Optional: a much brighter picture

Worth checking on any unit of this model. Read:

```bash
TV_HOST=<PROJECTOR-IP> tools/venv/bin/python -I tools/tv.py 'getprop | grep -iE "keystone|trapezoid"'
```

On the unit this was written from, `persist.keystone.zoom.percent` was **54** — the image was
digitally shrunk into about a quarter of the panel, throwing away roughly three quarters of the
light. Setting **Zoom in/out** back to off/100% in the projector's Projection Settings and moving
the projector physically closer to get the size you want gave about **3× more light on the wall**,
because shrinking optically keeps all the lumens while digital zoom discards them.

`persist.keystone.vertical.degree` shows how much keystone correction is applied. Correction crops
the image further and also makes focus uneven, since a tilted projector can only be sharp at one
distance. Levelling the projector and zeroing the correction recovers the rest — but **only zero the
keystone after the projector is physically level**, or you get a trapezoid instead of a rectangle.

# E-Gate EPG9 / EGP9 "Atom 2X Plus" (Amlogic t950s_be311, Android 13)

**Status: 22 packages applied and the home screen verified, 30 October 2026. Not lived with, and not
yet seen through a reboot.** It does not belong in the table in `examples/README.md` until it has
been — see CONTRIBUTING, rule 3.

## The blank home screen, and what it rules out

A first run disabled 23 packages. Everything reported `disabled-user`, the stock launcher stayed
enabled and `resolve-activity` still named it as the HOME handler — and the next press of HOME
landed on `com.android.tv.settings/.system.FallbackHome`, a blank screen. `tools/restore.sh` undid it
in one command, including putting HOME back, and left `com.mbox.accessibility` disabled because the
recovery record knew the factory had already disabled it.

Testing the three one at a time — disable, `am force-stop` the launcher, press HOME — named the cause:
**`com.jm.jmlauncher`**. Without it the stock launcher does not start, although it stays enabled and
still resolves as the HOME handler. `com.master.apps` and `com.google.android.tvrecommendations` are
cleared by the same test and are in the list.

Both launchers run in the shared user `android.uid.system` (uid 1000) and carry the same vendor's
names (`JmLauncher`, `JMFactory`), so the "HTC" launcher is a front for JM code rather than a
self-contained app. Re-enabling `com.jm.jmlauncher` brought the home screen back immediately.

The lesson for firmware like this — unbranded, undocumented, vendor-mixed — is to apply a list in
batches with a HOME check between them, not in one go.

## What the firmware actually is

| | |
|---|---|
| `ro.product.model` / `ro.product.device` / board | `t950s_be311` |
| `ro.board.platform` | `txhd2` (Amlogic; every vendor app is `com.droidlogic.*`) |
| Android | 13, SDK 33, build `be311-13 TQ2A.230405.003.E1-1750240472` |
| `ro.product.manufacturer` / brand | `Google` — a generic AOSP TV build, no E-Gate string anywhere |
| `ro.build.characteristics` | `tv,nosdcard` |
| Stock launcher | `com.htc.htclauncherhighenglishd08` (nothing to do with HTC), the only app answering HOME |
| Inputs | `com.droidlogic.tvinput` serves HDMI 1–4, AV 1–2, ARC, SPDIF, AUX and the tuners |
| Keystone | `com.softwinner.tcorrection`, activity `.projection.ProjectionSettingActivity` |
| ADB | USB debugging on, `service.adb.tcp.port=5555`, `ro.adb.secure` unset |

The vendor's product page for the Atom 2X Plus claims Android 11 on an Allwinner H713 with 1 GB /
8 GB. The device reports Android 13 on an Amlogic board. Take the rest of that page's specifications
the same way.

## Why this one is worth doing

115 system packages and 14 third-party ones, among them:

- **`com.abc.ninja`** — holds `android.permission.INSTALL_PACKAGES` (the privileged one, not the
  "ask the user" variant), plus `INTERNET` and a boot receiver, and registers no launcher activity
  at all. That is the shape of a silent installer.
- **`com.master.accessibility`** and **`com.mbox.accessibility`** — two accessibility-service
  packages. Neither is enabled right now (`enabled_accessibility_services` is null, and mbox ships
  disabled), and an accessibility service is the usual way an installer on these boxes taps
  "Install" for itself.
- **`com.koushikdutta.superuser`** — a root manager, preinstalled as a *system* app. Disabling it
  does not remove whatever `su` it manages. It says what kind of firmware this is.
- Four sideloaded IPTV/streaming front-ends and two sideloaded app stores.
- No device admin is active and no accessibility service is on, so none of the above is doing
  anything at this moment. They are all installed and able to start at boot.

## Uninstalled, not just disabled (30 October 2026)

Eight of the listed packages live in `/data`, so they are not part of the system image and `pm
uninstall` removes them for good — a factory reset will not bring them back either. They were backed
up first (`tools/tv.py --pull <path from "pm path"> <local>.apk`, each verified as a readable zip
with a manifest and dex before anything was removed) and then uninstalled:

`com.unitvnet.tvod`, `com.world.youcinetv`, `com.nmvdo.tv`, `com.seraphic.openinet.jiumao`,
`com.overseas.store.appstore`, `com.master.tv.market`, `com.master.accessibility`, `com.ht1.launcher`.

`/data` went from 70% to 65% full, about 248 MB back on a 4.5 GB partition. The remaining 14 entries
in the list are system packages in `/system`, `/vendor`, `/product` and `/system_ext`: they stay
disabled, because without root the most `pm uninstall -k --user 0` does is hide them from user 0
while the APK stays in the image, and that has a messier undo than `pm enable`.

Two consequences:

- `tools/restore.sh` will fail on those eight with "Unknown package" and carry on with the rest. They
  can only come back by reinstalling the saved APKs.
- **A factory reset wipes the eight but brings `com.abc.ninja` back, enabled**, since it is in the
  system image — and that is the package granted `INSTALL_PACKAGES` and `WRITE_SECURE_SETTINGS`. Run
  this list again before putting a reset projector on the network.

## Keystone

`com.softwinner.tcorrection` is the one package here that must not be disabled by accident, and its
name gives no hint — only its activity does. `tools/disable.sh`'s projector guard now catches
`correction` for exactly this reason; before this device it did not.

## A better home screen, cheaply

`com.google.android.leanbacklauncher` is installed and enabled. Pointing HOME at it replaces the
stock launcher without building anything:

```bash
TV_HOST=<ip> tools/tv.py 'cmd package set-home-activity com.google.android.leanbacklauncher/.MainActivity'
```

`tools/restore.sh` puts HOME back to whatever the recovery record holds.

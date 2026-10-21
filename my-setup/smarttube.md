# SmartTube — ad-free YouTube client (ON TRIAL)

**Status: trialling.** Installed 21 October 2026, to be judged after a few days of use
(review around 24 October 2026). Keep or remove — see both paths at the bottom.

Installed because YouTube's own app shows too many ads. SmartTube is an MIT-licensed, open-source
YouTube client for Android TV that plays videos without them. The stock YouTube app was **left
installed** so the two can be compared side by side.

## What is installed

| | |
|---|---|
| Package | `org.smarttube.stable` |
| Version | 32.68 stable (versionCode 2458), released 20 Oct 2026 |
| Variant | `armeabi-v7a` — **this TV is 32-bit ARM only** (`ro.product.cpu.abi`), the arm64 build will not install |
| Source | https://github.com/yuliskov/SmartTube/releases/tag/32.68s |
| File | `SmartTube_stable_32.68_armeabi-v7a.apk`, 25,135,011 bytes |
| File SHA-256 | `2130b23b17ed5cfd324baec81750a2be22059212b6ee17449f21cae2cb3a60d9` |
| Signer | `CN=Yurii L, OU=Android Development, O=SmartTube, C=US` |
| **Signing cert SHA-256** | **`109735aa24fe85e2e1623ebb3b1ecc4bf4263f4c6374e4411d646bfa2eda482a`** |
| minSdk / target | 17 / 34 (this TV is SDK 28) |
| Installed | 2026-10-21 22:12 |
| Signed in? | **No — deliberately signed out.** See below. |

It sits as the last tile of the second row on the Home screen. That needed no configuration: the
launcher sorts tiles it has no saved rank for after every ranked one, so a new install lands last
on its own.

## Why the certificate hash above matters

In **late November 2025 the developer's app signing key was stolen.** Attackers signed malicious
builds with it and pushed them out as a normal update; the payload (`libalphasdk.so`) collected
device info, installed apps and IP addresses, and Play Protect force-disabled the app on many TVs.

The source code was never the problem — the *signing key* was. So "open source" alone does not
protect you here: almost nobody compiles it themselves, and a prebuilt APK is only as trustworthy
as the key that signed it.

The developer has since rotated to a new key, which **changed the app ID**:

| | |
|---|---|
| Old, compromised lineage | `com.liskovsoft.smarttubetv` |
| Current | `org.smarttube.stable` ← what is installed here |

**Before installing any future update, check its signer against the hash above:**

```bash
$ANDROID_HOME/build-tools/34.0.0/apksigner verify --print-certs <new.apk> | grep SHA-256
```

A different signer on something claiming to be SmartTube is exactly what the 2025 attack looked
like. **Only ever download from the official GitHub releases page** — never an APK mirror or
"app store" site, which is how most people were caught out.

### F-Droid: safer provenance, but stale

F-Droid builds SmartTube from source on its own servers with its own key, which does not depend on
the developer's machine staying uncompromised. But its build was **31.30 (March 2026)** when
checked on 21 Oct 2026, and its reproducibility page showed recent rebuild attempts failing. Since
YouTube actively breaks these clients, a build that old risks simply not working. That is why
GitHub was chosen here. Revisit if F-Droid catches up.

## Signed out, on purpose

Sign-in uses a device-code flow (a code entered at `youtube.com/activate`), so the Google password
is never typed into the TV. But it leaves an **access token on the TV**, inside a sideloaded app
whose signing key was compromised once already. Signed out, there is no token there to steal.

The cost: no subscriptions, history, recommendations or playlists. The project's own FAQ also warns
that signed-out users can hit "Sign in to confirm you're not a bot" errors, because YouTube blocks
some IP ranges for anonymous viewers. (Not corroborated outside the project's own FAQ.)

**If sign-in becomes necessary, use a secondary Google account**, not the main one — the token on
the TV then has nothing of consequence behind it. Anything granted can be reviewed and revoked at
Google Account → Security → Third-party apps.

## Things to judge during the trial

- Are the ads actually gone — pre-roll, mid-roll and banner?
- Is playback smooth on 1 GB of RAM, and how much memory does it hold versus the stock app?
  (`dumpsys meminfo org.smarttube.stable`)
- Is anything missed by being signed out?
- **SponsorBlock** — a separate feature in SmartTube's own settings that skips in-video sponsor
  segments. Distinct from ad-blocking; worth switching on to evaluate properly.

## If keeping it

Swap it into the dock in place of YouTube by editing `my-setup/theme/config.json`:
replace `com.google.android.youtube.tv` with `org.smarttube.stable` in `dock_apps`, then
`TV_HOST=<tv ip> tools/theme.sh my-setup/theme`. Consider hiding or disabling the stock YouTube
app at that point. Update this file to drop the "ON TRIAL" status.

## If removing it

```bash
TV_HOST=<tv ip> tools/venv/bin/python -I tools/tv.py 'pm uninstall org.smarttube.stable'
```

Nothing else was changed for it — no theme edit, no package disabled, no permission granted. The
tile disappears on its own once the app is gone, and this file can be deleted.

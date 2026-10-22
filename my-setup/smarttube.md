# SmartTube — tried, and removed

**Installed 21 October 2026, uninstalled 22 October 2026.** Not kept.

An MIT-licensed, open-source YouTube client for Android TV that plays videos without ads, trialled
because the stock YouTube app shows too many. Removed after a day: not liked. No reason recorded
beyond that.

Kept here only so the decision is not re-tread later.

## What it was, if it is ever reconsidered

| | |
|---|---|
| Package | `org.smarttube.stable` (the old, compromised lineage was `com.liskovsoft.smarttubetv`) |
| Version trialled | 32.68 stable, `armeabi-v7a` — **this TV is 32-bit ARM only**, the arm64 build will not install |
| Source | https://github.com/yuliskov/SmartTube/releases — **official GitHub only**, never an APK mirror |
| Signing cert SHA-256 | `109735aa24fe85e2e1623ebb3b1ecc4bf4263f4c6374e4411d646bfa2eda482a` |

**Why that certificate hash is written down:** in November 2025 the developer's signing key was
stolen and used to push malicious builds. The source was never the problem, so "open source" alone
was no protection — what matters is whether the APK was signed by the key you expect. Verify any
future build with
`apksigner verify --print-certs <apk> | grep SHA-256` before installing.

It was run **signed out** throughout, so no Google account token was ever placed on the TV.

## Removal left nothing behind

`pm uninstall org.smarttube.stable` was the whole job: no theme change, no disabled package, no
permission granted, no leftover files. The stock YouTube app was never touched and is still there.

## The ad problem is still unsolved

The reason for trying this has not gone away. The remaining options:

- **YouTube Premium Lite**, about Rs 89/month in India — ad-free video, no YouTube Music, no
  downloads, no background play. **YouTube Premium** is about Rs 149/month for the full thing.
- DNS-level blocking (Pi-hole, AdGuard DNS, NextDNS) **does not work** for YouTube: ads come from
  the same `googlevideo.com` hosts as the video, and DNS can only allow or block a whole domain.
  Do not spend time on it.

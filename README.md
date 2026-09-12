# AQUASTRAP
JOIN THE BEST AT
[OUR DISCORD](https://discord.gg/X7kqQWMPjG)
**The best strap. Ever.** 🌧️

Aquastrap is a cozy, pixel-rain-soaked launcher and Fast Flag manager for
[Sober](https://github.com/vinegarhq/Sober) (the Roblox compatibility layer)
on Linux. Point, click, paste flags, launch — while the CRT warms up and the
waves roll by.

Built with Python and Tkinter. One application,
automatic updates.

---

## Install

One command. Copy it. Run it.

```bash
curl -fsSL https://raw.githubusercontent.com/dime-scripts/Aquastrap/refs/heads/main/installer.sh | bash
```

No `curl`? Use `wget`:

```bash
wget -qO- https://raw.githubusercontent.com/dime-scripts/Aquastrap/refs/heads/main/installer.sh | bash
```

What the installer does (no root required):

- installs the launcher to `~/aquastrap/main.py`
- adds an **Aquastrap** entry to your application menu
- on first launch, the launcher downloads the full application itself

Then start Aquastrap from your app menu, or:

```bash
python3 ~/aquastrap/main.py
```

### Prerequisites

A Debian/Ubuntu-based desktop (Linux Mint, Debian, Ubuntu, Pop!\_OS, …) with:

- `python3` with Tk (`python3-tk`) — the installer-era app sets itself up
- `flatpak`
- Sober (`org.vinegarhq.Sober`) from Flathub

```bash
sudo apt-get install -y python3-tk python3-venv flatpak
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
flatpak install -y flathub org.vinegarhq.Sober
```

---

## Features

- **One-click launch** — runs `flatpak run org.vinegarhq.Sober` and tracks it
- **Fast Flags manager** — add flags in a table, save profiles, import/export
  - import from a **link**, a **file**, or **clipboard paste**
  - copy the JSON or export `ClientAppSettings.json`
- **Smart configuration tab** — paste raw flags, hit APPLY. Aquastrap wraps
  them into the full, official Sober `config.json` and places every flag in
  the `"fflags"` block automatically. All Sober defaults and the warning
  header are preserved; nothing else is touched
- **Profiles** saved under `~/aquastrap/savedfastflags`
- **Settings tab** — automatic updates on/off, reset config, open data
  folders, runtime status, links to the repository and Sober docs
- **Automatic updates** — checks the repository on launch, downloads the
  newest build and restarts itself
- **Nostalgic loading screen** — pixel rain, snow, animated waves, a progress
  bar, and a programmer sleeping somewhere
- Pixel font, late-night color palette, animated everywhere

---

## How flags work

Sober regenerates the Roblox client settings itself on every launch from the
`fflags` object in:

```
~/.var/app/org.vinegarhq.Sober/config/sober/config.json
```

Aquastrap writes your flags exactly there, so they survive every launch and
update. You never edit the Roblox folders by hand.

Paste something like:

```json
{
  "DFIntTaskSchedulerTargetFps": 240,
  "FFlagDebugGraphicsPreferD3D11": true
}
```

hit **APPLY**, and Aquastrap produces a complete valid Sober configuration with
your flags nested inside `fflags`.

---

## Files

| Path | What it is |
| --- | --- |
| `~/aquastrap/main.py` | the launcher (always up to date) |
| `~/aquastrap/Main.py` | the full application, auto-downloaded |
| `~/aquastrap/savedfastflags/` | your flag profiles |
| `~/aquastrap/aquastrap.log` | logs |
| `~/.local/share/applications/aqua.desktop` | app menu entry |
| `~/.var/app/org.vinegarhq.Sober/config/sober/config.json` | Sober configuration |

---

## Updating

Nothing to do. Aquastrap checks for a new release on every startup and
installs it automatically. You can also press **CHECK FOR UPDATES NOW** in
Settings.

To reinstall the launcher:

```bash
curl -fsSL https://raw.githubusercontent.com/dime-scripts/Aquastrap/refs/heads/main/installer.sh | bash
```

---

## Troubleshooting

- **Window opens but text boxes won't type** — click inside the window once to
  focus it; the launcher strips the native title bar while keeping taskbar
  support
- **Sober exits with code 134** — your `config.json` is invalid. Open the
  Configuration tab, press **RESET config.json TO DEFAULT** in Settings, then
  re-apply your flags
- **Flags disappear after launching** — only happens with hand-edited
  Roblox files; let Aquastrap write flags (it uses the `fflags` block)
- **Menu icon missing** — launch Aquastrap once, then log out and back in so
  the desktop picks up the icon
- **Logs** — see `~/aquastrap/aquastrap.log`

---

## Links

- Repository: https://github.com/dime-scripts/Aquastrap
- Sober: https://vinegarhq.org
- Sober configuration docs: https://vinegarhq.org/Sober/Configuration/index.html

---
title: Install
summary: Raspberry Pi OS, one install script, a systemd service. Ten minutes once the hardware is wired.
---

## Requirements

- Raspberry Pi 4 (or Zero 2 W / 3B+) with Raspberry Pi OS Lite **64-bit** (Bookworm). Pi 5 is not supported yet because `pigpio` does not run on it.
- Network access on first install (pip, apt).
- I²C devices at 0x20, 0x39, 0x63 and a DS18B20 on GPIO 4.

## Install

```bash
sudo apt-get install -y git
git clone https://github.com/thetemplateblog/openreef.git
cd openreef/firmware/openreef_analyzer
./deploy/install.sh
```

The script enables I²C and 1-Wire, installs and starts `pigpiod`, creates `/opt/openreef` with a virtualenv, installs the package with the `rpi` and `mqtt` extras, copies `config.example.yaml` to `/etc/openreef/config.yaml` with `backend: rpi`, and installs and starts the `openreef` systemd service. The dashboard is then at `http://<pi>:8080`.

## Configure

Edit `/etc/openreef/config.yaml` (see [Configuration](/docs/software/configuration/)) and restart:

```bash
sudo nano /etc/openreef/config.yaml
/opt/openreef/.venv/bin/openreef check-config --config /etc/openreef/config.yaml
sudo systemctl restart openreef
journalctl -u openreef -f
```

Set an API key before exposing the port beyond your LAN:

```yaml
api:
  api_keys: ["$(openssl rand -hex 24)"]
```

## Update

```bash
cd ~/openreef && ./firmware/openreef_analyzer/deploy/update.sh
```

## Run without hardware

```bash
cd firmware/openreef_analyzer
./dev.sh                               # venv + install + simulator at http://localhost:8080
./dev.sh test                          # 8 tests, ~30 s
```

See [Simulator](/docs/software/simulator/).

## Files

| Path | Purpose |
|---|---|
| `/opt/openreef` | code + virtualenv |
| `/etc/openreef/config.yaml` | your configuration |
| `/opt/openreef/openreef.db` | SQLite results, runs, events, calibrations, reagent levels (WAL mode) |
| `/etc/systemd/system/openreef.service` | service unit; `ExecStopPost` disables the steppers |

Back up `openreef.db` and `config.yaml`; everything else is reproducible.

## Troubleshooting

| Symptom | Check |
|---|---|
| `pigpiod not running` | `sudo systemctl enable --now pigpiod` |
| `EZO-pH error code 2` | wrong I²C address or circuit in UART mode — short TX to PGND at power-up to switch to I²C |
| `AS7341 init failed` | STEMMA cable, 3V3, `i2cdetect` shows 0x39? |
| pH jumps when pumps run | EZO ground not isolated; move the carrier's GND off the 12 V return |
| Syringe runs to the far end on home | swap one motor coil pair (DIR sense) |
| `home switch not found` | switch wiring (NO to GND), MCP23017 port A pull-ups, `home_pin` in config |
| Dashboard empty, API 401 | API key in `localStorage` — open `http://<pi>:8080/?api_key=…` once |

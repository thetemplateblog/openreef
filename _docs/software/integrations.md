---
title: Hydros, MQTT & webhooks
summary: Getting results out of the analyzer and actions into your controller.
---

## Hydros (CoralVue)

CoralVue opened an official [developer API](https://www.coralvuehydros.com/api/) in 2026. You request a **Provider Key** from CoralVue and create a **Device Key** per controller in the Hydros app (*Device Properties → Manage API Keys*, "Read & write"). Requests authenticate with `Authorization: {provider_key}:{device_key}`. The [reference](https://developers.api.coralvuehydros.com/) documents device lookup, live state, logs/export, metadata and output overrides, with rate limits of 60/min for lookups, 10/min for state and overrides and 5 polling sessions per hour. Provider Keys are free through 2026 and remain free for up to 20 devices afterwards.

As documented, the API does **not** let a third party push sensor values into the controller. OpenReef therefore integrates in two directions:

### Rules → output overrides

```yaml
hydros:
  enabled: true
  provider_key: "…"
  device_key: "…"
  rules:
    - { when: "alk_dkh < 7.5", output: "Alk Doser", state: "on",  minutes: 30 }
    - { when: "alk_dkh > 9.8", output: "Alk Doser", state: "off", minutes: 360 }
    - { when: "po4_ppm > 0.2", output: "GFO Reactor", state: "on", minutes: 720 }
```

After every result the rules are evaluated and matching ones call the override endpoint for that output (never more than once a minute per output). Actions are logged as `hydros_action` events. The endpoint paths live in `openreef/integrations/hydros.py` (`DEFAULT_ENDPOINTS`) so they can be adjusted if the reference changes.

### Hardware alarm → Hydros Sense port

The analyzer's relay gives a dry contact; wire it to a Sense port configured as a float switch. Build rules in the Hydros app on "OpenReef alarm" — e.g. pause dosing, send a notification. This path needs no API key and works even when the Pi is offline (contact open = no alarm; invert in the app if you prefer fail-safe).

### Reading the controller

`GET /api/v1/hydros/state` proxies the controller's live state so the dashboard can show tank temperature and pH next to the chemistry. Polling is every 5 minutes by default (`hydros.poll_s`).

## MQTT and Home Assistant

```yaml
mqtt:
  enabled: true
  host: homeassistant.local
  username: openreef
  password: …
  base_topic: openreef
  ha_discovery: true
```

Topics: `openreef/alkalinity|phosphate|nitrate` (retained JSON result), `openreef/alarm` (`on`/`off`), `openreef/alert`, `openreef/progress`, `openreef/events/<type>`, `openreef/status` (`online`/`offline` with LWT). With discovery on, Home Assistant creates three sensors (dKH / ppm, `state_class: measurement`) and a `problem` binary sensor under one "OpenReef" device. Install the extra with `pip install openreef[mqtt]` (the install script does).

## Webhooks

```yaml
webhooks:
  - https://hooks.example.com/openreef
```

`result`, `alert`, `run_finished`, `reagent_low` and `calibration` events are POSTed as JSON to every URL with a 10 s timeout. Failures are logged and not retried.

## Prometheus / Grafana

Scrape `http://<pi>:8080/metrics`. A useful alert: `openreef_result_age_seconds{test="alkalinity"} > 8*3600` (a missed run).

## Other controllers

- **Neptune Apex**: no public inbound API; use the relay into a breakout-box input, or poll OpenReef's API from a bridge (e.g. Node-RED) and act through Apex's local REST endpoints.
- **Reef-Pi / Home Assistant automations**: consume MQTT or the REST API directly.
- **Google Sheets / spreadsheets**: `GET /api/v1/results/export.csv` on a schedule.

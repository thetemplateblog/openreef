"""MQTT publisher with Home Assistant discovery (optional: pip install openreef[mqtt])."""
from __future__ import annotations

import json
import logging
from typing import Any, Dict

from ..config import MqttConfig

log = logging.getLogger(__name__)

SENSORS = {
    "alkalinity": {"name": "Alkalinity", "unit": "dKH", "icon": "mdi:test-tube"},
    "phosphate": {"name": "Phosphate", "unit": "ppm", "icon": "mdi:test-tube"},
    "nitrate": {"name": "Nitrate", "unit": "ppm", "icon": "mdi:test-tube"},
}


class MqttBridge:
    def __init__(self, cfg: MqttConfig, device_id: str = "openreef"):
        self.cfg = cfg
        self.device_id = device_id
        self.client = None

    def start(self) -> None:
        import paho.mqtt.client as mqtt
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=self.device_id)
        if self.cfg.username:
            self.client.username_pw_set(self.cfg.username, self.cfg.password)
        self.client.will_set(f"{self.cfg.base_topic}/status", "offline", retain=True)
        self.client.connect(self.cfg.host, self.cfg.port, keepalive=60)
        self.client.loop_start()
        self.client.publish(f"{self.cfg.base_topic}/status", "online", retain=True)
        if self.cfg.ha_discovery:
            self._discovery()

    def stop(self) -> None:
        if self.client:
            self.client.publish(f"{self.cfg.base_topic}/status", "offline", retain=True)
            self.client.loop_stop()
            self.client.disconnect()

    def _discovery(self) -> None:
        dev = {"identifiers": [self.device_id], "name": "OpenReef", "manufacturer": "OpenReef",
               "model": "Analyzer"}
        for test, meta in SENSORS.items():
            topic = f"homeassistant/sensor/{self.device_id}_{test}/config"
            payload = {
                "name": meta["name"], "unique_id": f"{self.device_id}_{test}",
                "state_topic": f"{self.cfg.base_topic}/{test}", "value_template": "{{ value_json.value }}",
                "json_attributes_topic": f"{self.cfg.base_topic}/{test}",
                "unit_of_measurement": meta["unit"], "icon": meta["icon"],
                "availability_topic": f"{self.cfg.base_topic}/status", "device": dev,
                "state_class": "measurement",
            }
            self.client.publish(topic, json.dumps(payload), retain=True)
        self.client.publish(f"homeassistant/binary_sensor/{self.device_id}_alarm/config", json.dumps({
            "name": "OpenReef alarm", "unique_id": f"{self.device_id}_alarm",
            "state_topic": f"{self.cfg.base_topic}/alarm", "payload_on": "on", "payload_off": "off",
            "device_class": "problem", "availability_topic": f"{self.cfg.base_topic}/status", "device": dev,
        }), retain=True)

    async def handle_event(self, evt: Dict[str, Any]) -> None:
        if not self.client:
            return
        t = evt["type"]
        if t == "result":
            self.client.publish(f"{self.cfg.base_topic}/{evt['test']}", json.dumps(evt, default=str), retain=True)
        elif t == "alert":
            self.client.publish(f"{self.cfg.base_topic}/alarm", "on", retain=True)
            self.client.publish(f"{self.cfg.base_topic}/alert", json.dumps(evt, default=str))
        elif t == "progress":
            self.client.publish(f"{self.cfg.base_topic}/progress", json.dumps(evt, default=str))
        elif t in ("run_started", "run_finished", "reagent_low", "calibration"):
            self.client.publish(f"{self.cfg.base_topic}/events/{t}", json.dumps(evt, default=str))

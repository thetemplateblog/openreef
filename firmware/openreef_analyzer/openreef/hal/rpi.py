"""Raspberry Pi hardware backend.

Buses and devices
-----------------
* pigpio   - step pulse generation (DMA waveforms, accurate timing), GPIO for
             DIR/EN, LEDs, relay, leak sensor, heater PWM.
* I2C-1    - Atlas Scientific EZO-pH (0x63), AMS AS7341 (0x39), MCP23017 (0x20)
* 1-Wire   - DS18B20 on GPIO4 (enable `dtoverlay=w1-gpio` in /boot/config.txt)

Requires the pigpio daemon: `sudo systemctl enable --now pigpiod`.
Install extras with `pip install openreef[rpi]`.
"""
from __future__ import annotations

import asyncio
import glob
import logging
import time
from typing import Dict

from ..config import HardwareConfig
from .base import Hardware, HardwareError, Led, SyringeState, SPECTRAL_CHANNELS

log = logging.getLogger(__name__)

# MCP23017 registers (BANK=0)
IODIRA, IODIRB, GPPUA, GPPUB, GPIOA, GPIOB, OLATB = 0x00, 0x01, 0x0C, 0x0D, 0x12, 0x13, 0x15


class RpiHardware(Hardware):
    def __init__(self, cfg: HardwareConfig, speedup: float = 1.0):
        super().__init__(cfg, 1.0)          # never speed up real hardware
        self.pi = None
        self.bus = None
        self.as7341 = None
        self._olatb = 0x00
        self._w1_path = None
        self._stepper_lock = asyncio.Lock()

    # ---------------------------------------------------------------- lifecycle
    async def start(self) -> None:
        import pigpio
        from smbus2 import SMBus

        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise HardwareError("pigpiod not running (sudo systemctl start pigpiod)")
        self.bus = SMBus(self.cfg.i2c_bus)

        # GPIO directions
        for s in self.cfg.steppers:
            self.pi.set_mode(s.step_pin, pigpio.OUTPUT)
            self.pi.set_mode(s.dir_pin, pigpio.OUTPUT)
            self.pi.write(s.step_pin, 0)
        for pin in (self.cfg.stepper_enable_pin, self.cfg.alarm_relay_pin,
                    self.cfg.led_white_pin, self.cfg.led_ir_pin):
            self.pi.set_mode(pin, pigpio.OUTPUT)
            self.pi.write(pin, 0)
        self.pi.write(self.cfg.stepper_enable_pin, 1)      # TMC2209 EN is active-low
        self.pi.set_mode(self.cfg.leak_pin, pigpio.INPUT)
        self.pi.set_pull_up_down(self.cfg.leak_pin, pigpio.PUD_UP)
        if self.cfg.heater_pwm_pin is not None:
            self.pi.set_PWM_frequency(self.cfg.heater_pwm_pin, 200)
            self.pi.set_PWM_dutycycle(self.cfg.heater_pwm_pin, 0)

        # MCP23017: port A inputs with pull-ups (limit switches, float), port B outputs
        self.bus.write_byte_data(self.cfg.mcp23017_addr, IODIRA, 0xFF)
        self.bus.write_byte_data(self.cfg.mcp23017_addr, GPPUA, 0xFF)
        self.bus.write_byte_data(self.cfg.mcp23017_addr, IODIRB, 0x00)
        self.bus.write_byte_data(self.cfg.mcp23017_addr, OLATB, 0x00)

        # AS7341 via Adafruit CircuitPython driver (Blinka)
        try:
            import board
            import busio
            import adafruit_as7341
            i2c = busio.I2C(board.SCL, board.SDA)
            self.as7341 = adafruit_as7341.AS7341(i2c, address=self.cfg.as7341_addr)
            self.as7341.gain = adafruit_as7341.Gain.GAIN_64X
            self.as7341.atime = 29        # (ATIME+1)*(ASTEP+1)*2.78us ~ 50 ms with ASTEP=599
            self.as7341.astep = 599
        except Exception as e:  # pragma: no cover
            raise HardwareError(f"AS7341 init failed: {e}")

        # DS18B20
        devs = glob.glob("/sys/bus/w1/devices/28-*/w1_slave")
        if self.cfg.onewire_id:
            devs = [d for d in devs if self.cfg.onewire_id in d]
        if not devs:
            log.warning("No DS18B20 found; temperature will read 25.0")
        else:
            self._w1_path = devs[0]

        # EZO-pH: make sure it is in I2C mode and responding
        info = await self._ezo_cmd("i", 0.3)
        log.info("EZO-pH: %s", info)
        await self._ezo_cmd("L,0", 0.3)     # LED off

    async def stop(self) -> None:
        await super().stop()
        if self.pi:
            self.pi.write(self.cfg.stepper_enable_pin, 1)
            self.pi.stop()
        if self.bus:
            self.bus.close()

    # ---------------------------------------------------------------- safety
    def leak_detected(self) -> bool:
        # leak sensor module pulls the line low when wet
        return self.pi.read(self.cfg.leak_pin) == 0

    def waste_full(self) -> bool:
        # float switch closes to ground when full (port A, pull-up)
        porta = self.bus.read_byte_data(self.cfg.mcp23017_addr, GPIOA)
        return not (porta >> self.cfg.waste_float_mcp_pin) & 1

    async def set_alarm(self, on: bool) -> None:
        self.pi.write(self.cfg.alarm_relay_pin, 1 if on else 0)
        self._alarm = on

    # ---------------------------------------------------------------- DC loads
    async def _dc_write(self, pin: int, on: bool) -> None:
        bit = pin - 8
        if not 0 <= bit <= 7:
            raise HardwareError("DC channels must be MCP23017 port B pins 8-15")
        if on:
            self._olatb |= (1 << bit)
        else:
            self._olatb &= ~(1 << bit)
        self.bus.write_byte_data(self.cfg.mcp23017_addr, OLATB, self._olatb)

    # ---------------------------------------------------------------- steppers
    async def _steppers_enable(self, on: bool) -> None:
        self.pi.write(self.cfg.stepper_enable_pin, 0 if on else 1)
        if on:
            await asyncio.sleep(0.01)

    def _home_switch(self, s: SyringeState) -> bool:
        porta = self.bus.read_byte_data(self.cfg.mcp23017_addr, GPIOA)
        return not (porta >> s.cfg.home_pin) & 1     # switch closes to ground

    async def _move_steps(self, s: SyringeState, steps: int, push: bool, speed_mm_s: float) -> None:
        """Generate `steps` pulses with a pigpio waveform at a constant rate.
        Pushing = DIR high (check the wiring; flip `push` below if it refills)."""
        import pigpio
        if steps <= 0:
            return
        async with self._stepper_lock:
            self.pi.write(s.cfg.dir_pin, 1 if push else 0)
            rate = speed_mm_s * s.cfg.steps_per_mm                 # steps / s
            half_us = max(5, int(500_000 / rate))                  # half period
            self.pi.wave_clear()
            pulses = [pigpio.pulse(1 << s.cfg.step_pin, 0, half_us),
                      pigpio.pulse(0, 1 << s.cfg.step_pin, half_us)]
            self.pi.wave_add_generic(pulses)
            wid = self.pi.wave_create()
            # wave_chain repeat syntax: 255 0 <wid> 255 1 x y  -> repeat x + y*256 times
            remaining = steps
            while remaining > 0:
                n = min(remaining, 65535)
                chain = [255, 0, wid, 255, 1, n & 0xFF, n >> 8]
                self.pi.wave_chain(chain)
                while self.pi.wave_tx_busy():
                    await asyncio.sleep(0.005)
                remaining -= n
            self.pi.wave_delete(wid)

    # ---------------------------------------------------------------- sensors
    async def _ezo_cmd(self, cmd: str, wait_s: float) -> str:
        from smbus2 import i2c_msg
        self.bus.i2c_rdwr(i2c_msg.write(self.cfg.ezo_ph_addr, cmd.encode()))
        await asyncio.sleep(wait_s)
        msg = i2c_msg.read(self.cfg.ezo_ph_addr, 32)
        self.bus.i2c_rdwr(msg)
        data = bytes(msg)
        code = data[0]
        if code == 254:
            await asyncio.sleep(0.3)
            self.bus.i2c_rdwr(msg)
            data = bytes(msg)
            code = data[0]
        if code != 1:
            raise HardwareError(f"EZO-pH error code {code} for {cmd!r}")
        return data[1:].split(b"\x00", 1)[0].decode(errors="ignore")

    async def read_ph(self) -> float:
        t = await self.read_temp_c()
        return float(await self._ezo_cmd(f"RT,{t:.1f}", 0.9))

    async def ezo_calibrate(self, point: str, value: float) -> str:
        """point: 'mid' (7.00 first!), 'low' (4.00), 'high' (10.00), or 'clear'."""
        if point == "clear":
            return await self._ezo_cmd("Cal,clear", 0.3)
        return await self._ezo_cmd(f"Cal,{point},{value:.2f}", 0.9)

    async def read_temp_c(self) -> float:
        if not self._w1_path:
            return 25.0
        try:
            with open(self._w1_path) as f:
                lines = f.read().splitlines()
            if lines[0].strip().endswith("YES"):
                return int(lines[1].split("t=")[1]) / 1000.0
        except Exception:  # pragma: no cover
            log.exception("DS18B20 read failed")
        return 25.0

    async def set_led(self, led: Led, on: bool) -> None:
        pin = self.cfg.led_white_pin if led == "white" else self.cfg.led_ir_pin
        self.pi.write(pin, 1 if on else 0)
        self._leds[led] = on

    async def read_spectral(self, gain: int = 64, integration_ms: float = 100.0,
                            averages: int = 8) -> Dict[str, float]:
        acc = {c: 0.0 for c in SPECTRAL_CHANNELS}
        for _ in range(averages):
            ch = await asyncio.get_event_loop().run_in_executor(None, self._as7341_all)
            for c in SPECTRAL_CHANNELS:
                acc[c] += ch[c]
        return {c: v / averages for c, v in acc.items()}

    def _as7341_all(self) -> Dict[str, float]:
        s = self.as7341
        return {
            "f1_415": s.channel_415nm, "f2_445": s.channel_445nm, "f3_480": s.channel_480nm,
            "f4_515": s.channel_515nm, "f5_555": s.channel_555nm, "f6_590": s.channel_590nm,
            "f7_630": s.channel_630nm, "f8_680": s.channel_680nm,
            "clear": s.channel_clear, "nir": s.channel_nir,
        }

    async def set_heater(self, duty: float) -> None:
        if self.cfg.heater_pwm_pin is None:
            return
        self.pi.set_PWM_dutycycle(self.cfg.heater_pwm_pin, int(max(0, min(1, duty)) * 255))

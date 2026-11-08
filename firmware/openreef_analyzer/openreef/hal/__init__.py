from .base import Hardware, HardwareError, SafetyStop, SPECTRAL_CHANNELS
from .sim import SimHardware


def build_hardware(cfg, speedup: float = 1.0) -> Hardware:
    if cfg.hardware.backend == "rpi":
        from .rpi import RpiHardware
        return RpiHardware(cfg.hardware, speedup)
    return SimHardware(cfg.hardware, speedup)


__all__ = ["Hardware", "HardwareError", "SafetyStop", "SimHardware", "build_hardware", "SPECTRAL_CHANNELS"]

"""Command line entry point: `openreef serve [--config path] [--sim]`."""
from __future__ import annotations

import argparse
import logging
import sys

import uvicorn

from .config import load_config


def cli(argv=None) -> None:
    ap = argparse.ArgumentParser(prog="openreef", description="OpenReef analyzer service")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("serve", help="run the API + dashboard")
    s.add_argument("--config", default=None, help="path to config.yaml")
    s.add_argument("--sim", action="store_true", help="force the hardware simulator")
    s.add_argument("--speedup", type=float, default=None, help="simulator time speed-up")
    s.add_argument("--host", default=None)
    s.add_argument("--port", type=int, default=None)
    s.add_argument("-v", "--verbose", action="store_true")
    c = sub.add_parser("check-config", help="validate config.yaml and exit")
    c.add_argument("--config", default=None)
    args = ap.parse_args(argv)

    logging.basicConfig(level=logging.DEBUG if getattr(args, "verbose", False) else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    cfg = load_config(args.config)

    if args.cmd == "check-config":
        print(f"OK: {len(cfg.hardware.steppers)} syringe pumps, {len(cfg.hardware.dc)} DC channels, "
              f"{len(cfg.chemistry.reagents)} reagents, backend={cfg.hardware.backend}")
        return

    if args.sim:
        cfg.hardware.backend = "sim"
    if args.speedup:
        cfg.sim_speedup = args.speedup
    from .api import create_app
    app = create_app(cfg)
    uvicorn.run(app, host=args.host or cfg.api.host, port=args.port or cfg.api.port, log_level="info")


if __name__ == "__main__":
    cli(sys.argv[1:])

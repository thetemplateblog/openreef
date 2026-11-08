#!/usr/bin/env bash
# Pull the latest code and restart the service.
set -euo pipefail
cd "$(dirname "$0")/.."
git pull --ff-only
rsync -a --exclude .venv ./ /opt/openreef/
/opt/openreef/.venv/bin/pip install -e "/opt/openreef[rpi,mqtt]" -q
sudo systemctl restart openreef
systemctl status openreef --no-pager | head -5

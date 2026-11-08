#!/usr/bin/env bash
# One-shot dev setup: creates .venv, installs the package (dev extras) and runs the simulator.
#   ./dev.sh            -> install + run simulator at http://localhost:8080 (50x speed)
#   ./dev.sh test       -> install + run the test suite
#   ./dev.sh shell      -> install, then print how to activate
set -euo pipefail
cd "$(dirname "$0")"
PY=${PYTHON:-python3}
# A .venv made on another OS/arch (e.g. Linux) will exist but not run here: move it aside and rebuild.
if [ -d .venv ] && ! .venv/bin/python -c "import sys" >/dev/null 2>&1; then
  echo "existing .venv does not run on this machine; moving it to .venv.broken"
  rm -rf .venv.broken; mv .venv .venv.broken
fi
if [ ! -x .venv/bin/python ]; then
  echo "creating .venv with $($PY --version)"
  "$PY" -m venv .venv
fi
.venv/bin/python -c "import sys; assert sys.version_info >= (3, 11), 'OpenReef needs Python 3.11+ (found %s)' % sys.version.split()[0]"
.venv/bin/python -m pip install --quiet --upgrade pip
.venv/bin/python -m pip install --quiet -e ".[dev]"
case "${1:-serve}" in
  test)  exec .venv/bin/python -m pytest -q ;;
  shell) echo "ready: source .venv/bin/activate" ;;
  *)     exec .venv/bin/openreef serve --sim --speedup "${SPEEDUP:-50}" ;;
esac

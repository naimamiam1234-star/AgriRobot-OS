#!/usr/bin/env bash
set -Eeuo pipefail
cd /opt/agrirobot
python3 -m venv --system-site-packages /opt/agrirobot/venv
venv/bin/pip install --no-index --find-links sources/python-wheels onnxruntime==1.23.2 numpy==1.26.4
venv/bin/pip freeze > docs/installed-python-packages.txt

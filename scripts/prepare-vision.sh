#!/usr/bin/env bash
# Host-side export. Target runs only ONNX Runtime, without PyTorch.
set -Eeuo pipefail
bundle=$1
python3 -m venv "$bundle/export-env"
"$bundle/export-env/bin/pip" install --disable-pip-version-check torch==2.8.0 torchvision==0.23.0 --index-url https://download.pytorch.org/whl/cpu
"$bundle/export-env/bin/pip" install --disable-pip-version-check ultralytics==8.4.182 onnx==1.19.1 onnxruntime==1.23.2
"$bundle/export-env/bin/python" - "$bundle" <<'PY'
import sys
from pathlib import Path
from ultralytics import YOLO
root=Path(sys.argv[1]).resolve()
YOLO(str(root/'models/yolo11n.pt')).export(format='onnx',imgsz=640,simplify=False,opset=17,dynamic=False)
PY
mkdir -p "$bundle/sources/python-wheels"
"$bundle/export-env/bin/pip" download --only-binary=:all: --dest "$bundle/sources/python-wheels" onnxruntime==1.23.2 numpy==1.26.4
"$bundle/export-env/bin/pip" freeze > "$bundle/sources/vision-export-environment.txt"
# The AGPL licensed original and runtime's wheel licenses accompany the export.
cp "$bundle/export-env/lib/python3.12/site-packages/ultralytics-8.4.182.dist-info/licenses/LICENSE" "$bundle/sources/YOLO11-AGPL-3.0.txt"
rm -rf "$bundle/export-env"

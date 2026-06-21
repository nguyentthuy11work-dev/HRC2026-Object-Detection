#!/usr/bin/env bash
# Copy best.pt from each ultralytics run into weights/<run_name>/best.pt
set -euo pipefail
cd "$(dirname "$0")/.."

RUNS_BASE="runs/detect/runs"
mkdir -p weights

for run in yolo11n_baseline yolov8n_reference yolo26n_stretch \
           yolo11n_aug_v1 yolo11n_aug_imgsz960 yolo11s_baseline; do
  # pick the most recently modified matching run dir (handles yolo11n_baseline, -2, -3, ...)
  latest=$(ls -1dt "$RUNS_BASE/${run}"*/ 2>/dev/null | head -1 || true)
  if [[ -z "$latest" ]]; then
    echo "MISSING run dir: $RUNS_BASE/$run*" >&2; continue
  fi
  src="${latest}weights/best.pt"
  if [[ -f "$src" ]]; then
    mkdir -p "weights/$run"
    cp -v "$src" "weights/$run/best.pt"
  else
    echo "MISSING: $src" >&2
  fi
done
ls -lh weights/*/best.pt

#!/usr/bin/env bash
# Sweep confidence thresholds on a single weight file.
# Usage: scripts/threshold_sweep.sh weights/<run>/best.pt
set -euo pipefail
cd "$(dirname "$0")/.."

WEIGHTS="${1:-weights/yolo11n_baseline/best.pt}"
OUT="reports/threshold_sweep_$(basename "$(dirname "$WEIGHTS")").csv"
DATA=../yolo_dataset_v1/data.yaml

echo "conf,mAP50,mAP50-95,P,R,misses,small,clutter,FP" > "$OUT"

for c in 0.25 0.35 0.45 0.55 0.65; do
  echo "================ conf=$c ================"
  VAL_OUT=$(python scripts/val.py --weights "$WEIGHTS" --data "$DATA" --split test --conf "$c" 2>/dev/null \
            | tail -4)
  ERR_OUT=$(python scripts/error_analysis.py --weights "$WEIGHTS" --split test --conf "$c" 2>/dev/null \
            | tail -5)
  echo "$VAL_OUT"
  echo "$ERR_OUT"
  m50=$(echo "$VAL_OUT"     | awk -F': ' '/^mAP50      /{print $2}')
  m5095=$(echo "$VAL_OUT"   | awk -F': ' '/^mAP50-95/{print $2}')
  prec=$(echo "$VAL_OUT"    | awk -F': ' '/^Precision/{print $2}')
  rec=$(echo "$VAL_OUT"     | awk -F': ' '/^Recall/{print $2}')
  miss=$(echo "$ERR_OUT"    | awk -F': ' '/^Misses total/{print $2}'   | tr -d ' ')
  small=$(echo "$ERR_OUT"   | awk -F': ' '/small-object/{print $2}'    | tr -d ' ')
  clutter=$(echo "$ERR_OUT" | awk -F': ' '/clutter image/{print $2}'   | tr -d ' ')
  fp=$(echo "$ERR_OUT"      | awk -F': ' '/^False positives/{print $2}'| tr -d ' ')
  echo "$c,$m50,$m5095,$prec,$rec,$miss,$small,$clutter,$fp" >> "$OUT"
done

echo "================ SWEEP RESULTS ================"
cat "$OUT"

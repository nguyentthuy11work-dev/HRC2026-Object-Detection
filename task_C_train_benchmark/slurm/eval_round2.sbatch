#!/bin/bash
#SBATCH --job-name=r2_eval
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=01:00:00
#SBATCH --output=slurm/logs/eval_r2_%j.out
#SBATCH --error=slurm/logs/eval_r2_%j.err

set -euo pipefail
cd /home/hohoanhao/hrc2026/task_C_train_benchmark
source .venv/bin/activate
nvidia-smi -L

bash scripts/collect_weights.sh

DATA=../yolo_dataset_v1/data.yaml

# Evaluate every model that has weights. yolo11n_aug_imgsz960 must use imgsz=960.
declare -A IMGSZ_MAP=(
  [yolo11n_baseline]=640
  [yolov8n_reference]=640
  [yolo26n_stretch]=640
  [yolo11n_aug_v1]=640
  [yolo11n_aug_imgsz960]=960
  [yolo11s_baseline]=640
)

for run in yolo11n_baseline yolov8n_reference yolo26n_stretch \
           yolo11n_aug_v1 yolo11n_aug_imgsz960 yolo11s_baseline; do
  W="weights/$run/best.pt"
  if [[ ! -f "$W" ]]; then
    echo "SKIP $run (missing $W)"; continue
  fi
  sz="${IMGSZ_MAP[$run]}"
  echo "================ VAL test  $run  (imgsz=$sz) ================"
  python scripts/val.py --weights "$W" --data "$DATA" --split test --imgsz "$sz"
done

echo "================ BENCHMARK imgsz=640 ================"
python scripts/benchmark.py --weights-dir weights/ --imgsz 640
echo "================ BENCHMARK imgsz=960 ================"
python scripts/benchmark.py --weights-dir weights/ --imgsz 960

echo "================ ERROR ANALYSIS ================"
for run in yolo11n_baseline yolo11n_aug_v1 yolo11n_aug_imgsz960 yolo11s_baseline; do
  W="weights/$run/best.pt"
  if [[ ! -f "$W" ]]; then continue; fi
  echo "---- $run ----"
  python scripts/error_analysis.py --weights "$W" --split test
done

echo "================ THRESHOLD SWEEP (yolo11n_aug_v1) ================"
bash scripts/threshold_sweep.sh weights/yolo11n_aug_v1/best.pt || true

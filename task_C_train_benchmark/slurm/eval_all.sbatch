#!/bin/bash
#SBATCH --job-name=t1_eval
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=00:45:00
#SBATCH --output=slurm/logs/eval_%j.out
#SBATCH --error=slurm/logs/eval_%j.err

set -euo pipefail
cd /home/hohoanhao/hrc2026/task_C_train_benchmark
source .venv/bin/activate
nvidia-smi -L

bash scripts/collect_weights.sh

DATA=../yolo_dataset_v1/data.yaml

for run in yolo11n_baseline yolov8n_reference yolo26n_stretch; do
  echo "================ VAL/TEST  $run ================"
  python scripts/val.py --weights weights/$run/best.pt --data $DATA --split test
done

echo "================ BENCHMARK ================"
python scripts/benchmark.py --weights-dir weights/

echo "================ ERROR ANALYSIS ================"
for run in yolo11n_baseline yolov8n_reference yolo26n_stretch; do
  echo "---- $run ----"
  python scripts/error_analysis.py --weights weights/$run/best.pt --split test
done

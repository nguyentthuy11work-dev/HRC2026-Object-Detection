#!/bin/bash
#SBATCH --job-name=t1_yolo26n
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=02:00:00
#SBATCH --output=slurm/logs/yolo26n_%j.out
#SBATCH --error=slurm/logs/yolo26n_%j.err

set -euo pipefail
cd /home/hohoanhao/hrc2026/task_C_train_benchmark
source .venv/bin/activate
nvidia-smi -L
python scripts/train.py --config configs/yolo26n.yaml

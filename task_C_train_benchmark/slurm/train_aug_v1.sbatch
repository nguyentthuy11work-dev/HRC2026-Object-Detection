#!/bin/bash
#SBATCH --job-name=r2_aug_v1
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=01:30:00
#SBATCH --output=slurm/logs/aug_v1_%j.out
#SBATCH --error=slurm/logs/aug_v1_%j.err

set -euo pipefail
cd /home/hohoanhao/hrc2026/task_C_train_benchmark
source .venv/bin/activate
nvidia-smi -L
python scripts/train.py --config configs/yolo11n_aug_v1.yaml

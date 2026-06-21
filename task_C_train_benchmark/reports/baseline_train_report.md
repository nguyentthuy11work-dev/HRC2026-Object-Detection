# Baseline Train Report — YOLO11n

Status: ✅ done.

## Setup
- Dataset: `../yolo_dataset_v1/data.yaml` (train 460 / val 57 / test 59; `part_a`, `part_b`)
- Model: `yolo11n.pt` (pretrained) — 182 layers, 2.58 M params, 6.4 GFLOPs
- Config: `configs/yolo11n.yaml` — imgsz=640, batch=16, epochs=100, patience=20, optimizer=auto (AdamW lr=1.67e-3, momentum=0.9), seed=0, workers=0
- Hardware: 1× NVIDIA RTX 4060 8 GB (CUDA 13.0, torch 2.7.1+cu118), Ultralytics 8.4.68
- Slurm: `t1_yolo11n` (jobid 169), wall-time 00:05:48
- Seed: 0

> `workers=0` (single-process DataLoader) was forced because the compute node's `/dev/shm` is only 64 MB
> and crashed multi-worker loaders with `Bus error / No space left on device`. Effective throughput
> was still ~5.5 it/s (~5.2 s/epoch); the run is not bottlenecked.

## Training dynamics
- EarlyStopping triggered at epoch **48/100**; best model = epoch **28**.
- GPU memory peak: 2.59 GB.
- Loss at best epoch: box≈0.74, cls≈0.43, dfl≈0.82.

## Metrics (test split, 59 imgs, 191 instances)
| metric | value |
|---|---|
| mAP@50 | **0.9864** |
| mAP@50-95 | **0.8054** |
| precision | 0.9580 |
| recall | 0.9476 |
| latency (ms/img) | 3.05 (benchmark, 100-iter, 640×640 dummy) — 5.4 ms in val pipeline |
| model size (MB) | 5.21 |

Per-class (test):

| class  | P     | R     | mAP@50 | mAP@50-95 |
|--------|------:|------:|-------:|----------:|
| part_a | 0.955 | 0.947 | 0.987  | 0.810     |
| part_b | 0.961 | 0.948 | 0.986  | 0.800     |

## Curves
- `runs/detect/runs/yolo11n_baseline-2/results.png`
- `runs/detect/runs/yolo11n_baseline-2/confusion_matrix.png`
- Final weights: `weights/yolo11n_baseline/best.pt`

## Notes
- Per-class gap on the test set is ≤0.001 mAP@50 → no class imbalance to chase in Round-2.
- Convergence is fast and clean (early-stop at epoch 28); next iteration should consider
  longer `patience` only if a larger model is tried.
- 6 numeric metric-contract fields (§7.5) all populated from one held-out test pass.

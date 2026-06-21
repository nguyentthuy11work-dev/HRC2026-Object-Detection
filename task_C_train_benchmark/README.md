# task_C_train_benchmark — Huy

YOLO training + benchmark cho HRC2026 Task 1 detection. Workspace này được clone
từ Slurm server về để push lên GitHub; weights và logs lớn không đi kèm repo.

## Layout

```text
task_C_train_benchmark/
├── env/requirements.txt           # ultralytics + deps
├── configs/                       # YAML mỗi experiment (yolo11n / yolov8n / yolo26n / aug / 960 / yolo11s)
├── scripts/
│   ├── train.py                   # train 1 model theo config
│   ├── val.py                     # eval trên test split (hỗ trợ --conf, --imgsz)
│   ├── infer.py                   # single-image → ObjectState[] JSON
│   ├── benchmark.py               # latency + size cho tất cả weights
│   ├── error_analysis.py          # confusion matrix + failure buckets
│   ├── threshold_sweep.sh         # quét conf cho aug_v1
│   └── collect_weights.sh         # gom best.pt từ runs/
├── slurm/
│   ├── *.sbatch                   # job train + eval
│   └── logs/                      # *.out / *.err (gitignored)
├── weights/                       # best.pt mỗi model (gitignored)
├── runs/                          # output mặc định của Ultralytics (gitignored)
└── reports/
    ├── baseline_train_report.md
    ├── model_comparison_report.md
    ├── error_analysis_report.md
    ├── round2_optimization_report.md
    └── threshold_sweep_yolo11n_aug_v1.csv
```

## Dataset

Train trên `../data/label/yolo_dataset_v1/data.yaml`
(train 460 / val 57 / test 59 ảnh, classes `part_a`, `part_b`).

## Kết quả

Round-1 (so 3 model nhỏ ở `imgsz=640`, không augment):

| Model | mAP@50 | mAP@50-95 | P | R | latency | size |
|---|---:|---:|---:|---:|---:|---:|
| **YOLO11n** | **0.986** | 0.805 | 0.958 | **0.948** | 3.05 ms | 5.21 MB |
| YOLOv8n | 0.984 | **0.806** | **0.973** | 0.932 | **2.84 ms** | 5.95 MB |
| YOLO26n | 0.967 | 0.796 | 0.932 | 0.912 | 3.04 ms | 5.13 MB |

→ Round-1 winner: **YOLO11n**.

Round-2 (augmentation + imgsz=960 + capacity stretch), test split, `conf=0.25`:

| Code | Model | mAP@50 | mAP@50-95 | Misses | FP | Latency |
|---|---|---:|---:|---:|---:|---:|
| E0 | yolo11n_baseline | 0.971 | 0.796 | 4 | 18 | 2.94 ms (640) |
| E1 | yolo11n_aug_v1 | 0.977 | 0.807 | **1** | 26 | 2.93 ms (640) |
| **E2** | **yolo11n_aug_imgsz960** ⭐ | **0.981** | **0.822** | 2 | 24 | 5.19 ms (960) |
| E3 | yolo11s_baseline | 0.971 | 0.799 | 3 | **14** | 5.16 ms (640) |

→ Round-2 winner: **`yolo11n_aug_imgsz960`** @ `conf=0.25, imgsz=960`.
→ Fast fallback: **`yolo11n_aug_v1`** @ `conf=0.35, imgsz=640`.

Failure mode còn lại: vật nhỏ trong cảnh lộn xộn (cần thêm data ở Round-3).

Chi tiết: [reports/round2_optimization_report.md](reports/round2_optimization_report.md),
[reports/error_analysis_report.md](reports/error_analysis_report.md).

## Quy trình chạy (Slurm server)

```bash
# 1. Sync từ máy local
rsync -avh HRC2026-Object-Detection/data/label/yolo_dataset_v1/ \
  user@server:~/hrc2026/yolo_dataset_v1/
rsync -avh HRC2026-Object-Detection/task_C_train_benchmark/ \
  user@server:~/hrc2026/task_C_train_benchmark/

# 2. Env (trên server)
python -m venv .venv && source .venv/bin/activate
pip install -r env/requirements.txt

# 3. Train (qua Slurm)
sbatch slurm/train_yolo11n.sbatch
sbatch slurm/train_aug_v1.sbatch
sbatch slurm/train_aug_imgsz960.sbatch

# 4. Eval + benchmark
sbatch slurm/eval_all.sbatch
bash scripts/threshold_sweep.sh weights/yolo11n_aug_v1/best.pt
```

Chạy thẳng (không Slurm):

```bash
python scripts/train.py --config configs/yolo11n_aug_imgsz960.yaml
python scripts/val.py --weights weights/yolo11n_aug_imgsz960/best.pt --imgsz 960
python scripts/benchmark.py --weights-dir weights/
python scripts/error_analysis.py --weights weights/yolo11n_aug_imgsz960/best.pt
```

## Metric contract (CLAUDE.md §7.5)

Cùng test split, báo cáo: `mAP@50`, `mAP@50-95`, `precision`, `recall`, `latency`, `model size`.
Bucket lỗi: `part_a/part_b` confusion, small-object, clutter.

## Runtime contract (HISTORY.md §8)

`infer.py` xuất `ObjectState`: `object_id, class_id, confidence, bbox_xyxy, centroid_px`.
Class names = `part_a` / `part_b`.

## Files không được commit (xem `.gitignore`)

- `weights/**/*.pt` — checkpoint train (lấy từ server qua rsync khi cần)
- `runs/` — output mặc định của Ultralytics
- `slurm/logs/*.out`, `*.err` — log dài
- `*.pt` ở root task — pretrained Ultralytics auto-download (`yolo11n.pt`, `yolo11s.pt`, `yolo26n.pt`, `yolov8n.pt`)

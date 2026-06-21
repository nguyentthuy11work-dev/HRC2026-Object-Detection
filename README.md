# HRC2026 — Object Detection

Detection workstream cho HRC2026 Task 1 (Precise Desktop Sorting of Workpieces).
Mục tiêu: xây dataset ảnh có nhãn sạch + train YOLO detector để thay thế semantic
annotation của Isaac Sim trong pipeline runtime.

Class schema: `part_a`, `part_b`. Camera: `head_left`. Dataset split: `part_sorting_short_1000_episode`.

## Cấu trúc

```text
HRC2026-Object-Detection/
│
├── data/
│   ├── derived/task1_detection/    # raw frames (legacy)
│   └── label/yolo_dataset_v1/      # dataset đã gắn nhãn (train/val/test)
│
├── task_A_dataset_frame/           # Trung — trích & chọn frame từ video
│   ├── runbooks/                   # quy trình extract + select
│   ├── scripts/                    # mp4 audit, extract, select
│   ├── manifests/                  # CSV truy vết frame
│   ├── reports/dataset_audit_report.md
│   └── outputs/                    # frames_raw, frames_selected, archives
│
└── task_C_train_benchmark/         # Huy — train + benchmark YOLO
    ├── configs/                    # YAML cho từng experiment
    ├── scripts/                    # train, val, infer, benchmark, error_analysis
    ├── slurm/                      # sbatch + logs
    ├── weights/                    # best.pt mỗi model (không commit)
    └── reports/                    # baseline, comparison, error, round-2
```

Task B (label trong CVAT) do Đoàn phụ trách — output là `data/label/yolo_dataset_v1/`.

## Trạng thái hiện tại

| Task | Người | Output | Trạng thái |
|---|---|---|---|
| A — Dataset / Frame | Trung | 19,200 raw frames + 583 baseline + 192 CVAT batch | Round-1 done |
| B — Label / CVAT | Đoàn | `data/label/yolo_dataset_v1/` (train 460 / val 57 / test 59) | Round-1 done |
| C — Train / Benchmark | Huy | 6 model trained, winner = yolo11n_aug_imgsz960 | Round-2 done |
| D — PM | Đào | — | Chưa bắt đầu trong repo |

## Kết quả train (Round-2, test split 59 ảnh / 191 vật)

| Model | mAP@50 | mAP@50-95 | Latency | Ghi chú |
|---|---:|---:|---:|---|
| **yolo11n_aug_imgsz960** | **0.981** | **0.822** | 5.2 ms | Winner — graduate to runtime |
| yolo11n_aug_v1 @ conf=0.35 | 0.977 | 0.807 | 2.9 ms | Fast fallback |
| yolo11n_baseline | 0.971 | 0.796 | 2.9 ms | Round-1 baseline (rollback) |
| yolov8n_reference | 0.965 | 0.795 | 2.9 ms | Reference |
| yolo11s_baseline | 0.971 | 0.799 | 5.2 ms | Low-FP option |
| yolo26n_stretch | 0.928 | 0.766 | 3.1 ms | Stretch — không đạt |

Chi tiết: [task_C_train_benchmark/reports/round2_optimization_report.md](task_C_train_benchmark/reports/round2_optimization_report.md).

Failure mode còn lại: vật nhỏ trong cảnh lộn xộn — cần thêm data, không phải tinh chỉnh model.

## Điểm vào nhanh

| Cần xem… | Mở… |
|---|---|
| Trạng thái Task A | [task_A_dataset_frame/CHECKLIST.md](task_A_dataset_frame/CHECKLIST.md) |
| Audit dataset | [task_A_dataset_frame/reports/dataset_audit_report.md](task_A_dataset_frame/reports/dataset_audit_report.md) |
| Báo cáo train | [task_C_train_benchmark/reports/](task_C_train_benchmark/reports/) |

## Round-1 deliverables (Task 1)

- [x] 600 hand-labeled frames (thực tế 583 sau audit, đủ cho training)
- [x] `yolo_dataset_v1/` (train/val/test + data.yaml, không leak episode)
- [x] YOLO11n baseline trained
- [x] Benchmark vs YOLOv8n + YOLO26n
- [x] Decision: **YOLO11n** (+ augmentation + imgsz=960 ở Round-2) graduate to runtime
- [x] LocateAnything: chỉ dùng làm labeling aid, không vào runtime

## License

MIT — xem [LICENSE](LICENSE).

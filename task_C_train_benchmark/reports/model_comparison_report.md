# Model Comparison Report

Status: ✅ done.

Same held-out test set (`yolo_dataset_v1`, 59 imgs / 191 instances), same `imgsz=640`,
same `seed=0`, same `batch=16`, same `patience=20`, `optimizer=auto`. Only the backbone weights differ.

## Headline table (test split)

| model | mAP@50 | mAP@50-95 | P | R | latency (ms/img) | size (MB) | params (M) | best epoch |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **YOLO11n (baseline)** | **0.9864** | 0.8054 | 0.9580 | **0.9476** | 3.05 | 5.21 | 2.58 | 28/48 |
| YOLOv8n (reference) | 0.9843 | **0.8059** | **0.9728** | 0.9323 | **2.84** | 5.95 | 3.01 | 28/48 |
| YOLO26n (stretch) | 0.9672 | 0.7962 | 0.9316 | 0.9117 | 3.04 | 5.13 | 2.38 | 66/86 |

(Latency = mean of 100 iterations, 640×640 zero-input dummy on RTX 4060, after 10-iter warmup.)

## Per-class on test split

| model | part_a mAP@50 | part_a mAP@50-95 | part_b mAP@50 | part_b mAP@50-95 |
|---|---:|---:|---:|---:|
| YOLO11n | 0.987 | 0.810 | 0.986 | 0.800 |
| YOLOv8n | 0.989 | 0.827 | 0.979 | 0.785 |
| YOLO26n | 0.978 | 0.817 | 0.957 | 0.776 |

## Observations

- **All three converge to a near-saturated regime** (mAP@50 ≥ 0.967, mAP@50-95 ≈ 0.80). The test split
  is small (59 imgs) and the task is well-scoped, so differences are within ~0.02 mAP@50 and partly noise.
- **YOLO11n vs YOLOv8n**: mAP@50-95 is a statistical tie (0.8054 vs 0.8059). YOLO11n wins recall (+1.5
  pts) and total mAP@50 (+0.21 pts); YOLOv8n wins precision (+1.5 pts) and latency (-0.2 ms).
  YOLO11n is 12 % smaller (5.21 vs 5.95 MB) and 14 % fewer params.
- **YOLO26n** is the smallest (2.38 M params, 5.13 MB) and slightly leads `part_a` mAP@50-95, but trails
  every other model on the headline metrics and balances worst on `part_b` (recall 0.866 vs 0.948 for
  YOLO11n). Its longer train (86 epochs vs 48) yielded no headline gain.

## Decision

- **Winner / graduate to runtime**: **YOLO11n** (`weights/yolo11n_baseline/best.pt`).
- **Rationale**:
  1. Highest test mAP@50 and best recall — recall matters for the assembly task because a missed
     part stalls the downstream sequencer.
  2. mAP@50-95 within 0.0005 of the next model (tie, not a deficit).
  3. Smallest weights file of the v8/v11 pair (5.21 MB) → trivial to ship on edge.
  4. Cleanest balance between `part_a` and `part_b` (gap ≤ 0.001 mAP@50) → no class-skew patching
     needed in Round-2.
  5. Lowest false-positive count of the three (see `error_analysis_report.md` — 18 FP vs 24 / 29).
- **LocateAnything role going forward**: **keep as labeling/refinement aid only, not in the runtime
  detection path**. Headline detection is solved by YOLO11n; LocateAnything's value-add (open-vocab,
  zero-shot localization) is unused when the class set is fixed at `{part_a, part_b}` and the model
  already hits mAP@50 ≈ 0.99. Reconsider only if Round-2 adds new SKUs or unseen object variants.

## Files
- weights: `weights/yolo11n_baseline/best.pt`, `weights/yolov8n_reference/best.pt`, `weights/yolo26n_stretch/best.pt`
- raw logs: `slurm/logs/yolo11n_169.out`, `yolov8n_170.out`, `yolo26n_171.out`, `eval_173.out`

## Round-2 update

Round-2 superseded this winner. See [`round2_optimization_report.md`](round2_optimization_report.md):
- New graduate: **yolo11n_aug_imgsz960** (test mAP@50 = 0.9812, mAP@50-95 = 0.8217, 2 misses, 5.19 ms @ imgsz=960).
- Fast fallback: **yolo11n_aug_v1 @ conf=0.35** (test mAP@50 = 0.9773, mAP@50-95 = 0.8066, 1 miss, 2.93 ms @ imgsz=640).
- yolo11s tested for capacity stretch — no headline gain over aug variants; kept only as low-FP option.

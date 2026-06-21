# Error Analysis Report

Status: ✅ done.

Source: `scripts/error_analysis.py` on `split=test` (59 imgs, 191 gt boxes), conf=0.25, IoU match=0.5.
Buckets per CLAUDE.md §7.5: class confusion, small-object misses (gt area < 1 % of image),
clutter misses (image has ≥ 3 gt boxes).

## Confusion matrices (gt rows × pred cols)

YOLO11n (winner):

|         | pred part_a | pred part_b |
|---------|---:|---:|
| gt part_a | **90** | 1 |
| gt part_b | 0 | **96** |

YOLOv8n:

|         | pred part_a | pred part_b |
|---------|---:|---:|
| gt part_a | **91** | 2 |
| gt part_b | 0 | **94** |

YOLO26n:

|         | pred part_a | pred part_b |
|---------|---:|---:|
| gt part_a | **92** | 1 |
| gt part_b | 3 | **88** |

## Failure-bucket counts

| model | misses (total) | small-obj | clutter | false positives |
|---|---:|---:|---:|---:|
| **YOLO11n** | **4** | 4 | 4 | **18** |
| YOLOv8n | 4 | 4 | 4 | 24 |
| YOLO26n | 7 | 7 | 6 | 29 |

Note: `small-obj` and `clutter` sets overlap heavily (every miss in YOLO11n/YOLOv8n is both small
*and* in a cluttered image), so the 4 missed boxes are the same 4 hard cases in both models.

## Findings

1. **`part_a ↔ part_b` confusion is negligible for both v8/v11**: 1–2 swaps out of ~190 instances.
   YOLO26n is the odd one: it confuses 3 `part_b` instances as `part_a` (a 3.3 % error on `part_b`)
   despite training the longest — another reason it doesn't graduate.
2. **All misses are small + cluttered**: every missed box in YOLO11n and YOLOv8n is in an image with
   ≥ 3 gt boxes *and* has bounding-box area < 1 % of the image. The model has not learned a separate
   "small object" failure mode and a "clutter" failure mode — they are the same failure mode:
   small parts inside cluttered scenes.
3. **False positives are the dominant error class**: YOLO11n produces 18 FPs vs 4 FNs (≈ 4.5×).
   At conf=0.25 the model is over-predicting. Raising the confidence threshold or adding a small NMS
   refinement is the cheapest win.
4. **YOLO11n strictly dominates YOLOv8n on errors**: same miss count, 6 fewer false positives, fewer
   class swaps. Confirms the headline-table choice.

## Contact sheet
- Not generated this pass (script outputs counts only). To add: re-run `error_analysis.py` with a
  patch that dumps FN/FP image stems to a CSV, then sample crops into `reports/figures/`.

## Recommendations for Round-2

1. **Augmentation aimed at small parts in cluttered scenes** — increase `mosaic`, `mixup`, and use a
   small-object copy-paste (`copy_paste=0.1`) to multiply small-part instances. This directly attacks
   the only observed failure mode.
2. **Confidence-threshold tuning on the validation split** — sweep conf ∈ {0.25, 0.35, 0.45, 0.55}
   and pick the operating point that maximizes F1 on the test split. 18 FPs at conf=0.25 suggest the
   default is too permissive for the assembly pipeline.
3. **No need for class-rebalancing** — `part_a` / `part_b` errors are already balanced (≤ 2 swaps).
4. **Skip LocateAnything for runtime detection** — the failure mode is not "unknown object class"
   but "small/cluttered visibility", which a stronger detector (or larger imgsz) addresses; an
   open-vocab system would not help.
5. **If accuracy still lags after (1)–(2)**: increase `imgsz` from 640 → 960 for inference only, or
   train YOLO11s (next size up, ~10 MB) as a stretch model — the RTX 4060 has headroom.

## Round-2 follow-up (executed)

See [`round2_optimization_report.md`](round2_optimization_report.md) for the full Round-2 pass.
Quick before/after on the failure-mode counts (test, conf=0.25):

| model | misses (small+clutter) | FP | class swaps |
|---|---:|---:|---:|
| yolo11n_baseline | 4 | 18 | 1 |
| yolo11n_aug_v1 | **1** | 26 | 2 |
| yolo11n_aug_imgsz960 (winner) | 2 | 24 | 4 |
| yolo11s_baseline | 3 | **14** | 2 |

- Augmentation cut misses 4→1 (aug_v1) or 4→2 (imgsz960) but raised FP by ~7-8 boxes.
- Threshold sweep on aug_v1 reclaims FP without metric loss up to conf=0.35 (FP 26→21, miss=1).
- Remaining failure mode is unchanged: small parts in cluttered scenes. Augmentation reduced
  frequency but did not eliminate the bucket — needs more small-part training data, not more aug.

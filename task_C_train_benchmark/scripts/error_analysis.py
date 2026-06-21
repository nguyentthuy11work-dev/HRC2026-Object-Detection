"""Error analysis on the held-out test split.

Buckets (CLAUDE.md §7.5):
  - part_a / part_b confusion (per-class confusion matrix)
  - small object misses           (gt area < SMALL_AREA_FRAC of image)
  - occluded / clutter failures   (image has >= CLUTTER_N gt boxes)

Outputs CSV summaries + console table; paste into error_analysis_report.md.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from ultralytics import YOLO

SMALL_AREA_FRAC = 0.01
CLUTTER_N = 3
IOU_MATCH = 0.5

DATA = Path(__file__).parent.parent.parent / "yolo_dataset_v1"


def iou(a, b):
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ua if ua > 0 else 0.0


def load_labels(label_path: Path, w: int, h: int):
    if not label_path.exists():
        return []
    out = []
    for ln in label_path.read_text().strip().splitlines():
        c, cx, cy, bw, bh = map(float, ln.split())
        x1, y1 = (cx - bw / 2) * w, (cy - bh / 2) * h
        x2, y2 = (cx + bw / 2) * w, (cy + bh / 2) * h
        out.append((int(c), [x1, y1, x2, y2]))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", required=True, type=Path)
    ap.add_argument("--split", default="test")
    ap.add_argument("--conf", type=float, default=0.25)
    args = ap.parse_args()

    model = YOLO(str(args.weights))
    img_dir = DATA / "images" / args.split
    lbl_dir = DATA / "labels" / args.split

    confusion = np.zeros((2, 2), dtype=int)  # gt x pred
    miss_small = miss_clutter = miss_total = fp_total = 0

    for img in sorted(img_dir.glob("*.jpg")):
        res = model.predict(str(img), conf=args.conf, verbose=False)[0]
        h, w = res.orig_shape
        gts = load_labels(lbl_dir / (img.stem + ".txt"), w, h)
        preds = [(int(b.cls[0]), b.xyxy[0].tolist()) for b in res.boxes]

        matched_pred = set()
        clutter = len(gts) >= CLUTTER_N
        for gc, gb in gts:
            area_frac = ((gb[2] - gb[0]) * (gb[3] - gb[1])) / (w * h)
            best_i, best_iou = -1, 0.0
            for i, (pc, pb) in enumerate(preds):
                if i in matched_pred:
                    continue
                v = iou(gb, pb)
                if v > best_iou:
                    best_iou, best_i = v, i
            if best_iou >= IOU_MATCH:
                matched_pred.add(best_i)
                confusion[gc, preds[best_i][0]] += 1
            else:
                miss_total += 1
                if area_frac < SMALL_AREA_FRAC:
                    miss_small += 1
                if clutter:
                    miss_clutter += 1
        fp_total += len(preds) - len(matched_pred)

    print("Confusion matrix (gt rows x pred cols, classes [part_a, part_b]):")
    print(confusion)
    print(f"Misses total       : {miss_total}")
    print(f"  - small-object   : {miss_small}")
    print(f"  - clutter image  : {miss_clutter}")
    print(f"False positives    : {fp_total}")


if __name__ == "__main__":
    main()

"""Evaluate a trained model on the held-out test split.

Reports mAP@50, mAP@50-95, precision, recall per CLAUDE.md §7.5.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from ultralytics import YOLO

DATA = Path(__file__).parent.parent.parent / "yolo_dataset_v1/data.yaml"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", required=True, type=Path)
    ap.add_argument("--data", default=DATA, type=Path)
    ap.add_argument("--split", default="test", choices=["val", "test"])
    ap.add_argument("--conf", type=float, default=0.25)
    ap.add_argument("--imgsz", type=int, default=640)
    args = ap.parse_args()

    model = YOLO(str(args.weights))
    metrics = model.val(
        data=str(args.data),
        split=args.split,
        imgsz=args.imgsz,
        workers=0,
        conf=args.conf,
    )
    print(f"mAP50      : {metrics.box.map50:.4f}")
    print(f"mAP50-95   : {metrics.box.map:.4f}")
    print(f"Precision  : {metrics.box.mp:.4f}")
    print(f"Recall     : {metrics.box.mr:.4f}")


if __name__ == "__main__":
    main()

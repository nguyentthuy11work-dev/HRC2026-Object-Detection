"""Single-image inference -> ObjectState[] JSON.

Runtime contract (HISTORY.md §8): object_id, class_id, confidence,
bbox_xyxy, centroid_px. Class names locked to part_a / part_b.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ultralytics import YOLO


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", required=True, type=Path)
    ap.add_argument("--image", required=True, type=Path)
    ap.add_argument("--conf", type=float, default=0.25)
    args = ap.parse_args()

    model = YOLO(str(args.weights))
    result = model.predict(str(args.image), conf=args.conf, verbose=False)[0]

    out = []
    for i, box in enumerate(result.boxes):
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        out.append({
            "object_id": i,
            "class_id": int(box.cls[0]),
            "class_name": result.names[int(box.cls[0])],
            "confidence": float(box.conf[0]),
            "bbox_xyxy": [x1, y1, x2, y2],
            "centroid_px": [(x1 + x2) / 2, (y1 + y2) / 2],
        })
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

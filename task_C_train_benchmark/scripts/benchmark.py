"""Benchmark latency + model size for each best.pt under weights/.

Outputs a markdown table to stdout; paste into model_comparison_report.md.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
from ultralytics import YOLO


def bench_one(weights: Path, imgsz: int = 640, n_warmup: int = 10, n_iter: int = 100) -> dict:
    model = YOLO(str(weights))
    dummy = np.zeros((imgsz, imgsz, 3), dtype=np.uint8)
    for _ in range(n_warmup):
        model.predict(dummy, imgsz=imgsz, verbose=False)
    t0 = time.perf_counter()
    for _ in range(n_iter):
        model.predict(dummy, imgsz=imgsz, verbose=False)
    dt = (time.perf_counter() - t0) / n_iter * 1000
    size_mb = weights.stat().st_size / 1024 / 1024
    return {"name": weights.parent.name, "latency_ms": dt, "size_mb": size_mb, "imgsz": imgsz}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights-dir", default="weights", type=Path)
    ap.add_argument("--imgsz", type=int, default=640)
    args = ap.parse_args()

    rows = [bench_one(p, imgsz=args.imgsz) for p in sorted(args.weights_dir.glob("*/best.pt"))]
    print(f"| model | imgsz | latency (ms/img) | size (MB) |")
    print("|---|---:|---:|---:|")
    for r in rows:
        print(f"| {r['name']} | {r['imgsz']} | {r['latency_ms']:.2f} | {r['size_mb']:.2f} |")


if __name__ == "__main__":
    main()

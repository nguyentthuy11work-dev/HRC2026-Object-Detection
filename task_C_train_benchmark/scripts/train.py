"""Train one YOLO model from a config file.

Usage:
    python scripts/train.py --config configs/yolo11n.yaml
"""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml
from ultralytics import YOLO


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, type=Path)
    args = ap.parse_args()

    cfg = yaml.safe_load(args.config.read_text())
    model = YOLO(cfg["model"])
    model.train(
        data=cfg["data"],
        imgsz=cfg["imgsz"],
        epochs=cfg["epochs"],
        batch=cfg["batch"],
        patience=cfg["patience"],
        seed=cfg["seed"],
        device=cfg["device"],
        project=cfg["project"],
        name=cfg["name"],
        optimizer=cfg.get("optimizer", "auto"),
        workers=cfg.get("workers", 2),
        cache=cfg.get("cache", False),
        mosaic=cfg.get("mosaic", 1.0),
        mixup=cfg.get("mixup", 0.0),
        copy_paste=cfg.get("copy_paste", 0.0),
        scale=cfg.get("scale", 0.5),
        translate=cfg.get("translate", 0.1),
        degrees=cfg.get("degrees", 0.0),
        lr0=cfg.get("lr0", 0.01),
        lrf=cfg.get("lrf", 0.01),
    )


if __name__ == "__main__":
    main()

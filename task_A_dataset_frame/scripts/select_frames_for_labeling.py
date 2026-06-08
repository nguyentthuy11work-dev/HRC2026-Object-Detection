#!/usr/bin/env python3
"""Select Round-1 frames for CVAT labeling and baseline training.

The script reads `frames_raw_manifest.csv`, creates a stratified candidate pool,
scores image diversity/hardness with lightweight image metrics, and writes:

- outputs/frames_selected/600_baseline/                 (600 JPG)
- outputs/frames_selected/cvat_batch_001/               (200 JPG)
- manifests/frames_selected_manifest.csv                (600 rows)
- manifests/cvat_batch_001_manifest.csv                 (200 rows)
- manifests/hard_cases_manifest.csv                     (initial auto candidates)
- outputs/archives/*.zip                                (CVAT-ready archives)
- outputs/contact_sheets/*.jpg                          (visual review sheets)

Selection policy:
- preserve video-source proportions
- combine metadata coverage frames with visually diverse/hard frames
- avoid duplicates
"""

from __future__ import annotations

import argparse
import csv
import math
import shutil
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageOps


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_ROOT = REPO_ROOT / "task_A_dataset_frame"
RAW_MANIFEST = TASK_ROOT / "manifests" / "frames_raw_manifest.csv"
SELECTED_MANIFEST = TASK_ROOT / "manifests" / "frames_selected_manifest.csv"
CVAT_MANIFEST = TASK_ROOT / "manifests" / "cvat_batch_001_manifest.csv"
HARD_CASES_MANIFEST = TASK_ROOT / "manifests" / "hard_cases_manifest.csv"

BASELINE_DIR = TASK_ROOT / "outputs" / "frames_selected" / "600_baseline"
CVAT_DIR = TASK_ROOT / "outputs" / "frames_selected" / "cvat_batch_001"
CONTACT_DIR = TASK_ROOT / "outputs" / "contact_sheets"
ARCHIVE_DIR = TASK_ROOT / "outputs" / "archives"

BASELINE_N = 600
CVAT_N = 200
CANDIDATE_N = 2400
SOURCE_QUOTAS = {
    "short_head_left_file000": 183,
    "short_head_left_file001": 183,
    "short_head_left_file002": 183,
    "short_head_left_file003": 51,
}


def read_raw_manifest() -> list[dict[str, str]]:
    with RAW_MANIFEST.open(newline="") as handle:
        return list(csv.DictReader(handle))


def clean_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for item in path.iterdir():
        if item.is_file() and item.name != ".gitkeep":
            item.unlink()


def evenly_spaced(items: list[dict[str, str]], n: int) -> list[dict[str, str]]:
    if n <= 0 or not items:
        return []
    if n >= len(items):
        return list(items)
    if n == 1:
        return [items[len(items) // 2]]
    indexes = [round(i * (len(items) - 1) / (n - 1)) for i in range(n)]
    return [items[i] for i in indexes]


def proportional_quotas(counts: dict[str, int], total: int) -> dict[str, int]:
    raw = {k: counts[k] / sum(counts.values()) * total for k in counts}
    quotas = {k: math.floor(v) for k, v in raw.items()}
    remainder = total - sum(quotas.values())
    for k, _ in sorted(raw.items(), key=lambda kv: kv[1] - math.floor(kv[1]), reverse=True)[:remainder]:
        quotas[k] += 1
    return quotas


def image_metrics(path: Path) -> dict[str, float]:
    image = Image.open(path).convert("L").resize((160, 120))
    arr = np.asarray(image, dtype=np.float32) / 255.0
    brightness = float(arr.mean())
    contrast = float(arr.std())
    gy, gx = np.gradient(arr)
    grad_mag = np.sqrt(gx * gx + gy * gy)
    edge_density = float((grad_mag > 0.08).mean())
    sharpness = float(grad_mag.var())
    brightness_extreme = abs(brightness - 0.5) * 2.0
    # Higher = more likely visually difficult or useful for diversity.
    hard_score = (
        0.30 * edge_density
        + 0.25 * contrast
        + 0.25 * brightness_extreme
        + 0.20 * max(0.0, 0.0025 - sharpness) / 0.0025
    )
    return {
        "brightness": brightness,
        "contrast": contrast,
        "edge_density": edge_density,
        "sharpness": sharpness,
        "hard_score": hard_score,
    }


def score_candidates(candidates: list[dict[str, str]]) -> list[dict[str, str]]:
    scored = []
    for row in candidates:
        metrics = image_metrics(REPO_ROOT / row["output_file"])
        out = dict(row)
        for key, value in metrics.items():
            out[key] = f"{value:.6f}"
        scored.append(out)
    return scored


def select_baseline(scored: list[dict[str, str]]) -> list[dict[str, str]]:
    by_source: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in scored:
        by_source[row["source_id"]].append(row)
    selected: list[dict[str, str]] = []
    selected_ids: set[str] = set()

    for source_id, quota in SOURCE_QUOTAS.items():
        rows = sorted(
            by_source[source_id],
            key=lambda r: (int(r["episode_index"]), int(r["source_frame_index"])),
        )
        coverage_n = round(quota * 0.70)
        coverage = evenly_spaced(rows, coverage_n)
        for row in coverage:
            if row["frame_id"] not in selected_ids:
                selected.append(row)
                selected_ids.add(row["frame_id"])

        remaining_n = quota - sum(1 for r in selected if r["source_id"] == source_id)
        hard_sorted = sorted(rows, key=lambda r: float(r["hard_score"]), reverse=True)
        for row in hard_sorted:
            if remaining_n <= 0:
                break
            if row["frame_id"] in selected_ids:
                continue
            selected.append(row)
            selected_ids.add(row["frame_id"])
            remaining_n -= 1

    return sorted(selected, key=lambda r: (int(r["video_file_index"]), int(r["source_frame_index"])))


def selected_reason(row: dict[str, str], hard_threshold: float) -> str:
    tags = ["stratified_coverage"]
    if float(row["hard_score"]) >= hard_threshold:
        tags.append("visual_hard_candidate")
    return "+".join(tags)


def copy_selected(
    rows: list[dict[str, str]],
    out_dir: Path,
    manifest_path: Path,
    hard_threshold: float,
) -> None:
    clean_dir(out_dir)
    fieldnames = [
        "selected_index",
        "dataset_split",
        "camera",
        "video_file",
        "episode_index",
        "frame_index",
        "timestamp_seconds",
        "source_frame",
        "output_file",
        "selection_reason",
        "notes",
    ]
    with manifest_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for idx, row in enumerate(rows, start=1):
            src = REPO_ROOT / row["output_file"]
            dst = out_dir / src.name
            shutil.copy2(src, dst)
            writer.writerow(
                {
                    "selected_index": idx,
                    "dataset_split": row["dataset_split"],
                    "camera": row["camera"],
                    "video_file": row["video_file"],
                    "episode_index": row["episode_index"],
                    "frame_index": row["source_frame_index"],
                    "timestamp_seconds": row["timestamp_seconds"],
                    "source_frame": row["output_file"],
                    "output_file": str(dst.relative_to(REPO_ROOT)),
                    "selection_reason": selected_reason(row, hard_threshold),
                    "notes": f"hard_score={row['hard_score']}; brightness={row['brightness']}; contrast={row['contrast']}; edge_density={row['edge_density']}; sharpness={row['sharpness']}",
                }
            )


def write_hard_cases(rows: list[dict[str, str]], hard_threshold: float) -> None:
    fieldnames = [
        "case_id",
        "dataset_split",
        "camera",
        "video_file",
        "episode_index",
        "frame_index",
        "timestamp_seconds",
        "frame_path",
        "hard_case_tags",
        "priority",
        "locateanything_status",
        "notes",
    ]
    hard_rows = sorted(rows, key=lambda r: float(r["hard_score"]), reverse=True)[:120]
    with HARD_CASES_MANIFEST.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for idx, row in enumerate(hard_rows, start=1):
            tags = []
            if float(row["sharpness"]) < 0.0025:
                tags.append("motion_blur_candidate")
            if float(row["brightness"]) < 0.25 or float(row["brightness"]) > 0.75:
                tags.append("poor_lighting_candidate")
            if float(row["edge_density"]) > 0.25:
                tags.append("clutter_candidate")
            if not tags:
                tags.append("visual_hard_candidate")
            priority = "high" if float(row["hard_score"]) >= hard_threshold else "medium"
            writer.writerow(
                {
                    "case_id": f"hard_{idx:04d}",
                    "dataset_split": row["dataset_split"],
                    "camera": row["camera"],
                    "video_file": row["video_file"],
                    "episode_index": row["episode_index"],
                    "frame_index": row["source_frame_index"],
                    "timestamp_seconds": row["timestamp_seconds"],
                    "frame_path": row["output_file"],
                    "hard_case_tags": ";".join(tags),
                    "priority": priority,
                    "locateanything_status": "not_run",
                    "notes": f"auto_score={row['hard_score']}",
                }
            )


def make_zip(source_dir: Path, zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source_dir.glob("*.jpg")):
            archive.write(path, arcname=path.name)


def make_contact_sheet(rows: list[dict[str, str]], sheet_path: Path, title: str, max_images: int = 120) -> None:
    sheet_path.parent.mkdir(parents=True, exist_ok=True)
    sample = evenly_spaced(rows, min(max_images, len(rows)))
    thumb_w, thumb_h = 160, 120
    cols = 10
    rows_n = math.ceil(len(sample) / cols)
    header_h = 36
    canvas = Image.new("RGB", (cols * thumb_w, rows_n * (thumb_h + 20) + header_h), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((8, 8), title, fill=(0, 0, 0))
    for i, row in enumerate(sample):
        img = Image.open(REPO_ROOT / row["output_file"]).convert("RGB")
        img = ImageOps.contain(img, (thumb_w, thumb_h))
        x = (i % cols) * thumb_w
        y = header_h + (i // cols) * (thumb_h + 20)
        canvas.paste(img, (x, y))
        draw.text((x + 2, y + thumb_h + 2), f"ep{row['episode_index']} f{row['video_file_index']}", fill=(0, 0, 0))
    canvas.save(sheet_path, quality=90)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=int, default=BASELINE_N)
    parser.add_argument("--cvat", type=int, default=CVAT_N)
    parser.add_argument("--candidate", type=int, default=CANDIDATE_N)
    args = parser.parse_args()

    raw_rows = read_raw_manifest()
    by_source: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in raw_rows:
        by_source[row["source_id"]].append(row)

    candidate_quotas = proportional_quotas({k: len(v) for k, v in by_source.items()}, args.candidate)
    candidates: list[dict[str, str]] = []
    for source_id, rows in by_source.items():
        rows_sorted = sorted(rows, key=lambda r: (int(r["episode_index"]), int(r["source_frame_index"])))
        candidates.extend(evenly_spaced(rows_sorted, candidate_quotas[source_id]))

    scored = score_candidates(candidates)
    baseline = select_baseline(scored)
    if len(baseline) != args.baseline:
        raise RuntimeError(f"selected {len(baseline)} baseline frames, expected {args.baseline}")

    hard_scores = sorted(float(row["hard_score"]) for row in baseline)
    hard_threshold = hard_scores[max(0, int(len(hard_scores) * 0.70) - 1)]
    cvat_rows = evenly_spaced(baseline, args.cvat)

    copy_selected(baseline, BASELINE_DIR, SELECTED_MANIFEST, hard_threshold)
    copy_selected(cvat_rows, CVAT_DIR, CVAT_MANIFEST, hard_threshold)
    write_hard_cases(baseline, hard_threshold)
    make_zip(BASELINE_DIR, ARCHIVE_DIR / "frames_selected_600_baseline.zip")
    make_zip(CVAT_DIR, ARCHIVE_DIR / "cvat_batch_001_200.zip")
    make_contact_sheet(baseline, CONTACT_DIR / "baseline_600_contact_sheet.jpg", "Round-1 baseline 600")
    make_contact_sheet(cvat_rows, CONTACT_DIR / "cvat_batch_001_contact_sheet.jpg", "CVAT batch 001 - 200")
    make_contact_sheet(
        sorted(baseline, key=lambda r: float(r["hard_score"]), reverse=True)[:120],
        CONTACT_DIR / "hard_case_candidates_contact_sheet.jpg",
        "Auto hard-case candidates",
    )

    print("selected_baseline", len(baseline), dict(Counter(r["source_id"] for r in baseline)))
    print("selected_cvat", len(cvat_rows), dict(Counter(r["source_id"] for r in cvat_rows)))
    print("hard_threshold", f"{hard_threshold:.6f}")


if __name__ == "__main__":
    main()
